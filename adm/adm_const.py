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

NON_DIALOGUE_CONTENT_KIND = ["undefined", "music", "effect"]
DIALOGUE_CONTENT_KIND = ["undefined", "dialogue", "voiceover", "spoken subtitle", "audio description", "commentary", "emergency"]
MIXED_CONTENT_KIND = ["undefined", "complete main", "mixed", "hearing impaired"]
DIALOGUE_TEXT = ["nonDialogueContentKind", "dialogueContentKind", "mixedContentKind"]
COORDINATE_MODE = ["Polar", "Cartesian"]
TYPE_DEFINITION = ["Invalid", "DirectSpeakers", "Matrix", "Objects", "HOA", "Binaural"]
TYPE_LABEL = ["Invalid", "0001", "0002", "0003", "0004", "0005"]

AUDIO_PACK_STR = "AP_000"
AUDIO_PROGRAMME_STR = "APR_"
AUDIO_CONTENT_STR = "AC_"
AUDIO_OBJECT_STR = "AO_"
AUDIO_BLOCK_STR = "AB_000"
AUDIO_CHANNEL_STR = "AC_000"
AUDIO_TRACK_UID_STR = "ATU_0000"

NON_DIALOGUE_CONTENT = 0
DIALOGUE_CONTENT = 1
MIXED_CONTENT = 2

UNDEFINED = 0
MUSIC = 1
EFFECT = 2

DIALOGUE = 1
VOICEOVER = 2
SPOKEN_SUBTITLE = 3
AUDIO_DESCRIPTION = 4
COMMENTARY = 5
EMERGENCY = 6


ADM_NON_DIALOGUE_CONTENT_KIND = 0
ADM_DIALOGUE_CONTENT_KIND = 1
ADM_MIXED_CONTENT_KIND = 2

ADM_DIALOGUE_CONTENT_KIND_UNDEFINED = 0
ADM_DIALOGUE_CONTENT_KIND_DIALOGUE = 1
ADM_DIALOGUE_CONTENT_KIND_VOICEOVER = 2
ADM_DIALOGUE_CONTENT_KIND_SPOKEN_SUBTITLE = 3
ADM_DIALOGUE_CONTENT_KIND_AUDIO_DESCRIPTION = 4
ADM_DIALOGUE_CONTENT_KIND_COMMENTARY = 5
ADM_DIALOGUE_CONTENT_KIND_EMERGENCY = 6

COMPLETE_MAIN = 1
MIXED = 2
HEARING_IMPAIRED = 3

POLAR = 0
CARTESIAN = 1

DIRECTSPEAKERS = 1
MATRIX = 2
OBJECTS = 3
HOA = 4
BINAURAL = 5

MIN_AUDIO_CHANNEL = 1
MAX_AUDIO_CHANNEL = 256

DEFAULT_AUDIO_SAMPLE_RATE = 48000
DEFAULT_AUDIO_BIT_DEPTH = 24

MIN_MAX_AZIMUTH = 180
MIN_MAX_ELEVATION = 90
MIN_MAX_DISTANCE = 1

MIN_MAX_XPOS = 1
MIN_MAX_YPOS = 1
MIN_MAX_ZPOS = 1

LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_RANGE_START = 0x0
LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_A = 0x02
LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_B = 0x05
LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_D = 0x45
LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_J = 0x47
LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_RANGE_END = 0x100

LOUDSPEAKER_CONFIG_COMMON_USE_RANGE_START = 0x100
LOUDSPEAKER_CONFIG_COMMON_USE_2_0 = 0x102
LOUDSPEAKER_CONFIG_COMMON_USE_3_0 = 0x103
LOUDSPEAKER_CONFIG_COMMON_USE_5_0 = 0x105
LOUDSPEAKER_CONFIG_COMMON_USE_5_1 = 0x106
LOUDSPEAKER_CONFIG_COMMON_USE_5_0_4 = 0x145
LOUDSPEAKER_CONFIG_COMMON_USE_5_1_4 = 0x146
LOUDSPEAKER_CONFIG_COMMON_USE_7_0_4 = 0x147
LOUDSPEAKER_CONFIG_COMMON_USE_7_1_4 = 0x148
LOUDSPEAKER_CONFIG_COMMON_USE_9_0_6 = 0x169
LOUDSPEAKER_CONFIG_COMMON_USE_9_1_6 = 0x16a
LOUDSPEAKER_CONFIG_COMMON_USE_RANGE_END = 0x200

LOUDSPEAKER_CONFIG_HORIZONTAL_CHANNEL_MASK = 0xf
LOUDSPEAKER_CONFIG_VERTICAL_CHANNEL_MASK = 0xf0

LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_LABELS = ["M+030", "M-030", "M+000", "M+090", "M-090", "M+135", "M-135"]
LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_ALT_LABELS = ["M+030", "M-030", "M+000", "M+110", "M-110"]
LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_AZIMUTH = ["30.0", "-30.0", "0.0", "90.0", "-90.0", "135.0", "-135.0"]
LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_ALT_AZIMUTH = ["30.0", "-30.0", "0.0", "110.0", "-110.0"]
LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_ELEVATION = ["0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0"]
LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_DISTANCE = ["1.0", "1.0", "1.0", "1.0", "1.0", "1.0", "1.0"]

LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_ALT_SWITCH = 5

LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_LABELS = ["U+045", "U-045", "U+135", "U-135"]
LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_ALT_LABELS = ["U+030", "U-030", "U+110", "U-110"]
LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_AZIMUTH = ["45.0", "-45.0", "135.0", "-135.0"]
LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_ALT_AZIMUTH = ["30.0", "-30.0", "110.0", "-110.0"]
LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_ELEVATION = ["30.0", "30.0", "30.0", "30.0"]
LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_DISTANCE = ["1.0", "1.0", "1.0", "1.0"]

LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_LABELS = ["RC_L", "RC_R", "RC_C", "RC_LFE", "RC_Ls", "RC_Rs", "RC_Lrs", "RC_Rrs"]
LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_XPOS = ["-1.0", "1.0", "0.0", "-1.0", "-1.0", "1.0", "-1.0", "1.0"]
LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_YPOS = ["1.0", "1.0", "1.0", "1.0", "0.0", "0.0", "-1.0", "1.0"]
LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_ALT_YPOS = ["1.0", "1.0", "1.0", "1.0", "-1.0", "1.0"]
LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_ZPOS = ["0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0"]

LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_LFE_INDEX_VALUE = 3
LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_ALT_SWITCH = 6

LOUDSPEAKER_CONFIG_COMMON_USE_VERTICAL_SPEAKER_LABELS = ["RC_Ltf", "RC_Rtf", "RC_Ltr", "RC_Rtr"]
LOUDSPEAKER_CONFIG_COMMON_USE_VERTICAL_SPEAKER_XPOS = ["-1.0", "1.0", "-1.0", "1.0"]
LOUDSPEAKER_CONFIG_COMMON_USE_VERTICAL_SPEAKER_YPOS = ["1.0", "1.0", "-1.0", "-1.0"]
LOUDSPEAKER_CONFIG_COMMON_USE_VERTICAL_SPEAKER_ZPOS = ["1.0", "1.0", "1.0", "1.0"]

ADM_LOG_FILE = 'adm_tool.log'
LIMITS_FILE = 'limits.txt'
MSG_VALIDATION_PASS = 'Validation stage passed'
MSG_VALIDATION_FAIL = 'Validation stage failed'
MSG_VALIDATION_ABRT = ' *** Aborting ***'
MSG_INVALID_STUB = 'Ended up in code that should never execute in '
MSG_TYP_LBL_IS_DS = ' is type DirectSpeakers'
MSG_TYP_LBL_IS_OB = ' is type Object'
MSG_FND_EL = 'Found '
MSG_MIN_EL = ', minimum entries allowed is '
MSG_MAX_EL = ', maximum entries allowed is '
MSG_FND_NO = ' could not find '
MSG_LIM_NO = ' info in limits file *** Aborting ***'
MSG_CONTENT_INFO = 'Content kind'

ADM_XML_MODE_FILE = 0
ADM_XML_MODE_STRING = 1

ADM_XML_TYP_DS = '_0001'
ADM_XML_TYP_OB = '_0003'
ADM_XML_INT_TYP_DS = 1
ADM_XML_INT_TYP_OB = 3

ADM_XML_APR_ELN = 'audioProgramme'
ADM_XML_APR_ELN_AT_NM = 'audioProgrammeName'
ADM_XML_APR_ELN_AT_LN = 'audioProgrammeLanguage'
ADM_XML_APR_ELN_AT_ID = 'audioProgrammeID'
ADM_XML_APR_ELN_SE_PL = 'audioProgrammeLabel'
ADM_XML_APR_ELN_SE_PL_AT_LN = 'language'
ADM_XML_APR_ELN_SE_CR = 'audioContentIDRef'
ADM_XML_APR_ELN_SE_LM = 'loudnessMetadata'

ADM_XML_ACO_ELN = 'audioContent'
ADM_XML_ACO_ELN_AT_ID = 'audioContentID'
ADM_XML_ACO_ELN_AT_NM = 'audioContentName'
ADM_XML_APR_ELN_SE_DG = 'dialogue'
ADM_XML_APR_ELN_SE_DG_AT_ND = 'nonDialogueContentKind'
ADM_XML_APR_ELN_SE_DG_AT_DC = 'dialogueContentKind'
ADM_XML_APR_ELN_SE_DG_AT_MC = 'mixedContentKind'

ADM_XML_APR_ELN_SE_AO = 'audioObjectIDRef'

ADM_XML_AOB_ELN = 'audioObject'
ADM_XML_AOB_ELN_AT_ID = 'audioObjectID'
ADM_XML_AOB_ELN_AT_NM = 'audioObjectName'
ADM_XML_AOB_ELN_SE_AP = 'audioPackFormatIDRef'
ADM_XML_AOB_ELN_SE_AT = 'audioTrackUIDRef'
ADM_XML_AOB_ELN_SE_HL = 'headLocked'
ADM_XML_AOB_ELN_SE_GN = 'gain'

ADM_XML_APF_ELN = 'audioPackFormat'
ADM_XML_APF_ELN_AT_ID = 'audioPackFormatID'
ADM_XML_APF_ELN_AT_NM = 'audioPackFormatName'
ADM_XML_APF_ELN_AT_TL = 'typeLabel'
ADM_XML_APF_ELN_SE_AC = 'audioChannelFormatIDRef'

ADM_XML_ACF_ELN = 'audioChannelFormat'
ADM_XML_ACF_ELN_AT_ID = 'audioChannelFormatID'
ADM_XML_ACF_ELN_AT_NM = 'audioChannelFormatName'
ADM_XML_ACF_ELN_SE_AB = 'audioBlockFormat'
ADM_XML_ACF_ELN_SE_AB_AT_ID = 'audioBlockFormatID'
ADM_XML_ACF_ELN_SE_AB_SE_CT = 'cartesian'
ADM_XML_ACF_ELN_SE_AB_SE_SL = 'speakerLabel'
ADM_XML_ACF_ELN_SE_AB_SE_PS = 'position'
ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_CO = 'coordinate'
ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_XC = 'X'
ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_YC = 'Y'
ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_ZC = 'Z'
ADM_XML_ACF_ELN_SE_AB_SE_HR = 'headphoneRender'
ADM_XML_ACF_ELN_SE_AB_SE_HR_AT_BP = 'Bypass'
ADM_XML_ACF_ELN_SE_AB_SE_HR_AT_MD = 'Mode'

ADM_XML_ATU_ELN = 'audioTrackUID'
ADM_XML_ATU_ELN_AT_ID = 'UID'
ADM_XML_ATU_ELN_SE_CF = 'audioChannelFormatIDRef'
ADM_XML_ATU_ELN_SE_PF = 'audioPackFormatIDRef'

ADM_XML_INDENT = "  "
PMD_XML_MODE_FILE = 0
PMD_XML_MODE_STRING = 1

# ************************************************************************************************************************************************************ #
# ************************************************************************************************************************************************************ #
