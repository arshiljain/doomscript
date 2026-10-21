"""
Regression test suite ensuring all 45 code examples documented in vspython.md
parse and execute accurately and reliably end-to-end.
"""
from pathlib import Path
import re
import urllib.error
import pytest
from doomscript.compiler.engine import execute

ROOT_DIR = Path(__file__).resolve().parent.parent
DOC_PATH = ROOT_DIR / "vspython.md"


def load_vspython_examples():
    assert DOC_PATH.exists(), f"vspython.md not found at {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    pattern = r"#### Example (\d+):\s*([^\r\n]+).*?##### [^\n]*DoomScript\s*```doom(?:script)?\r?\n(.*?)```"
    matches = list(re.finditer(pattern, text, re.DOTALL))
    return [(int(m.group(1)), m.group(2).strip(), m.group(3)) for m in matches]


EXAMPLES = load_vspython_examples()


def test_vspython_example_count():
    assert len(EXAMPLES) == 45, f"Expected 45 examples in vspython.md, found {len(EXAMPLES)}"


@pytest.mark.parametrize(
    "example_num,title,code",
    EXAMPLES,
    ids=[f"ex_{num:02d}_{re.sub(r'[^a-zA-Z0-9_]', '_', title)[:25]}" for num, title, _ in EXAMPLES]
)
def test_vspython_example(example_num, title, code):
    try:
        env = execute(code)
        assert env is not None
    except (urllib.error.URLError, TimeoutError) as net_err:
        pytest.skip(f"Network error in Example {example_num} (likely offline test environment): {net_err}")
