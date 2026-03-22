#!/bin/bash
echo "=== Sample Pad - Fedora Install ==="
echo

# Install system dependencies
echo "Installing system dependencies..."
sudo dnf install -y python3 python3-pip python3-tkinter libsndfile SDL2 \
    SDL2_mixer SDL2_image SDL2_ttf portaudio-devel

# Install Python packages
echo "Installing Python dependencies..."
pip3 install --user numpy soundfile pygame-ce matplotlib

echo
echo "Installation complete! Run the program with:"
echo "  python3 sample_pad.py"
