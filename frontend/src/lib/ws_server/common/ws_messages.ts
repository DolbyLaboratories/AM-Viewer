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

// Wire types for the SSE channel between the SvelteKit server and the browser.
//
// The server acts as a WS↔SSE bridge: messages from the C++ backend (typed
// envelopes defined in `lib/cpp_backend_api/server/ws/types.ts`) pass through
// unmodified, plus the server injects a small number of meta messages
// (connection status, app version) that have no C++ counterpart.

import {
    isWebsocketMessage,
    type WebsocketMessage,
    type WebsocketMessageType,
} from "$lib/cpp_backend_api/server/ws/types";
import type { CPPBackendConnectionStatus } from "$lib/model/common/types";

export interface ConnectionStatusMessage {
    type: "connection-status";
    status: CPPBackendConnectionStatus;
}

export interface AppVersionMessage {
    type: "app-version";
    version: string;
}

// Server → browser liveness beat, emitted at a fixed cadence on the SSE stream.
// The client marks the SSE connection dead if it stops arriving.
export interface HeartbeatMessage {
    type: "heartbeat";
    timestamp: number;
}

export interface MetadataFpsMessage {
    type: "metadata-fps";
    fps: number; // average over the last sampling window (~1 s)
    realFps?: number; // average over the last sampling window (~1 s) - real time between messages received, for debugging/monitoring only
    realFpsHistory?: number[]; // rolling history of real-fps samples, oldest → newest (for graphing)
    sampleIntervalMs?: number; // spacing in ms between consecutive history samples
}

export interface IssueMessage {
    type: "issue";
    tag: string;
    error: {
        message: string;
        timestamp: number;
    } | null;
}

export interface LogMessage {
    type: "log";
    level: 0 | 1 | 2 | 3; // debug=0, info=1, warn=2, error=3
    tag: string;
    message: string;
    timestamp: number;
}

export type ServerInjectedMessage =
    | ConnectionStatusMessage
    | AppVersionMessage
    | HeartbeatMessage
    | MetadataFpsMessage
    | IssueMessage
    | LogMessage;
export type ServerInjectedMessageType = ServerInjectedMessage["type"];

export type SSEMessage = WebsocketMessage | ServerInjectedMessage;
export type SSEMessageType = WebsocketMessageType | ServerInjectedMessageType;

const SERVER_INJECTED_TYPES: ReadonlySet<ServerInjectedMessageType> = new Set([
    "connection-status",
    "app-version",
    "heartbeat",
    "metadata-fps",
    "log",
    "issue",
]);

function isServerInjectedMessage(obj: unknown): obj is ServerInjectedMessage {
    if (typeof obj !== "object" || obj === null) return false;
    const t = (obj as { type?: unknown }).type;
    return typeof t === "string" && SERVER_INJECTED_TYPES.has(t as ServerInjectedMessageType);
}

export function isSSEMessage(obj: unknown): obj is SSEMessage {
    return isWebsocketMessage(obj) || isServerInjectedMessage(obj);
}
