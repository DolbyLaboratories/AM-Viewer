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
    import type { Snippet } from "svelte";

    type Props = {
        title?: string|Snippet;
        theme?: "light" | "dark" | "none";
        children?: Snippet;
        contentClass?: string;
        contentStyle?: string;
        style?: string;
        padded?: boolean;
    }

    const { title, 
        theme = 'light', 
        children, 
        style, 
        contentClass, 
        contentStyle,
        padded = false
    }: Props = $props();


    const panelClass = $derived.by(()=>{switch(theme) {
        case 'light': return "dp59x-foreground";
        case 'dark': return "dp59x-background";
        case 'none': return "";
    }});
</script>


<div class="grid-base dp59x-panel" style="{style}; grid-template-rows: {title ? 'auto 1fr' : '1fr'}; gap: 0.2em;">
    {#if title}
    {#if typeof title === 'string'}
    <div style="opacity: 0.7;">
        {title}
    </div>
    {:else}
    {@render title?.()}
    {/if}
    {/if}
    <div class="dp59x-panel-content {panelClass} rounded fill-parent {contentClass}" class:padded={padded} style="{contentStyle}">
        {@render children?.()}
    </div>
</div>

<style>
    .dp59x-panel {
        max-height: 100%;
    }
</style>