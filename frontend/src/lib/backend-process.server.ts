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

import { spawn, type ChildProcess } from 'node:child_process';
import { getLogger } from '$lib/logger/server/mylogger';
import { LogTag } from '$lib/logger/logTags';
import { getHealthStatus } from '$lib/cpp_backend_api/server/cpp_backend_api';

const log = () => getLogger(LogTag.CPP_BACKEND);

type ProcessState = {
    child: ChildProcess | null;
    ready: boolean;
};

type GlobalThisWithProcess = typeof globalThis & {
    _amViewerProcess?: ProcessState;
};

function getState(): ProcessState {
    const g = globalThis as GlobalThisWithProcess;
    if (!g._amViewerProcess) {
        g._amViewerProcess = { child: null, ready: false };
    }
    return g._amViewerProcess;
}

async function pollReady(timeoutMs = 15000, intervalMs = 250): Promise<boolean> {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
        try {
            await getHealthStatus();
            return true;
        } catch {
            await new Promise(r => setTimeout(r, intervalMs));
        }
    }
    return false;
}

export async function ensureBackendProcess(): Promise<void> {
    const binPath = process.env.AMV_BIN;
    if (!binPath) {
        log().info('AMV_BIN not set — skipping backend process launch (expecting am_viewer already running)');
        return;
    }

    const state = getState();
    if (state.child && state.child.exitCode === null) {
        log().debug('Backend process already running, skipping spawn');
        return;
    }

    log().info(`Spawning backend: ${binPath}`);
    const child = spawn(binPath, [], { stdio: ['ignore', 'pipe', 'pipe'] });
    state.child = child;
    state.ready = false;

    child.stdout!.on('data', (d: Buffer) => {
        for (const line of d.toString().split('\n')) {
            const trimmed = line.trim();
            if (trimmed) log().info(`[am_viewer] ${trimmed}`);
        }
    });
    child.stderr!.on('data', (d: Buffer) => {
        for (const line of d.toString().split('\n')) {
            const trimmed = line.trim();
            if (trimmed) log().warn(`[am_viewer] ${trimmed}`);
        }
    });
    child.on('exit', (code, signal) => {
        log().info(`Backend process exited (code=${code ?? 'null'}, signal=${signal ?? 'null'})`);
        state.ready = false;
        state.child = null;
    });
    child.on('error', (err) => {
        log().error(`Failed to start backend process: ${err.message}`);
        state.child = null;
    });

    log().info('Waiting for backend to become ready...');
    const ready = await pollReady();
    if (ready) {
        state.ready = true;
        log().info('Backend is ready');
    } else {
        log().error('Backend did not become ready within timeout');
    }
}

export function stopBackendProcess(): void {
    const state = getState();
    const child = state.child;
    if (!child || child.exitCode !== null) return;

    log().info('Stopping backend process (SIGTERM)...');
    child.kill('SIGTERM');

    // If it doesn't exit cleanly within 3 s, force-kill it.
    const t = setTimeout(() => {
        if (child.exitCode === null) {
            log().warn('Backend did not exit after SIGTERM — sending SIGKILL');
            child.kill('SIGKILL');
        }
    }, 3000);
    // Don't let this timer keep the Node process alive.
    t.unref();
}

export function isBackendReady(): boolean {
    return getState().ready;
}
