# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Setting up virtual environment..."
    python -m venv .venv
}

# Activate virtual environment
. .\.venv\Scripts\Activate.ps1

# Check if uv is installed
try {
    $uvCheck = uv --version
    Write-Host "uv is already installed"
} catch {
    Write-Host "uv not found, installing uv..."
    pip install uv
}

# Ensure virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    . .\.venv\Scripts\Activate.ps1
}

# Run uv commands
uv sync
uv run node_cli.py