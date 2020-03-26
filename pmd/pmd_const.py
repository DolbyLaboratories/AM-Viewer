"""
****************************************************************************************************************************************************************
****************************************************************************************************************************************************************

    ___    ____  __  ___            ____  __  _______     ____               _           __
   /   |  / __ \/  |/  /           / __ \/  |/  / __ \   / __ \_________    (_)__  _____/ /_
  / /| | / / / / /|_/ /  ______   / /_/ / /|_/ / / / /  / /_/ / ___/ __ \  / / _ \/ ___/ __/
 / ___ |/ /_/ / /  / /  /_____/  / ____/ /  / / /_/ /  / ____/ /  / /_/ / / /  __/ /__/ /_
/_/  |_/_____/_/  /_/           /_/   /_/  /_/_____/  /_/   /_/   \____/_/ /\___/\___/\__/
                                                                      /___/

****************************************************************************************************************************************************************
****************************************************************************************************************************************************************

Copyright (c) 2018, Dolby Laboratories Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above
   copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials provided
   with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived
   from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

****************************************************************************************************************************************************************
****************************************************************************************************************************************************************
"""

# ************************************************************************************************************************************************************ #
# ************************************************************************************************************************************************************ #


PRESENTATION_CONFIG_TEXT = ["2.0", "3.0", "5.1", "5.1.2", "5.1.4", "7.1.4", "9.1.6"]
PRESENTATION_CONFIG_EQUIV = [2, 3, 6, 8, 10, 12, 16]

PRESENTATION_CONFIG_2_0 = 0
PRESENTATION_CONFIG_3_0 = 1
PRESENTATION_CONFIG_5_1 = 2
PRESENTATION_CONFIG_5_1_2 = 3
PRESENTATION_CONFIG_5_1_4 = 4
PRESENTATION_CONFIG_7_1_4 = 5
PRESENTATION_CONFIG_9_1_6 = 6

LOUDSPEAKER_CONFIG_2_0 = 0
LOUDSPEAKER_CONFIG_3_0 = 1
LOUDSPEAKER_CONFIG_5_0 = 2
LOUDSPEAKER_CONFIG_5_1 = 3
LOUDSPEAKER_CONFIG_5_0_2 = 4
LOUDSPEAKER_CONFIG_5_1_2 = 5
LOUDSPEAKER_CONFIG_5_0_4 = 6
LOUDSPEAKER_CONFIG_5_1_4 = 7
LOUDSPEAKER_CONFIG_7_0_4 = 8
LOUDSPEAKER_CONFIG_7_1_4 = 9
LOUDSPEAKER_CONFIG_9_0_6 = 10
LOUDSPEAKER_CONFIG_9_1_6 = 11

LOUDSPEAKER_CONFIG_COMMON_USE_RANGE_START = 0x100
LOUDSPEAKER_CONFIG_COMMON_USE_2_0 = 0x102
LOUDSPEAKER_CONFIG_COMMON_USE_3_0 = 0x103
LOUDSPEAKER_CONFIG_COMMON_USE_5_0 = 0x105
LOUDSPEAKER_CONFIG_COMMON_USE_5_1 = 0x106
LOUDSPEAKER_CONFIG_COMMON_USE_5_0_2 = 0x125
LOUDSPEAKER_CONFIG_COMMON_USE_5_1_2 = 0x126
LOUDSPEAKER_CONFIG_COMMON_USE_5_0_4 = 0x145
LOUDSPEAKER_CONFIG_COMMON_USE_5_1_4 = 0x146
LOUDSPEAKER_CONFIG_COMMON_USE_7_0_4 = 0x147
LOUDSPEAKER_CONFIG_COMMON_USE_7_1_4 = 0x148
LOUDSPEAKER_CONFIG_COMMON_USE_9_0_6 = 0x169
LOUDSPEAKER_CONFIG_COMMON_USE_9_1_6 = 0x16a
LOUDSPEAKER_CONFIG_COMMON_USE_RANGE_END = 0x200

LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_NAMES = ["2.0", "3.0", "5.0", "5.1", "5.0.2", "5.1.2", "5.0.4", "5.1.4", "7.0.4", "7.1.4", "9.0.6", "9.1.6"]
LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_EQUIV = [LOUDSPEAKER_CONFIG_COMMON_USE_2_0, LOUDSPEAKER_CONFIG_COMMON_USE_3_0, LOUDSPEAKER_CONFIG_COMMON_USE_5_0,
                                            LOUDSPEAKER_CONFIG_COMMON_USE_5_1, LOUDSPEAKER_CONFIG_COMMON_USE_5_0_2, LOUDSPEAKER_CONFIG_COMMON_USE_5_1_2,
                                            LOUDSPEAKER_CONFIG_COMMON_USE_5_0_4, LOUDSPEAKER_CONFIG_COMMON_USE_5_1_4, LOUDSPEAKER_CONFIG_COMMON_USE_7_0_4,
                                            LOUDSPEAKER_CONFIG_COMMON_USE_7_1_4, LOUDSPEAKER_CONFIG_COMMON_USE_9_0_6, LOUDSPEAKER_CONFIG_COMMON_USE_9_1_6]

LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_LFE_INDEX_VALUE = 3
LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_POST_INDEX_VALUE = 9

LOUDSPEAKER_CONFIG_HORIZONTAL_CHANNEL_MASK = 0xf
LOUDSPEAKER_CONFIG_VERTICAL_CHANNEL_MASK = 0xf0
LOUDSPEAKER_CONFIG_VERTICAL_CHANNEL_MIN = 0x2

LOUDSPEAKER_CONFIG_HORIZONTAL_SPEAKER_OUTPUT_TARGETS = ["Left", "Right", "Center", "LFE", "Left Surround", "Right Surround",
                                                        "Left Rear Surround", "Right Rear Surround", "Left Front Wide", "Right Front Wide"]

LOUDSPEAKER_CONFIG_VERTICAL_SPEAKER_OUTPUT_TARGETS = ["Left Top Middle", "Right Top Middle", "Left Top Front", "Right Top Front",
                                                      "Left Top Rear", "Right Top Rear"]

LOUDSPEAKER_CONFIG_VERTICAL_SPEAKER_POST_OUTPUT_TARGETS = ["Left Top Front", "Right Top Front", "Left Top Middle", "Right Top Middle",
                                                           "Left Top Rear", "Right Top Rear"]

OBJECT_CLASSES = ["Dialog", "VDS", "Voice Over", "Generic", "Spoken Subtitle", "Emergency Alert", "Emergency Information"]

AUDIO_SIGNAL_STR = "Ch-"

DIALOGUE = 0
VDS = 1
VOICEOVER = 2
GENERIC = 3
SPOKEN_SUBTITLE = 4
EMERGENCY_ALERT = 5
EMERGENCY_INFORMATION = 6

POLAR = 0
CARTESIAN = 1

MIN_AUDIO_SIGNAL = 1
MAX_AUDIO_SIGNAL = 4095

MIN_MAX_AZIMUTH = 180
MIN_MAX_ELEVATION = 90
MIN_MAX_DISTANCE = 1

MIN_MAX_XPOS = 1
MIN_MAX_YPOS = 1
MIN_MAX_ZPOS = 1

MIN_SIZE = 0
MAX_SIZE = 1

MIN_SOURCE_GAIN_DB = -25.0
MAX_SOURCE_GAIN_DB = 6.0

PMD_XML_AUDIO_SIGNALS_LEVEL = 1
PMD_XML_AUDIO_ELEMENTS_LEVEL = 2
PMD_XML_AUDIO_PRESENTATION_LEVEL = 3
PMD_XML_AUDIO_IAT_LEVEL = 4

PMD_XML_AUDIO_OBJECT_NAME = 0
PMD_XML_AUDIO_OBJECT_CLASS = 1
PMD_XML_AUDIO_OBJECT_DYNAMIC_UPDATES = 2
PMD_XML_AUDIO_OBJECT_XPOS = 3
PMD_XML_AUDIO_OBJECT_YPOS = 4
PMD_XML_AUDIO_OBJECT_ZPOS = 5
PMD_XML_AUDIO_OBJECT_SIZE = 6
PMD_XML_AUDIO_OBJECT_SIZE_3D = 7
PMD_XML_AUDIO_OBJECT_DIVERGE = 8
PMD_XML_AUDIO_OBJECT_AUDIO_SIGNAL = 9
PMD_XML_AUDIO_OBJECT_SOURCE_GAIN_DB = 10

PMD_XML_MODE_FILE = 0
PMD_XML_MODE_STRING = 1

PMD_XML_INDENT = "  "
PMD_XML_ATTRIB_ID = "id"

PMD_XML_ROOT = "Smpte2109"
PMD_XML_ROOT_CMT = "Generated by the PMD XML writer"
PMD_XML_ROOT_SE_CONTAINER = "ContainerConfig"
PMD_XML_ROOT_SE_CONTAINER_SE_SMP_OST = "SampleOffset"
PMD_XML_ROOT_SE_CONTAINER_SUB_E_D_TAGS = "DynamicTags"
PMD_XML_ROOT_SE_PMD = "ProfessionalMetadata"
PMD_XML_ROOT_SE_PMD_AT_VER = "version"
PMD_XML_ROOT_SE_PMD_AT_VER_VAL = "11.0"
PMD_XML_ROOT_SE_PMD_SE_TTL = "Title"

PMD_XML_ROOT_SE_PMD_SE_ASG = "AudioSignals"
PMD_XML_ROOT_SE_PMD_SE_ASG_SE_ASG = "AudioSignal"
PMD_XML_ROOT_SE_PMD_SE_ASG_SE_ASG_NME = "Name"
PMD_XML_ROOT_SE_PMD_SE_ASG_SE_ASG_AID = "ID"

PMD_XML_ROOT_SE_PMD_SE_AEL = "AudioElements"

PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB = "AudioBed"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_NME = "Name"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_CFG = "SpeakerConfig"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG = "OutputTargets"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG = "OutputTarget"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG_SE_ASG = "AudioSignals"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG_SE_ASG_SE_IDS = "ID"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG_SE_ASG_SE_GAN = "source_gain_db"

PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO = "AudioObject"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_NME = "Name"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_CLS = "Class"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_DUP = "DynamicUpdates"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_XPS = "X_Pos"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_YPS = "Y_Pos"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_ZPS = "Z_Pos"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_SIZ = "Size"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_S3D = "Size_3D"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_DVG = "Diverge"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_ASG = "AudioSignal"
PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_SGD = "SourceGainDB"


PMD_XML_ROOT_SE_PMD_SE_APR = "Presentations"
PMD_XML_ROOT_SE_PMD_SE_APR_SE_APR = "Presentation"
PMD_XML_ROOT_SE_PMD_SE_APR_AT_LNG = "language"
PMD_XML_ROOT_SE_PMD_SE_APR_SE_NME = "Name"
PMD_XML_ROOT_SE_PMD_SE_APR_SE_LNG = "Language"
PMD_XML_ROOT_SE_PMD_SE_APR_SE_CFG = "Config"
PMD_XML_ROOT_SE_PMD_SE_APR_SE_EMT = "Element"

PMD_XML_ROOT_SE_PMD_SE_IAT = "IAT"
PMD_XML_ROOT_SE_PMD_SE_IAT_SE_UUI = "UUID"
PMD_XML_ROOT_SE_PMD_SE_IAT_SE_CID = "Content_ID"
PMD_XML_ROOT_SE_PMD_SE_IAT_SE_TST = "Timestamp"

PMD_LOG_FILE = "pmd_tool.log"

# ************************************************************************************************************************************************************ #
# ************************************************************************************************************************************************************ #
