#!/usr/bin/env python3
# Copyright (c) 2026 Dolby International AB.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED
# BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent.parent

    parser = argparse.ArgumentParser(
        description="Run full AM-Viewer regression suite (text XML + web UI-state)"
    )
    parser.add_argument(
        "--text-binary",
        default=str(root / "build" / "build" / "Release" / "am_viewer"),
        help="Path to text-mode capable am_viewer executable",
    )
    parser.add_argument(
        "--backend",
        default=str(root / "build" / "build" / "Release" / "am_viewer"),
        help="Path to backend executable for UI-state regression",
    )
    parser.add_argument(
        "--pcap-dir",
        default=str(root / "pcap"),
        help="Directory containing .pcap or .pcap.zip files",
    )
    parser.add_argument(
        "--reference-dir",
        default=str(root / "tests" / "reference_xml"),
        help="Directory containing expected XML reference files",
    )
    parser.add_argument(
        "--work-dir",
        default=str(root / "build" / "pcap_test_work"),
        help="Working directory for extracted pcaps and outputs",
    )
    parser.add_argument(
        "--xml-dir",
        default=str(root / "xml"),
        help="Directory containing XML files for XML-folder regression",
    )
    parser.add_argument("--timeout-ms", type=int, default=15000)
    parser.add_argument("--xml-frames", type=int, default=1)
    parser.add_argument("--ui-host", default="127.0.0.1")
    parser.add_argument("--ui-port", type=int, default=8000)
    parser.add_argument("--ui-interface", default="lo0")
    parser.add_argument("--ui-capture-address", default="127.0.0.1")
    parser.add_argument("--ui-capture-port", type=int, default=5004)
    parser.add_argument("--ui-replay-packets", type=int, default=4000)
    parser.add_argument(
        "--generate-reference",
        action="store_true",
        help="Generate or update XML references before validation",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tests_dir = Path(__file__).resolve().parent
    pcap_script = tests_dir / "pcap_regression.py"
    xml_script = tests_dir / "xml_regression.py"

    pcap_cmd = [
        sys.executable,
        str(pcap_script),
        "--am-viewer",
        str(Path(args.text_binary).resolve()),
        "--pcap-dir",
        str(Path(args.pcap_dir).resolve()),
        "--reference-dir",
        str(Path(args.reference_dir).resolve()),
        "--work-dir",
        str(Path(args.work_dir).resolve()),
        "--timeout-ms",
        str(args.timeout_ms),
        "--xml-frames",
        str(args.xml_frames),
        "--with-ui-state",
        "--backend",
        str(Path(args.backend).resolve()),
        "--ui-host",
        args.ui_host,
        "--ui-port",
        str(args.ui_port),
        "--ui-interface",
        args.ui_interface,
        "--ui-capture-address",
        args.ui_capture_address,
        "--ui-capture-port",
        str(args.ui_capture_port),
        "--ui-replay-packets",
        str(args.ui_replay_packets),
    ]

    if args.generate_reference:
        pcap_cmd.append("--generate-reference")

    pcap_result = subprocess.run(pcap_cmd)
    if pcap_result.returncode != 0:
        return pcap_result.returncode

    xml_cmd = [
        sys.executable,
        str(xml_script),
        "--backend",
        str(Path(args.backend).resolve()),
        "--xml-dir",
        str(Path(args.xml_dir).resolve()),
        "--host",
        args.ui_host,
        "--port",
        str(args.ui_port),
    ]
    xml_result = subprocess.run(xml_cmd)
    return xml_result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
