import io
import sys
import pytest
import textwrap
from doomscript.compiler.engine import compile_to_ast, execute
from doomscript.grammar.phrases import normalize

def run(source: str, custom_globals: dict = None) -> dict:
    env = custom_globals if custom_globals is not None else {}
    norm = normalize(textwrap.dedent(source).strip())
    tree = compile_to_ast(norm)
    return execute(tree, custom_globals=env)



def test_bug1_compound_interest():
    code = """
    compound interest on 1000 at 5% for 10 years into fv1
    compound interest on 1000 at 0.05 for 10 years into fv2
    compound interest on 1000 at 5% for 10 years compounded monthly into fv_monthly
    """
    ns = run(code)
    # At 5% annual default, 1000 * (1.05)^10 = 1628.89
    assert ns["fv1"] == 1628.89
    assert ns["fv2"] == 1628.89
    # Monthly compounding: 1000 * (1 + 0.05/12)^120 = 1647.01
    assert ns["fv_monthly"] == 1647.01


def test_bug2_knowledge_index_ranking():
    code = """
    create knowledge index into idx
    index document "market_doc" text "Stock market trends and quarterly financial dividends" into idx
    index document "space_doc" text "Deep space galaxy telescope astronomy observations" into idx
    index document "cat_doc" text "My cat purrs softly when stroked" into idx

    search knowledge index idx for "my cat purrs" into results
    """
    ns = run(code)
    results = ns["results"]
    assert len(results) > 0
    # The cat document must be ranked #1, definitely not last
    assert results[0].id == "cat_doc"



def test_bug3_call_c_library_abs():
    code = """
    call c library "libc.so.6" function "abs" with args [-5] into res
    """
    ns = run(code)
    assert ns["res"] == 5


def test_bug4_ask_piped_input_and_eof(monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO("Alice\n42\n"))
    code = """
    ask "Enter name: " into name
    ask number "Enter age: " into age
    ask "Enter extra: " into extra
    """
    ns = run(code)
    assert ns["name"] == "Alice"
    assert ns["age"] == 42
    assert ns["extra"] == ""
