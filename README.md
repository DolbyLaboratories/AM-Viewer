# AM-Viewer (oatpp + SvelteKit)

AM-Viewer is a web-based Audio Metadata Viewer:
- **Backend:** C++17 + **oatpp** HTTP API, tinyxml2, libpcap, zlib
- **Frontend:** **SvelteKit** (Vite + TypeScript)

AM Viewer supports display of Serialized ADM (ITU-R BS 2125) metadata carried in either SMPTE ST 2110-31 or
SMPTE ST 2110-41 IP streams. The Dolby E ADM profile and ITU-R BS. 2168 emission profile are supported.

## Features

- **Live capture** of ST 2110-31 (AM824) and ST 2110-41 streams from a selected network interface.
- **Automatic service discovery** (SAP/mDNS) on the selected interface, with manual selection by pasting an SDP.
- **S-ADM decoding** of the carried metadata, including Dolby E program-specific metadata.
- **Metadata display** of programmes, beds, objects and their cross-references, updated live per frame.
- **Stream health indicators**: frame counter with continuity-error detection, FPS derived from RTP timestamps, and a measured (real) FPS graph.
- **XML tools**: view or save the current S-ADM frame as XML, and load offline ADM/S-ADM XML files.
- **SDP download** for any discovered service.
- **Log viewer** with level/tag filtering, live tail, download and clear.
- **Text mode** for headless extraction of S-ADM XML from an interface or a pcap file.
- **Regression suite** that replays PCAP captures and compares against reference XML.

## Repository layout

| Path | Purpose |
|------|---------|
| `src/main.cpp` | oatpp server entry point |
| `src/web/` | API controller, app state, XML parser, capture service |
| `src/model/` | shared metadata model structs |
| `frontend/` | SvelteKit WebUI |
| `tests/` | regression suite |
| `pcap/` | PCAP files used for regression replay |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Architecture diagram of the frontend, backend and library dependencies |

## Build

One-step build scripts build the backend (Conan + CMake into `build-oat/`) and then the frontend (`npm install && npm run build`):

| Platform | Script |
|----------|--------|
| macOS (arm64) | `./build-macos.sh` |
| Linux (x86_64, GCC) | `./build-linux.sh` |
| Windows (x86_64, MSVC) | `build-windows.bat` |

The steps below build the backend manually.

### Prerequisites

- Conan 2.x
- CMake 3.16+
- Node.js and npm (frontend)
- C++17 compiler (clang 16+ on macOS)
- libpcap and zlib (via Conan)

### Install Conan dependencies

```bash
conan install . --output-folder=build-oat --build=missing \
  -pr:h=conan/profiles/macos-arm64-clang16 \
  -pr:b=conan/profiles/macos-arm64-clang16
```

### Configure + build

```bash
cmake -S . -B build-oat -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_TOOLCHAIN_FILE=build-oat/build/Release/generators/conan_toolchain.cmake
cmake --build build-oat --parallel
```

On Windows the binary is `build-oat\Release\am_viewer.exe`.

### Run backend

```bash
./build-oat/am_viewer
```

Backend listens on `http://localhost:8000`.

### Command line options

Show all options:

```bash
./build-oat/am_viewer --help
```

| Option | Value | Description |
|---|---|---|
| `-h`, `--help` | none | Show command usage. |
| `--help-all` | none | Show command usage including generic Qt options. |
| `-v`, `--version` | none | Print version and exit. |
| `--xml` | `<file>` | Load an ADM/S-ADM XML file at startup. |
| `--sdp` | `<file>` | Load SDP file to preconfigure capture target. |
| `--debug` | none | Enable debug logging. |
| `--libpcap` | none | Enable libpcap path (where supported by current runtime mode). |
| `--text` | none | Run in non-GUI text mode (no web server/frontend). |
| `--interface` | `<name>` | Capture interface for text mode (for example `en0`). |
| `--pcap` | `<file>` | Replay packets from a pcap file in text mode. |
| `--address` | `<ip>` | Destination multicast/unicast address filter for text mode. |
| `--port` | `<port>` | Destination UDP port filter for text mode. |
| `--codec` | `AM824`\|`ST2110-41` | Payload codec/container used in text mode. |
| `--timeout-ms` | `<ms>` | Text mode timeout in milliseconds (default: `10000`). |
| `--xml-frames` | `<count>` | Number of XML frames to capture before exit in text mode (default: `1`). |
| `--save-xml` | `<file>` | Write captured XML payload to file in text mode. |

Text mode rules:
- `--text` requires exactly one input source: `--interface` or `--pcap`.
- `--text` requires `--codec`.
- For `--interface`, both `--address` and `--port` are required.
- For `--pcap`, `--address` and `--port` are optional, but if one is set the other must also be set.

Examples:

```bash
# Start backend with an offline XML file preloaded
./build-oat/am_viewer --xml xml/51_me_2d_ad.sadm.xml

# Start backend with explicit SDP and debug logs
./build-oat/am_viewer --sdp /absolute/path/session.sdp --debug

# Text mode from live interface
./build-oat/am_viewer --text --interface en0 --address 239.100.10.1 --port 5004 --codec ST2110-41 --xml-frames 1

# Text mode from pcap replay
./build-oat/am_viewer --text --pcap ./pcap/st2110-31_51_me.sadm.pcap --codec AM824 --xml-frames 1 --save-xml /tmp/out.xml
```

### Run full app (backend + frontend together)

```bash
./run-am-viewer.sh
```

Without auto-opening a browser tab:

```bash
./run-am-viewer.sh --no-browser
```

Windows (PowerShell or Command Prompt):

```bat
run-am-viewer.bat
```

Without auto-opening a browser tab:

```bat
run-am-viewer.bat --no-browser
```

If PowerShell execution policy blocks the script, run once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Temporary (current shell only, no permanent policy change):

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

This launches both services concurrently. The backend binary is found in `build-oat/` (or `build/`); the frontend spawns and manages it. On Linux/macOS the script serves the production frontend build (`vite preview`) and rebuilds it automatically if `frontend/src` is newer than `frontend/build`; on Windows it runs the dev server and runs `npm install` if `node_modules` is missing. By default it opens the frontend URL in a browser tab (unless `--no-browser` is used). Use the **Quit** button in the web UI to stop both processes.

All backend CLI options are forwarded through the launcher scripts (Linux/macOS and Windows). Examples:

```bash
./run-am-viewer.sh --xml /absolute/path/to/file.sadm.xml
./run-am-viewer.sh --sdp /absolute/path/to/file.sdp --debug
./run-am-viewer.sh --text --pcap ./pcap/st2110-31_51_me.sadm.pcap --xml-frames 1 --save-xml /tmp/out.xml
./run-am-viewer.sh --help
./run-am-viewer.sh --version
```

`--help`, `--help-all`, `--version`, and `--text` run in backend-only mode (frontend is not started).

## Frontend

```bash
cd frontend
npm install
npm run dev      # development server
npm run build   # production build
```

The frontend runs on `http://localhost:5173`. Its server routes call the backend at `localhost:8000` (override with `AMV_BACKEND_HOST` / `AMV_BACKEND_PORT`). When `AMV_BIN` is set to the backend binary, the frontend starts and stops the backend itself; otherwise start `am_viewer` manually.

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Service health check |
| `GET` | `/api/model` | Model summary (counts) |
| `GET` | `/api/interfaces` | List available network interfaces |
| `GET` | `/api/ui-state` | Full UI state: indicators, ADM metadata, beds, objects, presentations |
| `POST` | `/api/load-xml?file=<abs-path>` | Parse and load an ADM/S-ADM XML file |
| `POST` | `/api/service/select` | Save network service selection (interface, address, port, codec, …) |
| `POST` | `/api/capture/start` | Start live pcap capture on the selected interface/address/port |
| `POST` | `/api/capture/stop` | Stop live pcap capture |
| `POST` | `/api/app/exit` | Stop capture and terminate the backend process |

## Basic UI Instructions

Open `http://localhost:5173` (opened automatically by `run-am-viewer.sh`). The page shows "Connecting to server..." / "Connecting to backend..." until the backend is reachable.

### Receiving a stream

1. In **Service Selection** (left panel), choose a network interface from the **Interface** drop-down.
2. Wait while the viewer listens; discovered streams appear as buttons in the list.
3. Click a stream to select it. Capture starts and metadata appears once the first frame arrives.
4. If a stream is not announced, click **Upload SDP**, paste the SDP text and press **Submit**.
5. Click **SDP** on a discovered stream to view or **Download** its SDP.

### Stream Info bar

Shown across the top once a stream is selected:
- Stream name, system, address:port and codec.
- **Frame Counter**: increments per metadata frame. A continuity issue is flagged here; use its reset control to clear it.
- **FPS**: rate derived from RTP packet timestamps (sender's intended rate). An issue is flagged if it is unstable and can be reset.
- **Real FPS graph**: measured frame arrival rate over time.

### Metadata tab

- **S-ADM Info**: S-ADM/ADM version and profile fields.
- **Programmes**: table of programmes with name, layout, language and element icons (`P` programme, `B` bed, `O` object).
- **S-ADM Content**: the **Summary** tab lists all audio objects and Dolby E metadata; one tab per programme shows that programme's info, its beds/objects and its Dolby E metadata. Selecting a new stream returns to the first tab.
- **View XML** / **Save XML**: display or download the current frame as `<stream>-<frame>.sadm.xml`.

### Logs tab

- **Filter** by log level and tag (the badge shows the number of active filters; **Reset all** clears them).
- **Live** follows new messages; scrolling up pauses the tail.
- **Download logs** saves the log; **Clear all logs** removes entries after confirmation.

### Quitting

Use the power icon at the top-right and choose **Quit** to stop the frontend and backend (shown when launched via the run scripts).

### Load XML example

```bash
curl -X POST "http://localhost:8000/api/load-xml?file=/absolute/path/to/file.sadm.xml"
```

After a successful load, `GET /api/ui-state` returns populated beds, objects, presentations and the S-ADM/ADM version and profile fields, with the S-ADM indicator set to `on`.

## Regression Suite

Run all regression checks (text/XML reference + web UI-state PCAP replay) with a single command:

```bash
python3 tests/regression_suite.py
```

This runs:
1. **XML regression** – extracts text-mode XML from each PCAP and compares against references in `tests/reference_xml/`
2. **UI-state regression** – starts the backend, replays RTP payloads from each PCAP over UDP, and validates all `/api/ui-state` fields

### Prerequisites

- Python 3.9+
- `tshark` (Wireshark CLI) in `PATH`
- Loopback capture access (`lo0` on macOS; may need `sudo` or group membership)

## Dependencies & Licenses

### Backend (C++)

| Project | Version | License | Repository |
|---------|---------|---------|------------|
| oatpp | 1.3.0 | Apache 2.0 | https://github.com/oatpp/oatpp |
| tinyxml2 | 10.0.0 | Zlib | https://github.com/leethomason/tinyxml2 |
| libpcap | 1.10.5 | BSD 3-Clause | https://www.tcpdump.org/ |
| zlib | 1.3.1 | Zlib | https://github.com/madler/zlib |
| CMake | 3.29.6 | BSD 3-Clause | https://cmake.org/ |

### Frontend (SvelteKit)

| Project | Version | License | Repository |
|---------|---------|---------|------------|
| Svelte | ^5.55.2 | MIT | https://github.com/sveltejs/svelte |
| SvelteKit | ^2.57.0 | MIT | https://github.com/sveltejs/kit |
| @sveltejs/adapter-node | ^5.5.4 | MIT | https://github.com/sveltejs/kit |
| @sveltejs/vite-plugin-svelte | ^7.0.0 | MIT | https://github.com/sveltejs/vite-plugin-svelte |
| Vite | ^8.0.7 | MIT | https://github.com/vitejs/vite |
| TypeScript | ^6.0.2 | Apache 2.0 | https://github.com/microsoft/TypeScript |
| svelte-check | ^4.4.6 | MIT | https://github.com/sveltejs/language-tools |
| sveltekit-sse | ^0.14.3 | MIT | https://github.com/razshare/sveltekit-sse |
| rotating-file-stream | ^3.2.9 | MIT | https://github.com/iccicci/rotating-file-stream |
| @types/node | ^25.6.0 | MIT | https://github.com/DefinitelyTyped/DefinitelyTyped |

### Build & Test Tools

| Project | License | Repository |
|---------|---------|------------|
| Conan | MIT | https://github.com/conan-io/conan |
| pytest | MIT | https://github.com/pytest-dev/pytest |
| tshark/Wireshark | GPL 2.0 | https://www.wireshark.org/ |

### Custom options

```bash
python3 tests/regression_suite.py \
  --backend ./build-oat/am_viewer \
  --text-binary ./build-oat/am_viewer \
  --pcap-dir ./pcap
```

Generate or refresh XML references:

```bash
python3 tests/regression_suite.py --generate-reference
```

