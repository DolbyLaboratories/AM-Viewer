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
    type SourcePanningData = {
        x: number;
        y: number;
        z: number;
        channel: number;
        color: string;
    }

    type Props = {
        objects: SourcePanningData[];
        style?: string;
        size?: string;
        theme?: "light" | "dark";
    }

    let { objects, style, size = "100%", theme = "light"}: Props = $props();
</script>

<style>
    .atmos-cart-pan-view-main {
        width: 100%;
    }
</style>

<div class="atmos-cart-pan-view-main" style={style}>
    <svg width={size} height={size} viewBox="-1.3 -1.3 2.6 2.6" style="background-color: var(--dp59x-theme-{theme === "light" ? "bg" : "fg"}); aspect-ratio: 1 / 1; border-radius: 5%" preserveAspectRatio="xMidYMid meet">
        <g>
            <line x1="-1" y1="-1" x2="1" y2="-1" stroke="#ccc" stroke-width="0.01"/>
            <line x1="-1" y1="1" x2="1" y2="1" stroke="#ccc" stroke-width="0.01"/>
            <line x1="-1" y1="-1" x2="-1" y2="1" stroke="#ccc" stroke-width="0.01"/>
            <line x1="1" y1="-1" x2="1" y2="1" stroke="#ccc" stroke-width="0.01"/>
            <line x1="-1" y1="0" x2="1" y2="0" stroke="#ccc" stroke-width="0.01"/>
            <line x1="0" y1="-1" x2="0" y2="1" stroke="#ccc" stroke-width="0.01"/>
        </g>
        {#each objects as obj}
            <circle cx={obj.x} cy={-obj.y} r={0.2} fill={obj.color} />
            <text x={obj.x} y={-obj.y + 0.05} font-size="0.2" text-anchor="middle" fill="var(--dp59x-theme-on-{theme === "light" ? "bg" : "fg"})">{obj.channel + 1}</text>
        {/each}
    </svg>
</div>