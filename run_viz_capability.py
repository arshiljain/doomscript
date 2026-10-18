#!/usr/bin/env python3
"""
DoomScript Grammar-of-Graphics Visualization Capability Benchmark Runner.

Executes all 10 visual corpus programs across Level 1 (Explore),
Level 2 (Describe), and Level 3 (Compose), validating execution,
assertion correctness, and Lets-Plot rendering.
"""

import sys
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table

from doomscript.compiler.engine import execute

console = Console()
CORPUS_DIR = Path(__file__).parent / "tests" / "viz" / "corpus"


def main():
    console.print("\n[bold magenta]DOOMSCRIPT GRAMMAR-OF-GRAPHICS VISUALIZATION BENCHMARK SUITE[/bold magenta]")
    files = sorted(list(CORPUS_DIR.glob("*.doom")))
    console.print(f"Discovered [cyan]{len(files)}[/cyan] visual benchmark programs\n" + "=" * 80 + "\n")

    passed = 0
    failed = 0
    results = []

    for idx, f in enumerate(files, 1):
        source = f.read_text(encoding="utf-8")
        scope = {}
        t0 = time.perf_counter()
        try:
            execute(source, scope, filename=str(f))
            elapsed = (time.perf_counter() - t0) * 1000.0
            passed += 1
            results.append((idx, f.name, "PASS", elapsed, None))
            console.print(f"[green][OK][/green]  {idx:02d}/{len(files):02d} | {f.name:<38} | {elapsed:7.1f}ms")
        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000.0
            failed += 1
            results.append((idx, f.name, "FAIL", elapsed, str(e)))
            console.print(f"[red][FAIL][/red] {idx:02d}/{len(files):02d} | {f.name:<38} | {elapsed:7.1f}ms -> {e}")

    total = len(files)
    pct = (passed / total * 100.0) if total > 0 else 0.0

    console.print("\n" + "=" * 80)
    console.print(f"[bold]OVERALL VISUAL RESULTS: {passed}/{total} PASSED ({pct:.1f}%)[/bold]")
    console.print("=" * 80 + "\n")

    if failed == 0 and pct >= 95.0:
        console.print("[bold green]ALL VISUALIZATION CAPABILITY BENCHMARKS PASSED SUCCESSFULLY![/bold green]\n")
        return 0
    else:
        console.print(f"[bold red]BENCHMARK SUITE FAILED: {failed} programs failed.[/bold red]\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
