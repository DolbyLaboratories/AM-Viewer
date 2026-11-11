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

#include "background_service_discovery.h"

#include <algorithm>
#include <chrono>

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <unistd.h>

#include "logging.h"

namespace {
// SAP RFC 2974 allows announcements as infrequently as every 30 s.  Keep
// entries alive for 3× that interval so a single missed packet does not drop
// a service from the list.
constexpr std::uint64_t kSapKeepAliveMs    = 90000;
constexpr std::uint64_t kOtherKeepAliveMs  = 10000;

// How often (ms) to poll the persistent SAP socket in the worker loop.
constexpr int kSapPollMs = 200;

// How often (ms) to re-run Ravenna/mDNS discovery.
constexpr std::uint64_t kRavennaIntervalMs = 8000;

std::uint64_t now_monotonic_ms() {
    return static_cast<std::uint64_t>(
        std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now().time_since_epoch())
            .count());
}

std::string service_key(const DiscoveredService& service) {
    return service.system + "|" + service.name + "|" + service.address + "|" + std::to_string(service.port) + "|" + service.codec;
}
}

BackgroundServiceDiscovery& BackgroundServiceDiscovery::instance() {
    static BackgroundServiceDiscovery s_instance;
    return s_instance;
}

BackgroundServiceDiscovery::BackgroundServiceDiscovery() {
    m_worker = std::thread([this]() { run(); });
}

BackgroundServiceDiscovery::~BackgroundServiceDiscovery() {
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        m_stop = true;
    }
    m_cv.notify_all();
    if (m_worker.joinable()) {
        m_worker.join();
    }
}

void BackgroundServiceDiscovery::set_interface(std::string interfaceName) {
    AMV_LOG_DEBUG("set_interface \"{}\"", interfaceName);
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        if (m_interfaceName != interfaceName) {
            m_interfaceName = std::move(interfaceName);
            m_services.clear();
            m_serviceCache.clear();
        }
        m_forceRefresh = true;
    }
    m_cv.notify_one();
}

std::vector<DiscoveredService> BackgroundServiceDiscovery::snapshot() const {
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_services;
}

void BackgroundServiceDiscovery::set_services_changed_callback(ServicesChangedCallback cb) {
    std::lock_guard<std::mutex> lock(m_callbackMutex);
    m_servicesChangedCallback = std::move(cb);
}

void BackgroundServiceDiscovery::run() {
    std::uint64_t lastRavennaMs = 0;
    std::vector<DiscoveredService> lastFired;

    auto maybe_fire_changed = [this, &lastFired](const std::vector<DiscoveredService>& current) {
        if (current == lastFired) {
            return;
        }
        lastFired = current;
        ServicesChangedCallback cb;
        {
            std::lock_guard<std::mutex> lock(m_callbackMutex);
            cb = m_servicesChangedCallback;
        }
        AMV_LOG_DEBUG("maybe_fire_changed count={}", current.size());
        if (cb) {
            try {
                cb(current);
            } catch (...) {
                // Callback failures must not take down the discovery thread.
            }
        }
    };

    auto rebuild_services_locked = [this]() {
        const std::uint64_t nowMs = now_monotonic_ms();
        for (auto it = m_serviceCache.begin(); it != m_serviceCache.end();) {
            const std::uint64_t ttl = (it->second.service.system == "SAP")
                                          ? kSapKeepAliveMs
                                          : kOtherKeepAliveMs;
            if (nowMs > it->second.lastSeenMs + ttl) {
                it = m_serviceCache.erase(it);
            } else {
                ++it;
            }
        }
        m_services.clear();
        m_services.reserve(m_serviceCache.size());
        for (const auto& kv : m_serviceCache) {
            m_services.push_back(kv.second.service);
        }
        std::sort(m_services.begin(), m_services.end(),
                  [](const DiscoveredService& a, const DiscoveredService& b) {
                      if (a.system == b.system) return a.name < b.name;
                      return a.system < b.system;
                  });
    };

    AMV_LOG_DEBUG("BackgroundServiceDiscovery started");

    while (true) {
        // ----------------------------------------------------------------
        // 1. Wait briefly for a wakeup signal or interface to become set.
        // ----------------------------------------------------------------
        std::string activeInterface;
        bool stop = false;
        {
            std::unique_lock<std::mutex> lock(m_mutex);
            m_cv.wait_for(lock, std::chrono::milliseconds(50), [this]() {
                return m_stop || m_forceRefresh || !m_interfaceName.empty();
            });
            stop = m_stop;
            activeInterface = m_interfaceName;
            m_forceRefresh = false;
        }

        if (stop) {
            if (m_sapSocket >= 0) {
                ::close(m_sapSocket);
                m_sapSocket = -1;
            }
            return;
        }

        if (activeInterface.empty()) {
            continue;
        }

        // ----------------------------------------------------------------
        // 2. (Re-)open the persistent SAP socket when the interface changes.
        // ----------------------------------------------------------------
        if (m_sapSocket < 0 || activeInterface != m_sapSocketInterface) {
            if (m_sapSocket >= 0) {
                ::close(m_sapSocket);
                m_sapSocket = -1;
            }
            m_sapSocket = ServiceDiscovery::open_sap_socket(activeInterface);
            m_sapSocketInterface = activeInterface;
        }

        // ----------------------------------------------------------------
        // 3. Drain all pending SAP datagrams immediately (non-blocking poll).
        // ----------------------------------------------------------------
        if (m_sapSocket >= 0) {
            // Use a short select so we complete this step promptly.
            fd_set readSet;
            FD_ZERO(&readSet);
            FD_SET(m_sapSocket, &readSet);
            timeval tv{};
            tv.tv_sec = 0;
            tv.tv_usec = kSapPollMs * 1000;
            const int ready = ::select(m_sapSocket + 1, &readSet, nullptr, nullptr, &tv);

            if (ready > 0 && FD_ISSET(m_sapSocket, &readSet)) {
                std::vector<std::uint8_t> buf(4096);
                // Drain all datagrams queued on this socket in one pass.
                while (true) {
                    sockaddr_in peer{};
                    socklen_t peerLen = sizeof(peer);
                    const ssize_t n = ::recvfrom(m_sapSocket,
                                                 buf.data(),
                                                 buf.size(),
                                                 MSG_DONTWAIT,
                                                 reinterpret_cast<sockaddr*>(&peer),
                                                 &peerLen);
                    if (n <= 0) break;
                    buf.resize(static_cast<std::size_t>(n));

                    char sourceAddr[INET_ADDRSTRLEN] = {0};
                    std::string sourceIp;
                    if (::inet_ntop(AF_INET, &peer.sin_addr, sourceAddr, sizeof(sourceAddr)) != nullptr) {
                        sourceIp = sourceAddr;
                    }
                    const int sourcePort = ntohs(peer.sin_port);

                    DiscoveredService service;
                    if (ServiceDiscovery::parse_sap_packet(buf, service, sourceIp, sourcePort)) {
                        const std::uint64_t nowMs = now_monotonic_ms();
                        const std::string key = service_key(service);
                        std::vector<DiscoveredService> post;
                        bool didRebuild = false;
                        {
                            std::lock_guard<std::mutex> lock(m_mutex);
                            if (activeInterface == m_interfaceName) {
                                auto& entry = m_serviceCache[key];
                                entry.service = service;
                                entry.lastSeenMs = nowMs;
                                rebuild_services_locked();
                                post = m_services;
                                didRebuild = true;
                            }
                        }
                        if (didRebuild) maybe_fire_changed(post);
                    }

                    buf.resize(4096);
                }
            }
        }

        // ----------------------------------------------------------------
        // 4. Periodic Ravenna/mDNS discovery (non-blocking relative to SAP).
        // ----------------------------------------------------------------
        const std::uint64_t nowMs = now_monotonic_ms();
        if (nowMs - lastRavennaMs >= kRavennaIntervalMs) {
            lastRavennaMs = nowMs;
            // Use a short timeout so Ravenna never stalls the SAP listener.
            auto ravenna = ServiceDiscovery::discover_ravenna(800, 128);
            if (!ravenna.empty()) {
                const std::uint64_t ts = now_monotonic_ms();
                std::vector<DiscoveredService> post;
                bool didRebuild = false;
                {
                    std::lock_guard<std::mutex> lock(m_mutex);
                    if (activeInterface == m_interfaceName) {
                        for (auto& svc : ravenna) {
                            auto& entry = m_serviceCache[service_key(svc)];
                            entry.service = std::move(svc);
                            entry.lastSeenMs = ts;
                        }
                        rebuild_services_locked();
                        post = m_services;
                        didRebuild = true;
                    }
                }
                if (didRebuild) maybe_fire_changed(post);
            }
        }

        // ----------------------------------------------------------------
        // 5. Periodic stale-entry eviction (runs every loop regardless).
        // ----------------------------------------------------------------
        std::vector<DiscoveredService> post;
        bool didRebuild = false;
        {
            std::lock_guard<std::mutex> lock(m_mutex);
            if (activeInterface == m_interfaceName) {
                rebuild_services_locked();
                post = m_services;
                didRebuild = true;
            }
        }
        if (didRebuild) maybe_fire_changed(post);
    }
}
