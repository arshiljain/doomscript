"""
Tests for Phase 3: Learning and Error Experience
Validates error formatting with carets, difflib suggestions, explainer,
formatter (doom fmt), project scaffolder (doom new), and CLI commands.
"""

from typer.testing import CliRunner
from doomscript.cli import app
from doomscript.errors import format_syntax_error, find_closest_phrasings, translate_lark_error
from doomscript.explainer import explain_source
from doomscript.formatter import format_code
from doomscript.compiler.engine import compile_to_ast
from lark.exceptions import UnexpectedToken, UnexpectedCharacters

runner = CliRunner()


def test_closest_phrasings_difflib():
    # Broken or partial sentences
    suggestions = find_closest_phrasings("print hello to world")
    assert len(suggestions) > 0
    assert any("say" in s.lower() for s in suggestions)

    suggestions_loop = find_closest_phrasings("repeat 5 time")
    assert any("repeat 5 times:" in s for s in suggestions_loop)

    suggestions_cond = find_closest_phrasings("score is between 10 20")
    assert any("between" in s for s in suggestions_cond)


def test_error_translation_and_formatting():
    source = "set x = 100\nfoo bar baz ???"
    try:
        compile_to_ast(source)
    except Exception as e:
        plain_err = format_syntax_error(source, e, file_path="script.doom", theatrical=False)
        assert "script.doom" in plain_err
        assert "^" in plain_err  # Caret pointer
        assert "Did you mean:" in plain_err

        theatrical_err = format_syntax_error(source, e, file_path="script.doom", theatrical=True)
        assert "FOOLISH MORTAL" in theatrical_err
        assert "^" in theatrical_err


def test_explainer_line_by_line():
    code = """
    name = "Doom"
    count = 42
    say "Hello", name
    repeat 3 times:
        increase count by 1
    """
    items = explain_source(code)
    code_items = [item for item in items if item["is_code"]]
    assert len(code_items) >= 4
    assert any("Stores a computed value" in item["explanation"] for item in code_items)
    assert any("Prints values" in item["explanation"] for item in code_items)


def test_code_formatter():
    unformatted = """
please say "Hello"
set x to 10.
kindly increase x by 5
if x is bigger than 5:
    say "x is big"
"""
    formatted = format_code(unformatted)
    # Filler words stripped
    assert "please" not in formatted
    assert "kindly" not in formatted
    # Synonyms canonicalized
    assert "is greater than" in formatted
    assert 'say "Hello"' in formatted


def test_cli_suggest():
    res = runner.invoke(app, ["suggest", "say 'Hello'"])
    assert res.exit_code == 0
    assert "VALID DOOMSCRIPT" in res.stdout

    res_fail = runner.invoke(app, ["suggest", "random gibberish phrase ??"])
    assert res_fail.exit_code == 0
    assert "Supported phrasings you can use" in res_fail.stdout


def test_cli_explain_and_check(tmp_path):
    script_path = tmp_path / "test.doom"
    script_path.write_text('score = 99\nsay "Final Score:", score\n', encoding="utf-8")

    res_check = runner.invoke(app, ["check", str(script_path)])
    assert res_check.exit_code == 0
    assert "Syntax Valid" in res_check.stdout

    res_explain = runner.invoke(app, ["explain", str(script_path)])
    assert res_explain.exit_code == 0
    assert "Final Score" in res_explain.stdout


def test_cli_fmt(tmp_path):
    script_path = tmp_path / "unformatted.doom"
    script_path.write_text('please say "Formatted!"\n', encoding="utf-8")

    res = runner.invoke(app, ["fmt", str(script_path), "--write"])
    assert res.exit_code == 0
    content = script_path.read_text(encoding="utf-8")
    assert "please" not in content
    assert 'say "Formatted!"' in content


def test_cli_new(tmp_path):
    target = tmp_path / "my_doom_project"
    res = runner.invoke(app, ["new", str(target)])
    assert res.exit_code == 0
    assert (target / "main.doom").exists()
    assert (target / "README.md").exists()
    assert (target / "data" / "sales.csv").exists()
