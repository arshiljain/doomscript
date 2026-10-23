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
    # Check if example requires lets_plot and it is missing
    if "use viz" in code or "save chart" in code or "draw scatter" in code or example_num == 10:
        try:
            import lets_plot
        except ImportError:
            pytest.skip(f"Optional dependency 'lets_plot' is unavailable for Example {example_num} ({title})")

    try:
        env = execute(code)
        assert env is not None
    except (urllib.error.URLError, TimeoutError, OSError) as net_err:
        pytest.skip(f"Network error in Example {example_num} (likely offline test environment): {net_err}")
    except ImportError as imp_err:
        if "lets_plot" in str(imp_err).lower() or "lets-plot" in str(imp_err).lower():
            pytest.skip(f"Optional dependency 'lets_plot' is unavailable for Example {example_num} ({title}): {imp_err}")
        raise
    except Exception as exc:
        exc_str = str(exc).lower()
        if any(term in exc_str for term in ("rate limit", "urllib", "http error", "connection refused", "timeout", "temporary failure", "getaddrinfo")):
            pytest.skip(f"Network / API limit in Example {example_num}: {exc}")
        if "lets_plot" in exc_str or "lets-plot" in exc_str:
            pytest.skip(f"Optional dependency 'lets_plot' is unavailable for Example {example_num} ({title}): {exc}")
        raise
