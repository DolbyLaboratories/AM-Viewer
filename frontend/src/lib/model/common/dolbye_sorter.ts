/****************************************************************************
 *
 *
 * Copyright (c) 2026 Dolby International AB.
 * All rights reserved.

 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED
 * BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
 * BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 ******************************************************************************/

import type { DolbyEMetadataField } from "$lib/cpp_backend_api/common/cpp_backend_types";

export type ParsedDolbyEMetadata = {
    globalFields: DolbyEMetadataField[];
    programFields: DolbyEMetadataField[][];
}


type ParsedDolbyEMetadataField = {
    group: string;
    programIndex: number;
    label: string;
    value: any;
}

type ParsedGlobalDolbyEMetadataField = {
    label: string;
    value: any;
}

type ParsedDolbyEMetadataReturnType = {
    globalInfo: {
        fields: ParsedGlobalDolbyEMetadataField[] 
    };
    programInfo:{
        programFields: ParsedDolbyEMetadataField[];
        numPrograms: number;
        uniqueGroups: string[];
        uniqueFieldLabels: string[];
    };
}

export function parseAllDolbyEMetadataFieldsIntoSomethingUseful(fields: DolbyEMetadataField[]): ParsedDolbyEMetadataReturnType {
    const programFields: ParsedDolbyEMetadataField[] = fields.filter(f=>!f.group.startsWith("Dolby E")).map(f=>{
        const programMatch = f.group.match(/.*\s(\d+)$/);
        const strippedGroup = programMatch ? f.group.replace(/\s\d+$/, '') : f.group;
        const programIndex = programMatch ? parseInt(programMatch[1]) : 0;
        const label = f.label.replace(/\s\d+$/, ''); // Remove trailing program number from label
        return {
            group: strippedGroup,
            programIndex,
            label,
            value: f.value
        };
    });

    const globalFields = fields.filter(f=>f.group.startsWith("Dolby E")).map(f=>{
        return {
            label: f.label,
            value: f.value
        };
    });

    const numPrograms = Math.max(...programFields.map(f=>f.programIndex+1), 0);
    const uniqueGroups = programFields.map(f=>f.group).filter((v, i, a) => a.indexOf(v) === i);
    const uniqueFieldLabels = programFields.map(f=>f.label).filter((v, i, a) => a.indexOf(v) === i);

    return { 
        globalInfo: {
            fields: globalFields
        },
        programInfo: {
            programFields,
            numPrograms,
            uniqueGroups,
            uniqueFieldLabels
        }
    };
}

type FormatReadyForTableType = {
    map: Record<string, Record<string, any[]>>;
    globalRows: Record<string,  any>;
    numberOfPrograms: number;
}
export function parsedDolbyEMetadataToFormatReadyForTable(parsed: ParsedDolbyEMetadataReturnType): FormatReadyForTableType {
    const { programFields, numPrograms, uniqueGroups, uniqueFieldLabels } = parsed.programInfo;
    const bigOlMap: Record<string, Record<string, any[]>> = {};

    programFields.forEach(field => {
        if(!bigOlMap[field.group]) {
            bigOlMap[field.group] = {};
        }
        if(!bigOlMap[field.group][field.label]) {
            bigOlMap[field.group][field.label] = Array(numPrograms).fill(null);
        }
        bigOlMap[field.group][field.label][field.programIndex] = field.value;
    });

    const numberOfPrograms = parsed.programInfo.numPrograms;

    const globalRows: Record<string, any> = parsed.globalInfo.fields.reduce((acc, field) => {
        acc[field.label] = field.value;
        return acc;
     }, {} as Record<string, any>);

    return { map: bigOlMap, globalRows, numberOfPrograms: numberOfPrograms };
}
