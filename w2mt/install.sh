#!/bin/bash
set -e

# Change to the script's directory
cd "$(dirname "$0")"

# Check for python3
if ! command -v python3 &> /dev/null
then
    echo "python3 could not be found. Please install Python 3."
    exit 1
fi

VENV_DIR="venv"

# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment '$VENV_DIR' already exists."
fi

# Activate the virtual environment and install dependencies
echo "Installing dependencies from requirements.txt..."
# The following line works in the script, but you need to activate it manually in your shell
source "$VENV_DIR/bin/activate"
pip install -r requirements.txt

echo ""
echo "--------------------------------------------------"
echo "Installation complete."
echo "To activate the virtual environment in your shell, run:"
echo "source w2mt/venv/bin/activate"
echo "--------------------------------------------------"
