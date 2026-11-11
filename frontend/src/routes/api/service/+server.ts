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

import { validateDiscoveredService, validateServiceSelection, type DiscoveredService, type ServiceSelection, type Status } from "$lib/cpp_backend_api/common/cpp_backend_types.js";
import { getGlobalServerModel } from "$lib/model/server/model.js";
import { getLogger } from "$lib/logger/server/mylogger";
import { json } from "@sveltejs/kit";
import { LogTag } from "$lib/logger/logTags";

const logger = getLogger(LogTag.API);

export async function GET({request, url}){
    return json(getGlobalServerModel().service);
}

/**
 * Start listening to a service
 */
export async function POST({request, url}){
    const service = await request.json().catch(e => {
        logger.error("Failed to parse service selection request body as JSON", { error: e });
        return undefined;
    }) as DiscoveredService | null | undefined;

    if(service === undefined){
        return json({ error: "Invalid request body" }, { status: 400 });
    }

    if(service && !validateDiscoveredService(service)){
        logger.error("Received invalid service selection in request body", { service });
        return json({ error: "Invalid service selection" }, { status: 400 });
    }

    try {
        await getGlobalServerModel().setService(service);
        return new Response(null, { status: 204 });
    } catch (err) {
        logger.error(`Backend rejected service selection: ${err instanceof Error ? err.message : String(err)}`);
        return json({ error: "Failed to set service" }, { status: 500 });
    }

}

