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

import { getDefaultAPIEndpoint, selectInterface, selectService, selectServiceBySDP, startCapture, stopCapture, type APIEndpointParams } from "$lib/cpp_backend_api/server/cpp_backend_api";
import type { DiscoveredService, ServiceSelection } from "$lib/cpp_backend_api/common/cpp_backend_types";
import { building } from "$app/environment";
import type { CPPBackendConnectionStatus } from "../common/types";
import { CppBackendWSClient } from "$lib/cpp_backend_api/server/ws/cpp_backend_ws_client";

import type { MetadataFpsMessage, SSEMessage } from "$lib/ws_server/common/ws_messages";
import { isWebsocketMessage, type CaptureMessage, type InterfaceMessage, type MetadataMessage, type ServicesMessage, type StreamInfoMessage, type WebsocketMessage } from "$lib/cpp_backend_api/server/ws/types";
import { getLogger } from "$lib/logger/server/mylogger";
import { LogTag } from "$lib/logger/logTags";

interface LatestByType {
    capture?: CaptureMessage;
    services?: ServicesMessage;
    streamInfo?: StreamInfoMessage;
    interface?: InterfaceMessage;
    metadata?: MetadataMessage;
    "metadata-fps"?: MetadataFpsMessage;
}

class MetadataError extends Error {
    readonly frame: MetadataMessage | null;
    readonly timestamp: number;
    constructor(frame: MetadataMessage|null, message: string) {
        super(message);
        this.name = "MetadataError";
        this.frame = frame;
        this.timestamp = Date.now();
    }
};

interface MetadataErrorCheckerBase_ {
    readonly name: string;
    feedMetadataMessage(metadata: MetadataMessage): void;
    onError(callback: (error: MetadataError | null) => void): ()=>void;
    getError(): MetadataError | null;
    resetFlag(): void;
    onStart(): void;
    onStop(): void;
}

class MetadataContinuityChecker implements MetadataErrorCheckerBase_ {
    readonly name = "MetadataContinuityChecker";
    readonly logger = getLogger(LogTag.METADATA);
    private lastSequenceNumber: number | null = null;
    private lastError: MetadataError | null = null;
    private running: boolean = false;
    private errorCallbacks: Set<(error: MetadataError | null) => void> = new Set();

    feedMetadataMessage(metadata: MetadataMessage) {
        if(!this.running) return;
        if (!metadata.metadata) return; // can't check continuity if there's no metadata
        if(!metadata.rtpInfo)  return; // continuity can only be checked for RTP streams

        const sequenceNumber = metadata.rtpInfo.seq;
        try {
            if(this.lastSequenceNumber !== null && metadata.rtpInfo.packetsInBurst > 0){
                const expected = (this.lastSequenceNumber + metadata.rtpInfo.packetsInBurst) % 65536; // RTP sequence numbers are modulo 2^16
                if(sequenceNumber !== expected){
                    const err = new MetadataError(metadata, `RTP sequence number discontinuity: ${this.lastSequenceNumber} -> ${sequenceNumber} (expected ${expected})`);
                    this.logger.warnPublic(err.message);
                    this.errorCallbacks.forEach(callback=>callback(err));
                    this.lastError = err;
                }
            }
        }
        finally {
            this.lastSequenceNumber = sequenceNumber;
        }
    }

    getError(): MetadataError | null { return this.lastError; }
    resetFlag(): void { this.lastError = null; }
    onStop(): void { this.resetFlag(); this.lastSequenceNumber = null; this.running = false; }
    onStart(): void { this.running = true; }
    onError(callback: (error: MetadataError | null) => void): ()=>void {
        this.errorCallbacks.add(callback);
        return () => {
            this.errorCallbacks.delete(callback);
        }
    }
}

class MetadataFpsCalculator implements MetadataErrorCheckerBase_ {
    readonly name = "MetadataFpsCalculator";
    readonly logger = getLogger(LogTag.METADATA);

    // Cadence at which we roll up buffered per-frame rates into a history sample.
    static readonly SAMPLE_INTERVAL_MS = 400;
    // How many samples of real-fps history we retain for graphing.
    // SAMPLE_INTERVAL_MS * GRAPH_HISTORY_LENGTH = window shown in the graph.
    static readonly GRAPH_HISTORY_LENGTH = 300; // ~2 minutes at 400 ms

    private lastRTPTimestamp: number|undefined = 0;
    private lastRealTimestamp: number = 0;
    private unprocessedRTPFpsBuffer: number[] = [];
    private unprocessedRealFpsBuffer: number[] = [];
    private rtpFpsHistory: number[] = Array(1).fill(0);
    private realFpsHistory: number[] = Array(1).fill(0);
    private rtpFpsHistoryIndex = 0;
    private realFpsHistoryIndex = 0;
    // Rolling window of real-fps samples for graphing (oldest → newest).
    private realFpsGraphHistory: number[] = [];
    private framesSinceLastSample = 0;
    private receivingFrames: boolean | null = null;
    private running: boolean = false;
    private errorCallbacks: Set<(error: MetadataError | null) => void> = new Set();

    private sampleTimeout: ReturnType<typeof setTimeout> | null = null;

    private lastError: MetadataError | null = null;

    onUpdate: ((fps: {rtp: number, real: number}) => void) | null = null;

    feedMetadataMessage(metadata: MetadataMessage) {
        if(!this.running) return;
        this.framesSinceLastSample++;
        const timestamp = (metadata.rtpInfo ? metadata.rtpInfo.timestampSeconds * 1000 : null) ?? metadata.metadata?.timestampMs;
        const realTimestamp = metadata.metadata?.timestampMs ?? performance.now(); // Prefer timestamp written by service
        if (this.lastRTPTimestamp && this.lastRealTimestamp) {
            if(timestamp){
                const delta = timestamp - this.lastRTPTimestamp;
                const fps = delta > 0 ? 1000 / delta : 0;
                this.unprocessedRTPFpsBuffer.push(fps);
            }
            const realDelta = realTimestamp - this.lastRealTimestamp;
            const realFps = realDelta > 0 ? 1000 / realDelta : 0;
            this.unprocessedRealFpsBuffer.push(realFps);
        }
        this.lastRTPTimestamp = timestamp;
        this.lastRealTimestamp = realTimestamp;
    }

    getError(): MetadataError | null {
        return this.lastError;
    }

    resetFlag(): void {
        this.lastError = null;
    }

    onStart(){
        this.running = true;
        if(this.sampleTimeout) return; // already started
        this.sampleTimeoutHandler();
    }

    onStop(){
        this.running = false;
        if(this.sampleTimeout) {
            clearTimeout(this.sampleTimeout);
            this.sampleTimeout = null;
        }
        this.lastRTPTimestamp = 0;
        this.lastRealTimestamp = 0;
        this.unprocessedRTPFpsBuffer = [];
        this.unprocessedRealFpsBuffer = [];
        this.rtpFpsHistory.fill(0);
        this.realFpsHistory.fill(0);
        this.rtpFpsHistoryIndex = 0;
        this.realFpsHistoryIndex = 0;
        this.realFpsGraphHistory = [];
        this.framesSinceLastSample = 0;
        this.receivingFrames = null;
        this.lastError = null;
    }

    private sampleTimeoutHandler() {
        this.captureureFpsSample();
        this.sampleTimeout = setTimeout(() => this.sampleTimeoutHandler(), MetadataFpsCalculator.SAMPLE_INTERVAL_MS);
    }

    private filterOutliers(values: number[]): number[] {
        const avg = values.reduce((a, b) => a + b, 0) / values.length;
        const stdDev = Math.sqrt(values.reduce((sum, val) => sum + Math.pow(val - avg, 2), 0) / values.length);
        const threshold = stdDev * 2;
        return values.filter(val => Math.abs(val - avg) <= threshold);
    }

    private getFilteredMean(values: number[]): number {
        if(values.length === 0) return 0;
        const filtered = this.filterOutliers(values);
        if (filtered.length === 0) {
            return values.reduce((a, b) => a + b, 0) / values.length;
        }
        return filtered.reduce((a, b) => a + b, 0) / filtered.length;
    }

    private captureureFpsSample() {
        // Detect whether frames are still arriving since the last sample.
        const receivedFrames = this.framesSinceLastSample > 0;
        this.framesSinceLastSample = 0;
        if (receivedFrames) {
            if (this.receivingFrames !== null && this.receivingFrames === false) {
                this.logger.infoPublic("Started receiving metadata frames again");
            }
            this.receivingFrames = true;
        } else {
            if (this.receivingFrames === true) {
                this.logger.warnPublic("Stopped receiving metadata frames");
                this.receivingFrames = false;
            }
        }

        // RTP
        // const processedFps = this.getFilteredMean(this.unprocessedRTPFpsBuffer);
        const processedFps = this.unprocessedRTPFpsBuffer.length > 0 ? this.unprocessedRTPFpsBuffer.reduce((a, b) => a + b, 0) / this.unprocessedRTPFpsBuffer.length : 0;
        this.unprocessedRTPFpsBuffer = [];
        this.rtpFpsHistory[this.rtpFpsHistoryIndex] = processedFps;
        this.rtpFpsHistoryIndex = (this.rtpFpsHistoryIndex + 1) % this.rtpFpsHistory.length;

        // REAL
        // const processedRealFps = this.getFilteredMean(this.unprocessedRealFpsBuffer);
        const processedRealFps = this.unprocessedRealFpsBuffer.length > 0 ? this.unprocessedRealFpsBuffer.reduce((a, b) => a + b, 0) / this.unprocessedRealFpsBuffer.length : 0;
        this.unprocessedRealFpsBuffer = [];
        this.realFpsHistory[this.realFpsHistoryIndex] = processedRealFps;
        this.realFpsHistoryIndex = (this.realFpsHistoryIndex + 1) % this.realFpsHistory.length;

        // Append to the rolling graph history (rounded — display-only), evicting oldest.
        this.realFpsGraphHistory.push(Math.round(processedRealFps * 100) / 100);
        if (this.realFpsGraphHistory.length > MetadataFpsCalculator.GRAPH_HISTORY_LENGTH) {
            this.realFpsGraphHistory.shift();
        }

        if (this.onUpdate) {
            this.onUpdate(this.getFps());
        }
    }

    getFps(): {rtp: number, real: number} {
        const rtpFps = this.getFilteredMean(this.rtpFpsHistory);
        const realFps = this.getFilteredMean(this.realFpsHistory);

        const diffPerc = rtpFps > 0 ? Math.abs(rtpFps - realFps) / rtpFps : 0;
        if(diffPerc > 0.2){
            const err = new MetadataError(null, `High discrepancy between RTP FPS (${rtpFps.toFixed(2)}) and real FPS (${realFps.toFixed(2)}): ${(diffPerc*100).toFixed(1)}%`);
            if(this.lastError === null){
                this.logger.warnPublic(err.message);
                this.errorCallbacks.forEach(callback => callback(err));
            }
            this.lastError = err;
        }

        return { rtp: rtpFps, real: realFps };
    }

    getRealFpsHistory(): number[] {
        return [...this.realFpsGraphHistory];
    }

    onError(callback: (error: MetadataError | null) => void): ()=>void {
        this.errorCallbacks.add(callback);
        return () => {
            this.errorCallbacks.delete(callback);
        }
    }
};


/**
 * Acts as a WS↔SSE bridge:
 *  - Holds one long-lived websocket to the C++ backend.
 *  - Caches the latest envelope of each type so newly-connected SSE clients
 *    get an immediate snapshot.
 *  - Forwards every C++ envelope verbatim to SSE subscribers.
 *  - Injects two server-only messages: `connection-status` (when the WS to the
 *    C++ backend opens/closes) and `app-version` (sent at SSE connect).
 */
class AMViewerWebModel {
    readonly apiEndpoint: APIEndpointParams;
    private readonly logger = getLogger(LogTag.APP_SERVER);
    readonly appVersion: string = process.env.npm_package_version || "unknown";

    private readonly subscribers: Set<(message: SSEMessage) => void> = new Set();

    /**
     * Latest C++ envelope per type. Each slot is the matching variant of the
     * `WebsocketMessage` discriminated union; declared explicitly (rather than
     * via a mapped type) to keep TS narrowing predictable.
     */
    private latestByType: LatestByType = {};

    private cppBackendConnectionStatus: CPPBackendConnectionStatus = "disconnected";

    private metadataCheckers: MetadataErrorCheckerBase_[] = [];

    private readonly cppBackendWSClient: CppBackendWSClient;

    constructor() {
        this.apiEndpoint = getDefaultAPIEndpoint();
        this.cppBackendWSClient = new CppBackendWSClient(this.apiEndpoint.host, this.apiEndpoint.port);
        if (!building) {
            this.cppBackendWSClient.status.subscribe((status) => {
                const previous = this.cppBackendConnectionStatus;
                const next: CPPBackendConnectionStatus =
                    status === WebSocket.OPEN ? "connected" : "disconnected";
                if (previous === next) return;
                this.logger.info(`Backend capture service connection status: ${next}`);

                switch(next) {
                    case "disconnected":
                        this.logger.warnPublic("Lost connection to backend capture service");
                        break;
                    case "connected":
                        this.logger.infoPublic("Backend capture service connected");
                        break;
                }

                this.cppBackendConnectionStatus = next;
                if (next === "disconnected") {
                    // Anything we cached is stale once the backend capture service goes away.
                    this.latestByType = {};
                }
                this.broadcast({ type: "connection-status", status: next });
            });
        }

        this.cppBackendWSClient.onmessage = (msg) => {
            if (!isWebsocketMessage(msg)) {
                this.logger.warn("Dropping malformed message from C++ websocket", { msg });
                return;
            }
            // Discriminated-union narrowing on a dynamic key requires this cast;
            // the runtime value is correct by construction since `msg.type` is
            // the discriminator.
            switch(msg.type) {
                case "metadata":
                    for(const checker of this.metadataCheckers){
                        try {
                            checker.feedMetadataMessage(msg);
                        } catch (e) {
                            if(e instanceof MetadataError){
                                this.broadcast({ type: "issue", tag: checker.name, error: { message: e.message, timestamp: e.timestamp } });
                            } else {
                                this.logger.errorPublic(`${checker.name} threw unexpected error: ${(e as Error).message}`);
                            }
                        }
                    }
                    break;
                case "services":
                    // Log new services and any that have disappeared
                    const previousServices = this.latestByType.services?.services ?? [];
                    const newServices = msg.services;
                    const disappeared = previousServices.filter(ps => !newServices.some(ns => ns.name === ps.name && ns.codec === ps.codec));
                    const appeared = newServices.filter(ns => !previousServices.some(ps => ps.name === ns.name && ps.codec === ns.codec));
                    for(const service of appeared){
                        this.logger.infoPublic(`New service discovered: ${service.name} [${service.codec}] (${service.address}:${service.port})`);
                    }
                    for(const service of disappeared){
                        this.logger.infoPublic(`Service disappeared: ${service.name} [${service.codec}] (${service.address}:${service.port})`);
                    }
                    break;
                default:
                    break;
            }
            
            (this.latestByType as Record<string, WebsocketMessage>)[msg.type] = msg;
            this.broadcast(msg);
            
        };

        const metadataFpsCalculator = new MetadataFpsCalculator();    
        metadataFpsCalculator.onUpdate = (fps) => {
            const message: MetadataFpsMessage = {
                type: "metadata-fps",
                fps: fps.rtp,
                realFps: fps.real,
                realFpsHistory: metadataFpsCalculator.getRealFpsHistory(),
                sampleIntervalMs: MetadataFpsCalculator.SAMPLE_INTERVAL_MS,
            };
            // Cache it like the others so new subscribers get an immediate snapshot.
            this.latestByType["metadata-fps"] = message;
            this.broadcast(message);
        };
        this.metadataCheckers.push(metadataFpsCalculator);

        const continuityChecker = new MetadataContinuityChecker();
        this.metadataCheckers.push(continuityChecker);

        // Setup callbacks
        this.metadataCheckers.forEach(checker=>checker.onError(er=>this.broadcast({ type: "issue", tag: checker.name, error: er ? { message: er.message, timestamp: er.timestamp } : null })));

        this.startCheckers();

        // A single public anchor at startup makes downloaded logs easy to
        // segment across server restarts.
        this.logger.infoPublic(`AM Viewer web server started (v${this.appVersion})`);
    }

    // ---------------- Subscription / replay ---------------------------------

    /**
     * Adds a subscriber and immediately replays the current snapshot to it.
     * Returns an unsubscribe function.
     */
    onMessage(callback: (message: SSEMessage) => void): () => void {
        // Welcome bundle: meta first, then whatever C++ envelopes we have cached.
        try {
            callback({ type: "app-version", version: this.appVersion });
            callback({ type: "connection-status", status: this.cppBackendConnectionStatus });
            for (const cached of Object.values(this.latestByType)) {
                if (cached) callback(cached);
            }
            for(const checker of this.metadataCheckers){
                const error = checker.getError();
                if(error){
                    callback({ type: "issue", tag: checker.name, error: { message: error.message, timestamp: error.timestamp } });
                }
            }
        } catch (error) {
            this.logger.error(`Error replaying snapshot to new subscriber: ${(error as Error).message}`);
        }
        this.subscribers.add(callback);
        return () => this.subscribers.delete(callback);
    }

    private broadcast(message: SSEMessage) {
        for (const cb of this.subscribers) {
            try {
                cb(message);
            } catch (error) {
                this.logger.error(`Error in onMessage callback: ${(error as Error).message}`);
            }
        }
    }

    // ---------------- Public surface used by REST proxy routes --------------
    //
    // These accessors derive everything from the cached envelopes; the C++
    // backend remains the source of truth. Setters forward to the backend and
    // do not broadcast synthetic SSE events — the backend emits its own
    // envelope in response, which loops back through `onmessage` above.

    get interfaces(): string[] {
        return [...(this.latestByType.interface?.interfaces ?? [])];
    }

    get interface(): string | null {
        return this.latestByType.interface?.selectedInterface ?? null;
    }

    get services(): DiscoveredService[] {
        return [...(this.latestByType.services?.services ?? [])];
    }

    get service(): ServiceSelection | null {
        return this.latestByType.services?.selectedService ?? null;
    }

    /**
     * Selects a service: stops any running capture, then either clears
     * selection (when `service` is null) or selects + starts capture on the
     * currently-selected interface.
     */
    async setService(service: DiscoveredService | null) {
        const interfaceName = this.interface;

        if (service === null || !interfaceName) {
            // stopCapture emits its own public success/failure log.
            await stopCapture(this.apiEndpoint).catch((er) => {
                this.logger.error("Error stopping capture:", er);
                throw er;
            });
            return;
        }
        this.stopCheckers();
        await selectService(this.apiEndpoint, { ...service, interfaceName, audio: "" })
        .then(()=>{
            this.logger.infoPublic(`Service selected: ${service.name} [${service.codec}] (${service.address}:${service.port})`);
        })
        .catch((er) => {
            this.logger.errorPublic("Error selecting service:", er);
            throw er;
        })
        .finally(()=>{
            this.startCheckers();
        });
    }

    async setServiceBySDP(sdpText: string) {
        const interfaceName = this.interface;
        if(!interfaceName){
            const errorMsg = "No interface selected; cannot select service by SDP";
            this.logger.errorPublic(errorMsg);
            throw new Error(errorMsg);
        }
        this.stopCheckers();
        await selectServiceBySDP(this.apiEndpoint, sdpText)
        .then(()=>{
            this.logger.infoPublic(`Service selected by SDP:\n${sdpText}`);
        })
        .catch((er) => {
            this.logger.errorPublic("Error selecting service by SDP:", er);
            throw er;
        })
        .finally(()=>{
            this.startCheckers();
        });
    }

    async setInterface(interfaceName: string | null) {
        await selectInterface(this.apiEndpoint, interfaceName)
        .then(()=>{
            this.logger.infoPublic(`Interface selected: ${interfaceName}`);
        })
        .catch((er) => {
            this.logger.errorPublic("Error selecting interface:", er);
            throw er;
        });
    }

    resetIssueFlag(target: string){
        const checker = this.metadataCheckers.find(c => c.name === target);
        if(checker){
            checker.resetFlag();
            this.broadcast({ type: "issue", tag: checker.name, error: null });
        } else {
            this.logger.warn(`Failed to resetIssueFlag: No metadata checker found with name ${target}`);
        }
    }

    private startCheckers(){
        for(const checker of this.metadataCheckers){
            checker.onStart();
        }
    }

    private stopCheckers(){
        for(const checker of this.metadataCheckers){
            checker.onStop();
        }
    }
}


export type GlobalThisWithModel = typeof globalThis & {
    model?: AMViewerWebModel;
};

export function getGlobalServerModel() {
    if ((globalThis as GlobalThisWithModel).model) {
        return (globalThis as GlobalThisWithModel).model!;
    }
    (globalThis as GlobalThisWithModel).model = new AMViewerWebModel();
    return (globalThis as GlobalThisWithModel).model!;
}
