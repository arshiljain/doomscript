import pytest
from doomscript.compiler.engine import execute
from doomscript.taxonomy import Table
from doomscript.runtime import Record

def test_explain_domain():
    source = """use finance
explain domain finance into fin_info
"""
    env = execute(source)
    assert "fin_info" in env
    assert "verbs" in env["fin_info"]
    assert len(env["fin_info"]["verbs"]) > 0


def test_explain_table_and_preview():
    source = """
data = [
    {"product": "Apples", "sales": 100},
    {"product": "Oranges", "sales": 150}
]
explain data into info
preview of data into p
summary of data into s
"""
    env = execute(source)
    assert env["info"]["row_count"] == 2
    assert "sales" in env["info"]["columns"]
    assert len(env["p"]) == 2
    assert "sales" in env["s"]
