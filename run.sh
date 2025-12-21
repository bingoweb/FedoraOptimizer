#!/bin/bash

# Ensure we are in the script directory
cd "$(dirname "$0")"

# Check if setup has been run
if [ ! -f "venv/bin/python" ]; then
    echo "Virtual environment not found. Running setup.sh first..."
    chmod +x setup.sh
    ./setup.sh
fi

# Run the app using the VENV python, but with SUDO
# We use 'sudo' to run the specific python binary from the venv.
# This gives root access while keeping access to the installed packages in the venv.
sudo ./venv/bin/python src/ui/tui_app.py
