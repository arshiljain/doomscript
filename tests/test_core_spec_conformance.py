"""
Conformance test suite for docs/CORE_SPEC.md
Extracts and executes every code example in CORE_SPEC.md:
- Multi-line fenced doomscript code blocks
- Inline '**Example**:' snippets (e.g. separated by ' / ')
Verifies that all 30 guaranteed Core forms compile and execute cleanly.
"""

import io
import re
import sys
import textwrap
from pathlib import Path
import pytest
from doomscript.compiler.engine import execute
from doomscript.runtime import Record

CORE_SPEC_PATH = Path(__file__).parent.parent / "docs" / "CORE_SPEC.md"


def get_default_test_env():
    """Provides mock variables for all examples in the Core Spec."""
    return {
        "total": 500,
        "status": "active",
        "score": 95,
        "amount": 150,
        "balance": 200,
        "count": 5,
        "_var_count": 5,
        "_var_sum": 100,
        "_var_list": [1, 2, 3],
        "_var_first": 1,
        "age": 25,
        "role": "admin",
        "is_admin": True,
        "is_banned": False,
        "is_ready": True,
        "customers": ["Alice", "Bob"],
        "price": 100,
        "rate": 0.05,
        "tasks": ["eat", "sleep"],
        "scores": [90, 80, 95],
        "items": [1, 2, 3],
        "raw_ids": [101, 102, 101, 103],
        "test_scores": [88, 92, 79],
        "orders": [
            Record(status="paid", amount=150),
            Record(status="pending", amount=50),
        ],
        "paid_orders": [
            Record(status="paid", amount=150),
        ],
        "user": Record(name="Alice", role="admin"),
        "raw_email": "   alice@example.com   ",
        "book_name": "the doom of valyria",
        "row": Record(amount=100),
        "rows": [{"name": "item1", "price": 10}],
        "clean_rows": [{"name": "item1", "price": 10}],
        "payload": '{"total": 250}',
        "username": "tester",
    }


def extract_fenced_blocks(markdown_text: str):
    """Extracts all ```doomscript ... ``` blocks from markdown."""
    clean_text = markdown_text.replace("\r\n", "\n")
    pattern = re.compile(r"[ \t]*```(?:doomscript|doom)\s*\n(.*?)\n[ \t]*```", re.DOTALL)
    blocks = []
    for match in pattern.finditer(clean_text):
        blocks.append(textwrap.dedent(match.group(1)).strip())
    return blocks


def extract_inline_examples(markdown_text: str):
    """Extracts inline examples following '**Example**:'."""
    clean_text = markdown_text.replace("\r\n", "\n")
    pattern = re.compile(r"-\s*\*\*Example\*\*:\s*([^\n`]+.*)$", re.MULTILINE)
    examples = []
    for match in pattern.finditer(clean_text):
        line = match.group(1).strip()
        if not line or line.startswith("```"):
            continue
        parts = [p.strip() for p in line.split(" / ")]
        for part in parts:
            p = part.strip().strip("`").strip()
            if p and not p.startswith("```"):
                examples.append(p)
    return examples


def test_core_spec_fenced_blocks(tmp_path, monkeypatch):
    """Verify all fenced doomscript blocks in CORE_SPEC.md parse and execute cleanly."""
    content = CORE_SPEC_PATH.read_text(encoding="utf-8")
    blocks = extract_fenced_blocks(content)
    assert len(blocks) >= 15, f"Expected at least 15 fenced code blocks, found {len(blocks)}"

    monkeypatch.chdir(tmp_path)
    (tmp_path / "data.csv").write_text("name,price\nitem1,10\n", encoding="utf-8")
    (tmp_path / "audit.log").write_text("entry\n", encoding="utf-8")
    monkeypatch.setattr(sys, "stdin", io.StringIO("Alice\n" * 100))

    for idx, block in enumerate(blocks, start=1):
        env = get_default_test_env()
        try:
            execute(block, custom_globals=env)
        except Exception as e:
            pytest.fail(f"Failed to execute fenced block #{idx} in CORE_SPEC.md:\n{block}\nError: {e}")


def test_core_spec_inline_examples(monkeypatch):
    """Verify all inline examples in CORE_SPEC.md parse and execute cleanly."""
    content = CORE_SPEC_PATH.read_text(encoding="utf-8")
    inline_examples = extract_inline_examples(content)
    assert len(inline_examples) >= 15, f"Expected at least 15 inline examples, found {len(inline_examples)}"

    monkeypatch.setattr(sys, "stdin", io.StringIO("Alice\n" * 100))

    for idx, ex in enumerate(inline_examples, start=1):
        env = get_default_test_env()
        snippet = ex
        if snippet.startswith("if ") and snippet.endswith(":"):
            snippet = f"{snippet}\n    say 'ok'"

        try:
            execute(snippet, custom_globals=env)
        except Exception as e:
            pytest.fail(f"Failed to execute inline example #{idx} ('{ex}') in CORE_SPEC.md:\nError: {e}")


def test_form_20_unique_items_into_target():
    """Direct regression test for Core Spec Form #20: 'unique items of raw_ids into clean_ids'."""
    code = """
raw_ids = [1, 2, 2, 3, 1]
unique items of raw_ids into clean_ids
"""
    env = execute(code)
    assert env["clean_ids"] == [1, 2, 3]
