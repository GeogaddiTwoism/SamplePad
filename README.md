# Sample Pad

A 12-key sample pad with waveform display and sample chopping.

```
[ E ] [ R ] [ T ] [ Y ]
[ D ] [ F ] [ G ] [ H ]
[ C ] [ V ] [ B ] [ N ]
```

- Press a key or click a pad to play its sample
- Select a pad and press Enter to load an audio file
- Adjust the START and END sliders to chop the sample
- Retriggering the same pad restarts it; different pads layer

## Requirements

- Python 3.10+
- System libraries: SDL2, libsndfile, Tk
- Python packages: `numpy`, `soundfile`, `pygame-ce`, `matplotlib`

## Install

### Windows

```
install_windows.bat
```
Or double-click `install_windows.bat`. Requires Python 3.10+ installed and on PATH.

### macOS

```bash
chmod +x install_macos.sh
./install_macos.sh
```
Installs Homebrew if not present, then system deps and Python packages.

### Debian / Ubuntu

```bash
chmod +x install_debian.sh
./install_debian.sh
```

### Fedora

```bash
chmod +x install_fedora.sh
./install_fedora.sh
```

### Arch Linux

```bash
chmod +x install_arch.sh
./install_arch.sh
```

## Run

```bash
python sample_pad.py
```
On Linux/macOS use `python3` if `python` points to Python 2.

## Supported Audio Formats

WAV, MP3, OGG, FLAC, AIFF
