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

import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { createStream, type RotatingFileStream } from "rotating-file-stream";
import { LogLevel, type LogRecord, type LoggerBase, LogManager } from "../types";

// Logs are written as JSON Lines (NDJSON): one JSON record per line. This lets
// us *append* new records to the active file instead of rewriting the whole
// file, and parse the file back line-by-line on startup.
const LOG_DIR = "logs";
const LOG_BASENAME = "app.log"; // the active (un-rotated) file: logs/app.log
const MAX_LOGS = 10000; // in-memory ring buffer cap (does not bound the files)
const ROTATE_SIZE = "10M"; // rotate the active file once it reaches this size
const MAX_FILES = 10; // keep at most this many rotated files; older ones are removed

type ServerLogRecord = LogRecord & {
    visibleToClient: boolean;
};

type ServerLoggerBase = LoggerBase & {
    debugPublic: (tag: string, ...args: any[]) => void;
    infoPublic: (tag: string, ...args: any[]) => void;
    warnPublic: (tag: string, ...args: any[]) => void;
    errorPublic: (tag: string, ...args: any[]) => void;
}


/**
 * rfs filename generator. Called with a falsy `time` for the active file, and
 * with a rotation timestamp + index for rotated files. Rotated files embed a
 * fixed-width timestamp so a lexical sort of the directory is also chronological.
 */
const logFilename = (time: number | Date, index?: number): string => {
    if (!time) return LOG_BASENAME;
    const d = time instanceof Date ? time : new Date(time);
    const p = (n: number) => String(n).padStart(2, "0");
    const stamp =
        `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}` +
        `-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
    return `${LOG_BASENAME}.${stamp}.${index ?? 1}.gz`;
};

/**
 * Logger with the option to share logs with clients.
 *
 * Public (client-visible) logs are streamed to disk as JSON Lines via
 * rotating-file-stream and replayed into an in-memory ring buffer on startup.
 */
class MyLogger extends LogManager<ServerLogRecord> {
    private stream: RotatingFileStream | null = null;
    private newLogCallbacks: Set<(logs: ServerLogRecord) => void> = new Set();
    protected publicLogs: ServerLogRecord[] = [];
    private loggerMap: Map<string, ServerLoggerBase> = new Map();

    log(record: ServerLogRecord) {
        super.log(record);
        // Persist every record (public and internal); only public records are
        // kept in memory and pushed to clients.
        this.appendToFile(record);
        if (record.visibleToClient) {
            this.publicLogs.push(record);
            if (this.publicLogs.length > MAX_LOGS) {
                this.publicLogs.shift();
            }
            for (const cb of this.newLogCallbacks) {
                cb(record);
            }
        }
    }

    /**
     * Load existing logs into the in-memory buffer, then open the append stream.
     * Reads the active file plus, if needed, recent rotated (gzipped) files —
     * newest first — until the buffer is full (bounded to MAX_LOGS).
     */
    start() {
        this.loadLogs();
        this.initStream();
    }

    private appendToFile(record: ServerLogRecord) {
        if (!this.stream) return;
        try {
            this.stream.write(JSON.stringify(record) + "\n");
        } catch (e) {
            // Avoid recursing into a public log here; report to console only.
            super.log({
                timestamp: Date.now(),
                level: LogLevel.ERROR,
                tag: "LogManager",
                message: `Failed to write log to file: ${e}`,
                visibleToClient: false
            });
        }
    }

    private initStream() {
        try {
            this.stream = createStream(logFilename, {
                path: LOG_DIR,
                size: ROTATE_SIZE,
                maxFiles: MAX_FILES,
                compress: "gzip"
            });
            this.stream.on("error", (err) =>
                this.error("LogManager", "Log file stream error:", err)
            );
        } catch (e) {
            this.error("LogManager", "Failed to open log file stream:", e);
            this.stream = null;
        }
    }

    private loadLogs() {
        try {
            if (!fs.existsSync(LOG_DIR)) {
                this.publicLogs = [];
                return;
            }

            // The file holds both public and internal records; only public ones
            // are kept in memory, so filter as we read.
            const readPublic = (fp: string) =>
                this.readLogFile(fp).filter((r) => r.visibleToClient);

            // Active file first (chronological order within the file).
            let loaded = readPublic(path.join(LOG_DIR, LOG_BASENAME));

            // Backfill from rotated files, newest first, until the buffer is full.
            if (loaded.length < MAX_LOGS) {
                const rotated = fs
                    .readdirSync(LOG_DIR)
                    .filter((f) => f.startsWith(LOG_BASENAME + ".") && f.endsWith(".gz"))
                    .sort()
                    .reverse();
                for (const f of rotated) {
                    if (loaded.length >= MAX_LOGS) break;
                    loaded = readPublic(path.join(LOG_DIR, f)).concat(loaded);
                }
            }

            if (loaded.length > MAX_LOGS) {
                loaded = loaded.slice(loaded.length - MAX_LOGS);
            }
            this.publicLogs = loaded;
            this.info("LogManager", `Loaded ${this.publicLogs.length} logs from ${LOG_DIR}/`);
        } catch (e) {
            this.error("LogManager", "Failed to load logs from file:", e);
            this.publicLogs = [];
        }
    }

    private readLogFile(filepath: string): ServerLogRecord[] {
        if (!fs.existsSync(filepath)) return [];
        let buf = fs.readFileSync(filepath);
        if (filepath.endsWith(".gz")) buf = zlib.gunzipSync(buf);
        const out: ServerLogRecord[] = [];
        for (const line of buf.toString("utf-8").split("\n")) {
            const trimmed = line.trim();
            if (!trimmed) continue;
            try {
                out.push(JSON.parse(trimmed) as ServerLogRecord);
            } catch {
                // Skip a corrupt or partially-written final line.
            }
        }
        return out;
    }

    infoPublic(tag: string, ...args: any[]) {
        this.log({ timestamp: Date.now(), level: LogLevel.INFO, tag, message: MyLogger.buildMessage(...args), visibleToClient: true });
    }

    debugPublic(tag: string, ...args: any[]) {
        this.log({ timestamp: Date.now(), level: LogLevel.DEBUG, tag, message: MyLogger.buildMessage(...args), visibleToClient: true });
    }

    warnPublic(tag: string, ...args: any[]) {
        this.log({ timestamp: Date.now(), level: LogLevel.WARN, tag, message: MyLogger.buildMessage(...args), visibleToClient: true });
    }

    errorPublic(tag: string, ...args: any[]) {
        this.log({ timestamp: Date.now(), level: LogLevel.ERROR, tag, message: MyLogger.buildMessage(...args), visibleToClient: true });
    }

    getPublicLogs(): ServerLogRecord[] {
        return this.publicLogs;
    }

    /** Alias kept for callers that request only client-visible logs. */
    getLogs(_visibleToClientOnly: boolean = true): ServerLogRecord[] {
        return this.publicLogs;
    }

    /**
     * Read *every* persisted record (public and internal) from disk, in
     * chronological order: oldest rotated file first, ending with the active
     * file. Unlike the in-memory buffer this is not bounded to MAX_LOGS and is
     * not filtered by visibleToClient — it's the full on-disk history, used for
     * the "download all logs" export. Records still buffered by the file stream
     * and not yet flushed may be absent.
     */
    getAllPersistedLogs(): ServerLogRecord[] {
        try {
            if (!fs.existsSync(LOG_DIR)) return [];
            // Rotated files sort ascending into chronological order (their
            // fixed-width timestamps make a lexical sort chronological).
            const rotated = fs
                .readdirSync(LOG_DIR)
                .filter((f) => f.startsWith(LOG_BASENAME + ".") && f.endsWith(".gz"))
                .sort();
            let all: ServerLogRecord[] = [];
            for (const f of rotated) {
                all = all.concat(this.readLogFile(path.join(LOG_DIR, f)));
            }
            // Active (un-rotated) file holds the newest records.
            all = all.concat(this.readLogFile(path.join(LOG_DIR, LOG_BASENAME)));
            return all;
        } catch (e) {
            this.error("LogManager", "Failed to read all logs from file:", e);
            return [];
        }
    }

    onNewLog(callback: (logs: ServerLogRecord) => void) {
        this.newLogCallbacks.add(callback);

        return () => {
            this.offNewLog(callback);
        };
    }

    offNewLog(callback: (logs: ServerLogRecord) => void) {
        this.newLogCallbacks.delete(callback);
    }

    getLogger(tag: string): ServerLoggerBase {
        if (this.loggerMap.has(tag)) {
            return this.loggerMap.get(tag)!;
        }
        const logger: ServerLoggerBase = {
            debug: (...args: any[]) => this.debug(tag, ...args),
            info: (...args: any[]) => this.info(tag, ...args),
            warn: (...args: any[]) => this.warn(tag, ...args),
            error: (...args: any[]) => this.error(tag, ...args),
            debugPublic: (...args: any[]) => this.debugPublic(tag, ...args),
            infoPublic: (...args: any[]) => this.infoPublic(tag, ...args),
            warnPublic: (...args: any[]) => this.warnPublic(tag, ...args),
            errorPublic: (...args: any[]) => this.errorPublic(tag, ...args),
        };
        this.loggerMap.set(tag, logger);
        return logger;
    }
}



type GlobalThisWithLogManager = typeof globalThis & {
    logManager?: MyLogger;
};

export function getLogManager(logLevel: typeof LogLevel[keyof typeof LogLevel] = LogLevel.DEBUG): MyLogger {
    const globalLogManager = (globalThis as GlobalThisWithLogManager).logManager;
    if (globalLogManager) {
        return globalLogManager;
    }
    const newLogManager = new MyLogger(logLevel);
    newLogManager.start();
    (globalThis as GlobalThisWithLogManager).logManager = newLogManager;
    return newLogManager;
}

export function getLogger(tag: string, blacklist: boolean = false): ServerLoggerBase {
    const logManager = getLogManager();
    return logManager.getLogger(tag);
}


