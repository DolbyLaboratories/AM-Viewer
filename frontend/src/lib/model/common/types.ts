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

export type CPPBackendConnectionStatus = "connected" | "disconnected";



//////////////// STREAM INFO ////////////////


type DeframerStats = {
    paAcquisitions: number;
    paAcceptedRightBlanking: number;
    paAcceptedLeftBlanking: number;
    paAcceptedWithoutBlanking: number;
    pbDetections: number;
    pbAtPos6WrongChannel: number;
    nonPbAtPos6: number;
    nonPbAtPos9: number;
    headerDecodesAttempted: number;
    headerDecodesSucceeded: number;
    framesEmitted: number;
    framesRejectedWrongDataType: number;
    abortsDuringGotPa: number;
    abortsDuringGotSync: number;
    idleNonZeroRightResets: number;
    idleNonZeroLeftResets: number;
    gotSyncStateEntries: number;
    gotHeaderStateEntries: number;
};

type StreamInfoBase = {
    protocol: string;
};

type ST2110_31Info = StreamInfoBase & {
    protocol: "st2110-31";
    mode: 'frame' | 'subframe';
    depth: number;
    deframerStats: DeframerStats;
};

type ST2110_41Info = StreamInfoBase & {
    protocol: "st2110-41";
    ditValue: string;
};


export type StreamInfo = ST2110_31Info | ST2110_41Info; // | OtherStreamInfoTypes...













//////////////// METADATA ////////////////


type MetadataBase = {
    type: string;
};

export type SADMAudioBed = {
    source: string;
    config: string;
    name: string;
    gainDb: number;
    start: number;
    end: number;
};

export type SADMAudioObject = {
    id: number;
    type: string;
    name: string;
    diverge: boolean;
    channel: number;
    gainDb: number;
    x: number;
    y: number;
    z: number;
};

export type SADMPresentation = {
    index: number;
    name: string;
    nameLang: string;
    bedElement: string;
    targetCfg: string;
    objectElements: string;
    presLang: string;
};

export type SADMDolbyEMetadataField = {
    group: string;
    label: string;
    value: string;
};

export type SADMMetadata = MetadataBase & {
    type: "sadm";
    beds: SADMAudioBed[];
    objects: SADMAudioObject[];
    presentations: SADMPresentation[];
    dolbyEFields: SADMDolbyEMetadataField[];
    sadmVersion: string;
    admVersion: string;
    admProfile: string;
    admProfiles: string[];
    isDolbyEProfile: boolean;
};


export type Metadata = SADMMetadata; // | OtherMetadataTypes...




export type Interface = string;

export type CaptureStatus = {
    type: "capture";
    active: boolean;
    interfaceName: string;
    address: string;
    port: number;
    packetCount: number;
    lastError: string;
    streamInfo: StreamInfo|null;
};

export type ServiceSelection = {
    type: "service";
    name: string;
    system: string;
    interfaceName: string;
    address: string;
    port: number;
    codec: string;
    audio: string;
    sampleRate: number;
};











//////////////// STATUS ////////////////

export type Status = {
    status: string;
    message: string;
};

export type ModelSummary = {
    loadedFile: string;
    lastError: string;
    lastUpdated: string;
    metadata: Metadata;
};
