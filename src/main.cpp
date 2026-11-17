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

#include "web/app_component.h"
#include "web/adm_xml_parser.h"
#include "web/am824_deframer.h"
#include "web/app_state.h"
#include "web/capture_service.h"
#include "web/controller.h"
#include "web/logging.h"

#include "websocket/websocket_connection_listener.hpp"

#include "oatpp/network/Server.hpp"
#include "oatpp/core/base/Environment.hpp"

#include <pcap.h>

#include <iostream>
#include <thread>
#include <atomic>
#include <memory>
#include <chrono>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <cstdint>
#include <cstring>

static std::atomic<oatpp::network::Server*> g_server = nullptr;

namespace {

struct CliOptions {
    bool help = false;
    bool helpAll = false;
    bool version = false;
    std::string xmlFile;
    std::string sdpFile;
    bool debug = false;
    bool libpcap = false;
    bool text = false;
    std::string interfaceName;
    std::string pcapFile;
    std::string address;
    int port = 0;
    bool portSet = false;
    std::string codec;
    int timeoutMs = 10000;
    int xmlFrames = 1;
    std::string saveXml;
    std::string logLevel = "info";
};

void printUsage() {
    std::cout
        << "Usage: ./am_viewer [options]\n"
        << "Audio Metadata (AM) realtime viewer application\n\n"
        << "Options:\n"
        << "  -h, --help            Displays help on commandline options.\n"
        << "  --help-all            Displays help, including generic Qt options.\n"
        << "  -v, --version         Displays version information.\n"
        << "  --xml <file>          XML filename for offline display of XML\n"
        << "  --sdp <file>          SDP filename to avoid requiring stream discovery\n"
        << "  --debug               Enables debug mode\n"
        << "  --libpcap             Uses libpcap\n"
        << "  --text                Run in text mode (no GUI) for non-interactive testing\n"
        << "  --interface <name>    Network interface name for text mode\n"
        << "  --pcap <file>         Read packets from a pcap file in text mode (alternative\n"
        << "                        to --interface)\n"
        << "  --address <ip>        Multicast/unicast destination address for text mode\n"
        << "  --port <port>         UDP destination port for text mode\n"
        << "  --codec <codec>       Codec/container for text mode: AM824 or ST2110-41\n"
        << "  --timeout-ms <ms>     Text mode timeout in milliseconds\n"
        << "  --xml-frames <count>  Number of S-ADM XML frames to capture before exiting\n"
        << "                        text mode\n"
        << "  --save-xml <file>     Write captured XML payload to file in text mode\n"
        << "  --log-level <level>   Logger verbosity: trace|debug|info|warn|error|critical|off\n"
        << "                        (default: info)\n";
}

void printVersion() {
    std::cout << "am_viewer 4.2.0\n";
}

bool parseInt(const std::string& text, int& out) {
    try {
        std::size_t consumed = 0;
        const int value = std::stoi(text, &consumed, 10);
        if (consumed != text.size()) {
            return false;
        }
        out = value;
        return true;
    } catch (...) {
        return false;
    }
}

bool parseArgs(int argc, char* argv[], CliOptions& options, std::string& error) {
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        auto requireValue = [&](const char* optName, std::string& out) -> bool {
            if (i + 1 >= argc) {
                error = std::string("Missing value for option: ") + optName;
                return false;
            }
            out = argv[++i];
            return true;
        };

        if (arg == "-h" || arg == "--help") {
            options.help = true;
        } else if (arg == "--help-all") {
            options.helpAll = true;
        } else if (arg == "-v" || arg == "--version") {
            options.version = true;
        } else if (arg == "--xml") {
            if (!requireValue("--xml", options.xmlFile)) {
                return false;
            }
        } else if (arg == "--sdp") {
            if (!requireValue("--sdp", options.sdpFile)) {
                return false;
            }
        } else if (arg == "--debug") {
            options.debug = true;
        } else if (arg == "--libpcap") {
            options.libpcap = true;
        } else if (arg == "--text") {
            options.text = true;
        } else if (arg == "--interface") {
            if (!requireValue("--interface", options.interfaceName)) {
                return false;
            }
        } else if (arg == "--pcap") {
            if (!requireValue("--pcap", options.pcapFile)) {
                return false;
            }
        } else if (arg == "--address") {
            if (!requireValue("--address", options.address)) {
                return false;
            }
        } else if (arg == "--port") {
            std::string portText;
            if (!requireValue("--port", portText)) {
                return false;
            }
            if (!parseInt(portText, options.port)) {
                error = "Invalid value for --port";
                return false;
            }
            options.portSet = true;
        } else if (arg == "--codec") {
            if (!requireValue("--codec", options.codec)) {
                return false;
            }
        } else if (arg == "--timeout-ms") {
            std::string timeoutText;
            if (!requireValue("--timeout-ms", timeoutText)) {
                return false;
            }
            if (!parseInt(timeoutText, options.timeoutMs)) {
                error = "Invalid value for --timeout-ms";
                return false;
            }
        } else if (arg == "--xml-frames") {
            std::string xmlFramesText;
            if (!requireValue("--xml-frames", xmlFramesText)) {
                return false;
            }
            if (!parseInt(xmlFramesText, options.xmlFrames)) {
                error = "Invalid value for --xml-frames";
                return false;
            }
        } else if (arg == "--save-xml") {
            if (!requireValue("--save-xml", options.saveXml)) {
                return false;
            }
        } else if (arg == "--log-level") {
            if (!requireValue("--log-level", options.logLevel)) {
                return false;
            }
        } else {
            error = "Unknown option: " + arg;
            return false;
        }
    }

    return true;
}

std::string trim(const std::string& value) {
    const auto begin = value.find_first_not_of(" \t\r\n");
    if (begin == std::string::npos) {
        return "";
    }
    const auto end = value.find_last_not_of(" \t\r\n");
    return value.substr(begin, end - begin + 1);
}

std::string toUpper(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char c) {
        return static_cast<char>(std::toupper(c));
    });
    return value;
}

bool saveXmlToFile(const std::string& xml, const std::string& filePath) {
    std::ofstream out(filePath, std::ios::binary);
    if (!out) {
        return false;
    }
    out.write(xml.data(), static_cast<std::streamsize>(xml.size()));
    return static_cast<bool>(out);
}

bool parseSdpFile(const std::string& path, AppState& state, std::string& error) {
    std::ifstream in(path);
    if (!in) {
        error = "Failed to open SDP file: " + path;
        return false;
    }

    std::string line;
    std::string address;
    int port = 0;
    std::string codec = "";

    while (std::getline(in, line)) {
        line = trim(line);
        if (line.rfind("c=IN IP4 ", 0) == 0) {
            std::string addr = trim(line.substr(9));
            const auto slash = addr.find('/');
            if (slash != std::string::npos) {
                addr = addr.substr(0, slash);
            }
            address = addr;
        } else if (line.rfind("m=audio ", 0) == 0) {
            std::istringstream ss(line.substr(8));
            std::string portText;
            ss >> portText;
            int parsedPort = 0;
            if (parseInt(portText, parsedPort)) {
                port = parsedPort;
            }
        } else if (line.rfind("a=rtpmap:", 0) == 0) {
            const std::string upper = toUpper(line);
            if (upper.find("ST2110") != std::string::npos || upper.find("SMPTE2110") != std::string::npos) {
                codec = "ST2110-41";
            }
        }
    }

    if(!state.selectedService) {
        state.selectedService = std::make_unique<ServiceSelection>();
    }
    if (!address.empty()) {
        state.selectedService->address = address;
    }
    if (port > 0) {
        state.selectedService->port = port;
    }
    if (!codec.empty()) {
        state.selectedService->codec = codec;
    }
    state.selectedService->name = path;
    state.selectedService->system = "SDP";
    return true;
}

struct TextRunState {
    std::string codec;
    int targetFrames = 1;
    int capturedFrames = 0;
    std::string lastXml;
    bool lastParsed = false;
    int lastBeds = 0;
    int lastObjects = 0;
    int lastPresentations = 0;
    Am824Deframer deframer;
    std::vector<std::uint8_t> st2110_41Payload;
};

bool processSt211041Payload(const std::uint8_t* payloadData,
                           std::size_t payloadSize,
                           TextRunState& state) {
    if (!payloadData || payloadSize < 8) {
        return false;
    }

    const std::uint32_t dataItemType =
        ((static_cast<std::uint32_t>(payloadData[0]) << 24) |
         (static_cast<std::uint32_t>(payloadData[1]) << 16) |
         (static_cast<std::uint32_t>(payloadData[2]) << 8) |
         static_cast<std::uint32_t>(payloadData[3])) >> 10;

    std::size_t dataItemLengthWords =
        ((static_cast<std::uint32_t>(payloadData[2]) << 8) | static_cast<std::uint32_t>(payloadData[3])) & 0x1ff;
    if (dataItemLengthWords == 0) {
        return false;
    }
    dataItemLengthWords -= 1;

    std::size_t dataItemLengthBytes = dataItemLengthWords * 4;
    dataItemLengthBytes = std::min(dataItemLengthBytes, payloadSize - 8);

    const bool lastPacket = ((payloadData[2] & 0x2U) >> 1U) == 1U;
    const std::uint32_t segmentDataOffset =
        (static_cast<std::uint32_t>(payloadData[4]) << 24) |
        (static_cast<std::uint32_t>(payloadData[5]) << 16) |
        (static_cast<std::uint32_t>(payloadData[6]) << 8) |
        static_cast<std::uint32_t>(payloadData[7]);
    const bool firstPacket = segmentDataOffset == 0;
    const std::size_t offsetBytes = static_cast<std::size_t>(segmentDataOffset) * 4;

    if (firstPacket) {
        state.st2110_41Payload.clear();
    }
    if (state.st2110_41Payload.size() < offsetBytes + dataItemLengthBytes) {
        state.st2110_41Payload.resize(offsetBytes + dataItemLengthBytes);
    }
    std::memcpy(state.st2110_41Payload.data() + offsetBytes, payloadData + 8, dataItemLengthBytes);

    if (!lastPacket) {
        return false;
    }

    const bool isSadm = dataItemType == 0x3ff000 || dataItemType == 0x100;
    if (!isSadm) {
        state.st2110_41Payload.clear();
        return false;
    }

    std::string xml;
    std::string extractError;
    if (!adm_xml::extract_st2127_xml(state.st2110_41Payload, xml, extractError)) {
        state.st2110_41Payload.clear();
        return false;
    }

    amviewer::types::metadata::sadm::SADMMetadata parsedModel;
    std::string parseError;
    adm_xml::ParseInfo parseInfo;
    if (!adm_xml::parse_content(xml, parsedModel, parseError, &parseInfo)) {
        state.st2110_41Payload.clear();
        return false;
    }

    state.lastXml = std::move(xml);
    state.lastParsed = true;
    state.lastBeds = static_cast<int>(parsedModel.beds.size());
    state.lastObjects = static_cast<int>(parsedModel.objects.size());
    state.lastPresentations = static_cast<int>(parsedModel.programmes.size());
    state.capturedFrames += 1;
    state.st2110_41Payload.clear();
    return state.capturedFrames >= state.targetFrames;
}

bool processAm824Payload(const std::uint8_t* payloadData,
                         std::size_t payloadSize,
                         TextRunState& state) {
    if (!payloadData || payloadSize < 8) {
        return false;
    }

    state.deframer.receivePayload(payloadData, payloadSize);
    while (state.deframer.haveFrame()) {
        Am824Frame frame = state.deframer.popFrame();
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
            continue;
        }

        amviewer::types::metadata::sadm::SADMMetadata parsedModel;
        std::string parseError;
        adm_xml::ParseInfo parseInfo;
        if (!adm_xml::parse_content(xml, parsedModel, parseError, &parseInfo)) {
            continue;
        }

        state.lastXml = std::move(xml);
        state.lastParsed = true;
        state.lastBeds = static_cast<int>(parsedModel.beds.size());
        state.lastObjects = static_cast<int>(parsedModel.objects.size());
        state.lastPresentations = static_cast<int>(parsedModel.programmes.size());
        state.capturedFrames += 1;

        if (state.capturedFrames >= state.targetFrames) {
            return true;
        }
    }

    return false;
}

bool processPacket(const std::uint8_t* packetData,
                  std::size_t caplen,
                  int datalinkType,
                  TextRunState& state) {
    if (!packetData || caplen < 28) {
        return false;
    }

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

    if (datalinkType == DLT_EN10MB && caplen >= 14) {
        std::size_t l2Offset = 14;
        std::uint16_t etherType = static_cast<std::uint16_t>((packetData[12] << 8) | packetData[13]);
        while ((etherType == 0x8100 || etherType == 0x88A8 || etherType == 0x9100) &&
               caplen >= l2Offset + 4) {
            etherType = static_cast<std::uint16_t>((packetData[l2Offset + 2] << 8) | packetData[l2Offset + 3]);
            l2Offset += 4;
        }

        if (etherType == 0x0800 && caplen >= l2Offset + 20) {
            const std::size_t ihlBytes = (static_cast<std::size_t>(packetData[l2Offset] & 0x0F)) * 4;
            if ((packetData[l2Offset] >> 4) == 4 && ihlBytes >= 20 &&
                caplen >= l2Offset + ihlBytes + 8 && packetData[l2Offset + 9] == 17) {
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
        if (caplen < candidate + 20) {
            return;
        }
        const std::uint8_t version = packetData[candidate] >> 4;
        if (version != 4) {
            return;
        }
        const std::size_t ihlBytes = (static_cast<std::size_t>(packetData[candidate] & 0x0F)) * 4;
        if (ihlBytes < 20 || caplen < candidate + ihlBytes + 8) {
            return;
        }
        if (packetData[candidate + 9] != 17) {
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
        const std::size_t maxScanOffset = (caplen > 28) ? std::min<std::size_t>(caplen - 28, 128) : 0;
        for (std::size_t candidate = 0; candidate <= maxScanOffset && !foundIpv4Udp; ++candidate) {
            tryOffset(candidate);
        }
    }
    if (!foundIpv4Udp) {
        return false;
    }

    const std::size_t udpOffset = ipOffset + ipHeaderLen;
    if (caplen < udpOffset + 8) {
        return false;
    }
    const std::size_t udpPayloadOffset = udpOffset + 8;
    if (caplen <= udpPayloadOffset) {
        return false;
    }

    const auto* udpPayloadData = packetData + udpPayloadOffset;
    const std::size_t udpPayloadSize = caplen - udpPayloadOffset;
    if (udpPayloadSize < 12) {
        return false;
    }

    std::size_t rtpHeaderBytes = 12;
    const std::uint8_t rtpFirst = udpPayloadData[0];
    const std::uint8_t rtpVersion = static_cast<std::uint8_t>((rtpFirst >> 6U) & 0x03U);
    if (rtpVersion == 2) {
        const std::size_t csrcCount = static_cast<std::size_t>(rtpFirst & 0x0FU);
        const bool hasExtension = (rtpFirst & 0x10U) != 0;
        rtpHeaderBytes = 12 + (csrcCount * 4);
        if (udpPayloadSize < rtpHeaderBytes) {
            return false;
        }
        if (hasExtension) {
            if (udpPayloadSize < rtpHeaderBytes + 4) {
                return false;
            }
            const std::size_t extLenIndex = rtpHeaderBytes + 2;
            const std::uint16_t extWords =
                static_cast<std::uint16_t>((static_cast<std::uint16_t>(udpPayloadData[extLenIndex]) << 8) |
                                           static_cast<std::uint16_t>(udpPayloadData[extLenIndex + 1]));
            rtpHeaderBytes += 4 + (static_cast<std::size_t>(extWords) * 4);
            if (udpPayloadSize < rtpHeaderBytes) {
                return false;
            }
        }
    }

    if (udpPayloadSize <= rtpHeaderBytes) {
        return false;
    }

    const auto* payloadData = udpPayloadData + rtpHeaderBytes;
    const std::size_t payloadSize = udpPayloadSize - rtpHeaderBytes;
    if (payloadSize == 0) {
        return false;
    }

    if (state.codec == "ST2110-41") {
        return processSt211041Payload(payloadData, payloadSize, state);
    }

    auto countPreambles = [](const std::uint8_t* data, std::size_t size) {
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
        return processAm824Payload(payloadData, payloadSize, state);
    }
    return processAm824Payload(udpPayloadData, udpPayloadSize, state);
}

int runTextMode(const CliOptions& options) {
    const bool usePcapInput = !options.pcapFile.empty();
    const bool hasAddress = !options.address.empty();
    const bool hasPort = options.portSet;
    const bool shouldApplyFilter = hasAddress && hasPort;
    const bool hasValidCodec = (options.codec == "AM824" || options.codec == "ST2110-41");

    if ((!usePcapInput && options.interfaceName.empty()) ||
        (!usePcapInput && !shouldApplyFilter) ||
        (hasAddress != hasPort) ||
        (hasPort && options.port <= 0) ||
        !hasValidCodec ||
        options.xmlFrames <= 0 ||
        options.timeoutMs <= 0) {
        AMV_LOG_ERROR(
            "Text mode requires: (--interface <name> | --pcap <file>) --codec <AM824|ST2110-41>. "
            "For interface input, --address and --port are required. "
            "For pcap input, --address and --port are optional but must be provided together if used.");
        printUsage();
        return 1;
    }

    TextRunState state;
    state.codec = options.codec;
    state.targetFrames = options.xmlFrames;

    const auto start = std::chrono::steady_clock::now();

    char errbuf[PCAP_ERRBUF_SIZE] = {0};
    pcap_t* handle = nullptr;
    if (usePcapInput) {
        handle = pcap_open_offline(options.pcapFile.c_str(), errbuf);
        if (!handle) {
            AMV_LOG_ERROR("Failed to open pcap file for capture: {}", errbuf);
            return 2;
        }
    } else {
        handle = pcap_open_live(options.interfaceName.c_str(), 65535, 1, 200, errbuf);
        if (!handle) {
            AMV_LOG_ERROR("Failed to configure packet capture interface: {}", errbuf);
            return 2;
        }

        if (shouldApplyFilter) {
            bpf_program filter{};
            const std::string filterExpr = "ip dst " + options.address + " and udp dst port " + std::to_string(options.port);
            if (pcap_compile(handle, &filter, filterExpr.c_str(), 0, PCAP_NETMASK_UNKNOWN) == -1) {
                AMV_LOG_ERROR("Failed to compile capture filter: {}", pcap_geterr(handle));
                pcap_close(handle);
                return 2;
            }
            if (pcap_setfilter(handle, &filter) == -1) {
                AMV_LOG_ERROR("Failed to set capture filter: {}", pcap_geterr(handle));
                pcap_freecode(&filter);
                pcap_close(handle);
                return 2;
            }
            pcap_freecode(&filter);
        }
    }

    const int datalinkType = pcap_datalink(handle);
    int packetCount = 0;

    while (true) {
        const auto now = std::chrono::steady_clock::now();
        const auto elapsedMs = std::chrono::duration_cast<std::chrono::milliseconds>(now - start).count();
        if (elapsedMs >= options.timeoutMs) {
            pcap_close(handle);
            AMV_LOG_ERROR("Timeout waiting for S-ADM payload.");
            return 4;
        }

        pcap_pkthdr* header = nullptr;
        const u_char* packet = nullptr;
        const int rc = pcap_next_ex(handle, &header, &packet);
        if (rc == 1 && header && packet) {
            ++packetCount;
            if (processPacket(reinterpret_cast<const std::uint8_t*>(packet), header->caplen, datalinkType, state)) {
                break;
            }
            continue;
        }
        if (rc == 0) {
            continue;
        }
        if (rc == -2) {
            break;
        }
        pcap_close(handle);
        AMV_LOG_ERROR("Capture error.");
        return 2;
    }

    pcap_close(handle);

    if (state.capturedFrames < state.targetFrames) {
        AMV_LOG_ERROR("Timeout waiting for S-ADM payload.");
        return 4;
    }

    if (!options.saveXml.empty() && !saveXmlToFile(state.lastXml, options.saveXml)) {
        AMV_LOG_ERROR("Failed to save XML to: {}", options.saveXml);
        return 3;
    }

    std::ostringstream summary;
    summary << "Captured " << state.capturedFrames << " S-ADM XML frame"
            << (state.capturedFrames == 1 ? "" : "s") << ".";
    if (state.lastParsed) {
        summary << " Last frame: beds=" << state.lastBeds
                << " objects=" << state.lastObjects
                << " presentations=" << state.lastPresentations << ".";
    } else {
        summary << " Last frame ADM parse failed.";
    }
    if (!options.saveXml.empty()) {
        summary << " XML saved to " << options.saveXml << ".";
    }

    if (options.debug) {
        AMV_LOG_DEBUG("Processed packets: {}", packetCount);
    }
    std::cout << summary.str() << "\n";
    return 0;
}

}

int main(int argc, char* argv[]) {
    CliOptions options;
    std::string argError;
    if (!parseArgs(argc, argv, options, argError)) {
        std::cerr << argError << "\n";
        printUsage();
        return 1;
    }

    if (options.help || options.helpAll) {
        printUsage();
        return 0;
    }
    if (options.version) {
        printVersion();
        return 0;
    }

    spdlog::level::level_enum level = spdlog::level::info;
    if (!amviewer::logging::parse_level(options.logLevel, level)) {
        std::cerr << "Invalid value for --log-level: " << options.logLevel << "\n";
        return 1;
    }
    amviewer::logging::init(level);

    AMV_LOG_DEBUG("HEY");

    if (options.text) {
        return runTextMode(options);
    }

    oatpp::base::Environment::init();
    {
        AppComponent components;
        auto state = std::make_shared<AppState>();
        state->captureService = std::make_shared<CaptureService>();

        if (!options.xmlFile.empty()) {
            auto parsed = std::make_shared<amviewer::types::metadata::sadm::SADMMetadata>();
            std::string parseError;
            adm_xml::ParseInfo parseInfo;
            const bool ok = adm_xml::parse_file(options.xmlFile, *parsed, parseError, &parseInfo);
            if (ok) {
                std::lock_guard<std::mutex> lock(state->mutex);
                state->metadata = std::move(parsed);
                state->loadedFile = options.xmlFile;
                state->lastError.clear();
            } else {
                std::lock_guard<std::mutex> lock(state->mutex);
                state->lastError = parseError;
            }
        }

        if (!options.sdpFile.empty()) {
            std::string sdpError;
            if (!parseSdpFile(options.sdpFile, *state, sdpError)) {
                std::lock_guard<std::mutex> lock(state->mutex);
                state->lastError = sdpError;
            }
        }

        if (options.debug) {
            AMV_LOG_INFO("Debug mode enabled");
        }

        OATPP_COMPONENT(std::shared_ptr<oatpp::web::server::HttpRouter>, router);
        OATPP_COMPONENT(std::shared_ptr<oatpp::network::ConnectionHandler>, connectionHandler, "http");
        OATPP_COMPONENT(std::shared_ptr<oatpp::network::ServerConnectionProvider>, connectionProvider);

        auto controller = AmViewerController::createShared(state);
        router->addController(controller);
        controller->setupCaptureCallbacks();
        controller->setupDiscoveryCallbacks();
        controller->setupWelcomeHandler();

        AMV_LOG_INFO("AM-Viewer backend listening on http://0.0.0.0:8000");
        oatpp::network::Server server(connectionProvider, connectionHandler);

        g_server.store(&server, std::memory_order_relaxed);

        std::thread shutdownMonitor([state]() {
            while (!state->shouldShutdown.load(std::memory_order_acquire)) {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
            }
            AMV_LOG_INFO("Shutdown signal received, waiting for frontend to close...");
            std::this_thread::sleep_for(std::chrono::milliseconds(1000));
            auto srv = g_server.load(std::memory_order_relaxed);
            if (srv) {
                AMV_LOG_INFO("Stopping server...");
                srv->stop();
            }
        });
        shutdownMonitor.detach();

        server.run();
        AMV_LOG_INFO("Server stopped");

        g_server.store(nullptr, std::memory_order_relaxed);
    }
    oatpp::base::Environment::destroy();
    return 0;
}
