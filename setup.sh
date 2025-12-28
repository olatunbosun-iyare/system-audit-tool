#!/bin/bash
# Remove valid environment if it exists
rm -rf venv

# Create new virtual environment
python3 -m venv venv

# Upgrade pip
./venv/bin/pip install --upgrade pip

# Install dependencies
./venv/bin/pip install -r requirements.txt

echo "Setup complete! Run the script with: ./venv/bin/python system_audit.py"
