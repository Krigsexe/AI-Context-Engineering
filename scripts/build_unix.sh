#!/bin/bash
# Build script for Linux/Mac

set -e

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run PyInstaller
pyinstaller odin.spec

echo "Build complete. Binary located in dist/odin."

