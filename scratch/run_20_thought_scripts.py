"""
Benchmark Runner for the 20 Thought-to-Code End-to-End DoomScript Programs.
Measures execution time, catches syntax/runtime friction points, and outputs full report.
"""

import sys
import time
import pathlib
import io
import contextlib

sys.path.insert(0, r"C:\Users\kanha\.gemini\antigravity\scratch\doomscript\src")
from doomscript.compiler.engine import execute

SCRIPTS_DIR = pathlib.Path(r"C:\Users\kanha\.gemini\antigravity\scratch\doomscript\examples\thought_scripts")

def run_all_benchmarks():
    scripts = sorted(list(SCRIPTS_DIR.glob("*.doom")))
    print(f"Discovered {len(scripts)} benchmark scripts in {SCRIPTS_DIR}\n")
    print(f"{'#':<3} | {'Script Name':<42} | {'Status':<8} | {'Time (ms)':<10} | {'Notes'}")
    print("-" * 90)

    results = []
    passed_count = 0

    for idx, script_path in enumerate(scripts, 1):
        source = script_path.read_text(encoding="utf-8")
        out_buf = io.StringIO()
        start = time.perf_counter()
        status = "PASS"
        err_msg = ""
        try:
            with contextlib.redirect_stdout(out_buf):
                env = execute(source, filename=script_path.name)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            passed_count += 1
            note = f"{len(env)} symbols"
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            status = "FAIL"
            err_msg = str(e)
            note = f"Error: {e.__class__.__name__}: {str(e)[:45]}"

        print(f"{idx:<3} | {script_path.name:<42} | {status:<8} | {elapsed_ms:>8.1f}ms | {note}")
        results.append({
            "index": idx,
            "name": script_path.name,
            "status": status,
            "time_ms": elapsed_ms,
            "output": out_buf.getvalue(),
            "error": err_msg
        })

    print("-" * 90)
    print(f"\nFinal Summary: {passed_count}/{len(scripts)} scripts passed successfully ({passed_count/max(1, len(scripts))*100:.1f}%)\n")

    # If any failed, print full error trace
    failures = [r for r in results if r["status"] == "FAIL"]
    if failures:
        print("=== FAILURE DIAGNOSTICS ===")
        for f in failures:
            print(f"\n[{f['index']}] {f['name']}:")
            print(f"Error: {f['error']}")

    return results

if __name__ == "__main__":
    run_all_benchmarks()
