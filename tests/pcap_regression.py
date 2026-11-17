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
import difflib
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AM Viewer pcap regression tests")
    parser.add_argument("--am-viewer", required=True, help="Path to am_viewer executable")
    parser.add_argument("--pcap-dir", required=True, help="Directory containing .pcap or .pcap.zip files")
    parser.add_argument("--reference-dir", required=True, help="Directory containing expected XML files")
    parser.add_argument("--work-dir", required=True, help="Working directory for extracted pcaps and outputs")
    parser.add_argument("--timeout-ms", type=int, default=15000, help="Timeout for each pcap run")
    parser.add_argument("--xml-frames", type=int, default=1, help="Number of XML frames to capture")
    parser.add_argument(
        "--generate-reference",
        action="store_true",
        help="Generate/update reference XML files instead of comparing",
    )
    parser.add_argument(
        "--with-ui-state",
        action="store_true",
        help="Also run web UI-state regression checks across all PCAP files",
    )
    parser.add_argument("--backend", help="Path to backend executable for --with-ui-state")
    parser.add_argument("--ui-host", default="127.0.0.1", help="Backend host for --with-ui-state")
    parser.add_argument("--ui-port", type=int, default=8000, help="Backend port for --with-ui-state")
    parser.add_argument("--ui-interface", default="lo0", help="Capture interface for --with-ui-state")
    parser.add_argument("--ui-capture-address", default="127.0.0.1", help="Capture address for --with-ui-state")
    parser.add_argument("--ui-capture-port", type=int, default=5004, help="Capture port for --with-ui-state")
    parser.add_argument("--ui-replay-packets", type=int, default=4000, help="Replay packet count per PCAP for --with-ui-state")
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


def run_am_viewer(
    am_viewer: Path,
    pcap_input: Path,
    output_xml: Path,
    codec: str,
    timeout_ms: int,
    xml_frames: int,
) -> subprocess.CompletedProcess:
    cmd = [
        str(am_viewer),
        "--text",
        "--pcap",
        str(pcap_input),
        "--codec",
        codec,
        "--xml-frames",
        str(xml_frames),
        "--timeout-ms",
        str(timeout_ms),
        "--save-xml",
        str(output_xml),
    ]

    return subprocess.run(cmd, capture_output=True, text=True)


def compare_xml(expected: Path, actual: Path) -> tuple[bool, str]:
    expected_text = expected.read_text(encoding="utf-8", errors="replace")
    actual_text = actual.read_text(encoding="utf-8", errors="replace")

    if expected_text == actual_text:
        return True, ""

    diff = "\n".join(
        difflib.unified_diff(
            expected_text.splitlines(),
            actual_text.splitlines(),
            fromfile=str(expected),
            tofile=str(actual),
            lineterm="",
        )
    )
    return False, diff


def discover_inputs(pcap_dir: Path) -> list[Path]:
    patterns = ["*.pcap", "*.pcap.zip"]
    files: list[Path] = []
    for pattern in patterns:
        files.extend(sorted(pcap_dir.glob(pattern)))
    return files


def main() -> int:
    args = parse_args()

    am_viewer = Path(args.am_viewer).resolve()
    pcap_dir = Path(args.pcap_dir).resolve()
    reference_dir = Path(args.reference_dir).resolve()
    work_dir = Path(args.work_dir).resolve()
    extract_dir = work_dir / "extracted"
    output_dir = work_dir / "output_xml"

    if not am_viewer.exists():
        print(f"ERROR: am_viewer executable not found: {am_viewer}", file=sys.stderr)
        return 2

    if not pcap_dir.exists():
        print(f"ERROR: pcap directory not found: {pcap_dir}", file=sys.stderr)
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)
    reference_dir.mkdir(parents=True, exist_ok=True)

    pcap_inputs = discover_inputs(pcap_dir)
    if not pcap_inputs:
        print(f"ERROR: no pcap inputs found in {pcap_dir}", file=sys.stderr)
        return 2

    print(f"Discovered {len(pcap_inputs)} input file(s) in {pcap_dir}")

    failures: list[str] = []

    for src in pcap_inputs:
        base = pcap_base_name(src)
        codec = infer_codec(src.name)
        out_xml = output_dir / f"{base}.xml"
        ref_xml = reference_dir / f"{base}.xml"

        try:
            pcap_path = extract_pcap_if_needed(src, extract_dir)
        except Exception as exc:
            failures.append(f"{src.name}: extraction failed: {exc}")
            continue

        result = run_am_viewer(
            am_viewer=am_viewer,
            pcap_input=pcap_path,
            output_xml=out_xml,
            codec=codec,
            timeout_ms=args.timeout_ms,
            xml_frames=args.xml_frames,
        )

        if result.returncode != 0:
            failures.append(
                f"{src.name}: am_viewer failed with exit code {result.returncode}\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )
            continue

        if args.generate_reference:
            shutil.copyfile(out_xml, ref_xml)
            print(f"[GEN] {src.name} -> {ref_xml}")
            continue

        if not ref_xml.exists():
            failures.append(
                f"{src.name}: missing reference file {ref_xml}. "
                "Run with --generate-reference once to create it."
            )
            continue

        equal, diff = compare_xml(ref_xml, out_xml)
        if not equal:
            failures.append(f"{src.name}: XML mismatch\n{diff}")
        else:
            print(f"[OK ] {src.name}")

    if failures:
        print("\nRegression failures:", file=sys.stderr)
        for failure in failures:
            print(f"\n- {failure}", file=sys.stderr)
        return 1

    if args.with_ui_state:
        if not args.backend:
            print("ERROR: --backend is required when --with-ui-state is set", file=sys.stderr)
            return 2

        ui_script = Path(__file__).resolve().parent / "ui_pcap_regression.py"
        ui_cmd = [
            sys.executable,
            str(ui_script),
            "--backend",
            str(Path(args.backend).resolve()),
            "--pcap-dir",
            str(pcap_dir),
            "--host",
            args.ui_host,
            "--port",
            str(args.ui_port),
            "--interface",
            args.ui_interface,
            "--capture-address",
            args.ui_capture_address,
            "--capture-port",
            str(args.ui_capture_port),
            "--replay-packets",
            str(args.ui_replay_packets),
        ]

        ui_result = subprocess.run(ui_cmd)
        if ui_result.returncode != 0:
            return ui_result.returncode

    mode = "generated" if args.generate_reference else "validated"
    print(f"\nAll {len(pcap_inputs)} file(s) {mode} successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
