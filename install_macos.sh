#!/bin/bash
echo "=== Sample Pad - macOS Install ==="
echo

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install system dependencies
echo "Installing system dependencies..."
brew install python3 libsndfile portaudio sdl2 sdl2_mixer sdl2_image sdl2_ttf

# Install Python packages
echo "Installing Python dependencies..."
pip3 install --user numpy soundfile pygame-ce matplotlib

echo
echo "Installation complete! Run the program with:"
echo "  python3 sample_pad.py"
