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
    import AudioElementIcon from "$lib/components/AudioElementIcon.svelte";
    import InfoTable from "$lib/components/InfoTable.svelte";
    import { isAudioBed, isAudioObject, type AudioBed, type AudioObject } from "$lib/cpp_backend_api/common/cpp_backend_types";
    import ADMAudioObjectsPanningView from "./ADMAudioObjectsPanningView.svelte";

    type Props = {
        obj: AudioObject | AudioBed;
        objIndex: number;
        theme?: "light" | "dark";
        color?: string;
        style?: string;
        highlighted?: boolean;
        minimized?: boolean;
        programmeIndices?: number[];
    };

    let {
        obj,
        objIndex,
        color,
        style,
        highlighted,
        minimized = false,
        programmeIndices = undefined,
        theme = "light"
    }: Props = $props();

    const objInfoTheme = $derived(theme === "dark" ? "light" : "dark");
    const asAudioObj = $derived(isAudioObject(obj) ? obj : undefined);
    const asAudioBed = $derived(isAudioBed(obj) ? obj : undefined);


    let info = $derived( asAudioObj !== undefined ? {
        type: "Object",
        channel: asAudioObj.channel + 1,
        gain: asAudioObj.gainDb.toFixed(1) + " dB",
        x: asAudioObj.x.toFixed(2),
        y: asAudioObj.y.toFixed(2),
        z: asAudioObj.z.toFixed(2),
        diverge: asAudioObj.diverge
    } : asAudioBed !== undefined ? {
        type: "Bed",
        channels: `${asAudioBed.start} - ${asAudioBed.start + asAudioBed.end-1}`,
        gain: asAudioBed.gainDb.toFixed(1) + " dB"
    } : undefined);

</script>


<div title={obj.name} class="adm-audio-object-view-main dp59x-foreground highlightable" class:highlighted={highlighted} style="display: flex; align-content: center; flex-direction: column; align-items: center; gap: 0.5em; opacity: {minimized ? '0.5' : '1'}; background-color: var(--dp59x-theme-{theme === "light" ? "fg" : "bg"}); {style}">
    <div id="header" class="grid-base" style="align-items: center; grid-template-columns: auto 1fr; width: 100%; gap: {minimized ? '0' : '0.5em'};" aria-label="{obj.name}">
        <AudioElementIcon label="{asAudioObj ? 'O' : 'B'}{objIndex+1}" color={minimized ? '#999' : color} style="font-size: small;"/>
        {#if !minimized}
        <div style="position: relative;">
            <div id="name-label" style="max-width: 200%; text-overflow: ellipsis; white-space: nowrap; text-align: left; background-color: var(--dp59x-theme-fg); overflow: hidden;">{obj.name}</div>
        </div>
        {/if}
    </div>

    {#if !minimized}
    <div class="grid-base" style="gap: 0.5em; width: 100%; grid-template-rows: 1fr auto; height: 100%; justify-items: center;">
        <div>
            <ADMAudioObjectsPanningView objects={asAudioObj ? [asAudioObj] : []} beds={asAudioBed ? [asAudioBed] : []} objColor={color} theme={theme} size="140px"/>
            {#if info !== undefined}
            <InfoTable data={info} style="width: fit-content; padding: 0.5em; box-sizing: border-box;" nowrap/>
            {/if}
        </div>
        <div style="display: flex; flex-direction: column; align-items: center; gap: 0.2em;">
            {#if programmeIndices !== undefined && programmeIndices.length > 0}
            <div style="opacity: 0.4; font-size: smaller;">References</div>
            <div class="in-a-row" style="gap: 0.4em;">
            {#each programmeIndices as programmeIndex}
                <AudioElementIcon label={`P${programmeIndex+1}`} color='var(--prog-color)' style="font-size: small;"/>
            {/each}
            </div>
            {/if}
        </div>
    </div>
    {/if}
</div>


<style>
    .adm-audio-object-view-main{
        border: 1px solid var(--dp59x-foreground);
        border-radius: 0.3em;
        padding: 0.5em;
        font-size: 1em;
    }

    #name-label {
        position: absolute;
        transform: translateY(-50%);
        padding: 0.2em 0 0.2em 0;
        width: 100%;
    }

    #header:hover>*>#name-label {
        z-index: 10;
        overflow: visible !important;
        padding-right: 1em;
        width: auto;
    }

    .grid-base > * {
        overflow: visible;
    }
</style>