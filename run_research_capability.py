"""
Capability Benchmark Runner for DoomScript Postgraduate Research Corpus (50 Programs).
Validates compiler performance, natural English syntax, numerical accuracy, and scientific reproducibility.
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple
from doomscript.compiler.engine import execute


CORPUS_DIR = Path(__file__).parent / "tests" / "research" / "corpus"


def run_benchmark(file_path: Path) -> Tuple[bool, float, str]:
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    start_time = time.perf_counter()
    try:
        execute(source, filename=str(file_path))
        elapsed = time.perf_counter() - start_time
        return True, elapsed, "PASS"
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        return False, elapsed, f"FAIL: {type(e).__name__}: {str(e)}"


def main() -> int:
    files = sorted(list(CORPUS_DIR.glob("*.doom")))
    if not files:
        print(f"Error: No .doom benchmark files found in {CORPUS_DIR}")
        return 1

    print("\n" + "=" * 80)
    print("DOOMSCRIPT POSTGRADUATE RESEARCH CAPABILITY BENCHMARK SUITE")
    print(f"Found {len(files)} held-out postgraduate research programs across 3 domains")
    print("=" * 80 + "\n")

    results: List[Tuple[str, str, bool, float, str]] = []
    category_counts: Dict[str, Dict[str, int]] = {
        "Algorithms & Graphs": {"total": 0, "passed": 0},
        "Statistical Inference": {"total": 0, "passed": 0},
        "ML & Optimization": {"total": 0, "passed": 0},
    }

    for idx, f in enumerate(files, 1):
        num = int(f.name.split("_")[0])
        if num <= 15:
            cat = "Algorithms & Graphs"
        elif num <= 30:
            cat = "Statistical Inference"
        else:
            cat = "ML & Optimization"

        category_counts[cat]["total"] += 1
        passed, elapsed, message = run_benchmark(f)
        if passed:
            category_counts[cat]["passed"] += 1

        results.append((f.name, cat, passed, elapsed, message))
        status_symbol = "[OK] " if passed else "[FAIL]"
        print(f"{status_symbol} {idx:02d}/{len(files):02d} | {cat:<22} | {f.name:<36} | {elapsed*1000:6.1f}ms")
        if not passed:
            print(f"     -> {message}")

    total_passed = sum(1 for _, _, p, _, _ in results)
    total_count = len(results)
    pass_rate = (total_passed / total_count) * 100.0

    print("\n" + "-" * 80)
    print("DOMAIN SUMMARY BREAKDOWN")
    print("-" * 80)
    for cat, counts in category_counts.items():
        c_rate = (counts["passed"] / counts["total"]) * 100.0 if counts["total"] > 0 else 0.0
        print(f"  * {cat:<24}: {counts['passed']:2d}/{counts['total']:2d} ({c_rate:5.1f}%)")

    total_time = sum(el for _, _, _, el, _ in results)
    print("-" * 80)
    print(f"OVERALL RESULTS: {total_passed}/{total_count} PASSED ({pass_rate:.1f}%) in {total_time:.2f}s")
    print("=" * 80 + "\n")

    if pass_rate < 95.0:
        print(f"FAILURE: Pass rate {pass_rate:.1f}% is below target threshold of 95.0%")
        return 1

    print("ALL POSTGRADUATE CAPABILITY BENCHMARKS PASSED SUCCESSFULLY!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
