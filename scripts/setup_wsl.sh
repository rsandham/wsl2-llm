#!/bin/bash

# Check if WSL2 is enabled
if [ -z "$(wsl -l -v | grep -i 'wsl2')" ]; then
    echo "WSL2 is not enabled. Please enable WSL2 first."
    exit 1
fi

# Update package list
sudo apt update

# Install required packages
sudo apt install -y \
    python3-pip \
    python3-venv \
    git \
    nvidia-cuda-toolkit

# Create Python virtual environment
python3 -m venv ../venv
source ../venv/bin/activate

# Install Python dependencies
pip install -r ../requirements.txt

# Create models directory if it doesn't exist
mkdir -p ../models

echo "WSL2 environment setup complete!"