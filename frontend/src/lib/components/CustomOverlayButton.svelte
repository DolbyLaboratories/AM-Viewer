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
    type Props = {
        buttonText: string;
        buttonStyle?: string;
        title?: string;
        visible?: boolean;
        children?: any;
    };

    let { buttonText, buttonStyle, title, visible = $bindable<boolean>(false), children }: Props = $props();
</script>

<button class="dp59x-button" style={buttonStyle} title={title} onclick={ev=>{ev.stopPropagation(); ev.preventDefault(); visible = true;}}>
    {buttonText}
</button>

{#if visible}
    <div class="overlay" onclick={(ev)=>{ev.preventDefault(); ev.stopPropagation(); visible = false;}} onkeydown={(ev)=>{if (ev.key === 'Escape') visible = false;}} role="dialog" aria-modal="true" tabindex="0">
        <div class="overlay-container-main" onclick={ev=>{ev.stopPropagation()}} onkeydown={(ev)=>{if (ev.key === 'Escape') visible = false;}} role="dialog" tabindex="-1">
            <div class="overlay-title" style="font-size: larger;">
                <div style="padding: 0.2em 0.5em; opacity: 0.7;">
                    {title}
                </div>
                <button class="dp59x-button red center-content" style="font-size: large; width: 1.5em; height: 1.5em; border-radius: 50%;" onclick={() => visible = false}>&#x2715;</button>
            </div>
            <div class="overlay-content">
                {@render children?.()}
            </div>
        </div>
    </div>
{/if}

<style>
    .overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: #00000088;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .overlay-container-main {
        background-color: var(--dp59x-theme-fg);
        color: var(--dp59x-theme-on-fg);
        border: 1px solid var(--dp59x-theme-border);
        border-radius: 8px;
        width: 90%;
        max-width: 600px;
        max-height: 80%;
        display: grid;
        grid-template-rows: auto 1fr;
        overflow: hidden;
    }

    .overlay-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.3rem;
        border-bottom: 1px solid var(--dp59x-theme-border);
    }

    .overlay-content {
        background-color: var(--dp59x-theme-bg);
        color: var(--dp59x-theme-on-bg);
        padding: 1rem;
        overflow-y: auto;
    }
</style>