@echo off
echo === Sample Pad - Windows Install ===
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install --user numpy soundfile pygame-ce matplotlib

echo.
echo Installation complete! Run the program with:
echo   python sample_pad.py
echo.
pause
