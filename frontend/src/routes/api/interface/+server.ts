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
import { getGlobalServerModel } from "$lib/model/server/model";
import { json } from "@sveltejs/kit";
import { LogTag } from "$lib/logger/logTags";


/**
 * Returns the currently-selected interface (sourced from the cached
 * `interface` envelope, which is published by the C++ backend).
 */
export async function GET(){
    return json(getGlobalServerModel().interface);
}

export async function POST({request}){
    const logger = getLogger(LogTag.API);

    const interfaceName = await request.json().catch(e=>{
        logger.error("Failed to parse request body as JSON", {error: e});
        return null;
    }) as string | null;

    if(typeof interfaceName !== "string" && interfaceName !== null){
        logger.error("Received invalid interface name in request body", {interfaceName});
        return json({ error: "Invalid interface name" }, { status: 400 });
    }
    try {
        await getGlobalServerModel().setInterface(interfaceName);
    } catch (e) {
        logger.error(`Backend rejected interface selection (${interfaceName ?? "(cleared)"}): ${e instanceof Error ? e.message : String(e)}`);
        return json({ error: "Backend rejected interface selection" }, { status: 502 });
    }
    return new Response(null, { status: 204 });
}
