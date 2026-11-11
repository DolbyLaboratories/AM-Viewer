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

import type { CaptureStatus, DiscoveredService, ModelSummary, ServiceSelection, Status, UIState } from "../common/cpp_backend_types";
import { getLogger } from "$lib/logger/server/mylogger";
import { LogTag } from "$lib/logger/logTags";

function log() {
    return getLogger(LogTag.CPP_BACKEND);
}

export type APIEndpointParams = {
    host: string;
    port: number;
    protocol?: "http" | "https";
}

export function getDefaultAPIEndpoint(): APIEndpointParams {
    const endpoint: APIEndpointParams = {
        host: process.env.AMV_BACKEND_HOST || "localhost",
        port: parseInt(process.env.AMV_BACKEND_PORT || "8000"),
        protocol: process.env.AMV_BACKEND_PROTOCOL as "http" | "https" || "http",
    };
    log().info("Using default API Endpoint Params:", { ...endpoint });
    return endpoint;
}

export function apiEndpointParamsFromEnv(): APIEndpointParams {
    const defaultEndpoint = getDefaultAPIEndpoint();
    const host = process.env.AMV_BACKEND_HOST || defaultEndpoint.host;
    const port = parseInt(process.env.AMV_BACKEND_PORT || defaultEndpoint.port.toString());
    const protocol = process.env.AMV_BACKEND_PROTOCOL as "http" | "https" || defaultEndpoint.protocol;
    return { host, port, protocol };
}

function buildAPIUrl(endpoint: APIEndpointParams, path: string, queryParams?: URLSearchParams): string {
    const protocol = endpoint.protocol || "http";
    const url = `${protocol}://${endpoint.host}:${endpoint.port}${path}`;
    return queryParams ? `${url}?${queryParams.toString()}` : url;
}

export async function getHealthStatus(endpoint: APIEndpointParams = getDefaultAPIEndpoint()): Promise<Status> {
    const response = await fetch(buildAPIUrl(endpoint, "/api/health"));
    if (!response.ok) {
        log().warn(`Failed to fetch health status: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to fetch health status: ${response.statusText}`);
    }
    return response.json() as Promise<Status>;
}

export async function getModel(endpoint: APIEndpointParams = getDefaultAPIEndpoint()): Promise<ModelSummary> {
    const response = await fetch(buildAPIUrl(endpoint, "/api/model"));
    if (!response.ok) {
        log().warn(`Failed to fetch model summary: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to fetch model summary: ${response.statusText}`);
    }
    return response.json() as Promise<ModelSummary>;
}

export async function getInterfaces(endpoint: APIEndpointParams = getDefaultAPIEndpoint()): Promise<string[]> {
    const response = await fetch(buildAPIUrl(endpoint, "/api/interfaces"));
    if (!response.ok) {
        log().error(`Failed to fetch interfaces: ${response.statusText}`);
        throw new Error(`Failed to fetch interfaces: ${response.statusText}`);
    }
    return response.json() as Promise<string[]>;
}

export async function getServices(endpoint: APIEndpointParams = getDefaultAPIEndpoint(), interfaceName: string, timeoutMs: number = 5000): Promise<DiscoveredService[]> {
    const queryParams = new URLSearchParams({ interface: interfaceName, timeoutMs: timeoutMs.toString() });
    const response = await fetch(buildAPIUrl(endpoint, "/api/services/discover", queryParams));
    if (!response.ok) {
        log().errorPublic(`Failed to discover services on interface ${interfaceName}: ${response.statusText} (${response.url})`);
        throw new Error(`Failed to fetch services: ${response.statusText}`);
    }
    return response.json() as Promise<DiscoveredService[]>;
}


export async function selectInterface(
    endpoint: APIEndpointParams = getDefaultAPIEndpoint(),
    interfaceName: string | null
): Promise<Status> {
    const response = await fetch(buildAPIUrl(endpoint, "/api/interface"), {
        method: "POST",
        body: interfaceName || "", // Send empty body to clear selection when interfaceName is null
        headers: { "Content-Type": "text/plain" },
    });
    if (!response.ok) {
        log().error('Request to select interface failed: ', {
            statusText: response.statusText,
            url: response.url,
            interfaceName,
        });
        throw new Error(`Failed to select interface: ${response.statusText}`);
    }
    log().debug(`Interface selection request succeeded: ${interfaceName ?? "(cleared)"}`);
    return response.json() as Promise<Status>;
}

export async function selectService(
    endpoint: APIEndpointParams = getDefaultAPIEndpoint(), 
    service: ServiceSelection|null
): Promise<Status> {

    if(service === null) {
        // Clear selection by sending empty body
        const response = await fetch(buildAPIUrl(endpoint, "/api/service/clear"), {
            method: "POST"
        });
        
        if (!response.ok) {
            log().error('Request to clear service selection failed: ', {
                statusText: response.statusText,
                url: response.url,
            });
            throw new Error(`Failed to clear service selection: ${response.statusText}`);
        }
        log().debug("Service selection cleared");
        return response.json() as Promise<Status>;
    }
    const response = await fetch(buildAPIUrl(endpoint, "/api/service"), {
        method: "POST",
        body: JSON.stringify(service),
        headers: {
            "Content-Type": "application/json",
        }
    });

    if (!response.ok) {
        log().error('Request to select service failed: ', {
            statusText: response.statusText,
            url: response.url,
            service,
        });
        throw new Error(`Failed to select service: ${response.statusText}`);
    }
    log().debug(`Service selection request succeeded: ${service.name} (${service.address}:${service.port})`);
    return response.json() as Promise<Status>;
}

export async function getUIState(endpoint: APIEndpointParams = getDefaultAPIEndpoint()): Promise<UIState> {
    const response = await fetch(buildAPIUrl(endpoint, "/api/ui-state"));
    if (!response.ok) {
        log().warn(`Failed to fetch UI state: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to fetch UI state: ${response.statusText}`);
    }
    return response.json() as Promise<UIState>;
}

export async function loadXMLUpload(endpoint: APIEndpointParams = getDefaultAPIEndpoint(), name: string, body: string): Promise<Status> {

    const queryParams = new URLSearchParams({ name });
    const response = await fetch(buildAPIUrl(endpoint, "/api/model/upload", queryParams), {
        method: "POST",
        body: body,
        headers: {
            "Content-Type": "application/xml",
            "X-Filename": name,
        },
    });
    if (!response.ok) {
        log().errorPublic(`Failed to load XML file "${name}": ${response.status} ${response.statusText}`);
        throw new Error(`Failed to upload XML file: ${response.statusText}`);
    }
    log().infoPublic(`Loaded XML file "${name}" (${body.length} bytes)`);
    return response.json() as Promise<Status>;
}

export type StartCaptureParams = {
    interfaceName: string;
    address: string;
    port: number;
    codec: string;
}

export async function startCapture(endpoint: APIEndpointParams = getDefaultAPIEndpoint(), params: StartCaptureParams): Promise<Status> {
    const queryParams = new URLSearchParams({
        interface: params.interfaceName,
        address: params.address,
        port: params.port.toString(),
        codec: params.codec,
    });
    const response = await fetch(buildAPIUrl(endpoint, "/api/capture/start", queryParams), {
        method: "POST",
    });
    if (!response.ok) {
        log().errorPublic(`Failed to start capture on ${params.interfaceName} (${params.address}:${params.port}, ${params.codec}): ${response.status} ${response.statusText}`);
        throw new Error(`Failed to start capture: ${response.statusText}`);
    }
    log().infoPublic(`Capture started on ${params.interfaceName} (${params.address}:${params.port}, ${params.codec})`);
    return response.json() as Promise<Status>;
}

export async function stopCapture(endpoint: APIEndpointParams = getDefaultAPIEndpoint()): Promise<Status> {
    const response = await fetch(buildAPIUrl(endpoint, "/api/capture/stop"), {
        method: "POST",
    });
    if (!response.ok) {
        log().errorPublic(`Failed to stop capture: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to stop capture: ${response.statusText}`);
    }
    log().infoPublic("Capture stopped");
    return response.json() as Promise<Status>;
}

export async function shutdown(endpoint: APIEndpointParams = getDefaultAPIEndpoint()): Promise<Status> {
    log().info("Requesting C++ backend shutdown");
    const response = await fetch(buildAPIUrl(endpoint, "/api/app/exit"), {
        method: "POST",
    });
    if (!response.ok) {
        log().error(`Failed to shutdown backend: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to shutdown backend: ${response.statusText}`);
    }
    return response.json() as Promise<Status>;
}

export async function getCaptureStatus(endpoint: APIEndpointParams = getDefaultAPIEndpoint()): Promise<CaptureStatus> {
    const response = await fetch(buildAPIUrl(endpoint, "/api/capture/status"));
    if (!response.ok) {
        log().warn(`Failed to fetch capture status: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to fetch capture status: ${response.statusText}`);
    }
    return response.json() as Promise<CaptureStatus>;
}

export async function getDeframerStats(endpoint: APIEndpointParams = getDefaultAPIEndpoint()): Promise<any> {
    const response = await fetch(buildAPIUrl(endpoint, "/api/capture/deframer_stats"));
    if (!response.ok) {
        log().warn(`Failed to fetch deframer stats: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to fetch deframer stats: ${response.statusText}`);
    }
    return response.json() as Promise<any>;
}

export async function selectServiceBySDP(endpoint: APIEndpointParams = getDefaultAPIEndpoint(), sdpText: string): Promise<Status> {
    const response = await fetch(buildAPIUrl(endpoint, "/api/service/sdp"), {
        method: "POST",
        body: sdpText,
        headers: {
            "Content-Type": "text/plain",
        },
    });
    if (!response.ok) {
        try {
            const status = await response.text();
            log().error('Request to select service by SDP failed: ', {
                statusText: response.statusText,
                url: response.url,
                sdpText,
                status,
            });
        } catch {
            log().error('Request to select service by SDP failed: ', {
                statusText: response.statusText,
                url: response.url,
                sdpText,
                status: "(Failed to parse error response)",
            });
        }
        throw new Error(`Failed to select service by SDP: ${response.statusText}`);
    }
    return response.json() as Promise<Status>;
}

export async function getLiveXML(endpoint: APIEndpointParams = getDefaultAPIEndpoint()): Promise<string> {
    const response = await fetch(buildAPIUrl(endpoint, "/api/live-xml"));
    if (!response.ok) {
        log().warn(`Failed to fetch live XML: ${response.status} ${response.statusText}`);
        throw new Error(`Failed to fetch live XML: ${response.statusText}`);
    }
    return response.text();
}