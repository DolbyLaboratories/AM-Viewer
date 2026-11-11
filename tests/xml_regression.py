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
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AM Viewer XML folder regression tests")
    parser.add_argument("--backend", required=True, help="Path to am_viewer backend executable")
    parser.add_argument("--xml-dir", required=True, help="Directory containing XML files to validate")
    parser.add_argument("--host", default="127.0.0.1", help="Backend host")
    parser.add_argument("--port", type=int, default=8000, help="Backend port")
    parser.add_argument("--health-timeout", type=float, default=10.0, help="Seconds to wait for backend health")
    return parser.parse_args()


def local_name(tag: str) -> str:
    if not tag:
        return ""
    if "}" in tag:
        tag = tag.split("}", 1)[1]
    if ":" in tag:
        tag = tag.split(":", 1)[1]
    return tag


def attr_local(element: ET.Element, name: str) -> str:
    for key, value in element.attrib.items():
        if local_name(key) == name:
            return value
    return ""


def discover_xml_files(xml_dir: Path) -> list[Path]:
    files = sorted(path for path in xml_dir.rglob("*.xml") if path.is_file())
    return files


def expected_profile_count(xml_path: Path) -> int:
    try:
        root = ET.parse(xml_path).getroot()
    except Exception:
        return 0

    seen: set[str] = set()
    for node in root.iter():
        if local_name(node.tag) != "profile":
            continue
        profile_name = attr_local(node, "profileName") or (node.text or "").strip()
        if not profile_name:
            continue
        profile_version = attr_local(node, "profileVersion")
        profile_level = attr_local(node, "profileLevel")
        profile_text = (node.text or "").strip()
        key = "\n".join([profile_name, profile_version, profile_level, profile_text])
        seen.add(key)

    return len(seen)


def http_json(method: str, url: str) -> Any:
    req = urllib.request.Request(url=url, method=method)
    with urllib.request.urlopen(req, timeout=8) as response:
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


def load_xml(base_url: str, xml_path: Path) -> tuple[bool, str]:
    xml_text = xml_path.read_text(encoding="utf-8", errors="replace")
    query = urllib.parse.urlencode({"name": xml_path.name})
    url = f"{base_url}/api/load-xml-upload?{query}"
    req = urllib.request.Request(
        url=url,
        data=xml_text.encode("utf-8"),
        method="POST",
        headers={"Content-Type": "text/xml"},
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            payload = response.read().decode("utf-8", errors="replace")
        if not payload:
            return True, ""
        data = json.loads(payload)
        return True, data.get("message", "")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return False, f"HTTP {exc.code}: {body}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def validate_state(state: dict[str, Any], xml_path: Path, expected_profiles: int) -> None:
    summary = state.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("ui-state missing summary object")

    loaded_file = summary.get("loadedFile", "")
    if not isinstance(loaded_file, str) or not loaded_file:
        raise AssertionError("summary.loadedFile missing or empty")

    loaded_file_name = Path(urllib.parse.unquote(loaded_file)).name
    if loaded_file_name != xml_path.name:
        raise AssertionError(
            f"summary.loadedFile mismatch: expected file name {xml_path.name}, got {loaded_file}"
        )

    last_error = summary.get("lastError", "")
    if not isinstance(last_error, str):
        raise AssertionError("summary.lastError must be a string")
    if last_error:
        raise AssertionError(f"summary.lastError is not empty: {last_error}")

    adm_profiles = state.get("admProfiles")
    if not isinstance(adm_profiles, list):
        raise AssertionError("ui-state missing admProfiles list")

    if expected_profiles > 0 and len(adm_profiles) != expected_profiles:
        raise AssertionError(
            f"admProfiles count mismatch for {xml_path.name}: expected {expected_profiles}, got {len(adm_profiles)}"
        )


def main() -> int:
    args = parse_args()

    backend = Path(args.backend).resolve()
    xml_dir = Path(args.xml_dir).resolve()

    if not backend.exists():
        print(f"ERROR: backend executable not found: {backend}", file=sys.stderr)
        return 2
    if not xml_dir.exists():
        print(f"ERROR: xml directory not found: {xml_dir}", file=sys.stderr)
        return 2

    xml_files = discover_xml_files(xml_dir)
    if not xml_files:
        print(f"ERROR: no XML files found in {xml_dir}", file=sys.stderr)
        return 2

    base_url = f"http://{args.host}:{args.port}"
    failures: list[str] = []

    backend_proc = subprocess.Popen([str(backend)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        wait_for_health(base_url, args.health_timeout)

        for xml_path in xml_files:
            ok, message = load_xml(base_url, xml_path)
            if not ok:
                failures.append(f"{xml_path.name}: load failed: {message}")
                continue

            try:
                state = http_json("GET", f"{base_url}/api/ui-state")
                expected = expected_profile_count(xml_path)
                validate_state(state, xml_path, expected)
                print(f"[OK ] {xml_path.relative_to(xml_dir.parent)}")
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{xml_path.name}: {exc}")

    finally:
        backend_proc.terminate()
        try:
            backend_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            backend_proc.kill()

    if failures:
        print("\nXML regression failures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"\nAll {len(xml_files)} XML file(s) validated successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
