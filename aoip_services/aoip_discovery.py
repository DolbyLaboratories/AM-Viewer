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

import logging
import socket
import sys
import platform
import struct
from time import sleep
from typing import cast

from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf
import socket
import threading
import aoip_services.sdp_parser
from tkinter import *
import errno
from urllib.parse import quote
import netifaces
import sys

sap_addr = "239.255.255.255"
sap_port = 9875

class StoppableThread(threading.Thread):

    def __init__(self, **kwargs):
        super(StoppableThread, self).__init__(**kwargs)
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def get_lock(self):
        self._lock.acquire()

    def release_lock(self):
        self._lock.release()


class SAPPacket:
    def __init__(self, data, addr):
#		scapy.hexdump(data)
        self.Version = data[0] >> 5;
        self.IsIPv6 = bool((data[0] >> 4) & 1)
        self.T = (data[0] >> 2) & 1
        self.IsEncrypted = bool((data[0] >> 1) & 1)
        self.IsCompressed = bool(data[0] & 1)
        self.AuthLen = int(data[1])
        self.MsgIdHash = struct.unpack("H", data[2:4])
        data = data[4:]
        if self.IsIPv6:
            self.OrigSource = data[:4*4]
            data = data[4*4:]
        else:
            self.OrigSource = data[:4]
            data = data[4:]
        # ignore AuthData
        data = data[self.AuthLen * 4:]
        if self.IsEncrypted:
            # ignore timestamp for now...
            data = data[4:]
        # search 0-byte, set payload type
        self.PayloadType = None
        for i in range(0, len(data)):
            if data[i] == 0:
                self.PayloadType = data[0:i]
                data = data[i+1:]
                break
        self.PayloadData = data

        try:
            mediaAddr = self.Payload.c.split()[-1].split("/")[0]
        except:
            mediaAddr = None
        try:
            mediaPort = self.Payload.m.split()[1]
        except:
            mediaPort = None
        if mediaAddr and mediaPort:
            self.Media = {}
            self.Media["Sender"] = self.Payload.s
            self.Media["Playgroup"] = self.Payload.a.get("x-plgroup", "")
            self.Media["Addr"] = "udp://@" + mediaAddr + ":" + mediaPort

class aoip_service:

    name = ""
    system = None
    port = ""
    ip_address = ""
    codec = ""
    sdp_text = ""
    sdp = None
    interface_list = []
    dante_sock = None

class aoip_discovery:

    service_list = []
    service_list_lock = None
    callback = None
    dante_task = None
    cseq = 0

# call back is a function called when a service is added to the service list
# this is call
    def __init__(self, callback, interface_list):
        self.callback = callback
        # if bogus interface names are supplied, remove them
        # if we end up with an empty list then the default interface will be used
        self.interface_list = interface_list
        known_ifaces = netifaces.interfaces()
        for iface in interface_list:
            if iface not in known_ifaces:
                interface_list.remove(iface)
        # Startup ravenna discovery
        zeroconf = Zeroconf()
        browser = ServiceBrowser(zeroconf, "_ravenna_session._sub._rtsp._tcp.local.", handlers=[self.found_ravenna_service])
 
        # Startup Dante discovery
        self.dante_task = StoppableThread(target = self.dante_discovery_task)
        self.dante_task.start()
        self.service_list_lock = threading.Lock()
        self.cseq = 0

    def stop(self):
        self.dante_task.stop()

    def dante_discovery_task(self):

        self.dante_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Look up multicast group address in name server and find out IP version
        addrinfo = socket.getaddrinfo(sap_addr, None)[0]

        # Multicast code from: http://wiki.python.org/moin/UdpCommunication

        # Set some options to make it multicast-friendly
        self.dante_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.dante_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass # Some systems don't support SO_REUSEPORT
        #sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
        #sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)

        if len(self.interface_list) == 0:
            membership_request = struct.pack("4sl", socket.inet_aton(sap_addr), socket.INADDR_ANY)
            self.dante_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership_request)
        else:
            for iface in self.interface_list:
                localIp = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
                membership_request = struct.pack("4s4s", socket.inet_aton(sap_addr), socket.inet_aton(localIp))
        # See http://www.tldp.org/HOWTO/Multicast-HOWTO-6.html for explanation of sockopts
                self.dante_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership_request)

        if platform.system() == 'Windows':
            self.dante_sock.bind( ('', sap_port) ) # standard SAP port
        else:
            self.dante_sock.bind( (sap_addr, sap_port) ) # standard SAP port

        group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])

        self.dante_sock.setblocking(False)

        while not self.dante_task.stopped():
            try:
                data, addr = self.dante_sock.recvfrom(1024)
            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    sleep(1)
                    continue
                else:
                    raise e

#			print ("received:", data, addr)
#			scapy.hexdump(data)
            if data:
                p = SAPPacket(data,addr)
#			print(p.PayloadData.decode())
                self.add_aoip_service_from_sdp_text("SAP", p.PayloadData.decode())

        # Leave SAP group
        for iface in self.interface_list:
            self.remove_interface(iface)

        self.dante_sock.close()

    def add_interface(self, iface):
        self.interface_list.append(iface)
        localIp = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
        membership_request = struct.pack("4s4s", socket.inet_aton(sap_addr), socket.inet_aton(localIp))
        # See http://www.tldp.org/HOWTO/Multicast-HOWTO-6.html for explanation of sockopts
        self.dante_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership_request)

    def remove_interface(self, iface):
        self.interface_list.remove(iface)
        localIp = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
        membership_request = struct.pack("4s4s", socket.inet_aton(sap_addr), socket.inet_aton(localIp))
        self.dante_sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, membership_request)

    def remove_all_interfaces(self):
        for iface in self.interface_list:
            self.remove_interface(iface)
        self.interface_list = []

# Create a service based on an SDP text string
# This enables external discovery via shared SDP files
    def add_aoip_service_from_sdp_text(self,system,sdp_text):
        new_service = aoip_service()
        new_service.sdp = aoip_services.sdp_parser.sdp_parser(sdp_text)
        new_service.system = system
        new_service.name = new_service.sdp.session_name
        new_service.port = new_service.sdp.port
        new_service.ip_address = new_service.sdp.address
        new_service.codec = new_service.sdp.codec
        found = False
        for service in self.service_list:
            if new_service.name == service.name and new_service.system == service.system:
                found = True
        if not found:
            # This function can be called from multiple threads so this ensures that
            # list additions happen sequentially
            self.service_list_lock.acquire()
            self.service_list.append(new_service)
            self.service_list_lock.release()
            self.callback(new_service)

    def add_aoip_service_from_sdp_file(self,sdp_file):
        sdp_text=sdp_file.read()
        self.add_aoip_service_from_sdp_text("SDP",sdp_text)


    def found_ravenna_service(
        self, zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange,
    ) -> None:
        #print("Service %s of type %s state changed: %s" % (name, service_type, state_change))

        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if (service_type == '_ravenna_session._sub._rtsp._tcp.local.' and info is not None):
                name = name.split('.',1)[0]
                address = socket.inet_ntoa(cast(bytes, info.address))
                port = cast(int, info.port)
                req = 'DESCRIBE rtsp://' + address + ':' + str(port) + '/by-name/' + quote(name) + ' RTSP/1.0\r\n' + \
                'CSeq: ' + str(self.cseq) + '\r\n\r\n'
                self.cseq = (self.cseq + 1) % 65536
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.connect((address, port))
                    s.send(req.encode())
                    sdp_text = s.recv(4096).decode()
                    self.add_aoip_service_from_sdp_text("Ravenna", sdp_text)
                except RuntimeError:
                    pass


if __name__ == '__main__':

    root = Tk()

    def quit_discovery():
        root.quit()

    def run_discovery():
        root.wm_title("Listening for Services")
        #root.pack_propagate(0)
        text_box = Text(root, width = 40, height = 25)
        text_box.pack()
        button = Button(root, text="Quit", command=quit_discovery)
        button.pack()

        def console_print(string):
            text_box.insert(END, string + '\n')
            text_box.see("end")

        def new_service_callback(service):
            console_print("----------------------------------------")
            console_print("Name: " + service.name)
            console_print("System: " + service.system)
            console_print("IP Address:" + service.ip_address)
            console_print("Port:" + str(service.port))
            console_print("Codec:" + service.codec)
            console_print("Channels:" + str(service.sdp.channels))
            console_print("Sampling Frequency:" + str(service.sdp.fs))
            #print("SDP:")
            #service.sdp.print()
            console_print("----------------------------------------")

        # interface list passed as arguments
        new_aoip_discovery = aoip_discovery(new_service_callback, sys.argv[1:])

        root.mainloop()
        new_aoip_discovery.stop()

    run_discovery()








