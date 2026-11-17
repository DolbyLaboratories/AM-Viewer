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

import { getLogger, getLogManager } from "$lib/logger/server/mylogger";
import { getGlobalServerModel } from "$lib/model/server/model";
import { produce } from "sveltekit-sse";
import { LogTag } from "$lib/logger/logTags";

const logger = getLogger(LogTag.APP_SERVER);
export function POST(){
    return produce(async function start({emit}) {
        logger.info("Client has connected to SSE endpoint");

        const unsubscribe = getGlobalServerModel().onMessage((message)=>{
            emit('message', JSON.stringify(message));
        });

        const logsUnsubscribe = getLogManager().onNewLog((logEntry)=>{
            const logMessage = {
                type: "log",
                level: logEntry.level,
                tag: logEntry.tag,
                message: logEntry.message,
                timestamp: logEntry.timestamp,
            };
            emit('message', JSON.stringify(logMessage));
        });

        // Application-level liveness beat. The client watches for these and marks
        // the SSE stream dead if they stop arriving. Emitted well within the
        // client's timeout so ordinary jitter doesn't trip a false disconnect.
        const heartbeat = setInterval(()=>{
            const { error } = emit('message', JSON.stringify({ type: "heartbeat", timestamp: Date.now() }));
            if(error){
                clearInterval(heartbeat);
            }
        }, 500);

        return function stop(){
            clearInterval(heartbeat);
            logger.info("Unsubscribing from model messages for SSE client");
            unsubscribe();
            logger.info("Unsubscribing from log messages for SSE client");
            logsUnsubscribe();
        };
    }, {
        ping: 1000,
        stop(){
            logger.info("Client has disconnected");
        }
    });
}
