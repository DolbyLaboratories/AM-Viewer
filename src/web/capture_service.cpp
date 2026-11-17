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

#include "capture_service.h"
#include "adm_xml_parser.h"
#include "logging.h"

#include <pcap.h>

#include <iomanip>
#include <sstream>
#include <cstring>
#include <unordered_set>

namespace {
constexpr std::uint64_t kLivePacketStaleMs = 1500;
}

CaptureService::CaptureService()
    : m_handle(nullptr)
    , m_running(false)
    , m_packetCount(0)
    , m_lastPacketMonotonicMs(0)
    , m_lastFrameMonotonicMs(0)
    , m_port(0)
    , m_clockRate(0)
    , m_datalinkType(DLT_EN10MB)
    , m_st2110_41ExpectedBytes(0)
    , m_st2110_41PacketsInBurst(0)
    , m_lastBurstPacketCount(0) {
    reset_live_state_locked();
}

CaptureService::~CaptureService() {
    stop();
}

std::vector<std::string> CaptureService::list_interfaces() {
    std::vector<std::string> interfaces;
    std::unordered_set<std::string> seen;

    char errbuf[PCAP_ERRBUF_SIZE] = {0};
    pcap_if_t* allDevices = nullptr;

    if (pcap_findalldevs(&allDevices, errbuf) != 0) {
        return interfaces;
    }

    for (pcap_if_t* dev = allDevices; dev != nullptr; dev = dev->next) {
        if (!dev->name) {
            continue;
        }

        const std::string name = dev->name;
        
        if (seen.insert(name).second) {
            interfaces.push_back(name);
        }
    }

    pcap_freealldevs(allDevices);
    return interfaces;
}

bool CaptureService::start(const std::string& interfaceName,
                           const std::string& address,
                           int port,
                           const std::string& codec,
                           int clockRate,
                           std::string& error) {
    AMV_LOG_INFO("capture.start request iface={} addr={} port={} codec={} clockRate={}",
                 interfaceName, address, port, codec, clockRate);

    {
    std::lock_guard<std::mutex> lock(m_mutex);

    if (m_running) {
        error = "Capture is already running";
        AMV_LOG_WARN("capture.start rejected: {}", error);
        return false;
    }

    char errbuf[PCAP_ERRBUF_SIZE] = {0};
    pcap_t* handle = pcap_create(interfaceName.c_str(), errbuf);
    if (!handle) {
        error = std::string("Failed to create capture handle: ") + errbuf;
        m_lastError = error;
        AMV_LOG_ERROR("capture.start failed: {}", error);
        return false;
    }

    pcap_set_snaplen(handle, 65535);
    pcap_set_promisc(handle, 1);
    pcap_set_timeout(handle, 10);
    pcap_set_immediate_mode(handle, 1);

    if (int rc = pcap_activate(handle); rc != 0) {
        if (rc < 0) {
            error = std::string("Failed to activate capture handle: ") + pcap_geterr(handle);
            pcap_close(handle);
            m_lastError = error;
            AMV_LOG_ERROR("capture.start failed: {} (rc={})", error, rc);
            return false;
        }
        AMV_LOG_WARN("capture.start activate warning rc={} msg={}", rc, pcap_geterr(handle));
    }

    if (!address.empty() && port > 0) {
        bpf_program filter{};
        const std::string filterExpr = "ip dst " + address + " and udp dst port " + std::to_string(port);

        if (pcap_compile(handle, &filter, filterExpr.c_str(), 0, PCAP_NETMASK_UNKNOWN) == -1) {
            error = std::string("Failed to compile filter: ") + pcap_geterr(handle);
            pcap_close(handle);
            m_lastError = error;
            AMV_LOG_ERROR("capture.start failed: {}", error);
            return false;
        }

        if (pcap_setfilter(handle, &filter) == -1) {
            error = std::string("Failed to set filter: ") + pcap_geterr(handle);
            pcap_freecode(&filter);
            pcap_close(handle);
            m_lastError = error;
            AMV_LOG_ERROR("capture.start failed: {}", error);
            return false;
        }

        pcap_freecode(&filter);
    }

    m_handle = handle;
    m_datalinkType = pcap_datalink(handle);
    m_interfaceName = interfaceName;
    m_address = address;
    m_codec = codec;
    m_port = port;
    m_clockRate = clockRate;
    m_packetCount = 0;
    m_lastPacketMonotonicMs = 0;
    m_lastFrameMonotonicMs = 0;
    m_lastError.clear();
    reset_live_state_locked();

    {
        std::lock_guard<std::mutex> modelLock(m_liveModelMutex);
        if (m_codec == "ST2110-41") {
            m_liveModel = std::make_shared<amviewer::types::streaminfo::st2110_41::ST2110_41Info>();
        } else if (m_codec == "AM824") {
            m_liveModel = std::make_shared<amviewer::types::streaminfo::st2110_31::ST2110_31Info>();
        }
    }

    m_running = true;

    m_thread = std::thread([this]() { capture_loop(); });
    AMV_LOG_INFO("capture.start ok iface={} addr={} port={} codec={}",
                 interfaceName, address, port, codec);
    } // release m_mutex before firing callback

    // Notify listeners that metadata has been cleared so the frontend
    // doesn't keep displaying stale data from a previous capture.
    fire_metadata_frame_callback();

    return true;
}

void CaptureService::stop() {
    pcap_t* handleToClose = nullptr;

    {
        std::lock_guard<std::mutex> lock(m_mutex);
        if (!m_running) {
            return;
        }
        AMV_LOG_INFO("capture.stop iface={} addr={} port={}",
                     m_interfaceName, m_address, m_port);
        m_running = false;
        if (m_handle) {
            pcap_breakloop(m_handle);
        }
    }

    if (m_thread.joinable()) {
        m_thread.join();
    }

    {
        std::lock_guard<std::mutex> lock(m_mutex);
        handleToClose = m_handle;
        m_handle = nullptr;
        m_interfaceName.clear();
        m_address.clear();
        m_codec.clear();
        m_port = 0;
        m_clockRate = 0;
        m_frameCount = 0;
        m_packetCount = 0;
        m_lastFrameMonotonicMs = 0;
        m_lastPacketMonotonicMs = 0;
    }

    if (handleToClose) {
        pcap_close(handleToClose);
    }
}

bool CaptureService::running() const {
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_running;
}

CaptureSnapshot CaptureService::snapshot() const {
    std::lock_guard<std::mutex> lock(m_mutex);

    CaptureSnapshot out;
    out.active = m_running;
    out.interfaceName = m_interfaceName;
    out.address = m_address;
    out.port = m_port;
    out.packetCount = m_packetCount.load();
    out.frameCount = m_frameCount.load();
    out.lastError = m_lastError;
    out.ditValue = m_ditValue;
    out.liveXml = m_liveXml;
    out.packetTimestampMs = m_lastFrameMonotonicMs.load();

    const auto nowMs = static_cast<std::uint64_t>(
        std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now().time_since_epoch())
            .count());
    const std::uint64_t lastMetadataMs = m_lastFrameMonotonicMs.load();
    const bool stale = out.active && (lastMetadataMs == 0 || nowMs > lastMetadataMs + kLivePacketStaleMs);

    {
        std::lock_guard<std::mutex> modelLock(m_liveModelMutex);
        if (m_liveModel && !stale) {
            out.stream = m_liveModel;
            out.rtpInfo = m_liveModel->rtpInfo;
        }
    }

    return out;
}

Am824Deframer::Stats CaptureService::getDeframerStats() const {
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_am824Deframer.getStats();
}

void CaptureService::packet_callback(u_char* userData,
                                     const struct pcap_pkthdr* header,
                                     const u_char* packetData) {
    (void)header;
    (void)packetData;
    auto* self = reinterpret_cast<CaptureService*>(userData);
    if (self) {
        self->m_packetCount.fetch_add(1);
        const auto nowMs = static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::steady_clock::now().time_since_epoch())
                .count());
        self->m_lastPacketMonotonicMs.store(nowMs);

        {
            std::lock_guard<std::mutex> lock(self->m_mutex);
            self->m_lastFrameMonotonicMs.store(nowMs);
            // if (self->m_codec == "AM824") {
            //     self->m_smpte2110_31 = "on";
            //     self->m_smpte2110_41 = "off";
            //     if (self->m_frame == "off" && self->m_subframe == "off") {
            //         self->m_frame = "on";
            //     }
            //     if (self->m_depth20 == "off" && self->m_depth24 == "off") {
            //         self->m_depth24 = "on";
            //     }
            // } else if (self->m_codec == "ST2110-41") {
            //     self->m_lastFrameMonotonicMs.store(nowMs);
            //     self->m_smpte2110_41 = "on";
            //     self->m_smpte2110_31 = "off";
            // }
        }

        self->process_packet(header, packetData);
    }
}

void CaptureService::process_packet(const struct pcap_pkthdr* header, const u_char* packetData) {
    std::string codec;
    int datalinkType = DLT_EN10MB;
    int clockRate = 0;
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        codec = m_codec;
        datalinkType = m_datalinkType;
        clockRate = m_clockRate;
    }

    if (codec.empty() || !packetData || !header) {
        return;
    }

    const auto* bytes = reinterpret_cast<const std::uint8_t*>(packetData);

    std::vector<std::size_t> offsetCandidates;
    switch (datalinkType) {
        case DLT_NULL:
        case DLT_LOOP:
            offsetCandidates.push_back(4);
            break;
        case DLT_LINUX_SLL:
            offsetCandidates.push_back(16);
            break;
        case DLT_EN10MB:
            offsetCandidates.push_back(14);
            break;
        default:
            break;
    }
    offsetCandidates.push_back(0);
    offsetCandidates.push_back(4);
    offsetCandidates.push_back(14);
    offsetCandidates.push_back(16);

    std::size_t ipOffset = 0;
    std::size_t ipHeaderLen = 0;
    bool foundIpv4Udp = false;

    if (datalinkType == DLT_EN10MB && header->caplen >= 14) {
        std::size_t l2Offset = 14;
        std::uint16_t etherType = static_cast<std::uint16_t>((bytes[12] << 8) | bytes[13]);
        while ((etherType == 0x8100 || etherType == 0x88A8 || etherType == 0x9100) &&
               header->caplen >= l2Offset + 4) {
            etherType = static_cast<std::uint16_t>((bytes[l2Offset + 2] << 8) | bytes[l2Offset + 3]);
            l2Offset += 4;
        }

        if (etherType == 0x0800 && header->caplen >= l2Offset + 20) {
            const std::size_t ihlBytes = (static_cast<std::size_t>(bytes[l2Offset] & 0x0F)) * 4;
            if ((bytes[l2Offset] >> 4) == 4 && ihlBytes >= 20 &&
                header->caplen >= l2Offset + ihlBytes + 8 && bytes[l2Offset + 9] == 17) {
                ipOffset = l2Offset;
                ipHeaderLen = ihlBytes;
                foundIpv4Udp = true;
            }
        }
    }

    auto tryOffset = [&](std::size_t candidate) {
        if (foundIpv4Udp) {
            return;
        }
        if (header->caplen < candidate + 20) {
            return;
        }

        const std::uint8_t version = bytes[candidate] >> 4;
        if (version != 4) {
            return;
        }

        const std::size_t ihlBytes = (static_cast<std::size_t>(bytes[candidate] & 0x0F)) * 4;
        if (ihlBytes < 20) {
            return;
        }

        if (header->caplen < candidate + ihlBytes + 8) {
            return;
        }

        const std::uint8_t protocol = bytes[candidate + 9];
        if (protocol != 17) {
            return;
        }

        ipOffset = candidate;
        ipHeaderLen = ihlBytes;
        foundIpv4Udp = true;
    };

    for (const std::size_t candidate : offsetCandidates) {
        tryOffset(candidate);
    }

    if (!foundIpv4Udp) {
        const std::size_t maxScanOffset =
            (header->caplen > 28) ? std::min<std::size_t>(header->caplen - 28, 128) : 0;
        for (std::size_t candidate = 0; candidate <= maxScanOffset && !foundIpv4Udp; ++candidate) {
            tryOffset(candidate);
        }
    }

    if (!foundIpv4Udp) {
        return;
    }

    const std::size_t udpOffset = ipOffset + ipHeaderLen;
    if (header->caplen < udpOffset + 8) {
        return;
    }

    const std::size_t udpPayloadOffset = udpOffset + 8;
    if (header->caplen <= udpPayloadOffset) {
        return;
    }

    const u_char* udpPayloadData = packetData + udpPayloadOffset;
    const std::size_t udpPayloadSize = header->caplen - udpPayloadOffset;

    if (udpPayloadSize < 12) {
        return;
    }

    std::size_t rtpHeaderBytes = 12;
    const std::uint8_t rtpFirst = bytes[udpPayloadOffset];
    const std::uint8_t rtpVersion = static_cast<std::uint8_t>((rtpFirst >> 6U) & 0x03U);
    const std::uint16_t rtpSequenceNumber = static_cast<std::uint16_t>((bytes[udpPayloadOffset + 2] << 8) | bytes[udpPayloadOffset + 3]);
    const std::uint32_t rtpTimestamp = (static_cast<std::uint32_t>(bytes[udpPayloadOffset + 4]) << 24) |
                         (static_cast<std::uint32_t>(bytes[udpPayloadOffset + 5]) << 16) |
                         (static_cast<std::uint32_t>(bytes[udpPayloadOffset + 6]) << 8) |
                         static_cast<std::uint32_t>(bytes[udpPayloadOffset + 7]);
    const std::uint32_t rtpSsrc = (static_cast<std::uint32_t>(bytes[udpPayloadOffset + 8]) << 24) |
                         (static_cast<std::uint32_t>(bytes[udpPayloadOffset + 9]) << 16) |
                         (static_cast<std::uint32_t>(bytes[udpPayloadOffset + 10]) << 8) |
                         static_cast<std::uint32_t>(bytes[udpPayloadOffset + 11]);

    const double rtpTimestampSeconds = (clockRate > 0)
        ? static_cast<double>(rtpTimestamp) / static_cast<double>(clockRate)
        : 0.0;

    {
        std::lock_guard<std::mutex> modelLock(m_liveModelMutex);
        m_liveModel->rtpInfo = std::make_shared<amviewer::types::streaminfo::RTPInfo>(
            rtpVersion, rtpSequenceNumber, rtpTimestamp, rtpSsrc, rtpTimestampSeconds,
            m_lastBurstPacketCount.load()
        );
    }

    if (rtpVersion == 2) {
        const std::size_t csrcCount = static_cast<std::size_t>(rtpFirst & 0x0FU);
        const bool hasExtension = (rtpFirst & 0x10U) != 0;
        rtpHeaderBytes = 12 + (csrcCount * 4);

        if (udpPayloadSize < rtpHeaderBytes) {
            return;
        }

        if (hasExtension) {
            if (udpPayloadSize < rtpHeaderBytes + 4) {
                return;
            }

            const std::size_t extLenIndex = udpPayloadOffset + rtpHeaderBytes + 2;
            const std::uint16_t extWords =
                static_cast<std::uint16_t>(
                    (static_cast<std::uint16_t>(bytes[extLenIndex]) << 8) |
                    static_cast<std::uint16_t>(bytes[extLenIndex + 1]));
            rtpHeaderBytes += 4 + (static_cast<std::size_t>(extWords) * 4);
            if (udpPayloadSize < rtpHeaderBytes) {
                return;
            }
        }
    }

    const std::size_t payloadOffset = udpOffset + 8 + rtpHeaderBytes;
    if (header->caplen <= payloadOffset) {
        return;
    }

    const u_char* payloadData = packetData + payloadOffset;
    const std::size_t payloadSize = header->caplen - payloadOffset;
    if (payloadSize == 0) {
        return;
    }

    {
        std::lock_guard<std::mutex> lock(m_mutex);
        const auto nowMs = static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::steady_clock::now().time_since_epoch())
                .count());
        m_lastFrameMonotonicMs.store(nowMs);

        // if (codec == "ST2110-41") {
        //     m_smpte2110_41 = "on";
        //     m_smpte2110_31 = "off";
        // } else if (codec == "AM824") {
        //     m_smpte2110_31 = "on";
        //     m_smpte2110_41 = "off";
        // }
    }

    if (codec == "ST2110-41") {
        process_st2110_41_payload(payloadData, payloadSize);
    } else if (codec == "AM824") {
        auto countPreambles = [](const u_char* data, std::size_t size) {
            std::size_t matches = 0;
            for (std::size_t index = 0; index + 3 < size; index += 4) {
                const std::uint32_t sample =
                    (static_cast<std::uint32_t>(data[index + 1]) << 16) |
                    (static_cast<std::uint32_t>(data[index + 2]) << 8) |
                    static_cast<std::uint32_t>(data[index + 3]);
                if (sample == 0x6f8720 || sample == 0x96f872 || sample == 0x54e1f0 || sample == 0xa54e1f) {
                    ++matches;
                }
            }
            return matches;
        };

        const std::size_t strippedScore = countPreambles(payloadData, payloadSize);
        const std::size_t rawScore = countPreambles(udpPayloadData, udpPayloadSize);

        if (strippedScore > 0 || rawScore == 0) {
            process_am824_payload(payloadData, payloadSize);
        } else {
            process_am824_payload(udpPayloadData, udpPayloadSize);
        }
    }
}

void CaptureService::process_st2110_41_payload(const u_char* payloadData, std::size_t payloadSize) {
    if (!payloadData || payloadSize < 8) {
        return;
    }

    const auto* payload = reinterpret_cast<const std::uint8_t*>(payloadData);

    const std::uint32_t dataItemType =
        ((static_cast<std::uint32_t>(payload[0]) << 24) |
         (static_cast<std::uint32_t>(payload[1]) << 16) |
         (static_cast<std::uint32_t>(payload[2]) << 8) |
         static_cast<std::uint32_t>(payload[3])) >> 10;

    std::size_t dataItemLengthWords =
        ((static_cast<std::uint32_t>(payload[2]) << 8) | static_cast<std::uint32_t>(payload[3])) & 0x1ff;
    if (dataItemLengthWords == 0) {
        return;
    }
    dataItemLengthWords -= 1;

    std::size_t dataItemLengthBytes = dataItemLengthWords * 4;
    const bool lastPacket = ((payload[2] & 0x2U) >> 1U) == 1U;

    const std::uint32_t segmentDataOffset =
        (static_cast<std::uint32_t>(payload[4]) << 24) |
        (static_cast<std::uint32_t>(payload[5]) << 16) |
        (static_cast<std::uint32_t>(payload[6]) << 8) |
        static_cast<std::uint32_t>(payload[7]);
    const bool firstPacket = segmentDataOffset == 0;

    if (payloadSize < 8) {
        return;
    }
    dataItemLengthBytes = std::min(dataItemLengthBytes, payloadSize - 8);

    bool parsedNewFrame = false;
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        // m_smpte2110_41 = "on";
        // m_smpte2110_31 = "off";

        std::ostringstream dit;
        dit << "0x" << std::hex << std::uppercase << dataItemType;
        m_ditValue = dit.str();

        if (firstPacket) {
            m_st2110_41Payload.clear();
            m_st2110_41ExpectedBytes = dataItemLengthBytes;
            m_st2110_41PacketsInBurst = 0;
        }

        // Count this IP packet as part of the in-progress reassembly burst.
        ++m_st2110_41PacketsInBurst;

        const std::size_t offsetBytes = static_cast<std::size_t>(segmentDataOffset) * 4;
        if (m_st2110_41Payload.size() < offsetBytes + dataItemLengthBytes) {
            m_st2110_41Payload.resize(offsetBytes + dataItemLengthBytes);
        }

        std::memcpy(m_st2110_41Payload.data() + offsetBytes, payload + 8, dataItemLengthBytes);

        if (!lastPacket) {
            return;
        }

        const bool isSadm = dataItemType == 0x3ff000 || dataItemType == 0x100;
        const bool isPmd = dataItemType == 0x3ff001;

        if (isPmd) {
            // m_pmd = "on";
            // m_sadm = "off";
            const auto nowMs = static_cast<std::uint64_t>(
                std::chrono::duration_cast<std::chrono::milliseconds>(
                    std::chrono::steady_clock::now().time_since_epoch())
                    .count());
            m_lastFrameMonotonicMs.store(nowMs);
            m_st2110_41Payload.clear();
            m_st2110_41ExpectedBytes = 0;

            {
                std::lock_guard<std::mutex> modelLock(m_liveModelMutex);
                if (m_liveModel) {
                    m_liveModel->metadata = std::make_shared<amviewer::types::metadata::pmd::PMDMetadata>();
                }
            }

            return;
        }

        if (!isSadm) {
            m_st2110_41Payload.clear();
            m_st2110_41ExpectedBytes = 0;
            {
                std::lock_guard<std::mutex> modelLock(m_liveModelMutex);
                if(m_liveModel) m_liveModel->metadata.reset();
            }
            return;
        }

        const auto nowMs = static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::steady_clock::now().time_since_epoch())
                .count());
        m_lastFrameMonotonicMs.store(nowMs);

        std::string xml;
        std::string extractError;
        if (!adm_xml::extract_st2127_xml(m_st2110_41Payload, xml, extractError)) {
            // m_sadm = "error";
            m_lastError = extractError;
            m_st2110_41Payload.clear();
            m_st2110_41ExpectedBytes = 0;
            return;
        }

        m_liveXml = xml;

        auto parsed = std::make_shared<amviewer::types::metadata::sadm::SADMMetadata>();
        std::string parseError;
        adm_xml::ParseInfo parseInfo;
        if (!adm_xml::parse_content(xml, *parsed, parseError, &parseInfo)) {
            m_lastError = parseError;
            m_st2110_41Payload.clear();
            m_st2110_41ExpectedBytes = 0;
            return;
        }

        {
            std::lock_guard<std::mutex> modelLock(m_liveModelMutex);
            if (m_liveModel) {
                m_liveModel->metadata = parsed;
            }
        }
        m_lastError.clear();
        parsedNewFrame = true;

        // Record how many IP packets were captured to build this frame so it
        // can be surfaced via RTPInfo on the next snapshot.
        m_lastBurstPacketCount.store(static_cast<std::uint32_t>(m_st2110_41PacketsInBurst));

        m_st2110_41Payload.clear();
        m_st2110_41ExpectedBytes = 0;
    }

    if (parsedNewFrame) {
        m_frameCount.fetch_add(1);
        fire_metadata_frame_callback();
    }
}

void CaptureService::process_am824_payload(const u_char* payloadData, std::size_t payloadSize) {
    if (!payloadData || payloadSize < 8) {
        return;
    }

    bool sawPa20 = false;
    bool sawPa24 = false;
    bool sawPb20 = false;
    bool sawPb24 = false;

    std::vector<std::uint32_t> words;
    words.reserve(payloadSize / 4);
    std::vector<std::uint8_t> rawWordBytes;
    rawWordBytes.reserve((payloadSize / 4) * 3);

    for (std::size_t index = 0; index + 3 < payloadSize; index += 4) {
        const std::uint32_t sample =
            (static_cast<std::uint32_t>(payloadData[index + 1]) << 16) |
            (static_cast<std::uint32_t>(payloadData[index + 2]) << 8) |
            static_cast<std::uint32_t>(payloadData[index + 3]);
        words.push_back(sample);
        rawWordBytes.push_back(static_cast<std::uint8_t>(payloadData[index + 1]));
        rawWordBytes.push_back(static_cast<std::uint8_t>(payloadData[index + 2]));
        rawWordBytes.push_back(static_cast<std::uint8_t>(payloadData[index + 3]));

        if (sample == 0x6f8720) {
            sawPa20 = true;
        } else if (sample == 0x96f872) {
            sawPa24 = true;
        } else if (sample == 0x54e1f0) {
            sawPb20 = true;
        } else if (sample == 0xa54e1f) {
            sawPb24 = true;
        }
    }

    bool parsedNewFrame = false;
    {
    std::lock_guard<std::mutex> lock(m_mutex);

    bool frameDetected = false;
    bool subframeDetected = false;
    bool metadataDetected = false;

    for (std::size_t i = 0; i + 4 < words.size(); ++i) {
        const std::uint32_t pa = words[i];
        int bitDepth = 0;
        if (pa == 0x6f8720) {
            bitDepth = 20;
        } else if (pa == 0x96f872) {
            bitDepth = 24;
        } else {
            continue;
        }

        const bool pbFrame = (i + 1 < words.size()) && (words[i + 1] == 0x54e1f0 || words[i + 1] == 0xa54e1f);
        const bool pbSubframe = (i + 2 < words.size()) && (words[i + 2] == 0x54e1f0 || words[i + 2] == 0xa54e1f);

        if (!pbFrame && !pbSubframe) {
            continue;
        }

        frameDetected = pbFrame;
        subframeDetected = !pbFrame && pbSubframe;

        const std::size_t pcIndex = pbFrame ? (i + 3) : (i + 4);
        if (pcIndex >= words.size()) {
            break;
        }

        const std::uint32_t pcWord = words[pcIndex] >> (24 - bitDepth);
        int dataType = static_cast<int>((pcWord >> (bitDepth - 16)) & 0x1f);
        if (dataType == 31) {
            const std::size_t peIndex = pcIndex + 1;
            if (peIndex < words.size()) {
                const std::uint32_t peWord = words[peIndex] >> (24 - bitDepth);
                dataType += static_cast<int>(peWord & 0xffff);
            }
        }

        if (dataType == 27 || dataType == 32) {
            metadataDetected = true;
        }
        break;
    }

    m_am824Deframer.receivePayload(reinterpret_cast<const std::uint8_t*>(payloadData), payloadSize);
    while (m_am824Deframer.haveFrame()) {
        Am824Frame frame = m_am824Deframer.popFrame();
        if (frame.payload.empty()) {
            continue;
        }

        std::string xml;
        std::string extractError;
        if (!adm_xml::extract_st2116_xml(frame.payload,
                                         frame.bitDepth,
                                         frame.assembleFlag,
                                         frame.formatFlag,
                                         xml,
                                         extractError)) {
            if (!extractError.empty()) {
                m_lastError = extractError;
            }
            continue;
        }

        auto parsed = std::make_shared<amviewer::types::metadata::sadm::SADMMetadata>();
        std::string parseError;
        adm_xml::ParseInfo parseInfo;
        if (!adm_xml::parse_content(xml, *parsed, parseError, &parseInfo)) {
            if (!parseError.empty()) {
                m_lastError = parseError;
            }
            continue;
        }

        m_liveXml = std::move(xml);
        {
            std::lock_guard<std::mutex> modelLock(m_liveModelMutex);
            if (m_liveModel) {
                m_liveModel->metadata = parsed;
            }
        }
        metadataDetected = true;
        parsedNewFrame = true;
        m_lastError.clear();
    }

    if (metadataDetected || sawPa20 || sawPa24 || sawPb20 || sawPb24) {
        const auto nowMs = static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::steady_clock::now().time_since_epoch())
                .count());
        m_lastFrameMonotonicMs.store(nowMs);
    }

    (void)frameDetected;
    (void)subframeDetected;
    (void)sawPa20;
    (void)sawPa24;
    (void)sawPb20;
    (void)sawPb24;
    } // end m_mutex scope

    if (parsedNewFrame) {
        m_frameCount.fetch_add(1);
        fire_metadata_frame_callback();
    }
}

void CaptureService::setMetadataFrameCallback(MetadataFrameCallback cb) {
    std::lock_guard<std::mutex> lock(m_callbackMutex);
    m_metadataFrameCallback = std::move(cb);
}

void CaptureService::fire_metadata_frame_callback() {
    MetadataFrameCallback cb;
    {
        std::lock_guard<std::mutex> lock(m_callbackMutex);
        cb = m_metadataFrameCallback;
    }
    if (cb) {
        try {
            cb();
        } catch (...) {
            // Callback failures must not take down the capture thread.
        }
    }
}

void CaptureService::reset_live_state_locked() {
    m_st2110_41Payload.clear();
    m_st2110_41ExpectedBytes = 0;
    m_st2110_41PacketsInBurst = 0;
    m_lastBurstPacketCount.store(0);

    m_ditValue = "N/A";
    m_liveXml.clear();
    m_lastFrameMonotonicMs = 0;

    {
        std::lock_guard<std::mutex> modelLock(m_liveModelMutex);
        if (m_liveModel) {
            m_liveModel->metadata.reset();
        }
    }

    m_am824Deframer.reset();
}

void CaptureService::capture_loop() {
    pcap_t* localHandle = nullptr;

    {
        std::lock_guard<std::mutex> lock(m_mutex);
        localHandle = m_handle;
    }

    if (!localHandle) {
        return;
    }

    const int result = pcap_loop(localHandle, 0, &CaptureService::packet_callback, reinterpret_cast<u_char*>(this));
    if (result < 0) {
        std::lock_guard<std::mutex> lock(m_mutex);
        if (m_handle) {
            m_lastError = std::string("Capture loop error: ") + pcap_geterr(m_handle);
        }
    }
}
