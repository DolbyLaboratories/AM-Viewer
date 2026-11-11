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

#include "oatpp/core/Types.hpp"

#include OATPP_CODEGEN_BEGIN(DTO)


namespace amviewer
{
  namespace dto
  {
    class DeframerStatsDto : public oatpp::DTO {
      DTO_INIT(DeframerStatsDto, DTO)
      DTO_FIELD(UInt64, paAcquisitions);
      DTO_FIELD(UInt64, paAcceptedRightBlanking);
      DTO_FIELD(UInt64, paAcceptedLeftBlanking);
      DTO_FIELD(UInt64, paAcceptedWithoutBlanking);
      DTO_FIELD(UInt64, pbDetections);
      DTO_FIELD(UInt64, pbAtPos6WrongChannel);
      DTO_FIELD(UInt64, nonPbAtPos6);
      DTO_FIELD(UInt64, nonPbAtPos9);
      DTO_FIELD(UInt64, headerDecodesAttempted);
      DTO_FIELD(UInt64, headerDecodesSucceeded);
      DTO_FIELD(UInt64, framesEmitted);
      DTO_FIELD(UInt64, framesRejectedWrongDataType);
      DTO_FIELD(UInt64, abortsDuringGotPa);
      DTO_FIELD(UInt64, abortsDuringGotSync);
      DTO_FIELD(UInt64, idleNonZeroRightResets);
      DTO_FIELD(UInt64, idleNonZeroLeftResets);
      DTO_FIELD(UInt64, gotPaStateEntries);
      DTO_FIELD(UInt64, gotSyncStateEntries);
      DTO_FIELD(UInt64, gotHeaderStateEntries);
    };

    // Polymorphic stream info base.
    // `type` discriminates the concrete DTO shape for receivers:
    //   "st2110-31" -> ST2110_31InfoDto
    //   "st2110-41" -> ST2110_41InfoDto
    // `protocol` carries the wire-level protocol identifier (e.g. "st2110-31").
    class StreamInfoBaseDto : public oatpp::DTO {
      DTO_INIT(StreamInfoBaseDto, DTO)
      DTO_FIELD(String, protocol);
    };

    class ST2110_31InfoDto : public StreamInfoBaseDto {
      DTO_INIT(ST2110_31InfoDto, StreamInfoBaseDto)
      DTO_FIELD(String, mode); // "frame" or "subframe"
      DTO_FIELD(Int32, depth); // 20 or 24
      DTO_FIELD(Object<DeframerStatsDto>, deframer_stats);



      ST2110_31InfoDto() {
        protocol = "st2110-31";
      }
    };

    class ST2110_41InfoDto : public StreamInfoBaseDto {
      DTO_INIT(ST2110_41InfoDto, StreamInfoBaseDto)
      DTO_FIELD(String, ditValue);

      ST2110_41InfoDto() {
        protocol = "st2110-41";
      }
    };

    // Polymorphic metadata base
    class MetadataBaseDto : public oatpp::DTO {
      DTO_INIT(MetadataBaseDto, DTO)
      DTO_FIELD(String, type);
      DTO_FIELD(UInt64, timestampMs);
      DTO_FIELD(UInt64, frameCounter);
    };



    // S-ADM metadata DTO
    class SADMAudioBedDto : public oatpp::DTO {
      DTO_INIT(SADMAudioBedDto, DTO)
      DTO_FIELD(String, source);
      DTO_FIELD(String, config);
      DTO_FIELD(String, name);
      DTO_FIELD(Float64, gainDb);
      DTO_FIELD(Int32, start);
      DTO_FIELD(Int32, end);
    };


    class SADMAudioObjectDto : public oatpp::DTO {
      DTO_INIT(SADMAudioObjectDto, DTO)
      DTO_FIELD(Int32, id);
      DTO_FIELD(String, type);
      DTO_FIELD(String, name);
      DTO_FIELD(Boolean, diverge);
      DTO_FIELD(Int32, channel);
      DTO_FIELD(Float64, gainDb);
      DTO_FIELD(Float64, x);
      DTO_FIELD(Float64, y);
      DTO_FIELD(Float64, z);
    };

    class PresentationDto : public oatpp::DTO {
      DTO_INIT(PresentationDto, DTO)
      DTO_FIELD(Int32, index);
      DTO_FIELD(String, name);
      DTO_FIELD(String, nameLang);
      DTO_FIELD(String, bedElement);
      DTO_FIELD(String, targetCfg);
      DTO_FIELD(String, objectElements);
      DTO_FIELD(String, presLang);
    };

    class SADMDolbyEMetadataFieldDto : public oatpp::DTO {
      DTO_INIT(SADMDolbyEMetadataFieldDto, DTO)
      DTO_FIELD(String, group);
      DTO_FIELD(String, label);
      DTO_FIELD(String, value);
    };

    class SADMMetadataDto : public MetadataBaseDto {
      DTO_INIT(SADMMetadataDto, MetadataBaseDto)
      DTO_FIELD(List<Object<SADMAudioBedDto>>, beds);
      DTO_FIELD(List<Object<SADMAudioObjectDto>>, objects);
      DTO_FIELD(List<Object<PresentationDto>>, presentations);
      DTO_FIELD(String, sadmVersion);
      DTO_FIELD(String, admVersion);
      DTO_FIELD(String, admProfile);
      DTO_FIELD(List<String>, admProfiles);
      DTO_FIELD(Boolean, isDolbyEProfile);
      DTO_FIELD(List<Object<SADMDolbyEMetadataFieldDto>>, dolbyEFields);

      SADMMetadataDto() {
        type = "sadm";
      }
    };

    class RTPInfoDto : public oatpp::DTO {
      DTO_INIT(RTPInfoDto, DTO)
      DTO_FIELD(UInt8, version);
      DTO_FIELD(UInt16, seq);
      DTO_FIELD(UInt32, timestamp);
      DTO_FIELD(UInt32, ssrc);
      // timestamp / source clock rate, in seconds. 0 when clock rate unknown.
      DTO_FIELD(Float64, timestampSeconds);
      // Number of IP packets captured/reassembled to build the most recently
      // completed metadata frame.
      DTO_FIELD(UInt32, packetsInBurst);
    };

    class StatusDto : public oatpp::DTO {
      DTO_INIT(StatusDto, DTO);
      DTO_FIELD(String, status);
      DTO_FIELD(String, message);
    };

    class ModelSummaryDto : public oatpp::DTO {
      DTO_INIT(ModelSummaryDto, DTO)
      DTO_FIELD(String, loadedFile);
      DTO_FIELD(String, lastError);
      DTO_FIELD(String, lastUpdated);
      DTO_FIELD(Any, metadata); // Polymorphic metadata — Any preserves runtime type
    };

    class InterfacesDto : public oatpp::DTO {
      DTO_INIT(InterfacesDto, DTO)
      DTO_FIELD(List<String>, interfaces);
      DTO_FIELD(String, selectedInterface);
    };

    class CaptureStatusDto : public oatpp::DTO {
      DTO_INIT(CaptureStatusDto, DTO)
      DTO_FIELD(Boolean, active);
      DTO_FIELD(String, interfaceName);
      DTO_FIELD(String, address);
      DTO_FIELD(Int32, port);
      DTO_FIELD(UInt64, packetCount);
      DTO_FIELD(String, lastError);
      DTO_FIELD(Object<StreamInfoBaseDto>, streamInfo);
    };

    class ServiceSelectionDto : public oatpp::DTO {
      DTO_INIT(ServiceSelectionDto, DTO)
      DTO_FIELD(String, name);
      DTO_FIELD(String, system);
      DTO_FIELD(String, interfaceName);
      DTO_FIELD(String, address);
      DTO_FIELD(Int32, port);
      DTO_FIELD(String, codec);
      DTO_FIELD(String, audio);
      // Audio source clock rate (Hz) parsed from the SDP rtpmap line.
      DTO_FIELD(Int32, sampleRate);
    };

    class DiscoveredServiceDto : public oatpp::DTO {
      DTO_INIT(DiscoveredServiceDto, DTO)
      DTO_FIELD(String, name);
      DTO_FIELD(String, system);
      DTO_FIELD(String, address);
      DTO_FIELD(Int32, port);
      DTO_FIELD(String, codec);
      DTO_FIELD(Int32, channels);
      DTO_FIELD(Int32, sampleRate);
      DTO_FIELD(String, sdpText);
    };



    class UiStateDto : public oatpp::DTO {
      DTO_INIT(UiStateDto, DTO)
      DTO_FIELD(oatpp::Object<ModelSummaryDto>, summary);
      DTO_FIELD(oatpp::Object<CaptureStatusDto>, capture);
      DTO_FIELD(oatpp::Object<ServiceSelectionDto>, service);
      DTO_FIELD(oatpp::List<oatpp::String>, interfaces);
      DTO_FIELD(Object<StreamInfoBaseDto>, streamInfo); // Polymorphic stream info
      DTO_FIELD(Boolean, shutdownPending);
    };

    namespace ws {

      class WsDtoBase : public oatpp::DTO {
        DTO_INIT(WsDtoBase, DTO);
        DTO_FIELD(String, type);
      };

      class WsCaptureStatusDto : public WsDtoBase {
        DTO_INIT(WsCaptureStatusDto, WsDtoBase)
        DTO_FIELD(Object<CaptureStatusDto>, captureStatus);
        WsCaptureStatusDto() {
          type = "capture";
        }
      };

      class WsServicesDto : public WsDtoBase {
        DTO_INIT(WsServicesDto, WsDtoBase);
        DTO_FIELD(List<Object<DiscoveredServiceDto>>, services);
        DTO_FIELD(Object<ServiceSelectionDto>, selectedService);
        WsServicesDto() {
          type = "services";
        }
      };

      class WsStreamInfoDto : public WsDtoBase {
        DTO_INIT(WsStreamInfoDto, WsDtoBase);
        DTO_FIELD(Object<StreamInfoBaseDto>, streamInfo); // Polymorphic stream info
        WsStreamInfoDto() {
          type = "streamInfo";
        }
      };


      class WsInterfacesDto : public WsDtoBase {
        DTO_INIT(WsInterfacesDto, WsDtoBase);
        DTO_FIELD(List<String>, interfaces);
        DTO_FIELD(String, selectedInterface);

        WsInterfacesDto(){
          type = "interface";
        }
      };

      class WsMetadataDto : public WsDtoBase {
        DTO_INIT(WsMetadataDto, WsDtoBase);
        DTO_FIELD(Any, metadata);
        DTO_FIELD(Object<RTPInfoDto>, rtpInfo);
        WsMetadataDto() {
          type = "metadata";
        }
      };

    } // namespace ws

  }
} // namespace amviewer


#include OATPP_CODEGEN_END(DTO)
