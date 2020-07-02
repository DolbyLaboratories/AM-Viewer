#!/usr/bin/env python

"""
 AOIP Services
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

class sdp_parser:

    type = ""
    codec = ""
    fs = 0
    address = ""
    port = 0
    session_name = ""
    channels = 0

    def __init__(self, sdp_text):
        for line in sdp_text.splitlines():
            split_line = line.split('=',1)
            if len(split_line) > 1:
                header = split_line[0]
                body = split_line[1].split(' ')
                if header == 's' and len(body) > 0:
                    self.session_name = ' '.join(body[:])
                if header == 'm' and len(body) > 1:
                        self.type = body[0]
                        self.port = int(body[1])
                if header == 'c' and len(body) > 0:
                    self.address = body[-1].split('/',1)[0]
                if header == 'a' and len(body) > 1:
                    if body[0].find("rtpmap:") != -1:
                        format = body[1].split('/',2)
                        if len(format) > 1:
                            self.codec = format[0]
                            self.fs = int(format[1])
                            if len(format) > 2:
                                self.channels = int(format[2])
                            else:
                                self.channels = 0

    def print(self):
        print("SDP Contents")
        print("============")
        print("Name:", self.session_name)
        print("Type: ", self.type)
        print("Multicast address: ", self.address)
        print("Port", self.port)
        print("Codec: ", self.codec)
        print("Sampling Frequency: ", self.fs,"Hz")
        print("No of channels:", self.channels)


    def isAM824(self):
        return((self.codec == "AM824") and (self.fs == 48000) and (self.channels == 2))

    def isAESX242(self):
        return(self.codec == "smpte336m")

    def isAES67(self):
        return(self.codec == "L16" or self.codec == "L24")