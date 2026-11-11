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

import { getLogger } from "$lib/logger/server/mylogger";
import { writable, type Readable } from "svelte/store";
import type { WebsocketMessage } from "./types";

export class CppBackendWSClient {
    private readonly logger = getLogger('CppBackendWSClient')
    private ws: WebSocket|null = null;
    private status_ = writable<number>(WebSocket.CLOSED);
    private reconnectOnClose = false;
    readonly status: Readable<number> = this.status_;
    private reconnectTimeout: NodeJS.Timeout|null = null;
    readonly wsEndpointURL: string;

    onmessage: ((msg: WebsocketMessage)=>void) | null = null;

    constructor(readonly host: string, readonly port: number){
        this.wsEndpointURL = `ws://${host}:${port}/ws`;
        this.logger.debug(`Creating CppBackendWSClient @ ${this.wsEndpointURL}`);
        this.reconnect("initialising");
    }

    private disconnect(){
        if(this.ws){
            this.status_.set(WebSocket.CLOSING);
            this.ws?.close();
        }
    }

    private reconnect(reason?: string){
        if(this.reconnectTimeout){
            clearTimeout(this.reconnectTimeout);
        }
        this.reconnectTimeout = setTimeout(()=>{
            this.logger.debug(`${this.ws ? "Rec" : "C"}onnecting WebSocket${reason ? ` because "${reason}"` : ""}...`);
            this.ws = this.createNewClient();
            this.reconnectOnClose = true;
        }, 1000);
    }

    private createNewClient(): WebSocket{
        const ws = new WebSocket(this.wsEndpointURL);
        ws.onclose = (ev: CloseEvent)=>{
            this.status_.set(WebSocket.CLOSED);
            if(this.reconnectOnClose){
                this.logger.warn(`WebSocket closed unexpectedly: "${ev.reason}"`);
                this.reconnect(`WebSocket closed: "${ev.reason}"`);
            } else {
                this.logger.info(`WebSocket closed: "${ev.reason}"`);
            }
        }
        ws.onerror = (ev: Event)=>{
            this.logger.warn(`WebSocket error`);
            ws.close();
        }

        ws.onopen = (ev: Event)=>{
            this.logger.info(`WebSocket connected`);
            this.status_.set(WebSocket.OPEN);
        }

        ws.onmessage = (ev: MessageEvent)=>{
            try{
                const msg = JSON.parse(ev.data) as WebsocketMessage;
                this.onmessage?.(msg);
            } catch(e){
                this.logger.warn(`Failed to handle message: ${e instanceof Error ? e.message : String(e)}`);
            }
        }

        this.status_.set(WebSocket.CONNECTING);

        return ws;
    }

    close(){
        this.reconnectOnClose = false;
        if(this.reconnectTimeout){
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }
        this.ws?.close();
    }
}