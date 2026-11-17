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
    import CustomOverlayButton from './CustomOverlayButton.svelte';

    type Props = {
        label?: string;
        value: number|undefined;
        digits?: number;
        decimalPlaces?: number; // alternative to digits, will add a decimal point and pad with zeros accordingly
        issue?: { message: string, timestamp: number }; // if provided, will show an error state instead of the value
        onResetIssue?: () => void; // if provided, will be called when the issue overlay is closed
        helpText?: string; // if provided, shows a "?" button next to the label that opens a help overlay
    };

    let { label, value, digits = 7, decimalPlaces=0, issue=undefined, onResetIssue=undefined, helpText=undefined }: Props = $props();

    let valuePadded = $derived((value ?? 0).toFixed(decimalPlaces).padStart(digits, '0'));

    let issueOverlayVisible = $state(false);
    let helpOverlayVisible = $state(false);

    function handleClick() {
        if (issue) {
            issueOverlayVisible = true;
        }
    }
</script>

<div class="number-counter-main">
    {#if label}
    <div class="number-counter-label-row">
        <div class="number-counter-label" class:has-issue={issue}>{label}</div>
        {#if helpText}
        <button
            class="number-counter-help-button"
            title="What is this?"
            aria-label="Help"
            onclick={() => { helpOverlayVisible = true; }}
        >?</button>
        {/if}
    </div>
    {/if}
    <div
        class="number-counter-digit-container"
        class:has-issue={issue}
        onclick={handleClick}
        role="button"
        tabindex="0"
        onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleClick(); } }}
    >
        {#each valuePadded as digit}
            <!-- If numerical, display as digit -->
             {#if digit >= '0' && digit <= '9'}
                <div class="number-counter-digit">{digit}</div>
            {:else}
                <!-- Otherwise, display as is (e.g. decimal point) -->
                <div class="number-counter-non-digit">{digit}</div>
            {/if}
        {/each}
    </div>

    {#if issue}
        <!-- Hidden trigger button: the overlay is opened by clicking the counter above.
             We reuse CustomOverlayButton purely for its overlay UI. -->
        <CustomOverlayButton
            bind:visible={issueOverlayVisible}
            buttonText=""
            buttonStyle="display: none;"
            title={'Frame Continuity Error'}
        >
            <div class="number-counter-issue-message">{issue.message}</div>
            <div class="number-counter-issue-message" style="opacity: 0.5">Received at {new Date(issue.timestamp).toLocaleString()}</div>
            <button class="dp59x-button active centered" onclick={() => { issueOverlayVisible = false; onResetIssue?.(); }} style="padding: 0.5em 1em; margin-top: 1em;">
                Dismiss
            </button>
        </CustomOverlayButton>
    {/if}

    {#if helpText}
        <CustomOverlayButton
            bind:visible={helpOverlayVisible}
            buttonText=""
            buttonStyle="display: none;"
            title={label ? `${label} — Help` : 'Help'}
        >
            <div class="number-counter-help-text">{helpText}</div>
        </CustomOverlayButton>
    {/if}
</div>

<style>
    .number-counter-digit-container {
        display: flex;
        gap: 0.1em;
        justify-content: center;
        align-items: stretch;
        padding: 0.1em;
        background-color: var(--dp59x-theme-bg);
        border: 1px solid var(--dp59x-theme-border);
        border-radius: 4px;
        cursor: pointer;
        width: fit-content;
        margin: 0 auto;
    }

    .number-counter-digit-container > .number-counter-digit {
        flex: 1;
        text-align: center;
        padding: 0.2em;
        background-color: var(--dp59x-theme-fg);
        color: var(--dp59x-theme-on-fg);
        border: 1px solid var(--dp59x-theme-border);
        border-radius: 4px;
        font-family: monospace;
        font-size: larger;
    }

    .number-counter-label-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.3em;
        margin-bottom: 0.2em;
    }

    .number-counter-label {
        font-size: smaller;
        color: var(--dp59x-theme-on-bg);
        text-align: center;
    }

    .number-counter-help-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 1.2em;
        height: 1.2em;
        padding: 0;
        border-radius: 50%;
        border: 1px solid var(--dp59x-theme-border);
        background-color: var(--dp59x-theme-bg);
        color: var(--dp59x-theme-on-bg);
        font-size: smaller;
        line-height: 1;
        cursor: pointer;
    }

    .number-counter-help-button:hover {
        background-color: var(--dp59x-theme-fg);
        color: var(--dp59x-theme-on-fg);
    }

    .number-counter-help-text {
        text-align: center;
        word-break: break-word;
    }

    .number-counter-label.has-issue {
        color: var(--dp59x-theme-error, #b33a3a);
    }

    .number-counter-digit-container.has-issue {
        border-color: var(--dp59x-theme-error, #b33a3a);
    }

    .number-counter-issue-message {
        text-align: center;
        word-break: break-word;
    }
</style>
