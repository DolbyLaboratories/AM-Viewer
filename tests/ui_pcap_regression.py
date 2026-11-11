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
import json
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AM Viewer web UI-state pcap regression tests")
    parser.add_argument("--backend", required=True, help="Path to am_viewer backend executable")
    parser.add_argument("--pcap-dir", required=True, help="Directory containing .pcap or .pcap.zip files")
    parser.add_argument("--host", default="127.0.0.1", help="Backend host")
    parser.add_argument("--port", type=int, default=8000, help="Backend port")
    parser.add_argument("--interface", default="lo0", help="Capture interface to use")
    parser.add_argument("--capture-address", default="127.0.0.1", help="Capture filter destination address")
    parser.add_argument("--capture-port", type=int, default=5004, help="Capture filter destination UDP port")
    parser.add_argument("--replay-packets", type=int, default=4000, help="Max RTP payload packets to replay per pcap")
    parser.add_argument("--health-timeout", type=float, default=10.0, help="Seconds to wait for backend health")
    return parser.parse_args()


def infer_codec(file_name: str) -> str:
    lower = file_name.lower()
    if "2110-41" in lower:
        return "ST2110-41"
    return "AM824"


def pcap_base_name(pcap_path: Path) -> str:
    if pcap_path.name.endswith(".pcap.zip"):
        return pcap_path.name[: -len(".pcap.zip")]
    if pcap_path.name.endswith(".pcap"):
        return pcap_path.stem
    return pcap_path.stem


def extract_pcap_if_needed(input_path: Path, extract_dir: Path) -> Path:
    if input_path.suffix != ".zip":
        return input_path

    extract_dir.mkdir(parents=True, exist_ok=True)
    target_name = pcap_base_name(input_path) + ".pcap"
    extracted_path = extract_dir / target_name

    with zipfile.ZipFile(input_path, "r") as archive:
        pcap_members = [
            member
            for member in archive.namelist()
            if member.lower().endswith(".pcap") and not Path(member).name.startswith("._")
        ]

        if not pcap_members:
            raise RuntimeError(f"No .pcap member found in archive: {input_path}")

        member = pcap_members[0]
        with archive.open(member, "r") as src, extracted_path.open("wb") as dst:
            shutil.copyfileobj(src, dst)

    return extracted_path


def discover_inputs(pcap_dir: Path) -> list[Path]:
    patterns = ["*.pcap", "*.pcap.zip"]
    files: list[Path] = []
    for pattern in patterns:
        files.extend(sorted(pcap_dir.glob(pattern)))
    return files


def http_json(method: str, url: str) -> Any:
    req = urllib.request.Request(url=url, method=method)
    with urllib.request.urlopen(req, timeout=5) as response:
        payload = response.read().decode("utf-8", errors="replace")
    if not payload:
        return {}
    return json.loads(payload)


def wait_for_health(base_url: str, timeout_seconds: float) -> None:
    deadline = time.time() + timeout_seconds
    last_error = ""
    while time.time() < deadline:
        try:
            data = http_json("GET", f"{base_url}/api/health")
            if data.get("status") == "ok":
                return
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
        time.sleep(0.2)
    raise RuntimeError(f"Backend health did not become ready: {last_error}")


def replay_rtp_payloads(pcap_path: Path, dst_host: str, dst_port: int, max_packets: int) -> int:
    tshark = shutil.which("tshark") or "/Applications/Wireshark.app/Contents/MacOS/tshark"
    cmd = [
        tshark,
        "-r",
        str(pcap_path),
        "-Y",
        f"udp && rtp && udp.dstport=={dst_port}",
        "-T",
        "fields",
        "-e",
        "rtp.payload",
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    sent = 0

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        assert process.stdout is not None
        for line in process.stdout:
            payload_hex = line.strip()
            if not payload_hex:
                continue
            try:
                payload = bytes.fromhex(payload_hex.replace(":", ""))
            except ValueError:
                continue

            sock.sendto(payload, (dst_host, dst_port))
            sent += 1

            if sent >= max_packets:
                break

            if sent % 50 == 0:
                time.sleep(0.001)
    finally:
        sock.close()
        process.kill()

    return sent


def require_field(obj: dict[str, Any], key: str, expected_type: type) -> None:
    if key not in obj:
        raise AssertionError(f"missing key '{key}'")
    if not isinstance(obj[key], expected_type):
        raise AssertionError(f"key '{key}' expected type {expected_type.__name__}, got {type(obj[key]).__name__}")


def validate_ui_state(data: dict[str, Any], expected_codec: str, expected_packets_min: int) -> None:
    require_field(data, "summary", dict)
    require_field(data, "capture", dict)
    require_field(data, "service", dict)
    require_field(data, "interfaces", list)
    require_field(data, "beds", list)
    require_field(data, "objects", list)
    require_field(data, "presentations", list)

    for key in ("sadmVersion", "admVersion", "admProfile", "ditValue"):
        require_field(data, key, str)

    indicator_keys = ["pmd", "sadm", "smpte2110_31", "smpte2110_41", "frame", "subframe", "depth20", "depth24"]
    for key in indicator_keys:
        require_field(data, key, str)
        if data[key] not in {"off", "on", "error"}:
            raise AssertionError(f"indicator '{key}' has invalid value: {data[key]}")

    summary = data["summary"]
    for key in ("objects", "beds", "presentations"):
        require_field(summary, key, int)
    for key in ("loadedFile", "lastError", "lastUpdated"):
        require_field(summary, key, str)

    capture = data["capture"]
    require_field(capture, "active", bool)
    require_field(capture, "interfaceName", str)
    require_field(capture, "address", str)
    require_field(capture, "port", int)
    require_field(capture, "packetCount", int)
    require_field(capture, "lastError", str)

    if not capture["active"]:
        raise AssertionError("capture.active is false during replay")
    if capture["packetCount"] < expected_packets_min:
        raise AssertionError(f"capture.packetCount {capture['packetCount']} < expected {expected_packets_min}")

    service = data["service"]
    for key in ("name", "system", "interfaceName", "address", "codec", "audio"):
        require_field(service, key, str)
    require_field(service, "port", int)

    if expected_codec == "AM824":
        if data["smpte2110_31"] != "on":
            raise AssertionError("expected smpte2110_31=on for AM824 replay")
        if data["smpte2110_41"] != "off":
            raise AssertionError("expected smpte2110_41=off for AM824 replay")
        if data["frame"] != "on" and data["subframe"] != "on":
            raise AssertionError("expected either frame or subframe indicator on for AM824 replay")
        if data["depth20"] != "on" and data["depth24"] != "on":
            raise AssertionError("expected either depth20 or depth24 indicator on for AM824 replay")

    for bed in data["beds"]:
        if not isinstance(bed, dict):
            raise AssertionError("beds[] contains non-object entry")
        for key in ("source", "config", "name"):
            require_field(bed, key, str)
        require_field(bed, "gainDb", (int, float))
        require_field(bed, "start", int)
        require_field(bed, "end", int)

    for obj in data["objects"]:
        if not isinstance(obj, dict):
            raise AssertionError("objects[] contains non-object entry")
        for key in ("type", "name"):
            require_field(obj, key, str)
        require_field(obj, "diverge", bool)
        require_field(obj, "channel", int)
        require_field(obj, "gainDb", (int, float))
        require_field(obj, "x", (int, float))
        require_field(obj, "y", (int, float))
        require_field(obj, "z", (int, float))

    for pres in data["presentations"]:
        if not isinstance(pres, dict):
            raise AssertionError("presentations[] contains non-object entry")
        require_field(pres, "index", int)
        for key in ("name", "nameLang", "bedElement", "targetCfg", "objectElements", "presLang"):
            require_field(pres, key, str)


def main() -> int:
    args = parse_args()

    backend = Path(args.backend).resolve()
    pcap_dir = Path(args.pcap_dir).resolve()
    extract_dir = pcap_dir / "_ui_extract"

    if not backend.exists():
        print(f"ERROR: backend executable not found: {backend}", file=sys.stderr)
        return 2
    if not pcap_dir.exists():
        print(f"ERROR: pcap directory not found: {pcap_dir}", file=sys.stderr)
        return 2

    pcap_inputs = discover_inputs(pcap_dir)
    if not pcap_inputs:
        print(f"ERROR: no pcap inputs found in {pcap_dir}", file=sys.stderr)
        return 2

    base_url = f"http://{args.host}:{args.port}"

    backend_proc = subprocess.Popen([str(backend)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    failures: list[str] = []

    try:
        wait_for_health(base_url, args.health_timeout)

        for src in pcap_inputs:
            base = pcap_base_name(src)
            codec = infer_codec(src.name)

            try:
                pcap_path = extract_pcap_if_needed(src, extract_dir)
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{src.name}: extraction failed: {exc}")
                continue

            try:
                query = urllib.parse.urlencode(
                    {
                        "interface": args.interface,
                        "name": base,
                        "system": "Regression",
                        "address": args.capture_address,
                        "port": args.capture_port,
                        "codec": codec,
                        "audio": "Program1",
                    }
                )
                http_json("POST", f"{base_url}/api/service/select?{query}")

                start_query = urllib.parse.urlencode(
                    {
                        "interface": args.interface,
                        "address": args.capture_address,
                        "port": args.capture_port,
                    }
                )
                http_json("POST", f"{base_url}/api/capture/start?{start_query}")

                sent = replay_rtp_payloads(pcap_path, args.capture_address, args.capture_port, args.replay_packets)
                time.sleep(0.8)
                state = http_json("GET", f"{base_url}/api/ui-state")
                validate_ui_state(state, expected_codec=codec, expected_packets_min=max(1, min(sent, args.replay_packets // 2)))
                print(f"[OK ] {src.name} ({sent} packets)")
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{src.name}: {exc}")
            finally:
                try:
                    http_json("POST", f"{base_url}/api/capture/stop")
                except Exception:
                    pass

    finally:
        backend_proc.terminate()
        try:
            backend_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            backend_proc.kill()

    if failures:
        print("\nUI regression failures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"\nAll {len(pcap_inputs)} PCAP file(s) passed web UI-state regression checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
