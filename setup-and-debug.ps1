# WebRTC + RAG Conferencing Diagnostic & Setup Script (Windows PowerShell)
# Usage: powershell -ExecutionPolicy Bypass -File setup-and-debug.ps1

param(
    [switch]$SkipDependencies = $false,
    [switch]$StartServices = $false
)

$ErrorActionPreference = "Continue"

function Print-Section { param([string]$Title)
    Write-Host "`n" -ForegroundColor White
    Write-Host ("═" * 50) -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host ("═" * 50) -ForegroundColor Cyan
    Write-Host ""
}

function Print-OK { param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Print-Error { param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Print-Warn { param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Test-PortOpen { param([int]$Port)
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.Connect("127.0.0.1", $Port)
        $tcpClient.Dispose()
        return $true
    }
    catch { return $false }
}

$ProjectRoot = Get-Location

# ─── Phase 1: Environment Check ─────────────────────────────────────────

Print-Section "PHASE 1: Environment Check"

# Node.js check
$nodeVersion = node --version 2>$null
if ($nodeVersion) {
    Print-OK "Node.js: $nodeVersion"
}
else {
    Print-Error "Node.js not installed. Download from https://nodejs.org/"
    exit 1
}

# npm check
$npmVersion = npm --version 2>$null
if ($npmVersion) {
    Print-OK "npm: $npmVersion"
}
else {
    Print-Error "npm not installed"
    exit 1
}

# Python check
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Print-OK "Python: $pythonVersion"
}
else {
    Print-Warn "Python not found. RAG backend requires Python 3.8+"
}

# ─── Phase 2: Install Dependencies ──────────────────────────────────────

if (-not $SkipDependencies) {
    Print-Section "PHASE 2: Installing Dependencies"

    if (Test-Path "AI_Enhanced_RealTime_Conferencing-main\server\package.json") {
        Write-Host "Installing server dependencies..." -ForegroundColor Gray
        Push-Location "AI_Enhanced_RealTime_Conferencing-main\server"
        npm install --silent | Out-Null
        Print-OK "Server dependencies installed"
        Pop-Location
    }

    if (Test-Path "AI_Enhanced_RealTime_Conferencing-main\client\package.json") {
        Write-Host "Installing client dependencies..." -ForegroundColor Gray
        Push-Location "AI_Enhanced_RealTime_Conferencing-main\client"
        npm install --silent | Out-Null
        Print-OK "Client dependencies installed"
        Pop-Location
    }

    if (Test-Path "rag-chatbot-main\backend\requirements.txt") {
        Write-Host "Installing RAG dependencies..." -ForegroundColor Gray
        Push-Location "rag-chatbot-main\backend"
        pip install -q -r requirements.txt 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Print-OK "RAG dependencies installed"
        }
        else {
            Print-Warn "Some Python packages may have failed — see pip output"
        }
        Pop-Location
    }
}

# ─── Phase 3: Port Availability Check ─────────────────────────────────────

Print-Section "PHASE 3: Port Availability Check"

$ports = @{
    3011 = "Signaling Server"
    8000 = "RAG Backend"
    5173 = "React Dev Server"
}

foreach ($port in $ports.Keys) {
    if (Test-PortOpen -Port $port) {
        Print-Warn "$($ports[$port]) (port $port) already in use"
    }
    else {
        Print-OK "Port $port available for $($ports[$port])"
    }
}

# ─── Phase 4: Connectivity Tests ─────────────────────────────────────────

Print-Section "PHASE 4: Connectivity Tests"

try {
    $response = Invoke-WebRequest -Uri "https://api.groq.com" -TimeoutSec 2 -ErrorAction Stop
    Print-OK "Internet connectivity: OK (can reach Groq API)"
}
catch {
    Print-Warn "Cannot reach Groq API — LLM features may fail (check your internet)"
}

# ─── Phase 5: Config Validation ─────────────────────────────────────────

Print-Section "PHASE 5: Configuration Validation"

# Check for GROQ API key
$groqKey = $env:GROQ_API_KEY
if (-not $groqKey) {
    Print-Warn "GROQ_API_KEY not set. RAG backend will fail."
    Write-Host "  Set it: `$env:GROQ_API_KEY = 'gsk_your_key_here'" -ForegroundColor Gray
    Write-Host "  Get key from: https://console.groq.com" -ForegroundColor Gray
}
else {
    $keyLength = $groqKey.Length
    Print-OK "GROQ_API_KEY set ($keyLength chars)"
}

# ─── Phase 6: Service Startup ───────────────────────────────────────────

if ($StartServices) {
    Print-Section "PHASE 6: Starting Services"

    # Signaling Server
    Write-Host "Starting Signaling Server (port 3011)..." -ForegroundColor Gray
    Start-Process pwsh -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$ProjectRoot\AI_Enhanced_RealTime_Conferencing-main\server'; npm start"
    ) -WindowStyle Normal
    Print-OK "Signaling server process started"

    Start-Sleep -Seconds 2

    # RAG Backend
    if ($groqKey) {
        Write-Host "Starting RAG Backend (port 8000)..." -ForegroundColor Gray
        Start-Process pwsh -ArgumentList @(
            "-NoExit",
            "-Command",
            "`$env:GROQ_API_KEY = '$groqKey'; cd '$ProjectRoot\rag-chatbot-main\backend'; python main.py"
        ) -WindowStyle Normal
        Print-OK "RAG backend process started"
    }
    else {
        Print-Warn "GROQ_API_KEY not set — skipping RAG backend"
    }

    Start-Sleep -Seconds 2

    # React Dev Server
    Write-Host "Starting React Dev Server (port 5173)..." -ForegroundColor Gray
    Start-Process pwsh -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$ProjectRoot\AI_Enhanced_RealTime_Conferencing-main\client'; npm run dev"
    ) -WindowStyle Normal
    Print-OK "React dev server process started"

    Write-Host "`nAll services started! Open http://localhost:5173 when ready." -ForegroundColor Green
}

# ─── Phase 7: Diagnostic Output ────────────────────────────────────────

Print-Section "PHASE 7: Quick Start Guide"

$guide = @"
MANUAL STARTUP (if -StartServices not used):

Terminal 1 - Signaling Server:
  cd AI_Enhanced_RealTime_Conferencing-main\server
  npm start

Terminal 2 - RAG Backend:
  `$env:GROQ_API_KEY = "gsk_YOUR_KEY"
  cd rag-chatbot-main\backend
  python main.py

Terminal 3 - React Frontend:
  cd AI_Enhanced_RealTime_Conferencing-main\client
  npm run dev

Then open: http://localhost:5173

CONNECTIVITY TESTS (PowerShell):
  curl http://localhost:3011 -Verbose     # Signaling
  curl http://localhost:8000/sessions     # RAG backend
  curl http://localhost:5173              # Frontend

BROWSER DEBUGGING (Press F12):
  - Console → Look for "Socket connected"
  - Console → Watch for "user-joined" events
  - Console → Monitor "webrtc-offer" / "webrtc-answer"
  - Network → Filter to "WS" for WebSocket traffic

COMMON ISSUES:

  ✗ "Connection refused"
    → Service not running; check Terminal output
    → Use: Get-NetTCPConnection -LocalPort PORT | Select OwningProcess
    → Kill: Stop-Process -Id PROCESS_ID -Force

  ✗ "CORS error in browser"
    → Check: rag-chatbot-main/backend/main.py
    → Ensure localhost:5173 in CORS_ORIGINS

  ✗ "GROQ_API_KEY not set"
    → Export before running Python
    → Verify: Write-Host $env:GROQ_API_KEY

  ✗ "Port already in use"
    → Get-NetTCPConnection -LocalPort PORT
    → Stop-Process -Id PROCESS_ID -Force

LOGS LOCATION:
  - Server logs: Terminal 1 output
  - RAG logs: Terminal 2 output
  - Frontend logs: Browser Console (F12)
  - Browser network logs: DevTools Network tab

"@

Write-Host $guide -ForegroundColor White

Print-OK "Setup complete!"
Write-Host "`nRun with -StartServices to auto-launch all services:" -ForegroundColor Gray
Write-Host "  powershell -ExecutionPolicy Bypass -File setup-and-debug.ps1 -StartServices`n" -ForegroundColor Gray
