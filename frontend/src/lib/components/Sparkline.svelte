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

<!--
 Minimal, axis-less line chart ("sparkline") for a series of numbers.
 The line is scaled to the min/max of the supplied data so trends are visible
 even when the absolute range is small. Stroke width is kept constant regardless
 of the SVG's rendered size via vector-effect="non-scaling-stroke".
-->
<script lang="ts">
    type Props = {
        data: number[];
        width?: number;
        height?: number;
        color?: string;
        strokeWidth?: number;
        fill?: boolean;
        min?: number; // fixed lower bound; defaults to the data minimum
        max?: number; // fixed upper bound; defaults to the data maximum
    };

    let {
        data,
        width = 120,
        height = 32,
        color = "var(--dp59x-theme-button-active)",
        strokeWidth = 1.5,
        fill = true,
        min: minProp = undefined,
        max: maxProp = undefined,
    }: Props = $props();

    const pad = 2;

    let geom = $derived.by(() => {
        const n = data.length;
        if (n === 0) return { line: "", area: "" };
        const min = minProp ?? Math.min(...data);
        const max = maxProp ?? Math.max(...data);
        const range = max - min || 1;
        const innerW = width - pad * 2;
        const innerH = height - pad * 2;
        const x = (i: number) => pad + (n === 1 ? innerW / 2 : (i / (n - 1)) * innerW);
        const y = (v: number) => pad + innerH - ((v - min) / range) * innerH;
        const pts = data.map((v, i) => `${x(i).toFixed(2)},${y(v).toFixed(2)}`);
        const line = "M" + pts.join(" L");
        const area =
            `M${x(0).toFixed(2)},${(height - pad).toFixed(2)} L` +
            pts.join(" L") +
            ` L${x(n - 1).toFixed(2)},${(height - pad).toFixed(2)} Z`;
        return { line, area };
    });
</script>

<svg
    class="sparkline"
    viewBox={`0 0 ${width} ${height}`}
    {width}
    {height}
    preserveAspectRatio="none"
    role="img"
    aria-label="trend graph"
>
    {#if data.length > 0}
        {#if fill}
            <path d={geom.area} fill={color} fill-opacity="0.15" stroke="none" />
        {/if}
        <path
            d={geom.line}
            fill="none"
            stroke={color}
            stroke-width={strokeWidth}
            vector-effect="non-scaling-stroke"
            stroke-linejoin="round"
            stroke-linecap="round"
        />
    {/if}
</svg>

<style>
    .sparkline {
        display: block;
    }
</style>
