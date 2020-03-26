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


class ProfessionalMetadata(object):
    def __init__(self, version):
        self.version = version
        self.title = ""
        self.audio_signals = []
        self.audio_elements = []
        self.audio_presentations = []
        self.iat = []

    def update_version(self, version):
        self.version = version

    def update_title(self, title):
        self.title = title


class AudioPresentation(object):
    def __init__(self, name, language, id):
        self.id = id
        self.config = ""
        self.name = name
        self.language = language
        self.name_language = []
        self.elements = []

    def update_name(self, name):
        self.name = name

    def update_name_language(self, name_language):
        self.name_language = name_language

    def update_config(self, config):
        self.config = config

    def update_language(self, language):
        self.language = language

    def add_local_language_name(self, name, language):
        self.name_language.append(PresentationNameLanguage(name, language))


class PresentationNameLanguage(object):
    def __init__(self, name, language):
        self.name = name
        self.language = language


class AudioObject(object):
    def __init__(self, id):
        self.id = id
        self.name = ""
        self.classification = ""
        self.dynamic_updates = False
        self.azimuth_or_x = 0.0
        self.elevation_or_y = 0.0
        self.distance_or_z = 0.0
        self.size = 0.0
        self.size_3d = False
        self.diverge = False
        self.audio_signal = None
        self.source_gain_db = 0.0

    def update_name(self, name):
        self.name = name

    def update_classification(self, classification):
        self.classification = classification

    def update_dynamic_updates(self, dynamic_updates):
        self.dynamic_updates = dynamic_updates

    def update_coordinates(self, azimuth_or_x, elevation_or_y, distance_or_z):
        self.azimuth_or_x = azimuth_or_x
        self.elevation_or_y = elevation_or_y
        self.distance_or_z = distance_or_z

    def update_size(self, size):
        self.size = size

    def update_size_3d(self, size_3d):
        self.size_3d = size_3d

    def update_diverge(self, diverge):
        self.diverge = diverge

    def update_audio_signal(self, audio_signal_ref):
        self.audio_signal = audio_signal_ref

    def update_source_gain_db(self, source_gain_db):
        self.source_gain_db = source_gain_db


class AudioSignal(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def update_name(self, name):
        self.name = name


class OutputTarget(object):
    def __init__(self, target):
        self.target = target
        self.audio_signals = []


class AudioBed(object):
    def __init__(self, id, name, speaker_config, gain_db):
        self.id = id
        self.name = name
        self.speaker_config = speaker_config
        self.gain_db = gain_db
        self.output_targets = []

    def update_name(self, name):
        self.name = name

    def update_speaker_config(self, speaker_config):
        self.speaker_config = speaker_config


class IaT(object):
    def __init__(self, content_uuid, time_stamp):
        self.content_uuid = content_uuid
        self.time_stamp = time_stamp

# ************************************************************************************************************************************************************ #
# ************************************************************************************************************************************************************ #
