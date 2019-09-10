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
import sys
import subprocess
import binascii
import zlib
import netifaces
import scapy.all as scapy
import argparse
import queue
import copy
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
from pmd.pmd_const import OBJECT_CLASSES
from am_viewer.am_xml_viewer import XML_Viewer
from am_viewer.am_xml_viewer import isFilePmd
from am_viewer.am_xml_viewer import isFileSADM
import aoip_services.aoip_discovery
import aoip_services.multicast

__version__ = "1.1"

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
	START = 3
	END = 4


# Helper functions

def get_cmd_stdio(args):
	import subprocess
	#print(args)
	run_output = subprocess.run(args, stdout=subprocess.PIPE)
	text = str(run_output.stdout.decode("utf-8"))
	text = text.replace('\\n', '\n')
	text = text.replace('\\r', '\r')
	text = text.replace('\\t', '\t')
	return(text)


def get_word(payload, index, subframe_mode):
	if subframe_mode:
		return(int.from_bytes(payload[index*2:(index*2)+3], byteorder='big') >> 4)
	else:	
		return(int.from_bytes(payload[index:index+3], byteorder='big') >> 4)


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
		#print("Nibbles:",input_nibbles)
		for nibble in input_nibbles:
			if (output_nibble_count != 5):
				if output_nibble_hi_lo == 1:
					array20[-1] = array20[-1] | nibble
					#print(hex(array20[-1]))
				else:
					array20.append(nibble << 4)
					#print("new:",hex(array20[-1]))
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

def hasSync(packet):
	pa_bytes = bytes([0x6F,0x87,0x20])
	return(bytes(packet["RTP"].payload).find(pa_bytes))

def get_pmd_xml(payload24, pack20_flag):
	pmd_tool_exec = os.path.dirname(__file__) + "/pmd_tool." + platform.system()
	if (platform.system() == 'Windows'):
		pmd_tool_exec = pmd_tool_exec + '.exe'
	if not os.path.exists(pmd_tool_exec):
		print("__file__:",__file__,"  pmd_tool path:", pmd_tool_exec)
		print("Platform", platform.system(), "not supported", file=sys.stderr)
		exit(-4)

	#my_hexdump(payload24)
	if pack20_flag:
		klv_payload = pack_20bits(payload24)
	else:
		klv_payload = payload24
	#my_hexdump(klv_payload, 10)
	with open("pmd.klv", "wb") as klv_file:
		klv_file.write(klv_payload)
	try:
		os.remove("pmd.xml")
	except:
		pass
	args = [pmd_tool_exec, "-i", "pmd.klv", "-o", "pmd.xml"]
	#print(args)
	subprocess.run(args)
	if not os.path.exists("pmd.xml"):
		print("KLV to XML conversion failed. PMD is probably corrupted", file=sys.stderr)
		return False
	return True
		
def get_sadm_xml(payload24, sADM_assemble_flag, sADM_format_flag):
	#my_hexdump(self.pmd_payload24)
	index = 0
	if sADM_assemble_flag == 1:
		assemble_info = get_word(payload24, index, False)
		in_timeline_flag = (assemble_info >> 4) & 0x3
		# Only support full frame mode so this must be 0
		if (in_timeline_flag != 0):
			return(None)
		#Commenting the next two elements out for speed as they are ignored
		#track_numbers = (assemble_info >> 6) & 0x3f
		#track_ID = (assemble_info >> 12) & 0x3f
		index = index + 3
	if sADM_format_flag == 1:
		format_info = get_word(payload24, index, False)
		format_type = format_info >> 4 & 0xf
		index = index + 3
	if format_type == 1:
		gzip_data = pack_20bits(payload24[index:])
		try:
			adm_xml = zlib.decompress(gzip_data, 15 + 32)
		except:
			adm_xml = None
	else:
		adm_xml = payload24[index:]
	return(adm_xml)

class State:
	IDLE = 0
	GOT_SYNC = 1
	GOT_HEADER = 2
	GOT_FRAME = 3

class pmdDeframer:
 
	subframe_mode = None
	got_header = False
	length20=0
	length24=0
	data_type=0

	payloads = None
	state = State.IDLE
	last_sequnce_no = None
	new_frame = None
	new_frame_format = None 

	pa = 0x6f872
	pb = 0x54e1f


	def reset(self):
		subframe_mode = None
		got_header = False
		length20 = 0
		length24 = 0
		data_type = 0
		payloads = None
		state = State.IDLE
		last_sequnce_no = None
		new_frame = None
		new_frame_format = None
		sADM_assemble_flag = None
		sADM_format_flag = None


	def receivePacket(self,packet,codec):
		if codec == "AM824":
			self.receiveSMPTEPacket(packet)
		elif codec == "smpte336m":
			self.receiveAESX242Packet(packet)
		else:
			raise("Unknown format")


	def receiveAESX242Packet(self,packet):
		packet["UDP"].payload = scapy.RTP(packet["Raw"].load)
		#detect marker bit to see if this is the first packet of the KLVunit
		if packet["RTP"].marker:
			# Ideally at this point we would probe the payload to see if it is complete
			# For now we are just going to see if we already have at least one packet
			# already and try to decode that
			if self.payloads != None:
				self.new_frame = self.payloads
				self.new_frame_format = "AESX242"
			self.payloads = bytes(packet["RTP"].payload)
		else:
			self.payloads = self.payloads + bytes(packet["RTP"].payload)

	# Receive raw packets as they are received
	def receiveSMPTEPacket(self, packet):
		#my_hexdump(packet)

		# Force packet to be interpreted as RTP
		packet["UDP"].payload = scapy.RTP(packet["Raw"].load)

		if self.state == State.IDLE:
			start = hasSync(packet)
			if not start == -1:
				# Strip out user bits etc.
				packet_payload = bytes(packet["RTP"].payload)
				self.payloads = b''
#                my_hexdump(packet_payload, 8)
				for index in range(start,len(packet_payload),4):
					# Because we are aligned to the actual sync word we drop the fourth/last byte
					self.payloads = self.payloads + packet_payload[index:index+3]
#				my_hexdump(self.payloads, 8)
				self.last_sequnce_no = packet["RTP"].sequence
				self.subframe_mode = None
				self.state = State.GOT_SYNC

		elif self.state == State.GOT_SYNC:
			# Check sequence otherwise if we are out of order mid-frame then errors
			# are certain so reset state machine and reacquire sync
			if not packet["RTP"].sequence == (self.last_sequnce_no + 1) & 0xffff:
				self.state = State.IDLE
			else:
				self.last_sequnce_no = packet["RTP"].sequence
				# Strip out user bits etc.
				packet_payload = bytes(packet["RTP"].payload)
				for index in range(0,len(packet_payload),4):
					# We are aligned with 32 bit word boundary so drop the first byte
					self.payloads = self.payloads + packet_payload[index + 1:index + 4]

				# At this point we can check Pb
				if self.subframe_mode == None and len(self.payloads) > 6:
					if (get_word(self.payloads, 3, False) != self.pb) and (get_word(self.payloads, 6, False) != self.pb):
						# Pb is bad so reset state machine
						self.state = State.IDLE
					else:
						if get_word(self.payloads, 3, False) == self.pb:
							self.subframe_mode = False
						else:
							self.subframe_mode = True
				words24 = len(self.payloads)

				if (self.subframe_mode and words24 > 36) or (not self.subframe_mode and words24 > 24):
					Pc = get_word(self.payloads, 6, self.subframe_mode)
					self.data_type = (Pc & 0x01f0) >> 4
					# If entended data type then add in Pe
					if self.data_type == 31:
						self.data_type = self.data_type + get_word(self.payloads, 12, self.subframe_mode) & 0xffff
					# 8 bits, scale up to 24 bits because we are not using packed 20 bits yet
					Pd = get_word(self.payloads, 9, self.subframe_mode)
					self.length20 = int(Pd / 8)
					self.length24 = int(Pd / 20) * 3
					# If subframe mode then we need twice as many samples to hold frame
					if self.subframe_mode:
						self.length24 = self.length24 * 2
					if self.is_sADM():
						self.sADM_assemble_flag = (Pc >> 13) & 0x1
						self.sADM_format_flag = (Pc >> 14) & 0x1
					# eat header
					if (self.data_type > 30):
						if self.subframe_mode:
							self.payloads = self.payloads[36:]
						else:
							self.payloads = self.payloads[18:]
						# adjust for Pe and Pf
						self.length20 = self.length20 - 5
						self.length24 = self.length24 - 6
					else:
						if self.subframe_mode:
							self.payloads = self.payloads[24:]
						else:
							self.payloads = self.payloads[12:]
					self.state = State.GOT_HEADER

				if (not (self.is_pmd())) and (not (self.is_sADM())):
					# detected wrong SMPTE data type
					self.state == State.IDLE

		elif self.state == State.GOT_HEADER:
			# Still check sequence number
			if not packet["RTP"].sequence == (self.last_sequnce_no + 1) & 0xffff:
				self.state = State.IDLE
			else:
				self.last_sequnce_no = packet["RTP"].sequence
				# Strip out user bits etc.
				packet_payload = bytes(packet["RTP"].payload)
				for index in range(0,len(packet_payload),4):
					# We are aligned with 32 bit word boundary so drop the first byte
					self.payloads = self.payloads + packet_payload[index + 1:index + 4]

			# See if we have complete frame
			if len(self.payloads) > self.length24:
				# trim excess off
				self.payloads = self.payloads[:self.length24]
				if self.subframe_mode:
					self.new_frame = subframe_to_framemode(self.payloads)
				else:
					self.new_frame = self.payloads

#                my_hexdump(self.new_frame, 6)
				if self.is_pmd():
					self.new_frame_format = "PMD"
				elif self.is_sADM():
					self.new_frame_format = "SADM"
				else:
					self.new_frame_format = "Uknown"
				self.state = State.IDLE

	def getFrame(self):
		if self.new_frame is not None:
			tuple = (self.new_frame_format, self.new_frame)
			self.new_frame = None
			return tuple
		else:
			return None

	def haveFrame(self):
		return self.new_frame is not None

	def is_sADM(self):
		if self.data_type == 32:
			return True
		else:
			return False

	def is_pmd(self):
		if self.data_type == 27:
			return True
		else:
			return False

	def is_subframe_mode(self):
		if self.subframe_mode:
			return True
		else:
			return False

	def get_sADM_assemble_flag(self):
		return self.sADM_assemble_flag

	def get_sADM_format_flag(self):
		return self.sADM_format_flag

# Main GUI App Class

class PmdAdmDisplayGUI:

	numObjects = 4
	numPresentations = 4
	numBeds = 2
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
	selectedService = None
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

		audio_beds_label = Label(master, text="Audio Beds")
		audio_beds_label.pack(fill=X)

		self.abFrame = Frame(master, relief= self.frameRelief, borderwidth=self.frameBorderwidth)
		self.abFrame.pack(fill=BOTH, expand=True)

		abLabels = [ "Source", "Config", "Name", "Start", "End" ]

		for abColumn in range(1,6):
			abLabel = Label(self.abFrame, text = abLabels[abColumn - 1])
			abLabel.grid(row = 0, column = abColumn)

		self.bedFields = [[], []]
		for bed in range(0,self.numBeds):

			bed_label = Label(self.abFrame, text = str(bed+1))
			bed_label.grid(row = bed + 1, column = 0)

			for abColumn in range(1,6):
				self.bedFields[bed].append(Label(self.abFrame, text = "None", relief=SUNKEN, bg = '#B3B4C8'))
				self.bedFields[bed][-1].grid(row = bed + 1, column = abColumn, sticky=N+E+S+W)

		for abColumn in range(0,6):
			self.abFrame.grid_columnconfigure(abColumn,minsize = 100)

		audio_objects_label = Label(master, text="Audio Objects")
		audio_objects_label.pack(fill=X)

		self.aoFrame = Frame(master, relief=RAISED, borderwidth=5)
		self.aoFrame.pack(fill=BOTH, expand=True)

		aoLabels = [ "Type", "Name", "Diverge", "Ch", "Gain(dB)", "X", "Y", "Z" ]

		for aoColumn in range(1, len(aoLabels) + 1):
			aoLabel = Label(self.aoFrame, text = aoLabels[aoColumn - 1])
			aoLabel.grid(row = 0, column = aoColumn)

		self.objectFields = [ [], [], [], [] ]
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

		presLabels = [ "Name", "NameLang", "Bed Element", "Target Cfg", "Object Elements", "PresLang" ]

		for presColumn in range(1, len(presLabels) + 1):
			presLabel = Label(self.presFrame, text = presLabels[presColumn - 1])
			presLabel.grid(row = 0, column = presColumn)

		self.presFields = [ [], [], [], [] ]
		self.oeFrames = []
		self.objectElements = [ [], [], [], [] ]
		self.oeVars = [ [], [], [], [] ]
		for presentation in range(0, self.numPresentations):
			presentation_number_label = Label(self.presFrame, text = str(presentation + 1))
			presentation_number_label.grid(row = presentation + 1, column = 0)

			# First do regular indicator labels
			for presColumn in [1,2,3,4,6]:
				#print ("presColumn", presColumn)
				self.presFields[presentation].append(Label(self.presFrame, text = "None", relief=SUNKEN, bg = '#B3B4C8'))
				self.presFields[presentation][-1].grid(row = presentation + 1, column = presColumn, sticky=N+E+S+W)

			#print("presFields length", len(self.presFields[0]))

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
					model = parse_pmd_xml(xml_filename, PMD_XML_MODE_FILE)
					xml_filename.seek(0)
				except:
					raise RuntimeError("Recognized file as PMD but parsing failed")
			elif isFileSADM(xml_filename):
				try:
					model = populate_model_from_adm(xml_filename, ADM_XML_MODE_FILE)
				except:
					raise RuntimeError("Recognized file as ADM but parsing failed")
			else:
				raise("File format not recognized")
			self.updateFromModel(model)
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
					if netifaces.ifaddresses(guid).get(netifaces.AF_INET) != None and name != 'Npcap Loopback Adapter':
						ifList.append(name)
			else:
				for iface in fullIfListNames:
					if netifaces.ifaddresses(iface).get(netifaces.AF_INET) != None and iface != 'lo0':
						ifList.append(iface)

			# Now we have a list of interfaces, create Drop-down menu to select interface
			self.interface = StringVar(master)
			if ifList is not []:
				self.interface.set(ifList[-1])
				self.ifList = OptionMenu(master, self.interface, *ifList, command=self.setInterfaceName)
				self.ifList.pack(side=LEFT)
			self.interfaceName = self.interface.get()

		self.pmdInd = Label(master, text='PMD', variable=self.pmdIndVar, fg='black')
		self.pmdInd.pack(side=LEFT)
		self.sadmInd = Label(master, text='sADM', variable=self.sadmIndVar, fg='black')
		self.sadmInd.pack(side=LEFT)
		self.aesx242Ind = Label(master, text='AES-X242', variable=self.aesx242IndVar, fg='black')
		self.aesx242Ind.pack(side=LEFT)

		self.FrameInd = Label(master, text='Frame', fg='black')
		self.FrameInd.pack(side=LEFT)
		self.SubFrameInd = Label(master, text='Subframe', fg='black')
		self.SubFrameInd.pack(side=LEFT)

		self.indicators = self.Indicators(self)

		label = Label(master, text="Service:")
		label.pack(side=LEFT)
		self.serviceSelection = StringVar(master)
		#self.serviceSelection.set(self.serviceNameList[0])
		self.serviceMenu = OptionMenu(master, self.serviceSelection, "Service")
		self.serviceMenu.pack(side=LEFT)

		button = Button(master, text="XML", command=self.view_XML)
		button.pack(side=LEFT)

		# Now that the GUI is complete it is safe to start discovery
		# Option menu must exist first so this can't be moved up

		# Make sure a main thread exists so it is able to accept messages, even if it is not started

		self.messageQueue = queue.Queue()
		self.discoveryService = aoip_services.aoip_discovery.aoip_discovery(self.discoveryCallback)
		# If an SDP file was provided then add an additional service based on the file
		if sdp_filename is not None:
			self.discoveryService.add_aoip_service_from_sdp_file(sdp_filename)
		# This object is needed for joins and leaves
		self.multicast = aoip_services.multicast.MulticastGroup()

	def post(self, command, data):
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


	def reset_ui(self):
		# Reset lights
		self.indicators.reset()

		# Reset Metadata display

		for ununsedBeds in range(0,self.numBeds):
				self.bedFields[ununsedBeds][AudioBedHeadings.SOURCE].configure(text="")
				self.bedFields[ununsedBeds][AudioBedHeadings.CONFIG].configure(text="")
				self.bedFields[ununsedBeds][AudioBedHeadings.NAME].configure(text="")
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
		bedCount = 0;
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
				self.bedFields[bedCount][AudioBedHeadings.START].configure(text=element.output_targets[0].audio_signals[0].id)
				self.bedFields[bedCount][AudioBedHeadings.END].configure(text=element.output_targets[0].audio_signals[0].id + 
					PRESENTATION_CONFIG_EQUIV[PRESENTATION_CONFIG_TEXT.index(element.speaker_config)] - 1)
				bedCount = bedCount + 1

		for ununsedBeds in range(bedCount,self.numBeds):
				self.bedFields[ununsedBeds][AudioBedHeadings.SOURCE].configure(text="")
				self.bedFields[ununsedBeds][AudioBedHeadings.CONFIG].configure(text="")
				self.bedFields[ununsedBeds][AudioBedHeadings.NAME].configure(text="")
				self.bedFields[ununsedBeds][AudioBedHeadings.START].configure(text="")
				self.bedFields[ununsedBeds][AudioBedHeadings.END].configure(text="") 

		for unusedObject in range(objectCount,self.numObjects):
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
				for i in range(0,self.numObjects):
					self.oeVars[presentationCount][i].set(objectIncludeList[i])
				presentationCount = presentationCount + 1

		for unusedPresentations in range(presentationCount,self.numPresentations):
			self.presFields[unusedPresentations][PresentationHeadings.NAME].configure(text="")
			self.presFields[unusedPresentations][PresentationHeadings.NAME_LANG].configure(text="")
			self.presFields[unusedPresentations][PresentationHeadings.TARGET_CFG].configure(text="")
			self.presFields[unusedPresentations][PresentationHeadings.PRES_LANG].configure(text="")
			self.presFields[unusedPresentations][PresentationHeadings.BED_ELEMENT].configure(text="")

			for i in range(0,self.numObjects):
				self.oeVars[unusedPresentations][i].set(0)

	def processNextMessage(self, master):
		if self.messageWaiting():
			[command,messageData] = self.getMessage()
			if command == "newService":
				newService = messageData
				if newService.sdp.isAM824() or newService.sdp.isAESX242():
					if self.debug:
						print("Found ",newService.system, " Service ", newService.name)
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
			if command == "updateInd":
				self.pmdInd.config(bg=self.indicators.pmd)
				self.sadmInd.config(bg=self.indicators.sadm)
				self.aesx242Ind.config(bg=self.indicators.aesx242)
				self.FrameInd.config(bg=self.indicators.frame)
				self.SubFrameInd.config(bg=self.indicators.subframe)
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
							(format,payload24) = deframer.getFrame()
							try:
								if format == "PMD":
									if get_pmd_xml(payload24, True):
										try:
											model = parse_pmd_xml("pmd.xml", PMD_XML_MODE_FILE)
										except:
											self.indicators.pmdError()
											raise RuntimeError("PMD XML parsing failed!")
										self.post("updateModel", copy.deepcopy(model))
										self.indicators.pmdOn()
									else:
										self.indicators.pmdError()
										raise RuntimeError("PMD conversion to XML failed!")
								elif format == "SADM":
									xmlText = get_sadm_xml(payload24, deframer.get_sADM_assemble_flag(), deframer.get_sADM_format_flag())
									if xmlText is not None:
										try:
											#model = populate_model_from_adm("sadm.xml", ADM_XML_MODE_FILE)
											model = populate_model_from_adm(xmlText, ADM_XML_MODE_STRING)
										except:
											self.indicators.sadmError()
											raise RuntimeError("SADM XML parsing failed")
										self.post("updateModel", copy.deepcopy(model))
										self.indicators.sadmOn()
									else:
										self.indicators.sadmError()
										raise RuntimeError("SADM conversion to XML failed!")
								elif format == "AESX242":
									if get_pmd_xml(payload24,False):
										try:
											model = parse_pmd_xml("pmd.xml", PMD_XML_MODE_FILE)
										except:
											self.indicators.aesx242Error()
											raise RuntimeError("AESX242 XML parsing failed!")
										self.post("updateModel", copy.deepcopy(model))
										self.indicators.aesx242On()
									else:
										self.indicators.aesx242Error()
										raise RuntimeError("AESX242 conversion to XML failed!")
								else:
									# received some unknown format
									self.indicators.reset()

								# Handle framing indicators for PMD & SADM
								if format == "PMD" or format == "SADM":
									if deframer.is_subframe_mode():
										self.indicators.subFrameMode()
									else:
										self.indicators.frameMode()

								if (self.XMLViewerRequest):
									if format == "PMD":
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
	#   			scapy.hexdump(payload24)
	#                for pkt in pkts:
	#                   print(pkt["RTP"].sequence)
		sys.stdout.flush()
		# Quit
		try:
			os.remove("pmd.klv")
		except:
			pass
		try:
			os.remove("pmd.xml")
		except:
			pass
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
	print("Starting...")
	main()
