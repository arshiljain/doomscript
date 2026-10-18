"""
DoomScript Coursework Capability Benchmark Runner
Executes 40 undergraduate and postgraduate CS & Data Science coursework benchmarks
across 4 categories: CS1, CS2, Data Science, and ML/Math.
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Ensure src is on sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR / "src"
if SRC_DIR.exists() and str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from doomscript.compiler.engine import compile_to_ast, execute, export_to_python

TEMP_CSV_FILES = [
    "students.csv",
    "employees.csv",
    "leaderboard.csv",
    "raw_pipeline.csv",
    "pipeline_output.csv"
]


def cleanup_temp_files():
    for f in TEMP_CSV_FILES:
        p = Path(f)
        if p.exists():
            try:
                p.unlink()
            except OSError:
                pass


def run_all_benchmarks(category_filter: str = None) -> Dict[str, Any]:
    capability_dir = SCRIPT_DIR / "tests" / "capability"
    categories = ["cs1", "cs2", "datascience", "ml_math"]
    if category_filter:
        categories = [c for c in categories if c == category_filter]

    results_by_cat = {}
    total_count = 0
    passed_count = 0

    for cat in categories:
        cat_dir = capability_dir / cat
        files = sorted(list(cat_dir.glob("*.doom")))
        cat_results = []

        for f in files:
            total_count += 1
            cleanup_temp_files()
            with open(f, "r", encoding="utf-8") as fp:
                source = fp.read()

            status = "PASS"
            err_msg = ""

            # 1. Execute directly in DoomScript engine
            try:
                execute(source)
            except Exception as e:
                status = "FAIL_EXEC"
                err_msg = f"Execution error: {type(e).__name__}: {e}"

            # 2. Test export_to_python and verify valid Python syntax
            if status == "PASS":
                try:
                    py_code = export_to_python(source)
                    # Verify python code compiles cleanly
                    compile(py_code, filename=f.stem + ".py", mode="exec")
                except Exception as e:
                    status = "FAIL_EXPORT"
                    err_msg = f"Export error: {type(e).__name__}: {e}"

            cleanup_temp_files()

            if status == "PASS":
                passed_count += 1

            cat_results.append({
                "file": f.name,
                "status": status,
                "error": err_msg
            })

        results_by_cat[cat] = cat_results

    cleanup_temp_files()

    pass_rate = (passed_count / total_count * 100.0) if total_count > 0 else 0.0
    return {
        "total": total_count,
        "passed": passed_count,
        "pass_rate": pass_rate,
        "by_category": results_by_cat
    }


def main():
    parser = argparse.ArgumentParser(description="DoomScript Capability Benchmark Runner")
    parser.add_argument("--category", choices=["cs1", "cs2", "datascience", "ml_math"], help="Run only specific category")
    parser.add_argument("--fail-under", type=float, default=95.0, help="Fail if pass rate is under percentage")
    args = parser.parse_args()

    print("Running DoomScript 40-Program Coursework Capability Benchmarks...\n")
    results = run_all_benchmarks(category_filter=args.category)

    for cat, tests in results["by_category"].items():
        cat_pass = sum(1 for t in tests if t["status"] == "PASS")
        print(f"=== Category: {cat.upper()} ({cat_pass}/{len(tests)}) ===")
        for t in tests:
            mark = "PASS" if t["status"] == "PASS" else "FAIL"
            print(f"  [{mark}] {t['file']}")
            if t["status"] != "PASS":
                print(f"         {t['error']}")
        print()

    print("=" * 60)
    print(f"Capability Benchmark Results: {results['passed']}/{results['total']} passed ({results['pass_rate']:.1f}%)")
    print("=" * 60)

    if results["pass_rate"] < args.fail_under:
        print(f"\nERROR: Pass rate {results['pass_rate']:.1f}% is below required threshold of {args.fail_under}%.")
        sys.exit(1)
    else:
        print(f"\nSUCCESS: Coursework capability target met ({results['pass_rate']:.1f}% >= {args.fail_under}%).")
        sys.exit(0)


if __name__ == "__main__":
    main()
