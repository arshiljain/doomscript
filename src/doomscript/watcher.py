"""
DoomScript File Watcher & Auto-Reload Daemon (Phase 18)
Monitors files or directories and re-runs `doom run` or `doom test` upon modification.
"""

import time
import subprocess
import sys
from pathlib import Path
from typing import Optional, Callable
from rich.console import Console

console = Console()

def get_file_mtimes(path: Path) -> dict:
    mtimes = {}
    if path.is_file():
        mtimes[path] = path.stat().st_mtime
    else:
        for p in path.rglob("*.doom"):
            try:
                mtimes[p] = p.stat().st_mtime
            except OSError:
                pass
    return mtimes

def watch_path(target: Path, action: str = "run", max_ticks: Optional[int] = None):
    """
    Watches target file or directory.
    When modified, executes the selected action (run or test).
    max_ticks allows controlled execution during automated testing.
    """
    console.print(f"[bold cyan]DoomScript Watcher active[/bold cyan]: monitoring '{target}' (action={action})")
    last_mtimes = get_file_mtimes(target)
    ticks = 0

    while True:
        time.sleep(0.5)
        ticks += 1
        if max_ticks is not None and ticks >= max_ticks:
            break

        current_mtimes = get_file_mtimes(target)
        changed = False
        for p, mt in current_mtimes.items():
            if p not in last_mtimes or mt > last_mtimes[p]:
                changed = True
                console.print(f"\n[bold yellow]Change detected in {p.name}[/bold yellow] - Re-executing...")
                break

        if changed:
            last_mtimes = current_mtimes
            cmd = [sys.executable, "-m", "doomscript.cli", action, str(target)]
            try:
                subprocess.run(cmd)
            except Exception as e:
                console.print(f"[bold red]Execution error:[/bold red] {e}")
