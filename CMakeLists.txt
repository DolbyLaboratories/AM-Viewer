# Copyright (c) 2026 Dolby International AB.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED
# BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

cmake_minimum_required(VERSION 3.16)
project(AMViewer VERSION 4.2.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(oatpp REQUIRED)
find_package(oatpp-websocket REQUIRED)
find_package(tinyxml2 REQUIRED CONFIG)
find_package(libpcap REQUIRED CONFIG)
find_package(ZLIB REQUIRED)
find_package(spdlog REQUIRED CONFIG)
find_package(fmt REQUIRED CONFIG)

set(PCAP_TARGET "")
if(TARGET libpcap::libpcap)
    set(PCAP_TARGET libpcap::libpcap)
elseif(TARGET pcap::pcap)
    set(PCAP_TARGET pcap::pcap)
elseif(TARGET CONAN_PKG::libpcap)
    set(PCAP_TARGET CONAN_PKG::libpcap)
endif()

if(NOT PCAP_TARGET)
    message(FATAL_ERROR "libpcap CMake target not found. Run Conan install and configure with the generated toolchain.")
endif()

add_executable(am_viewer
    src/main.cpp
    src/model/audio_model.cpp
    src/web/adm_xml_parser.cpp
    src/web/am824_deframer.cpp
    src/web/background_service_discovery.cpp
    src/web/capture_service.cpp
    src/web/logging.cpp
    src/web/service_discovery.cpp
)

target_include_directories(am_viewer PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(am_viewer
    oatpp::oatpp
    oatpp::oatpp-websocket
    tinyxml2::tinyxml2
    ${PCAP_TARGET}
    ZLIB::ZLIB
    spdlog::spdlog
    fmt::fmt
)

if(APPLE)
    find_library(DNSSD_LIBRARY dns_sd)
    if(DNSSD_LIBRARY)
        target_link_libraries(am_viewer ${DNSSD_LIBRARY})
    endif()
endif()

if(WIN32)
    target_link_libraries(am_viewer ws2_32 iphlpapi)
endif()

install(TARGETS am_viewer DESTINATION bin)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
