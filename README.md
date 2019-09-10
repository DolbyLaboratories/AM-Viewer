# Audio Metadata (AM) Viewer


## Overview

This is a python based realtime viewer for PMD, Serial ADM and AES-X242. Once running the viewer can detect real-time changes in the metadata and display them in real-time. The purpose of the viewer is to be able to demonstrate the real-time capabilities of the various formats by allowing the dynamic behaviour to be viewed. The viewer also supports static display of the underlying XML representation.

## General System Requirements

MacOS, Windows and Linux supported.

Python 3 (Tested with Python v3.7.2 from python.org)

Python Modules (install using PIP)
scapy, zeroconf, netifaces

Note: Scapy v2.4.1 and v2.4.2 has a bug that affects Windows. Windows users should revert to 2.4.0 or use 2.4.3 or later when available.

## Windows Requirements

NPcap (https://nmap.org/npcap/)

## Mac OS Requirements

See https://scapy.readthedocs.io/en/latest/installation.html

## Linux Requirements

Because packet sniffing is used to receive the stream, the application requires elevated permissions i.e. sudo to run. Future versions will not have this restriction.

## Installation


In the dist directory is a wheel file. Install using pip3 like this: pip3 install dist/pmd_viewer-1.1-py3-none-any.whl
The contents of this directory can be copied and the tool run directly in which case dependencies must be satisfied manually.

## Instructions

If installed type 'am_viewer'. If not installed, execute the run script.

The viewer can use either an XML or a IP stream as input. To use a file as input use the -xml option to specify the filename. If a stream is used as input then there are two possible ways for the viewer to obtain RTP session information. Either an SDP file can be provided using the -sdp option or the stream can be discovered using the Ravenna discovery protocol (Bonjour & RTSP).

If XML file mode is used the display will immediately update its display based on the XML file. The only control at this point is to quit the application. This is essentially a debug mode.

The stream mode is used then a list of interfaces and a list of available services will be provided on the bottom option bar. Once the appropriate interface and service has been selected then the 'Run' button can be pressed to start the monitoring of the stream. If more than one service is available then the service list can be used to switch between services. If the '-sdp' option was used then one option in the service list should correspond to the sdp file.

When receiving a stream the 'XML' can be pressed at anytime to yield a static XMl snapshot. The XML tree can be explored by expand the various levels of the tree in the XML viewer windows.

Several indicators on the bottom bar show status. The PMD indicator will be green when receiving PMD and grey when not. If an error is received the PMD indicator will flash or stay red for continuous errors. The SADM and AES-X242 indicators work in the same way. The subframe-mode / frame mode indicators indicate whether the received stream is using the frame mode or subframe mode of the SMPTE ST 337 container format inside the SMPTE 2110-31 stream. This indicator is not applicable for AES-X242 streams which do not use SMPTE frames.

## License

 AM Viewer
 Copyright (c) 2019, Dolby Laboratories Inc.
 All rights reserved.
 
 Redistribution and use in source and binary forms, with or without modification, are permitted
 provided that the following conditions are met:
 
 1. Redistributions of source code must retain the above copyright notice,
 this list of conditions and the following disclaimer.
    
 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
    and the following disclaimer in the documentation and/or other materials provided with the distribution.
    
 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or
    promote products derived from this software without specific prior written permission.
 
 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR APARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
