#!/bin/sh

if [ ! -d ".venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# Check if uv is installed globally or in the virtual environment
if ! command -v uv &> /dev/null; then
    echo "uv not found, installing uv..."
    if ! pip show uv &> /dev/null; then
        pip install uv
    fi
fi

# Activate the virtual environment
source .venv/bin/activate

uv sync
uv run node_cli.py
