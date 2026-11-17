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

<script lang="ts" generics="T, T2">
    import type { Snippet } from "svelte";

    type Props = {
        tabs: { label: string|Snippet<[T2?]>; content: Snippet<[T?]>; contentArg?: T; labelArg?: T2 }[];
        contentStyle?: string;
        contentClass?: string;
        buttonClass?: string;
        buttonStyle?: string;
        style?: string;
        forceShowTabs?: boolean; // if true, will show the tab buttons even if there's only one tab
        tabPosition?: "top" | "left";
        theme?: "light" | "dark" | "none";
        tabIndex?: number; // if provided, will control the active tab (0-based index)
    }

    let { tabs, contentStyle, contentClass, buttonStyle, buttonClass, theme = "none", forceShowTabs = false, tabPosition = "top", style, tabIndex = $bindable(0)}: Props = $props();


    const panelClass = $derived.by(()=>{switch(theme) {
        case 'light': return "dp59x-foreground";
        case 'dark': return "dp59x-background";
        default: return "";
    }});
</script>

<div class="grid-base tabs-view" style="grid-template-{tabPosition === "top" ? "rows" : "columns"}: {tabs.length > 1 || forceShowTabs ? 'auto 1fr' : '1fr'}; gap: 0; {style}">
    {#if tabs.length > 1 || forceShowTabs}
    <div class="buttons-{tabPosition=="top" ? "row" : "column"}">
        {#each tabs as tab, index}
            <button onclick={() => tabIndex = index} class:active={tabIndex === index} class="{buttonClass}" style="border: 2px solid transparent; {buttonStyle}">
                {#if typeof tab.label === 'string'}
                    {tab.label}
                {:else}
                    {@render tab.label(tab.labelArg)}
                {/if}
            </button>
        {/each}
    </div>
    {/if}
    <div class="{panelClass} padded rounded {contentClass}" style="max-height: 100%; border-top-left-radius: 0; {contentStyle}; ">
        {#if tabs[tabIndex]}
        {@const tab = tabs[tabIndex]}
        {@render tab.content(tab.contentArg)}
        {/if}
    </div>
</div>

<style>
    .tabs-view {
        height: 100%; 
        overflow: hidden; 
    }

    .buttons-row {
        display: flex;
        gap: 0.5em;
        flex-wrap: wrap;
    }

    .buttons-row button {
        background-color: var(--dp59x-theme-button);
        color: var(--dp59x-theme-on-button);
        border: none;
        padding: 0.5em 1em;
        cursor: pointer;
        border-radius: 0.3em 0.3em 0 0;
        opacity: 0.6;
    }

    .buttons-row button.active {
        opacity: 1;
        border-bottom: 2px solid var(--dp59x-theme-button-active) !important;
        color: var(--dp59x-theme-button-text);
    }

    .buttons-column {
        display: flex;
        flex-direction: column;
        gap: 0.1em;
    }

    .buttons-column button {
        border: none;
        padding: 0.5em 1em;
        cursor: pointer;
        background-color: var(--dp59x-theme-button);
        color: var(--dp59x-theme-text);
        opacity: 0.6;
    }

    .buttons-column button.active {
        opacity: 1;
        border-right: 2px solid var(--dp59x-theme-button-active) !important;
        background-color: var(--dp59x-theme-button);
        color: var(--dp59x-theme-text);
    }
</style>