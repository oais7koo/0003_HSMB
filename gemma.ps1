# gemma.ps1 - Gemma4 SLM Ollama Local Runner (PowerShell)

$PORT = "8080"
$OLLAMA_HOST = "0.0.0.0:$PORT"
$env:OLLAMA_HOST = $OLLAMA_HOST

function Write-Header {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "  Gemma4 SLM - Ollama Local Runner" -ForegroundColor Cyan
    Write-Host "  Port: $OLLAMA_HOST" -ForegroundColor White
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step($num, $msg) {
    Write-Host "[$num] $msg" -ForegroundColor Yellow
}

function Write-OK($msg) {
    Write-Host "      [OK] $msg" -ForegroundColor Green
}

function Write-Warn($msg) {
    Write-Host "      [!]  $msg" -ForegroundColor DarkYellow
}

function Write-Info($msg) {
    Write-Host "      [*]  $msg" -ForegroundColor Cyan
}

function Write-Err($msg) {
    Write-Host "      [ERROR] $msg" -ForegroundColor Red
}

# -- Refresh Windows PATH (User + Machine) -----------------------------------
$env:PATH = [Environment]::GetEnvironmentVariable('PATH','Machine') + ';' + [Environment]::GetEnvironmentVariable('PATH','User')

# -- Header ------------------------------------------------------------------
Write-Header

# -- Model Selection ---------------------------------------------------------
$MODELS = @(
    [PSCustomObject]@{ Key="1"; Name="gemma4:e2b"; Desc="Gemma4 5.1B Q4_K_M (lightweight, fast, default)" }
    [PSCustomObject]@{ Key="2"; Name="gemma4:e4b"; Desc="Gemma4 8B  Q4_K_M" }
    [PSCustomObject]@{ Key="3"; Name="gemma4:26b"; Desc="Gemma4 26B (not installed)" }
    [PSCustomObject]@{ Key="4"; Name="gemma4:31b"; Desc="Gemma4 31B (not installed)" }
)

# Load last used model (per computer)
$LAST_MODEL_FILE = "$PSScriptRoot\.claude\skills\gemma\references\last_model.json"
$COMPUTER = $env:COMPUTERNAME
$defaultKey = "1"
$lastModelHint = ""

if (Test-Path $LAST_MODEL_FILE) {
    try {
        $lastModelMap = Get-Content $LAST_MODEL_FILE -Raw | ConvertFrom-Json
        $lastModel = $lastModelMap.$COMPUTER
        if ($lastModel) {
            $match = $MODELS | Where-Object { $_.Name -eq $lastModel }
            if ($match) {
                $defaultKey = $match.Key
                $lastModelHint = " (last: $lastModel)"
            }
        }
    } catch { }
}

Write-Host "  Select a model to use: [$COMPUTER$lastModelHint]" -ForegroundColor White
foreach ($m in $MODELS) {
    $marker = if ($m.Key -eq $defaultKey) { "*" } else { " " }
    Write-Host ("   $marker {0}) {1,-18} {2}" -f $m.Key, $m.Name, $m.Desc) -ForegroundColor Gray
}
Write-Host ""
$modelChoice = Read-Host "  Choice (default: $defaultKey)"
if ([string]::IsNullOrWhiteSpace($modelChoice)) { $modelChoice = $defaultKey }

$selected = $MODELS | Where-Object { $_.Key -eq $modelChoice }
if (-not $selected) {
    Write-Warn "Invalid choice. Falling back to default model."
    $selected = $MODELS | Where-Object { $_.Key -eq $defaultKey }
}
$MODEL = $selected.Name

# Save selected model (per computer)
try {
    $lastModelMap = if (Test-Path $LAST_MODEL_FILE) {
        Get-Content $LAST_MODEL_FILE -Raw | ConvertFrom-Json
    } else {
        [PSCustomObject]@{}
    }
    $lastModelMap | Add-Member -NotePropertyName $COMPUTER -NotePropertyValue $MODEL -Force
    $lastModelMap | ConvertTo-Json | Set-Content $LAST_MODEL_FILE -Encoding UTF8
} catch { }

Write-OK "Selected model: $MODEL"
Write-Host ""

# -- 1. Check Ollama Installation --------------------------------------------
Write-Step "1/4" "Checking Ollama installation..."
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Warn "Ollama is not installed."

    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

    if (-not $isAdmin) {
        Write-Host ""
        Write-Err "Administrator privileges required to install Ollama."
        Write-Host "      [>] Option 1: Run PowerShell as Administrator and re-run this script" -ForegroundColor Gray
        Write-Host "      [>] Option 2: Install manually from https://ollama.com/download/windows" -ForegroundColor Gray
        Write-Host "      [>] Option 3: winget install Ollama.Ollama (run in admin PowerShell)" -ForegroundColor Gray
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }

    Write-Info "Starting automatic installation via winget..."
    Write-Host ""
    winget install Ollama.Ollama --silent --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Err "Automatic installation failed (winget exit code: $LASTEXITCODE)."
        Write-Host "      [>] Manual install: https://ollama.com/download/windows" -ForegroundColor Gray
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host ""
    Write-OK "Ollama installed successfully!"
    Write-Warn "Please close this window and run again to apply PATH changes."
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 0
}
Write-OK "Ollama installation confirmed"
Write-Host ""

# -- 2. Check Port Conflict --------------------------------------------------
Write-Step "2/4" "Checking port $PORT availability..."
$portInUse = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue
if ($portInUse) {
    $pid_ = $portInUse[0].OwningProcess
    $proc = Get-Process -Id $pid_ -ErrorAction SilentlyContinue
    $procName = if ($proc) { $proc.ProcessName } else { "unknown" }

    Write-Warn "Port $PORT is already in use."
    Write-Host "      [>] Process: $procName (PID: $pid_)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "      Select an option:" -ForegroundColor White
    Write-Host "        1) Kill existing process and restart" -ForegroundColor White
    Write-Host "        2) Switch to port 11434 (Ollama default)" -ForegroundColor White
    Write-Host "        3) Try connecting anyway (OK if existing is Ollama)" -ForegroundColor White
    Write-Host "        0) Cancel" -ForegroundColor White
    Write-Host ""
    $choice = Read-Host "      Choice (0/1/2/3)"

    switch ($choice) {
        "1" {
            Write-Host ""
            Write-Info "Killing PID $pid_ ($procName)..."
            Stop-Process -Id $pid_ -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
            Write-OK "Process terminated"
            Write-Info "Restarting Ollama server..."
            Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
            $ready = $false
            for ($i = 1; $i -le 15; $i++) {
                Start-Sleep -Seconds 1
                try {
                    $r = Invoke-WebRequest -Uri "http://localhost:$PORT" -TimeoutSec 1 -ErrorAction Stop
                    $ready = $true
                    break
                } catch { }
                Write-Host "      [*]  Waiting for server... ($i/15)" -ForegroundColor DarkGray
            }
            if ($ready) {
                Write-OK "Server ready"
            } else {
                Write-Warn "No server response - continuing anyway"
            }
        }
        "2" {
            Write-Host ""
            $PORT = "11434"
            $OLLAMA_HOST = "0.0.0.0:$PORT"
            $env:OLLAMA_HOST = $OLLAMA_HOST
            Write-OK "Switched to port 11434."
        }
        "3" {
            Write-Host ""
            Write-Info "Attempting to connect to existing server..."
        }
        default {
            Write-Host ""
            Write-Info "Cancelled."
            exit 0
        }
    }
} else {
    Write-OK "Port $PORT is available"
    Write-Info "Starting Ollama server..."
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    $ready = $false
    for ($i = 1; $i -le 15; $i++) {
        Start-Sleep -Seconds 1
        try {
            Invoke-WebRequest -Uri "http://localhost:$PORT" -TimeoutSec 1 -ErrorAction Stop | Out-Null
            $ready = $true
            break
        } catch { }
        Write-Host "      [*]  Waiting for server... ($i/15)" -ForegroundColor DarkGray
    }
    if ($ready) {
        Write-OK "Server ready"
    } else {
        Write-Warn "No server response - continuing anyway"
    }
}
Write-Host ""

# -- 3. Check Model (filesystem + ollama list) --------------------------------
Write-Step "3/4" "Checking model: $MODEL"
$modelName = $MODEL.Split(":")[0]
$modelTag  = if ($MODEL.Contains(":")) { $MODEL.Split(":")[1] } else { "latest" }

$ollamaBase = if ($env:OLLAMA_MODELS) {
    $env:OLLAMA_MODELS
} else {
    "$env:USERPROFILE\.ollama\models"
}
$manifestPath = "$ollamaBase\manifests\registry.ollama.ai\library\$modelName\$modelTag"
Write-Host "      [>] Path: $manifestPath" -ForegroundColor DarkGray

$modelFound = (Test-Path $manifestPath)
if (-not $modelFound) {
    $modelList = ollama list 2>&1
    $modelFound = ($modelList -match [regex]::Escape($modelName))
}

if (-not $modelFound) {
    Write-Warn "Model not found locally."
    Write-Info "Starting download (may take several minutes)..."
    Write-Host ""
    ollama pull $MODEL
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Err "Model download failed."
        Write-Host "      [>] Check your network connection and try again." -ForegroundColor Gray
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host ""
    Write-OK "Model downloaded: $MODEL"
} else {
    Write-OK "Model confirmed: $MODEL"
}
Write-Host ""

# -- 4. Run ------------------------------------------------------------------
Write-Step "4/4" "Running Gemma4..."
Write-Host "      Port: http://localhost:$PORT" -ForegroundColor Gray
Write-Host "      Exit: type /bye or press Ctrl+C" -ForegroundColor Gray
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
ollama run $MODEL
