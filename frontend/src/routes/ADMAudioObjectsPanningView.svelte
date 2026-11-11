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
    This view is responsible for displaying the audio objects and beds in a SADM metadata file.
    It uses the AtmosCartPannerView to display the objects and beds in a 3D space.
-->

<script lang="ts">
    import type { AudioBed, AudioObject } from "$lib/cpp_backend_api/common/cpp_backend_types";
    import AtmosCartPannerView from "./AtmosCartPannerView.svelte";
    

    let {
        objects, 
        beds, 
        objColor = "#3498db", 
        bedColor = "#e67e22",
        size,
        theme = "light"
    }: {
        objects?: AudioObject[],
        beds?: AudioBed[],
        objColor?: string,
        bedColor?: string,
        size?: string,
        theme?: "light" | "dark"
    } = $props();

    function bedConfigToObjectViewPositions(bed: AudioBed): ({x: number, y: number, z: number, channel: number, color: string}[] | null){

        const CHANNEL_TO_OBJ: Record<string, {x: number, y: number, z: number}> = {
            "L": {x: -1, y: 1, z: 0},
            "R": {x: 1, y: 1, z: 0},
            "C": {x: 0, y: 1, z: 0},
            "LFE": {x: -1, y: 1, z: -1},
            "LS": {x: -1, y: -1, z: 0},
            "RS": {x: 1, y: -1, z: 0},
            "LSS": {x: -1, y: 0, z: 0},
            "RSS": {x: 1, y: 0, z: 0},
            "LTF": {x: -1, y: 1, z: 1},
            "RTF": {x: 1, y: 1, z: 1},
            "LCF": {x: 0, y: 1, z: 1},
            "LFE2": {x: 0, y: 0, z: -1},
            "LTR": {x: -1, y: -1, z: 1},
            "RTR": {x: 1, y: -1, z: 1},
            "LTS": {x: -1, y: 0, z: 1},
            "RTS": {x: 1, y: 0, z: 1}
        };

        const BED_TO_CHANNELS: Record<string, string[]> = {
            "2.0": ["L", "R"],
            "5.1": ["L", "R", "C", "LFE", "LS", "RS"],
            "7.1": ["L", "R", "C", "LFE", "LS", "RS", "LSS", "RSS"],
            "5.1.4": ["L", "R", "C", "LFE", "LS", "RS", "LTF", "RTF", "LTR", "RTR"],
            "7.1.4": ["L", "R", "C", "LFE", "LS", "RS", "LSS", "RSS", "LTF", "RTF", "LTR", "RTR"],
            "9.1.6": ["L", "R", "C", "LFE", "LS", "RS", "LSS", "RSS", "LTF", "RTF", "LCF", "LFE2", "LTR", "RTR", "LTS", "RTS"],
            "5.1.2": ["L", "R", "C", "LFE", "LS", "RS", "LTS", "RTS"],
        };

        let channels = BED_TO_CHANNELS[bed.config];
        if(!channels){
            console.warn("Unsupported bed configuration:", bed);
            return null;
        }

        const positions = channels.map((ch, index) => {
            const obj = CHANNEL_TO_OBJ[ch];
            if(!obj){
                console.warn("Unsupported channel in bed configuration:", ch);
                return null;
            }
            return {...obj, channel: index, color: bedColor};
        });

        if(positions.includes(null)){
            console.warn("Some channels in bed configuration are unsupported:", bed);
            return null;
        }

        return positions.filter(p=>p!==null);
    }

    let bedObjectPositions = $derived(beds ? beds.map(bedConfigToObjectViewPositions).flat().filter(p=>p!==null).filter(p=>p.z >= 0) : []);

    let objectPositions = $derived(objects ? objects.map(obj=>({x: obj.x, y: obj.y, z: obj.z, channel: obj.channel, color: objColor})) : []);

    let combinedObjectsAndBedPositions = $derived([...objectPositions, ...bedObjectPositions]);
</script>

<style>

</style>

<div class="in-a-row">
    <AtmosCartPannerView objects={combinedObjectsAndBedPositions} size={size} theme={theme}/>
</div>