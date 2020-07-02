#!/usr/bin/env python3

"""
 AM Viewer
 Copyright (c) 2019, Dolby Laboratories Inc.
 All rights reserved.
 
 Redistribution and use in source and binary forms, with or without modification, are permitted
 provided that the following conditions are met:
 
 1. Redistributions of source code must retain the above copyright notice, this list of conditions
    and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
    and the following disclaimer in the documentation and/or other materials provided with the distribution.
 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or
    promote products derived from this software without specific prior written permission.
 
 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
 WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
 PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
 ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 OF THE POSSIBILITY OF SUCH DAMAGE.
"""


from tkinter import *
import time
import random
import threading
import platform
import os
import signal
import sys
import subprocess
import binascii
import zlib
import netifaces
import scapy.all as scapy
import argparse
import queue
import copy
import wave
import errno
import math
from pmd.pmd_tool import parse_pmd_xml
from pmd.pmd_tool import populate_model_from_xml
from pmd.pmd_tool import populate_model_from_adm
from pmd.pmd_tool import PMD_XML_MODE_FILE
from pmd.pmd_tool import ADM_XML_MODE_FILE
from adm.adm_tool import ADM_XML_MODE_STRING
from pmd.pmd_classes import AudioObject
from pmd.pmd_classes import AudioBed
from pmd.pmd_tool import check_parameter_type
from pmd.pmd_const import PRESENTATION_CONFIG_TEXT
from pmd.pmd_const import PRESENTATION_CONFIG_EQUIV
from pmd.pmd_const import LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_NAMES
from pmd.pmd_const import LOUDSPEAKER_CONFIG_2_0
from pmd.pmd_const import LOUDSPEAKER_CONFIG_3_0
from pmd.pmd_const import LOUDSPEAKER_CONFIG_5_1
from pmd.pmd_const import LOUDSPEAKER_CONFIG_5_1_2
from pmd.pmd_const import LOUDSPEAKER_CONFIG_5_1_4
from pmd.pmd_const import LOUDSPEAKER_CONFIG_7_1_4
from pmd.pmd_const import OBJECT_CLASSES
from am_viewer.am_xml_viewer import XML_Viewer
from am_viewer.am_xml_viewer import isFilePmd
from am_viewer.am_xml_viewer import isFileSADM
import aoip_services.aoip_discovery
import aoip_services.multicast

__version__ = "3.5"

class AudioObjectHeadings:
    TYPE = 0
    NAME = 1
    DIVERGE = 2
    CH = 3
    GAIN = 4
    X = 5
    Y = 6
    Z = 7

class PresentationHeadings:
    NAME = 0
    NAME_LANG = 1
    BED_ELEMENT = 2
    TARGET_CFG = 3
    PRES_LANG = 4

class AudioBedHeadings:
    SOURCE = 0
    CONFIG = 1
    NAME = 2
    GAIN = 3
    START = 4
    END = 5


# Helper functions

def get_cmd_stdio(args):
    import subprocess
    run_output = subprocess.run(args, stdout=subprocess.PIPE)
    text = str(run_output.stdout.decode("utf-8"))
    text = text.replace('\\n', '\n')
    text = text.replace('\\r', '\r')
    text = text.replace('\\t', '\t')
    return(text)


def gain_from_db(db):
    return 10 ** (db / 20)

def get_word(payload, index, subframe_mode):
    if subframe_mode:
        return(int.from_bytes(payload[index*2:(index*2)+3], byteorder='big') >> 4)
    else:
        return(int.from_bytes(payload[index:index+3], byteorder='big') >> 4)


def endian_swap24(array24):
    swapped24 = bytearray(b'')
    for i in range (0, len(array24), 3):
        swapped24.append(array24[i + 2])
        swapped24.append(array24[i + 1])
        swapped24.append(array24[i])
    return swapped24

def check_xml_complete():
    with open('pmd.xml') as f:
        lines = f.readlines()
        if len(lines) < 25:
            return False
        for line in lines[::-1]:
            if line.find("<IAT>") > 0:
                return True
        return False


def pack_20bits(array24):
    output_nibble_hi_lo = 0
    output_nibble_count = 0
    input_word_count = len(array24)
    array20 = bytearray(b'')

    for i in range(0, input_word_count, 3):
        input_nibbles = []
        for j in range(0,3):
            input_nibbles.append((array24[i+j] >> 4) & 0x0f)
            input_nibbles.append(array24[i+j] & 0x0f)
        # Write out 5 nibbles
        for nibble in input_nibbles:
            if (output_nibble_count != 5):
                if output_nibble_hi_lo == 1:
                    array20[-1] = array20[-1] | nibble
                else:
                    array20.append(nibble << 4)
                output_nibble_hi_lo = 1 - output_nibble_hi_lo
                output_nibble_count = output_nibble_count + 1
            else:
                output_nibble_count = 0

    return(array20)

def subframe_to_framemode(array24):
    if (len(array24) % 6) != 0:
        print("Warning: trying to convert from subframe mode with incomplete # words")
        limit = (len(array24) // 6) * 6 #uses floor division //
    else:
        limit = len(array24)
    frame_array = bytearray(b'')
    for i in range(0, limit, 6):
        for j in range(i, i+3):
            frame_array.append(array24[j])
    return(bytes(frame_array))


def clean_up_temp_files(filelist):
    for tmpfile in filelist:
        try:
            os.remove(tmpfile)
        except:
            pass



# Debug helpers -- This can be deleted after development

# --- - chunking helpers
def chunks(seq, size):
    '''Generator that cuts sequence (bytes, memoryview, etc.)
     into chunks of given size. If `seq` length is not multiply
     of `size`, the lengh of the last chunk returned will be
     less than requested.

     >>> list( chunks([1,2,3,4,5,6,7], 3) )
     [[1, 2, 3], [4, 5, 6], [7]]
    '''
    d, m = divmod(len(seq), size)
    for i in range(d):
        yield seq[i*size:(i+1)*size]
    if m:
        yield seq[d*size:]

def chunkread(f, size):
    '''Generator that reads from file like object. May return less
     data than requested on the last read.'''
    c = f.read(size)
    while len(c):
        yield c
        c = f.read(size)

def genchunks(mixed, size):
    '''Generator to chunk binary sequences or file like objects.
     The size of the last chunk returned may be less than
     requested.'''
    if hasattr(mixed, 'read'):
        return chunkread(mixed, size)
    else:
        return chunks(mixed, size)
# --- - /chunking helpers

def dump(binary, size=2, sep=' '):
    '''
    Convert binary data (bytes in Python 3 and str in
    Python 2) to hex string like '00 DE AD BE EF'.
    `size` argument specifies length of text chunks
    and `sep` sets chunk separator.
    '''
    hexstr = binascii.hexlify(binary)
    if sys.version_info[0] >= 3:
        hexstr = hexstr.decode('ascii')
    return sep.join(chunks(hexstr.upper(), size))


def my_hexdump(data, stride = 8):
    '''
    Generator that produces strings:

    '00000000: 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ................'
    '''
    generator = genchunks(data, stride)
    for addr, d in enumerate(generator):
        # 00000000:
        line = '%04X ' % (addr*stride)
        # 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00
        dumpstr = dump(d)
        line += dumpstr[:3 * (int(stride /2))]
        if len(d) > 3:  # insert separator if needed
            line += ' ' + dumpstr[3 * (int(stride / 2)):]
        # ................
        # calculate indentation, which may be different for the last line
        pad = 2
        #if len(d) < 16:
        #  pad += 3*(16 - len(d))
        #if len(d) <= 8:
        #  pad += 1
        line += ' '*pad

        for byte in d:
        # printable ASCII range 0x20 to 0x7E
            if sys.version_info[0] < 3:
                byte = ord(byte)
            if 0x20 <= byte <= 0x7E:
                line += chr(byte)
            else:
                line += '.'
        print(line)


# Main Classes

## Payload Class

class StoppableThread(threading.Thread):

    def __init__(self, **kwargs):
        super(StoppableThread, self).__init__(**kwargs)
        self._stop_event = threading.Event()
        self._reset_event = threading.Event()
        self._lock = threading.Lock()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def reset(self):
        self._reset_event.set()

    def is_reset(self):
        return self._reset_event.is_set()

    def clear_reset(self):
        self._reset_event.clear()

    def get_lock(self):
        self._lock.acquire()

    def release_lock(self):
        self._lock.release()

    def lock(self):
        return(self._lock)

#def hasSync(packet):
#	pa_bytes = bytes([0x6F,0x87,0x20])
#	return(bytes(packet["RTP"].payload).find(pa_bytes))


def get_next_pmd_timeslot(sampleCount):
    # Maintain 4 samples of zeros between burst and find start of the next time-slot
    return ((((sampleCount + 4) // 160) + 1) * 160) - sampleCount



def get_pmd_xml_from_wav(frame):
    pmd_tool_exec = os.path.dirname(__file__) + "/pmd_tool." + platform.system()
    if (platform.system() == 'Windows'):
        pmd_tool_exec = pmd_tool_exec + '.exe'
    if not os.path.exists(pmd_tool_exec):
        print("__file__:",__file__,"  pmd_tool path:", pmd_tool_exec)
        print("Platform", platform.system(), "not supported", file=sys.stderr)
        exit(-4)
    # Add preamble


    with wave.open("pmd.wav", "wb") as wave_file:
        wave_file.setnchannels(2)
        wave_file.setsampwidth(3)  # 24 bits / 3 bytes
        wave_file.setframerate(48000)

        # Start with zero padding from vSync
        sampleCount = 32
        wave_file.writeframes(bytes(sampleCount * 6))
        # Now add payloads
        for payload in frame.payloads:
            # swap to little endian as payload 24 is big endian as required for KLV
            # unfortunately wav is little so we have to swap here
            payload24_le = endian_swap24(payload)
            wave_file.writeframes(payload24_le)
            sampleCount = sampleCount + (len(payload24_le) // 6)
            # Add post frame seperator
            zeroPadSamples = get_next_pmd_timeslot(sampleCount)
            wave_file.writeframes(bytes(zeroPadSamples * 6))
            sampleCount = sampleCount + zeroPadSamples

    args = [pmd_tool_exec, "-i", "pmd.wav", "-o", "pmd.xml"]
    subprocess.run(args)
    if not os.path.exists("pmd.xml"):
        print("KLV to XML conversion failed. PMD is probably corrupted", file=sys.stderr)
        return False
    return True


def get_pmd_xml_from_klv(frame, pack20_flag):
    pmd_tool_exec = os.path.dirname(__file__) + "/pmd_tool." + platform.system()
    if platform.system() == 'Windows':
        pmd_tool_exec = pmd_tool_exec + '.exe'
    if not os.path.exists(pmd_tool_exec):
        print("__file__:",__file__,"  pmd_tool path:", pmd_tool_exec)
        print("Platform", platform.system(), "not supported", file=sys.stderr)
        exit(-4)

    if pack20_flag:
        klv_payload = pack_20bits(frame.payload)
    else:
        klv_payload = frame.payloads[0]
    with open("pmd.klv", "wb") as klv_file:
        klv_file.write(klv_payload)
    try:
        os.remove("pmd.xml")
    except:
        pass
    args = [pmd_tool_exec, "-i", "pmd.klv", "-o", "pmd.xml"]
    subprocess.run(args)
    if not os.path.exists("pmd.xml"):
        print("KLV to XML conversion failed. PMD is probably corrupted", file=sys.stderr)
        return False
    return True


def get_sadm_xml(frame):
    index = 0
    if frame.sADM_assemble_flag == 1:
        assemble_info = get_word(frame.payloads[0], index, False)
        in_timeline_flag = (assemble_info >> 4) & 0x3
        # Only support full frame mode so this must be 0
        if (in_timeline_flag != 0):
            return(None)
        #Commenting the next two elements out for speed as they are ignored
        #track_numbers = (assemble_info >> 6) & 0x3f
        #track_ID = (assemble_info >> 12) & 0x3f
        index = index + 3
    if frame.sADM_format_flag == 1:
        format_info = get_word(frame.payloads[0], index, False)
        format_type = format_info >> 4 & 0xf
        index = index + 3
    else:
        format_type = 0
    if format_type == 1:
        gzip_data = pack_20bits(frame.payloads[0][index:])
        try:
            adm_xml = zlib.decompress(gzip_data, 15 + 32)
        except:
            adm_xml = None
    else:
        adm_xml = frame.payloads[0][index:]
    return adm_xml

class State:
    IDLE = 16
    GOT_LEFT_BLANKING = 32
    GOT_RIGHT_BLANKING = 64
    GOT_FRAME_MODE_BLANKING = 128
    GOT_PA = 1
    GOT_SYNC = 2
    GOT_HEADER = 3
    GOT_PMD_FRAME = 4
    GOT_END_BLANKING = 5

class pmdDeframer:
 
    subframe_mode = None
    got_header = False
    length20=0
    length24=0
    data_type=0

    payloads = b''
    left_zero_count = 0
    right_zero_count = 0
    frame_mode_zero_count = 0
    end_zero_count = 0
    state = State.IDLE
    last_sequnce_no = None
    new_frames = []
    active_channel = False

    pa = 0x6f872
    pb = 0x54e1f
    zero_threshold = 350
    intraframe_zero_threshold = 160

    class NewFrame:
        payload = None
        format = None
        subframe_mode = None
        right_not_left = None
        sADM_assemble_flag = None
        sADM_format_flag = None

        def __init__(self):
            self.payloads = []
            self.format = None
            self.subframe_mode = None
            self.right_not_left = None
            self.sADM_assemble_flag = None
            self.sADM_format_flag = None

        def is_sADM(self):
            if self.format == "SADM":
                return True
            else:
                return False

        def is_pmd(self):
            if self.format == "PMD":
                return True
            else:
                return False

        def is_AESX242(self):
            if self.format == "AESX242":
                return True
            else:
                return False

        def get_sADM_assemble_flag(self):
            return self.sADM_assemble_flag

        def get_sADM_format_flag(self):
            return self.sADM_format_flag


    def __init__(self):
        self.subframe_mode = None
        self.got_header = False
        self.length20=0
        self.length24=0
        self.data_type=0

        self.payloads = b''
        self.left_zero_count = 0
        self.right_zero_count = 0
        self.frame_mode_zero_count = 0
        self.end_zero_count = 0
        self.state = State.IDLE
        self.last_sequnce_no = None
        self.new_frames = []
        self.next_frame = None
        self.active_channel = False

        self.pa = 0x6f872
        self.pb = 0x54e1f
        self.zero_threshold = 350
        self.intraframe_zero_threshold = 160



    def reset(self):
        self.subframe_mode = None
        self.got_header = False
        self.length20 = 0
        self.length24 = 0
        self.data_type = 0
        self.payloads = b''
        self.left_zero_count = 0
        self.right_zero_count = 0
        self.frame_mode_zero_count = 0
        self.end_zero_count = 0
        self.state = State.IDLE
        self.last_sequnce_no = None
        self.active_channel = False
        self.next_frame = None

    def receivePacket(self, packet, codec):
        if codec == "AM824":
            self.receiveSMPTEPacket(packet)
        elif codec == "smpte336m":
            self.receiveAESX242Packet(packet)
        else:
            raise("Unknown format")

    def receiveAESX242Packet(self, packet):
        packet["UDP"].payload = scapy.RTP(packet["Raw"].load)
        # detect marker bit to see if this is the first packet of the KLVunit
        if packet["RTP"].marker:
            # See if we already have a payload, if so then we can process it
            if len(self.payloads) > 0:
                next_frame = self.NewFrame()
                next_frame.format = "AESX242"
                next_frame.payloads = [self.payloads]
                self.new_frames.append(next_frame)
            self.payloads = bytes(packet["RTP"].payload)
        else:
            self.payloads = self.payloads + bytes(packet["RTP"].payload)

    # Receive raw packets as they are received
    def receiveSMPTEPacket(self, packet):

        # Force packet to be interpreted as RTP
        packet["UDP"].payload = scapy.RTP(packet["Raw"].load)
        packet_payload = bytes(packet["RTP"].payload)
        right_not_left = True
        if self.last_sequnce_no is None:
            self.last_sequnce_no = packet["RTP"].sequence
        elif packet["RTP"].sequence == (self.last_sequnce_no + 1) & 0xffff:
            self.last_sequnce_no = packet["RTP"].sequence
        else:
            self.reset()
        for index in range(0, len(packet_payload), 4):
            # If subframe mode is detected
            right_not_left = not right_not_left
            if self.subframe_mode:
                if not self.active_channel:
                    self.active_channel = True
                    continue
                else:
                    self.active_channel = False

            # Because we are aligned to the actual sync word we drop the fourth/last byte
            next_word = packet_payload[index + 1:index + 4]
            next_sample = int.from_bytes(next_word, byteorder='big') >> 4

            # Search for blanking period: 350 zeros
            if self.state & State.IDLE:
                if next_sample == 0:
                    if right_not_left:
                        self.right_zero_count = self.right_zero_count + 1
                        if self.right_zero_count >= self.zero_threshold:
                            self.state = self.state | State.GOT_RIGHT_BLANKING
                    else:
                        self.left_zero_count = self.left_zero_count + 1
                        if self.left_zero_count >= self.zero_threshold:
                            self.state = self.state | State.GOT_LEFT_BLANKING
                    self.frame_mode_zero_count = self.frame_mode_zero_count + 1

                    # If we've got enough zeros to know the first burst is next then move to next state
                    if self.frame_mode_zero_count >= self.zero_threshold:
                        self.state = self.state | State.GOT_FRAME_MODE_BLANKING

                    # Check to see if we have a PMD frame to release because we know there are no new payloads
                    if self.next_frame is not None and self.next_frame.is_pmd():
                        if self.next_frame.subframe_mode:
                            if self.next_frame.right_not_left and (self.right_zero_count > self.intraframe_zero_threshold):
                                self.next_frame.payloads.append(self.payloads)
                                self.new_frames.append(self.next_frame)
                                self.next_frame = None
                            if (not self.next_frame.right_not_left) and (self.left_zero_count > self.intraframe_zero_threshold):
                                self.next_frame.payloads.append(self.payloads)
                                self.new_frames.append(self.next_frame)
                                self.next_frame = None
                        else:
                            if self.right_zero_count > self.intraframe_zero_threshold and self.left_zero_count > self.intraframe_zero_threshold:
                                self.next_frame.payloads.append(self.payloads)
                                self.new_frames.append(self.next_frame)
                                self.next_frame = None
                else:
                    # reset parser until we find zeros
                    if right_not_left:
                        if next_sample == self.pa and (self.state & State.GOT_RIGHT_BLANKING):
                            self.state = State.GOT_PA
                            self.payloads = self.payloads + next_word
                        else:
                            self.right_zero_count = 0
                            self.frame_mode_zero_count = 0
                            self.state = self.state & ~(State.GOT_RIGHT_BLANKING + State.GOT_FRAME_MODE_BLANKING)
                    else:
                        if next_sample == self.pa and (self.state & State.GOT_LEFT_BLANKING):
                            self.state = State.GOT_PA
                            self.payloads = self.payloads + next_word
                        else:
                            self.left_zero_count = 0
                            self.frame_mode_zero_count = 0
                            # Remove word as not used
                            self.state = self.state & ~(State.GOT_LEFT_BLANKING + State.GOT_FRAME_MODE_BLANKING)

            elif self.state == State.GOT_PA:
                self.payloads = self.payloads + next_word
                frame_pos = len(self.payloads)
                if frame_pos == 6:
                    if next_sample == self.pb and right_not_left:
                        self.subframe_mode = False
                        self.state = State.GOT_SYNC
                elif frame_pos == 9:
                    if next_sample == self.pb:
                        self.subframe_mode = True
                        self.state = State.GOT_SYNC
                        # remove middle word from payload
                        self.payloads = self.payloads[0:3] + self.payloads[6:9]
                    else:
                        self.reset()
                else:
                    # should be reachable as reset above should be reached first
                    self.reset()

            elif self.state == State.GOT_SYNC:
                self.payloads = self.payloads + next_word
                if self.next_frame is None:
                    self.next_frame = self.NewFrame()
                # Check sequence otherwise if we are out of order mid-frame then errors
                # are certain so reset state machine and reacquire sync
                frame_pos = len(self.payloads)

                if frame_pos == 15:
                    Pc = get_word(self.payloads, 6, False)
                    self.data_type = (Pc & 0x01f0) >> 4
                    # If extended data type then add in Pe
                    if self.data_type == 31:
                        self.data_type = self.data_type + get_word(self.payloads, 12, False) & 0xffff
                    # 8 bits, scale up to 24 bits because we are not using packed 20 bits yet
                    Pd = get_word(self.payloads, 9, False)
                    self.length20 = int(Pd / 8)
                    # Ceil is used here so that if Pd is not divisible by 20 i.e. not whole number
                    # of 20 bit words then we get the extra partial word
                    self.length24 = int(math.ceil(Pd / 20.0)) * 3
                    # If subframe mode then we need twice as many samples to hold frame
                    if self.data_type == 27:
                        self.next_frame.format = "PMD"
                    if self.data_type == 32:
                        self.next_frame.format = "SADM"
                        self.next_frame.sADM_assemble_flag = (Pc >> 13) & 0x1
                        self.next_frame.sADM_format_flag = (Pc >> 14) & 0x1
                    # adjust for Pe & Pf
                    #if self.data_type > 30:
                        # adjust for Pe and Pf
                    #    self.length20 = self.length20 - 5
                    #    self.length24 = self.length24 - 6
                    self.state = State.GOT_HEADER
                    if (not (self.next_frame.is_pmd())) and (not (self.next_frame.is_sADM())):
                        # detected wrong SMPTE data type
                        self.reset()

            elif self.state == State.GOT_HEADER:
                self.payloads = self.payloads + next_word
                # See if we have complete frame
                if len(self.payloads) - 12 >= self.length24:
                    self.payloads = self.payloads[0: self.length24 + 12]
                    self.next_frame.subframe_mode = self.subframe_mode

                    # Don't signal new frame if pmd because we might have more payloads
                    if self.next_frame.is_pmd():
                        self.next_frame.payloads.append(self.payloads)
                        self.next_frame.right_not_left = right_not_left
                        # Hold reference to current frame across reset
                        temp_next_frame = self.next_frame
                        self.reset()
                        self.next_frame = temp_next_frame
                        # Set state according frame mode and location of Pa
                        if self.next_frame.subframe_mode and self.next_frame.right_not_left:
                            self.state = self.state + State.GOT_RIGHT_BLANKING
                        else:
                            self.state = self.state + State.GOT_LEFT_BLANKING
                    else:
                        # Strip header according to data type because of Pe/Pf
                        # [0] should be first word of SMPTE 337 payload
                        if self.data_type > 30:
                            self.next_frame.payloads.append(self.payloads[18:])
                        else:
                            self.next_frame.payloads.append(self.payloads[12:])
                        self.new_frames.append(self.next_frame)
                        self.reset()
            else:
                raise RuntimeError("Unknown State")

    def getFrame(self):
        if len(self.new_frames) > 0:
            return self.new_frames.pop(0)
        else:
            return None

    def haveFrame(self):
        return len(self.new_frames) > 0

# Main GUI App Class

class PmdAdmDisplayGUI:

    numObjects = 6
    numPresentations = 6
    numBeds = 4
    frameRelief = RAISED
    frameBg = "blue"
    frameBorderwidth = 5
    running = False
    stop = False
    interface = None
    interfaceName = ""
    mainThread = None
    serviceList = []
    serviceNameList = []
    audioList = []
    audioNameList = []
    selectedService = None
    audioService = None
    pmdIndVar = None
    sadmIndVar = None
    aesx242IndVar = None
    XMLViewerRequest = False
    discoveryService = None
    start_time = 0
    numCapturePackets = 42
    debug = False
    messageQueue = None
    multicast = None
    playbackPres = None
    playbackPresVar = None
    model = None
    audioPipeLine = None
    mixMatrix = None
    haveGstreamer = False
    lastModelUpdateTime = 0

    class Indicators:
        pmd = "gray"
        sadm = "gray"
        aesx242 = "gray"
        frame = "gray"
        subframe = "gray"
        gui = None

        def __init__(self, gui):
            self.gui = gui

        def reset(self):
            self.pmd = "gray"
            self.sadm = "gray"
            self.aesx242 = "gray"
            self.frame = "gray"
            self.subframe = "gray"
            self.gui.post("updateInd", None)

        def rxMetadata(self):
            return self.pmd =="light green" or self.sadm =="light green" or self.aesx242 =="light green"

        def pmdOn(self):
            if not self.pmd == "light green":
                self.pmd = "light green"
                self.sadm = "gray"
                self.aesx242 = "gray"
                self.gui.post("updateInd", None)

        def pmdError(self):
            if not self.pmd == "red":
                self.pmd = "red"
                self.sadm = "gray"
                self.aesx242 = "gray"
                self.gui.post("updateInd", None)

        def sadmOn(self):
            if not self.sadm == "light green":
                self.sadm = "light green"
                self.pmd = "gray"
                self.aesx242 = "gray"
                self.gui.post("updateInd", None)

        def sadmError(self):
            if not self.sadm == "red":
                self.sadm = "red"
                self.pmd = "gray"
                self.aesx242 = "gray"
                self.gui.post("updateInd", None)

        def aesx242On(self):
            if not self.aesx242 == "light green":
                self.aesx242 = "light green"
                self.pmd = "gray"
                self.sadm = "gray"
                self.frame = "gray"
                self.subframe = "gray"
                self.gui.post("updateInd", None)

        def aesx242Error(self):
            if not self.aesx242 == "red":
                self.aesx242 = "red"
                self.pmd = "gray"
                self.sadm = "gray"
                self.frame = "gray"
                self.subframe = "gray"
                self.gui.post("updateInd", None)


        def frameMode(self):
            if not self.frame == "light green":
                self.frame = "light green"
                self.subframe = "gray"
                self.gui.post("updateInd", None)

        def subFrameMode(self):
            if not self.subframe == "light green":
                self.subframe = "light green"
                self.frame = "gray"
                self.gui.post("updateInd", None)


    def __init__(self, master, xml_filename, sdp_filename, debug_mode):

        master.title("Audio Metadata Viewer v" + __version__)
        self.debug = debug_mode

        self.indFrame = Frame(master, relief=self.frameRelief, borderwidth=self.frameBorderwidth)
        self.indFrame.pack(fill=BOTH, expand=True)

        self.pmdInd = Label(self.indFrame, text='PMD', variable=self.pmdIndVar, fg='black')
        self.pmdInd.pack(side=LEFT)
        self.sadmInd = Label(self.indFrame, text='sADM', variable=self.sadmIndVar, fg='black')
        self.sadmInd.pack(side=LEFT)
        self.aesx242Ind = Label(self.indFrame, text='AES-X242', variable=self.aesx242IndVar, fg='black')
        self.aesx242Ind.pack(side=LEFT)

        self.FrameInd = Label(self.indFrame, text='Frame', fg='black')
        self.FrameInd.pack(side=LEFT)
        self.SubFrameInd = Label(self.indFrame, text='Subframe', fg='black')
        self.SubFrameInd.pack(side=LEFT)

        self.indicators = self.Indicators(self)

        audio_beds_label = Label(master, text="Audio Beds")
        audio_beds_label.pack(fill=X)

        self.abFrame = Frame(master, relief= self.frameRelief, borderwidth=self.frameBorderwidth)
        self.abFrame.pack(fill=BOTH, expand=True)

        abLabels = [ "Source", "Config", "Name", "Gain(dB)", "Start", "End" ]

        for abColumn in range(1,7):
            abLabel = Label(self.abFrame, text = abLabels[abColumn - 1])
            abLabel.grid(row = 0, column = abColumn)

        self.bedFields = [[] for i in range(self.numBeds + 1)]
        for bed in range(0,self.numBeds):

            bed_label = Label(self.abFrame, text = str(bed+1))
            bed_label.grid(row = bed + 1, column = 0)

            for abColumn in range(1,7):
                self.bedFields[bed].append(Label(self.abFrame, text = "None", relief=SUNKEN, bg = '#B3B4C8'))
                self.bedFields[bed][-1].grid(row = bed + 1, column = abColumn, sticky=N+E+S+W)

        for abColumn in range(0,7):
            self.abFrame.grid_columnconfigure(abColumn,minsize = 100)

        audio_objects_label = Label(master, text="Audio Objects")
        audio_objects_label.pack(fill=X)

        self.aoFrame = Frame(master, relief=RAISED, borderwidth=5)
        self.aoFrame.pack(fill=BOTH, expand=True)

        aoLabels = [ "Type", "Name", "Diverge", "Ch", "Gain(dB)", "X", "Y", "Z" ]

        for aoColumn in range(1, len(aoLabels) + 1):
            aoLabel = Label(self.aoFrame, text = aoLabels[aoColumn - 1])
            aoLabel.grid(row = 0, column = aoColumn)

        self.objectFields = [[] for i in range(self.numObjects)]
        for aoObject in range(0,self.numObjects):
            audio_object_number_label = Label(self.aoFrame, text = str(aoObject + 1))
            audio_object_number_label.grid(row = aoObject + 1, column = 0)

            for aoColumn in range(1, len(aoLabels) + 1):
                self.objectFields[aoObject].append(Label(self.aoFrame, justify = LEFT, text = "None", relief=SUNKEN, bg = '#B3B4C8'))
                self.objectFields[aoObject][-1].grid(row = aoObject + 1, column = aoColumn, sticky=N+E+S+W)

        for aoColumn in range(0, len(aoLabels) + 1):
            self.aoFrame.grid_columnconfigure(aoColumn,minsize = 100)

        presentations_label = Label(master, text="Presentations")
        presentations_label.pack(fill=X)

        self.presFrame = Frame(master, relief=RAISED, borderwidth=5)
        self.presFrame.pack(fill=BOTH, expand=True)

        presLabels = ["Name", "NameLang", "Bed Element", "Target Cfg", "Object Elements", "PresLang"]

        for presColumn in range(1, len(presLabels) + 1):
            presLabel = Label(self.presFrame, text = presLabels[presColumn - 1])
            presLabel.grid(row = 0, column = presColumn)

        self.presFields = [[] for i in range(self.numPresentations)]
        self.oeFrames = []
        self.objectElements = [[] for i in range(self.numObjects)]
        self.oeVars = [[] for i in range(self.numObjects)]
        self.playbackPresVar = IntVar(master)
        self.playbackPresVar.set(None)
        self.presButtons = []
        for presentation in range(0, self.numPresentations):
            self.presButtons.append(Radiobutton(self.presFrame, variable=self.playbackPresVar, state=DISABLED, command=self.playback_button, text=str(presentation + 1), indicatoron=0, value=presentation + 1))
            self.presButtons[-1].grid(row=presentation + 1, column=0, sticky=N+E+S+W)

            # First do regular indicator labels
            for presColumn in [1,2,3,4,6]:
                self.presFields[presentation].append(Label(self.presFrame, text = "None", relief=SUNKEN, bg = '#B3B4C8'))
                self.presFields[presentation][-1].grid(row = presentation + 1, column = presColumn, sticky=N+E+S+W)

            # Now indicators for object elements
            self.oeFrames.append(Frame(self.presFrame))
            self.oeFrames[-1].grid(row = presentation + 1, column = 5)
            for indicator in range(1,self.numObjects + 1):
                self.oeVars[presentation].append(IntVar())
                self.oeVars[presentation][indicator - 1].set(0);
                self.objectElements[presentation].append(Checkbutton(self.oeFrames[-1],state=DISABLED, variable = self.oeVars[presentation][indicator - 1]))
                self.objectElements[presentation][-1].pack(side=LEFT)

            for presColumn in range(0, len(presLabels) + 1):
                self.presFrame.grid_columnconfigure(presColumn, minsize = 100)

        button = Button(master, text="Run", command=self.run)
        button.pack(side=LEFT)


        button = Button(master, text="Quit", command=self.quit)
        button.pack(side=LEFT)

        if self.debug:
            button = Button(master, text="Memory", command=self.memoryDebug)
            button.pack(side=LEFT)

        # If a filename was specified then load it into UI, otherwise just wait for run to pressed to search for service
        if xml_filename is not None:
            if isFilePmd(xml_filename):
                try:
                    self.model = parse_pmd_xml(xml_filename, PMD_XML_MODE_FILE)
                    xml_filename.seek(0)
                except:
                    raise RuntimeError("Recognized file as PMD but parsing failed")
            elif isFileSADM(xml_filename):
                try:
                    self.model = populate_model_from_adm(xml_filename, ADM_XML_MODE_FILE)
                except:
                    raise RuntimeError("Recognized file as ADM but parsing failed")
            else:
                raise("File format not recognized")
            self.updateFromModel(self.model)
        else:
            # Create Drop down for IP Interfaces
            if platform.system() == 'Windows':
                fullIfListNames = [x['name'] for x in scapy.get_windows_if_list()]
                fullIfListGuids = [x['guid'] for x in scapy.get_windows_if_list()]
#				#full_ifList = netifaces.interfaces()
            else:
                fullIfListNames = scapy.get_if_list()

            # Filter interfaces according to those that have

            ifList = []
            if platform.system() == 'Windows':
                for iface in range(0,len(fullIfListNames)):
                    name = fullIfListNames[iface]
                    guid = fullIfListGuids[iface]
                    if netifaces.ifaddresses(guid).get(netifaces.AF_INET) != None and ("Loopback" not in name):
                        ifList.append(name)
            else:
                for iface in fullIfListNames:
                    if netifaces.ifaddresses(iface).get(netifaces.AF_INET) != None and iface != 'lo0' and iface != 'lo':
                        ifList.append(iface)

            # Now we have a list of interfaces, create Drop-down menu to select interface
            self.interface = StringVar(master)
            if ifList is not []:
                self.interface.set(ifList[-1])
                self.ifList = OptionMenu(master, self.interface, *ifList, command=self.setInterfaceName)
                self.ifList.pack(side=LEFT)
            self.interfaceName = self.interface.get()

        label = Label(master, text="Service:")
        label.pack(side=LEFT)
        self.serviceSelection = StringVar(master)
        #self.serviceSelection.set(self.serviceNameList[0])
        self.serviceMenu = OptionMenu(master, self.serviceSelection, "Service")
        self.serviceMenu.pack(side=LEFT)
        label = Label(master, text="Audio:")
        label.pack(side=LEFT)
        self.audioSelection = StringVar(master)
        self.audioMenu = OptionMenu(master, self.audioSelection, "Audio")
        self.audioMenu.pack(side=LEFT)

        button = Button(master, text="XML", command=self.view_XML)
        button.pack(side=LEFT)

        # Now that the GUI is complete it is safe to start discovery
        # Option menu must exist first so this can't be moved up

        # Make sure a main thread exists so it is able to accept messages, even if it is not started

        self.messageQueue = queue.Queue()
        self.discoveryService = aoip_services.aoip_discovery.aoip_discovery(self.discoveryCallback, [self.interface.get()])
        # If an SDP file was provided then add an additional service based on the file
        if sdp_filename is not None:
            self.discoveryService.add_aoip_service_from_sdp_file(sdp_filename)
        # This object is needed for joins and leaves
        self.multicast = aoip_services.multicast.MulticastGroup()

        try:
        	shellState = (platform.system() == "Windows")
        	self.haveGstreamer = ((subprocess.call(["gst-launch-1.0", "--version"], shell=shellState, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)) == 0)
        except OSError as e:
        	if e.errno == errno.ENOENT:
        		self.haveGstreamer = False
        	else:
        		# Something else went wrong while trying to check for gstreamer
        		raise
        		self.haveGstreamer = False

    def post(self, command, data):
        # If the packet processor is running faster than the UI background task
        # then UI updates are dropped
        # This avoids the UI lagging behind and a memory leak with an ever increasing queue of models
        if self.messageQueue.qsize() < 5 or command != "updateModel":
            self.messageQueue.put([command,data])

    def messageWaiting(self):
        return not self.messageQueue.empty()

    def getMessage(self):
        if self.messageQueue.empty():
            return None
        else:
            return self.messageQueue.get()

    def discoveryCallback(self, newService):
        self.post("newService", newService)

    def setInterfaceName(self, selected):
        self.interfaceName = self.interface.get()
        self.discoveryService.remove_all_interfaces()
        self.discoveryService.add_interface(self.interface.get())


    # This call provides a service that can be used to update the elements in the display
    # A task is created that sniffs packets and updates the parameters
    def set_service(self, service):
        # If we don't have a main thread then create one
        # If we do then signal it to stop
        self.multicast.leave()
        if self.mainThread is None:
            self.mainThread = StoppableThread(target = self.mainStart)
            self.service = service
            self.mainThread.start()
        else:
            self.service = service
            self.mainThread.reset()
        # The interface name that the multicast module needs has to be able to be used with sockets
        # which has a different format for Windows vs POSIX
        if platform.system() == "Windows":
            socketIfName = [x['guid'] for x in scapy.get_windows_if_list() if x['name'] == self.interfaceName][0]
        else:
            socketIfName = self.interfaceName
        self.multicast.join(socketIfName, self.service.sdp.address, self.service.sdp.port)

    def playback_button(self):
        if (self.playbackPres == self.playbackPresVar.get()):
            self.presButtons[self.playbackPres - 1].deselect()
            self.playbackPres = None
            # Stop playback here
        else:
            # Start playback here
            # First check to see if we are in a valid state to start playback
            # Check we are receiving metadata and an audio stream has been selected
            # This is enough to get started. Checking will happen as audio is brought up
            # If not then deselect
            # If the user has somehow managed to click a button that should be inactive then revert
            # this case should be unreachable
            if self.playbackPresVar.get() > len(self.model.audio_presentations):
                self.presButtons[self.playbackPresVar.get() - 1].deselect()
                if self.playbackPres is not None:
                    self.playbackPresVar.set(self.playbackPres)

            if self.indicators.rxMetadata() and self.audioSelection is not None:
                self.playbackPres = self.playbackPresVar.get()
                self.audioService = self.audioList[self.audioNameList.index(self.audioSelection.get())]
            else:
                self.presButtons[self.playbackPres - 1].deselect()
                self.playbackPres = None
                self.stop_playback()

    def pollPlayback(self):
        if self.playbackPres is not None:
            success = self.start_playback()
            # Playback can fail for many reasons, mostly invalid or changed metadata
            # Playback should stop and reach safe state
            if not success:
                #Not is main loop so can't deselect
                #self.presButtons[self.playbackPres - 1].deselect()
                self.stop_playback()
                self.playbackPres = None
        elif self.playing():
            self.stop_playback()


    def get_launch_str(self):
        # Now construct string to pass to gstreamer launch
        buffer_time = 0.6
        buffer_size = buffer_time * self.audioService.sdp.fs * self.audioService.sdp.channels
        if self.audioService.sdp.codec == 'L24':
            buffer_size = int(buffer_size * 3)
        else:
            buffer_size = int(buffer_size * 2)
        launchstr = 'udpsrc address=' + self.audioService.sdp.address + ' port=' + str(self.audioService.sdp.port) + \
                    ' buffer-size=' + str(buffer_size) + ' caps="application/x-rtp, media=(string)audio, clock-rate=(int)' + \
                    str(self.audioService.sdp.fs) + ', channels = ' + str(self.audioService.sdp.channels) + ', encoding-name=(string)' + \
                    self.audioService.sdp.codec + '" ! rtp' + self.audioService.sdp.codec + 'depay '
        if self.audioService.sdp.channels > 8:
                    launchstr = launchstr + '! audio/x-raw,channels=' + \
                    str(self.audioService.sdp.channels) + ',channel-mask=(bitmask)0x000000000000 '
        launchstr = launchstr + '! audioconvert mix-matrix="<<'
        for outchan in [0, 1]:
            for inchan in range(self.audioService.sdp.channels):
                launchstr = launchstr + '(float)' + str(self.mixMatrix[outchan][inchan]) + ', '
            launchstr = launchstr.rstrip(', ')
            launchstr = launchstr + '>, <'
        launchstr = launchstr.rstrip('>, <')
        launchstr = launchstr + '>>" ! playsink volume = 5 channels = 2'
        #launchstr = 'udpsrc address=239.150.138.1 port=5004 buffer-size=1000000 caps="application/x-rtp, media=(string)audio, clock-rate=(int)48000, channels = 9, encoding-name=(string)L16" ! rtpL16depay ! audio/x-raw,channels=9,channel-mask=(bitmask)0x000000000000 ! audioconvert mix-matrix="<<(float)1.0, (float)0.0, (float)1.0, (float)0.0, (float)1.0, (float)0.0, (float)1.0, (float)0.0, (float)0.0>, <(float)0.0, (float)1.0, (float)1.0, (float)0.0, (float)0.0, (float)1.0, (float)1.0, (float)0.0, (float)0.0>>" ! playsink volume = 5 channels = 2'
        return(launchstr)

    def start_playback(self):
        # Create mixing matrix by first adding in beds
        # Check that beds do not exceed total number of audio channels
        # Create empty mixing matrix

        # Stereo output only,
        newMixMatrix = [[0] * self.audioService.sdp.channels, [0] * self.audioService.sdp.channels]
        m3db = 0.7071
        bedCount = 0
        # audioScale is a value to ensure that matrix coefficients can never exceed 1.0
        # This is a universal gain that is determined by calculating worst case for a coefficient (currently +6dB)
        # and ensuring that this worst case is still less than < 1.0
        audioScale = 0.5011 # -6dB
        # If presentation was deleted then the playbackPres may be now invalid
        if self.playbackPres > len(self.model.audio_presentations):
            return False
        for element in self.model.audio_presentations[self.playbackPres - 1].elements:
            if type(element) is AudioBed and bedCount < self.numBeds:
                # We have a bed so mix
                startChannel = int(element.output_targets[0].audio_signals[0].id - 1)
                endChannel = int(element.output_targets[0].audio_signals[0].id + \
                             PRESENTATION_CONFIG_EQUIV[PRESENTATION_CONFIG_TEXT.index(element.speaker_config)] - 2)
                # Check that bed does not extend beyond audio service
                if endChannel <= startChannel or endChannel > self.audioService.sdp.channels:
                    return False
                bedAudioScale = audioScale * gain_from_db(element.gain_db)
                if element.speaker_config == LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_NAMES[LOUDSPEAKER_CONFIG_2_0]:
                    newMixMatrix[0][startChannel] = bedAudioScale 
                    newMixMatrix[1][startChannel + 1] = bedAudioScale 
                elif element.speaker_config == LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_NAMES[LOUDSPEAKER_CONFIG_3_0]:
                    newMixMatrix[0][startChannel] = bedAudioScale 
                    newMixMatrix[1][startChannel + 1] = bedAudioScale 
                    newMixMatrix[0][startChannel + 2] = m3db * bedAudioScale 
                    newMixMatrix[1][startChannel + 2] = m3db * bedAudioScale 
                elif element.speaker_config == LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_NAMES[LOUDSPEAKER_CONFIG_5_1]:
                    newMixMatrix[0][startChannel] = bedAudioScale 
                    newMixMatrix[1][startChannel + 1] = bedAudioScale 
                    newMixMatrix[0][startChannel + 2] = m3db * bedAudioScale
                    newMixMatrix[1][startChannel + 2] = m3db * bedAudioScale
                    newMixMatrix[0][startChannel + 4] = m3db * bedAudioScale
                    newMixMatrix[1][startChannel + 5] = m3db * bedAudioScale
                # unsupported bed configuration
                elif element.speaker_config == LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_NAMES[LOUDSPEAKER_CONFIG_5_1_2]:
                    newMixMatrix[0][startChannel] = bedAudioScale
                    newMixMatrix[1][startChannel + 1] = bedAudioScale
                    newMixMatrix[0][startChannel + 2] = m3db * bedAudioScale
                    newMixMatrix[1][startChannel + 2] = m3db * bedAudioScale
                    newMixMatrix[0][startChannel + 4] = m3db * bedAudioScale
                    newMixMatrix[1][startChannel + 5] = m3db * bedAudioScale
                    newMixMatrix[0][startChannel + 6] = 0.5 * bedAudioScale
                    newMixMatrix[1][startChannel + 7] = 0.5 * bedAudioScale
                elif element.speaker_config == LOUDSPEAKER_CONFIG_COMMON_USE_TEXT_NAMES[LOUDSPEAKER_CONFIG_5_1_4]:
                    newMixMatrix[0][startChannel] = bedAudioScale
                    newMixMatrix[1][startChannel + 1] = bedAudioScale
                    newMixMatrix[0][startChannel + 2] = m3db * bedAudioScale
                    newMixMatrix[1][startChannel + 2] = m3db * bedAudioScale
                    newMixMatrix[0][startChannel + 4] = m3db * bedAudioScale
                    newMixMatrix[1][startChannel + 5] = m3db * bedAudioScale
                    newMixMatrix[0][startChannel + 6] = 0.5 * bedAudioScale
                    newMixMatrix[1][startChannel + 7] = 0.5 * bedAudioScale
                    newMixMatrix[0][startChannel + 8] = 0.5 * bedAudioScale
                    newMixMatrix[1][startChannel + 9] = 0.5 * bedAudioScale
                else:
                    return False
            if type(element) == AudioObject:
                # Check that audio object channel is not outside audio service
                if element.audio_signal.id > self.audioService.sdp.channels:
                    return False
                # Calculate Lo & Ro gains from X,Y,Z
                yz_prod = ((0.207 * element.elevation_or_y) + 0.5) * (m3db - (m3db * element.distance_or_z))
                newMixMatrix[0][element.audio_signal.id - 1] = (0.603 - (0.603 * element.azimuth_or_x)) * yz_prod * gain_from_db(element.source_gain_db) * audioScale
                newMixMatrix[1][element.audio_signal.id - 1] = (0.603 + (0.603 * element.azimuth_or_x)) * yz_prod * gain_from_db(element.source_gain_db) * audioScale

        # If pipeline is not playing or matrix has changed size then
        if not self.playing():
            self.mixMatrix = newMixMatrix
            launchstr = self.get_launch_str()
            self.launch_pipeline(launchstr)
        else:
            if len(newMixMatrix) != len(self.mixMatrix) or len(newMixMatrix[0]) != len(self.mixMatrix[0]):
                self.mixMatrix = newMixMatrix
                launchstr = self.get_launch_str()
                self.launch_pipeline(launchstr)
            else:
                # compare matrices
                diff = 0
                for row in range(len(newMixMatrix)):
                    for col in range(len(newMixMatrix[0])):
                        diff = diff + abs(newMixMatrix[row][col] - self.mixMatrix[row][col])
                if diff > 0.001:
                    self.mixMatrix = newMixMatrix
                    launchstr = self.get_launch_str()
                    self.launch_pipeline(launchstr)

        # Indicate that playback started successfully
        return True

    def launch_pipeline(self, launchstr):
        args = ['gst-launch-1.0', '-q']
        args = args + launchstr.split()
        shellState = (platform.system() == "Windows")
        newAudioPipeLine = subprocess.Popen(args, shell=shellState, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if self.audioPipeLine is not None:
            self.stop_playback()
        self.audioPipeLine = newAudioPipeLine

    def playing(self):
        return self.audioPipeLine is not None

    def stop_playback(self):
        if self.audioPipeLine is not None:
            if (platform.system() == "Windows"):
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.audioPipeLine.pid)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            else:
                os.kill(self.audioPipeLine.pid, signal.SIGSTOP)
                os.kill(self.audioPipeLine.pid, signal.SIGKILL)
        self.audioPipeLine = None

    def reset_ui(self):
        # Reset lights
        self.indicators.reset()

        # Reset Metadata display

        for ununsedBeds in range(0,self.numBeds):
                self.bedFields[ununsedBeds][AudioBedHeadings.SOURCE].configure(text="")
                self.bedFields[ununsedBeds][AudioBedHeadings.CONFIG].configure(text="")
                self.bedFields[ununsedBeds][AudioBedHeadings.NAME].configure(text="")
                self.bedFields[ununsedBeds][AudioBedHeadings.GAIN].configure(text="")
                self.bedFields[ununsedBeds][AudioBedHeadings.START].configure(text="")
                self.bedFields[ununsedBeds][AudioBedHeadings.END].configure(text="")

        for unusedObject in range(0,self.numObjects):
                self.objectFields[unusedObject][AudioObjectHeadings.TYPE].configure(text="")
                self.objectFields[unusedObject][AudioObjectHeadings.NAME].configure(text="")
                self.objectFields[unusedObject][AudioObjectHeadings.DIVERGE].configure(text="")
                self.objectFields[unusedObject][AudioObjectHeadings.CH].configure(text="")
                self.objectFields[unusedObject][AudioObjectHeadings.GAIN].configure(text="")
                self.objectFields[unusedObject][AudioObjectHeadings.X].configure(text="")
                self.objectFields[unusedObject][AudioObjectHeadings.Y].configure(text="")
                self.objectFields[unusedObject][AudioObjectHeadings.Z].configure(text="")

        for unusedPresentations in range(0,self.numPresentations):
            self.presButtons[unusedPresentations]['state'] = 'disabled'
            self.presFields[unusedPresentations][PresentationHeadings.NAME].configure(text="")
            self.presFields[unusedPresentations][PresentationHeadings.NAME_LANG].configure(text="")
            self.presFields[unusedPresentations][PresentationHeadings.TARGET_CFG].configure(text="")
            self.presFields[unusedPresentations][PresentationHeadings.PRES_LANG].configure(text="")
            self.presFields[unusedPresentations][PresentationHeadings.BED_ELEMENT].configure(text="")

            for i in range(0,self.numObjects):
                self.oeVars[unusedPresentations][i].set(0)


    def quit(self):
        # Stop discovery
        self.multicast.leave()
        self.discoveryService.stop()
        self.playbackPres = None
        if self.playing():
            self.stop_playback()
        #shut down main thread if it is running
        if self.mainThread is not None and not self.mainThread.stopped():
            # Signal main Thread to Step
            self.mainThread.stop()
        else:
            self.post("quit", None)

    # Based on the selected service, set it as active
    def run(self):
        if len(self.serviceNameList) > 0:
            #service = self.serviceSelection.get()
            #name = self.serviceNameList.index(service)
            self.set_service(self.serviceList[self.serviceNameList.index(self.serviceSelection.get())])

    def memoryDebug(self):
        key_type='lineno'
        limit=10
        snapshot = tracemalloc.take_snapshot()
        snapshot = snapshot.filter_traces((tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),tracemalloc.Filter(False, "<unknown>")))
        top_stats = snapshot.statistics(key_type)
        print("Top %s lines" % limit)
        print('{: <10}'.format("index"),'{: <40}'.format("filename"), '{: <10}'.format("line no"),'{: <10}'.format("size kB"))
        for index, stat in enumerate(top_stats[:limit], 1):
            frame = stat.traceback[0]
            filename = os.sep.join(frame.filename.split(os.sep)[-2:])
            print('{: <10}'.format(index),'{: <40}'.format(filename), '{: <10}'.format(frame.lineno),'{:0.1f}'.format(stat.size / 1024),"kB")
            line = linecache.getline(frame.filename, frame.lineno).strip()
            if line:
                print('    %s' % line)
        other = top_stats[limit:]
        if other:
            size = sum(stat.size for stat in other)
            print("%s other: %.1f KiB" % (len(other), size / 1024))
        total = sum(stat.size for stat in top_stats)
        print("Total allocated size: %.1f KiB" % (total / 1024))

    def view_XML(self):
        self.XMLViewerRequest = True

    def updateFromModel(self, model):
        objectCount = 0
        objectIdList = []
        bedCount = 0
        for element in model.audio_elements:
            if (type(element) is AudioObject) and (objectCount < self.numObjects):
                if element.classification < len(OBJECT_CLASSES):
                    self.objectFields[objectCount][AudioObjectHeadings.TYPE].configure(text=OBJECT_CLASSES[element.classification])
                self.objectFields[objectCount][AudioObjectHeadings.NAME].configure(text=element.name)
                if element.diverge == 1:
                    self.objectFields[objectCount][AudioObjectHeadings.DIVERGE].configure(text="True")
                else:
                    self.objectFields[objectCount][AudioObjectHeadings.DIVERGE].configure(text="False")
                if element.audio_signal is not None:
                    self.objectFields[objectCount][AudioObjectHeadings.CH].configure(text=element.audio_signal.id)
                else:
                    self.objectFields[objectCount][AudioObjectHeadings.CH].configure(text="")
                self.objectFields[objectCount][AudioObjectHeadings.GAIN].configure(text=element.source_gain_db)
                self.objectFields[objectCount][AudioObjectHeadings.X].configure(text=element.azimuth_or_x)
                self.objectFields[objectCount][AudioObjectHeadings.Y].configure(text=element.elevation_or_y)
                self.objectFields[objectCount][AudioObjectHeadings.Z].configure(text=element.distance_or_z)
                objectIdList.append(element.id)
                objectCount = objectCount + 1
            if type(element) is AudioBed and bedCount < self.numBeds:
                self.bedFields[bedCount][AudioBedHeadings.SOURCE].configure(text="Direct")
                self.bedFields[bedCount][AudioBedHeadings.CONFIG].configure(text=element.speaker_config)
                self.bedFields[bedCount][AudioBedHeadings.NAME].configure(text=element.name)
                self.bedFields[bedCount][AudioBedHeadings.GAIN].configure(text=element.gain_db)
                self.bedFields[bedCount][AudioBedHeadings.START].configure(text=element.output_targets[0].audio_signals[0].id)
                self.bedFields[bedCount][AudioBedHeadings.END].configure(text=element.output_targets[0].audio_signals[0].id +
                    PRESENTATION_CONFIG_EQUIV[PRESENTATION_CONFIG_TEXT.index(element.speaker_config)] - 1)
                bedCount = bedCount + 1

        for ununsedBeds in range(bedCount, self.numBeds):
                self.bedFields[ununsedBeds][AudioBedHeadings.SOURCE].configure(text="")
                self.bedFields[ununsedBeds][AudioBedHeadings.CONFIG].configure(text="")
                self.bedFields[ununsedBeds][AudioBedHeadings.NAME].configure(text="")
                self.bedFields[ununsedBeds][AudioBedHeadings.GAIN].configure(text="")
                self.bedFields[ununsedBeds][AudioBedHeadings.START].configure(text="")
                self.bedFields[ununsedBeds][AudioBedHeadings.END].configure(text="")

        for unusedObject in range(objectCount, self.numObjects):
                self.objectFields[unusedObject][AudioObjectHeadings.TYPE].configure(text="")
                self.objectFields[unusedObject][AudioObjectHeadings.NAME].configure(text="")
                self.objectFields[unusedObject][AudioObjectHeadings.DIVERGE].configure(text="")
                self.objectFields[unusedObject][AudioObjectHeadings.CH].configure(text="")
                self.objectFields[unusedObject][AudioObjectHeadings.GAIN].configure(text="")
                self.objectFields[unusedObject][AudioObjectHeadings.X].configure(text="")
                self.objectFields[unusedObject][AudioObjectHeadings.Y].configure(text="")
                self.objectFields[unusedObject][AudioObjectHeadings.Z].configure(text="")

        presentationCount = 0
        for presentation in model.audio_presentations:
            if presentationCount < self.numPresentations:
                if len(presentation.name_language) > 0:
                    self.presFields[presentationCount][PresentationHeadings.NAME].configure(text=presentation.name_language[0].name)
                    self.presFields[presentationCount][PresentationHeadings.NAME_LANG].configure(text=presentation.name_language[0].language)
                else:
                    self.presFields[presentationCount][PresentationHeadings.NAME].configure(text="")
                    self.presFields[presentationCount][PresentationHeadings.NAME_LANG].configure(text="")
                self.presFields[presentationCount][PresentationHeadings.TARGET_CFG].configure(text=presentation.config)
                self.presFields[presentationCount][PresentationHeadings.PRES_LANG].configure(text=presentation.language)
                objectIncludeList = [0] * self.numObjects
                for element in presentation.elements:
                    if type(element) == AudioObject:
                        objectIncludeList[objectIdList.index(element.id)] = 1
                    if type(element) == AudioBed:
                        self.presFields[presentationCount][PresentationHeadings.BED_ELEMENT].configure(text=element.name)
                for i in range(0, self.numObjects):
                    self.oeVars[presentationCount][i].set(objectIncludeList[i])
                if self.presButtons[presentationCount]['state'] == 'disabled' and self.haveGstreamer:
                    self.presButtons[presentationCount]['state'] = 'normal'
                presentationCount = presentationCount + 1

        for unusedPresentations in range(presentationCount, self.numPresentations):
            self.presButtons[unusedPresentations]['state'] = 'disabled'
            self.presFields[unusedPresentations][PresentationHeadings.NAME].configure(text="")
            self.presFields[unusedPresentations][PresentationHeadings.NAME_LANG].configure(text="")
            self.presFields[unusedPresentations][PresentationHeadings.TARGET_CFG].configure(text="")
            self.presFields[unusedPresentations][PresentationHeadings.PRES_LANG].configure(text="")
            self.presFields[unusedPresentations][PresentationHeadings.BED_ELEMENT].configure(text="")

            for i in range(0, self.numObjects):
                self.oeVars[unusedPresentations][i].set(0)

    def processNextMessage(self, master):
        if self.messageWaiting():
            [command,messageData] = self.getMessage()
            if command == "newService":
                newService = messageData
                if newService.sdp.isAM824() or newService.sdp.isAESX242():
                    if self.debug:
                        print("Found ", newService.system, " Service ", newService.name)
                    self.serviceList.append(newService)
                    self.serviceNameList.append(newService.system + ':' + newService.name)
                    # Check if this is the first service, if so display it
                    if len(self.serviceNameList) == 1:
                        self.serviceSelection.set(self.serviceNameList[0])
                    # Now update GUI menu
                    self.serviceMenu['menu'].delete(0, 'end')
                    for service in self.serviceNameList:
                        self.serviceMenu['menu'].add_command(label=service, command=lambda value=service: self.serviceSelection.set(value))
                    # Set capture period according to received service type
                    if newService.sdp.isAESX242():
                        self.numCapturePackets = 1
                    else:
                        self.numCapturePackets = 42
                elif newService.sdp.isAES67():
                    self.audioList.append(newService)
                    self.audioNameList.append(newService.system + ':' + newService.name)
                    # Check if this is the first service, if so display it
                    if len(self.audioNameList) == 1:
                        self.audioSelection.set(self.audioNameList[0])
                    # Now update GUI menu
                    self.audioMenu['menu'].delete(0, 'end')
                    for service in self.audioNameList:
                        self.audioMenu['menu'].add_command(label=service, command=lambda value=service: self.audioSelection.set(value))

            if command == "reset":
                self.reset_ui()
            if command == "quit":
                master.quit()
                master.destroy()
                # Signal to main loop to quit
                return False
            if command == "PMD XML":
                XMLWindow = Toplevel(master)
                XMLWindow.geometry("1000x1000")
                XML_Viewer(XMLWindow, messageData, heading_text=" Audio Metadata Viewer  ").pack()
                self.XMLViewerRequest = False
            if command == "ADM XML":
                XMLWindow = Toplevel(master)
                XMLWindow.geometry("1500x1000")
                XML_Viewer(XMLWindow, messageData, heading_text=" Audio Metadata Viewer  ").pack()
                self.XMLViewerRequest = False
            if command == "updateModel":
                self.updateFromModel(messageData)
                self.lastModelUpdateTime = time.time()
            if command == "updateInd":
                self.pmdInd.config(bg=self.indicators.pmd)
                self.sadmInd.config(bg=self.indicators.sadm)
                self.aesx242Ind.config(bg=self.indicators.aesx242)
                self.FrameInd.config(bg=self.indicators.frame)
                self.SubFrameInd.config(bg=self.indicators.subframe)
        # Check to see if model has timed out, Using 2 second timeout for UI
        if (self.lastModelUpdateTime > 0) and (time.time() > (self.lastModelUpdateTime + 2.0)):
            self.reset_ui()
            self.lastModelUpdateTime = 0
            
           
        return True

    def mainStart(self):
        while not self.mainThread.stopped():
            deframer = pmdDeframer()
            self.post("reset", None)
            self.mainThread.clear_reset()

            while not (self.mainThread.is_reset() or self.mainThread.stopped()):
                    try:
                        packets = scapy.sniff(iface=self.interfaceName, filter="ip dst " + self.service.sdp.address + " and udp dst port " + str(self.service.sdp.port), count=self.numCapturePackets, timeout=1)
                    except RuntimeError as e:
                        print(e)
                        packets = []
                        print("Error capturing packets...Stopping Capture")
                        self.mainThread.stop();
                    if len(packets) > 0:
                        for packet in packets:
                            if packet["UDP"].dport == self.service.sdp.port:
                                deframer.receivePacket(packet, self.service.sdp.codec)
                            if deframer.haveFrame():
                                break
                        if deframer.haveFrame():
                            newFrame = deframer.getFrame()
                            try:
                                if newFrame.is_pmd():
                                    if get_pmd_xml_from_wav(newFrame):
                                        if (check_xml_complete()):
                                            try:
                                                self.model = parse_pmd_xml("pmd.xml", PMD_XML_MODE_FILE)
                                            except:
                                                self.indicators.pmdError()
                                                raise RuntimeError("PMD XML parsing failed!")
                                            self.post("updateModel", copy.deepcopy(self.model))
                                            self.indicators.pmdOn()
                                    else:
                                        self.indicators.pmdError()
                                        raise RuntimeError("PMD conversion to XML failed!")
                                elif newFrame.is_sADM():
                                    xmlText = get_sadm_xml(newFrame)
                                    if xmlText is not None:
                                        try:
                                            #model = populate_model_from_adm("sadm.xml", ADM_XML_MODE_FILE)
                                            self.model = populate_model_from_adm(xmlText, ADM_XML_MODE_STRING)
                                        except:
                                            self.indicators.sadmError()
                                            raise RuntimeError("SADM XML parsing failed")
                                        self.post("updateModel", copy.deepcopy(self.model))
                                        self.indicators.sadmOn()
                                    else:
                                        self.indicators.sadmError()
                                        raise RuntimeError("SADM conversion to XML failed!")
                                elif newFrame.is_AESX242():
                                    if get_pmd_xml_from_klv(newFrame,False):
                                        try:
                                            self.model = parse_pmd_xml("pmd.xml", PMD_XML_MODE_FILE)
                                        except:
                                            self.indicators.aesx242Error()
                                            raise RuntimeError("AESX242 XML parsing failed!")
                                        self.post("updateModel", copy.deepcopy(self.model))
                                        self.indicators.aesx242On()
                                    else:
                                        self.indicators.aesx242Error()
                                        raise RuntimeError("AESX242 conversion to XML failed!")
                                else:
                                    # received some unknown format
                                    self.indicators.reset()

                                # Handle framing indicators for PMD & SADM
                                if newFrame.is_pmd() or newFrame.is_sADM():
                                    if newFrame.subframe_mode:
                                        self.indicators.subFrameMode()
                                    else:
                                        self.indicators.frameMode()

                                if (self.XMLViewerRequest):
                                    if newFrame.is_pmd() or newFrame.is_AESX242():
                                        with open("pmd.xml", "r") as xmlFile:
                                            xmlText = xmlFile.read()
                                        self.post("PMD XML", xmlText)
                                    else:
                                        self.post("ADM XML", xmlText)
                                    self.XMLViewerRequest = False


                            except RuntimeError as e:
                                print(e)
                    else:
                        # No packets received before timeout
                        self.post("reset", None)
                    if self.debug:
                        # fps counter, useful for establishing performance
                        print("fps:", round(1/(time.time() - self.start_time)), sep=' ', end='  \r', flush=True)
                        self.start_time = time.time()
                    self.pollPlayback()
     #   			scapy.hexdump(payload24)
    #                for pkt in pkts:
    #                   print(pkt["RTP"].sequence)
        sys.stdout.flush()
        # Quit
        clean_up_temp_files(["pmd.klv", "pmd.wav", "pmd.xml"])
        self.post("quit", None)

# The main thread takes a single file as input. This takes a single filename
# If a filename is provided then the UI prepolulates with that file
# If not then the UI starts empty and waits for control input with the UI gadgets

def main():
    parser = argparse.ArgumentParser(description='Audio Metadata (AM) realtime viewer application')
    parser.add_argument('-xml', type=argparse.FileType('r'), default=None, help='XML filename for offline display of XML')
    parser.add_argument('-sdp', type=argparse.FileType('r'), default=None, help='SDP filename to avoid requiring stream discovery')
    parser.add_argument('-debug', action='store_const', const=True, help='Enables debug mode')
    args = parser.parse_args()

    if args.debug:
        global tracemalloc
        import tracemalloc
        global linecache
        import linecache
        tracemalloc.start()

    root = Tk()
    root['bg'] = '#B3B4D8'
    root.tk_setPalette(background='#A3A4C8', foreground='black',
                   activeBackground='#A3A4C8', activeForeground='black')
    my_gui = PmdAdmDisplayGUI(root, args.xml, args.sdp, args.debug)

    root.update()

    while my_gui.processNextMessage(root):
        root.update()

#	root.mainloop()

if __name__ == '__main__':
    main()
