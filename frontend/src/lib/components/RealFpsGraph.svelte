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
 Small clickable real-fps sparkline. Clicking it opens an overlay with the
 larger annotated FpsGraphView. "Real" fps is measured from the wall-clock
 arrival time of parsed metadata frames (as opposed to the RTP-timestamp fps
 shown by the plain FPS counter).
-->
<script lang="ts">
    import CustomOverlayButton from "./CustomOverlayButton.svelte";
    import Sparkline from "./Sparkline.svelte";
    import FpsGraphView from "./FpsGraphView.svelte";

    type Props = {
        label?: string;
        history: number[];
        current: number;
        sampleIntervalMs?: number;
    };

    let { label = "Real FPS", history, current, sampleIntervalMs = 0 }: Props = $props();

    let overlayVisible = $state(false);

    function open() {
        overlayVisible = true;
    }
</script>

<div class="real-fps-graph">
    <div class="real-fps-label">{label}</div>
    <div
        class="real-fps-clickable"
        onclick={open}
        role="button"
        tabindex="0"
        title="Click to view the real FPS graph"
        onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } }}
    >
        <Sparkline data={history} width={80} height={26} min={0} />
        <div class="real-fps-value">{current.toFixed(1)}</div>
    </div>

    <CustomOverlayButton
        bind:visible={overlayVisible}
        buttonText=""
        buttonStyle="display: none;"
        title={'Real FPS'}
    >
        <FpsGraphView data={history} {sampleIntervalMs} />
    </CustomOverlayButton>
</div>

<style>
    .real-fps-graph {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .real-fps-label {
        font-size: smaller;
        color: var(--dp59x-theme-on-bg);
        text-align: center;
        margin-bottom: 0.2em;
    }

    .real-fps-clickable {
        display: flex;
        align-items: center;
        gap: 0.4em;
        padding: 0.1em 0.4em;
        background-color: var(--dp59x-theme-bg);
        border: 1px solid var(--dp59x-theme-border);
        border-radius: 4px;
        cursor: pointer;
    }

    .real-fps-value {
        font-family: monospace;
        font-size: larger;
        min-width: 4ch;
        text-align: right;
    }
</style>
