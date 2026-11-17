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

import { getLogger } from "$lib/logger/client/mylogger";
import type { DiscoveredService, ServiceSelection } from "$lib/cpp_backend_api/common/cpp_backend_types";
import type { LogMessage, SSEMessage } from "$lib/ws_server/common/ws_messages";
import { writable, type Readable, type Writable } from "svelte/store";
import { source, type Source } from "sveltekit-sse";
import type { CaptureStatusWithStream, Metadata, StreamInfo } from "$lib/cpp_backend_api/server/ws/types";
import type { CPPBackendConnectionStatus } from "../common/types";
import type { LoggerBase } from "$lib/logger/types";
import { logLevelToString } from "$lib/logger/util";
export class ClientModel {
    private source: Source | null = null;
    private sourceEvent: Readable<SSEMessage|null> | null = null;
    private unsubscribeSourceEvent: (() => void) | null = null;

    readonly logger = getLogger('ClientModel');

    private interfaceNames_: Writable<string[]> = writable([]);
    private discoveredServices_: Writable<DiscoveredService[]> = writable([]);
    private selectedInterface_: Writable<string|null> = writable(null);
    private selectedService_: Writable<ServiceSelection|null> = writable(null);
    private metadata_: Writable<Metadata|null> = writable(null);
    private metadataFrameCounter_: Writable<number> = writable(0);
    private sseConnected_: Writable<boolean> = writable(false);
    private metadataFps_: Writable<number> = writable(0);
    private realFps_: Writable<number> = writable(0);
    private realFpsHistory_: Writable<number[]> = writable([]);
    private fpsSampleIntervalMs_: Writable<number> = writable(0);
    private captureStatus_: Writable<CaptureStatusWithStream|null> = writable(null);
    private streamInfo_: Writable<StreamInfo|null> = writable(null);
    private cppBackendConnectionStatus_: Writable<CPPBackendConnectionStatus> = writable("disconnected");
    private appVersion_: Writable<string> = writable("unknown");
    private unresolvedIssues_: Writable<Record<string, { message: string, timestamp: number }>> = writable({});

    private onNewLogCallback?: (msg: LogMessage) => void;

    // Health of the browser ↔ SvelteKit SSE stream (distinct from the
    // SvelteKit ↔ C++ backend websocket exposed via cppBackendConnectionStatus).
    //
    // sveltekit-sse's stripped-down fetch transport never invokes the `error`
    // callback and only fires `close` on a *graceful* stream end, so its
    // lifecycle hooks can't be trusted to detect the server dying. Instead the
    // server emits an application-level `heartbeat` message on the stream (see
    // sse/+server.ts); if none arrives within SSE_HEARTBEAT_TIMEOUT_MS we treat
    // the stream as dead and attempt to reconnect (the transport doesn't
    // auto-reconnect either).
    private static readonly SSE_HEARTBEAT_TIMEOUT_MS = 1000;
    private static readonly SSE_WATCHDOG_INTERVAL_MS = 250;
    private lastHeartbeatMs = 0;
    private sseWatchdog: ReturnType<typeof setInterval> | null = null;


    get interfaceNames(): Readable<string[]> { return this.interfaceNames_; }
    get sseConnected(): Readable<boolean> { return this.sseConnected_; }
    get discoveredServices(): Readable<DiscoveredService[]> { return this.discoveredServices_; }
    get selectedInterface(): Readable<string|null> { return this.selectedInterface_; }
    get selectedService(): Readable<ServiceSelection|null> { return this.selectedService_; }
    get metadata(): Readable<Metadata|null> { return this.metadata_; }
    get metadataFrameCounter(): Readable<number> { return this.metadataFrameCounter_; }
    get metadataFps(): Readable<number> { return this.metadataFps_; }
    get realFps(): Readable<number> { return this.realFps_; }
    get realFpsHistory(): Readable<number[]> { return this.realFpsHistory_; }
    get fpsSampleIntervalMs(): Readable<number> { return this.fpsSampleIntervalMs_; }
    get captureStatus(): Readable<CaptureStatusWithStream|null> { return this.captureStatus_; }
    get streamInfo(): Readable<StreamInfo|null> { return this.streamInfo_; }
    get cppBackendConnectionStatus(): Readable<CPPBackendConnectionStatus> { return this.cppBackendConnectionStatus_; }
    get appVersion(): Readable<string> { return this.appVersion_; }
    get unresolvedIssues(): Readable<Record<string, { message: string, timestamp: number }>> { return this.unresolvedIssues_; }

    constructor(opts: {onNewLogCallback?: (msg: LogMessage) => void} = {}) {
        this.onNewLogCallback = opts.onNewLogCallback;
        this.logger.debug("ClientModel instance created");
    }

    setup(){
        this.close(); // Ensure any existing connections are closed before setting up a new one
        this.logger.debug("Setting up ClientModel SSE connection...");
        this.connectSource();

        // Heartbeat watchdog + reconnect. `sseConnected` is driven by inbound
        // `heartbeat` messages (see handleMessage). If one hasn't arrived within
        // the timeout, mark the stream dead and rebuild it — the transport does
        // not auto-reconnect, and while the server is down the fetch rejects fast
        // so this effectively retries about once per watchdog interval.
        this.lastHeartbeatMs = Date.now();
        this.sseWatchdog = setInterval(() => {
            if (Date.now() - this.lastHeartbeatMs > ClientModel.SSE_HEARTBEAT_TIMEOUT_MS) {
                this.setSseConnected(false);
                this.logger.debug("SSE heartbeat missed; attempting to reconnect...");
                this.connectSource();
            }
        }, ClientModel.SSE_WATCHDOG_INTERVAL_MS);
    }

    /** (Re)establishes the SSE source and its subscriptions, tearing down any prior one. */
    private connectSource() {
        this.teardownSource();

        this.source = source('/sse', {
            error: (err) => {
                this.logger.error("SSE error:", err);
            },
            close: () => {
                this.logger.warn("SSE connection closed");
                this.setSseConnected(false);
            },
            open: () => {
                this.logger.info("SSE connection opened");
            }
        });

        this.sourceEvent = this.source.select('message').json<SSEMessage>(({error, raw, previous})=>{
            if(error){
                this.logger.error("Failed to parse SSE message:", error, "Raw data:", raw);
                return previous; // Return previous value on error to avoid breaking the stream
            }
            return previous;
        });

        this.unsubscribeSourceEvent = this.sourceEvent.subscribe((data) => {
            if (data === null) return;
            this.handleMessage(data);
        });
    }

    private teardownSource() {
        if(this.unsubscribeSourceEvent) {
            this.unsubscribeSourceEvent();
            this.unsubscribeSourceEvent = null;
        }
        if(this.source){
            this.source.close();
            this.source = null;
        }
    }

    private setSseConnected(connected: boolean) {
        this.sseConnected_.set(connected);
    }

    private handleMessage(msg: SSEMessage) {
        switch (msg.type) {
            case "connection-status":
                this.cppBackendConnectionStatus_.set(msg.status);
                break;
            case "app-version":
                this.appVersion_.set(msg.version);
                break;
            case "heartbeat":
                this.lastHeartbeatMs = Date.now();
                this.setSseConnected(true);
                break;
            case "interface":
                this.interfaceNames_.set(msg.interfaces);
                this.selectedInterface_.set(msg.selectedInterface);
                break;
            case "services":
                this.discoveredServices_.set(msg.services);
                this.selectedService_.set(msg.selectedService);
                break;
            case "capture":
                this.captureStatus_.set(msg.captureStatus);
                break;
            case "streamInfo":
                this.streamInfo_.set(msg.streamInfo);
                break;
            case "metadata":
                this.metadata_.set(msg.metadata);
                this.metadataFrameCounter_.set(msg.metadata?.frameCounter ?? 0);
                break;
            case "metadata-fps":
                this.metadataFps_.set(msg.fps);
                if (msg.realFps !== undefined) this.realFps_.set(msg.realFps);
                if (msg.realFpsHistory !== undefined) this.realFpsHistory_.set(msg.realFpsHistory);
                if (msg.sampleIntervalMs !== undefined) this.fpsSampleIntervalMs_.set(msg.sampleIntervalMs);
                break;
            case "log":
                this.logger[logLevelToString(msg.level).toLowerCase() as keyof LoggerBase](`Log message from server: ${msg.message} (timestamp: ${new Date(msg.timestamp).toISOString()})`);
                if(this.onNewLogCallback){
                    this.onNewLogCallback(msg);
                }
                break;
            case "issue":
                this.unresolvedIssues_.update(issues => {
                    if(msg.error){
                        this.logger.warn(`Received issue from server: ${msg.tag} - ${msg.error.message} (timestamp: ${msg.error.timestamp})`);
                        return {...issues, [msg.tag]: { message: msg.error.message, timestamp: new Date(msg.error.timestamp).getTime() }};
                    } else {
                        this.logger.info(`Issue resolved: ${msg.tag}`);
                        const {[msg.tag]: _, ...rest} = issues;
                        return rest;
                    }
                });
                break;
            default: {
                // Exhaustiveness check: if you add a new SSEMessage variant
                // above and forget to handle it here, this will fail to compile.
                const _exhaustive: never = msg;
                this.logger.warn("Received unknown SSE message", { msg: _exhaustive });
            }
        }
    }

    close(){
        if(this.sseWatchdog) {
            clearInterval(this.sseWatchdog);
            this.sseWatchdog = null;
        }
        this.setSseConnected(false);
        this.teardownSource();
    }

    async setInterface(interfaceName: string) {
        await fetch(`/api/interface`, { method: "POST", headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(interfaceName) }).then(response => {
            if(!response.ok){
                this.logger.error("Failed to set interface:", response.statusText);
                throw new Error(`Failed to set interface: ${response.statusText}`);
            }
        }).catch(err => {
            this.logger.error("Error setting interface:", err);
            throw err;
        });
    }

    async setService(service: DiscoveredService | null) {
        await fetch(`/api/service`, { method: "POST", headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(service) }).then(response => {
            if(!response.ok){
                this.logger.error("Failed to set service:", response.statusText);
                throw new Error(`Failed to set service: ${response.statusText}`);
            }
        }).catch(err => {
            this.logger.error("Error setting service:", err);
            throw err;
        });
    }
}
