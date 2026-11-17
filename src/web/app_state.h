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

#include "model/types.hpp"
#include "adm_xml_parser.h"

#include <mutex>
#include <memory>
#include <string>
#include <atomic>
#include <vector>

class CaptureService;

struct ServiceSelection {
    std::string name;
    std::string system;
    std::string interfaceName;
    std::string address;
    int port = 0;
    std::string codec;
    std::string audio;
    // Audio source clock rate (Hz) extracted from the SDP rtpmap line.
    // Used to convert RTP timestamps to seconds. 0 when unknown.
    int sampleRate = 0;
};

struct AppState {
    mutable std::mutex mutex;

    std::string loadedFile;
    std::string lastError;
    std::string lastUpdated;
    
    std::unique_ptr<ServiceSelection> selectedService;
    std::shared_ptr<CaptureService> captureService;

    std::shared_ptr<amviewer::types::metadata::MetadataBase> metadata;
    std::shared_ptr<amviewer::types::streaminfo::RTPInfo> rtpInfo;
    uint64_t metadataTimestampMs = 0;
    uint64_t metadataFrameCounter = 0;

    // Shutdown coordination
    std::atomic<bool> shouldShutdown{false};
};
