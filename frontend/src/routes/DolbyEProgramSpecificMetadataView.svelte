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
    import Panel from "$lib/dp59x-theme/components/Panel.svelte";
    import ScrollingView from "$lib/dp59x-theme/components/ScrollingView.svelte";
    import { parsedDolbyEMetadataToFormatReadyForTable } from "$lib/model/common/dolbye_sorter";

    type Props = {
        sortedDolbyEMetadata: ReturnType<typeof parsedDolbyEMetadataToFormatReadyForTable>;
        programmeIndex?: number;
        theme?: "light" | "dark";
        style?: string;
    }

    const { sortedDolbyEMetadata, theme, style, programmeIndex }: Props = $props();
    const showGlobalFields = $derived(programmeIndex === undefined);
    const programIndicesToShow = $derived(programmeIndex !== undefined ? [programmeIndex] : Array(sortedDolbyEMetadata.numberOfPrograms).fill(0).map((_, i) => i));

</script>

<ScrollingView x>
<table class="all-metadata-table" style="height: max-content;">
    <tbody>
        <tr>
            <th rowspan="2" style="font-weight: bolder;">Field Name</th>
            <th colspan="{programIndicesToShow.length}" style="font-weight: bolder;">Value</th>
        </tr>
        <tr>
            {#each programIndicesToShow as i}
                <th style="font-weight: bolder;">
                    <div class="in-a-row" style="justify-content: center;">
                        <div style="white-space: nowrap;">
                            Program {i+1}
                        </div>
                    </div>
                </th>
            {/each}
        </tr>
        {#if showGlobalFields}
        <tr>
            <th colspan="{programIndicesToShow.length+1}" style="background-color: var(--dp59x-theme-border)">Global Fields</th>
        </tr>
        {#each Object.entries(sortedDolbyEMetadata.globalRows) as [label, value]}
            <tr>
                <th style="text-align: end; opacity: 0.7">{label}</th>
                <td style="text-align: left;" colspan="{programIndicesToShow.length}">{value !== null ? value : "-"}</td>
            </tr>
        {/each}
        {/if}
        {#each Object.entries(sortedDolbyEMetadata.map) as [group, fields]}
        <tr>
            <th colspan="{programIndicesToShow.length+1}" style="background-color: var(--dp59x-theme-border)">{group}</th>
        </tr>
        {#each Object.entries(fields) as [label, values]}
            <tr>
                <th style="text-align: end; opacity: 0.7; max-width: 180px;">{label}</th>
                {#each values.filter((v, i) => programIndicesToShow.includes(i)) as v, i (i)}
                    <td style="text-align: left; max-width: 170px;">{v !== null ? v : "-"}</td>
                {/each}
            </tr>
        {/each}
        {/each}
    </tbody>
</table>
</ScrollingView>

<style>

    .all-metadata-table {
        border-collapse: collapse;
        color: var(--dp59x-theme-on-fg);
    }

    .all-metadata-table th {
        font-weight: normal;
        color: var(--dp59x-theme-on-bg);
        background-color: var(--dp59x-theme-fg);
    }

    .all-metadata-table td {
        background-color: var(--dp59x-theme-fg);
    }

    .all-metadata-table th, .all-metadata-table td {
        border: 1px solid var(--dp59x-theme-border);
        padding: 0.3em 0.6em;
    }

    .all-metadata-table tbody tr:nth-child(odd) {
        background-color: var(--dp59x-theme-bg);
    }
</style>