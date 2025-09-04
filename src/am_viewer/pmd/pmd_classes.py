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
from typing import List, Iterable
import math


class MetadataContainer():
    def __init__(self, audio_model, adm_info):
        self.audio_model = audio_model
        self.adm_info = adm_info


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


class CartCoordinate(List):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        super(CartCoordinate, self).__init__([x, y, z])

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        return self[2]

    @x.setter
    def x(self, new_x):
        self[0] = new_x

    @y.setter
    def y(self, new_y):
        self[1] = new_y

    @z.setter
    def z(self, new_z):
        self[2] = new_z

    def rotate_around_x(self, deg: float):
        r = math.sqrt(pow(self.y, 2) + pow(self.z, 2))
        if self.y == 0:
            theta = (math.pi/2 if self.z > 0 else 3*math.pi/2) + deg
        else:
            theta = math.atan(self.z/self.y) + deg
            if self.y < 0:
                theta = (theta + math.pi) % (2*math.pi)
        self.z = r*math.sin(theta)
        self.y = r*math.cos(theta)

    def rotate_around_z(self, deg: float):
        r = math.sqrt(pow(self.x, 2) + pow(self.y, 2))

        if self.y == 0:
            theta = (math.pi/2 if self.x > 0 else 3*math.pi/2) + deg
        else:
            theta = math.atan(self.x/self.y) + deg
            if self.y < 0:
                theta = (theta + math.pi) % (2*math.pi)
        self.y = r*math.cos(theta)
        self.x = r*math.sin(theta)

    def __mul__(self, other):
        if not issubclass(type(other), Iterable):
            self.x *= other
            self.y *= other
            self.z *= other
        else:
            self.x *= other[0]
            self.y *= other[1]
            self.z *= other[2]

    def to_atmos_cart(self):
        to_ret = CartCoordinate((self.x + 1)/2, (self.y + 1)/2, (self.z + 1)/2)

        to_ret.x = min(1.0, to_ret.x)
        to_ret.x = max(0.0, to_ret.x)
        to_ret.y = min(1.0, to_ret.y)
        to_ret.y = max(0.0, to_ret.y)
        to_ret.z = min(1.0, to_ret.z)
        to_ret.z = max(0.0, to_ret.z)

        return to_ret


class Coordinate(List):
    def __init__(self, az=0.0, el=0.0, r=0.0):
        super(Coordinate, self).__init__([az, el, r])

    def pretty(self, deg=True):
        m = 360/(2*math.pi) if deg else 1
        return f'az={self.az*m:+.01f}, el={self.el*m:+.01f}, r={self.r:.02f}'

    @property
    def az(self):
        return self[0]

    @property
    def el(self):
        return self[1]

    @property
    def r(self):
        return self[2]

    @az.setter
    def az(self, new_az):
        self[0] = new_az % (2*math.pi)

    @el.setter
    def el(self, new_el):
        self[1] = new_el % (2*math.pi)

    @r.setter
    def r(self, new_r):
        self[2] = new_r

    def to_cart(self):
        t1 = self.r * math.cos(self.el)
        return CartCoordinate(t1 * math.sin(self.az), t1 * math.cos(self.az), self.r * math.sin(self.el))

    def _update_from_cart(self, x, y, z):
        psquared = pow(x, 2) + pow(y, 2) + pow(z, 2)
        self.r = math.sqrt(psquared)
        self.az = math.atan(x/y) if y != 0 else math.pi/2 if x > 0 else 3*math.pi/2
        if y < 0:
            self.az = (self.az + math.pi) % (2*math.pi)
        self.el = math.asin(z/self.r) if self.r != 0 else 0

    @classmethod
    def from_cart(cls, c: CartCoordinate):
        to_ret = cls()
        to_ret._update_from_cart(c.x, c.y, c.z)
        return to_ret

    def __add__(self, other):
        c1 = self.to_cart()
        c2 = other.to_cart()
        self._update_from_cart(c1[0] + c2[0], c1[1] + c2[1], c1[2] + c2[2])

    def __mul__(self, other):
        if not issubclass(type(other), Iterable):
            self.az *= other
            self.el *= other
            self.r *= other
        else:
            self.az *= other[0]
            self.el *= other[1]
            self.r *= other[2]

# ************************************************************************************************************************************************************ #
# ************************************************************************************************************************************************************ #
