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

#include "service_discovery.h"

#include <algorithm>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <map>
#include <set>
#include <string>
#include <vector>

#include <arpa/inet.h>
#include <ifaddrs.h>
#include <net/if.h>
#include <netinet/in.h>
#include <netdb.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <unistd.h>

#ifdef __APPLE__
#include <dns_sd.h>
#endif

namespace {

constexpr const char* kSapAddress = "239.255.255.255";
constexpr int kSapPort = 9875;

std::string trim_copy(const std::string& value) {
    std::size_t start = 0;
    while (start < value.size() && std::isspace(static_cast<unsigned char>(value[start]))) {
        ++start;
    }
    std::size_t end = value.size();
    while (end > start && std::isspace(static_cast<unsigned char>(value[end - 1]))) {
        --end;
    }
    return value.substr(start, end - start);
}

std::string to_upper_copy(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char c) { return static_cast<char>(std::toupper(c)); });
    return value;
}

std::string sanitize_sdp_text(const std::string& value) {
    std::string out;
    out.reserve(value.size() * 2);
    for (unsigned char c : value) {
        if (c == '\r') {
            continue;
        }
        if (c == '\n') {
            out += "\\n";
            continue;
        }
        if (c < 0x20) {
            out.push_back(' ');
            continue;
        }
        out.push_back(static_cast<char>(c));
    }
    return out;
}

bool get_interface_ipv4(const std::string& interfaceName, in_addr& outAddr) {
    if (interfaceName.empty()) {
        outAddr.s_addr = htonl(INADDR_ANY);
        return true;
    }

    ifaddrs* ifaddr = nullptr;
    if (getifaddrs(&ifaddr) != 0) {
        return false;
    }

    bool found = false;
    for (ifaddrs* cursor = ifaddr; cursor; cursor = cursor->ifa_next) {
        if (!cursor->ifa_name || !cursor->ifa_addr) {
            continue;
        }
        if (interfaceName != cursor->ifa_name) {
            continue;
        }
        if (cursor->ifa_addr->sa_family != AF_INET) {
            continue;
        }
        if ((cursor->ifa_flags & IFF_UP) == 0) {
            continue;
        }

        outAddr = reinterpret_cast<sockaddr_in*>(cursor->ifa_addr)->sin_addr;
        found = true;
        break;
    }

    freeifaddrs(ifaddr);
    return found;
}

bool parse_sap_payload(const std::vector<std::uint8_t>& data, std::string& sdpText) {
    sdpText.clear();

    if (data.size() < 8) {
        return false;
    }

    const std::uint8_t flags = data[0];
    const bool isIPv6 = ((flags >> 4) & 0x01) != 0;
    const bool isEncrypted = ((flags >> 1) & 0x01) != 0;
    const std::uint8_t authLen = data[1];

    std::size_t offset = 4;
    offset += isIPv6 ? 16 : 4;
    offset += static_cast<std::size_t>(authLen) * 4;
    if (isEncrypted) {
        offset += 4;
    }

    if (offset >= data.size()) {
        return false;
    }

    std::size_t payloadTypeEnd = offset;
    while (payloadTypeEnd < data.size() && data[payloadTypeEnd] != 0) {
        ++payloadTypeEnd;
    }
    if (payloadTypeEnd >= data.size()) {
        return false;
    }

    offset = payloadTypeEnd + 1;
    if (offset >= data.size()) {
        return false;
    }

    sdpText.assign(reinterpret_cast<const char*>(data.data() + offset), data.size() - offset);
    return true;
}

bool parse_int(const std::string& text, int& outValue) {
    try {
        outValue = std::stoi(text);
        return true;
    } catch (...) {
        return false;
    }
}

} // namespace (reopen below)

DiscoveredService parse_sdp(const std::string& sdpText) {
    DiscoveredService service;
    service.system = "SAP";
    service.sdpText = sanitize_sdp_text(sdpText);

    std::string rtpmapCodec;
    std::string rtpmapClock;
    int rtpmapChannels = 0;

    std::size_t pos = 0;
    while (pos < sdpText.size()) {
        std::size_t lineEnd = sdpText.find('\n', pos);
        if (lineEnd == std::string::npos) {
            lineEnd = sdpText.size();
        }
        std::string line = sdpText.substr(pos, lineEnd - pos);
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        pos = lineEnd + 1;

        if (line.size() < 2 || line[1] != '=') {
            continue;
        }

        const std::string value = trim_copy(line.substr(2));
        if (line.rfind("s=", 0) == 0) {
            service.name = value;
        } else if (line.rfind("c=", 0) == 0) {
            const std::size_t ipPos = value.find("IP4 ");
            if (ipPos != std::string::npos) {
                std::string addr = value.substr(ipPos + 4);
                const std::size_t slash = addr.find('/');
                if (slash != std::string::npos) {
                    addr = addr.substr(0, slash);
                }
                service.address = trim_copy(addr);
            }
        } else if (line.rfind("m=", 0) == 0) {
            const std::string media = value;
            const std::size_t firstSpace = media.find(' ');
            const std::size_t secondSpace = media.find(' ', firstSpace + 1);
            if (firstSpace != std::string::npos && secondSpace != std::string::npos) {
                const std::string mediaType = to_upper_copy(trim_copy(media.substr(0, firstSpace)));
                if (mediaType == "AUDIO" || mediaType == "APPLICATION") {
                    const std::string portText = media.substr(firstSpace + 1, secondSpace - (firstSpace + 1));
                    parse_int(portText, service.port);
                }
            }
        } else if (line.rfind("a=rtpmap:", 0) == 0) {
            const std::size_t space = value.find(' ');
            if (space != std::string::npos) {
                const std::string encPart = value.substr(space + 1);
                const std::size_t slash1 = encPart.find('/');
                if (slash1 != std::string::npos) {
                    rtpmapCodec = encPart.substr(0, slash1);
                    const std::size_t slash2 = encPart.find('/', slash1 + 1);
                    if (slash2 == std::string::npos) {
                        rtpmapClock = encPart.substr(slash1 + 1);
                    } else {
                        rtpmapClock = encPart.substr(slash1 + 1, slash2 - (slash1 + 1));
                        parse_int(encPart.substr(slash2 + 1), rtpmapChannels);
                    }
                }
            }
        }
    }

    std::string codecUpper = to_upper_copy(rtpmapCodec);
    if (codecUpper == "AM824") {
        service.codec = "AM824";
    } else if (codecUpper == "ST2110-41" || codecUpper == "ST 2110-41") {
        service.codec = "ST2110-41";
    } else {
        service.codec = rtpmapCodec;
    }

    if (!rtpmapClock.empty()) {
        parse_int(rtpmapClock, service.sampleRate);
    }
    service.channels = rtpmapChannels;

    return service;
}

namespace {

bool is_supported_for_metadata(const DiscoveredService& service) {
    return service.codec == "AM824" || service.codec == "ST2110-41";
}

std::string percent_encode(const std::string& value) {
    static const char* hex = "0123456789ABCDEF";
    std::string out;
    out.reserve(value.size() * 3);
    for (unsigned char c : value) {
        if ((c >= 'a' && c <= 'z') ||
            (c >= 'A' && c <= 'Z') ||
            (c >= '0' && c <= '9') ||
            c == '-' || c == '_' || c == '.' || c == '~') {
            out.push_back(static_cast<char>(c));
        } else {
            out.push_back('%');
            out.push_back(hex[(c >> 4) & 0x0F]);
            out.push_back(hex[c & 0x0F]);
        }
    }
    return out;
}

std::string rtsp_describe_sdp(const std::string& host, int port, const std::string& serviceName) {
    if (host.empty() || port <= 0) {
        return {};
    }

    addrinfo hints{};
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    addrinfo* result = nullptr;
    const std::string portText = std::to_string(port);
    if (::getaddrinfo(host.c_str(), portText.c_str(), &hints, &result) != 0) {
        return {};
    }

    int sock = -1;
    for (addrinfo* ai = result; ai; ai = ai->ai_next) {
        sock = ::socket(ai->ai_family, ai->ai_socktype, ai->ai_protocol);
        if (sock < 0) {
            continue;
        }

        timeval timeout{};
        timeout.tv_sec = 1;
        timeout.tv_usec = 0;
        ::setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
        ::setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

        if (::connect(sock, ai->ai_addr, ai->ai_addrlen) == 0) {
            break;
        }

        ::close(sock);
        sock = -1;
    }
    ::freeaddrinfo(result);

    if (sock < 0) {
        return {};
    }

    const std::string encodedName = percent_encode(serviceName);
    const std::string request =
        "DESCRIBE rtsp://" + host + ":" + std::to_string(port) + "/by-name/" + encodedName +
        " RTSP/1.0\r\nCSeq: 1\r\n\r\n";

    if (::send(sock, request.c_str(), request.size(), 0) < 0) {
        ::close(sock);
        return {};
    }

    std::string response;
    response.reserve(4096);
    char buffer[2048];
    while (true) {
        const ssize_t n = ::recv(sock, buffer, sizeof(buffer), 0);
        if (n <= 0) {
            break;
        }
        response.append(buffer, static_cast<std::size_t>(n));
        if (response.size() > 256 * 1024) {
            break;
        }
    }
    ::close(sock);

    std::size_t sdpStart = response.find("\r\n\r\n");
    if (sdpStart == std::string::npos) {
        sdpStart = response.find("\n\n");
        if (sdpStart == std::string::npos) {
            return {};
        }
        sdpStart += 2;
    } else {
        sdpStart += 4;
    }

    return trim_copy(response.substr(sdpStart));
}

#ifdef __APPLE__
struct BrowseContext {
    struct PendingService {
        std::string name;
        uint32_t interfaceIndex = 0;
        std::string regType;
        std::string domain;
    };

    std::vector<PendingService> pending;
    std::set<std::string> dedup;
};

void DNSSD_API ravenna_browse_callback(DNSServiceRef,
                                       DNSServiceFlags flags,
                                       uint32_t interfaceIndex,
                                       DNSServiceErrorType errorCode,
                                       const char* serviceName,
                                       const char* regtype,
                                       const char* replyDomain,
                                       void* context) {
    if (errorCode != kDNSServiceErr_NoError) {
        return;
    }
    if ((flags & kDNSServiceFlagsAdd) == 0) {
        return;
    }
    if (!serviceName || !regtype || !replyDomain) {
        return;
    }

    auto* ctx = static_cast<BrowseContext*>(context);
    const std::string key = std::string(serviceName) + "|" + regtype + "|" + replyDomain;
    if (!ctx->dedup.insert(key).second) {
        return;
    }

    ctx->pending.push_back({serviceName, interfaceIndex, regtype, replyDomain});
}

struct ResolveContext {
    bool done = false;
    bool ok = false;
    std::string host;
    int port = 0;
};

void DNSSD_API ravenna_resolve_callback(DNSServiceRef,
                                        DNSServiceFlags,
                                        uint32_t,
                                        DNSServiceErrorType errorCode,
                                        const char*,
                                        const char* hosttarget,
                                        uint16_t port,
                                        uint16_t,
                                        const unsigned char*,
                                        void* context) {
    auto* ctx = static_cast<ResolveContext*>(context);
    ctx->done = true;
    if (errorCode != kDNSServiceErr_NoError || !hosttarget) {
        ctx->ok = false;
        return;
    }

    ctx->ok = true;
    ctx->host = hosttarget;
    if (!ctx->host.empty() && ctx->host.back() == '.') {
        ctx->host.pop_back();
    }
    ctx->port = ntohs(port);
}

void process_dns_events(DNSServiceRef ref, int timeoutMs) {
    const int fd = DNSServiceRefSockFD(ref);
    if (fd < 0) {
        return;
    }

    fd_set readSet;
    FD_ZERO(&readSet);
    FD_SET(fd, &readSet);

    timeval tv{};
    tv.tv_sec = timeoutMs / 1000;
    tv.tv_usec = (timeoutMs % 1000) * 1000;

    const int ready = ::select(fd + 1, &readSet, nullptr, nullptr, &tv);
    if (ready > 0 && FD_ISSET(fd, &readSet)) {
        DNSServiceProcessResult(ref);
    }
}
#endif

} // namespace

std::vector<DiscoveredService> ServiceDiscovery::discover_ravenna(int timeoutMs,
                                                                  std::size_t maxServices) {
    std::vector<DiscoveredService> services;

#ifndef __APPLE__
    (void)timeoutMs;
    (void)maxServices;
    return services;
#else
    if (timeoutMs < 1) {
        timeoutMs = 1;
    }

    DNSServiceRef browseRef = nullptr;
    BrowseContext browseContext;

    const DNSServiceErrorType browseErr = DNSServiceBrowse(&browseRef,
                                                           0,
                                                           0,
                                                           "_rtsp._tcp,_ravenna_session",
                                                           nullptr,
                                                           ravenna_browse_callback,
                                                           &browseContext);
    if (browseErr != kDNSServiceErr_NoError || !browseRef) {
        return services;
    }

    const int rounds = std::max(1, timeoutMs / 200);
    for (int i = 0; i < rounds; ++i) {
        process_dns_events(browseRef, 200);
    }
    DNSServiceRefDeallocate(browseRef);

    for (const auto& pending : browseContext.pending) {
        if (services.size() >= maxServices) {
            break;
        }

        DNSServiceRef resolveRef = nullptr;
        ResolveContext resolveContext;
        const DNSServiceErrorType resolveErr = DNSServiceResolve(&resolveRef,
                                                                 0,
                                                                 pending.interfaceIndex,
                                                                 pending.name.c_str(),
                                                                 pending.regType.c_str(),
                                                                 pending.domain.c_str(),
                                                                 ravenna_resolve_callback,
                                                                 &resolveContext);
        if (resolveErr != kDNSServiceErr_NoError || !resolveRef) {
            continue;
        }

        process_dns_events(resolveRef, 400);
        DNSServiceRefDeallocate(resolveRef);

        if (!resolveContext.ok || resolveContext.host.empty() || resolveContext.port <= 0) {
            continue;
        }

        const std::string sdp = rtsp_describe_sdp(resolveContext.host, resolveContext.port, pending.name);
        if (sdp.empty()) {
            continue;
        }

        DiscoveredService service = parse_sdp(sdp);
        service.system = "Ravenna";
        if (service.name.empty()) {
            service.name = pending.name;
        }
        if (!is_supported_for_metadata(service)) {
            continue;
        }
        if (service.address.empty()) {
            service.address = resolveContext.host;
        }
        if (service.port <= 0) {
            service.port = resolveContext.port;
        }

        services.push_back(std::move(service));
    }

    std::sort(services.begin(), services.end(), [](const DiscoveredService& a, const DiscoveredService& b) {
        return a.name < b.name;
    });

    return services;
#endif
}

std::vector<DiscoveredService> ServiceDiscovery::discover_all(const std::string& interfaceName,
                                                              int timeoutMs,
                                                              std::size_t maxServices) {
    std::vector<DiscoveredService> result = discover_sap(interfaceName, timeoutMs, maxServices);
    const int ravennaTimeoutMs = std::min(600, std::max(100, timeoutMs / 10));
    std::vector<DiscoveredService> ravenna = discover_ravenna(ravennaTimeoutMs, maxServices);

    std::set<std::string> dedup;
    for (const auto& service : result) {
        dedup.insert(service.system + "|" + service.name + "|" + service.address + "|" + std::to_string(service.port) + "|" + service.codec);
    }

    for (auto& service : ravenna) {
        if (result.size() >= maxServices) {
            break;
        }
        const std::string key = service.system + "|" + service.name + "|" + service.address + "|" + std::to_string(service.port) + "|" + service.codec;
        if (dedup.insert(key).second) {
            result.push_back(std::move(service));
        }
    }

    std::sort(result.begin(), result.end(), [](const DiscoveredService& a, const DiscoveredService& b) {
        if (a.system == b.system) {
            return a.name < b.name;
        }
        return a.system < b.system;
    });

    return result;
}

std::vector<DiscoveredService> ServiceDiscovery::discover_sap(const std::string& interfaceName,
                                                              int timeoutMs,
                                                              std::size_t maxServices) {
    std::vector<DiscoveredService> services;
    std::set<std::string> dedupKeys;

    const int sock = ::socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        return services;
    }

    int reuse = 1;
    (void)::setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));
#ifdef SO_REUSEPORT
    (void)::setsockopt(sock, SOL_SOCKET, SO_REUSEPORT, &reuse, sizeof(reuse));
#endif

    sockaddr_in bindAddr{};
    bindAddr.sin_family = AF_INET;
    bindAddr.sin_port = htons(kSapPort);

#ifdef __APPLE__
    // Match Qt/legacy behavior on macOS: bind to SAP multicast address first.
    if (::inet_pton(AF_INET, kSapAddress, &bindAddr.sin_addr) != 1) {
        ::close(sock);
        return services;
    }
    if (::bind(sock, reinterpret_cast<sockaddr*>(&bindAddr), sizeof(bindAddr)) != 0) {
        bindAddr.sin_addr.s_addr = htonl(INADDR_ANY);
        if (::bind(sock, reinterpret_cast<sockaddr*>(&bindAddr), sizeof(bindAddr)) != 0) {
            ::close(sock);
            return services;
        }
    }
#else
    bindAddr.sin_addr.s_addr = htonl(INADDR_ANY);
    if (::bind(sock, reinterpret_cast<sockaddr*>(&bindAddr), sizeof(bindAddr)) != 0) {
        ::close(sock);
        return services;
    }
#endif

    in_addr ifaceAddr{};
    const bool hasInterfaceIp = get_interface_ipv4(interfaceName, ifaceAddr);
    if (!hasInterfaceIp) {
        ifaceAddr.s_addr = htonl(INADDR_ANY);
    }

    ip_mreq mreq{};
    if (::inet_pton(AF_INET, kSapAddress, &mreq.imr_multiaddr) != 1) {
        ::close(sock);
        return services;
    }
    mreq.imr_interface = ifaceAddr;

    if (::setsockopt(sock, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) != 0) {
        // Fallback: try default interface membership if specific interface join fails.
        mreq.imr_interface.s_addr = htonl(INADDR_ANY);
        if (::setsockopt(sock, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) != 0) {
            ::close(sock);
            return services;
        }
    }

    if (timeoutMs < 1) {
        timeoutMs = 1;
    }

    const auto endTime = static_cast<long long>(timeoutMs);
    long long waitedMs = 0;
    constexpr int kStepMs = 200;
    constexpr int kPostFirstPacketWindowMs = 300;
    long long firstPacketAtMs = -1;

    while (waitedMs < endTime && services.size() < maxServices) {
        if (firstPacketAtMs >= 0 && (waitedMs - firstPacketAtMs) >= kPostFirstPacketWindowMs) {
            break;
        }

        fd_set readSet;
        FD_ZERO(&readSet);
        FD_SET(sock, &readSet);

        timeval step{};
        const int remainingMs = static_cast<int>(std::min<long long>(kStepMs, endTime - waitedMs));
        step.tv_sec = remainingMs / 1000;
        step.tv_usec = (remainingMs % 1000) * 1000;

        const int ready = ::select(sock + 1, &readSet, nullptr, nullptr, &step);
        waitedMs += remainingMs;
        if (ready <= 0 || !FD_ISSET(sock, &readSet)) {
            continue;
        }

        std::vector<std::uint8_t> buffer(2048);
        sockaddr_in peer{};
        socklen_t peerLen = sizeof(peer);
        const ssize_t received = ::recvfrom(sock,
                                            buffer.data(),
                                            buffer.size(),
                                            0,
                                            reinterpret_cast<sockaddr*>(&peer),
                                            &peerLen);
        if (received <= 0) {
            continue;
        }
        buffer.resize(static_cast<std::size_t>(received));

        char sourceAddr[INET_ADDRSTRLEN] = {0};
        std::string sourceIp;
        if (::inet_ntop(AF_INET, &peer.sin_addr, sourceAddr, sizeof(sourceAddr)) != nullptr) {
            sourceIp = sourceAddr;
        }
        const int sourcePort = ntohs(peer.sin_port);

        DiscoveredService service;
        if (!ServiceDiscovery::parse_sap_packet(buffer, service, sourceIp, sourcePort)) {
            continue;
        }

        const std::string key = service.system + "|" + service.name + "|" + service.address + "|" + std::to_string(service.port) + "|" + service.codec;
        if (dedupKeys.insert(key).second) {
            services.push_back(std::move(service));
            if (firstPacketAtMs < 0) {
                firstPacketAtMs = waitedMs;
            }
        }
    }

    ::setsockopt(sock, IPPROTO_IP, IP_DROP_MEMBERSHIP, &mreq, sizeof(mreq));
    ::close(sock);

    std::sort(services.begin(), services.end(), [](const DiscoveredService& a, const DiscoveredService& b) {
        return a.name < b.name;
    });

    return services;
}

// ---------------------------------------------------------------------------
// Public helpers for persistent SAP listener
// ---------------------------------------------------------------------------

int ServiceDiscovery::open_sap_socket(const std::string& interfaceName) {
    const int sock = ::socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        return -1;
    }

    int reuse = 1;
    (void)::setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));
#ifdef SO_REUSEPORT
    (void)::setsockopt(sock, SOL_SOCKET, SO_REUSEPORT, &reuse, sizeof(reuse));
#endif

    sockaddr_in bindAddr{};
    bindAddr.sin_family = AF_INET;
    bindAddr.sin_port = htons(kSapPort);

#ifdef __APPLE__
    if (::inet_pton(AF_INET, kSapAddress, &bindAddr.sin_addr) != 1) {
        ::close(sock);
        return -1;
    }
    if (::bind(sock, reinterpret_cast<sockaddr*>(&bindAddr), sizeof(bindAddr)) != 0) {
        bindAddr.sin_addr.s_addr = htonl(INADDR_ANY);
        if (::bind(sock, reinterpret_cast<sockaddr*>(&bindAddr), sizeof(bindAddr)) != 0) {
            ::close(sock);
            return -1;
        }
    }
#else
    bindAddr.sin_addr.s_addr = htonl(INADDR_ANY);
    if (::bind(sock, reinterpret_cast<sockaddr*>(&bindAddr), sizeof(bindAddr)) != 0) {
        ::close(sock);
        return -1;
    }
#endif

    in_addr ifaceAddr{};
    get_interface_ipv4(interfaceName, ifaceAddr);

    ip_mreq mreq{};
    if (::inet_pton(AF_INET, kSapAddress, &mreq.imr_multiaddr) != 1) {
        ::close(sock);
        return -1;
    }
    mreq.imr_interface = ifaceAddr;
    if (::setsockopt(sock, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) != 0) {
        mreq.imr_interface.s_addr = htonl(INADDR_ANY);
        (void)::setsockopt(sock, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq));
    }

    return sock;
}

bool ServiceDiscovery::parse_sap_packet(const std::vector<std::uint8_t>& data,
                                        DiscoveredService& out,
                                        const std::string& sourceIp,
                                        int sourcePort) {
    std::string sdpText;
    if (!parse_sap_payload(data, sdpText)) {
        return false;
    }
    out = parse_sdp(sdpText);

    if (out.address.empty() && !sourceIp.empty()) {
        out.address = sourceIp;
    }
    if (out.port <= 0 && sourcePort > 0) {
        out.port = sourcePort;
    }
    if (out.name.empty()) {
        out.name = !sourceIp.empty() ? ("SAP@" + sourceIp) : "SAP";
    }

    if (out.address.empty() || out.port <= 0 || out.codec.empty()) {
        return false;
    }
    return is_supported_for_metadata(out);
}


