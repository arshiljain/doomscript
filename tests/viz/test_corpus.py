"""Parameterized pytest suite executing all 10 Visual Corpus programs."""

from pathlib import Path
import pytest
from doomscript.compiler.engine import execute

CORPUS_DIR = Path(__file__).parent / "corpus"
CORPUS_FILES = sorted(list(CORPUS_DIR.glob("*.doom")))


@pytest.mark.parametrize("file_path", CORPUS_FILES, ids=lambda p: p.name)
def test_corpus_program(file_path: Path):
    source = file_path.read_text(encoding="utf-8")
    scope = {}
    execute(source, scope, filename=str(file_path))
