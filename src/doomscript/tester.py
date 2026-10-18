"""
DoomScript Native Test Runner (Phase 10)
Discovers and executes plain-English tests written with `test "..."` and `expect ... to ...`.
"""

import time
import re
import textwrap
from pathlib import Path
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from doomscript.compiler.engine import compile_to_ast, execute
from doomscript.exceptions import DoomError

console = Console()


def extract_test_blocks(source: str) -> List[Dict[str, Any]]:
    """
    Extracts top-level `test "name":` blocks from a .doom file.
    If no explicit `test` blocks are present, treats the entire file as one test.
    """
    source = textwrap.dedent(source)
    lines = source.splitlines()
    blocks = []
    current_test_name = None
    current_lines = []

    for idx, line in enumerate(lines, start=1):
        test_m = re.match(r"^test\s+(.+?):?$", line.strip(), re.IGNORECASE)
        if test_m and (len(line) - len(line.lstrip())) == 0:
            if current_test_name is not None and current_lines:
                blocks.append({
                    "name": current_test_name,
                    "code": textwrap.dedent("\n".join(current_lines)),
                    "line": idx - len(current_lines)
                })
            current_test_name = test_m.group(1).strip().strip('"\'')
            current_lines = []
            continue

        if current_test_name is not None:
            current_lines.append(line)

    if current_test_name is not None and current_lines:
        blocks.append({
            "name": current_test_name,
            "code": textwrap.dedent("\n".join(current_lines)),
            "line": len(lines) - len(current_lines) + 1
        })

    return blocks


def run_doom_tests(target_path: Optional[Path] = None) -> bool:
    """
    Discovers and executes DoomScript tests.
    Returns True if all tests passed, False otherwise.
    """
    if target_path is None:
        target_path = Path.cwd()

    doom_files = []
    if target_path.is_file():
        if target_path.suffix == ".doom":
            doom_files.append(target_path)
    else:
        tests_dir = target_path / "tests"
        if tests_dir.exists() and tests_dir.is_dir():
            doom_files.extend(sorted(tests_dir.glob("*.doom")))
        doom_files.extend(sorted(target_path.glob("test_*.doom")))

    if not doom_files:
        console.print(f"[yellow]No DoomScript test files (*.doom) found in '{target_path}'.[/yellow]")
        return True

    console.print(f"[bold cyan]DoomScript Test Runner[/bold cyan] (Found {len(doom_files)} test file(s))\n")

    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    start_total_time = time.perf_counter()

    for file_path in doom_files:
        console.print(f"[bold]{file_path.name}[/bold]")
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        test_blocks = extract_test_blocks(source)
        if not test_blocks:
            # Entire file is a single test
            test_blocks = [{
                "name": file_path.stem,
                "code": source,
                "line": 1
            }]

        for tb in test_blocks:
            total_tests += 1
            t_name = tb["name"]
            t_code = tb["code"]
            t_start = time.perf_counter()

            try:
                execute(t_code)
                duration = time.perf_counter() - t_start
                passed_tests += 1
                console.print(f"  [bold green]PASS[/bold green] test \"{t_name}\" [dim]({duration:.3f}s)[/dim]")
            except AssertionError as ae:
                duration = time.perf_counter() - t_start
                failed_tests += 1
                console.print(f"  [bold red]FAIL[/bold red] test \"{t_name}\" [dim]({duration:.3f}s)[/dim]")
                console.print(f"    [bold red]Assertion Failed:[/bold red] {ae}")
            except DoomError as de:
                duration = time.perf_counter() - t_start
                failed_tests += 1
                console.print(f"  [bold red]FAIL[/bold red] test \"{t_name}\" [dim]({duration:.3f}s)[/dim]")
                console.print(f"    [bold red]DoomScript Error:[/bold red] {de.message}")
            except Exception as exc:
                duration = time.perf_counter() - t_start
                failed_tests += 1
                console.print(f"  [bold red]FAIL[/bold red] test \"{t_name}\" [dim]({duration:.3f}s)[/dim]")
                console.print(f"    [bold red]Unexpected Error:[/bold red] {exc}")

        console.print()

    total_time = time.perf_counter() - start_total_time

    if failed_tests == 0:
        console.print(f"[bold green]All {passed_tests} test(s) passed in {total_time:.3f}s![/bold green]")
        return True
    else:
        console.print(f"[bold red]Test Summary: {passed_tests} passed, {failed_tests} failed out of {total_tests} in {total_time:.3f}s.[/bold red]")
        return False
