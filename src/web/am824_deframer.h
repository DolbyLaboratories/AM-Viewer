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

#pragma once

#include <cstdint>
#include <deque>
#include <vector>

struct Am824Frame {
    std::vector<std::uint8_t> payload;
    int bitDepth = 0;
    bool assembleFlag = false;
    bool formatFlag = false;
    bool subframeMode = false;
};

class Am824Deframer {
public:
    Am824Deframer();

    void reset();
    void receivePayload(const std::uint8_t* payload, std::size_t payloadSize);

    bool haveFrame() const;
    Am824Frame popFrame();

    struct Stats {
        std::uint64_t paAcquisitions = 0;
        std::uint64_t paAcceptedRightBlanking = 0;
        std::uint64_t paAcceptedLeftBlanking = 0;
        std::uint64_t paAcceptedWithoutBlanking = 0;
        std::uint64_t pbDetections = 0;
        std::uint64_t pbAtPos6WrongChannel = 0;
        std::uint64_t nonPbAtPos6 = 0;
        std::uint64_t nonPbAtPos9 = 0;
        std::uint64_t headerDecodesAttempted = 0;
        std::uint64_t headerDecodesSucceeded = 0;
        std::uint64_t framesEmitted = 0;
        std::uint64_t framesRejectedWrongDataType = 0;
        std::uint64_t abortsDuringGotPa = 0;
        std::uint64_t abortsDuringGotSync = 0;
        std::uint64_t idleNonZeroRightResets = 0;
        std::uint64_t idleNonZeroLeftResets = 0;
        std::uint64_t gotPaStateEntries = 0;
        std::uint64_t gotSyncStateEntries = 0;
        std::uint64_t gotHeaderStateEntries = 0;
    };
    Stats getStats() const;

private:
    enum class State {
        IDLE,
        GOT_PA,
        GOT_SYNC,
        GOT_HEADER
    };

    bool isPa(std::uint32_t sample);
    bool isPb(std::uint32_t sample);
    std::uint32_t getWord(const std::vector<std::uint8_t>& payload, std::size_t byteIndex, int bitDepth) const;

private:
    State m_state;
    bool m_gotLeftBlanking;
    bool m_gotRightBlanking;
    bool m_gotFrameModeBlanking;
    bool m_subframeMode;
    int m_length24;
    int m_dataType;
    int m_bitDepth;
    std::vector<std::uint8_t> m_payloads;

    int m_leftZeroCount;
    int m_rightZeroCount;
    int m_frameModeZeroCount;
    bool m_activeChannel;
    bool m_rightNotLeft;

    struct PendingFrame {
        int bitDepth = 0;
        bool assembleFlag = false;
        bool formatFlag = false;
        bool subframeMode = false;
    };

    bool m_hasPendingFrame;
    PendingFrame m_pendingFrame;

    std::deque<Am824Frame> m_frames;
    Stats m_stats;

    static constexpr int ZERO_THRESHOLD = 350;
};
