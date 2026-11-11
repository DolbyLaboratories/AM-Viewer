# Cross-Platform Build Guide

This document covers building AM-Viewer on macOS, Linux, and Windows.

## macOS (ARM64)

### Prerequisites
- Conan 2.x
- CMake 3.16+
- clang 16+ (via Xcode or homebrew)
- libpcap and zlib (via homebrew or Conan)

### Build

```bash
conan install . --output-folder=build --build=missing \
  -pr:h=conan/profiles/macos-arm64-clang16 \
  -pr:b=conan/profiles/macos-arm64-clang16

cmake -S . -B build-oat -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_TOOLCHAIN_FILE=build/build/Release/generators/conan_toolchain.cmake

cmake --build build-oat --parallel

./build-oat/am_viewer
```

## Linux (x86_64, GCC)

### Prerequisites
- Conan 2.x
- CMake 3.16+
- GCC 11+ (or Clang 14+)
- libpcap-dev and zlib1g-dev (system packages)

### Install system dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake libpcap-dev zlib1g-dev python3
```

**Fedora/RHEL:**
```bash
sudo dnf install -y gcc-c++ cmake libpcap-devel zlib-devel
```

### Build

```bash
conan install . --output-folder=build --build=missing \
  -pr:h=conan/profiles/linux-gcc-x64 \
  -pr:b=conan/profiles/linux-gcc-x64

cmake -S . -B build-oat -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_TOOLCHAIN_FILE=build/build/Release/generators/conan_toolchain.cmake

cmake --build build-oat --parallel

./build-oat/am_viewer
```

### Frontend (same for all platforms)

```bash
cd frontend
npm install
npm run build
```

## Windows (x86_64, MSVC)

### Prerequisites
- Conan 2.x
- CMake 3.16+ (via Visual Studio or standalone)
- Visual Studio 2019+ with C++ build tools (MSVC v193)
- WinPcap or Npcap developer pack (for libpcap)

### Install dependencies

1. **Visual Studio Build Tools:**
   - Download and install Visual Studio Build Tools or Community Edition
   - Ensure C++ workload is selected

2. **Conan:**
   ```cmd
   pip install conan
   ```

3. **WinPcap/Npcap SDK:**
   - Download Npcap SDK from https://npcap.com/
   - Extract to a known location (e.g., `C:\Npcap-SDK`)

### Build

```cmd
conan install . --output-folder=build --build=missing ^
  -pr:h=conan/profiles/windows-msvc-x64 ^
  -pr:b=conan/profiles/windows-msvc-x64

cmake -S . -B build-oat -DCMAKE_BUILD_TYPE=Release ^
  -DCMAKE_TOOLCHAIN_FILE=build/build/Release/generators/conan_toolchain.cmake ^
  -DPCAP_INCLUDE_DIR="C:\Npcap-SDK\Include" ^
  -DPCAP_LIBRARY="C:\Npcap-SDK\Lib\x64\wpcap.lib"

cmake --build build-oat --config Release

build-oat\Release\am_viewer.exe
```

### Frontend (same for all platforms)

```cmd
cd frontend
npm install
npm run build
```

## Troubleshooting

### Conan dependency conflicts
If Conan fails, try:
```bash
conan remove "*" -c  # Clear cache
conan install . --build=missing  # Rebuild all
```

### CMake not finding compiler
Set `CC` and `CXX` environment variables:
```bash
# Linux/macOS
export CC=gcc
export CXX=g++

# Windows (PowerShell)
$env:CC="cl"
$env:CXX="cl"
```

### libpcap/Npcap not found
- **Linux:** Ensure `libpcap-dev` is installed (`apt-get install libpcap-dev`)
- **macOS:** `brew install libpcap` or rely on Conan
- **Windows:** Verify Npcap SDK path in CMake command

## Frontend development

For local frontend development (with live reload):
```bash
cd frontend
npm run dev
```

Frontend dev server runs on `http://localhost:5173` and proxies `/api` requests to the backend.
