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

import { getLogger, getLogManager } from '$lib/logger/server/mylogger';
import { getGlobalServerModel } from '$lib/model/server/model';
import { fail } from '@sveltejs/kit';
import { LogTag } from "$lib/logger/logTags";

const logger = getLogger(LogTag.API);

export async function load(){
    const logManager = getLogManager();
    const logs = logManager.getPublicLogs();
    return {
        logs,
        showPowerBtn: process.env.AMV_SHOW_POWERBTN === '0' ? false
            : process.env.AMV_SHOW_POWERBTN === '1' ? true
            : !!process.env.AMV_BIN,
    };
}

export const actions = {
    selectServiceBySDP: async ({request})=>{
        const formData = await request.formData();
        const sdpText = formData.get('sdpText');
        if (typeof sdpText !== 'string') {
            logger.error("selectServiceBySDP action received invalid SDP text");
            return fail(400, {error: 'Invalid SDP text'});
        }
        const model = getGlobalServerModel();
        try {
            await model.setServiceBySDP(sdpText);
        } catch (e) {
            // model.setServiceBySDP already emits a public error; this records the detail.
            logger.error(`selectServiceBySDP action failed: ${e instanceof Error ? e.message : String(e)}`);
            return fail(502, {error: 'Backend rejected SDP selection'});
        }

        return {success: true};
    },
    resetIssue: async ({ request })=>{
        const formData = await request.formData();
        const key = formData.get("key");
        if(typeof key !== "string"){
            logger.error(`Missing or invalid issue key in resetIssue action (got ${key})`);
            return fail(400, {error: "Missing issue key"});
        }
        const model = getGlobalServerModel();
        model.resetIssueFlag(key);
        logger.info(`Reset issue flag for key: ${key}`);
        return {success: true};
    }
}