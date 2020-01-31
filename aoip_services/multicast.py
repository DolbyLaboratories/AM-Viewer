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


import socket
import struct
import sys
import netifaces
import platform

class MulticastGroup:

    interface = None
    sock = None
    address = None
    port = None
    localIp = None

    def join(self,interface, address, port):
        """
        Creates a socket, sets the necessary options on it, then binds it. The socket is then returned for use.
        """

        self.interface = interface
        self.localIp = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
        self.port = port
        self.address = address
        # create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Not all platforms support REUSEPORT i.e. Windows does not
        # The linux check below won't always work e.g. 3.10 will fail but it is close enough
        if platform.system() == 'Darwin' or (platform.system() == 'Linux' and platform.release() > "3.9"):
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.localIp))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        membership_request = socket.inet_aton(self.address) + socket.inet_aton(self.localIp)

        # See http://www.tldp.org/HOWTO/Multicast-HOWTO-6.html for explanation of sockopts
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership_request)

        # Bind the socket to an interface depending on system
        if platform.system() == 'Darwin':
            self.sock.bind(('0.0.0.0', self.port))
        else:
            self.sock.bind((self.localIp, self.port))

    def leave(self):
        # leave group if active
        if (self.address != None):
            membership_request = socket.inet_aton(self.address) + socket.inet_aton(self.localIp)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, membership_request)
            self.sock.close()
            self.address = None
            self.interface = None
            self.port = None
            self.localIp = None