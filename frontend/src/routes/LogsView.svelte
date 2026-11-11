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
    import { LogLevel, type LogRecord } from "$lib/logger/types";
    import { logLevelToString } from "$lib/logger/util";
    import { SvelteSet } from "svelte/reactivity";

    type Props = {
        logs: LogRecord[];
        onClear?: () => void;
    }

    const {logs, onClear}: Props = $props();

    // Ordered list of all log levels, used to render the level checkboxes.
    const allLevels = Object.values(LogLevel).sort((a, b) => a - b);

    let availableTags = $derived(logs.map(l=>l.tag).filter((v, i, a) => a.indexOf(v) === i));

    // We track what is *hidden* rather than what is shown, so that levels/tags
    // default to visible and any newly-appearing tag is shown automatically.
    let hiddenLevels = new SvelteSet<number>();
    let hiddenTags = new SvelteSet<string>();

    let filterOpen = $state(false);

    // Number of active filters, used to badge the Filter button.
    const activeFilterCount = $derived(hiddenLevels.size + hiddenTags.size);

    function toggle<T>(set: SvelteSet<T>, value: T) {
        if (set.has(value)) set.delete(value);
        else set.add(value);
    }

    function resetAll() {
        hiddenLevels.clear();
        hiddenTags.clear();
    }

    let confirmClearOpen = $state(false);

    // Close a popup when clicking anywhere outside its container. `close` is
    // called on an outside pointer-down while the popup is open.
    function clickOutside(node: HTMLElement, params: { isOpen: () => boolean; close: () => void }) {
        function onPointerDown(e: PointerEvent) {
            if (params.isOpen() && !node.contains(e.target as Node)) {
                params.close();
            }
        }
        document.addEventListener("pointerdown", onPointerDown, true);
        return {
            destroy() {
                document.removeEventListener("pointerdown", onPointerDown, true);
            }
        };
    }

    // Download the *complete* server-side log history — including internal logs
    // that are never streamed to the client. The endpoint reads the on-disk
    // files and returns a formatted .log attachment.
    function downloadLogs() {
        const a = document.createElement("a");
        a.href = "/api/logs/download";
        // The `download` attribute makes the browser fetch this as a download
        // instead of navigating the top-level document to it. Without it the
        // navigation attempt aborts the page's in-flight requests — including
        // the SSE stream — until the download commits or the tab regains focus.
        // The server's Content-Disposition still supplies the actual filename.
        a.download = "";
        document.body.appendChild(a);
        a.click();
        a.remove();
    }

    function clearLogs() {
        confirmClearOpen = false;
        onClear?.();
    }

    const filteredLogs = $derived(
        logs.filter(l => !hiddenLevels.has(l.level) && !hiddenTags.has(l.tag))
    );

    let scrollEl = $state<HTMLDivElement>();
    let stick = $state(true); // whether the view is pinned to the bottom

    function onScroll() {
        if (!scrollEl) return;
        // Within a few px of the bottom counts as "at the bottom"
        stick = scrollEl.scrollHeight - scrollEl.scrollTop - scrollEl.clientHeight <= 4;
    }

    function goLive() {
        stick = true;
        if (scrollEl) scrollEl.scrollTop = scrollEl.scrollHeight;
    }

    $effect(() => {
        filteredLogs.length; // re-run when the rendered rows change
        if (stick && scrollEl) {
            scrollEl.scrollTop = scrollEl.scrollHeight;
        }
    });
</script>

<style>
    th, td {
        padding: 0.2em 0.5em;
    }

    tbody td {
        vertical-align: top;
    }
    

    thead th {
        position: sticky;
        top: 0;
        background: var(--dp59x-theme-bg);
        z-index: 1;
    }

    .error>.level, .error>.message {
        color: var(--dp59x-theme-error);
    }

    .warn>.level, .warn>.message {
        color: var(--dp59x-theme-warning);
    }

    .info>.level {
        color: var(--dp59x-theme-info);
    }

    .debug>.level {
        color: var(--dp59x-theme-debug);
    }

    .timestamp {
        white-space: nowrap;
    }

    .level {
        text-align: center;
    }

    .live-button {
        display: inline-flex;
        align-items: center;
        gap: 0.5em;
        background-color: var(--dp59x-theme-button);
        color: var(--dp59x-theme-on-button);
        border: none;
        padding: 0.3em 0.8em;
        border-radius: 0.3em;
        cursor: pointer;
        opacity: 0.6;
    }

    .live-button:hover {
        opacity: 0.85;
    }

    .live-button.active {
        opacity: 1;
        background-color: var(--dp59x-theme-button-active);
        color: var(--dp59x-theme-on-button-active);
    }

    .live-dot {
        width: 0.55em;
        height: 0.55em;
        border-radius: 50%;
        background-color: currentColor;
        opacity: 0.5;
    }

    .live-button.active .live-dot {
        opacity: 1;
        animation: live-pulse 1.5s ease-in-out infinite;
    }

    @keyframes live-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    .logs-body {
        display: flex;
        flex-direction: column;
        height: 100%;
        min-height: 0;
        gap: 0.3em;
    }

    .filter {
        position: relative;
    }

    .filter-button, .bar-button {
        display: inline-flex;
        align-items: center;
        gap: 0.45em;
    }

    .filter-icon, .button-icon {
        width: 1em;
        height: 1em;
    }

    .clear {
        position: relative;
    }

    .clear-popup {
        position: absolute;
        top: calc(100% + 0.4em);
        left: 0;
        z-index: 10;
        display: flex;
        flex-direction: column;
        gap: 0.6em;
        padding: 0.8em 1em;
        border-radius: 0.3em;
        border: 1px solid var(--dp59x-theme-border);
        box-shadow: 0 0.4em 1em var(--dp59x-theme-shadow);
        white-space: nowrap;
    }

    .clear-actions {
        display: flex;
        justify-content: flex-end;
        gap: 0.5em;
    }

    .filter-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 1.4em;
        height: 1.4em;
        padding: 0 0.35em;
        border-radius: 0.7em;
        background: var(--dp59x-theme-bg-root);
        color: var(--dp59x-theme-on-button-active);
        font-size: 0.8em;
    }

    .filter-popup {
        position: absolute;
        top: calc(100% + 0.4em);
        left: 0;
        z-index: 10;
        display: grid;
        grid-template-columns: repeat(2, minmax(8em, auto));
        column-gap: 1.5em;
        row-gap: 0.35em;
        align-items: start;
        padding: 0.8em 1em;
        border-radius: 0.3em;
        border: 1px solid var(--dp59x-theme-border);
        box-shadow: 0 0.4em 1em var(--dp59x-theme-shadow);
    }

    .filter-popup section {
        display: flex;
        flex-direction: column;
        gap: 0.35em;
    }

    .filter-header {
        margin-bottom: 0.35em;
        font-weight: bold;
    }

    .filter-footer {
        grid-column: 1 / -1;
        display: flex;
        justify-content: flex-end;
        margin-top: 0.6em;
    }

    .filter-option {
        display: flex;
        align-items: center;
        gap: 0.5em;
        cursor: pointer;
        white-space: nowrap;
    }

    .filter-option input {
        cursor: pointer;
    }

    .filter-empty {
        opacity: 0.5;
        font-style: italic;
    }

</style>



{#snippet toolbar()}
    <div class="in-a-row" style="align-items: center; gap: 0.5em; justify-content: flex-start; flex-wrap: nowrap; overflow: visible;">
        <div class="filter" use:clickOutside={{ isOpen: () => filterOpen, close: () => (filterOpen = false) }}>
            <button
                class="dp59x-button filter-button"
                class:active={activeFilterCount > 0}
                onclick={() => (filterOpen = !filterOpen)}
            >
                <svg class="filter-icon" viewBox="0 0 16 16" aria-hidden="true">
                    <path
                        d="M1.5 2.5h13l-5 6v4.5l-3 1.5v-6z"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.3"
                        stroke-linejoin="round"
                    />
                </svg>
                Filter{#if activeFilterCount > 0}<span class="filter-badge">{activeFilterCount}</span>{/if}
            </button>

            {#if filterOpen}
                <div class="filter-popup dp59x-background">
                    <div class="filter-header">Log Level</div>
                    <div class="filter-header">Tag</div>

                    <section>
                        {#each allLevels as level}
                            <label class="filter-option">
                                <input
                                    type="checkbox"
                                    checked={!hiddenLevels.has(level)}
                                    onchange={() => toggle(hiddenLevels, level)}
                                />
                                {logLevelToString(level)}
                            </label>
                        {/each}
                    </section>

                    <section>
                        {#if availableTags.length === 0}
                            <div class="filter-empty">No tags</div>
                        {/if}
                        {#each availableTags as tag}
                            <label class="filter-option">
                                <input
                                    type="checkbox"
                                    checked={!hiddenTags.has(tag)}
                                    onchange={() => toggle(hiddenTags, tag)}
                                />
                                {tag}
                            </label>
                        {/each}
                    </section>

                    <div class="filter-footer">
                        <button class="dp59x-button" onclick={resetAll}>Reset all</button>
                    </div>
                </div>
            {/if}
        </div>

        <button class="dp59x-button bar-button" title="Download logs" onclick={downloadLogs}>
            <svg class="button-icon" viewBox="0 0 16 16" aria-hidden="true">
                <path
                    d="M8 1.5v8m0 0 3-3m-3 3-3-3M2.5 12.5h11"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                />
            </svg>
            Download
        </button>

        <div class="clear" use:clickOutside={{ isOpen: () => confirmClearOpen, close: () => (confirmClearOpen = false) }}>
            <button
                class="dp59x-button bar-button"
                title="Clear all logs"
                onclick={() => (confirmClearOpen = !confirmClearOpen)}
            >
                <svg class="button-icon" viewBox="0 0 16 16" aria-hidden="true">
                    <path
                        d="M2.5 4h11M5.5 4V2.5h5V4M4 4l.7 9.5h6.6L12 4"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                </svg>
                Clear
            </button>

            {#if confirmClearOpen}
                <div class="clear-popup dp59x-background">
                    <div class="clear-message">Clear all logs?</div>
                    <div class="clear-actions">
                        <button class="dp59x-button" onclick={() => (confirmClearOpen = false)}>Cancel</button>
                        <button class="dp59x-button red" onclick={clearLogs}>Clear</button>
                    </div>
                </div>
            {/if}
        </div>

        <button class="live-button" class:active={stick} onclick={goLive}>
            <span class="live-dot"></span>
            Live
        </button>
    </div>
{/snippet}

<div class="logs-body">
    {@render toolbar()}
    <Panel theme="dark" padded style="flex: 1; min-height: 0;">
        <ScrollingView y startAtBottom bind:element={scrollEl} onscroll={onScroll}>
        <table style="width: 100%; border-collapse: separate; border-spacing: 0;">
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Level</th>
                    <th>Tag</th>
                    <th style="text-align: left; width: 100%;">Message</th>
                </tr>
            </thead>
            <tbody>
                {#each filteredLogs as log, i (i)}
                    {@const logLevelStr = logLevelToString(log.level).toLowerCase()}
                    <tr class="{logLevelStr}" style="font-family: monospace;">
                        <td style="text-align: left; opacity: 0.7;" class="timestamp">{new Date(log.timestamp).toLocaleString()}</td>
                        <td style="text-align: center; opacity: 0.7;" class="level">{logLevelStr}</td>
                        <td style="text-align: left; white-space: nowrap; opacity: 0.7;" class="message">{log.tag}</td>
                        <td style="text-align: left; white-space: pre-wrap;" class="message">{log.message}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
        </ScrollingView>
    </Panel>
</div>

