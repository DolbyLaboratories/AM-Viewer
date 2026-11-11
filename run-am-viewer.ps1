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

param(
    [string]$RootDir = $(Split-Path -Parent $MyInvocation.MyCommand.Path),
    [switch]$NoBrowser,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$BackendArgs
)

$ErrorActionPreference = 'Stop'
$frontendBasePort = 5173
$frontendUrl = "http://localhost:$frontendBasePort"

$backendBin = ''
$backendOat = Join-Path $RootDir 'build-oat\am_viewer.exe'
$backendOatRelease = Join-Path $RootDir 'build-oat\Release\am_viewer.exe'
$backendStd = Join-Path $RootDir 'build\am_viewer.exe'

if (Test-Path $backendOat) {
    $backendBin = $backendOat
} elseif (Test-Path $backendOatRelease) {
    $backendBin = $backendOatRelease
} elseif (Test-Path $backendStd) {
    $backendBin = $backendStd
} else {
    Write-Error 'Backend binary not found. Build first (expected build-oat\am_viewer.exe or build\am_viewer.exe).'
    exit 1
}

$frontendDir = Join-Path $RootDir 'frontend'
if (-not (Test-Path (Join-Path $frontendDir 'package.json'))) {
    Write-Error "Frontend package.json not found at $frontendDir"
}

$passthroughArgs = New-Object System.Collections.Generic.List[string]
foreach ($arg in $BackendArgs) {
    if ($arg -eq '--no-browser' -or $arg -eq '-NoBrowser') {
        $NoBrowser = $true
        continue
    }
    $passthroughArgs.Add($arg)
}

$backendOnly = $false
foreach ($arg in $passthroughArgs) {
    if ($arg -eq '-h' -or $arg -eq '--help' -or $arg -eq '--help-all' -or $arg -eq '-v' -or $arg -eq '--version' -or $arg -eq '--text') {
        $backendOnly = $true
        break
    }
}

if ($backendOnly) {
    & $backendBin @passthroughArgs
    exit $LASTEXITCODE
}

$env:AMV_BIN = $backendBin
Write-Host "AMV_BIN=$backendBin (frontend will manage the backend process)"

$frontendProc = $null

if (-not (Test-Path (Join-Path $frontendDir 'node_modules'))) {
    Write-Host 'Installing frontend dependencies...'
    Push-Location $frontendDir
    try { npm install } finally { Pop-Location }
}

try {
    $openFlag = if (-not $NoBrowser) { '--open' } else { $null }
    if ($NoBrowser) { Write-Host 'Browser auto-open disabled (-NoBrowser).' }

    Write-Host 'Starting frontend dev server'
    Write-Host ''
    Write-Host 'AM-Viewer is launching...'
    Write-Host "Frontend URL: $frontendUrl"
    Write-Host "Use the frontend 'Quit' button to stop everything cleanly."
    Write-Host '(Closing this launcher stops the frontend; the frontend will also stop the backend.)'
    Write-Host ''

    $devArgs = if ($openFlag) { "cd /d \"\"$frontendDir\"\" && npm run dev -- $openFlag" } else { "cd /d \"\"$frontendDir\"\" && npm run dev" }
    $frontendProc = Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $devArgs -PassThru

    $frontendProc.WaitForExit()
}
finally {
    if ($frontendProc -and -not $frontendProc.HasExited) {
        Stop-Process -Id $frontendProc.Id -Force
    }
}
