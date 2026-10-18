"""
Pytest integration for the 50-program postgraduate research benchmark corpus.
"""

from pathlib import Path
import pytest
from doomscript.compiler.engine import execute


CORPUS_DIR = Path(__file__).parent / "corpus"
BENCHMARK_FILES = sorted(list(CORPUS_DIR.glob("*.doom")))


@pytest.mark.parametrize("file_path", BENCHMARK_FILES, ids=lambda p: p.name)
def test_research_benchmark_program(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    # Must compile and execute without raising an unhandled exception or failed assertion
    execute(source, filename=str(file_path))
