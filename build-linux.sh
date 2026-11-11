#!/bin/bash
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

# build-linux.sh - Build AM-Viewer on Linux (x86_64, GCC)

set -e

PROFILE="conan/profiles/linux-gcc-x64"
BUILD_DIR="build-oat"

echo "Building AM-Viewer for Linux..."
echo "==============================="

# Check for system dependencies
if ! command -v gcc > /dev/null 2>&1; then
    echo "Error: gcc not found. Install build-essential or gcc-c++"
    exit 1
fi

if ! command -v cmake > /dev/null 2>&1; then
    echo "Error: cmake not found. Please install cmake"
    exit 1
fi

# Install Conan dependencies
echo "Installing Conan dependencies..."
conan install . --output-folder="$BUILD_DIR" --build=missing \
  -pr:h="$PROFILE" \
  -pr:b="$PROFILE"

# Configure CMake
echo "Configuring CMake..."
cmake -S . -B "$BUILD_DIR" -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_TOOLCHAIN_FILE="$BUILD_DIR"/build/Release/generators/conan_toolchain.cmake

# Build
echo "Building..."
cmake --build "$BUILD_DIR" --parallel

echo "Building frontend..."
(cd frontend && npm install && npm run build)

echo "Build complete!"
echo "Run backend: ./$BUILD_DIR/am_viewer"
echo "Run frontend (separate terminal): cd frontend && npm run dev"
