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

import { logLevelToString } from "./util";

export const LogLevel = {
    DEBUG: 0,
    INFO: 1,
    WARN: 2,
    ERROR: 3
} as const;


export type LogRecord = {
    timestamp: number;
    level: typeof LogLevel[keyof typeof LogLevel];
    tag: string;
    message: string;
};

export type LoggerBase = {
    debug: (...args: any[]) => void;
    info: (...args: any[]) => void;
    warn: (...args: any[]) => void;
    error: (...args: any[]) => void;
};



export class LogManager<T extends LogRecord = LogRecord> implements LoggerBase {
    logLevel: typeof LogLevel[keyof typeof LogLevel] = LogLevel.DEBUG;

    constructor(logLevel: typeof LogLevel[keyof typeof LogLevel] = LogLevel.DEBUG) {
        this.logLevel = logLevel;
    }

    log(record: T) {
        if (record.level >= this.logLevel) {
            const levelStr = logLevelToString(record.level);
            const msg = `${new Date(record.timestamp).toISOString().padEnd(24)} | ${levelStr.padEnd(5)} | [${record.tag}] ${record.message}`;
            switch(record.level) {
                case LogLevel.INFO:
                    console.info(msg);
                    break;
                case LogLevel.WARN:
                    console.warn(msg);
                    break;
                case LogLevel.ERROR:
                    console.error(msg);
                    break;
                case LogLevel.DEBUG:
                    console.debug(msg);
                    break;
            }
        }
    }

    static buildMessage(...args: any[]): string {
        return args.map(arg => (typeof arg === "string" ? arg : JSON.stringify(arg))).join(" ");
    }

    debug(tag: string, ...args: any[]) {
        this.log({ timestamp: Date.now(), level: LogLevel.DEBUG, tag, message: LogManager.buildMessage(...args) } as T);
    }

    info(tag: string, ...args: any[]) {
        this.log({ timestamp: Date.now(), level: LogLevel.INFO, tag, message: LogManager.buildMessage(...args) } as T);
    }

    warn(tag: string, ...args: any[]) {
        this.log({ timestamp: Date.now(), level: LogLevel.WARN, tag, message: LogManager.buildMessage(...args) } as T);
    }

    error(tag: string, ...args: any[]) {
        this.log({ timestamp: Date.now(), level: LogLevel.ERROR, tag, message: LogManager.buildMessage(...args) } as T);
    }
}
