import pytest
from doomscript.compiler.engine import execute

def test_flagship_fluent_orchestration(tmp_path):
    report_xlsx = str(tmp_path / "summary.xlsx").replace("\\", "/")
    source = f"""use finance
use data
use office
use cloud

fetch stock prices for "AAPL" from "2024-01-01" to "2024-01-20" into prices
prices where close is over 100 into rally
create spreadsheet into sheet
add rows from rally to sheet
save spreadsheet sheet to "{report_xlsx}"
connect to bucket "vault" into b
upload file "{report_xlsx}" to bucket b as "reports/rally.xlsx"
list all files in bucket b into cloud_files
"""
    env = execute(source)
    assert len(env["rally"]) > 0
    assert "reports/rally.xlsx" in env["cloud_files"]

def test_flagship_domain_introspections():
    source = """use office
use cloud
use graph
use audio
explain domain office into off_info
explain domain cloud into cld_info
explain domain graph into grp_info
explain domain audio into aud_info
"""
    env = execute(source)
    assert len(env["off_info"].verbs) > 0
    assert len(env["cld_info"].verbs) > 0
    assert len(env["grp_info"].verbs) > 0
    assert len(env["aud_info"].verbs) > 0
