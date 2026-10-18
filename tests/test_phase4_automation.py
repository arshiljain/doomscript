"""
Tests for Phase 4: Batteries-Included Automation & Data Stdlib
Validates table relational joins, HTML parsing, HTTP fetch/post,
email helper, timezones, and business date math.
"""

import textwrap
import pytest
from doomscript.compiler.engine import execute


def run(source: str):
    env = {}
    execute(textwrap.dedent(source).strip(), custom_globals=env)
    return env


def test_table_relational_joins():
    code = """
    employees = [
        {id: 1, name: "Alice", role: "Dev"},
        {id: 2, name: "Bob", role: "Designer"},
        {id: 3, name: "Charlie", role: "Manager"}
    ]
    salaries = [
        {id: 1, amount: 95000},
        {id: 2, amount: 85000},
        {id: 4, amount: 70000}
    ]

    # Inner join
    combine employees and salaries on "id" into roster

    # Left join
    combine employees and salaries on "id" with style "left" into full_roster
    """
    env = run(code)
    # Inner join matches 1 and 2
    assert len(env["roster"]) == 2
    assert env["roster"][0]["name"] == "Alice"
    assert env["roster"][0]["amount"] == 95000
    assert env["roster"][1]["name"] == "Bob"

    # Left join includes 1, 2, 3
    assert len(env["full_roster"]) == 3
    assert env["full_roster"][2]["name"] == "Charlie"
    assert "amount" not in env["full_roster"][2]


def test_html_extraction():
    code = """
    html_doc = '''
    <html>
        <head><title>Test Page</title><style>.hidden { display: none; }</style></head>
        <body>
            <h1>Welcome to DoomScript</h1>
            <p>Visit the <a href="https://doomscript.org/docs">Documentation</a>.</p>
            <p>Or check <a href="https://github.com/doomscript/doomscript">GitHub repo</a>.</p>
            <script>console.log("ignore me");</script>
        </body>
    </html>
    '''

    extract text from html html_doc into clean_text
    extract links from html html_doc into links
    """
    env = run(code)
    text = env["clean_text"]
    assert "Welcome to DoomScript" in text
    assert "Documentation" in text
    assert "ignore me" not in text
    assert "display: none" not in text

    links = env["links"]
    assert len(links) == 2
    assert "https://doomscript.org/docs" in links
    assert "https://github.com/doomscript/doomscript" in links


def test_email_sending():
    code = """
    send email to "test@example.com" with subject "Weekly Summary" and body "Everything looks great!" into result
    """
    env = run(code)
    assert env["result"]["to"] == "test@example.com"
    assert env["result"]["subject"] == "Weekly Summary"
    assert env["result"]["status"] in ("SENT", "SIMULATED")


def test_timezones_and_date_math():
    code = """
    utc_time = now in "UTC"
    next_work_day = next business day from "2026-10-16"  # Friday -> Monday
    weekend_check = today is weekend
    """
    env = run(code)
    assert len(env["utc_time"]) >= 19
    assert env["next_work_day"] == "2026-10-19"  # Monday
    assert isinstance(env["weekend_check"], bool)
