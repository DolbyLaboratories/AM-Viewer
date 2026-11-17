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

#include <atomic>
#include <chrono>
#include <cstdint>
#include <functional>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

#include "am824_deframer.h"
#include "adm_xml_parser.h"
#include "model/types.hpp"
#include <memory>

struct pcap;
struct bpf_program;

struct CaptureSnapshot {
    bool active = false;
    std::string interfaceName;
    std::string address;
    int port = 0;
    std::uint64_t packetCount = 0;
    std::uint64_t frameCount = 0;
    std::uint64_t packetTimestampMs = 0;
    std::string lastError;
    std::shared_ptr<amviewer::types::streaminfo::StreamInfoBase> stream;
    std::shared_ptr<amviewer::types::streaminfo::RTPInfo> rtpInfo;
    std::string ditValue;
    std::string liveXml;
};

class CaptureService {
public:
    CaptureService();
    ~CaptureService();

    static std::vector<std::string> list_interfaces();

    bool start(const std::string& interfaceName,
               const std::string& address,
               int port,
               const std::string& codec,
               int clockRate,
               std::string& error);
    void stop();
    bool running() const;
    CaptureSnapshot snapshot() const;
    Am824Deframer::Stats getDeframerStats() const;

    using MetadataFrameCallback = std::function<void()>;
    // Registers a callback invoked on the capture thread whenever a fresh
    // SADM metadata frame is parsed. Pass nullptr to clear. Callback is
    // invoked without any CaptureService mutex held, so it may call snapshot().
    void setMetadataFrameCallback(MetadataFrameCallback cb);

private:
    void fire_metadata_frame_callback();
    static void packet_callback(u_char* userData, const struct pcap_pkthdr* header, const u_char* packetData);
    void process_packet(const struct pcap_pkthdr* header, const u_char* packetData);
    void process_st2110_41_payload(const u_char* payloadData, std::size_t payloadSize);
    void process_am824_payload(const u_char* payloadData, std::size_t payloadSize);
    void reset_live_state_locked();
    void capture_loop();

private:
    mutable std::mutex m_mutex;
    pcap* m_handle;
    std::thread m_thread;
    std::atomic<bool> m_running;
    std::atomic<std::uint64_t> m_packetCount;
    std::atomic<std::uint64_t> m_frameCount;
    std::atomic<std::uint64_t> m_lastPacketMonotonicMs;
    std::atomic<std::uint64_t> m_lastFrameMonotonicMs;
    std::string m_interfaceName;
    std::string m_address;
    std::string m_codec;
    int m_port;
    // Audio source clock rate (Hz) used to convert RTP timestamps to seconds.
    // 0 disables the conversion (RTPInfo.timestampSeconds stays 0.0).
    int m_clockRate;
    std::string m_lastError;
    int m_datalinkType;

    std::vector<std::uint8_t> m_st2110_41Payload;
    std::size_t m_st2110_41ExpectedBytes;
    // IP packets accumulated for the in-progress ST2110-41 reassembly burst.
    std::size_t m_st2110_41PacketsInBurst;
    // Packet count of the most recently completed metadata frame's burst.
    std::atomic<std::uint32_t> m_lastBurstPacketCount;
    std::string m_ditValue;

    std::string m_liveXml;
    Am824Deframer m_am824Deframer;

    std::shared_ptr<amviewer::types::streaminfo::StreamInfoBase>     m_liveModel;
    mutable std::mutex                                               m_liveModelMutex;

    MetadataFrameCallback                                            m_metadataFrameCallback;
    mutable std::mutex                                               m_callbackMutex;
};
