REM Copyright (c) 2026 Dolby International AB.
REM All rights reserved.
REM
REM Redistribution and use in source and binary forms, with or without
REM modification, are permitted provided that the following conditions are
REM met:
REM
REM 1. Redistributions of source code must retain the above copyright
REM    notice, this list of conditions and the following disclaimer.
REM
REM 2. Redistributions in binary form must reproduce the above copyright
REM    notice, this list of conditions and the following disclaimer in
REM    the documentation and/or other materials provided with the
REM    distribution.
REM
REM 3. Neither the name of the copyright holder nor the names of its
REM    contributors may be used to endorse or promote products derived
REM    from this software without specific prior written permission.
REM
REM NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED
REM BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
REM CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
REM BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
REM FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
REM HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
REM SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
REM LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
REM DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
REM THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
REM (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
REM OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

@echo off
REM build-windows.bat - Build AM-Viewer on Windows (x86_64, MSVC)

setlocal enabledelayedexpansion

set PROFILE=conan/profiles/windows-msvc-x64
set BUILD_DIR=build-oat

REM Check for required tools
where cl >nul 2>nul
if errorlevel 1 (
    echo Error: MSVC compiler not found. Install Visual Studio Build Tools.
    exit /b 1
)

where cmake >nul 2>nul
if errorlevel 1 (
    echo Error: cmake not found. Please install CMake.
    exit /b 1
)

echo Building AM-Viewer for Windows...
echo =================================

REM Install Conan dependencies
echo Installing Conan dependencies...
conan install . --output-folder=%BUILD_DIR% --build=missing ^
  -pr:h=%PROFILE% ^
  -pr:b=%PROFILE%

if errorlevel 1 (
    echo Error during Conan install
    exit /b 1
)

REM Configure CMake
echo Configuring CMake...
cmake -S . -B %BUILD_DIR% -DCMAKE_BUILD_TYPE=Release ^
    -DCMAKE_TOOLCHAIN_FILE=%BUILD_DIR%/build/Release/generators/conan_toolchain.cmake ^
  -G "Visual Studio 17 2022"

if errorlevel 1 (
    echo Error during CMake configuration
    exit /b 1
)

REM Build
echo Building...
cmake --build %BUILD_DIR% --config Release --parallel

if errorlevel 1 (
    echo Error during build
    exit /b 1
)

echo Building frontend...
pushd frontend
call npm install
if errorlevel 1 (
    popd
    echo Error during npm install
    exit /b 1
)
call npm run build
if errorlevel 1 (
    popd
    echo Error during frontend build
    exit /b 1
)
popd

echo Build complete!
echo Run backend: %BUILD_DIR%\Release\am_viewer.exe
echo Run frontend (separate terminal): cd frontend && npm run dev
