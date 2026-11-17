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
 Larger, annotated real-fps chart shown in the overlay. Renders a 0-based
 y-axis with gridlines, time-ago x-axis ticks, the fps line/area, a dashed
 average line and a min/max/avg/current stat readout.
-->
<script lang="ts">
    type Props = {
        data: number[];
        sampleIntervalMs?: number;
        lineColor?: string;
    };

    let {
        data,
        sampleIntervalMs = 0,
        lineColor = "var(--dp59x-theme-button-active)",
    }: Props = $props();

    // Window over which the displayed average is computed. The average is
    // recency-weighted (newer samples count more) across samples in this window.
    const WEIGHTED_AVG_WINDOW_MS = 10000;

    const VB_W = 640;
    const VB_H = 300;
    const M = { top: 16, right: 16, bottom: 30, left: 48 };
    const plotW = VB_W - M.left - M.right;
    const plotH = VB_H - M.top - M.bottom;

    function niceCeil(v: number): number {
        if (v <= 0) return 1;
        const mag = Math.pow(10, Math.floor(Math.log10(v)));
        const norm = v / mag;
        let nice: number;
        if (norm <= 1) nice = 1;
        else if (norm <= 2) nice = 2;
        else if (norm <= 5) nice = 5;
        else nice = 10;
        return nice * mag;
    }

    let chart = $derived.by(() => {
        const finite = data.filter((v) => Number.isFinite(v));
        const n = finite.length;
        const dataMax = n ? Math.max(...finite) : 0;
        const dataMin = n ? Math.min(...finite) : 0;
        const current = n ? finite[n - 1] : 0;

        // Recency-weighted average over the last WEIGHTED_AVG_WINDOW_MS.
        // Falls back to the whole series when the sample interval is unknown.
        const windowCount =
            sampleIntervalMs > 0
                ? Math.min(n, Math.max(1, Math.round(WEIGHTED_AVG_WINDOW_MS / sampleIntervalMs)))
                : n;
        // Keep each sample's recency weight (oldest in window = 1, newest = windowCount)
        // alongside its value so weights survive outlier filtering.
        const windowSamples = finite
            .slice(n - windowCount)
            .map((v, i) => ({ v, w: i + 1 }));

        // Reject outliers beyond 2σ before averaging.
        let kept = windowSamples;
        if (windowSamples.length > 1) {
            const mean =
                windowSamples.reduce((a, s) => a + s.v, 0) / windowSamples.length;
            const stdDev = Math.sqrt(
                windowSamples.reduce((a, s) => a + (s.v - mean) ** 2, 0) /
                    windowSamples.length
            );
            const threshold = stdDev * 2;
            const filtered = windowSamples.filter(
                (s) => Math.abs(s.v - mean) <= threshold
            );
            if (filtered.length > 0) kept = filtered; // keep unfiltered if all rejected (e.g. σ=0)
        }

        let weightedSum = 0;
        let weightTotal = 0;
        for (const { v, w } of kept) {
            weightedSum += v * w;
            weightTotal += w;
        }
        const avg = weightTotal > 0 ? weightedSum / weightTotal : 0;

        const yMax = niceCeil(Math.max(dataMax, 1) * 1.1);
        const yMin = 0;

        const xForIndex = (i: number) =>
            M.left + (n <= 1 ? plotW : (i / (n - 1)) * plotW);
        const yForVal = (v: number) =>
            M.top + plotH - ((v - yMin) / (yMax - yMin)) * plotH;

        let line = "";
        let area = "";
        if (n > 0) {
            const pts = finite.map(
                (v, i) => `${xForIndex(i).toFixed(2)},${yForVal(v).toFixed(2)}`
            );
            line = "M" + pts.join(" L");
            area =
                `M${xForIndex(0).toFixed(2)},${(M.top + plotH).toFixed(2)} L` +
                pts.join(" L") +
                ` L${xForIndex(n - 1).toFixed(2)},${(M.top + plotH).toFixed(2)} Z`;
        }

        const yTickCount = 4;
        const yTicks: { val: number; y: number }[] = [];
        for (let i = 0; i <= yTickCount; i++) {
            const val = yMin + (i / yTickCount) * (yMax - yMin);
            yTicks.push({ val, y: yForVal(val) });
        }

        const xTicks: { x: number; label: string }[] = [];
        if (sampleIntervalMs > 0 && n > 1) {
            const xTickCount = Math.min(6, n - 1);
            for (let i = 0; i <= xTickCount; i++) {
                const idx = Math.round((i / xTickCount) * (n - 1));
                const secondsAgo = ((n - 1 - idx) * sampleIntervalMs) / 1000;
                xTicks.push({
                    x: xForIndex(idx),
                    label: secondsAgo === 0 ? "now" : `-${secondsAgo.toFixed(0)}s`,
                });
            }
        }

        return {
            n,
            dataMin,
            dataMax,
            avg,
            current,
            yMax,
            line,
            area,
            yTicks,
            xTicks,
            avgY: yForVal(avg),
            baseY: M.top + plotH,
            leftX: M.left,
            rightX: M.left + plotW,
        };
    });
</script>

<div class="fps-graph-view">
    <div class="fps-stats">
        <div class="fps-stat"><span class="k">Current</span><span class="v">{chart.current.toFixed(2)}</span></div>
        <div class="fps-stat"><span class="k">Avg (10s)</span><span class="v">{chart.avg.toFixed(2)}</span></div>
        <div class="fps-stat"><span class="k">Min</span><span class="v">{chart.dataMin.toFixed(2)}</span></div>
        <div class="fps-stat"><span class="k">Max</span><span class="v">{chart.dataMax.toFixed(2)}</span></div>
    </div>

    {#if chart.n === 0}
        <div class="fps-empty">No frames received yet.</div>
    {:else}
        <svg class="fps-svg" viewBox={`0 0 ${VB_W} ${VB_H}`} role="img" aria-label="Real FPS over time">
            <!-- y gridlines + labels -->
            {#each chart.yTicks as tick}
                <line
                    x1={chart.leftX}
                    y1={tick.y}
                    x2={chart.rightX}
                    y2={tick.y}
                    class="grid-line"
                />
                <text x={chart.leftX - 6} y={tick.y} class="axis-label y-label">{tick.val.toFixed(0)}</text>
            {/each}

            <!-- x ticks -->
            {#each chart.xTicks as tick}
                <line x1={tick.x} y1={chart.baseY} x2={tick.x} y2={chart.baseY + 4} class="grid-line" />
                <text x={tick.x} y={chart.baseY + 16} class="axis-label x-label">{tick.label}</text>
            {/each}

            <!-- area + line -->
            <path d={chart.area} fill={lineColor} fill-opacity="0.12" stroke="none" />
            <path
                d={chart.line}
                fill="none"
                stroke={lineColor}
                stroke-width="1.5"
                vector-effect="non-scaling-stroke"
                stroke-linejoin="round"
                stroke-linecap="round"
            />

            <!-- average line -->
            <line
                x1={chart.leftX}
                y1={chart.avgY}
                x2={chart.rightX}
                y2={chart.avgY}
                class="avg-line"
            />
            <text x={chart.rightX - 2} y={chart.avgY - 4} class="axis-label avg-label">avg {chart.avg.toFixed(1)}</text>
        </svg>
    {/if}
</div>

<style>
    .fps-graph-view {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        width: 100%;
    }

    .fps-stats {
        display: flex;
        gap: 1.5rem;
        justify-content: center;
        flex-wrap: wrap;
    }

    .fps-stat {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .fps-stat .k {
        font-size: smaller;
        opacity: 0.6;
    }

    .fps-stat .v {
        font-family: monospace;
        font-size: larger;
    }

    .fps-svg {
        width: 100%;
        height: auto;
        display: block;
    }

    .grid-line {
        stroke: var(--dp59x-theme-border);
        stroke-width: 1;
        opacity: 0.5;
    }

    .avg-line {
        stroke: var(--dp59x-theme-on-bg);
        stroke-width: 1;
        stroke-dasharray: 4 3;
        opacity: 0.6;
    }

    .axis-label {
        fill: var(--dp59x-theme-on-bg);
        font-size: 11px;
        opacity: 0.75;
    }

    .y-label {
        text-anchor: end;
        dominant-baseline: middle;
    }

    .x-label {
        text-anchor: middle;
    }

    .avg-label {
        text-anchor: end;
        opacity: 0.6;
    }

    .fps-empty {
        text-align: center;
        opacity: 0.6;
        padding: 2rem 0;
    }
</style>
