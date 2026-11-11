#!/usr/bin/env bash
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

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
FRONTEND_BASE_PORT=5173
NO_BROWSER=0
PASSTHROUGH_ARGS=()
BACKEND_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-browser)
      NO_BROWSER=1
      shift
      ;;
    -h|--help|--help-all|-v|--version|--text)
      BACKEND_ONLY=1
      PASSTHROUGH_ARGS+=("$1")
      shift
      ;;
    *)
      PASSTHROUGH_ARGS+=("$1")
      shift
      ;;
  esac
done

if [[ -x "$ROOT_DIR/build-oat/am_viewer" ]]; then
  BACKEND_BIN="$ROOT_DIR/build-oat/am_viewer"
elif [[ -x "$ROOT_DIR/build/am_viewer" ]]; then
  BACKEND_BIN="$ROOT_DIR/build/am_viewer"
else
  echo "Backend binary not found. Build first (expected build-oat/am_viewer or build/am_viewer)."
  exit 1
fi

cleanup() {
  if [[ -n "${FRONTEND_PID:-}" ]]; then
    kill "$FRONTEND_PID" 2>/dev/null || true
    wait "$FRONTEND_PID" 2>/dev/null || true
  fi
  pids=$(lsof -ti tcp:${FRONTEND_BASE_PORT}-$((FRONTEND_BASE_PORT + 9)) 2>/dev/null || true)
  if [[ -n "$pids" ]]; then
    kill $pids 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

if [[ $BACKEND_ONLY -eq 1 ]]; then
  exec "$BACKEND_BIN" ${PASSTHROUGH_ARGS+"${PASSTHROUGH_ARGS[@]}"}
fi

export AMV_BIN="$BACKEND_BIN"
echo "AMV_BIN=$AMV_BIN (frontend will manage the backend process)"


if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
  echo "Frontend package.json not found at $FRONTEND_DIR"
  exit 1
fi

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  echo "Installing frontend dependencies..."
  (cd "$FRONTEND_DIR" && npm install)
fi

if [[ ! -d "$FRONTEND_DIR/build" ]] || \
   [[ -n "$(find "$FRONTEND_DIR/src" "$FRONTEND_DIR/package.json" -newer "$FRONTEND_DIR/build" -print -quit)" ]]; then
  echo "Building frontend..."
  (cd "$FRONTEND_DIR" && npm run build)
fi

OPEN_FLAG=()
if [[ $NO_BROWSER -eq 0 ]]; then
  OPEN_FLAG=("--open")
else
  echo "Browser auto-open disabled (--no-browser)."
fi

echo "Starting frontend server..."
echo "Frontend URL: http://localhost:${FRONTEND_BASE_PORT}"
echo "Use the frontend 'Quit' button to stop everything cleanly."
echo "(Ctrl+C here stops the frontend; the frontend will also stop the backend.)"
echo
(
  cd "$FRONTEND_DIR" &&
  exec npm run preview -- --port "$FRONTEND_BASE_PORT" ${OPEN_FLAG+"${OPEN_FLAG[@]}"}
) &
FRONTEND_PID=$!

wait "$FRONTEND_PID" 2>/dev/null || true
