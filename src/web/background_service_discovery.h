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

#include "service_discovery.h"

#include <condition_variable>
#include <cstdint>
#include <functional>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_map>
#include <vector>

class BackgroundServiceDiscovery {
public:
    static BackgroundServiceDiscovery& instance();

    void set_interface(std::string interfaceName);
    std::string get_interface() const {
        std::lock_guard<std::mutex> lock(m_mutex);
        return m_interfaceName;
    };
    std::vector<DiscoveredService> snapshot() const;

    using ServicesChangedCallback = std::function<void(std::vector<DiscoveredService>)>;
    // Registers a callback invoked from the discovery worker thread whenever
    // the discovered-services set actually changes. The callback receives a
    // fresh copy of the current services and runs without any
    // BackgroundServiceDiscovery mutex held.
    void set_services_changed_callback(ServicesChangedCallback cb);

private:
    BackgroundServiceDiscovery();
    ~BackgroundServiceDiscovery();

    BackgroundServiceDiscovery(const BackgroundServiceDiscovery&) = delete;
    BackgroundServiceDiscovery& operator=(const BackgroundServiceDiscovery&) = delete;

    void run();

    mutable std::mutex m_mutex;
    std::condition_variable m_cv;
    std::thread m_worker;

    bool m_stop = false;
    bool m_forceRefresh = false;
    std::string m_interfaceName;
    std::vector<DiscoveredService> m_services;

    struct TimedService {
        DiscoveredService service;
        std::uint64_t lastSeenMs = 0;
    };
    std::unordered_map<std::string, TimedService> m_serviceCache;

    // Persistent SAP socket (owned by the worker thread, not protected by m_mutex).
    int m_sapSocket = -1;
    std::string m_sapSocketInterface;

    mutable std::mutex m_callbackMutex;
    ServicesChangedCallback m_servicesChangedCallback;
};
