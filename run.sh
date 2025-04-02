#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python 3 is installed
if ! command_exists python3; then
    echo "Python 3 is not installed. Please install Python 3.11 first."
    exit 1
fi

# Check if venv module is available
if ! python3 -c "import venv" &>/dev/null; then
    echo "Python venv module is not installed. Please install python3-venv first."
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Virtual environment path
VENV_DIR="$SCRIPT_DIR/.venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install requirements
    echo "Installing requirements..."
    pip install -r "$SCRIPT_DIR/requirements.txt"

else
    # Activate existing virtual environment
    source "$VENV_DIR/bin/activate"
fi

# Run the program
echo "Starting OBD Diagnostic Tool..."
python "$SCRIPT_DIR/src/main.py" 