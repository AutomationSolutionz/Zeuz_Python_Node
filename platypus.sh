#!/bin/sh

# Clone the repository if node_cli.py does not exist
if [ ! -f "zeuz_node" ]; then
    echo "ZeuZ Node not found, cloning repository..."
    git clone https://github.com/AutomationSolutionz/Zeuz_Python_Node.git zeuz_node
    cd zeuz_node
    git switch uv-and-cli-cleanup
    cd ..
fi

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

cd zeuz_node
../.venv/bin/uv sync --active
../.venv/bin/python node_cli.py
