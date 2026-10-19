"""Unit and integration tests for Web Scraping & Document Extraction domain (use web)."""

import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.web.runtime import (
    WebPage,
    parse_html,
    webpage_title,
    webpage_text,
    extract_web_links,
    extract_web_table,
    download_web_media,
)

SAMPLE_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>DoomScript Tech Portal</title>
</head>
<body>
    <h1>Welcome to DoomScript</h1>
    <p>English-first programming language with high performance.</p>
    <div class="nav">
        <a href="https://doomscript.org/docs" class="nav-item">Documentation</a>
        <a href="https://github.com/arshiljain/doomscript" class="github-link">GitHub Repo</a>
        <a href="/about" class="nav-item">About Us</a>
    </div>
    <div class="pricing">
        <table id="plans">
            <tr>
                <th>Tier</th>
                <th>Price</th>
                <th>Users</th>
            </tr>
            <tr>
                <td>Community</td>
                <td>0</td>
                <td>1000</td>
            </tr>
            <tr>
                <td>Pro</td>
                <td>49</td>
                <td>50000</td>
            </tr>
        </table>
    </div>
</body>
</html>
"""


def test_web_runtime_direct():
    page = parse_html(SAMPLE_HTML, url="https://doomscript.org")
    assert webpage_title(page) == "DoomScript Tech Portal"
    assert "English-first programming language" in webpage_text(page)

    # Links
    links = extract_web_links(page)
    assert len(links) == 3
    assert any("docs" in l["url"] for l in links)

    # Filtered Links
    nav_links = extract_web_links(page, filter_class="nav-item")
    assert len(nav_links) == 2
    assert all("nav-item" in l["class"] for l in nav_links)

    # Table extraction
    table = extract_web_table(page, header_contains="Price")
    assert len(table) == 2
    assert table[0]["Tier"] == "Community"
    assert table[0]["Price"] == 0
    assert table[1]["Tier"] == "Pro"
    assert table[1]["Price"] == 49


def test_web_domain_script_execution():
    escaped_html = SAMPLE_HTML.replace("\n", " ").replace('"', '\\"')
    source = f"""use web

raw_html = "{escaped_html}"
parse html raw_html into portal_page
title of portal_page into doc_title
text in portal_page into doc_text
extract all links from portal_page into links
extract links from portal_page where class is "nav-item" into nav_links
find table containing "Price" in portal_page into pricing_table
"""
    env = execute(source)
    assert env["doc_title"] == "DoomScript Tech Portal"
    assert "English-first programming language" in env["doc_text"]
    assert len(env["links"]) == 3
    assert len(env["nav_links"]) == 2
    assert len(env["pricing_table"]) == 2
    assert env["pricing_table"][0]["Tier"] == "Community"
    assert env["pricing_table"][1]["Price"] == 49


def test_web_domain_python_export():
    source = """use web

parse html "<html><title>Hi</title><body><a href='http://x.com'>Link</a></body></html>" into page
title of page into title_text
extract all links from page into link_list
"""
    py_code = export_to_python(source)
    assert "parse_html" in py_code
    assert "webpage_title" in py_code
    assert "extract_web_links" in py_code
