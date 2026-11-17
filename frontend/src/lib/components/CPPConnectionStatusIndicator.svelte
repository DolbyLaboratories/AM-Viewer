<!--
Copyright (c) 2026 Dolby International AB.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in
   the documentation and/or other materials provided with the
   distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived
   from this software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED
BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
-->

<script lang="ts">
    import type { CPPBackendConnectionStatus } from "$lib/model/common/types";

    let {status, size} = $props<{
        status: CPPBackendConnectionStatus,
        size: string
    }>();

</script>

<style>
    .cpp-connection-status-indicator {
        --red: #e74c3c;
        --yellow: #f1c40f;
        --green: #2ecc71;

        width: var(--size, 1rem);
        height: var(--size, 1rem);
        border-radius: 50%;
        background-color: var(--red);
        display: inline-block;
    }
</style>
<div class="in-a-row" style="gap: 0.5em;">
    <div style="opacity: 0.7;">Backend Service: {status === 'connected' ? 'OK' : status === 'connecting' ? '...' : 'KO'}</div>
    <div class="cpp-connection-status-indicator" style="--size: {size}; background-color: {status === "connected" ? "var(--green)" : status === "connecting" ? "var(--yellow)" : "var(--red)"};" title={status}></div>
</div>