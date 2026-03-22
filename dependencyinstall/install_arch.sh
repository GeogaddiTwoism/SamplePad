#!/bin/bash
echo "=== Sample Pad - Arch Linux Install ==="
echo

# Install system dependencies
echo "Installing system dependencies..."
sudo pacman -Syu --noconfirm python python-pip tk libsndfile sdl2 sdl2_mixer \
    sdl2_image sdl2_ttf portaudio

# Install Python packages
echo "Installing Python dependencies..."
pip3 install --user numpy soundfile pygame-ce matplotlib

echo
echo "Installation complete! Run the program with:"
echo "  python3 sample_pad.py"
