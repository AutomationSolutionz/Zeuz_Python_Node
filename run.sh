#!/bin/sh

# Check if uv is installed globally or in the virtual environment
if ! command -v uv &> /dev/null; then
    echo "uv not found, setting up virtual environment and installing uv..."
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    if ! pip show uv &> /dev/null; then
        pip install uv
    fi
else
    echo "uv is already installed"
fi

# Activate the virtual environment
source .venv/bin/activate

uv sync
uv run node_cli.py
