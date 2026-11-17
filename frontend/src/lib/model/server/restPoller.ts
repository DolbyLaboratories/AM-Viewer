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

export class MyLoopingFunction {
    readonly args: any[];
    private timeout: NodeJS.Timeout|null = null;
    readonly logger;

    constructor(
        readonly name: string,
        readonly intervalMs: number, 
        readonly callback: (...args: any[])=>Promise<void>,
        ...args: any[]
    ){
        this.args = args;
        this.logger = getLogger(name);
    }

    async once(){
        await this.callback(...this.args);
    }

    stop(withLogging: boolean = true){
        if(this.timeout){
            clearTimeout(this.timeout);
            this.timeout = null;
            if(withLogging){
                this.logger.debug("Stopped");
            }
        }
    }

    async restart(firstTime: boolean = true){
        this.stop(firstTime);

        this.once().catch(er => {
            this.logger.error("Error in callback:", er);
        }).finally(()=>{
            this.timeout = setTimeout(()=>this.restart(false), this.intervalMs);
        });

        if(firstTime){
            this.logger.debug("Started with interval", this.intervalMs, "ms");
        }
    }
}

// export class RESTPoller<T = object> extends MyLoopingFunction{
//     private previousValue = writable<T|null>(null);
//     readonly value: Readable<T|null> = this.previousValue;

//     constructor(name: string, readonly url: string, readonly method: string, intervalMs: number, private readonly opts: {
//         dataAdapter?: (value: Response)=>Promise<T>;
//         compareFunction?: (a: T, b: T)=>boolean;
//         method?: string;
//     } = {}){
//         super(name, intervalMs, ()=>{return this.lfCallback()});
//     }

//     private async lfCallback(){
//         await fetch(this.url, {method: this.opts.method ?? "GET"}).then(this.opts.dataAdapter || ((value: Response)=>value.json())).then((newValue:T)=>{
//             this.previousValue.update(prev=>{
//                 if(prev === null) return newValue;
//                 const compareFn = this.opts.compareFunction || ((a, b)=>{return a!=b});
//                 if(compareFn(prev, newValue)){
//                     return newValue;
//                 }
//                 return prev;
//             });
//         });
//     }
// }