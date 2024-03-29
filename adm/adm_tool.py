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

from adm.adm_const import ADM_XML_CM, ADM_XML_FT, ADM_XML_AF

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

from adm.adm_const import SADM_XML_TTF_ELN_SE_AT_SE_AR, SADM_XML_TTF_ELN_SE_AT_AT_TI, SADM_XML_FH, SADM_XML_TTF_ELN
from adm.adm_const import SADM_XML_TTF_ELN_SE_AT, SADM_XML_FRM_AT_VER, SADM_XML_FRM_AT_VER_OV, ADM_XML_FRM_AT_VER_OV
from adm.adm_const import ADVSS_PROFILE_NAME, TARGET_ADM_VER, TARGET_SADM_VER, ADM_XML_APR_ELN_SE_AV, ADM_XML_AOB_ELN_SE_CO
from adm.adm_const import ADM_XML_AOB_ELN_SE_AV

# Classes ******************************************************************************************************************************************************
from adm.adm_classes import AudioProgramme, AudioContent, AudioObject, AudioBlockFormat, AudioPackFormat, AudioProgrammeLabel
from adm.adm_classes import AudioChannelFormat, AudioTrackFormat, AudioTrackUID, AudioMXFLookUp, AudioStreamFormat
from adm.adm_classes import Objects, DirectSpeakers, HeadphoneRender, LoudnessMetadata, Dialogue, NonDialogueContentKind, DialogueContentKind, MixedContentKind
from adm.adm_classes import AudioObjectInteraction, GainInteractionRange, PositionInteractionRange, Zone, ChannelLock, JumpPosition
from adm.adm_classes import ItemValidationData, Position, Headphone, AudioFormatExtended, AlternativeValueSet, RolledProgramme

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
alternative_value_set_list = []

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
    global alternative_value_set_list

    # Clear out model lists
    del audio_programme_list[:]
    del audio_content_list[:]
    del audio_object_list[:]
    del audio_channel_format_list[:]
    del audio_pack_format_list[:]
    del audio_block_format_list[:]
    del audio_track_uid_list[:]
    del transport_track_format_list[:]
    del alternative_value_set_list[:]

    tree = None

    xml_audio_programme_list = []
    xml_audio_content_list = []
    xml_audio_object_list = []
    xml_audio_channel_format_list = []
    xml_audio_pack_format_list = []
    xml_audio_block_format_list = []
    xml_audio_track_uid_list = []
    xml_transport_track_format_list = []
    xml_alternative_value_set_list = []

    # Is source a blob of XML or an XML file ?
    if mode == ADM_XML_MODE_FILE:
        logging.info('Parsing XML ADM file ') # + xml_struct.name)
        tree = ET.ElementTree(file=xml_struct)
    elif mode == ADM_XML_MODE_STRING:
        logging.info('Parsing XML ADM blob ')
        tree = ET.ElementTree(ET.fromstring(xml_struct))
    tree.getroot()
    root = tree.getroot()

    # Find root of metadata, there are two variants with S-ADM, one with and one without coreMetadata in the structure
    sadm_format_root = root.find(ADM_XML_CM)
    if sadm_format_root is not None:

        adm_format_root = sadm_format_root.find(ADM_XML_FT)
        adm_format_extended_root = adm_format_root.find(ADM_XML_AF)
    else:
        adm_format_extended_root = root.find(ADM_XML_AF)

    sadm_version = None
    adm_version = None
    sadm_advss_profile = False
    adm_advss_profile = False

    # Get S-ADM version
    if SADM_XML_FRM_AT_VER in root.attrib:
        sadm_version = root.attrib[SADM_XML_FRM_AT_VER]
    else:
        sadm_version = SADM_XML_FRM_AT_VER_OV

    sadm_frame_header_root = root.find(SADM_XML_FH)
    # Get profile info
    if sadm_frame_header_root is not None:
        sadm_profile_list = sadm_frame_header_root.find('profileList')
        if sadm_profile_list is not None:
            sadm_profiles_list = sadm_profile_list.findall('profile')
            if sadm_profiles_list is not None:
                # Do we have an AdvSS emission profile entry?
                for i in range(0, len(sadm_profiles_list)):
                    if sadm_profiles_list[i].attrib['profileName'] == ADVSS_PROFILE_NAME:
                        sadm_advss_profile = True
                        break

        # Get profile info and virtual to physical track mapping info
        sadm_transport_track_format = sadm_frame_header_root.find(SADM_XML_TTF_ELN)
        if sadm_transport_track_format is not None:
            xml_transport_track_format_list = sadm_transport_track_format.findall(SADM_XML_TTF_ELN_SE_AT)

    # Get ADM version, see if there is profile information
    if adm_format_extended_root is not None:
        if SADM_XML_FRM_AT_VER in adm_format_extended_root.attrib:
            adm_version = adm_format_extended_root.attrib[SADM_XML_FRM_AT_VER]
            if adm_version == TARGET_ADM_VER:
                adm_profile_list = adm_format_extended_root.find('profileList')
                if adm_profile_list is not None:
                    adm_profiles_list = adm_profile_list.findall('profile')
                    if adm_profiles_list is not None:
                        adm_advss_profile = False
                        # Do we have an AdvSS emission profile entry?
                        for i in range(0, len(adm_profiles_list)):
                            if adm_profiles_list[i].attrib['profileName'] == ADVSS_PROFILE_NAME:
                                adm_advss_profile = True
                                break
        else:
            adm_version = ADM_XML_FRM_AT_VER_OV

        # Get list of programmes
        xml_audio_programme_list = adm_format_extended_root.findall(ADM_XML_APR_ELN)
    else:
        logging.critical('Failed to find ' + ADM_XML_APR_ELN + ' *** Aborting ***')
        return False

    # Save composition details
    composition_details = {'sadm_version': sadm_version, 'adm_version': adm_version,
                           'sadm_advss_profile': sadm_advss_profile, 'adm_advss_profile': adm_advss_profile}

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

            if len(k) > 0:
                for j in range(0, len(k)):
                    audio_programme_list[i].audio_content_idref.append(k[j].text)
            else:
                logging.debug(MSG_INVALID_STUB + ADM_XML_APR_ELN_SE_CR)

            # TODO actually grab loudness metadata and populate
            k = xml_audio_programme_list[i].findall(ADM_XML_APR_ELN_SE_LM)

            # Check limits for element, abort if content is invalid
            if not get_item_limits(ADM_XML_APR_ELN_SE_LM, len(k)):
                return False

            if len(k) > 0:
                for j in range(0, len(k)):
                    audio_programme_list[i].loudness_metadata = LoudnessMetadata()
            else:
                logging.debug(MSG_INVALID_STUB + ADM_XML_APR_ELN_SE_LM)

            # Get any alternative values sets
            k = xml_audio_programme_list[i].findall(ADM_XML_APR_ELN_SE_AV)
            if len(k) > 0:
                for j in range(0, len(k)):
                    audio_programme_list[i].alternative_value_set_idref.append(k[j].text)
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
                    audio_object_list[i].gain['gain_value'] = float(k[j].text)
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

            # For each object get complementary objects
            k = xml_audio_object_list[i].findall(ADM_XML_AOB_ELN_SE_CO)
            if k is not None:
                for j in range(0, len(k)):
                    audio_object_list[i].audio_complementary_object_idref.append(k[j].text)

            # For each object get alternative value sets, for now just gain
            # TODO Add more alternative value parameters
            k = xml_audio_object_list[i].findall(ADM_XML_AOB_ELN_SE_AV)
            if k is not None:
                for j in range(0, len(k)):
                    audio_object_list[i].alternative_value_set.append(k[j].attrib['alternativeValueSetID'])
                    a = k[j].find('gain')
                    if a is not None:
                        alternative_value_set_list.append(({'alternative_value_set_id': k[j].attrib['alternativeValueSetID'] ,
                                                            'gain_value': a.text,
                                                            'gain_unit': a.attrib['gainUnit']}))
                    a = k[j].find('positionOffset')
                    if a is not None:
                        alternative_value_set_list.append(({'alternative_value_set_id': k[j].attrib['alternativeValueSetID'],
                                                            'offset': a.text,
                                                            'coordinate': a.attrib['coordinate']}))
            # TODO audioObjectIDRef
            k = xml_audio_object_list[i].findall('audioObjectIDRef')
            if k is not None:
                for l in range(0, len(k)):

                    audio_object_list[i].audio_object_idref.append(k[j])
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
                if type_label == ADM_XML_INT_TYP_OB:
                    # What coordinate mode is being used
                    a = k[0].find(ADM_XML_ACF_ELN_SE_AB_SE_CT)
                    if a is not None:
                        audio_block_format_list[audio_block_format_counter].cartesian = int(a.text)
                        audio_block_format_list[audio_block_format_counter].position_coord.is_polar = False
                    else:
                        audio_block_format_list[audio_block_format_counter].cartesian = POLAR
                        audio_block_format_list[audio_block_format_counter].position_coord.is_polar = True

                # Get position coordinates and update
                m = k[0].findall(ADM_XML_ACF_ELN_SE_AB_SE_PS)

                # Check limits for element, abort if content is invalid
                if not get_item_limits(ADM_XML_ACF_ELN_SE_AB_SE_PS, len(m)):
                    return False

                for q in range(0, len(m)):
                    if audio_block_format_list[audio_block_format_counter].cartesian == POLAR:
                        if m[q].attrib[ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_CO] == 'azimuth':
                            audio_block_format_list[audio_block_format_counter].position_coord.x_or_az = m[q].text
                        elif m[q].attrib[ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_CO] == 'elevation':
                            audio_block_format_list[audio_block_format_counter].position_coord.y_or_el = m[q].text
                        elif m[q].attrib[ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_CO] == 'distance':
                            audio_block_format_list[audio_block_format_counter].position_coord.z_or_ds = m[q].text
                    elif audio_block_format_list[audio_block_format_counter].cartesian == CARTESIAN:
                        if m[q].attrib[ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_CO] == ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_XC:
                            audio_block_format_list[audio_block_format_counter].position_coord.x_or_az = m[q].text
                        elif m[q].attrib[ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_CO] == ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_YC:
                            audio_block_format_list[audio_block_format_counter].position_coord.y_or_el = m[q].text
                        elif m[q].attrib[ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_CO] == ADM_XML_ACF_ELN_SE_AB_SE_PS_AT_ZC:
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

    # Does composition contain audio programmes that reference complementary group leaders
    programme_has_complementary_leader = []

    for i in range(0, len(audio_programme_list)):
        for j in range(0, len(audio_programme_list[i].audio_content_idref)):
            audio_content_idref = audio_programme_list[i].audio_content_idref[j]
            # Get referenced audio object and see if it contains complementary object references
            for k in range(0, len(audio_content_list)):
                if audio_content_idref == audio_content_list[k].id:
                    for m in range(0, len(audio_content_list[k].audio_object_idref)):
                        audio_object_idref = audio_content_list[k].audio_object_idref[m]
                        for n in range(0, len(audio_object_list)):
                            if audio_object_idref == audio_object_list[n].id:
                                a = len(audio_object_list[n].audio_complementary_object_idref)
                                if a > 0:
                                    programme_has_complementary_leader.\
                                        append({'audio_programme_id': audio_programme_list[i].id,
                                                'object_group_leader': audio_object_list[n].id})

    # Get list of objects that are complementary to the group leader
    object_group_leader_info = []
    for i in range(0, len(programme_has_complementary_leader)):
        for j in range(0, len(audio_object_list)):
            if programme_has_complementary_leader[i]['object_group_leader'] == audio_object_list[j].id:
                object_group_leader_info.append({'audio_programme_id': programme_has_complementary_leader[i]['audio_programme_id'],
                                                'object_group_leader': audio_object_list[j].id,
                                                'complementary_objects': audio_object_list[j].audio_complementary_object_idref})

    # Populate the final model
    mdl_audio_programmes = []
    mdl_audio_content = []
    mdl_audio_object = []
    mdl_audio_pack_fmt = []
    mdl_audio_channel_fmt = []
    mdl_audio_block_fmt = []
    mdl_audio_track_uid = []

    # TODO audio pack ref in object for common defs, insert common def bed into audio channel format
    # Start populating audio programmes
    for i in range(0, len(audio_programme_list)):
        mdl_audio_programmes.append(AudioProgramme(audio_programme_list[i].name, audio_programme_list[i].language, audio_programme_list[i].id))
        mdl_audio_programmes[i].loudness_metadata = audio_programme_list[i].loudness_metadata
        mdl_audio_programmes[i].audio_programme_label = audio_programme_list[i].audio_programme_label
        for j in range(0, len(object_group_leader_info)):
            if mdl_audio_programmes[i].id == object_group_leader_info[j]['audio_programme_id']:
                mdl_audio_programmes[i].needs_unrolling = True

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
        mdl_audio_channel_fmt[i].audio_block = find_list_reference_by_id(mdl_audio_block_fmt, search)

    # Update audio pack with audio channel
    for i in range(0, len(mdl_audio_pack_fmt)):
        for j in range(0, len(audio_pack_format_list[i].audio_channel_idref)):
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
                break

        for j in range(0, len(xml_transport_track_format_list)):
            q = xml_transport_track_format_list[j].findall(SADM_XML_TTF_ELN_SE_AT_SE_AR)
            if q is not None:
                for k in range(0, len(q)):
                    if q[k].text.lower() == audio_track_uid_list[i].id.lower():
                        mdl_audio_track_uid[i].track_id = xml_transport_track_format_list[j].attrib[SADM_XML_TTF_ELN_SE_AT_AT_TI]
                        break

    # Update audio object with gain, audio_pack_idref, audio_track_uidref
    for i in range(0, len(mdl_audio_object)):
        # Gain
        for j in range(0, len(audio_object_list)):
            if mdl_audio_object[i].id == audio_object_list[j].id:
                mdl_audio_object[i].gain['gain_value'] = audio_object_list[j].gain['gain_value']
                break

        # Audio pack
        for j in range(0, len(audio_object_list)):
            if mdl_audio_object[i].id == audio_object_list[j].id:
                # TODO Proper common definitions
                # Is this a nested object?
                if len(audio_object_list[j].audio_pack_idref) > 0:
                    if int(audio_object_list[j].audio_pack_idref[0][7:8]) == 0:
                        mdl_audio_object[i].audio_pack_idref = audio_object_list[j].audio_pack_idref[0]
                    else:
                        mdl_audio_object[i].audio_pack_idref.append(find_list_reference_by_id(mdl_audio_pack_fmt, audio_object_list[j].audio_pack_idref[0]))
                    break

        # Nested audio objects
        for j in range(0, len(audio_object_list)):
            if mdl_audio_object[i].id == audio_object_list[j].id:
                # Is this a nested object?
                if len(audio_object_list[j].audio_object_idref) > 0:
                    for k in range(len(audio_object_list[j].audio_object_idref)):
                        mdl_audio_object[i].audio_object_idref.append(audio_object_list[j].audio_object_idref[k])

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
    # Update audio programmes with alternative value sets
    for i in range(0, len(mdl_audio_programmes)):
        for j in range(0, len(audio_programme_list)):
            if mdl_audio_programmes[i].id == audio_programme_list[j].id:

                for k in range(0, len(audio_programme_list[j].alternative_value_set_idref)):
                    mdl_audio_programmes[i].alternative_value_set_idref.append(audio_programme_list[j].alternative_value_set_idref[k])

    # Update audio objects that are complimentary group leaders
    for i in range(0, len(mdl_audio_object)):
        for j in range(0, len(object_group_leader_info)):
            if mdl_audio_object[i].id == object_group_leader_info[j]['object_group_leader']:
                #mdl_audio_object[i].audio_complementary_object_idref = object_group_leader_info[j]['complementary_objects']
                for k in range(0, len(object_group_leader_info[j]['complementary_objects'])):
                    #b = find_list_reference_by_id(mdl_audio_object, object_group_leader_info[j]['complementary_objects'][k])
                    if find_list_reference_by_id(mdl_audio_object, object_group_leader_info[j]['complementary_objects']
                    [k]) not in mdl_audio_object[i].audio_complementary_object_idref:
                        mdl_audio_object[i].audio_complementary_object_idref.append\
                            (find_list_reference_by_id(mdl_audio_object,object_group_leader_info[j]['complementary_objects'][k]))

    # Update audio objects that contain alternative value sets
    for i in range(0, len(mdl_audio_object)):
        for j in range(0, len(alternative_value_set_list)):
            a = mdl_audio_object[i].id[3:]
            b = alternative_value_set_list[j]['alternative_value_set_id'][4:8]
            if a == b:
                mdl_audio_object[i].alternative_value_set.append(alternative_value_set_list[j])

    # Package all the data together into a audio format extended container
    a = AudioFormatExtended()
    a.composition_details = composition_details
    a.audio_programme = mdl_audio_programmes
    a.audio_content = mdl_audio_content
    a.audio_object = mdl_audio_object
    a.audio_pack_format = mdl_audio_pack_fmt
    a.audio_channel_format = mdl_audio_channel_fmt
    a.audio_track_uid = mdl_audio_track_uid

    return a


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
            #my_metadata = parse_adm_xml("skip.sadm.advss.xml", ADM_XML_MODE_FILE)
            #my_metadata = parse_adm_xml("dtm_axml_v2_sadm.xml", ADM_XML_MODE_FILE)
            #my_metadata = parse_adm_xml("eac_axml_v2_sadm.xml", ADM_XML_MODE_FILE)
            #my_metadata = parse_adm_xml("skip.sadm.emission.profile.compliant_v2.xml", ADM_XML_MODE_FILE)
            my_metadata = parse_adm_xml("complimentary_objects_v2.xml", ADM_XML_MODE_FILE)

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

