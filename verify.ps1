$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"
$venvDir = Join-Path $backendDir ".venv"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$Program,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory
    )

    Push-Location $WorkingDirectory
    try {
        & $Program @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed with exit code $LASTEXITCODE : $Program $($Arguments -join ' ')"
        }
    }
    finally {
        Pop-Location
    }
}

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    throw "Python was not found on PATH. Install Python 3.10+ and retry."
}

$requiredEnvKeys = @(
    "GROQ_API_KEY",
    "GROQ_MODEL",
    "VERCEL_ORIGIN",
    "PORT",
    "NEXT_PUBLIC_API_URL"
)
$exampleEnvPath = Join-Path $repoRoot ".env.example"
if (-not (Test-Path $exampleEnvPath)) {
    throw "Missing .env.example at repository root."
}
$exampleContents = Get-Content $exampleEnvPath -Raw
foreach ($key in $requiredEnvKeys) {
    if ($exampleContents -notmatch "(?m)^\s*$([regex]::Escape($key))=") {
        throw "The root .env.example is missing $key."
    }
}
Write-Host "Environment template: required backend and frontend keys are present."
Write-Host "Secrets are not required for this test run; Groq is mocked by pytest."

if (-not (Test-Path $venvDir)) {
    Invoke-Checked -Program $pythonCommand.Source -Arguments @("-m", "venv", $venvDir) -WorkingDirectory $repoRoot
}
$venvPython = Join-Path $venvDir "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Virtual environment Python was not created at $venvPython."
}

Invoke-Checked -Program $venvPython -Arguments @("-m", "pip", "install", "-r", "requirements.txt") -WorkingDirectory $backendDir
Invoke-Checked -Program $venvPython -Arguments @("-m", "pytest", "-q", "-p", "no:cacheprovider", "test_main.py") -WorkingDirectory $backendDir

Invoke-Checked -Program "npm" -Arguments @("ci") -WorkingDirectory $frontendDir
Invoke-Checked -Program "npm" -Arguments @("run", "build") -WorkingDirectory $frontendDir

Write-Host "Backend tests and frontend production build completed successfully." -ForegroundColor Green
