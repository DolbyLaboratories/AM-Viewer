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

# **************************************************************************************************************************************************************
# **************************************************************************************************************************************************************

# Consts
from adm.adm_const import DIRECTSPEAKERS, MATRIX, OBJECTS, HOA, BINAURAL
from adm.adm_const import MIXED_CONTENT, UNDEFINED, MUSIC, EFFECT, COMPLETE_MAIN
from adm.adm_const import DIALOGUE, VOICEOVER, SPOKEN_SUBTITLE, AUDIO_DESCRIPTION, COMMENTARY, EMERGENCY
from adm.adm_const import NON_DIALOGUE_CONTENT_KIND, DIALOGUE_CONTENT_KIND, MIXED_CONTENT_KIND, NON_DIALOGUE_CONTENT, DIALOGUE_CONTENT, DIALOGUE_TEXT
from adm.adm_const import POLAR, CARTESIAN, COORDINATE_MODE

from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_A, LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_B
from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_D, LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_J
from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_2_0, LOUDSPEAKER_CONFIG_COMMON_USE_5_0, LOUDSPEAKER_CONFIG_COMMON_USE_5_1
from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_5_1_4, LOUDSPEAKER_CONFIG_COMMON_USE_5_0_4
from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_7_0_4, LOUDSPEAKER_CONFIG_COMMON_USE_7_1_4

from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_LABELS
from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_ALT_LABELS
from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_AZIMUTH
from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_ALT_AZIMUTH
from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_ELEVATION
from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_DISTANCE

from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_ALT_SWITCH
from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_RANGE_START
from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_RANGE_END

from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_LABELS
from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_ALT_LABELS
from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_AZIMUTH
from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_ALT_AZIMUTH
from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_ELEVATION
from adm.adm_const import LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_DISTANCE

from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_LABELS
from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_XPOS
from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_YPOS
from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_ALT_YPOS
from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_ZPOS

from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_LFE_INDEX_VALUE
from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_ALT_SWITCH
from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_RANGE_START
from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_RANGE_END

from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_VERTICAL_SPEAKER_LABELS
from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_VERTICAL_SPEAKER_XPOS
from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_VERTICAL_SPEAKER_YPOS
from adm.adm_const import LOUDSPEAKER_CONFIG_COMMON_USE_VERTICAL_SPEAKER_ZPOS

from adm.adm_const import LOUDSPEAKER_CONFIG_HORIZONTAL_CHANNEL_MASK
from adm.adm_const import LOUDSPEAKER_CONFIG_VERTICAL_CHANNEL_MASK

from adm.adm_const import MIN_AUDIO_CHANNEL, MAX_AUDIO_CHANNEL

from adm.adm_const import MIN_MAX_AZIMUTH, MIN_MAX_ELEVATION, MIN_MAX_DISTANCE
from adm.adm_const import MIN_MAX_XPOS, MIN_MAX_YPOS, MIN_MAX_ZPOS

# Profile support **********************************************************************************************************************************************
from adm.adm_const import LIMITS_FILE

# Logging and related ******************************************************************************************************************************************
from adm.adm_const import ADM_LOG_FILE
from adm.adm_const import MSG_VALIDATION_PASS, MSG_VALIDATION_FAIL, MSG_VALIDATION_ABRT, MSG_INVALID_STUB, MSG_TYP_LBL_IS_DS, MSG_TYP_LBL_IS_OB
from adm.adm_const import MSG_FND_EL, MSG_MIN_EL, MSG_MAX_EL, MSG_FND_NO, MSG_LIM_NO, MSG_CONTENT_INFO

# XML file parsing *********************************************************************************************************************************************
from adm.adm_const import ADM_XML_TYP_DS, ADM_XML_TYP_OB,ADM_XML_INT_TYP_DS, ADM_XML_INT_TYP_OB

from adm.adm_const import ADM_XML_MODE_FILE
from adm.adm_const import ADM_XML_MODE_STRING

from adm.adm_const import ADM_XML_APR_ELN, ADM_XML_APR_ELN_AT_NM, ADM_XML_APR_ELN_AT_LN, ADM_XML_APR_ELN_AT_ID, ADM_XML_APR_ELN_SE_PL
from adm.adm_const import ADM_XML_APR_ELN_SE_PL_AT_LN, ADM_XML_APR_ELN_SE_CR, ADM_XML_APR_ELN_SE_LM, ADM_XML_APR_ELN_SE_AO

from adm.adm_const import ADM_XML_ACO_ELN, ADM_XML_ACO_ELN_AT_ID, ADM_XML_ACO_ELN_AT_NM, ADM_XML_APR_ELN_SE_DG

from adm.adm_const import ADM_XML_AOB_ELN, ADM_XML_AOB_ELN_AT_ID, ADM_XML_AOB_ELN_AT_NM, ADM_XML_AOB_ELN_SE_AP
from adm.adm_const import ADM_XML_AOB_ELN_SE_AT, ADM_XML_AOB_ELN_SE_HL, ADM_XML_AOB_ELN_SE_GN

from adm.adm_const import ADM_XML_APF_ELN, ADM_XML_APF_ELN_AT_ID, ADM_XML_APF_ELN_AT_NM, ADM_XML_APF_ELN_AT_TL, ADM_XML_APF_ELN_SE_AC

from adm.adm_const import ADM_XML_ACF_ELN, ADM_XML_ACF_ELN_AT_ID, ADM_XML_ACF_ELN_AT_NM, ADM_XML_ACF_ELN_SE_AB, ADM_XML_ACF_ELN_SE_AB_SE_CT
from adm.adm_const import ADM_XML_ACF_ELN_SE_AB_SE_SL, ADM_XML_ACF_ELN_SE_AB_SE_PS, ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_XC, ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_YC
from adm.adm_const import ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_ZC, ADM_XML_ACF_ELN_SE_AB_SE_HR, ADM_XML_ACF_ELN_SE_AB_SE_HR_AT_BP, ADM_XML_ACF_ELN_SE_AB_SE_HR_AT_MD
from adm.adm_const import ADM_XML_ACF_ELN_SE_AB_AT_ID, ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_CO, ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_XC, ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_YC
from adm.adm_const import ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_ZC

from adm.adm_const import ADM_XML_ATU_ELN, ADM_XML_ATU_ELN_AT_ID, ADM_XML_ATU_ELN_SE_CF, ADM_XML_ATU_ELN_SE_PF

from adm.adm_const import ADM_XML_APR_ELN_SE_DG_AT_ND, ADM_XML_APR_ELN_SE_DG_AT_DC, ADM_XML_APR_ELN_SE_DG_AT_MC

from adm.adm_const import ADM_XML_INDENT, PMD_XML_MODE_FILE, PMD_XML_MODE_STRING

# Classes ******************************************************************************************************************************************************
from adm.adm_classes import AudioProgramme, AudioContent, AudioObject, AudioBlockFormat, AudioPackFormat, AudioProgrammeLabel
from adm.adm_classes import AudioChannelFormat, AudioTrackFormat, AudioTrackUID, AudioMXFLookUp, AudioStreamFormat
from adm.adm_classes import Objects, DirectSpeakers, HeadphoneRender, LoudnessMetadata, Dialogue, NonDialogueContentKind, DialogueContentKind, MixedContentKind
from adm.adm_classes import AudioObjectInteraction, GainInteractionRange, PositionInteractionRange, Zone, ChannelLock, JumpPosition
from adm.adm_classes import ItemValidationData, Position, Headphone, AudioFormatExtended

# External system **********************************************************************************************************************************************
import csv
import logging
import xml.etree.cElementTree as ET
from collections import defaultdict
import xml.dom.minidom as minidom
import os

# Globals to keep track of ID allocation, lists etc. ***********************************************************************************************************
audio_object_counter = 0
audio_content_counter = 0
audio_programme_counter = 0
audio_pack_format_counter = 0
audio_channel_format_counter = 0
audio_stream_format_counter = 0
audio_track_format_counter = 0
audio_block_format_counter = 0
audio_track_uid_counter = 0

coordinate_mode = POLAR

audio_programme_list = []
audio_content_list = []
audio_object_list = []
audio_channel_format_list = []
audio_pack_format_list = []
audio_block_format_list = []
audio_track_uid_list = []
transport_track_format_list = []

# ************************************************************************************************************************************************************ #
# ************************************************************************************************************************************************************ #


def check_parameter_type(parameter, expected_type, calling_function):
    if type(parameter) is not expected_type:
        logging.debug(str(type(parameter)) + " value of " + str(parameter) + ' is not the expected data type of ' + str(
            expected_type) + ' in ' + str(calling_function))
    return


def check_parameter_value_range(parameter, min_value, max_value, calling_function):
    if parameter < min_value or parameter > max_value:
        logging.debug(str(type(parameter)) + " value of " + str(parameter) + ' is out of min/max range of ' + str(
            min_value) + ' to ' + str(max_value) + ' in ' + str(calling_function))
    return


def prettify_xml(elem):
    # This cleans up output from element tree (xml doesn't have indents, new lines, ugly), uses inbuilt minidom lib
    # Google's XML style guide states 2 space indents for sub element nesting
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent=ADM_XML_INDENT)


def find_list_reference_by_name(list_to_search, name):
    for i in range(0, len(list_to_search)):
        if list_to_search[i].name == name:
            return list_to_search[i]
    return None


def find_list_reference_by_id(list_to_search, id):
    for i in range(0, len(list_to_search)):
        if list_to_search[i].id == id:
            return list_to_search[i]
    return None


def get_audio_program_reference(object_name):
    i = 0
    while i < audio_programme_list.__len__():
        if audio_programme_list[i].name == object_name:
            return audio_programme_list[i]
        i += 1
    return None


def get_audio_content_reference(object_name):
    i = 0
    while i < audio_object_list.__len__():
        if audio_content_list[i].name == object_name:
            return audio_content_list[i]
        i += 1
    return None


def parse_adm_xml(xml_struct, mode):
    global audio_programme_list, audio_content_list, audio_object_list, audio_channel_format_list
    global audio_pack_format_list, audio_block_format, audio_track_uid_list, transport_track_format_list

    # Clear out model lists
    del audio_programme_list[:]
    del audio_content_list[:]
    del audio_object_list[:]
    del audio_channel_format_list[:]
    del audio_pack_format_list[:]
    del audio_block_format_list[:]
    del audio_track_uid_list[:]
    del transport_track_format_list[:]

    tree = None

    xml_audio_programme_list = []
    xml_audio_content_list = []
    xml_audio_object_list = []
    xml_audio_channel_format_list = []
    xml_audio_pack_format_list = []
    xml_audio_block_format_list = []
    xml_audio_track_uid_list = []
    xml_transport_track_format_list = []


    # Is source a blob of XML or an XML file ?
    if mode == ADM_XML_MODE_FILE:
        logging.info('Parsing XML ADM file ' + xml_struct)
        tree = ET.ElementTree(file=xml_struct)
    elif mode == ADM_XML_MODE_STRING:
        logging.info('Parsing XML ADM blob ')
        tree = ET.ElementTree(ET.fromstring(xml_struct))
    tree.getroot()
    root = tree.getroot()

    # Find root of metadata, there are two variants with S-ADM, one with and one without coreMetadata in the structure
    sadm_format_root = root.find('coreMetadata')
    if sadm_format_root is not None:
        adm_format_root = sadm_format_root.find('format')
        adm_format_extended_root = adm_format_root.find('audioFormatExtended')
    else:
        # adm_format_extended_root = adm_format_root.find('audioFormatExtended')
        adm_format_extended_root = root.find('audioFormatExtended')

    sadm_frame_header_root = root.find('frameHeader')
    if sadm_frame_header_root is not None:
        sadm_transport_track_format = sadm_frame_header_root.find('transportTrackFormat')
        if sadm_transport_track_format is not None:
            xml_transport_track_format_list = sadm_transport_track_format.findall('audioTrack')



    if adm_format_extended_root is not None:
        xml_audio_programme_list = adm_format_extended_root.findall(ADM_XML_APR_ELN)
    else:
        logging.critical('Failed to find ' + ADM_XML_APR_ELN + ' *** Aborting ***')
        return False

    # Check limits for element, abort if content is invalid
    if not get_item_limits(ADM_XML_APR_ELN, len(xml_audio_programme_list)):
        return False

    # Populate programmes list from XML source
    if xml_audio_programme_list is not None:
        for i in range(0, len(xml_audio_programme_list)):
            audio_programme_list.append(AudioProgramme(xml_audio_programme_list[i].attrib[ADM_XML_APR_ELN_AT_NM],
                                                       xml_audio_programme_list[i].attrib[ADM_XML_APR_ELN_AT_LN],
                                                       xml_audio_programme_list[i].attrib[ADM_XML_APR_ELN_AT_ID]))

            # For each program get all audioProgrammeLabels, audioContentIDRefs, and loudnessMetadata
            k = xml_audio_programme_list[i].findall(ADM_XML_APR_ELN_SE_PL)

            # Check limits for element, abort if content is invalid
            if not get_item_limits(ADM_XML_APR_ELN_SE_PL, len(k)):
                return False

            for j in range(0, len(k)):
                audio_programme_list[i].audio_programme_label.append(AudioProgrammeLabel(k[j].text, k[j].attrib[ADM_XML_APR_ELN_SE_PL_AT_LN]))

            k = xml_audio_programme_list[i].findall(ADM_XML_APR_ELN_SE_CR)

            # Check limits for element, abort if content is invalid
            if not get_item_limits(ADM_XML_APR_ELN_SE_CR, len(k)):
                return False

            if k is not None:
                # logging.info(audio_programme_list[i].id + ' contains ' + str(len(k)) + ' ' + ADM_XML_APR_ELN_SE_CR)
                for j in range(0, len(k)):
                    audio_programme_list[i].audio_content_idref.append(k[j].text)
            else:
                logging.debug(MSG_INVALID_STUB + ADM_XML_APR_ELN_SE_CR)

                # logging.error(audio_programme_list[i].id + ' contains ' + str(len(k)) + ' ' + ADM_XML_APR_ELN_SE_CR)
                # return False

            # TODO actually grab loudness metadata and populate
            k = xml_audio_programme_list[i].findall(ADM_XML_APR_ELN_SE_LM)

            # Check limits for element, abort if content is invalid
            if not get_item_limits(ADM_XML_APR_ELN_SE_LM, len(k)):
                return False

            if k is not None:
                for j in range(0, len(k)):
                    audio_programme_list[i].loudness_metadata = LoudnessMetadata()
            else:
                logging.debug(MSG_INVALID_STUB + ADM_XML_APR_ELN_SE_LM)

    else:
        logging.debug(MSG_INVALID_STUB + ADM_XML_APR_ELN)

    # Populate content list from XML source
    xml_audio_content_list = adm_format_extended_root.findall(ADM_XML_ACO_ELN)

    # Check limits for element, abort if content is invalid
    if not get_item_limits(ADM_XML_ACO_ELN, len(xml_audio_content_list)):
        return False

    if xml_audio_content_list is not None:
        for i in range(0, len(xml_audio_content_list)):
            audio_content_list.append(AudioContent(xml_audio_content_list[i].attrib[ADM_XML_ACO_ELN_AT_ID],
                                                   xml_audio_content_list[i].attrib[ADM_XML_ACO_ELN_AT_NM]))

            # For each content get dialogue entry
            k = xml_audio_content_list[i].findall(ADM_XML_APR_ELN_SE_DG)

            # Check limits for element, abort if content is invalid
            if not get_item_limits(ADM_XML_APR_ELN_SE_DG, len(k)):
                return False

            if k is not None:
                x = int(k[0].text)
                # ADM_XML_APR_ELN_SE_DG_AT_ND, ADM_XML_APR_ELN_SE_DG_AT_DC, ADM_XML_APR_ELN_SE_DG_AT_MC
                # y = int(k[0].attrib[ADM_XML_APR_ELN_SE_DG_AT_CK])

                z = DIALOGUE_TEXT[x] + ' = '
                if x == 0:
                    y = int(k[0].attrib[ADM_XML_APR_ELN_SE_DG_AT_ND])
                    z = z + NON_DIALOGUE_CONTENT_KIND[y]
                    audio_content_list[i].dialogue = Dialogue(k[0].text, k[0].attrib[ADM_XML_APR_ELN_SE_DG_AT_ND])
                elif x == 1:
                    y = int(k[0].attrib[ADM_XML_APR_ELN_SE_DG_AT_DC])
                    z = z + DIALOGUE_CONTENT_KIND[y]
                    audio_content_list[i].dialogue = Dialogue(k[0].text, k[0].attrib[ADM_XML_APR_ELN_SE_DG_AT_DC])
                elif x == 2:
                    y = int(k[0].attrib[ADM_XML_APR_ELN_SE_DG_AT_MC])
                    z = z + MIXED_CONTENT_KIND[y]
                    audio_content_list[i].dialogue = Dialogue(k[0].text, k[0].attrib[ADM_XML_APR_ELN_SE_DG_AT_MC])

                logging.info(ADM_XML_APR_ELN_SE_DG + ', ' + z)

                # audio_content_list[i].dialogue = Dialogue(k[0].text, k[0].attrib[ADM_XML_APR_ELN_SE_DG_AT_CK])
            else:
                logging.debug(MSG_INVALID_STUB + ADM_XML_APR_ELN_SE_DG)

            # For each content get audio object entries
            k = xml_audio_content_list[i].findall(ADM_XML_APR_ELN_SE_AO)

            # Check limits for element, abort if content is invalid
            if not get_item_limits(ADM_XML_APR_ELN_SE_AO, len(k)):
                return False

            if k is not None:
                for j in range(0, len(k)):
                    audio_content_list[i].audio_object_idref.append(k[j].text)
            else:
                logging.debug(MSG_INVALID_STUB + ADM_XML_APR_ELN_SE_AO)
    else:
        logging.debug(MSG_INVALID_STUB + ADM_XML_ACO_ELN)

    # Populate object list from XML source
    xml_audio_object_list = adm_format_extended_root.findall(ADM_XML_AOB_ELN)

    # Check limits for element, abort if content is invalid
    if not get_item_limits(ADM_XML_AOB_ELN, len(xml_audio_object_list)):
        return False

    if xml_audio_object_list is not None:
        for i in range(0, len(xml_audio_object_list)):
            audio_object_list.append(AudioObject(xml_audio_object_list[i].attrib[ADM_XML_AOB_ELN_AT_ID],
                                                 xml_audio_object_list[i].attrib[ADM_XML_AOB_ELN_AT_NM]))

            # For each object get audio pack entry
            k = xml_audio_object_list[i].findall(ADM_XML_AOB_ELN_SE_AP)

            # Check limits for element, abort if content is invalid
            if not get_item_limits(ADM_XML_AOB_ELN_SE_AP, len(k)):
                return False

            if k is not None:
                for j in range(0, len(k)):
                    audio_object_list[i].audio_pack_idref.append(k[j].text)
            else:
                logging.debug(MSG_INVALID_STUB + ADM_XML_AOB_ELN_SE_AP)

            # For each object get audio track uids
            k = xml_audio_object_list[i].findall(ADM_XML_AOB_ELN_SE_AT)

            # Check limits for element, abort if content is invalid
            if not get_item_limits(ADM_XML_AOB_ELN_SE_AT, len(k)):
                return False

            if k is not None:
                for j in range(0, len(k)):
                    audio_object_list[i].audio_track_idref.append(k[j].text)
            else:
                logging.debug(MSG_INVALID_STUB + ADM_XML_AOB_ELN_SE_AT)

            # For each object get gain
            k = xml_audio_object_list[i].findall(ADM_XML_AOB_ELN_SE_GN)

            # Check limits for element, abort if content is invalid
            if not get_item_limits(ADM_XML_AOB_ELN_SE_GN, len(k)):
                return False

            if k is not None:
                for j in range(0, len(k)):
                    audio_object_list[i].gain = k[j].text
            else:
                logging.debug(MSG_INVALID_STUB + ADM_XML_AOB_ELN_SE_GN)

            # For each object get headlocked
            k = xml_audio_object_list[i].findall(ADM_XML_AOB_ELN_SE_HL)

            # Check limits for element, abort if content is invalid
            if not get_item_limits(ADM_XML_AOB_ELN_SE_HL, len(k)):
                return False

            if k is not None:
                for j in range(0, len(k)):
                    audio_object_list[i].head_locked = k[j].text
            else:
                logging.debug(MSG_INVALID_STUB + ADM_XML_AOB_ELN_SE_HL)
    else:
        logging.debug(MSG_INVALID_STUB + ADM_XML_AOB_ELN)

    # Populate pack format list from XML source
    xml_audio_pack_format_list = adm_format_extended_root.findall(ADM_XML_APF_ELN)

    # Check limits for element, abort if content is invalid
    if not get_item_limits(ADM_XML_APF_ELN, len(xml_audio_pack_format_list)):
        return False

    # TODO set different ranges of channel formats based upon typelabel
    if xml_audio_pack_format_list is not None:
        for i in range(0, len(xml_audio_pack_format_list)):

            audio_pack_format_list.append(AudioPackFormat(xml_audio_pack_format_list[i].attrib[ADM_XML_APF_ELN_AT_ID],
                                                          xml_audio_pack_format_list[i].attrib[ADM_XML_APF_ELN_AT_NM],
                                                          xml_audio_pack_format_list[i].attrib[ADM_XML_APF_ELN_AT_TL]))

            # For each pack get audio channel format
            k = xml_audio_pack_format_list[i].findall(ADM_XML_APF_ELN_SE_AC)

            # Check limits for element, abort if content is invalid
            if not get_item_limits(ADM_XML_APF_ELN_SE_AC, len(k)):
                return False

            if k is not None:
                for j in range(0, len(k)):
                    audio_pack_format_list[i].audio_channel_idref.append(k[j].text)
            else:
                logging.debug(MSG_INVALID_STUB + ADM_XML_APF_ELN_SE_AC)
    else:
        logging.debug(MSG_INVALID_STUB + ADM_XML_APF_ELN)

    # Populate channel format list from XML source
    xml_audio_channel_format_list = adm_format_extended_root.findall(ADM_XML_ACF_ELN)

    # Check limits for element, abort if content is invalid
    if not get_item_limits(ADM_XML_ACF_ELN, len(xml_audio_channel_format_list)):
        return False


    audio_block_format_counter = 0
    if xml_audio_channel_format_list is not None:
        for i in range(0, len(xml_audio_channel_format_list)):
            audio_channel_format_list.append(AudioChannelFormat(xml_audio_channel_format_list[i].attrib[ADM_XML_ACF_ELN_AT_ID],
                                                                xml_audio_channel_format_list[i].attrib[ADM_XML_ACF_ELN_AT_NM]))

            # Is it a bed or object ? (use to set the cartesian flag)
            if xml_audio_channel_format_list[i].attrib[ADM_XML_ACF_ELN_AT_ID].find(ADM_XML_TYP_DS) > -1:
                type_label = ADM_XML_INT_TYP_DS
                logging.info(ADM_XML_ACF_ELN + MSG_TYP_LBL_IS_DS)
            elif xml_audio_channel_format_list[i].attrib[ADM_XML_ACF_ELN_AT_ID].find(ADM_XML_TYP_OB) > -1:
                type_label = ADM_XML_INT_TYP_OB
                logging.info(ADM_XML_ACF_ELN + MSG_TYP_LBL_IS_OB)

            # For each channel format get audio blocks
            k = xml_audio_channel_format_list[i].findall(ADM_XML_ACF_ELN_SE_AB)

            # Check limits for element, abort if content is invalid
            if not get_item_limits(ADM_XML_ACF_ELN_SE_AB, len(k)):
                return False

            # Currently we assume that there is only one audio block for now as PMD XML does not support dynamic XML timelines
            if k is not None:
                audio_block_format_list.append(AudioBlockFormat(k[0].attrib[ADM_XML_ACF_ELN_SE_AB_AT_ID]))
                audio_block_format_list[audio_block_format_counter].position_coord = Position(False)
                # If we are dealing with a type lable of Object then set teh cartesian flag
                if type_label == ADM_XML_INT_TYP_OB:
                    audio_block_format_list[audio_block_format_counter].cartesian = 1

                # Get position coordinates and update
                m = k[0].findall(ADM_XML_ACF_ELN_SE_AB_SE_PS)

                # Check limits for element, abort if content is invalid
                if not get_item_limits(ADM_XML_ACF_ELN_SE_AB_SE_PS, len(m)):
                    return False

                for q in range(0, len(m)):
                    if m[q].attrib[ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_CO] == ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_XC:
                        audio_block_format_list[audio_block_format_counter].position_coord.x_or_az = m[q].text
                    if m[q].attrib[ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_CO] == ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_YC:
                        audio_block_format_list[audio_block_format_counter].position_coord.y_or_el = m[q].text
                    if m[q].attrib[ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_CO] == ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_ZC:
                        audio_block_format_list[audio_block_format_counter].position_coord.z_or_ds = m[q].text

                # Get speaker label and update
                m = k[0].find(ADM_XML_ACF_ELN_SE_AB_SE_SL)
                if m is not None:
                    audio_block_format_list[audio_block_format_counter].speaker_label = m.text
                    logging.info(MSG_FND_EL + ADM_XML_ACF_ELN_SE_AB_SE_SL + ' ' + m.text)

                # Get headphone render and update
                m = k[0].find(ADM_XML_ACF_ELN_SE_AB_SE_HR)
                if m is not None:
                    audio_block_format_list[audio_block_format_counter].headphone_render = \
                        Headphone(m.text, m.attrib[ADM_XML_ACF_ELN_SE_AB_SE_HR_AT_BP], m.attrib[ADM_XML_ACF_ELN_SE_AB_SE_HR_AT_MD])
                    logging.info(MSG_FND_EL + ADM_XML_ACF_ELN_SE_AB_SE_HR + ' ' + m.text)

                audio_block_format_counter += 1
            else:
                logging.debug(MSG_INVALID_STUB + ADM_XML_ACF_ELN_SE_AB)
    else:
        logging.debug(MSG_INVALID_STUB + ADM_XML_ACF_ELN)

    # Populate audio track uid list from XML source
    xml_audio_track_uid_list = adm_format_extended_root.findall(ADM_XML_ATU_ELN)

    # Check limits for element, abort if content is invalid
    if not get_item_limits(ADM_XML_ATU_ELN, len(xml_audio_track_uid_list)):
        return False

    if xml_audio_track_uid_list is not None:
        # audio_track_uid_counter = 0
        for i in range(0, len(xml_audio_track_uid_list)):
            audio_track_uid_list.append(AudioTrackUID(xml_audio_track_uid_list[i].attrib[ADM_XML_ATU_ELN_AT_ID]))
            # Get channel format id and update
            j = xml_audio_track_uid_list[i].findall(ADM_XML_ATU_ELN_SE_CF)

            # TODO Add extra checking for only 1 each of audioChannelFormatIDRef & audioPackFormatIDRef
            if j is not None:
                # Check limits for element, abort if content is invalid
                if not get_item_limits(ADM_XML_ATU_ELN_SE_CF, len(j)):
                    return False

                audio_track_uid_list[i].channel_format_id = j[0].text
                logging.info(MSG_FND_EL + '1 ' + ADM_XML_ATU_ELN_SE_CF + ' ' + j[0].text)
            else:
                logging.critical(ADM_XML_ATU_ELN + MSG_FND_NO + ADM_XML_ATU_ELN_SE_CF)
                return False


            # Get pack format id and update
            j = xml_audio_track_uid_list[i].findall(ADM_XML_ATU_ELN_SE_PF)

            if j is not None:
                # Check limits for element, abort if content is invalid
                if not get_item_limits(ADM_XML_ATU_ELN_SE_PF, len(j)):
                    return False

                audio_track_uid_list[i].pack_format_id = j[0].text
                logging.info(MSG_FND_EL + '1 ' + ADM_XML_ATU_ELN_SE_PF + ' ' + j[0].text)
            else:
                logging.critical(ADM_XML_ATU_ELN + MSG_FND_NO + ADM_XML_ATU_ELN_SE_PF)
                return False

    else:
        logging.debug(MSG_INVALID_STUB + ADM_XML_ACF_ELN)

    # Populate the final model
    mdl_audio_programmes = []
    mdl_audio_content = []
    mdl_audio_object = []
    mdl_audio_pack_fmt = []
    mdl_audio_channel_fmt = []
    mdl_audio_block_fmt = []
    mdl_audio_track_uid = []

    # Start populating audio programmes
    for i in range(0, len(audio_programme_list)):
        mdl_audio_programmes.append(AudioProgramme(audio_programme_list[i].name, audio_programme_list[i].language, audio_programme_list[i].id))
        mdl_audio_programmes[i].loudness_metadata = audio_programme_list[i].loudness_metadata
        mdl_audio_programmes[i].audio_programme_label = audio_programme_list[i].audio_programme_label

    # Start populating audio content
    for i in range(0, len(audio_content_list)):
        mdl_audio_content.append(AudioContent(audio_content_list[i].id, audio_content_list[i].name))
        mdl_audio_content[i].dialogue = audio_content_list[i].dialogue

    # Start populating audio object
    for i in range(0, len(audio_object_list)):
        mdl_audio_object.append(AudioObject(audio_object_list[i].id, audio_object_list[i].name))

    # Start populating audio pack
    for i in range(0, len(audio_pack_format_list)):
        mdl_audio_pack_fmt.append(AudioPackFormat(audio_pack_format_list[i].id, audio_pack_format_list[i].name, audio_pack_format_list[i].type_label))

    # Start populating audio block
    mdl_audio_block_fmt = audio_block_format_list

    # Update audio channel with audio block
    for i in range(0, len(audio_channel_format_list)):
        mdl_audio_channel_fmt.append(AudioChannelFormat(audio_channel_format_list[i].id, audio_channel_format_list[i].name))
        search = 'AB_' + mdl_audio_channel_fmt[i].id[3:] + '_00000001'
        # z = find_list_reference_by_id(mdl_audio_block_fmt, search)
        mdl_audio_channel_fmt[i].audio_block = find_list_reference_by_id(mdl_audio_block_fmt, search)

    # Update audio pack with audio channel
    for i in range(0, len(mdl_audio_pack_fmt)):
        for j in range(0, len(audio_pack_format_list[i].audio_channel_idref)):
            # z = find_list_reference_by_id(mdl_audio_channel_fmt, audio_pack_format_list[i].audio_channel_idref[j])
            mdl_audio_pack_fmt[i].audio_channel_idref.append(find_list_reference_by_id(mdl_audio_channel_fmt, audio_pack_format_list[i].audio_channel_idref[j]))

    # Start populating audio track
    for i in range(0, len(audio_track_uid_list)):
        mdl_audio_track_uid.append(AudioTrackUID(audio_track_uid_list[i].id))

        for j in range(0, len(mdl_audio_channel_fmt)):
            if mdl_audio_channel_fmt[j].id == audio_track_uid_list[i].channel_format_id:
                mdl_audio_track_uid[i].channel_format_id = mdl_audio_channel_fmt[j]
                break

        for j in range(0, len(mdl_audio_pack_fmt)):
            if mdl_audio_pack_fmt[j].id == audio_track_uid_list[i].pack_format_id:
                mdl_audio_track_uid[i].pack_format_id = mdl_audio_pack_fmt[j]

        for j in range(0, len(xml_transport_track_format_list)):
            q = xml_transport_track_format_list[j].find('audioTrackUIDRef')
            if q.text == audio_track_uid_list[i].id:
                mdl_audio_track_uid[i].track_id = xml_transport_track_format_list[j].attrib['trackID']

    # Update audio object with gain, audio_pack_idref, audio_track_uidref
    for i in range(0, len(mdl_audio_object)):
        # gain
        for j in range(0, len(audio_object_list)):
            if mdl_audio_object[i].id == audio_object_list[j].id:
                mdl_audio_object[i].gain = audio_object_list[j].gain
                break

        # Audio pack
        for j in range(0, len(audio_object_list)):
            if mdl_audio_object[i].id == audio_object_list[j].id:
                mdl_audio_object[i].audio_pack_idref.append(find_list_reference_by_id(mdl_audio_pack_fmt, audio_object_list[j].audio_pack_idref[0]))
                break

        # Audio tracks
        for j in range(0, len(audio_object_list)):
            if mdl_audio_object[i].id == audio_object_list[j].id:
                for k in range(0, len(audio_object_list[j].audio_track_idref)):
                    mdl_audio_object[i].audio_track_idref.append(find_list_reference_by_id(mdl_audio_track_uid, audio_object_list[j].audio_track_idref[k]))
                break

    # Update audio content with audio_object_idref
    for i in range(0, len(mdl_audio_content)):
        for j in range(0, len(audio_content_list)):
            if mdl_audio_content[i].id == audio_content_list[j].id:
                for k in range(0, len(audio_content_list[j].audio_object_idref)):
                    mdl_audio_content[i].audio_object_idref.append(find_list_reference_by_id(mdl_audio_object, audio_content_list[j].audio_object_idref[k]))
                break

    # Update audio programmes with audio_content_idref
    for i in range(0, len(mdl_audio_programmes)):
        for j in range(0, len(audio_programme_list)):
            if mdl_audio_programmes[i].id == audio_programme_list[j].id:
                for k in range(0, len(audio_programme_list[j].audio_content_idref)):
                    z = find_list_reference_by_id(mdl_audio_content, audio_programme_list[j].audio_content_idref[k])
                    mdl_audio_programmes[i].audio_content_idref.append(z)
                break

    # Package all the data together into a audio format extended container
    a = AudioFormatExtended()
    a.audio_programme = mdl_audio_programmes
    a.audio_content = mdl_audio_content
    a.audio_object = mdl_audio_object
    a.audio_pack_format = mdl_audio_pack_fmt
    a.audio_channel_format = mdl_audio_channel_fmt
    a.audio_track_uid = mdl_audio_track_uid

    return a


def populate_model_from_xml(audio_program_list, audio_content_list, audio_object_list, audio_pack_format_list,
                            audio_channel_format_list, audio_block_format_list, audio_track_uid_list):
    print()
    return


def get_item_limits(item_name, number_found):

    # TODO This is slow
    return True

    minval = None
    maxval = None
    limits_filename = os.path.dirname(__file__) + "/" + LIMITS_FILE
    with open(limits_filename) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row["element"] == item_name:
                minval = row["min_occurs"]
                maxval = row["max_occurs"]
                break

    if minval is None:
        logging.critical(MSG_VALIDATION_FAIL + MSG_FND_NO + item_name + MSG_LIM_NO)
        return False

    logging.info(MSG_FND_EL + str(number_found) + ' ' + item_name + MSG_MIN_EL + minval + MSG_MAX_EL + maxval)
    if number_found < int(minval) or number_found > int(maxval):
        logging.critical(MSG_VALIDATION_FAIL + MSG_VALIDATION_ABRT)
        return False
    else:
        logging.info(MSG_VALIDATION_PASS)
    return True


def start_logging():
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(levelname)s %(message)s', filename=ADM_LOG_FILE, filemode='w')
    logging.info('Started')
    return

"""
def convert_adm_xml_to_pmd_xml(xml_struct, mode):
    # my_metadata = parse_adm_xml(xml_struct, mode)

    # (xml_file, ext_audio_signal_list, ext_audio_bed_list, ext_audio_object_list, ext_audio_presentation_list, ext_iat_list):
    # write_pmd_xml_from_external('converted_adm_.xml')
    a = create_audio_bed("7.1.4 M&E", LOUDSPEAKER_CONFIG_COMMON_USE_7_1_4, 1)


DIALOGUE = 0
VDS = 1
VOICEOVER = 2
GENERIC = 3
SPOKEN_SUBTITLE = 4
EMERGENCY_ALERT = 5
EMERGENCY_INFORMATION = 6


    b = create_object("English Dialogue", DIALOGUE, False, -1.0, 1.0, 0.0, 0.0, False, False, 20, 0.0)
    c = create_object("French Dialogue", VDS, False, -1.0, 1.0, 0.0, 0.0, False, False, 21, 0.0)
    d = create_object("German Dialogue", SPOKEN_SUBTITLE, False, -1.0, 1.0, 0.0, 0.0, False, False, 22, 0.0)

    # from pmd_tool import create_audio_bed, create_object, add_audio_presentation_names_by_name, add_iat
    add_iat(str(uuid.uuid4()), 12345678)
    return
"""

# ************************************************************************************************************************************************************ #
# Create the ADM model of content
# ************************************************************************************************************************************************************ #


# start_logging()

# Set global coordinate mode
coordinate_mode = CARTESIAN

if __name__ == "__main__":
    print ("main")

    cmdline = True

    if cmdline:
        import os
        import linecache
        import time
        import tracemalloc

        # tracemalloc.start()
 
        loop_counter = 1
        startsecs = time.time()
        
        for i in range(0, loop_counter):
            my_metadata = parse_adm_xml("skip_sadm.xml", ADM_XML_MODE_FILE)
            #my_metadata = parse_adm_xml("gen.adm_+_gen.sadm.xml", ADM_XML_MODE_FILE)

        endsecs = time.time()
        call_time = (endsecs - startsecs) / loop_counter
        print('Runtime = ' + str(endsecs - startsecs))
        print ('Call time = ' + str(call_time))        

        """
        key_type = 'lineno'
        limit = 10
        snapshot = tracemalloc.take_snapshot()
        snapshot = snapshot.filter_traces((tracemalloc.Filter(False, "<frozen importlib._bootstrap>"), tracemalloc.Filter(False, "<unknown>")))
        top_stats = snapshot.statistics(key_type)
        print("Top %s lines" % limit)
        print('{: <10}'.format("index"), '{: <40}'.format("filename"), '{: <10}'.format("line no"), '{: <10}'.format("size kB"))
        for index, stat in enumerate(top_stats[:limit], 1):
            frame = stat.traceback[0]
            filename = os.sep.join(frame.filename.split(os.sep)[-2:])
            print('{: <10}'.format(index), '{: <40}'.format(filename), '{: <10}'.format(frame.lineno), '{:0.1f}'.format(stat.size / 1024), "kB")
            line = linecache.getline(frame.filename, frame.lineno).strip()
            if line:
                print('    %s' % line)
        other = top_stats[limit:]
        if other:
            size = sum(stat.size for stat in other)
            print("%s other: %.1f KiB" % (len(other), size / 1024))
        total = sum(stat.size for stat in top_stats)
        print("Total allocated size: %.1f KiB" % (total / 1024))         
        """


        # convert_adm_xml_to_pmd_xml("serial_adm.xml", ADM_XML_MODE_FILE)
        #my_metadata = parse_adm_xml("serial_adm.xml", ADM_XML_MODE_FILE)
        #print()
"""
# create_static_dialogue_object(name, dialogue_type, azimuth_or_x, elevation_or_y, distance_or_z, channel_number)
create_static_dialogue_object("English Dialogue", DIALOGUE, -1.0, 1.0, 0.0, 12)
create_static_dialogue_object("English AD", AUDIO_DESCRIPTION, -0.5, -0.3, 0.5, 13)
create_static_dialogue_object("French Dialogue", DIALOGUE, 0.75, 0.65, 0.55, 14)
create_static_dialogue_object("French AD", AUDIO_DESCRIPTION, -0.11, -0.22, -0.33, 15)

# create_audio_bed(name, configuration, start_channel)
create_audio_bed("7.1.4 M&E", LOUDSPEAKER_CONFIG_COMMON_USE_7_1_4, 1)

# create_audio_programme(name, language, [names list of objects to include in the programme])
create_audio_programme("P1", "eng", ["7.1.4 M&E", "English Dialogue"])
create_audio_programme("P2", "fra", ["7.1.4 M&E", "French Dialogue"])
create_audio_programme("P3", "eng", ["7.1.4 M&E", "English AD"])
create_audio_programme("P4", "fra", ["7.1.4 M&E", "French AD"])

# add_audio_programme_labels(name, [list of vales and language code pairs]
add_audio_programme_labels("P1", ["English Commentator", "eng", "Commentateur Anglais", "fra"])
add_audio_programme_labels("P2", ["French Commentator", "eng", "Commentateur Francais", "fra"])
add_audio_programme_labels("P3", ["English AD", "eng", "Audiodescription en Anglais", "fra"])
add_audio_programme_labels("P4", ["French AD", "eng", "Audiodescription en Francais", "fra"])

print("Done")

        key_type = 'lineno'
        limit = 10
        snapshot = tracemalloc.take_snapshot()
        snapshot = snapshot.filter_traces((tracemalloc.Filter(False, "<frozen importlib._bootstrap>"), tracemalloc.Filter(False, "<unknown>")))
        top_stats = snapshot.statistics(key_type)
        print("Top %s lines" % limit)
        print('{: <10}'.format("index"), '{: <40}'.format("filename"), '{: <10}'.format("line no"), '{: <10}'.format("size kB"))
        for index, stat in enumerate(top_stats[:limit], 1):
            frame = stat.traceback[0]
            filename = os.sep.join(frame.filename.split(os.sep)[-2:])
            print('{: <10}'.format(index), '{: <40}'.format(filename), '{: <10}'.format(frame.lineno), '{:0.1f}'.format(stat.size / 1024), "kB")
            line = linecache.getline(frame.filename, frame.lineno).strip()
            if line:
                print('    %s' % line)
        other = top_stats[limit:]
        if other:
            size = sum(stat.size for stat in other)
            print("%s other: %.1f KiB" % (len(other), size / 1024))
        total = sum(stat.size for stat in top_stats)
        print("Total allocated size: %.1f KiB" % (total / 1024))


"""

# ************************************************************************************************************************************************************ #

# ************************************************************************************************************************************************************ #
"""
Rules For Parsing ADM

1. Search for all objects
2. For each object store audioObjectID, audioObjectName, audioPackFormatIDRef, gain, headlocked, and list of audioTrackUIDRef
3. Search for each audioPackFormatID
4. For each audio pack store audioPackFormatID, audioPackFormatName, typeLabel, and list of audioChannelFormatIDRef
5. Search for each audioChannelFormatID
6. For each channel format store audioChannelFormatID, audioChannelFormatName, typeLabel, and list of audioBlockFormat entries
7. Search for each audioBlockFormat
7. For each audioBlockFormat store audioBlockFormatID, cartesian flag, position coordinates, speaker label, objectDivergence, headphoneRender
8. Search for each audioTrackUID
9. For each audioTrack store UID, audioChannelFormatIDRef, audioPacklFormatIDRef
10. Search for each audioProgramme
11. For each audioProgramme store audioProgrammeID, audioProgrammeName, audioProgrammeLanguage, loudnessMetadata, list of audioProgrammeLabel, list of audioContentIDRef
12. Search for each audioContent
13. For each store audioContentID, audioContentName, list of audioObjectIDRef, dialog
"""

# ************************************************************************************************************************************************************ #


"""
def check_positional_coordinates_in_range(azimuth_or_x, elevation_or_y, distance_or_z, calling_function):
    global coordinate_mode
    if coordinate_mode == POLAR:
        azimuth_or_x_range = MIN_MAX_AZIMUTH
        elevation_or_y_range = MIN_MAX_ELEVATION
        distance_or_z_range = MIN_MAX_DISTANCE
    elif coordinate_mode == CARTESIAN:
        azimuth_or_x_range = MIN_MAX_XPOS
        elevation_or_y_range = MIN_MAX_YPOS
        distance_or_z_range = MIN_MAX_ZPOS

    if abs(azimuth_or_x) > azimuth_or_x_range:
        logging.debug(str(type(azimuth_or_x)) + " value of " + str(azimuth_or_x) + ' is out of min/max range of ' + str(
            azimuth_or_x_range) + ' in ' + str(calling_function))

    if abs(elevation_or_y) > elevation_or_y_range:
        logging.debug(str(type(elevation_or_y)) + " value of " + str(elevation_or_y) + ' is out of min/max range of ' + str(
            elevation_or_y_range) + ' in ' + str(calling_function))

    if abs(distance_or_z) > distance_or_z_range:
        logging.debug(str(type(distance_or_z)) + " value of " + str(distance_or_z) + ' is out of min/max range of ' + str(
            distance_or_z_range) + ' in ' + str(calling_function))
    return

def create_audio_bed(obj_name, loudspeaker_configuration, start_audio_channel):

    ************************************************************************************************************************************************************
    ************************************************************************************************************************************************************

        Incoming loudspeaker_configuration
            logical and with LOUDSPEAKER_CONFIG_HORIZONTAL_CHANNEL_MASK (0xf) = number of horizontal channels
            logical and with LOUDSPEAKER_CONFIG_VERTICAL_CHANNEL_MASK (0xf0) = number of vertical channels

        Supported configurations already defined in BS.2051 (configurations use polar coordinates)
            LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_A = Sound system A (Stereo)
            LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_B = Sound system B (5.0)
            LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_D = Sound system D (5.0.4)
            LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_J = Sound system J (7.0.4)

        Additional configurations that are in common use (configurations use cartesian coordinates)
            LOUDSPEAKER_CONFIG_COMMON_USE_2_0 = 2.0
            LOUDSPEAKER_CONFIG_COMMON_USE_5_0 = 5.0
            LOUDSPEAKER_CONFIG_COMMON_USE_5_1 = 5.1
            LOUDSPEAKER_CONFIG_COMMON_USE_5_1_4 = 5.0.4
            LOUDSPEAKER_CONFIG_COMMON_USE_5_1_4 = 5.1.4
            LOUDSPEAKER_CONFIG_COMMON_USE_7_1_4 = 7.0.4
            LOUDSPEAKER_CONFIG_COMMON_USE_7_1_4 = 7.1.4

    ************************************************************************************************************************************************************
    ************************************************************************************************************************************************************


    global audio_object_counter
    global audio_content_counter
    global audio_pack_format_counter
    global audio_channel_format_counter
    global audio_block_format_counter
    global audio_track_uid_counter
    global coordinate_mode

    # Check incoming parameter data types
    check_parameter_type(obj_name, str, create_audio_bed)
    check_parameter_type(start_audio_channel, int, create_audio_bed)

    # Range check parameters
    check_parameter_value_range(start_audio_channel, MIN_AUDIO_CHANNEL, MAX_AUDIO_CHANNEL, create_audio_bed)

    # Snapshot current counter values for later on
    start_audio_track_uid_counter = audio_track_uid_counter
    start_audio_channel_format_counter = audio_channel_format_counter
    start_audio_block_format_counter = audio_block_format_counter

    # Figure the number of channels present for each speaker plane
    horizontal_channel_count = loudspeaker_configuration & LOUDSPEAKER_CONFIG_HORIZONTAL_CHANNEL_MASK
    vertical_channel_count = (loudspeaker_configuration & LOUDSPEAKER_CONFIG_VERTICAL_CHANNEL_MASK) / 0x10

    i = 0
    while i < (horizontal_channel_count + vertical_channel_count):
        audio_track_uid_list.append(AudioTrackUID(start_audio_channel + i))
        audio_track_uid_counter += 1
        i += 1

    # Create audio bed object
    audio_object_list.append(AudioObject(audio_object_counter + 1, obj_name))
    audio_object_list[audio_object_counter].update_dialogue(NON_DIALOGUE_CONTENT)

    # Add references to newly created AudioTrackUID
    i = 0
    while i < (audio_track_uid_counter - start_audio_track_uid_counter):
        audio_object_list[audio_object_counter].audio_track_uid_refs.append(audio_track_uid_list[start_audio_track_uid_counter + i])
        i += 1

    # Create a content holder for audio bed
    audio_content_list.append(AudioContent(audio_content_counter + 1, obj_name))
    # Note, should add Music + Effects option to ADM, currently options are Undefined, Music, Effects
    audio_content_list[audio_content_counter].update_non_dialogue(MUSIC)

    # Add reference to AudioObject
    audio_content_list[audio_content_counter].audio_object_id_refs.append(audio_object_list[audio_object_counter])

    # Create the AudioPackFormat to point to AudioChannelFormats
    audio_pack_format_list.append(AudioPackFormat(audio_pack_format_counter + 1, DIRECTSPEAKERS, obj_name))

    # Add reference in AudioObject to newly created AudioPackFormat
    audio_object_list[audio_object_counter].audio_pack_format_id_refs.append(audio_pack_format_list[audio_pack_format_counter])

    # Create AudioChannelFormat entries, references in AudioPackFormat, and  AudioBlockFormat
    i = 0
    while i < (horizontal_channel_count + vertical_channel_count):
        audio_channel_format_list.append(AudioChannelFormat(start_audio_channel_format_counter + i, DIRECTSPEAKERS, obj_name))
        audio_pack_format_list[audio_pack_format_counter].audio_channel_format_id_refs.append(
            audio_channel_format_list[start_audio_channel_format_counter + i])

        # AudioChannelFormat reference in AudioTrackUID is because PCM does not need to have corresponding audioTrackFormat & audioStreamFormat elements
        audio_track_uid_list[start_audio_track_uid_counter + i].audio_channel_format_id_ref.append(
            audio_channel_format_list[start_audio_channel_format_counter + i])

        # Create a single AudioBlockFormat entry as speaker channels are static, id has to align with the AudioChannelFormat its associated with
        audio_block_format_list.append(AudioBlockFormat(start_audio_channel_format_counter + 1 + i, DIRECTSPEAKERS, coordinate_mode, 1))
        audio_channel_format_counter += 1
        audio_block_format_counter += 1
        i += 1

    # Update created AudioBlockFormat speaker labels for horizontal channels
    i = 0
    while i < horizontal_channel_count:
        # BS.2015 definitions ?
        if LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_RANGE_START <= loudspeaker_configuration <= LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_RANGE_END:
            # Speaker labels and positions change based upon the number of horizontal channels in the configuration
            if horizontal_channel_count > LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_ALT_SWITCH:
                # Update speaker labels
                audio_block_format_list[start_audio_block_format_counter + i].definition.update_speaker_label(
                    LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_LABELS[i])
                # Update speaker positions
                audio_block_format_list[start_audio_block_format_counter + i].update_coordinates(
                    LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_AZIMUTH[i],
                    LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_ELEVATION[i],
                    LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_DISTANCE[i])
            else:
                # Update speaker labels
                audio_block_format_list[start_audio_block_format_counter + i].definition.update_speaker_label(
                    LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_ALT_LABELS[i])
                # Update speaker positions
                audio_block_format_list[start_audio_block_format_counter + i].update_coordinates(
                    LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_ALT_AZIMUTH[i],
                    LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_ELEVATION[i],
                    LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_DISTANCE[i])

        # Common usage definitions ?
        if LOUDSPEAKER_CONFIG_COMMON_USE_RANGE_START <= loudspeaker_configuration <= LOUDSPEAKER_CONFIG_COMMON_USE_RANGE_END:
            # Note, unlike the BS.2051 definitions, the horizontal speaker labels for common format don't change based upon number of horizontal channels
            skip_lfe = 0
            # There is the option of not including the LFE channel, this can be detected by the horizontal_channel_count being an odd number
            if horizontal_channel_count % 2 != 0:
                # Reached the LFE index value yet ?, if so bump offset by one in the label and positional lists
                if i >= LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_LFE_INDEX_VALUE:
                    skip_lfe = 1

            audio_block_format_list[start_audio_block_format_counter + i].definition.update_speaker_label(
                LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_LABELS[i + skip_lfe])

            # Update speaker positions
            if horizontal_channel_count > LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_ALT_SWITCH:
                audio_block_format_list[start_audio_block_format_counter + i].update_coordinates(
                    LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_XPOS[i + skip_lfe],
                    LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_YPOS[i + skip_lfe],
                    LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_ZPOS[i + skip_lfe])
            else:
                audio_block_format_list[start_audio_block_format_counter + i].update_coordinates(
                    LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_XPOS[i + skip_lfe],
                    LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_ALT_YPOS[i + skip_lfe],
                    LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_ZPOS[i + skip_lfe])
        i += 1

    # Update created AudioBlockFormat speaker labels for vertical channels
    i = 0
    while i < vertical_channel_count:
        # BS.2015 definitions ?
        if LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_RANGE_START <= loudspeaker_configuration <= LOUDSPEAKER_CONFIG_BS_2051_SOUND_SYSTEM_RANGE_END:
            # Vertical speaker labels and positions change based upon the number of horizontal channels in the configuration
            if horizontal_channel_count > LOUDSPEAKER_CONFIG_BS_2051_HORIZONTAL_SPEAKER_ALT_SWITCH:
                # Update speaker labels
                audio_block_format_list[start_audio_block_format_counter + horizontal_channel_count + i].definition.update_speaker_label(
                    LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_LABELS[i])
                # Update speaker positions
                audio_block_format_list[start_audio_block_format_counter + horizontal_channel_count + i].update_coordinates(
                    LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_AZIMUTH[i],
                    LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_ELEVATION[i],
                    LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_DISTANCE[i])
            else:
                # Update speaker labels
                audio_block_format_list[start_audio_block_format_counter + horizontal_channel_count + i].definition.update_speaker_label(
                    LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_ALT_LABELS[i])
                # Update speaker positions
                audio_block_format_list[start_audio_block_format_counter + horizontal_channel_count + i].update_coordinates(
                    LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_ALT_AZIMUTH[i],
                    LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_ELEVATION[i],
                    LOUDSPEAKER_CONFIG_BS_2051_VERTICAL_SPEAKER_DISTANCE[i])

        # Common usage definition ?
        if LOUDSPEAKER_CONFIG_COMMON_USE_RANGE_START <= loudspeaker_configuration <= LOUDSPEAKER_CONFIG_COMMON_USE_RANGE_END:
            # Note, unlike the BS.2051 definitions the vertical speaker labels and positions don't change based upon number of horizontal channels
            audio_block_format_list[start_audio_block_format_counter + horizontal_channel_count + i].definition.update_speaker_label(
                LOUDSPEAKER_CONFIG_COMMON_USE_VERTICAL_SPEAKER_LABELS[i])
            # Update speaker positions
            audio_block_format_list[start_audio_block_format_counter + horizontal_channel_count + i].update_coordinates(
                LOUDSPEAKER_CONFIG_COMMON_USE_VERTICAL_SPEAKER_XPOS[i],
                LOUDSPEAKER_CONFIG_COMMON_USE_VERTICAL_SPEAKER_YPOS[i],
                LOUDSPEAKER_CONFIG_COMMON_USE_VERTICAL_SPEAKER_ZPOS[i])
        i += 1

    # Add references in AudioChannelFormat to newly created AudioBlockFormat
    i = 0
    while i < (horizontal_channel_count + vertical_channel_count):
        audio_channel_format_list[start_audio_channel_format_counter + i].audio_block_format_id_ref.append(
            audio_block_format_list[start_audio_block_format_counter + i])
        i += 1
    audio_object_counter += 1
    audio_content_counter += 1
    audio_pack_format_counter += 1
    return


def create_static_dialogue_object(obj_name, dialog_type, azimuth_or_x, elevation_or_y, distance_or_z, audio_channel):
    global audio_object_counter
    global audio_content_counter
    global audio_pack_format_counter
    global audio_channel_format_counter
    global audio_block_format_counter
    global audio_track_uid_counter
    global coordinate_mode

    # Check incoming parameter data types
    check_parameter_type(obj_name, str, create_static_dialogue_object)
    check_parameter_type(dialog_type, int, create_static_dialogue_object)
    check_parameter_type(azimuth_or_x, float, create_static_dialogue_object)
    check_parameter_type(elevation_or_y, float, create_static_dialogue_object)
    check_parameter_type(distance_or_z, float, create_static_dialogue_object)
    check_parameter_type(audio_channel, int, create_static_dialogue_object)

    # Range check parameters
    check_parameter_value_range(dialog_type, DIALOGUE, EMERGENCY, create_static_dialogue_object)
    check_positional_coordinates_in_range(azimuth_or_x, elevation_or_y, distance_or_z, create_static_dialogue_object)
    check_parameter_value_range(audio_channel, MIN_AUDIO_CHANNEL, MAX_AUDIO_CHANNEL, create_static_dialogue_object)

    # Add AudioTrackUID entry to audio_track_uid_list
    audio_track_uid_list.append(AudioTrackUID(audio_channel))

    # Create new dialogue audio object
    audio_object_list.append(AudioObject(audio_object_counter + 1, obj_name))
    audio_object_list[audio_object_counter].update_dialogue(DIALOGUE_CONTENT)

    # Add reference to newly created AudioTrackUID
    audio_object_list[audio_object_counter].audio_track_uid_refs.append(audio_track_uid_list[audio_track_uid_counter])

    # Create a content holder for dialogue, you need one as the object itself doesn't signal the dialogue kind/sub-kind
    audio_content_list.append(AudioContent(audio_content_counter + 1, obj_name))
    audio_content_list[audio_content_counter].update_dialogue(dialog_type)

    # Add reference to AudioObject
    audio_content_list[audio_content_counter].audio_object_id_refs.append(audio_object_list[audio_object_counter])

    # Create the AudioPackFormat to point to AudioChannelFormat
    audio_pack_format_list.append(AudioPackFormat(audio_pack_format_counter + 1, OBJECTS, obj_name))

    # Add reference in AudioObject to newly created AudioPackFormat
    audio_object_list[audio_object_counter].audio_pack_format_id_refs.append(audio_pack_format_list[audio_pack_format_counter])

    # Create AudioChannelFormat entry
    audio_channel_format_list.append(AudioChannelFormat(audio_channel_format_counter + 1, OBJECTS, obj_name))

    # Create AudioChannelFormat reference in AudioTrackUID. PCM does not need to have corresponding audioTrackFormat & audioStreamFormat elements
    audio_track_uid_list[audio_track_uid_counter].audio_channel_format_id_ref.append(audio_channel_format_list[audio_channel_format_counter])

    # Add reference in AudioPackFormat and AudioTrackUID to newly created AudioChannelFormat
    audio_pack_format_list[audio_pack_format_counter].audio_channel_format_id_refs.append(audio_channel_format_list[audio_channel_format_counter])

    # Create a single AudioBlockFormat entry as object is static, id has to align with the AudioChannelFormat its associated with
    audio_block_format_list.append(AudioBlockFormat(audio_channel_format_counter + 1, OBJECTS, coordinate_mode, 1))

    # Update created AudioBlockFormat positional coordinates
    audio_block_format_list[audio_block_format_counter].update_coordinates(azimuth_or_x, elevation_or_y, distance_or_z)

    # Add reference in AudioChannelFormat to newly created AudioBlockFormat
    audio_channel_format_list[audio_channel_format_counter].audio_block_format_id_ref.append(audio_block_format_list[audio_block_format_counter])

    audio_object_counter += 1
    audio_content_counter += 1
    audio_pack_format_counter += 1
    audio_channel_format_counter += 1
    audio_block_format_counter += 1
    audio_track_uid_counter += 1
    return


def create_audio_programme(name, language, object_list):
    global audio_programme_counter

    # Check incoming parameter data types
    check_parameter_type(name, str, create_audio_programme)
    check_parameter_type(language, str, create_audio_programme)
    check_parameter_type(object_list, list, create_audio_programme)

    audio_programme_list.append(AudioProgramme(name, language, audio_programme_counter + 1))

    i = 0
    while i < object_list.__len__():
        audio_content = get_audio_content_reference(object_list[i])
        if audio_content is not None:
            audio_programme_list[audio_programme_counter].content_id_refs.append(audio_content)
        i += 1
    audio_programme_counter += 1
    return


def add_audio_programme_labels(audio_program_name, value_language_code_list):
    # Check incoming parameter data types
    check_parameter_type(audio_program_name, str, add_audio_programme_labels)
    check_parameter_type(value_language_code_list, list, add_audio_programme_labels)

    # Range check parameters
    if value_language_code_list.__len__() % 2 != 0:
        logging.debug("Parameter list " + str(value_language_code_list) + " does not contain pairs of values, there are only " + str(
            value_language_code_list.__len__()) + " total" + " in " + str(add_audio_programme_labels))

    audio_programme = get_audio_program_reference(audio_program_name)
    if audio_programme is not None:
        i = 0
        while i < value_language_code_list.__len__():
            audio_programme.add_programme_label(value_language_code_list[i], value_language_code_list[i + 1])
            i += 2
    return
"""
