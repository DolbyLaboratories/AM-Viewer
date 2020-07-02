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
# """
#
# # ************************************************************************************************************************************************************ #
# # ************************************************************************************************************************************************************ #
#
# # Consts
from pmd.pmd_const import LOUDSPEAKER_CONFIG_HORIZONTAL_SPEAKER_OUTPUT_TARGETS, OBJECT_CLASSES

from pmd.pmd_const import MIN_MAX_AZIMUTH, MIN_MAX_ELEVATION, MIN_MAX_DISTANCE
from pmd.pmd_const import MIN_MAX_XPOS, MIN_MAX_YPOS, MIN_MAX_ZPOS
from pmd.pmd_const import MIN_SIZE, MAX_SIZE
from pmd.pmd_const import MIN_SOURCE_GAIN_DB
from pmd.pmd_const import MAX_SOURCE_GAIN_DB

from pmd.pmd_const import POLAR, CARTESIAN

from pmd.pmd_const import LOUDSPEAKER_CONFIG_HORIZONTAL_CHANNEL_MASK
from pmd.pmd_const import LOUDSPEAKER_CONFIG_VERTICAL_CHANNEL_MASK
from pmd.pmd_const import LOUDSPEAKER_CONFIG_HORIZONTAL_SPEAKER_OUTPUT_TARGETS
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_LFE_INDEX_VALUE
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_POST_INDEX_VALUE
from pmd.pmd_const import LOUDSPEAKER_CONFIG_VERTICAL_SPEAKER_OUTPUT_TARGETS
from pmd.pmd_const import LOUDSPEAKER_CONFIG_VERTICAL_SPEAKER_POST_OUTPUT_TARGETS
from pmd.pmd_const import LOUDSPEAKER_CONFIG_VERTICAL_CHANNEL_MIN

from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_RANGE_START
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_2_0
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_3_0
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_5_0
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_5_1
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_5_0_2
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_5_1_2
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_5_0_4
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_5_1_4
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_7_0_4
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_7_1_4
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_9_0_6
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_9_1_6
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_RANGE_END

from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_NAMES
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_EQUIV

from pmd.pmd_const import PRESENTATION_CONFIG_TEXT
from pmd.pmd_const import PRESENTATION_CONFIG_EQUIV
from pmd.pmd_const import PRESENTATION_CONFIG_2_0
from pmd.pmd_const import PRESENTATION_CONFIG_3_0
from pmd.pmd_const import PRESENTATION_CONFIG_5_1
from pmd.pmd_const import PRESENTATION_CONFIG_5_1_2
from pmd.pmd_const import PRESENTATION_CONFIG_5_1_4
from pmd.pmd_const import PRESENTATION_CONFIG_7_1_4
from pmd.pmd_const import PRESENTATION_CONFIG_9_1_6

from pmd.pmd_const import MIN_AUDIO_SIGNAL, MAX_AUDIO_SIGNAL
from pmd.pmd_const import DIALOGUE, VDS, VOICEOVER, GENERIC, SPOKEN_SUBTITLE, EMERGENCY_ALERT, EMERGENCY_INFORMATION
from pmd.pmd_const import AUDIO_SIGNAL_STR
from pmd.pmd_const import PMD_LOG_FILE

from pmd.pmd_const import PMD_XML_AUDIO_SIGNALS_LEVEL
from pmd.pmd_const import PMD_XML_AUDIO_ELEMENTS_LEVEL
from pmd.pmd_const import PMD_XML_AUDIO_PRESENTATION_LEVEL
from pmd.pmd_const import PMD_XML_AUDIO_IAT_LEVEL

from pmd.pmd_const import PMD_XML_AUDIO_OBJECT_NAME
from pmd.pmd_const import PMD_XML_AUDIO_OBJECT_CLASS
from pmd.pmd_const import PMD_XML_AUDIO_OBJECT_DYNAMIC_UPDATES
from pmd.pmd_const import PMD_XML_AUDIO_OBJECT_XPOS
from pmd.pmd_const import PMD_XML_AUDIO_OBJECT_YPOS
from pmd.pmd_const import PMD_XML_AUDIO_OBJECT_ZPOS
from pmd.pmd_const import PMD_XML_AUDIO_OBJECT_SIZE
from pmd.pmd_const import PMD_XML_AUDIO_OBJECT_SIZE_3D
from pmd.pmd_const import PMD_XML_AUDIO_OBJECT_DIVERGE
from pmd.pmd_const import PMD_XML_AUDIO_OBJECT_AUDIO_SIGNAL
from pmd.pmd_const import PMD_XML_AUDIO_OBJECT_SOURCE_GAIN_DB

from pmd.pmd_const import PMD_XML_MODE_FILE
from pmd.pmd_const import PMD_XML_MODE_STRING
from pmd.pmd_const import PMD_XML_INDENT
from pmd.pmd_const import PMD_XML_ATTRIB_ID
from pmd.pmd_const import PMD_XML_ROOT
from pmd.pmd_const import PMD_XML_ROOT_CMT

from pmd.pmd_const import PMD_XML_ROOT_SE_CONTAINER
from pmd.pmd_const import PMD_XML_ROOT_SE_CONTAINER_SE_SMP_OST
from pmd.pmd_const import PMD_XML_ROOT_SE_CONTAINER_SUB_E_D_TAGS
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_AT_VER
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_AT_VER_VAL
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_TTL

from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_ASG
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_ASG_SE_ASG
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_ASG_SE_ASG_AID
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_ASG_SE_ASG_NME

from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_NME
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_CFG
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG_SE_ASG
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG_SE_ASG_SE_IDS
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG_SE_ASG_SE_GAN

from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_NME
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_CLS
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_DUP
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_CLS
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_XPS
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_YPS
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_ZPS
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_SIZ
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_S3D
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_DVG
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_ASG
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_SGD

from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_APR
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_APR_AT_LNG
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_APR_SE_APR
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_APR_SE_NME
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_APR_SE_LNG
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_APR_SE_CFG
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_APR_SE_EMT

from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_IAT
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_IAT_SE_CID
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_IAT_SE_UUI
from pmd.pmd_const import PMD_XML_ROOT_SE_PMD_SE_IAT_SE_TST

# Classes
from pmd.pmd_classes import ProfessionalMetadata, AudioPresentation, AudioBed, AudioObject, AudioSignal, OutputTarget, IaT, PresentationNameLanguage

# External system
import logging
import uuid
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import tracemalloc

# ADM bits and pieces



from adm.adm_tool import parse_adm_xml
from adm.adm_const import ADM_XML_MODE_FILE, ADM_XML_INT_TYP_DS, ADM_XML_INT_TYP_OB
from adm.adm_const import NON_DIALOGUE_CONTENT, DIALOGUE_CONTENT, MIXED_CONTENT

from adm.adm_const import ADM_NON_DIALOGUE_CONTENT_KIND, ADM_DIALOGUE_CONTENT_KIND, ADM_MIXED_CONTENT_KIND
from adm.adm_const import ADM_DIALOGUE_CONTENT_KIND_UNDEFINED, ADM_DIALOGUE_CONTENT_KIND_DIALOGUE, ADM_DIALOGUE_CONTENT_KIND_VOICEOVER
from adm.adm_const import ADM_DIALOGUE_CONTENT_KIND_SPOKEN_SUBTITLE, ADM_DIALOGUE_CONTENT_KIND_AUDIO_DESCRIPTION, ADM_DIALOGUE_CONTENT_KIND_COMMENTARY
from adm.adm_const import ADM_DIALOGUE_CONTENT_KIND_EMERGENCY


# Globals to keep track of ID allocation, lists etc.

professional_metadata_list = []
audio_presentation_list = []
audio_element_list = []
audio_object_list = []
audio_bed_list = []
audio_signal_list = []
iat_list = []

audio_presentation_counter = 0
audio_element_counter = 0
audio_object_counter = 0
audio_bed_counter = 0
audio_signal_counter = 0

#xml_audio_object_counter = 0
#xml_audio_bed_counter = 0
#xml_audio_signal_counter = 0
#xml_audio_element_counter = 0
#xml_audio_presentation_counter = 0

coordinate_mode = CARTESIAN

# ************************************************************************************************************************************************************ #
# ************************************************************************************************************************************************************ #


def str2bool(v):
    return v.lower() in ('yes', 'true', 't', '1')


def check_parameter_type(parameter, expected_type, calling_function):
    if type(parameter) is not expected_type:
        logging.debug(str(type(parameter)) + ' value of ' + str(parameter) + ' is not the expected data type of ' + str(
            expected_type) + ' in ' + str(calling_function))
        return False
    return True


def check_parameter_value_range(parameter, min_value, max_value, calling_function):
    if parameter < min_value or parameter > max_value:
        logging.debug(str(type(parameter)) + ' value of ' + str(parameter) + ' is out of min/max range of ' + str(
            min_value) + ' to ' + str(max_value) + ' in ' + str(calling_function))
    return


def check_positional_coordinates_in_range(azimuth_or_x, elevation_or_y, distance_or_z, calling_function):
    global coordinate_mode
    azimuth_or_x_range = 0
    elevation_or_y_range = 0
    distance_or_z_range = 0

    if coordinate_mode == POLAR:
        azimuth_or_x_range = MIN_MAX_AZIMUTH
        elevation_or_y_range = MIN_MAX_ELEVATION
        distance_or_z_range = MIN_MAX_DISTANCE
    elif coordinate_mode == CARTESIAN:
        azimuth_or_x_range = MIN_MAX_XPOS
        elevation_or_y_range = MIN_MAX_YPOS
        distance_or_z_range = MIN_MAX_ZPOS

    if abs(azimuth_or_x) > azimuth_or_x_range:
        logging.debug(str(type(azimuth_or_x)) + ' value of ' + str(azimuth_or_x) + ' is out of min/max range of ' + str(
            azimuth_or_x_range) + ' in ' + str(calling_function))

    if abs(elevation_or_y) > elevation_or_y_range:
        logging.debug(str(type(elevation_or_y)) + ' value of ' + str(elevation_or_y) + ' is out of min/max range of ' + str(
            elevation_or_y_range) + ' in ' + str(calling_function))

    if abs(distance_or_z) > distance_or_z_range:
        logging.debug(str(type(distance_or_z)) + ' value of ' + str(distance_or_z) + ' is out of min/max range of ' + str(
            distance_or_z_range) + ' in ' + str(calling_function))
    return


def create_object(name, classification, dynamic_updates, azimuth_or_x, elevation_or_y, distance_or_z,
                  size, size_3d, diverge, audio_signal, source_gain_db, original_id=0):
    global audio_element_counter, audio_object_counter, audio_signal_counter, audio_signal_list, audio_object_list, audio_element_list

    # Check parameter types
    check_parameter_type(name, str, create_object)
    check_parameter_type(classification, int, create_object)
    check_parameter_type(dynamic_updates, bool, create_object)
    check_parameter_type(azimuth_or_x, float, create_object)
    check_parameter_type(elevation_or_y, float, create_object)
    check_parameter_type(distance_or_z, float, create_object)
    check_parameter_type(size, float, create_object)
    check_parameter_type(size_3d, bool, create_object)
    check_parameter_type(diverge, bool, create_object)
    check_parameter_type(audio_signal, int, create_object)
    check_parameter_type(source_gain_db, float, create_object)

    # Range check parameters
    check_parameter_value_range(size, MIN_SIZE, MAX_SIZE, create_object)
    check_parameter_value_range(audio_signal, MIN_AUDIO_SIGNAL, MAX_AUDIO_SIGNAL, create_object)
    check_parameter_value_range(source_gain_db, MIN_SOURCE_GAIN_DB, MAX_SOURCE_GAIN_DB, create_object)
    check_positional_coordinates_in_range(azimuth_or_x, elevation_or_y, distance_or_z, create_object)

    # Add AudioSignal entry to audio_signal_list if it doesn't already exist, if exists save index for later
    ok_to_add = True
    replacement_counter = 0
    for i in range(0, len(audio_signal_list)):
        if audio_signal == audio_signal_list[i].id:
            ok_to_add = False
            replacement_counter = i
            break

    if ok_to_add:
        audio_signal_list.append(AudioSignal(audio_signal, AUDIO_SIGNAL_STR + str(audio_signal)))

    # Create new audio object, add to object list
    if original_id > 0:
        audio_object_list.append(AudioObject(original_id))
    else:
        audio_object_list.append(AudioObject(audio_element_counter + 1))

    audio_object_list[audio_object_counter].update_name(name)
    audio_object_list[audio_object_counter].update_classification(classification)
    audio_object_list[audio_object_counter].update_dynamic_updates(dynamic_updates)
    audio_object_list[audio_object_counter].update_coordinates(azimuth_or_x, elevation_or_y, distance_or_z)
    audio_object_list[audio_object_counter].update_size(size)
    audio_object_list[audio_object_counter].update_size_3d(size_3d)
    audio_object_list[audio_object_counter].update_diverge(diverge)
    audio_object_list[audio_object_counter].update_source_gain_db(source_gain_db)

    # Add a reference to the audio signal, if we created a new one above then also inc the audio_signal_counter
    if ok_to_add:
        audio_object_list[audio_object_counter].update_audio_signal(audio_signal_list[audio_signal_counter])
        audio_signal_counter += 1
    else:
        audio_object_list[audio_object_counter].update_audio_signal(audio_signal_list[replacement_counter])

    # Create audio object reference in audio element list
    audio_element_list.append(audio_object_list[audio_object_counter])

    audio_element_counter += 1
    audio_object_counter += 1
    return audio_object_list


def create_audio_bed(obj_name, loudspeaker_configuration, start_audio_signal, original_id=0, gain_db=0.0):
    global audio_element_counter, audio_bed_counter, audio_signal_counter, audio_bed_list, audio_element_list
    # TODO add support for output targets to have more than one audio signal i.e. support beyond direct beds

    # Check parameter types
    check_parameter_type(obj_name, str, create_audio_bed)
    check_parameter_type(loudspeaker_configuration, int, create_audio_bed)
    check_parameter_type(start_audio_signal, int, create_audio_bed)

    # Range check parameters
    check_parameter_value_range(start_audio_signal, MIN_AUDIO_SIGNAL, MAX_AUDIO_SIGNAL, create_audio_bed)

    # Figure the number of channels present for each speaker plane
    horizontal_channel_count = loudspeaker_configuration & LOUDSPEAKER_CONFIG_HORIZONTAL_CHANNEL_MASK
    vertical_channel_count = (loudspeaker_configuration & LOUDSPEAKER_CONFIG_VERTICAL_CHANNEL_MASK) / 0x10

    # Get text version of speaker_config
    for i in range(0, len(LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_EQUIV)):
        if loudspeaker_configuration == LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_EQUIV[i]:
            break

    # Create audio bed reference in audio bed list. If reading from XML then optional original_id param should be non zero
    if original_id > 0:
        audio_bed_list.append(AudioBed(original_id, obj_name, LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_NAMES[i], gain_db))
    else:
        audio_bed_list.append(AudioBed(audio_element_counter + 1, obj_name, LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_NAMES[i], gain_db))

    # Create audio bed reference in audio element list
    audio_element_list.append(audio_bed_list[audio_bed_counter])

    # Add AudioSignal entries to audio_signal_list
    i = 0
    while i < horizontal_channel_count:
        skip_lfe = 0
        if horizontal_channel_count % 2 != 0:
            # Reached the LFE index value yet ?, if so bump offset by one in the label and positional lists (a 5.x.2 use case)
            if i >= LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_LFE_INDEX_VALUE:
                skip_lfe = 1

        # Add AudioSignal entry to audio_signal_list if it doesn't already exist, current support is for direct audio beds only
        ok_to_add = True
        replacement_counter = 0
        for j in range(0, len(audio_signal_list)):
            if (start_audio_signal + i) == audio_signal_list[j].id:
                ok_to_add = False
                replacement_counter = j
                break

        if ok_to_add:
            audio_signal_list.append(AudioSignal(start_audio_signal + i, AUDIO_SIGNAL_STR + str(start_audio_signal + i)))

        # Setup the output speaker targets that signals are routed to
        audio_bed_list[audio_bed_counter].output_targets.append(OutputTarget(LOUDSPEAKER_CONFIG_HORIZONTAL_SPEAKER_OUTPUT_TARGETS[i + skip_lfe]))

        # Add entry for the source audio signal, need logic if we are reusing a signal
        if ok_to_add:
            audio_bed_list[audio_bed_counter].output_targets[i].audio_signals.append(audio_signal_list[audio_signal_counter])
            audio_signal_counter += 1
        else:
            audio_bed_list[audio_bed_counter].output_targets[i].audio_signals.append(audio_signal_list[replacement_counter])
        i += 1

    i = 0
    while i < vertical_channel_count:
        skip_middle = LOUDSPEAKER_CONFIG_VERTICAL_CHANNEL_MIN

        # Add AudioSignal entry to audio_signal_list if it doesn't already exist
        ok_to_add = True
        replacement_counter = 0
        for j in range(0, len(audio_signal_list)):
            if (start_audio_signal + horizontal_channel_count + i) == audio_signal_list[j].id:
                ok_to_add = False
                replacement_counter = j
                break

        if ok_to_add:
            audio_signal_list.append(AudioSignal(start_audio_signal + horizontal_channel_count + i, AUDIO_SIGNAL_STR + str(
                start_audio_signal + i + horizontal_channel_count)))

        # Is loudspeaker_configuration smaller than 9.x.6 ? (reorder vertical speaker channels ?)
        if horizontal_channel_count < LOUDSPEAKER_CONFIG_COMMON_USE_HORIZONTAL_SPEAKER_POST_INDEX_VALUE:
            # Does loudspeaker_configuration have more than two vertical speakers ?
            if vertical_channel_count == LOUDSPEAKER_CONFIG_VERTICAL_CHANNEL_MIN:
                skip_middle = 0

            # Setup the output speaker targets that signals are routed to
            audio_bed_list[audio_bed_counter].output_targets.append(OutputTarget(LOUDSPEAKER_CONFIG_VERTICAL_SPEAKER_OUTPUT_TARGETS[i + skip_middle]))

            # Add entry for the source audio signal
            if ok_to_add:
                audio_bed_list[audio_bed_counter].output_targets[horizontal_channel_count + i].audio_signals.append(audio_signal_list[audio_signal_counter])
            else:
                audio_bed_list[audio_bed_counter].output_targets[horizontal_channel_count + i].audio_signals.append(audio_signal_list[replacement_counter])
        else:
            # Setup the output speaker targets that signals are routed to
            audio_bed_list[audio_bed_counter].output_targets.append(OutputTarget(LOUDSPEAKER_CONFIG_VERTICAL_SPEAKER_POST_OUTPUT_TARGETS[i]))

            # Add entry for the source audio signal
            audio_bed_list[audio_bed_counter].output_targets[horizontal_channel_count + i].audio_signals.append(audio_signal_list[audio_signal_counter])

        if ok_to_add:
            audio_signal_counter += 1
        i += 1

    audio_element_counter += 1
    audio_bed_counter += 1
    return audio_bed_list


def create_audio_presentation(internal_name, language, presentation_config, element_id_list, original_id=0):
    global audio_presentation_counter, audio_presentation_list, audio_element_list

    # Check incoming parameter data types
    check_parameter_type(internal_name, str, create_audio_presentation)
    check_parameter_type(language, str, create_audio_presentation)
    check_parameter_type(presentation_config, int, create_audio_presentation)
    check_parameter_type(element_id_list, list, create_audio_presentation)

    if original_id > 0:
        # audio_object_list.append(AudioObject(original_id))
        audio_presentation_list.append(AudioPresentation(internal_name, language, original_id))
    else:
        # audio_object_list.append(AudioObject(audio_element_counter + 1))
        audio_presentation_list.append(AudioPresentation(internal_name, language, audio_presentation_counter + 1))

    # Set presentation config
    presentation_config_text_idx = 0
    if presentation_config == LOUDSPEAKER_CONFIG_COMMON_USE_2_0:
        presentation_config_text_idx = 0
    elif presentation_config == LOUDSPEAKER_CONFIG_COMMON_USE_3_0:
        presentation_config_text_idx = 1
    elif presentation_config == LOUDSPEAKER_CONFIG_COMMON_USE_5_0 or presentation_config == LOUDSPEAKER_CONFIG_COMMON_USE_5_1:
        presentation_config_text_idx = 2
    elif presentation_config == LOUDSPEAKER_CONFIG_COMMON_USE_5_0_2 or presentation_config == LOUDSPEAKER_CONFIG_COMMON_USE_5_1_2:
        presentation_config_text_idx = 3
    elif presentation_config == LOUDSPEAKER_CONFIG_COMMON_USE_5_0_4 or presentation_config == LOUDSPEAKER_CONFIG_COMMON_USE_5_1_4:
        presentation_config_text_idx = 4
    elif presentation_config == LOUDSPEAKER_CONFIG_COMMON_USE_7_0_4 or presentation_config == LOUDSPEAKER_CONFIG_COMMON_USE_7_1_4:
        presentation_config_text_idx = 5
    elif presentation_config == LOUDSPEAKER_CONFIG_COMMON_USE_9_0_6 or presentation_config == LOUDSPEAKER_CONFIG_COMMON_USE_9_1_6:
        presentation_config_text_idx = 6
    audio_presentation_list[audio_presentation_counter].config = PRESENTATION_CONFIG_TEXT[presentation_config_text_idx]

    for i in range(0, len(element_id_list)):
        k = find_list_reference_by_id(audio_element_list, element_id_list[i])
        if k is not None:
            audio_presentation_list[audio_presentation_counter].elements.append(k)

    audio_presentation_counter += 1
    return


def add_audio_presentation_names(presentation_ref, name_language_code_list):
    # Check incoming parameter data types
    check_parameter_type(name_language_code_list, list, add_audio_presentation_names)

    for i in range(0, len(name_language_code_list)):
        presentation_ref.add_local_language_name(name_language_code_list[i].text, name_language_code_list[i].attrib[PMD_XML_ROOT_SE_PMD_SE_APR_AT_LNG])
    return


def add_audio_presentation_names_by_name(presentation_ref, name_language_code_list):
    # Check incoming parameter data types
    check_parameter_type(name_language_code_list, list, add_audio_presentation_names)

    for i in range(0, len(name_language_code_list), 2):
        presentation_ref.add_local_language_name(name_language_code_list[i], name_language_code_list[i + 1])
    return


def xml_add_audio_presentation_names(xml_audio_presentation_ref, name_language_code_list):
    # Check incoming parameter data types
    check_parameter_type(name_language_code_list, list, xml_add_audio_presentation_names)

    for i in range(0, len(name_language_code_list)):
        xml_audio_presentation_ref.add_local_language_name(name_language_code_list[i].name, name_language_code_list[i].language)
    return


def xml_add_audio_element_list(xml_audio_presentation_ref, elements_list):
    for i in range(0, len(elements_list)):
        xml_audio_presentation_ref.elements.append(elements_list[i])
    return


def parse_pmd_xml(xml_struct, mode):
    xml_audio_element_list = []

    # Is source a blob of XML or an XML file ?
    if mode == PMD_XML_MODE_FILE:
        tree = ET.ElementTree(file=xml_struct)
    elif mode == PMD_XML_MODE_STRING:
        tree = ET.ElementTree(ET.fromstring(xml_struct))

    tree.getroot()
    root = tree.getroot()

    # Find root of metadata
    pmd_root = root.find(PMD_XML_ROOT_SE_PMD)
    audio_signal_root = pmd_root.find(PMD_XML_ROOT_SE_PMD_SE_ASG)
    if audio_signal_root is not None:
        xml_audio_signal_list = audio_signal_root.findall(PMD_XML_ROOT_SE_PMD_SE_ASG_SE_ASG)

    # Find all audio elements, depending upon type, put into correct list, then create references in xml_audio_element_list
    audio_element_root = pmd_root.find(PMD_XML_ROOT_SE_PMD_SE_AEL)
    if audio_element_root is not None:
        xml_audio_bed_list = audio_element_root.findall(PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB)
        xml_audio_object_list = audio_element_root.findall(PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO)
        # Audio beds
        for i in range(0, len(xml_audio_bed_list)):
            xml_audio_element_list.append(xml_audio_bed_list[i])
        # Audio objects
        for i in range(0, len(xml_audio_object_list)):
            xml_audio_element_list.append(xml_audio_object_list[i])

    # Find all audio presentations
    audio_presentation_root = pmd_root.find(PMD_XML_ROOT_SE_PMD_SE_APR)
    if audio_presentation_root is not None:
        xml_audio_presentation_list = audio_presentation_root.findall(PMD_XML_ROOT_SE_PMD_SE_APR_SE_APR)

    # Find all IAT entries (should only be one) TODO expand to support more than content_id = uuid and timestamp
    iat_root = pmd_root.find(PMD_XML_ROOT_SE_PMD_SE_IAT)
    if iat_root is not None:
        xml_iat_content_id_list = iat_root.findall(PMD_XML_ROOT_SE_PMD_SE_IAT_SE_CID)
        xml_iat_timestamp_list = iat_root.findall(PMD_XML_ROOT_SE_PMD_SE_IAT_SE_TST)
    else:
        xml_iat_content_id_list = []
        xml_iat_timestamp_list = []

    return populate_model_from_xml(xml_audio_signal_list, xml_audio_bed_list, xml_audio_object_list,
                                   xml_audio_presentation_list, xml_iat_content_id_list, xml_iat_timestamp_list)


def populate_model_from_xml(xml_signals, xml_beds, xml_objects, xml_presentations, xml_iat_cid, xml_iat_time):
    # Primary call from an external process
    # TODO Need to fix for use cases where there is more than 1 bed (issues with second bed audio signals being assigned to output targets)

    global audio_signal_list, audio_presentation_list, audio_bed_list, audio_object_list, audio_element_list, iat_list
    global audio_presentation_counter, audio_object_counter, audio_bed_counter

    # Clear out lists (delete works on all python versions)
    del audio_signal_list[:]
    del audio_presentation_list[:]
    del audio_bed_list[:]
    del audio_object_list[:]
    del audio_element_list[:]
    del iat_list[:]

    # Zero counters
    audio_presentation_counter = 0
    audio_object_counter = 0
    audio_bed_counter = 0

    # Audio signals
    # Create entry in audio_signal_list
    for i in range(0, len(xml_signals)):
        f = int(xml_signals[i].attrib[PMD_XML_ATTRIB_ID])
        audio_signal_list.append(AudioSignal(f, get_element_text(xml_signals[i], PMD_XML_ROOT_SE_PMD_SE_ASG_SE_ASG_NME)))
    i = 0
    while i < len(xml_beds):
        # TODO add support for output targets to have more than one audio signal + gain attribute, i.e. support beyond direct beds
        # Get equivalent speaker config value
        config = get_element_text(xml_beds[i], PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_CFG)
        speaker_config = 0
        for j in range(0, len(LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_NAMES)):
            if config == LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_NAMES[j]:
                speaker_config = LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_EQUIV[j]
                break

        # Figure the bed start_channel (it will be first audio signal id for first output target)
        output_targets = xml_beds[i].find(PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG)
        output_target = output_targets.findall(PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG)
        left_channel = output_target[0]
        first_signal = left_channel.find(PMD_XML_ROOT_SE_PMD_SE_ASG)
        first_audio_signal_id = first_signal.find(PMD_XML_ROOT_SE_PMD_SE_ASG_SE_ASG_AID)

        if PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG_SE_ASG_SE_GAN in first_audio_signal_id.attrib:
            gain_db = float(first_audio_signal_id.attrib[PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG_SE_ASG_SE_GAN][:-2])
        else:
            gain_db = 0.0

            # create_audio_bed(obj_name, loudspeaker_configuration, start_audio_signal, original_id=0):
        create_audio_bed(get_element_text(xml_beds[i], PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_NME),
                         speaker_config, int(first_audio_signal_id.text),
                         int(xml_beds[i].attrib[PMD_XML_ATTRIB_ID]), gain_db)
        i += 1



    # Audio objects
    for i in range(0, len(xml_objects)):
        # Convert class text in xml into index value for model
        classification = 0
        for j in range(0, len(OBJECT_CLASSES)):
            if OBJECT_CLASSES[j] == get_element_text(xml_objects[i], PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_CLS):
                classification = j
                break

        create_object(get_element_text(xml_objects[i], PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_NME), classification,
                      str2bool(get_element_text(xml_objects[i], PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_DUP)),
                      float(get_element_text(xml_objects[i], PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_XPS)),
                      float(get_element_text(xml_objects[i], PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_YPS)),
                      float(get_element_text(xml_objects[i], PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_ZPS)),
                      float(get_element_text(xml_objects[i], PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_SIZ)),
                      str2bool(get_element_text(xml_objects[i], PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_S3D)),
                      str2bool(get_element_text(xml_objects[i], PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_DVG)),
                      int(get_element_text(xml_objects[i], PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_ASG)),
                      float(get_element_text(xml_objects[i], PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_SGD)[:-2]),
                      int(xml_objects[i].attrib[PMD_XML_ATTRIB_ID]))

    # Audio presentations
    i = 0
    while i < len(xml_presentations):
        # Get equivalent speaker config value
        a = get_element_text(xml_presentations[i], PMD_XML_ROOT_SE_PMD_SE_APR_SE_CFG)
        b = get_element_text(xml_presentations[i], PMD_XML_ROOT_SE_PMD_SE_APR_SE_CFG).find(" ")
        if b > 0:
            config_part = a[0:b]
        else:
            config_part = a[:]

        # Find corresponding speaker_config value
        speaker_config = 0
        for j in range(0, len(LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_NAMES)):
            if config_part == LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_NAMES[j]:
                speaker_config = LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_EQUIV[j]
                break

        # Find required elements by id and populate id list for create presentation call
        element_id_list = []
        element_xml_list = xml_presentations[i].findall(PMD_XML_ROOT_SE_PMD_SE_APR_SE_EMT)
        for j in range(0, len(element_xml_list)):
            k = find_list_reference_by_id(audio_element_list, int(element_xml_list[j].text))
            if k is not None:
                element_id_list.append(k.id)

        create_audio_presentation(get_element_text(xml_presentations[i], PMD_XML_ROOT_SE_PMD_SE_APR_SE_NME),
                                  get_element_text(xml_presentations[i], PMD_XML_ROOT_SE_PMD_SE_APR_SE_LNG),
                                  speaker_config, element_id_list, int(xml_presentations[i].attrib['id']))

        # Find presentation name
        language_names_list = xml_presentations[i].findall(PMD_XML_ROOT_SE_PMD_SE_APR_SE_NME)

        # Update presentation names
        add_audio_presentation_names(audio_presentation_list[i], language_names_list)
        i += 1

    # IAT, there should only be one IAT payload in the list, add error checking for this
    if len(xml_iat_cid) > 0 and len(xml_iat_time) > 0:
    	iat_list.append(IaT(get_element_text(xml_iat_cid[0], PMD_XML_ROOT_SE_PMD_SE_IAT_SE_UUI), int(xml_iat_time[0].text)))

    # Package all the data together into a professional metadata container
    k = ProfessionalMetadata(PMD_XML_ROOT_SE_PMD_AT_VER_VAL)
    k.audio_signals = audio_signal_list
    k.audio_elements = audio_element_list
    k.audio_presentations = audio_presentation_list
    k.iat = iat_list
    return k


def get_element_text(element_ref, element_name):
    if len(element_ref.findall(element_name)) > 0:
        return element_ref.find(element_name).text
    return ''


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


def find_list_reference_by_tag(list_to_search, tag):
    for i in range(0, len(list_to_search)):
        if list_to_search[i].tag == tag:
            return list_to_search[i]
    return None


def prettify_xml(elem):
    # This cleans up output from element tree (xml doesn't have indents, new lines, ugly), uses inbuilt minidom lib
    # Google's XML style guide states 2 space indents for sub element nesting
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent=PMD_XML_INDENT)


def write_pmd_xml(xml_file):
    # Reorder audio signals list (if need be, it looks nicer) so that id values are ascending
    audio_signal_list.sort(key=lambda x: x.id, reverse=False)

    root = ET.Element(PMD_XML_ROOT)
    root.append(ET.Comment(PMD_XML_ROOT_CMT))

    container_config = ET.SubElement(root, PMD_XML_ROOT_SE_CONTAINER)
    ET.SubElement(container_config, PMD_XML_ROOT_SE_CONTAINER_SE_SMP_OST).text = '0'
    ET.SubElement(container_config, PMD_XML_ROOT_SE_CONTAINER_SUB_E_D_TAGS)

    professional_metadata = ET.SubElement(root, PMD_XML_ROOT_SE_PMD, {PMD_XML_ROOT_SE_PMD_AT_VER: PMD_XML_ROOT_SE_PMD_AT_VER_VAL})

    ET.SubElement(professional_metadata, PMD_XML_ROOT_SE_PMD_SE_TTL)
    audio_signals = ET.SubElement(professional_metadata, PMD_XML_ROOT_SE_PMD_SE_ASG)
    audio_elements = ET.SubElement(professional_metadata, PMD_XML_ROOT_SE_PMD_SE_AEL)
    audio_presentations = ET.SubElement(professional_metadata, PMD_XML_ROOT_SE_PMD_SE_APR)
    iat = ET.SubElement(professional_metadata, PMD_XML_ROOT_SE_PMD_SE_IAT)

    # Copy audio_signals_list into audio_signals tree
    for i in range(0, len(audio_signal_list)):
        audio_signal = ET.SubElement(audio_signals, PMD_XML_ROOT_SE_PMD_SE_ASG_SE_ASG, {PMD_XML_ATTRIB_ID: str(audio_signal_list[i].id)})
        audio_signal_name = ET.SubElement(audio_signal, PMD_XML_ROOT_SE_PMD_SE_ASG_SE_ASG_NME)
        audio_signal_name.text = audio_signal_list[i].name

    # Copy all audio_elements_list into audio elements tree
    # Beds
    for i in range(0, len(audio_bed_list)):
        audio_bed = ET.SubElement(audio_elements, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB, {PMD_XML_ATTRIB_ID: str(audio_bed_list[i].id)})
        ET.SubElement(audio_bed, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_NME).text = audio_bed_list[i].name
        ET.SubElement(audio_bed, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_CFG).text = audio_bed_list[i].speaker_config
        audio_bed_output_targets = ET.SubElement(audio_bed, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG)

        # Loop through all output targets and populate
        for j in range(0, len(audio_bed_list[i].output_targets)):
            audio_bed_output_target = ET.SubElement(audio_bed_output_targets, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG,
                                                    {PMD_XML_ATTRIB_ID: str(audio_bed_list[i].output_targets[j].target)})

            # TODO add support for output targets to have more than one audio signal + gain attribute, i.e. support beyond direct beds
            # Loop through all audio signals for each target
            audio_signals = ET.SubElement(audio_bed_output_target, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG_SE_ASG)
            for k in range(0, len(audio_bed_list[i].output_targets[j].audio_signals)):
                ET.SubElement(audio_signals, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG_SE_ASG_SE_IDS).text\
                    = str(audio_bed_list[i].output_targets[j].audio_signals[k].id)

    # Objects
    for i in range(0, len(audio_object_list)):
        audio_object = ET.SubElement(audio_elements, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO, {PMD_XML_ATTRIB_ID: str(audio_object_list[i].id)})
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_NME).text = audio_object_list[i].name
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_CLS).text = OBJECT_CLASSES[audio_object_list[i].classification]
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_DUP).text = str(audio_object_list[i].dynamic_updates)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_XPS).text = str(audio_object_list[i].azimuth_or_x)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_YPS).text = str(audio_object_list[i].elevation_or_y)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_ZPS).text = str(audio_object_list[i].distance_or_z)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_SIZ).text = str(audio_object_list[i].size)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_S3D).text = str(audio_object_list[i].size_3d)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_DVG).text = str(audio_object_list[i].diverge)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_ASG).text = str(audio_object_list[i].audio_signal.id)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_SGD).text = str(audio_object_list[i].source_gain_db)

    # Copy presentations
    for i in range(0, len(audio_presentation_list)):
        audio_presentation = ET.SubElement(audio_presentations, PMD_XML_ROOT_SE_PMD_SE_APR_SE_APR, {PMD_XML_ATTRIB_ID: str(audio_presentation_list[i].id)})

        # Loop through names list
        for j in range(0, len(audio_presentation_list[i].name_language)):
            ET.SubElement(audio_presentation, PMD_XML_ROOT_SE_PMD_SE_APR_SE_NME, {PMD_XML_ROOT_SE_PMD_SE_APR_AT_LNG:
                          audio_presentation_list[i].name_language[j].language}).text = audio_presentation_list[i].name_language[j].name
        ET.SubElement(audio_presentation, PMD_XML_ROOT_SE_PMD_SE_APR_SE_CFG).text = audio_presentation_list[i].config
        ET.SubElement(audio_presentation, PMD_XML_ROOT_SE_PMD_SE_APR_SE_LNG).text = audio_presentation_list[i].language

        # Loop through elements list
        for j in range(0, len(audio_presentation_list[i].elements)):
            ET.SubElement(audio_presentation, PMD_XML_ROOT_SE_PMD_SE_APR_SE_EMT).text = str(audio_presentation_list[i].elements[j].id)

    # Copy iat_list into iat tree
    for i in range(0, len(iat_list)):
        iat_content_id = ET.SubElement(iat, PMD_XML_ROOT_SE_PMD_SE_IAT_SE_CID)
        iat_content_id_uuid = ET.SubElement(iat_content_id, PMD_XML_ROOT_SE_PMD_SE_IAT_SE_UUI)
        iat_content_id_uuid.text = iat_list[0].content_uuid

        iat_timestamp = ET.SubElement(iat, PMD_XML_ROOT_SE_PMD_SE_IAT_SE_TST)
        iat_timestamp.text = str(iat_list[0].time_stamp)

    # Write cleaned up xml to disk
    with open(xml_file, "w") as text_file:
        text_file.write(prettify_xml(root))
    return

"""
def write_pmd_xml_from_external(xml_file, ext_audio_signal_list, ext_audio_bed_list, ext_audio_object_list, ext_audio_presentation_list, ext_iat_list):
    # Reorder audio signals list (if need be, it looks nicer) so that id values are ascending
    ext_audio_signal_list.sort(key=lambda x: x.id, reverse=False)

    root = ET.Element(PMD_XML_ROOT)
    root.append(ET.Comment(PMD_XML_ROOT_CMT))

    container_config = ET.SubElement(root, PMD_XML_ROOT_SE_CONTAINER)
    ET.SubElement(container_config, PMD_XML_ROOT_SE_CONTAINER_SE_SMP_OST).text = '0'
    ET.SubElement(container_config, PMD_XML_ROOT_SE_CONTAINER_SUB_E_D_TAGS)

    professional_metadata = ET.SubElement(root, PMD_XML_ROOT_SE_PMD, {PMD_XML_ROOT_SE_PMD_AT_VER: PMD_XML_ROOT_SE_PMD_AT_VER_VAL})

    ET.SubElement(professional_metadata, PMD_XML_ROOT_SE_PMD_SE_TTL)
    audio_signals = ET.SubElement(professional_metadata, PMD_XML_ROOT_SE_PMD_SE_ASG)
    audio_elements = ET.SubElement(professional_metadata, PMD_XML_ROOT_SE_PMD_SE_AEL)
    audio_presentations = ET.SubElement(professional_metadata, PMD_XML_ROOT_SE_PMD_SE_APR)
    iat = ET.SubElement(professional_metadata, PMD_XML_ROOT_SE_PMD_SE_IAT)

    # Copy audio_signals_list into audio_signals tree
    for i in range(0, len(ext_audio_signal_list)):
        audio_signal = ET.SubElement(audio_signals, PMD_XML_ROOT_SE_PMD_SE_ASG_SE_ASG, {PMD_XML_ATTRIB_ID: str(ext_audio_signal_list[i].id)})
        audio_signal_name = ET.SubElement(audio_signal, PMD_XML_ROOT_SE_PMD_SE_ASG_SE_ASG_NME)
        audio_signal_name.text = ext_audio_signal_list[i].name

    # Copy all audio_elements_list into audio elements tree
    # Beds
    for i in range(0, len(ext_audio_bed_list)):
        audio_bed = ET.SubElement(audio_elements, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB, {PMD_XML_ATTRIB_ID: str(ext_audio_bed_list[i].id)})
        ET.SubElement(audio_bed, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_NME).text = ext_audio_bed_list[i].name
        ET.SubElement(audio_bed, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_CFG).text = ext_audio_bed_list[i].speaker_config
        audio_bed_output_targets = ET.SubElement(audio_bed, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG)

        # Loop through all output targets and populate
        for j in range(0, len(ext_audio_bed_list[i].output_targets)):
            audio_bed_output_target = ET.SubElement(audio_bed_output_targets, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG,
                                                    {PMD_XML_ATTRIB_ID: str(ext_audio_bed_list[i].output_targets[j].target)})

            # TODO add support for output targets to have more than one audio signal + gain attribute, i.e. support beyond direct beds
            # Loop through all audio signals for each target
            audio_signals = ET.SubElement(audio_bed_output_target, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG_SE_ASG)
            for k in range(0, len(ext_audio_bed_list[i].output_targets[j].audio_signals)):
                ET.SubElement(audio_signals, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AB_SE_OTG_SE_OTG_SE_ASG_SE_IDS).text\
                    = str(ext_audio_bed_list[i].output_targets[j].audio_signals[k].id)

    # Objects
    for i in range(0, len(ext_audio_object_list)):
        audio_object = ET.SubElement(audio_elements, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO, {PMD_XML_ATTRIB_ID: str(ext_audio_object_list[i].id)})
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_NME).text = ext_audio_object_list[i].name
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_CLS).text = OBJECT_CLASSES[ext_audio_object_list[i].classification]
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_DUP).text = str(ext_audio_object_list[i].dynamic_updates)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_XPS).text = str(ext_audio_object_list[i].azimuth_or_x)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_YPS).text = str(ext_audio_object_list[i].elevation_or_y)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_ZPS).text = str(ext_audio_object_list[i].distance_or_z)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_SIZ).text = str(ext_audio_object_list[i].size)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_S3D).text = str(ext_audio_object_list[i].size_3d)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_DVG).text = str(ext_audio_object_list[i].diverge)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_ASG).text = str(ext_audio_object_list[i].audio_signal.id)
        ET.SubElement(audio_object, PMD_XML_ROOT_SE_PMD_SE_AEL_SE_AO_SE_SGD).text = str(ext_audio_object_list[i].source_gain_db)

    # Copy presentations
    for i in range(0, len(ext_audio_presentation_list)):
        audio_presentation = ET.SubElement(audio_presentations, PMD_XML_ROOT_SE_PMD_SE_APR_SE_APR, {PMD_XML_ATTRIB_ID: str(ext_audio_presentation_list[i].id)})

        # Loop through names list
        for j in range(0, len(ext_audio_presentation_list[i].name_language)):
            ET.SubElement(audio_presentation, PMD_XML_ROOT_SE_PMD_SE_APR_SE_NME, {PMD_XML_ROOT_SE_PMD_SE_APR_AT_LNG:
                          ext_audio_presentation_list[i].name_language[j].language}).text = ext_audio_presentation_list[i].name_language[j].name
        ET.SubElement(audio_presentation, PMD_XML_ROOT_SE_PMD_SE_APR_SE_CFG).text = ext_audio_presentation_list[i].config
        ET.SubElement(audio_presentation, PMD_XML_ROOT_SE_PMD_SE_APR_SE_LNG).text = ext_audio_presentation_list[i].language

        # Loop through elements list
        for j in range(0, len(ext_audio_presentation_list[i].elements)):
            ET.SubElement(audio_presentation, PMD_XML_ROOT_SE_PMD_SE_APR_SE_EMT).text = str(ext_audio_presentation_list[i].elements[j].id)

    # Copy iat_list into iat tree
    for i in range(0, len(ext_iat_list)):
        iat_content_id = ET.SubElement(iat, PMD_XML_ROOT_SE_PMD_SE_IAT_SE_CID)
        iat_content_id_uuid = ET.SubElement(iat_content_id, PMD_XML_ROOT_SE_PMD_SE_IAT_SE_UUI)
        iat_content_id_uuid.text = ext_iat_list[0].content_uuid

        iat_timestamp = ET.SubElement(iat, PMD_XML_ROOT_SE_PMD_SE_IAT_SE_TST)
        iat_timestamp.text = str(ext_iat_list[0].time_stamp)

    # Write cleaned up xml to disk
    with open(xml_file, "w") as text_file:
        text_file.write(prettify_xml(root))
    return
"""


def start_logging():
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(levelname)s %(message)s', filename=PMD_LOG_FILE, filemode='w')
    logging.info('Started')
    return


def add_iat(content_uuid, time_stamp):
    global iat_list
    iat_list.append(IaT(content_uuid, time_stamp))
    return


def populate_model_from_adm(xml_struct, mode):
    global audio_signal_list, audio_presentation_list, audio_bed_list, audio_object_list, audio_element_list, iat_list
    global audio_presentation_counter, audio_element_counter, audio_object_counter, audio_bed_counter, audio_signal_counter

    # Clear out lists (delete works on all python versions)
    del audio_signal_list[:]
    del audio_presentation_list[:]
    del audio_bed_list[:]
    del audio_object_list[:]
    del audio_element_list[:]
    del iat_list[:]

    # Zero counters
    audio_presentation_counter = 0
    audio_element_counter = 0
    audio_object_counter = 0
    audio_bed_counter = 0
    audio_signal_counter = 0

    my_adm_metadata = parse_adm_xml(xml_struct, mode)

    for i in range(0, len(my_adm_metadata.audio_object)):
        if int(my_adm_metadata.audio_object[i].audio_pack_idref[0].type_label) == ADM_XML_INT_TYP_DS:
            # The number of audio_channel_idref entries in audio_pack can inform us of the bed configuration without looking that the speaker labels
            # in the corresponding audio_blocks. This works ok for fixed formats such as those used in the PMD editor 2, 3, 6, 8, 10, 12
            if len(my_adm_metadata.audio_object[i].audio_pack_idref[0].audio_channel_idref) == 2:
                config = LOUDSPEAKER_CONFIG_COMMON_USE_2_0
            elif len(my_adm_metadata.audio_object[i].audio_pack_idref[0].audio_channel_idref) == 3:
                config = LOUDSPEAKER_CONFIG_COMMON_USE_3_0
            elif len(my_adm_metadata.audio_object[i].audio_pack_idref[0].audio_channel_idref) == 6:
                config = LOUDSPEAKER_CONFIG_COMMON_USE_5_1
            elif len(my_adm_metadata.audio_object[i].audio_pack_idref[0].audio_channel_idref) == 8:
                config = LOUDSPEAKER_CONFIG_COMMON_USE_5_1_2
            elif len(my_adm_metadata.audio_object[i].audio_pack_idref[0].audio_channel_idref) == 10:
                config = LOUDSPEAKER_CONFIG_COMMON_USE_5_1_4
            elif len(my_adm_metadata.audio_object[i].audio_pack_idref[0].audio_channel_idref) == 12:
                config = LOUDSPEAKER_CONFIG_COMMON_USE_7_1_4

            # Create the bed
            # create_audio_bed(obj_name, loudspeaker_configuration, start_audio_signal, original_id=0)
            create_audio_bed(my_adm_metadata.audio_object[i].name, config,
                             int(my_adm_metadata.audio_object[i].audio_track_idref[0].track_id, 10), int(my_adm_metadata.audio_object[i].id[3:], 16) - 0x1000)

        if int(my_adm_metadata.audio_object[i].audio_pack_idref[0].type_label) == ADM_XML_INT_TYP_OB:
            # In ADM, you can only get specifics about the nature of the essence (dialog, music, spoken subtitle etc) at the content level
            # Search all audio content buckets looking for a matching audio_object.id
            for j in range(0, len(my_adm_metadata.audio_content)):
                for k in range(0, len(my_adm_metadata.audio_content[j].audio_object_idref)):
                    if my_adm_metadata.audio_content[j].audio_object_idref[k].id == my_adm_metadata.audio_object[i].id:

                        # If we are not 100% on the nature of the content then play safe with assuming GENERIC
                        if my_adm_metadata.audio_content[j].dialogue.value == ADM_NON_DIALOGUE_CONTENT_KIND:
                            classification = GENERIC
                        elif my_adm_metadata.audio_content[j].dialogue.value == ADM_DIALOGUE_CONTENT_KIND:
                            if my_adm_metadata.audio_content[j].dialogue.content_kind.classification == ADM_DIALOGUE_CONTENT_KIND_UNDEFINED:
                                classification = GENERIC
                            elif my_adm_metadata.audio_content[j].dialogue.content_kind.classification == ADM_DIALOGUE_CONTENT_KIND_DIALOGUE:
                                classification = DIALOGUE
                            elif my_adm_metadata.audio_content[j].dialogue.content_kind.classification == ADM_DIALOGUE_CONTENT_KIND_VOICEOVER:
                                classification = VOICEOVER
                            elif my_adm_metadata.audio_content[j].dialogue.content_kind.classification == ADM_DIALOGUE_CONTENT_KIND_SPOKEN_SUBTITLE:
                                classification = SPOKEN_SUBTITLE
                            elif my_adm_metadata.audio_content[j].dialogue.content_kind.classification == ADM_DIALOGUE_CONTENT_KIND_AUDIO_DESCRIPTION:
                                classification = VDS
                            elif my_adm_metadata.audio_content[j].dialogue.content_kind.classification == ADM_DIALOGUE_CONTENT_KIND_COMMENTARY:
                                classification = DIALOGUE
                            elif my_adm_metadata.audio_content[j].dialogue.content_kind.classification == ADM_DIALOGUE_CONTENT_KIND_EMERGENCY:
                                classification = EMERGENCY_ALERT
                        elif my_adm_metadata.audio_content[j].dialogue.value == ADM_MIXED_CONTENT_KIND:
                            classification = GENERIC

                        # The coordinates of the 'object' can be found in the audio_block_format entry of the associated audio_channel_format entry
                        # We only expect a single audio pack instance for each audio_object, audio_channel entry, and audio_block entry
                        x = my_adm_metadata.audio_content[j].audio_object_idref[k].audio_pack_idref[0].audio_channel_idref[
                            0].audio_block.position_coord.x_or_az
                        y = my_adm_metadata.audio_content[j].audio_object_idref[k].audio_pack_idref[0].audio_channel_idref[
                            0].audio_block.position_coord.y_or_el
                        z = my_adm_metadata.audio_content[j].audio_object_idref[k].audio_pack_idref[0].audio_channel_idref[
                            0].audio_block.position_coord.z_or_ds

                        # create_object(my_adm_metadata.audio_object[i].name, classification, False, 0.0, 0.0, 0.0, 0.0, False, False, 1, 0)
                        create_object(my_adm_metadata.audio_object[i].name, classification, False,
                                      float(my_adm_metadata.audio_content[j].audio_object_idref[k].audio_pack_idref[0].audio_channel_idref[
                                                0].audio_block.position_coord.x_or_az),
                                      float(my_adm_metadata.audio_content[j].audio_object_idref[k].audio_pack_idref[0].audio_channel_idref[
                                                0].audio_block.position_coord.y_or_el),
                                      float(my_adm_metadata.audio_content[j].audio_object_idref[k].audio_pack_idref[0].audio_channel_idref[
                                                0].audio_block.position_coord.z_or_ds),
                                      0.0, False, False, int(my_adm_metadata.audio_object[i].audio_track_idref[0].track_id, 10),
                                      float(my_adm_metadata.audio_content[j].audio_object_idref[k].gain),
                                      int(my_adm_metadata.audio_object[i].id[3:], 16) - 0x1000)

    # Create audio presentations out of audio_programme and audio_content pieces
    for i in range(0, len(my_adm_metadata.audio_programme)):
        list = []
        name = my_adm_metadata.audio_programme[i].name

        # Get id's of beds and objects
        for j in range(0, len(my_adm_metadata.audio_programme[i].audio_content_idref)):
            # Expect there to only be a single entry for audio_object_idref in each audioContent element
            list.append(int(my_adm_metadata.audio_programme[i].audio_content_idref[j].audio_object_idref[0].id[3:], 16) - 0x1000)

        # Create presentation
        # z = int(my_adm_metadata.audio_programme[i].id[4:], 16) - 0x1000
        create_audio_presentation("P" + str(i), my_adm_metadata.audio_programme[i].language, config, list,
                                  int(my_adm_metadata.audio_programme[i].id[4:], 16) - 0x1000)

        del list[:]
        for j in range(0, len(my_adm_metadata.audio_programme[i].audio_programme_label)):
            list.append(my_adm_metadata.audio_programme[i].audio_programme_label[j].name)
            list.append(my_adm_metadata.audio_programme[i].audio_programme_label[j].language)

        add_audio_presentation_names_by_name(find_list_reference_by_name(audio_presentation_list, 'P' + str(i)), list)

    # Lastly, create an IaT entry
    add_iat(str(uuid.uuid4()), 12345678)

    # Package all the data together into a professional metadata container
    k = ProfessionalMetadata(PMD_XML_ROOT_SE_PMD_AT_VER_VAL)
    k.audio_signals = audio_signal_list
    k.audio_elements = audio_element_list
    k.audio_presentations = audio_presentation_list
    k.iat = iat_list
    return k

# ************************************************************************************************************************************************************ #
# Create the PMD model of content
# ************************************************************************************************************************************************************ #
# start_logging()

if __name__ == "__main__":
    print ("main")
    # ******************************************************************************************************************************************************** #
    # Example section for API calls, i.e. model not driven by xml reader but UI or command line
    # ******************************************************************************************************************************************************** #
    cmdline = True
    if cmdline:
        import os
        import linecache
        import time
        #tracemalloc.start()

        # me = populate_model_from_adm('serial_adm.xml', PMD_XML_MODE_FILE)

        """
        

        create_audio_bed("7.1.4 ME", LOUDSPEAKER_CONFIG_COMMON_USE_7_1_4, 1)
        create_audio_bed("5.1 ME", LOUDSPEAKER_CONFIG_COMMON_USE_5_1, 13)
        create_audio_bed("2.0 ME", LOUDSPEAKER_CONFIG_COMMON_USE_2_0, 19)

        create_object("English Dialogue", DIALOGUE, False, -1.0, 1.0, 0.0, 0.0, False, False, 20, 0.0)
        create_object("French Dialogue", VDS, False, -1.0, 1.0, 0.0, 0.0, False, False, 21, 0.0)
        create_object("German Dialogue", SPOKEN_SUBTITLE, False, -1.0, 1.0, 0.0, 0.0, False, False, 22, 0.0)

        create_audio_presentation("P1", "eng", LOUDSPEAKER_CONFIG_COMMON_USE_5_1_4, ["5.1.4 ME", "English Dialogue"])
        create_audio_presentation("P2", "eng", LOUDSPEAKER_CONFIG_COMMON_USE_5_1, ["5.1 ME", "English Dialogue"])
        create_audio_presentation("P3", "fra", LOUDSPEAKER_CONFIG_COMMON_USE_5_1_4, ["2.0 ME", "French Dialogue"])
        create_audio_presentation("P4", "fra", LOUDSPEAKER_CONFIG_COMMON_USE_5_1, ["5.1 ME", "French Dialogue"])

        add_audio_presentation_names_by_name(find_list_reference_by_name(audio_presentation_list, "P1"),
                                             ["English Commentary", "eng", "Commentateur Anglais",
                                              "fra", "German Commentary", "eng", "Commentateur Achtung", "ger"])

        add_audio_presentation_names_by_name(find_list_reference_by_name(audio_presentation_list, "P2"), ["English-2", "eng", "Commentateur-2", "fra"])
        add_audio_presentation_names_by_name(find_list_reference_by_name(audio_presentation_list, "P3"), ["English-3", "eng", "Commentateur-3", "fra"])
        add_audio_presentation_names_by_name(find_list_reference_by_name(audio_presentation_list, "P4"), ["English-4", "eng", "Commentateur-4", "fra"])

        # Configure IaT (UUID, timestamp)
        add_iat(str(uuid.uuid4()), 12345678)
        write_pmd_xml("pmd_created.xml")
        print()      
       """

        loop_counter = 1
        startsecs = time.time()

        for i in range(0, loop_counter):
            a = 0
            #my_metadata = parse_pmd_xml("pmd_gen.xml", PMD_XML_MODE_FILE)
            #my_metadata = parse_pmd_xml("gen.pmd1.xml", PMD_XML_MODE_FILE)
            me = populate_model_from_adm('skip_sadm.xml', PMD_XML_MODE_FILE)
            #me = parse_adm_xml('serial_adm.xml', PMD_XML_MODE_FILE)

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

    # ******************************************************************************************************************************************************** #

    # ******************************************************************************************************************************************************** #
    # Example section for API calls, i.e. model driven by xml reader
    # ******************************************************************************************************************************************************** #

    else:
        my_metadata = parse_pmd_xml("pmd_gen2.xml", PMD_XML_MODE_FILE)
    # ******************************************************************************************************************************************************** #

    # ******************************************************************************************************************************************************** #
    # Example section for API calls, i.e. model driven by xml writer
    # ******************************************************************************************************************************************************** #

    # !!!!! Not finished yet !!!!!
        write_pmd_xml("pmd_created.xml")
    # ******************************************************************************************************************************************************** #
