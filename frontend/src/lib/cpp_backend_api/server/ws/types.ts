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

// Wire types for messages broadcast on the C++ backend websocket (`/ws`).
// Keep this file in sync with `src/web/dto.h` (namespace `amviewer::dto::ws`).
//
// Each message is a typed envelope; `type` is the discriminator.

import type {
    AudioBed,
    AudioObject,
    AudioPresentation,
    CaptureStatus,
    DeframerStats,
    DiscoveredService,
    DolbyEMetadataField,
    ServiceSelection,
} from "../../common/cpp_backend_types";

// ---------------------------------------------------------------------------
// Polymorphic stream info (discriminated on `protocol`)
// Mirrors StreamInfoBaseDto + ST2110_31InfoDto + ST2110_41InfoDto
// ---------------------------------------------------------------------------

export interface StreamInfoBase {
    protocol: string;
}

export interface ST2110_31Info extends StreamInfoBase {
    protocol: "st2110-31";
    mode: "frame" | "subframe" | "";
    depth: number; // 20 or 24
    deframer_stats: DeframerStats | null;
}

export interface ST2110_41Info extends StreamInfoBase {
    protocol: "st2110-41";
    ditValue: string;
}

export type StreamInfo = ST2110_31Info | ST2110_41Info;

// ---------------------------------------------------------------------------
// Polymorphic metadata (discriminated on `type`)
// Mirrors MetadataBaseDto + SADMMetadataDto
// ---------------------------------------------------------------------------

export interface MetadataBase {
    type: string;
    timestampMs: number;
    frameCounter: number;
}

export interface SADMMetadata extends MetadataBase {
    type: "sadm";
    beds: AudioBed[];
    objects: AudioObject[];
    presentations: AudioPresentation[];
    sadmVersion: string;
    admVersion: string;
    admProfile: string;
    admProfiles: string[];
    isDolbyEProfile: boolean;
    dolbyEFields: DolbyEMetadataField[];
}

export type Metadata = SADMMetadata; // extend the union as new metadata kinds are added

// ---------------------------------------------------------------------------
// Capture status that ships through the websocket includes the polymorphic
// stream-info field; the REST `CaptureStatus` doesn't, hence this local widening.
// ---------------------------------------------------------------------------

export interface CaptureStatusWithStream extends CaptureStatus {
    streamInfo: StreamInfo | null;
}

// ---------------------------------------------------------------------------
// Envelope types — one per `WsXxxDto` in dto.h
// ---------------------------------------------------------------------------

interface WebsocketMessageBase {
    type: string;
}

export interface CaptureMessage extends WebsocketMessageBase {
    type: "capture";
    captureStatus: CaptureStatusWithStream | null;
}

export interface ServicesMessage extends WebsocketMessageBase {
    type: "services";
    services: DiscoveredService[];
    selectedService: ServiceSelection | null;
}

export interface StreamInfoMessage extends WebsocketMessageBase {
    type: "streamInfo";
    streamInfo: StreamInfo | null;
}

export interface InterfaceMessage extends WebsocketMessageBase {
    type: "interface";
    interfaces: string[];
    selectedInterface: string | null;
}

// Mirrors RTPInfoDto. `timestampSeconds` is the RTP timestamp converted to
// seconds using the source clock rate from the SDP (0 when the rate is unknown).
export interface RTPInfo {
    version: number;
    seq: number;
    timestamp: number;
    ssrc: number;
    timestampSeconds: number;
    packetsInBurst: number;
}

export interface MetadataMessage extends WebsocketMessageBase {
    type: "metadata";
    metadata: Metadata | null;
    rtpInfo: RTPInfo | null;
}

export type WebsocketMessage =
    | CaptureMessage
    | ServicesMessage
    | StreamInfoMessage
    | InterfaceMessage
    | MetadataMessage;

// ---------------------------------------------------------------------------
// Narrowing helpers
// ---------------------------------------------------------------------------

export type WebsocketMessageType = WebsocketMessage["type"];

const KNOWN_TYPES: ReadonlySet<WebsocketMessageType> = new Set([
    "capture",
    "services",
    "streamInfo",
    "interface",
    "metadata",
]);

export function isWebsocketMessage(obj: unknown): obj is WebsocketMessage {
    return (
        typeof obj === "object" &&
        obj !== null &&
        typeof (obj as { type?: unknown }).type === "string" &&
        KNOWN_TYPES.has((obj as { type: WebsocketMessageType }).type)
    );
}

export function isCaptureMessage(m: WebsocketMessage): m is CaptureMessage {
    return m.type === "capture";
}

export function isServicesMessage(m: WebsocketMessage): m is ServicesMessage {
    return m.type === "services";
}

export function isStreamInfoMessage(m: WebsocketMessage): m is StreamInfoMessage {
    return m.type === "streamInfo";
}

export function isInterfaceMessage(m: WebsocketMessage): m is InterfaceMessage {
    return m.type === "interface";
}

export function isMetadataMessage(m: WebsocketMessage): m is MetadataMessage {
    return m.type === "metadata";
}

export function isSADMMetadata(m: Metadata): m is SADMMetadata {
    return m.type === "sadm";
}

export function isST2110_31(s: StreamInfo): s is ST2110_31Info {
    return s.protocol === "st2110-31";
}

export function isST2110_41(s: StreamInfo): s is ST2110_41Info {
    return s.protocol === "st2110-41";
}
