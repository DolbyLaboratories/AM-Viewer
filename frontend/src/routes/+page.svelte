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
    import { browser } from "$app/environment";
    import SADMMetadataView from "./SADMMetadataView.svelte";
    import Spinner from "$lib/dp59x-theme/components/Spinner.svelte";
    import { ClientModel } from "$lib/model/client/clientModel";
    import { onDestroy, onMount } from "svelte";
    import dlbLogo from "$lib/assets/dlb_logo.png";
    import DiscoveredServiceButton from "$lib/components/DiscoveredServiceButton.svelte";
    import NumberCounter from "$lib/components/NumberCounter.svelte";
    import RealFpsGraph from "$lib/components/RealFpsGraph.svelte";
    import InfoTable from "$lib/components/InfoTable.svelte";
    import TabsView from "$lib/dp59x-theme/components/TabsView.svelte";
    import Panel from "$lib/dp59x-theme/components/Panel.svelte";
    import type { DiscoveredService } from "$lib/cpp_backend_api/common/cpp_backend_types";
    import CustomOverlayButton from "$lib/components/CustomOverlayButton.svelte";
    import { enhance } from "$app/forms";
    import type { LogRecord } from "$lib/logger/types";
    import LogsView from "./LogsView.svelte";

    type Props = {
        data: {
            logs: LogRecord[];
            showPowerBtn: boolean;
        }
    }

    const {data}: Props = $props();

    let logs = $derived(data.logs);
    const showPowerBtn = $derived(data.showPowerBtn);

    const model = new ClientModel({onNewLogCallback: (msg) => {
        logs = [...logs, msg];
    }});

    let availableInterfaces = model.interfaceNames;
    let selectedInterface = model.selectedInterface;
    let discoveredServices = model.discoveredServices;
    let selectedService = model.selectedService;
    let connectionStatus = model.cppBackendConnectionStatus;
    let sseConnected = model.sseConnected;
    let metadata = model.metadata;
    let metadataFps = model.metadataFps;
    let realFps = model.realFps;
    let realFpsHistory = model.realFpsHistory;
    let fpsSampleIntervalMs = model.fpsSampleIntervalMs;
    let metadataFrameCounter = model.metadataFrameCounter; // to help detect in-place changes of metadata
    let appVersion = model.appVersion;
    let unresolvedIssues = model.unresolvedIssues;


    let metadataViewTabIndex = $state(0);
    let sadmMetadataProgrammeTabIndex = $state(0);

    let uploadSDPOverlayVisible = $state(false);

    $effect(()=>{
        if(metadataViewTabIndex) {} // depend on metadataViewTabIndex to reset sadmMetadataProgrammeTabIndex when switching main tabs
        sadmMetadataProgrammeTabIndex = 0;

    })

    onMount(()=>{
        console.debug("App mounted, setting up model...");
        if(browser){
            model.setup();
        }
    });

    onDestroy(()=>{
        model.close();
    });


    function selectService(service: DiscoveredService) {
        model.setService(service).catch(er=>alert(`Error selecting service: ${er}`)).then(()=>{
            sadmMetadataProgrammeTabIndex = 0; // reset to first tab when selecting a new service
        });
    }

    function resetIssue(key: string) {
        fetch(`?/resetIssue`, { method: "POST", body: new URLSearchParams({key}), headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        }}).then(res=>{
            if(!res.ok){
                alert(`Failed to reset issue: ${res.status} ${res.statusText}`);
            }
        }).catch(er=>{
            alert(`Error resetting issue: ${er}`);
        });
    }
        

    const continuityIssueKey = "MetadataContinuityChecker";
    const fpsIssueKey = "MetadataFpsCalculator";
    const continuityIssue = $derived($unresolvedIssues ? $unresolvedIssues[continuityIssueKey] : undefined);
    const fpsIssue = $derived($unresolvedIssues ? $unresolvedIssues[fpsIssueKey] : undefined);

    let powerMenuOpen = $state(false);

    async function handleShutdown() {
        powerMenuOpen = false;
        await fetch("/api/shutdown", { method: "POST" }).catch(() => {});
        window.close();
    }
</script>

<style>
    .main {
        margin-top: 0.4em;
    }

    .title-banner {
        font-size: xx-large;
        gap: 0.4em;
        height: 100%;
        flex: 1;
        height: fit-content;
        padding: 0.2em;
        opacity: 0.8;
    }

    .power-button-wrap {
        position: fixed;
        top: 0.6rem;
        right: 0.6rem;
        z-index: 1000;
    }

    .power-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        background: none;
        border: 1px solid transparent;
        border-radius: 4px;
        padding: 4px;
        cursor: pointer;
        color: inherit;
        opacity: 0.6;
        transition: opacity 0.15s, border-color 0.15s;
    }
    .power-btn:hover {
        opacity: 1;
        border-color: currentColor;
    }

    .power-dropdown {
        position: absolute;
        top: calc(100% + 2px);
        right: 0;
        background: var(--dp59x-theme-fg);
        color: var(--dp59x-theme-on-bg);
        border: 1px solid var(--dp59x-theme-border);
        border-radius: 4px;
        min-width: 6em;
        z-index: 100;
        box-shadow: 0 4px 12px var(--dp59x-theme-shadow);
        overflow: hidden;
    }

    .power-dropdown-item {
        display: block;
        width: 100%;
        padding: 0.5em 0.9em;
        background: none;
        border: none;
        text-align: left;
        cursor: pointer;
        color: inherit;
        font-size: inherit;
        white-space: nowrap;
    }
    .power-dropdown-item:hover {
        background: var(--dp59x-theme-button);
        color: white;
    }

</style>

{#if showPowerBtn}
<div class="power-button-wrap">
    <button class="power-btn" title="Power" onclick={() => powerMenuOpen = !powerMenuOpen} aria-haspopup="true" aria-expanded={powerMenuOpen}>
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M18.36 6.64A9 9 0 1 1 5.64 6.64"/>
            <line x1="12" y1="2" x2="12" y2="12"/>
        </svg>
    </button>
    {#if powerMenuOpen}
    <div class="power-dropdown" role="menu">
        <button role="menuitem" class="power-dropdown-item" onclick={handleShutdown}>Quit</button>
    </div>
    {/if}
</div>
{/if}

<div class="main grid-base fill-parent" style="grid-template-columns: auto 1fr; grid-template-rows: auto 1fr;">
        <div class="title-banner in-a-row">
            <div style="text-align: left; margin-bottom: 0.1em;">
                <div class="in-a-row" style="gap: 0.3em;">
                    <img src={dlbLogo} alt="DLB Logo" style="height: 1.4em;" />
                    <div>AM Viewer</div>
                </div>
                <div style="opacity: 0.5; font-size: small;">Version {$appVersion}</div>
            </div>
        </div>
        
        <!-- STREAM INFO SECTION -->
        <div id="stream-info-section">
            {#if $sseConnected && $connectionStatus === 'connected'}
            <Panel title="Stream Info" theme="light" contentClass="padded">
                <div class="in-a-row" style="justify-content: space-between;">
                    <div class="in-a-row">
                        {#if $selectedService !== null && $selectedService.name.length > 0}
                        <InfoTable data={{
                            stream_name: $selectedService.name,
                            system: $selectedService.system,
                            }} headerAlign="start"/>
                        <InfoTable data={{
                            address: `${$selectedService.address}:${$selectedService.port}`,
                            codec: $selectedService.codec,
                            }} headerAlign="start"/>
                        {/if}
                    </div>
                    <div class="in-a-row">
                        <NumberCounter label="Frame Counter" value={$metadataFrameCounter} issue={continuityIssue} onResetIssue={() => resetIssue(continuityIssueKey) }/>
                        <NumberCounter label="FPS" value={$metadataFps} digits={5} decimalPlaces={2} issue={fpsIssue} onResetIssue={() => resetIssue(fpsIssueKey) } helpText="This FPS is derived from the timestamps in the RTP packet headers — i.e. the rate the sender intended, computed from the difference between successive RTP timestamps."/>
                        <RealFpsGraph history={$realFpsHistory} current={$realFps} sampleIntervalMs={$fpsSampleIntervalMs} />
                    </div>
                </div>
            </Panel>
            {/if}
        </div>

        {#if !$sseConnected}
            <div class="fill-parent in-a-row center-content" style="gap: 1em; grid-column: span 2;">
                <div>Connecting to server...</div>
                <Spinner size="1.5rem" />
            </div>
        {:else if $connectionStatus !== 'connected'}
            <div class="fill-parent in-a-row center-content" style="gap: 1em; grid-column: span 2;">
                <div>Connecting to backend...</div>
                <Spinner size="1.5rem" />
            </div>
        {:else}
        <!-- SERVICE SELECTION PANEL -->
         <Panel title="Service Selection" theme="light" style="min-width: 18em;">
            <div style="grid-template-rows: auto 1fr auto;" class="fill-parent grid-base">
                <div class="in-a-row" style="gap: 0.5em; justify-content: end;">
                    <div>Interface:</div>
                    <select class="dp59x-select" class:highlighted={$selectedInterface === null} value={$selectedInterface} onchange={(e) => model.setInterface((e.target as HTMLSelectElement).value)}>
                        <option value="" disabled selected>None</option>
                        {#each $availableInterfaces as iface}
                            <option value={iface}>{iface}</option>
                        {/each}
                    </select>
                </div>
                <div class="fill-parent scrolling dp59x-background" class:highlighted={$selectedInterface !== null && ($selectedService === null || $selectedService.name.length === 0)} style="display: flex; flex-direction: column; gap: 0.4em; align-content: stretch; padding: 0.4em; border-radius: 0.3em;">
                    {#if $selectedInterface === null}
                        <div style="height: 100%; padding: 1em;" class="center-content">
                            <div style="text-align: center;">Select an interface<br/>to start listening</div>
                        </div>
                    {:else if $discoveredServices.length === 0}
                        <div style="height: 100%; gap: 1em;" class="center-content fill-parent">
                            <div>Listening on {$selectedInterface}...</div>
                            <Spinner size="2.5rem" />
                        </div>
                    {:else}
                    {#each $discoveredServices as service}
                        {@const isSelected = service.name === $selectedService?.name && service.port === $selectedService?.port && service.address === $selectedService?.address}
                        <DiscoveredServiceButton {service} onSelect={() => selectService(service)} highlighted={isSelected} />
                    {/each}
                    {/if}
                </div>
                <div>
                    {#if $selectedInterface !== null}
                    <CustomOverlayButton buttonText="Upload SDP" title="Upload SDP" buttonStyle="width: 100%;" bind:visible={uploadSDPOverlayVisible}>
                        <form id="uploadSDPForm" class="in-a-column" action="?/selectServiceBySDP" method="POST" use:enhance={()=>{
                            console.log("Enhancing form...");
                            return ({result})=>{
                                switch(result.type){
                                    case "success":
                                        console.log("Service selected by SDP successfully");
                                        uploadSDPOverlayVisible = false;
                                        break;
                                    case "error":
                                        alert(`Error selecting service by SDP: ${result.error}`);
                                        break;
                                    case "failure":
                                        alert(`Failed to select service by SDP: ${result.status} ${result.data?.error}`);
                                        break;
                                    default:
                                        alert("Unexpected result from form submission");
                                        break;
                                }
                            }
                        }}>
                            <textarea name="sdpText" required style="width: 100%; height: 300px; font-family: monospace; font-size: small;" placeholder="Paste SDP text here"></textarea>
                            <button class="dp59x-button active" type="submit" form="uploadSDPForm" style="width: 100%;">Submit</button>
                        </form>
                    </CustomOverlayButton>
                    {/if}
                </div>
            </div>
        </Panel>

        <div style="width: 100%; height: 100%; overflow: hidden;">
            <!-- METADATA VIEWER PANEL -->
                {#snippet sadmMetadataTab()}
                    {#if $metadata !== null}
                        {#if $metadata.type === 'sadm'}
                            <SADMMetadataView {metadata} 
                            theme="dark" 
                            style="min-height: 100%;"
                            bind:programmeTabIndex={sadmMetadataProgrammeTabIndex}
                            getSadmXmlFilename={() => `${$selectedService?.name ?? "frame"}-${$metadataFrameCounter}.sadm.xml`}
                            />
                        {:else}
                            <div style="text-align: center; opacity: 0.7;">
                                <h1 style="color: red;">Error</h1>
                                <p>Unsupported metadata type: {$metadata.type}</p>
                            </div>
                        {/if}
                    {:else if $selectedService !== null && $selectedService.name.length > 0}
                        <!-- Waiting for first metadata frame -->
                        <div class="fill-parent center-content">
                            <Spinner size="2.5rem" />
                        </div>
                    {:else}
                        <!-- No service selected -->
                        <div class="fill-parent center-content">
                            <div style="opacity: 0.5;">Select a service to view metadata</div>
                        </div>
                    {/if}
                {/snippet}

                {#snippet logsTab()}
                    <LogsView logs={logs} onClear={() => { logs = []; }} />
                {/snippet}

                <TabsView tabs={[
                    {
                        label: "Metadata",
                        content: sadmMetadataTab
                    },
                    {
                        label: "Logs",
                        content: logsTab
                    }
                ]}
                theme="light" 
                forceShowTabs
                contentStyle="padding: 1em;"
                style="min-height: 100%;"
                bind:tabIndex={metadataViewTabIndex}
                />
        </div>
            
    {/if}
</div>