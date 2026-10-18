#!/usr/bin/env python3
"""
DoomScript Official One-Line Installer
Supports Windows, macOS, and Linux.
Usage:
  curl -sSL https://raw.githubusercontent.com/arshiljain/doomscript/main/install.py | python3
"""

import sys
import subprocess
import shutil
from pathlib import Path

MIN_PYTHON = (3, 8)


def main():
    print("================================================================")
    print("           DoomScript Official One-Line Installer               ")
    print("   The English-first programming language for mortals & data    ")
    print("================================================================\n")

    # 1. Verify Python version
    if sys.version_info < MIN_PYTHON:
        print(f"[!] Error: DoomScript requires Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+. Current: {sys.version}")
        sys.exit(1)

    print(f"[*] Detected Python {sys.version.split()[0]} on {sys.platform}.")

    # 2. Check installation source
    # If running from inside a cloned repo directory, install local; otherwise from GitHub
    here = Path(__file__).parent.resolve()
    repo_url = "git+https://github.com/arshiljain/doomscript.git"

    if (here / "pyproject.toml").exists() and (here / "src" / "doomscript").exists():
        target = str(here)
        print(f"[*] Installing DoomScript from local repository ({target})...")
    else:
        target = repo_url
        print(f"[*] Installing DoomScript from remote ({repo_url})...")

    # 3. Run pip install
    cmd = [sys.executable, "-m", "pip", "install", target]
    try:
        res = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Installation failed:\n{e.stderr or e.stdout}")
        sys.exit(1)

    # 4. Verify CLI executable
    doom_bin = shutil.which("doom")
    print("\n[+] DoomScript installed successfully!")
    if doom_bin:
        print(f"[*] CLI binary: {doom_bin}")
    else:
        print(f"[*] CLI available via: {sys.executable} -m doomscript.cli")

    # 5. Quick self-test
    test_code = "say 'DoomScript is ready to clean your spreadsheets.'"
    try:
        test_res = subprocess.run(
            [sys.executable, "-c", f"from doomscript import execute; execute({test_code!r})"],
            capture_output=True,
            text=True
        )
        if test_res.returncode == 0:
            print(f"[+] Self-test passed: {test_res.stdout.strip()}")
    except Exception:
        pass

    print("\n----------------------------------------------------------------")
    print("Next steps:")
    print("  1. Launch interactive playground : doom playground")
    print("  2. Run a script                  : doom run my_script.doom")
    print("  3. Start interactive REPL        : doom repl")
    print("----------------------------------------------------------------\n")


if __name__ == "__main__":
    main()
