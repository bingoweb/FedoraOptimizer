#!/bin/bash
set -e

echo "Setting up Fedora Admin Suite environment..."

# 1. Create Virtual Environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# 2. Install dependencies into venv
echo "Installing dependencies..."
# Upgrade pip inside venv
./venv/bin/pip install --upgrade pip
# Install requirements
./venv/bin/pip install -r requirements.txt

echo "Setup Complete!"
echo "You can now run the app with: sudo ./run.sh"
