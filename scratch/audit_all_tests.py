import os
import sys
import subprocess
import glob
import time
from typing import Dict, Any, List

def run_all_test_files():
    test_files = sorted(glob.glob("tests/test_*.py"))
    print(f"Discovered {len(test_files)} test files in tests/ directory.")
    
    results = []
    passed_files = 0
    failed_files = 0
    timeout_files = 0
    
    total_start = time.time()
    
    for idx, test_file in enumerate(test_files, 1):
        rel_path = os.path.relpath(test_file)
        start_time = time.time()
        print(f"[{idx:02d}/{len(test_files):02d}] Running {rel_path}...", end=" ", flush=True)
        
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", rel_path, "-q", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60
            )
            elapsed = time.time() - start_time
            if proc.returncode == 0:
                passed_files += 1
                print(f"PASSED ({elapsed:.2f}s)")
                results.append({
                    "file": rel_path,
                    "status": "PASS",
                    "elapsed": elapsed,
                    "output": proc.stdout.strip()
                })
            else:
                failed_files += 1
                print(f"FAILED (code {proc.returncode}, {elapsed:.2f}s)")
                print("--- STDOUT ---")
                print(proc.stdout[:1500])
                if proc.stderr:
                    print("--- STDERR ---")
                    print(proc.stderr[:1000])
                print("--------------")
                results.append({
                    "file": rel_path,
                    "status": "FAIL",
                    "returncode": proc.returncode,
                    "elapsed": elapsed,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr
                })
        except subprocess.TimeoutExpired as e:
            elapsed = time.time() - start_time
            timeout_files += 1
            print(f"TIMEOUT (>25s)")
            results.append({
                "file": rel_path,
                "status": "TIMEOUT",
                "elapsed": elapsed,
            })
            
    total_elapsed = time.time() - total_start
    print("\n" + "="*70)
    print("TEST SUITE AUDIT SUMMARY:")
    print(f"Total Test Files: {len(test_files)}")
    print(f"Passed Files    : {passed_files}")
    print(f"Failed Files    : {failed_files}")
    print(f"Timeout Files   : {timeout_files}")
    print(f"Total Wall Time : {total_elapsed:.2f}s")
    print("="*70)
    
    if failed_files > 0 or timeout_files > 0:
        print("\nPROBLEMATIC FILES:")
        for r in results:
            if r["status"] != "PASS":
                print(f" - {r['file']}: {r['status']} ({r['elapsed']:.2f}s)")
                
    return results

if __name__ == "__main__":
    run_all_test_files()
