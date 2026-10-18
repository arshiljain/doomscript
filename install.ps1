# DoomScript One-Line Installer for Windows PowerShell
$ErrorActionPreference = "Stop"

Write-Host "[*] Downloading and launching DoomScript installer..." -ForegroundColor Cyan
$installScript = Invoke-RestMethod -Uri "https://raw.githubusercontent.com/arshiljain/doomscript/main/install.py"
python -c "$installScript"
