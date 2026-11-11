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

#include <string>
#include <vector>
#include <memory>
#include <cstdint>

namespace amviewer {

    namespace types {

        namespace metadata {


            struct MetadataBase {
                enum class Type {
                    PMD,
                    SADM,
                    ISXD
                };
                const Type type;
                MetadataBase(Type t) : type(t) {}
                virtual ~MetadataBase() = default;
            };

            namespace pmd {
                struct PMDMetadata : public MetadataBase {
                    PMDMetadata() : MetadataBase{Type::PMD} {}
                };
            }

            namespace sadm {

                struct DolbyEMetadataField {
                    std::string group;
                    std::string label;
                    std::string value;
                };

                struct SADMAudioProgramme {
                    int id;
                    std::string name;
                    std::string language;
                    std::string config;
                    std::vector<int> elementIds;
                    std::string alternativeValueSetId;
                };

                struct SADMAudioObject {
                    int id;
                    std::string name;
                    int classification;
                    bool diverge;
                    int channel;
                    float gainDb;
                    float x;
                    float y;
                    float z;
                };

                struct SADMAudioBed {
                    int id;
                    std::string name;
                    std::string source;
                    std::string config;
                    float gainDb;
                    int start;
                    int end;
                };

                struct SADMMetadata : public MetadataBase {
                    SADMMetadata() : MetadataBase{Type::SADM} {}
                    std::string version;
                    std::string sadmVersion;
                    std::string admVersion;
                    std::string admProfile;
                    std::vector<std::string> admProfiles;
                    bool isDolbyEProfile = false;
                    std::vector<DolbyEMetadataField> dolbyEFields;
                    std::vector<SADMAudioProgramme> programmes;
                    std::vector<SADMAudioObject> objects;
                    std::vector<SADMAudioBed> beds;

                    void clear(){
                        version.clear();
                        sadmVersion.clear();
                        admVersion.clear();
                        admProfile.clear();
                        admProfiles.clear();
                        isDolbyEProfile = false;
                        dolbyEFields.clear();
                        programmes.clear();
                        objects.clear();
                        beds.clear();
                    }
                };
            } // namespace sadm

        } // namespace metadata


        namespace streaminfo {
            struct RTPInfo {
                std::uint8_t version;
                std::uint16_t seq;
                std::uint32_t timestamp;
                std::uint32_t ssrc;
                // RTP timestamp converted to seconds using the source clock
                // rate from the SDP. 0.0 when the clock rate is unknown.
                double timestampSeconds;
                // Number of IP packets captured/reassembled to build the most
                // recently completed metadata frame. 0 when not yet known.
                std::uint32_t packetsInBurst;

                RTPInfo(std::uint8_t v, std::uint16_t s, std::uint32_t t, std::uint32_t ss, double tSec,
                        std::uint32_t pib = 0)
                    : version(v), seq(s), timestamp(t), ssrc(ss), timestampSeconds(tSec), packetsInBurst(pib) {}
            };

            struct StreamInfoBase {
                enum class Protocol {
                    Unknown,
                    ST2110_41,
                    ST2110_31
                };
                const Protocol protocol;
                std::shared_ptr<RTPInfo> rtpInfo;
                std::shared_ptr<metadata::MetadataBase> metadata;
                StreamInfoBase(Protocol p) : protocol(p) {}
                virtual ~StreamInfoBase() = default;
            };

            namespace st2110_41 {
                struct ST2110_41Info : public StreamInfoBase {
                    ST2110_41Info() : StreamInfoBase{Protocol::ST2110_41} {}
                    int ditValue = 0;
                };
            } // namespace st2110_41

            namespace st2110_31 {
                enum class ST2110_31Mode {
                    Frame,
                    Subframe
                };

                struct ST2110_31Info : public StreamInfoBase {
                    ST2110_31Info() : StreamInfoBase{Protocol::ST2110_31} {}
                    ST2110_31Mode mode = ST2110_31Mode::Frame;
                    int depth = 0;
                };
            } // namespace st2110_31
        } // namespace streaminfo
    } // namespace types

} // namespace amviewer
