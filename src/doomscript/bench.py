"""
DoomScript Performance Benchmarking & Profiler (Phase 24)
Executes a .doom file multiple times, collecting timing, throughput, and memory stats.
"""

import time
import tracemalloc
from pathlib import Path
from typing import Dict, Any
from rich.console import Console
from rich.table import Table

from doomscript.compiler.engine import execute

console = Console()

def benchmark_script(file_path: Path, iterations: int = 10) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    console.print(f"[bold cyan]Benchmarking '{file_path.name}'[/bold cyan] ({iterations} iterations)...")
    
    durations = []
    tracemalloc.start()
    
    for _ in range(iterations):
        t0 = time.perf_counter()
        execute(source)
        t1 = time.perf_counter()
        durations.append(t1 - t0)
        
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    total_time = sum(durations)
    avg_time = total_time / iterations
    min_time = min(durations)
    max_time = max(durations)
    ops_per_sec = iterations / total_time if total_time > 0 else 0

    table = Table(title=f"DoomScript Benchmark: {file_path.name}")
    table.add_column("Metric", style="bold cyan")
    table.add_column("Value", style="green")

    table.add_row("Iterations", str(iterations))
    table.add_row("Total Time", f"{total_time:.4f} s")
    table.add_row("Avg Latency", f"{avg_time * 1000:.3f} ms")
    table.add_row("Min Latency", f"{min_time * 1000:.3f} ms")
    table.add_row("Max Latency", f"{max_time * 1000:.3f} ms")
    table.add_row("Throughput", f"{ops_per_sec:,.1f} runs/sec")
    table.add_row("Peak Memory", f"{peak_mem / 1024:.2f} KB")

    console.print(table)

    return {
        "file": str(file_path),
        "iterations": iterations,
        "total_time": total_time,
        "avg_time": avg_time,
        "ops_per_sec": ops_per_sec,
        "peak_mem_kb": peak_mem / 1024
    }
