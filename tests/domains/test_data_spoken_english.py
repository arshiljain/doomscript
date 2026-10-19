import pytest
from doomscript.compiler.engine import execute

def test_data_spoken_english_seven_liner(tmp_path):
    raw_file = tmp_path / "sales_raw.csv"
    raw_file.write_text("customer,status,amount\nAlice,paid,120.0\nBob,pending,25.0\nCharlie,paid,80.0\nDavid,paid,30.0\n", encoding="utf-8")
    clean_file = tmp_path / "clean_report.csv"

    source = f"""use data

read csv file "{raw_file.as_posix()}" into orders
orders where status is "paid" into valid
valid where amount is over 50 into high_value
sort high_value by amount descending
write csv high_value into file "{clean_file.as_posix()}"
"""
    env = execute(source)
    assert len(env["orders"]) == 4
    assert len(env["valid"]) == 3
    assert len(env["high_value"]) == 2
    assert env["high_value"][0]["customer"] == "Alice"
    assert env["high_value"][1]["customer"] == "Charlie"
    assert clean_file.exists()


def test_data_domain_verb_declarations():
    source = """use data
explain domain data into info
"""
    env = execute(source)
    assert "verbs" in env["info"]
    verb_names = [v["name"] for v in env["info"]["verbs"]]
    assert "read_file" in verb_names
    assert "write_file" in verb_names
    assert "remove_duplicates" in verb_names
