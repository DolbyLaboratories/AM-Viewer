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

from adm.adm_const import NON_DIALOGUE_CONTENT_KIND
from adm.adm_const import DIALOGUE_CONTENT_KIND
from adm.adm_const import MIXED_CONTENT_KIND

from adm.adm_const import DIALOGUE_CONTENT_KIND
from adm.adm_const import NON_DIALOGUE_CONTENT_KIND
from adm.adm_const import MIXED_CONTENT_KIND
from adm.adm_const import DIALOGUE_CONTENT
from adm.adm_const import NON_DIALOGUE_CONTENT
from adm.adm_const import MIXED_CONTENT
from adm.adm_const import DIALOGUE_CONTENT
from adm.adm_const import DIALOGUE
from adm.adm_const import VOICEOVER
from adm.adm_const import SPOKEN_SUBTITLE
from adm.adm_const import AUDIO_DESCRIPTION
from adm.adm_const import COMMENTARY
from adm.adm_const import EMERGENCY
from adm.adm_const import TYPE_DEFINITION
from adm.adm_const import TYPE_LABEL

from adm.adm_const import AUDIO_PACK_STR
from adm.adm_const import AUDIO_PROGRAMME_STR
from adm.adm_const import AUDIO_CONTENT_STR
from adm.adm_const import AUDIO_OBJECT_STR
from adm.adm_const import AUDIO_BLOCK_STR
from adm.adm_const import AUDIO_CHANNEL_STR
from adm.adm_const import AUDIO_TRACK_UID_STR

from adm.adm_const import DIRECTSPEAKERS
from adm.adm_const import MATRIX
from adm.adm_const import OBJECTS
from adm.adm_const import HOA
from adm.adm_const import BINAURAL
from adm.adm_const import POLAR
from adm.adm_const import CARTESIAN

from adm.adm_const import DEFAULT_AUDIO_SAMPLE_RATE
from adm.adm_const import DEFAULT_AUDIO_BIT_DEPTH

# ************************************************************************************************************************************************************ #


class AudioFormatExtended(object):
    def __init__(self):
        self.audio_programme = []
        self.audio_content = []
        self.audio_object = []
        self.audio_pack_format = []
        self.audio_channel_format = []
        self.audio_track_uid = []


class LoudnessMetadata:
    def __init__(self):
        self.loudness_method = ""
        self.loudness_rec_type = ""
        self.loudness_correction_type = ""
        self.integrated_loudness = 0.0
        self.loudness_range = 0.0
        self.max_true_peak = 0.0
        self.max_momentary = 0.0
        self.max_short_term = 0.0
        self.dialogue_loudness = 0.0

    def update_loudness_method(self, loudness_method):
        self.loudness_method = loudness_method

    def update_loudness_rec_type(self, loudness_rec_type):
        self.loudness_rec_type = loudness_rec_type

    def update_loudness_correction_type(self, loudness_correction_type):
        self.loudness_correction_type = loudness_correction_type

    def update_integrated_loudness(self, integrated_loudness):
        self.integrated_loudness = integrated_loudness

    def update_loudness_range(self, loudness_range):
        self.loudness_range = loudness_range

    def update_max_true_peak(self, max_true_peak):
        self.max_true_peak = max_true_peak

    def update_max_momentary(self, max_momentary):
        self.max_momentary = max_momentary

    def update_max_short_term(self, max_short_term):
        self.max_short_term = max_short_term

    def update_dialogue_loudness(self, dialogue_loudness):
        self.dialogue_loudness = dialogue_loudness


class AudioProgrammeLabel:
    def __init__(self, name, language):
        self.name = name
        self.language = language


class AudioPackFormat:
    def __init__(self, id, name, type_label):
        self.id = id
        self.name = name
        self.audio_channel_idref = []
        self.type_label = type_label


class AudioProgramme:
    def __init__(self, name, language, id):
        self.name = name
        self.language = language
        self.id = id
        self.audio_programme_label = []
        self.audio_content_idref = []
        self.loudness_metadata = None


class AudioContent:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.dialogue = None
        self.audio_object_idref = []


class Dialogue:
    def __init__(self, value, classification):
        value = int(value)
        classification = int(classification)
        self.value = value
        if value == NON_DIALOGUE_CONTENT:
            self.content_kind = NonDialogueContentKind(classification)
        elif value == DIALOGUE_CONTENT:
            self.content_kind = DialogueContentKind(classification)
        elif value == MIXED_CONTENT:
            self.content_kind = MixedContentKind(classification)


class NonDialogueContentKind:
    def __init__(self, classification):
        self.classification = classification
        self.classification_text = NON_DIALOGUE_CONTENT_KIND[classification]


class DialogueContentKind:
    def __init__(self, classification):
        self.classification = classification
        self.classification_text = DIALOGUE_CONTENT_KIND[classification]


class MixedContentKind:
    def __init__(self, classification):
        self.classification = classification
        self.classification_text = MIXED_CONTENT_KIND[classification]


class AudioObject:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.audio_pack_idref = []
        self.audio_track_idref = []
        self.head_locked = None
        self.gain = None


class AudioChannelFormat:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.audio_block = None


class AudioBlockFormat:
    def __init__(self, id):
        self.id = id
        self.cartesian = None
        self.position_coord = None
        self.headphone_render = None
        self.speaker_label = None


class Position:
    def __init__(self, is_polar):
        self.is_polar = is_polar
        self.x_or_az = None
        self.y_or_el = None
        self.z_or_ds = None

class Headphone:
    def __init__(self, value, bypass, mode):
        self.value = value
        self.bypass = bypass
        self.mode = mode


class AudioTrackUID:
    def __init__(self, id):
        self.id = id
        self.channel_format_id = None
        self.pack_format_id = None
        self.track_id = None


"""

class AudioContent:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class AudioProgrammeLabel:
    def __init__(self, value, language):
        self.language = language
        self.name = value

    def update_language(self, language):
        self.language = language

    def update_name(self, name):
        self.name = name
        
        
class AudioPackFormat:
    def __init__(self, id, type_definition, name):

        # Note that custom id's start at 1000 not 0000
        if id < 0x10:
            idhext = "100"
        elif id < 0x100:
            idhext = "10"
        elif id < 0x1000:
            idhext = "1"
        elif id < 0x10000:
            idhext = ""

        # ID for the object is based upon its type_definition
        self.id = AUDIO_PACK_STR + str(type_definition) + idhext + hex(id)[2:]
        self.name = name
        self.type_label = TYPE_LABEL[type_definition]
        self.type_definition = TYPE_DEFINITION[type_definition]
        self.importance = 0
        self.audio_channel_format_id_refs = []
        self.audio_pack_format_id_refs = []
        self.absolute_distance = 0.0

    def update_id(self, id):
        self.id = id

    def update_name(self, name):
        self.name = name

    def update_type_label(self, type_label):
        self.type_label = type_label

    def update_type_definition(self, type_definition):
        self.type_definition = type_definition

    def update_importance(self, importance):
        self.importance = importance

    def update_absolute_distance(self, absolute_distance):
        self.absolute_distance = absolute_distance
class AudioProgramme:
    def __init__(self, name, language, id):
        if id < 0x10:
            idhext = "000"
        elif id < 0x100:
            idhext = "00"
        elif id < 0x1000:
            idhext = "0"
        elif id < 0x10000:
            idhext = ""

        self.id = AUDIO_PROGRAMME_STR + idhext + hex(id)[2:]
        self.name = name
        self.language = language
        self.start = ""
        self.end = ""
        self.max_ducking_depth = ""
        self.audio_program_labels = []
        self.content_id_refs = []
        self.loudness = []

    def update_id(self, id):
        self.id = id

    def update_name(self, name):
        self.name = name

    def update_language(self, language):
        self.language = language

    def update_start_time(self, start):
        self.start = start

    def update_end_time(self, end):
        self.end = end

    def update_max_ducking_depth(self, max_ducking_depth):
        self.max_ducking_depth = max_ducking_depth

    def add_programme_label(self, value, language):
        self.audio_program_labels.append(AudioProgrammeLabel(value, language))

    def add_programme_loudness(self):
        self.loudness.append(LoudnessMetadata())
"""


"""
class AudioContent:
    def __init__(self, id, name):
        if id < 0x10:
            idhext = "000"
        elif id < 0x100:
            idhext = "00"
        elif id < 0x1000:
            idhext = "0"
        elif id < 0x10000:
            idhext = ""

        self.id = AUDIO_CONTENT_STR + idhext + hex(id)[2:]
        self.name = name
        self.language = ""
        self.dialogue = Dialogue()
        self.audio_object_id_refs = []

    def update_id(self, id):
        self.id = id

    def update_name(self, name):
        self.name = name

    def update_language(self, language):
        self.language = language

    def update_dialogue(self, dialog_type):
        self.dialogue.update_value(DIALOGUE_CONTENT, dialog_type)

    def update_non_dialogue(self, non_dialogue_type):
        self.dialogue.update_value(NON_DIALOGUE_CONTENT, non_dialogue_type)


class Dialogue:
    def __init__(self):
        self.value = 0
        self.content_kind = NonDialogueContentKind()

    def update_value(self, value, classification, kind):
        self.value = value
        if value == NON_DIALOGUE_CONTENT:
            self.content_kind = NonDialogueContentKind()
        elif value == DIALOGUE_CONTENT:
            self.content_kind = DialogueContentKind()
        elif value == MIXED_CONTENT:
            self.content_kind = MixedContentKind()

        self.content_kind.update_classification(classification)
"""




"""
class AudioObject:
    def __init__(self, id, name):
        if id < 0x10:
            idhext = "000"
        elif id < 0x100:
            idhext = "00"
        elif id < 0x1000:
            idhext = "0"
        elif id < 0x10000:
            idhext = ""

        self.id = AUDIO_OBJECT_STR + idhext + hex(id)[2:]
        self.name = name
        self.start = ""
        self.duration = ""
        self.dialogue = 0
        self.importance = 0
        self.interact = 0
        self.disable_ducking = 0
        self.audio_pack_format_id_refs = []
        self.audio_object_id_refs = []
        self.audio_complimentary_object_id_refs = []
        self.audio_track_uid_refs = []
        self.object_interaction = AudioObjectInteraction()
        self.gain = 1.0
        self.headlocked = 0

    def update_id(self, id):
        self.id = id

    def update_name(self, name):
        self.name = name

    def update_start(self, start):
        self.start = start

    def update_duration(self, duration):
        self.duration = duration

    def update_dialogue(self, dialogue):
        self.dialogue = dialogue

    def update_importance(self, importance):
        self.importance = importance

    def update_interact(self, interact):
        self.interact = interact

    def update_disable_ducking(self, disable_ducking):
        self.disable_ducking = disable_ducking

    def update_gain(self, gain):
        self.gain = gain

    def update_headlocked(self, headlocked):
        self.headlocked = headlocked
"""


class ItemValidationData:
    def __init__(self, min_occurs, max_occurs):
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs


class AudioObjectInteraction:
    def __init__(self):
        self.on_off_interact = 0
        self.gain_interact = 0
        self.position_interact = 0
        self.gain_interaction_range = GainInteractionRange()
        self.position_interaction_range = PositionInteractionRange()

    def update_interactive(self, on_off_interact, gain_interact, position_interact):
        self.on_off_interact = on_off_interact
        self.gain_interact = gain_interact
        self.position_interact = position_interact


class GainInteractionRange:
    def __init__(self):
        self.gain_min = 1.0
        self.gain_max = 1.0

    def update_min_max_gain(self, gain_min, gain_max):
        self.gain_min = gain_min
        self.gain_max = gain_max


class PositionInteractionRange:
    def __init__(self):
        self.azimuth_or_x_min = 0.0
        self.azimuth_or_x_max = 0.0
        self.elevation_or_y_min = 0.0
        self.elevation_or_y_max = 0.0
        self.distance_or_z_min = 0.0
        self.distance_or_z_max = 0.0

    def update_position_min_max(self, azimuth_or_x_min, azimuth_or_x_max, elevation_or_y_min, elevation_or_y_max, distance_or_z_min, distance_or_z_max):
        self.azimuth_or_x_min = azimuth_or_x_min
        self.azimuth_or_x_max = azimuth_or_x_max
        self.elevation_or_y_min = elevation_or_y_min
        self.elevation_or_y_max = elevation_or_y_max
        self.distance_or_z_min = distance_or_z_min
        self.distance_or_z_max = distance_or_z_max


"""
class AudioBlockFormat:
    def __init__(self, id, type_definition, coordinate_mode, update_number):
        if id < 0x10:
            idhext = "100"
        elif id < 0x100:
            idhext = "10"
        elif id < 0x1000:
            idhext = "1"
        elif id < 0x10000:
            idhext = ""

        str_update_number = hex(update_number)[2:]
        i = 8 - len(str_update_number)
        while i > 0:
            str_update_number = "0" + str_update_number
            i -= 1

        self.id = AUDIO_BLOCK_STR + str(type_definition) + idhext + hex(id)[2:] + "_" + str_update_number
        self.rtime = ""
        self.duration = ""
        self.gain = 1.0
        self.coordinate_mode = coordinate_mode

        if type_definition == DIRECTSPEAKERS:
            self.definition = DirectSpeakers()
        elif type_definition == MATRIX:
            self.definition = Matrix()
        elif type_definition == OBJECTS:
            self.definition = Objects(self.coordinate_mode)
        elif type_definition == HOA:
            self.defination = HoA()
        elif type_definition == BINAURAL:
            self.definition = Binaural()

        if self.coordinate_mode == POLAR:
            self.azimuth = 0.0
            self.elevation = 0.0
            self.distance = 0.0
        elif self.coordinate_mode == CARTESIAN:
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0

    def update_id(self, id):
        self.id = id

    def update_rtime(self, rtime):
        self.rtime = rtime

    def update_duration(self, duration):
        self.duration = duration

    def update_gain(self, gain):
        self.gain = gain

    def update_type_definition(self, typedef):
        if typedef == DIRECTSPEAKERS:
            self.definition = DirectSpeakers()
        elif typedef == MATRIX:
            self.definition = Matrix()
        elif typedef == OBJECTS:
            self.definition = Objects(self.coordinate_mode)
        elif typedef == HOA:
            self.defination = HoA()
        elif typedef == BINAURAL:
            self.definition = Binaural()

    def update_coordinates(self, azimuth_or_x, elevation_or_y, distance_or_z):
        if self.coordinate_mode == POLAR:
            self.azimuth = azimuth_or_x
            self.elevation = elevation_or_y
            self.distance = distance_or_z
        elif self.coordinate_mode == CARTESIAN:
            self.x = azimuth_or_x
            self.y = elevation_or_y
            self.z = distance_or_z




"""


class DirectSpeakers:
    def __init__(self,):
        self.speaker_label = ""

    def update_speaker_label(self, speaker_label):
        self.speaker_label = speaker_label


class Objects:
    def __init__(self, coordinate_mode):
        self.cartesian = coordinate_mode
        self.width = 0.0
        self.depth = 0.0
        self.height = 0.0
        self.diffuse = 0
        self.channel_lock = ChannelLock()
        self.divergence_range = 0.0
        self.jump_position = JumpPosition()
        self.zone_exclusion = []


class Zone:
    def __init__(self, name, min_azimuth_or_x, max_azimuth_or_x, min_elevation_or_y, max_elevation_or_y, min_z, max_z):
        self.name = name
        self.min_azimuth_or_x = min_azimuth_or_x
        self.max_azimuth_or_x = max_azimuth_or_x
        self.min_elevation_or_y = min_elevation_or_y
        self.max_elevation_or_y = max_elevation_or_y
        self.min_z = min_z
        self.max_z = max_z

    def update_zone_position(self, min_azimuth_or_x, max_azimuth_or_x, min_elevation_or_y, max_elevation_or_y, min_z, max_z):
        self.min_azimuth_or_x = min_azimuth_or_x
        self.max_azimuth_or_x = max_azimuth_or_x
        self.min_elevation_or_y = min_elevation_or_y
        self.max_elevation_or_y = max_elevation_or_y
        self.min_z = min_z
        self.max_z = max_z


class ChannelLock:
    def __init__(self):
        self.value = 0
        self.max_distance = 0.0

    def update(self, value, max_distance):
        self.value = value
        self.max_distance = max_distance


class JumpPosition:
    def __init__(self):
        self.value = 0
        self.interpolation_length = 0.0

    def update(self, value, interpolation_length):
        self.value = value
        self.interpolation_length = interpolation_length


class HeadphoneRender:
    def __init__(self):
        self.bypass = 0
        self.mode = 0

    def update(self, bypass, mode):
        self.bypass = bypass
        self.mode = mode

"""
class AudioChannelFormat:
    def __init__(self, id, type_definition, name):
        if id < 0x10:
            idhext = "000"
        elif id < 0x100:
            idhext = "00"
        elif id < 0x1000:
            idhext = "0"
        elif id < 0x10000:
            idhext = ""

        self.id = AUDIO_CHANNEL_STR + str(type_definition) + idhext + hex(id)[2:]
        self.name = name
        self.type_label = TYPE_LABEL[type_definition]
        self.type_definition = TYPE_DEFINITION[type_definition]
        self.frequency = []
        self.audio_block_format_id_ref = []

    def update_name(self, name):
        self.name = name

    def update_id(self, id):
        self.id = id

    def update_type_label(self, type_label):
        self.type_label = type_label

    def update_type_definition(self, type_definition):
        self.type_definition = type_definition
"""


"""
class AudioTrackUID:
    def __init__(self, id):
        if id < 0x10:
            idhext = "000"
        elif id < 0x100:
            idhext = "00"
        elif id < 0x1000:
            idhext = "0"
        elif id < 0x10000:
            idhext = ""

        self.id = AUDIO_TRACK_UID_STR + idhext + hex(id)[2:]
        self.sample_rate = DEFAULT_AUDIO_SAMPLE_RATE
        self.bit_depth = DEFAULT_AUDIO_BIT_DEPTH
        self.audio_mxf_lookup = AudioMXFLookUp()
        self.audio_track_format_id_ref = []
        self.audio_channel_format_id_ref = []
        self.audio_pack_format_id_ref = []

"""


class AudioMXFLookUp:
    def __init__(self):
        self.umid = ""
        self.track_id_ref = 0
        self.channel_id_ref = 0

    def update_audio_mxf_lookup(self, umid, track_id_ref, channel_id_ref):
        self.umid = umid
        self.track_id_ref = track_id_ref
        self.channel_id_ref = channel_id_ref


class AudioTrackFormat:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.format_label = ""
        self.format_definition = ""
        self.audio_stream_format_id_ref = []

    def update_id(self, id):
        self.id = id

    def update_name(self, name):
        self.name = name

    def update_format_label(self, format_label):
        self.format_label = format_label

    def update_format_definition(self, format_definition):
        self.format_definition = format_definition


class AudioStreamFormat:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.format_label = ""
        self.format_definition = ""
        self.audio_channel_format_id_ref = []
        self.audio_pack_format_id_ref = []
        self.audio_track_format_id_ref = []

    def update_id(self, id):
        self.id = id

    def update_name(self, name):
        self.name = name

    def update_format_label(self, format_label):
        self.format_label = format_label

    def update_format_definition(self, format_definition):
        self.format_definition = format_definition

# ************************************************************************************************************************************************************ #
# ************************************************************************************************************************************************************ #
