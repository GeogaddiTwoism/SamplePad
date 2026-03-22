#!/bin/bash
echo "=== Sample Pad - Debian/Ubuntu Install ==="
echo

# Install system dependencies
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-tk libsndfile1 libsdl2-2.0-0 \
    libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-ttf-2.0-0 portaudio19-dev

# Install Python packages
echo "Installing Python dependencies..."
pip3 install --user numpy soundfile pygame-ce matplotlib

echo
echo "Installation complete! Run the program with:"
echo "  python3 sample_pad.py"
