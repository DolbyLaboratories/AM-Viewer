/****************************************************************************
 *
 *
 * Copyright (c) 2026 Dolby International AB.
 * All rights reserved.

 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED
 * BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
 * BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 ******************************************************************************/

#include "am824_deframer.h"

#include <algorithm>
#include <cmath>

Am824Deframer::Am824Deframer()
    : m_state(State::IDLE)
    , m_gotLeftBlanking(false)
    , m_gotRightBlanking(false)
    , m_gotFrameModeBlanking(false)
    , m_subframeMode(false)
    , m_length24(0)
    , m_dataType(0)
    , m_bitDepth(0)
    , m_leftZeroCount(0)
    , m_rightZeroCount(0)
    , m_frameModeZeroCount(0)
    , m_activeChannel(false)
    , m_rightNotLeft(true)
    , m_hasPendingFrame(false) {}

void Am824Deframer::reset() {
    m_state = State::IDLE;
    m_gotLeftBlanking = false;
    m_gotRightBlanking = false;
    m_gotFrameModeBlanking = false;
    m_subframeMode = false;
    m_length24 = 0;
    m_dataType = 0;
    m_bitDepth = 0;
    m_payloads.clear();
    m_leftZeroCount = 0;
    m_rightZeroCount = 0;
    m_frameModeZeroCount = 0;
    m_activeChannel = false;
    m_rightNotLeft = true;
    m_hasPendingFrame = false;
}

bool Am824Deframer::haveFrame() const {
    return !m_frames.empty();
}

Am824Frame Am824Deframer::popFrame() {
    if (m_frames.empty()) {
        return {};
    }
    Am824Frame frame = std::move(m_frames.front());
    m_frames.pop_front();
    return frame;
}

Am824Deframer::Stats Am824Deframer::getStats() const {
    return m_stats;
}

bool Am824Deframer::isPa(std::uint32_t sample) {
    constexpr std::uint32_t PA20 = 0x6f8720;
    constexpr std::uint32_t PA24 = 0x96f872;

    if (sample == PA20) {
        m_bitDepth = 20;
        return true;
    }
    if (sample == PA24) {
        m_bitDepth = 24;
        return true;
    }
    return false;
}

bool Am824Deframer::isPb(std::uint32_t sample) {
    constexpr std::uint32_t PB20 = 0x54e1f0;
    constexpr std::uint32_t PB24 = 0xa54e1f;

    if (sample == PB20) {
        m_bitDepth = 20;
        return true;
    }
    if (sample == PB24) {
        m_bitDepth = 24;
        return true;
    }
    return false;
}

std::uint32_t Am824Deframer::getWord(const std::vector<std::uint8_t>& payload,
                                     std::size_t byteIndex,
                                     int bitDepth) const {
    if (byteIndex + 2 >= payload.size()) {
        return 0;
    }

    const std::uint32_t sample =
        (static_cast<std::uint32_t>(payload[byteIndex]) << 16) |
        (static_cast<std::uint32_t>(payload[byteIndex + 1]) << 8) |
        static_cast<std::uint32_t>(payload[byteIndex + 2]);
    return sample >> (24 - bitDepth);
}

void Am824Deframer::receivePayload(const std::uint8_t* payload, std::size_t payloadSize) {
    if (!payload || payloadSize < 4) {
        return;
    }

    // Python reference uses a packet-local right_not_left phase that is reset for each RTP payload.
    m_rightNotLeft = true;

    for (std::size_t index = 0; index + 3 < payloadSize; index += 4) {
        m_rightNotLeft = !m_rightNotLeft;

        if (m_subframeMode) {
            if (!m_activeChannel) {
                m_activeChannel = true;
                continue;
            }
            m_activeChannel = false;
        }

        const std::uint32_t nextSample =
            (static_cast<std::uint32_t>(payload[index + 1]) << 16) |
            (static_cast<std::uint32_t>(payload[index + 2]) << 8) |
            static_cast<std::uint32_t>(payload[index + 3]);

        const std::uint8_t nextWord[3] = {
            static_cast<std::uint8_t>(payload[index + 1]),
            static_cast<std::uint8_t>(payload[index + 2]),
            static_cast<std::uint8_t>(payload[index + 3]),
        };

        if (m_state == State::IDLE) {
            if (nextSample == 0) {
                if (m_rightNotLeft) {
                    ++m_rightZeroCount;
                    if (m_rightZeroCount >= ZERO_THRESHOLD) {
                        m_gotRightBlanking = true;
                    }
                } else {
                    ++m_leftZeroCount;
                    if (m_leftZeroCount >= ZERO_THRESHOLD) {
                        m_gotLeftBlanking = true;
                    }
                }
                ++m_frameModeZeroCount;
                if (m_frameModeZeroCount >= ZERO_THRESHOLD) {
                    m_gotFrameModeBlanking = true;
                }
            } else {
                if (isPa(nextSample)) {
                    ++m_stats.paAcquisitions;
                    if (m_rightNotLeft && m_gotRightBlanking) {
                        ++m_stats.paAcceptedRightBlanking;
                    } else if (!m_rightNotLeft && m_gotLeftBlanking) {
                        ++m_stats.paAcceptedLeftBlanking;
                    } else {
                        ++m_stats.paAcceptedWithoutBlanking;
                    }
                    m_state = State::GOT_PA;
                    ++m_stats.gotPaStateEntries;
                    m_payloads.assign(nextWord, nextWord + 3);
                } else if (m_rightNotLeft) {
                    ++m_stats.idleNonZeroRightResets;
                    m_rightZeroCount = 0;
                    m_frameModeZeroCount = 0;
                    m_gotRightBlanking = false;
                    m_gotFrameModeBlanking = false;
                } else {
                    ++m_stats.idleNonZeroLeftResets;
                    m_leftZeroCount = 0;
                    m_frameModeZeroCount = 0;
                    m_gotLeftBlanking = false;
                    m_gotFrameModeBlanking = false;
                }
            }
            continue;
        }

        if (m_state == State::GOT_PA) {
            ++m_stats.gotPaStateEntries;
            m_payloads.insert(m_payloads.end(), nextWord, nextWord + 3);
            const std::size_t framePos = m_payloads.size();

            if (framePos == 6) {
                if (isPb(nextSample)) {
                    if (m_rightNotLeft) {
                        ++m_stats.pbDetections;
                        m_subframeMode = false;
                        m_state = State::GOT_SYNC;
                        ++m_stats.gotSyncStateEntries;
                    } else {
                        ++m_stats.pbAtPos6WrongChannel;
                    }
                } else {
                    ++m_stats.nonPbAtPos6;
                }
                // If not Pb/right_not_left at position 6, continue to check position 9
            } else if (framePos == 9) {
                if (isPb(nextSample)) {
                    // Pb at position 9 → subframe mode
                    ++m_stats.pbDetections;
                    m_subframeMode = true;
                    m_state = State::GOT_SYNC;
                    ++m_stats.gotSyncStateEntries;

                    // Remove middle word from payload (subframe mode compacting)
                    std::vector<std::uint8_t> compact;
                    compact.reserve(6);
                    compact.insert(compact.end(), m_payloads.begin(), m_payloads.begin() + 3);
                    compact.insert(compact.end(), m_payloads.begin() + 6, m_payloads.begin() + 9);
                    m_payloads = std::move(compact);
                } else {
                    // No Pb at position 9 → abort
                    ++m_stats.nonPbAtPos9;
                    ++m_stats.abortsDuringGotPa;
                    m_state = State::IDLE;
                    m_payloads.clear();
                }
            } else {
                // Frame positions other than 6 or 9 → abort
                ++m_stats.abortsDuringGotPa;
                m_state = State::IDLE;
                m_payloads.clear();
            }
            continue;
        }

        if (m_state == State::GOT_SYNC) {
            ++m_stats.gotSyncStateEntries;
            m_payloads.insert(m_payloads.end(), nextWord, nextWord + 3);
            const std::size_t framePos = m_payloads.size();

            if (framePos == 15) {
                ++m_stats.headerDecodesAttempted;
                
                const auto decodeWord = [&](std::size_t byteIndex, bool reverseBytes) {
                    if (byteIndex + 2 >= m_payloads.size()) {
                        return std::uint32_t{0};
                    }

                    std::uint32_t sample = 0;
                    if (!reverseBytes) {
                        sample =
                            (static_cast<std::uint32_t>(m_payloads[byteIndex]) << 16) |
                            (static_cast<std::uint32_t>(m_payloads[byteIndex + 1]) << 8) |
                            static_cast<std::uint32_t>(m_payloads[byteIndex + 2]);
                    } else {
                        sample =
                            (static_cast<std::uint32_t>(m_payloads[byteIndex + 2]) << 16) |
                            (static_cast<std::uint32_t>(m_payloads[byteIndex + 1]) << 8) |
                            static_cast<std::uint32_t>(m_payloads[byteIndex]);
                    }

                    return sample >> (24 - m_bitDepth);
                };

                const auto decodeDataType = [&](bool reverseBytes) {
                    const std::uint32_t pcWord = decodeWord(6, reverseBytes);
                    int dataType = static_cast<int>((pcWord >> (m_bitDepth - 16)) & 0x1F);
                    if (dataType == 31) {
                        const std::uint32_t peWord = decodeWord(12, reverseBytes);
                        dataType += static_cast<int>(peWord & 0xFFFF);
                    }
                    return std::pair<int, std::uint32_t>{dataType, pcWord};
                };

                auto [primaryDataType, primaryPc] = decodeDataType(false);
                auto [alternateDataType, alternatePc] = decodeDataType(true);

                std::uint32_t pc = primaryPc;
                m_dataType = primaryDataType;
                if (m_dataType != 27 && m_dataType != 32 &&
                    (alternateDataType == 27 || alternateDataType == 32)) {
                    m_dataType = alternateDataType;
                    pc = alternatePc;
                }

                const std::uint32_t pd = getWord(m_payloads, 9, m_bitDepth);
                m_length24 = static_cast<int>(std::ceil(pd / static_cast<float>(m_bitDepth)) * 3.0f);

                if (m_dataType != 32) {
                    ++m_stats.framesRejectedWrongDataType;
                    ++m_stats.abortsDuringGotSync;
                    m_state = State::IDLE;
                    m_payloads.clear();
                    continue;
                }

                ++m_stats.headerDecodesSucceeded;
                m_hasPendingFrame = true;
                m_pendingFrame.bitDepth = m_bitDepth;
                m_pendingFrame.subframeMode = m_subframeMode;
                m_pendingFrame.assembleFlag = ((pc >> (m_bitDepth - 7)) & 0x1) != 0;
                m_pendingFrame.formatFlag = ((pc >> (m_bitDepth - 6)) & 0x1) != 0;
                m_state = State::GOT_HEADER;
                ++m_stats.gotHeaderStateEntries;
            }
            continue;
        }

        if (m_state == State::GOT_HEADER) {
            ++m_stats.gotHeaderStateEntries;
            m_payloads.insert(m_payloads.end(), nextWord, nextWord + 3);

            if (static_cast<int>(m_payloads.size()) - 12 < m_length24) {
                continue;
            }

            std::size_t totalBytes = static_cast<std::size_t>(m_length24 + 12);
            if (totalBytes > m_payloads.size()) {
                totalBytes = m_payloads.size();
            }
            m_payloads.resize(totalBytes);

            std::size_t headerBytes = (m_dataType > 30) ? 18 : 12;
            if (headerBytes < m_payloads.size() && m_hasPendingFrame) {
                ++m_stats.framesEmitted;
                Am824Frame frame;
                frame.bitDepth = m_pendingFrame.bitDepth;
                frame.assembleFlag = m_pendingFrame.assembleFlag;
                frame.formatFlag = m_pendingFrame.formatFlag;
                frame.subframeMode = m_pendingFrame.subframeMode;
                frame.payload.assign(m_payloads.begin() + static_cast<std::ptrdiff_t>(headerBytes),
                                     m_payloads.end());
                m_frames.push_back(std::move(frame));
            }

            m_state = State::IDLE;
            m_payloads.clear();
            m_hasPendingFrame = false;
        }
    }
}
