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

export type Status = {
    status: string;
    message: string;
};

export type ModelSummary = {
    objects: number;
    beds: number;
    presentations: number;
    loadedFile: string;
    lastError: string;
    lastUpdated: string;
};

export type CaptureStatus = {
    active: boolean;
    interfaceName: string;
    address: string;
    port: number;
    packetCount: number;
    lastError: string;
};

export type ServiceSelection = {
    name: string;
    system: string;
    interfaceName: string;
    address: string;
    port: number;
    codec: string;
    audio: string;
    // Audio source clock rate (Hz) from the SDP rtpmap line. 0 if unknown.
    sampleRate: number;
};

export type DiscoveredService = {
    name: string;
    system: string;
    address: string;
    port: number;
    codec: string;
    channels: number;
    sampleRate: number;
    sdpText: string;
};

export type AudioBed = {
    source: string;
    config: string;
    name: string;
    gainDb: number;
    start: number;
    end: number;
};

export type AudioObject = {
    id: number;
    type: string;
    name: string;
    diverge: boolean;
    channel: number;
    gainDb: number;
    x: number;
    y: number;
    z: number;
}

export type AudioPresentation = {
    index: number;
    name: string;
    nameLang: string;
    bedElement: string;
    targetCfg: string;
    objectElements: string;
    presLang: string;
};

export type DolbyEMetadataField = {
    group: string;
    label: string;
    value: string;
}

export type UIState = {
    summary: ModelSummary;
    capture: CaptureStatus;
    service: ServiceSelection;
    interfaces: string[];
    beds: AudioBed[];
    objects: AudioObject[];
    presentations: AudioPresentation[];
    sadmVersion: string;
    admVersion: string;
    admProfile: string;
    admProfiles: string[];
    isDolbyEProfile: boolean;
    dolbyEFields: DolbyEMetadataField[];
    ditValue: string;
    pmd: string;
    sadm: string;
    smpte2110_31: string;
    smpte2110_41: string;
    frame: string;
    subframe: string;
    depth20: string;
    depth24: string;
    liveXML: string;
    shutdownPending: boolean;
};


export type DeframerStats = {
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
    headerDecodesFailed: number;
    framesEmitted: number;
    framesRejectionWrongDataType: number;
    abortsDuringGotPa: number;
    abortsDuringGotSync: number;
    idleNonZeroRightResets: number;
    idleNonZeroLeftResets: number;
    gotPaStateEntries: number;
    gotSyncStateEntries: number;
    gotHeaderStateEntries: number;
};

export function validateDiscoveredService(service: any): service is DiscoveredService {
    return typeof service === "object" &&
        typeof service.name === "string" &&
        typeof service.system === "string" &&
        typeof service.address === "string" &&
        typeof service.port === "number" &&
        typeof service.codec === "string" &&
        typeof service.channels === "number" &&
        typeof service.sampleRate === "number" &&
        typeof service.sdpText === "string";
}


export function validateServiceSelection(selection: any): selection is ServiceSelection {
    return typeof selection === "object" &&
        typeof selection.name === "string" &&
        typeof selection.system === "string" &&
        typeof selection.interfaceName === "string" &&
        typeof selection.address === "string" &&
        typeof selection.port === "number" &&
        typeof selection.codec === "string" &&
        typeof selection.audio === "string" &&
        typeof selection.sampleRate === "number";
}

export function isAudioObject(obj: any): obj is AudioObject {
    return typeof obj === "object" &&
        typeof obj.id === "number" &&
        typeof obj.type === "string" &&
        typeof obj.name === "string" &&
        typeof obj.diverge === "boolean" &&
        typeof obj.channel === "number" &&
        typeof obj.gainDb === "number" &&
        typeof obj.x === "number" &&
        typeof obj.y === "number" &&
        typeof obj.z === "number";
}

export function isAudioBed(obj: any): obj is AudioBed {
    return typeof obj === "object" &&
        typeof obj.source === "string" &&
        typeof obj.config === "string" &&
        typeof obj.name === "string" &&
        typeof obj.gainDb === "number" &&
        typeof obj.start === "number" &&
        typeof obj.end === "number";
}