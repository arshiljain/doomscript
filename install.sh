#!/usr/bin/env bash
# DoomScript One-Line Shell Installer for macOS & Linux
set -e

echo "[*] Downloading and running DoomScript installer..."
python3 -c "$(curl -fsSL https://raw.githubusercontent.com/arshiljain/doomscript/main/install.py)"
