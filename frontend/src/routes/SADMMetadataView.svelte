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
    import Spinner from "$lib/dp59x-theme/components/Spinner.svelte";
    import type { Metadata } from "$lib/cpp_backend_api/server/ws/types";
    import type { Readable } from "svelte/store";
    import AudioElementIcon from "$lib/components/AudioElementIcon.svelte";
    import {type AudioPresentation } from "$lib/cpp_backend_api/common/cpp_backend_types";
    import InfoTable from "$lib/components/InfoTable.svelte";
    import Panel from "$lib/dp59x-theme/components/Panel.svelte";
    import TabsView from "$lib/dp59x-theme/components/TabsView.svelte";
    import ADMAudioObjectOrBedView from "./ADMAudioObjectOrBedView.svelte";
    import DolbyEProgramSpecificMetadataView from "./DolbyEProgramSpecificMetadataView.svelte";
    import { parseAllDolbyEMetadataFieldsIntoSomethingUseful, parsedDolbyEMetadataToFormatReadyForTable } from "$lib/model/common/dolbye_sorter";
    import ScrollingView from "$lib/dp59x-theme/components/ScrollingView.svelte";

    type ExportedProps = {
        metadata: Readable<Metadata|null>;
        theme?: "light" | "dark";
        style?: string;
        programmeTabIndex?: number;
        getSadmXmlFilename?: () => string;
    };

    let { metadata, theme, style, programmeTabIndex = $bindable(0), getSadmXmlFilename }: ExportedProps = $props();

    const panelTheme = $derived(theme === "dark" ? "light" : "dark");

    const usefulDolbyEMetadata = $derived($metadata !== null ? parseAllDolbyEMetadataFieldsIntoSomethingUseful($metadata.dolbyEFields) : null);
    const sortedDolbyEMetadata = $derived(usefulDolbyEMetadata !== null ? parsedDolbyEMetadataToFormatReadyForTable(usefulDolbyEMetadata) : null);

    function viewLiveXML(){
        fetch('/api/xml')
            .then(res => res.text())
            .then(xml => {
                const blob = new Blob([xml], { type: "application/xml" });
                const url = URL.createObjectURL(blob);
                window.open(url, '_blank');
                URL.revokeObjectURL(url);
            })
            .catch(err => {
                console.error("Error fetching S-ADM XML:", err);
                alert("Failed to fetch S-ADM XML. See console for details.");
            });
    }

    async function saveLiveXML(){
        try {
            const res = await fetch('/api/xml');
            if (res.status !== 200) {
                alert("No live XML available to save.");
                return;
            }
            const xml = await res.text();
            const blob = new Blob([xml], { type: "application/xml;charset=utf-8" });

            if ('showSaveFilePicker' in window) {
                try {
                    const handle = await (window as any).showSaveFilePicker({
                        suggestedName: getSadmXmlFilename ? getSadmXmlFilename() : `live_sadm.xml`,
                        types: [{ description: "XML Files", accept: { "application/xml": [".xml"] } }]
                    });
                    const writable = await handle.createWritable();
                    await writable.write(blob);
                    await writable.close();
                    return;
                } catch (e: any) {
                    if (e.name === 'AbortError') return;
                }
            }

            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = getSadmXmlFilename ? getSadmXmlFilename() : "live_sadm.xml";
            a.click();
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error("Error saving S-ADM XML:", err);
            alert("Failed to save S-ADM XML. See console for details.");
        }
    }
</script>


<div class="sadm-viewer-main" style="overflow: hidden; height: 100%; {style}">
    {#if $metadata === null}
        <div class="center-content fill-parent dp59x-foreground">
            <div class="in-a-row center-content" style="gap: 1em;">
                <div>Loading metadata...</div>
                <Spinner size="1.5rem" />
            </div>
        </div>
    {:else if $metadata.type !== 'sadm'}
        <div style="text-align: center; opacity: 0.7;">
            <h1 style="color: red;">Error</h1>
            <p>Unsupported metadata type: {$metadata.type}</p>
        </div>
    {:else}
        {#snippet renderAdmProfiles()}
            <ul style="margin:0; padding: 0; list-style-type: none;">
                {#each $metadata.admProfiles as profile}
                    <li>{profile}</li>
                {/each}
            </ul>
        {/snippet}
       
        {#snippet allContent()}
            <ScrollingView y>
            <div class="in-a-column">
                <!-- SADM INFO SECTION -->
                <Panel title="S-ADM Info" theme={panelTheme} contentClass="padded">
                    <InfoTable data={{
                        "S-ADM Version": $metadata.sadmVersion,
                        "ADM Version": $metadata.admVersion,
                        // "ADM Profile": $metadata.admProfile,
                        "ADM Profiles": renderAdmProfiles,
                    }}/>
                </Panel>

                <Panel title="Programmes" theme={panelTheme} style="margin-bottom: 1em;">
                    <div class="in-a-row" style="gap: 0.5em; flex-wrap: wrap;">
                    {#if $metadata.presentations.length === 0}
                        <div style="opacity: 0.7;">No programmes found in metadata.</div>
                    {:else}
                        <table style="text-align: center;">
                            <thead>
                                <tr>
                                    <th></th>
                                    <th>Name</th>
                                    <th>Layout</th>
                                    <th>Language</th>
                                    <th>Elements</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each $metadata.presentations as presentation, i (presentation.name, i)}
                                {@const objectIndices = presentation.objectElements ? presentation.objectElements.split(',').map(Number).map(o => o-1) : []}
                                {@const bedIndex = presentation.bedElement ? $metadata.beds.findIndex(b => b.name === presentation.bedElement) : undefined}
                                <tr>
                                    <td><AudioElementIcon label={`P${i+1}`} color='var(--prog-color)' style="font-size: small; margin-left: -0.5em;"/></td>
                                    <td class="text-ellipsis">{presentation.name}</td>
                                    <td>{presentation.targetCfg}</td>
                                    <td>{presentation.presLang}</td>
                                    <td><div class="in-a-row" style="gap: 0.4em;">
                                        {#each $metadata.beds as bed, j (bed.name, j)}
                                        {@const isReferenced = bedIndex === j}
                                            <AudioElementIcon label={`B${j+1}`} color='var(--bed-color)' style="font-size: small; filter: grayscale({isReferenced ? 0 : 100}%); opacity: {isReferenced ? 1 : 0.5}"/>
                                        {/each}
                                        <div></div>
                                        {#each $metadata.objects as obj, k (obj.name, k)}
                                        {@const isReferenced = objectIndices.includes(k)}
                                            <AudioElementIcon label={`O${k+1}`} color='var(--obj-color)' style="font-size: small; filter: grayscale({isReferenced ? 0 : 100}%); opacity: {isReferenced ? 1 : 0.5}"/>
                                        {/each}
                                    </div></td>
                                </tr>
                                {/each}
                            </tbody>
                        </table>
                    {/if}
                    </div>

                </Panel>

                <Panel title="All Audio Objects" theme="none">
                    <ScrollingView x>
                        <div class="in-a-row" style="gap: 0.5em; align-items: stretch; width: min-content; padding: 0.5em; border-radius: 0.3em;">
                            {#each $metadata.beds as bed, i (bed.name, i)}
                            <ADMAudioObjectOrBedView obj={bed} objIndex={i} color="var(--bed-color)" style="flex-grow: 1;" programmeIndices={$metadata.presentations.filter(p=>p.bedElement === bed.name).map(p=>p.index-1)}/>
                            {/each}
                            <div style="width: 0.5em;"></div>
                            {#each $metadata.objects as object, i (object.name, i)}
                            <ADMAudioObjectOrBedView obj={object} objIndex={i} color="var(--obj-color)" programmeIndices={$metadata.presentations.filter(p=>p.objectElements.split(',').map(Number).map(o => o-1).includes(i)).map(p=>p.index-1)}/>
                            {/each}
                        </div>
                    </ScrollingView>
                </Panel>

                {#if $metadata.dolbyEFields.length > 0 && sortedDolbyEMetadata !== null}
                <Panel title="All Dolby E Metadata" theme="none">
                    <DolbyEProgramSpecificMetadataView sortedDolbyEMetadata={sortedDolbyEMetadata} programmeIndex={undefined}/>
                </Panel>
                {/if}
                
            </div>
            </ScrollingView>
        {/snippet}

        {#snippet renderPresentationContent(presentation: AudioPresentation|undefined=undefined)}
            <ScrollingView y>
            {@const objs = presentation ? presentation.objectElements?.split(',').map(Number).map(o => o-1) || [] : []}
            {@const bedIndex = presentation && presentation.bedElement ? [$metadata.beds.findIndex(b => b.name === presentation.bedElement)].filter(b=>b!==undefined) : []}

            <div style="display: flex; flex-wrap: wrap; gap: 1em;">
                
                <div style="flex-grow: 1;">
                    
                    <Panel title="Programme Info" theme={panelTheme} style="margin-bottom: 1em;">
                        {#if presentation === undefined}
                            <div>ERROR</div>
                        {:else}
                            <div style="display: flex; flex-wrap: wrap; column-gap: 2em;">
                                <InfoTable data={{
                                    "Programme Name": presentation.name,
                                    "Name Label Language": presentation.nameLang,
                                }} style="width: fit-content;"/>

                                <InfoTable data={{
                                    "Programme Language": presentation.presLang,
                                    "Target Layout": presentation.targetCfg,
                                }} style="width: fit-content;"/>
                            </div>
                        {/if}

                    </Panel>

                    <Panel title="Audio Objects in {presentation?.name ?? "Programme"}" theme="none">
                        <ScrollingView x>
                        <div class="in-a-row" style="gap: 0.5em; align-items: stretch; width: min-content; max-width: 100%; padding: 0.5em; border-radius: 0.3em;">
                        {#each $metadata.beds as bed, i (bed.name, i)}
                            <ADMAudioObjectOrBedView obj={$metadata.beds[i]} objIndex={i} color="var(--bed-color)" style="flex-grow: 1;" minimized={presentation?.bedElement !== bed.name}/>
                        {/each}
                        <div style="width: 0.5em;"></div>
                        {#each $metadata.objects as obj, i (obj.name, i)}
                            <ADMAudioObjectOrBedView obj={$metadata.objects[i]} objIndex={i} color="var(--obj-color)" style="flex-grow: 1;" minimized={objs.includes(i) === false}/>
                        {/each}
                        </div>
                        </ScrollingView>
                    </Panel>

                </div>

                {#if $metadata.dolbyEFields.length > 0 && sortedDolbyEMetadata !== null}
                    <Panel title="Dolby E Metadata in {presentation?.name ?? "Programme"}" theme="none">
                        {@const presentationIndex = presentation ? presentation.index - 1 : undefined}
                        <DolbyEProgramSpecificMetadataView sortedDolbyEMetadata={sortedDolbyEMetadata} programmeIndex={presentationIndex}/>
                    </Panel>
                {/if}

            </div>
            </ScrollingView>
        {/snippet}


        {#snippet renderProgrammeTab(programmeIndex: number|undefined=undefined)}
            {#if programmeIndex === undefined}
                <div>ERROR</div>
            {:else}
            {@const programme = $metadata.presentations[programmeIndex]}
            <div style="display: flex; flex-direction: column; align-items: center; gap: 0.1em;">
                <div class="in-a-row" style="font-size: larger; gap: 0.5em;" >
                    <AudioElementIcon label={`P${programmeIndex+1}`} color='var(--prog-color)' style="font-size: small; margin-left: -0.5em;"/>
                    <div class="text-ellipsis" style="max-width: 100px;">{programme.name}</div>
                </div>
                <InfoTable data={{
                    "Layout": programme.targetCfg,
                    "Language": programme.presLang,
                }}/>
            </div>
            {/if}
        {/snippet}

        {#snippet renderSadmContentPanelTitle()}
            <div class="in-a-row" style="justify-content: space-between; align-items: center; gap: 1em;">
                <div>S-ADM Content</div>
                <div class="in-a-row" style="gap: 0.4em;">
                    <button class="dp59x-button" style="margin-bottom: 0.2em;" onclick={viewLiveXML}>View XML</button>
                    <button class="dp59x-button" style="margin-bottom: 0.2em;" onclick={saveLiveXML}>Save XML</button>
                </div>
            </div>
        {/snippet}

        <Panel title={renderSadmContentPanelTitle} theme="none">
            <TabsView tabs={[
                {label: "Summary", content: allContent},
                ...Array.from($metadata.presentations, (p, i)=> ({
                    label: renderProgrammeTab,
                    labelArg: i,
                    content: renderPresentationContent,
                    contentArg: p,
                }))
            ]}
            theme={theme} 
            tabPosition="left"
            bind:tabIndex={programmeTabIndex}
            />
        </Panel>
    {/if}
</div>

<style>
    .sadm-viewer-main{
        display: flex;
        flex-direction: column;
        gap: 1em;
        width: 100%;
        box-sizing: border-box;
    }

    table {
        border-collapse: collapse;
    }


    table > * > * > * {
        padding: 0.3em 0.6em;
        border-collapse: collapse;
    }

    table th {
        background-color: var(--dp59x-theme-fg);
        font-weight: normal;
        color: var(--dp59x-theme-on-bg);
        opacity: 0.7;
    }

    tr {
        background-color: var(--dp59x-theme-bg);
    }
</style>