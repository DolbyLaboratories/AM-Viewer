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
    import type { DiscoveredService } from "$lib/cpp_backend_api/common/cpp_backend_types";
    import CustomOverlayButton from "./CustomOverlayButton.svelte";
    import InfoTable from "./InfoTable.svelte";

    type Props = {
        service: DiscoveredService;
        highlighted?: boolean;
        onSelect: () => void;
    };


    let { service, onSelect, highlighted }: Props = $props();

    let sdpTextParsed = $derived(JSON.parse('"' + service.sdpText + '"'));

    function downloadSDP() {
        const blob = new Blob([sdpTextParsed], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${service.name}_sdp.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
</script>
<div style="position: relative;">
    <button class="dp59x-button" class:highlighted={highlighted} style="width: 100%;" onclick={onSelect}>
        <div style="text-align: start;">
            <div style="font-size: larger; width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: white; margin-bottom: 0.2em; text-align: center">{service.name}</div>
            <InfoTable data={{
                "Address": `${service.address}:${service.port}`,
                "Codec": service.codec
            }} style="width: fit-content;"/>
        </div>
    </button>
    {#if service.sdpText}
    <div style="position: absolute; right: 0.3em; bottom: 0.3em;">
        <CustomOverlayButton buttonText="SDP" title="SDP: {service.name}" buttonStyle="background-color: var(--dp59x-theme-fg); color: var(--dp59x-theme-on-fg); font-size: smaller;" >
            <textarea readonly style="width: 100%; height: 300px; font-family: monospace; font-size: small;">{sdpTextParsed}</textarea>
            <button class="dp59x-button" onclick={downloadSDP}>Download</button>
        </CustomOverlayButton>
    </div>
    {/if}
</div>

<style>
</style>
