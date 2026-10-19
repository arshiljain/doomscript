"""Unit and integration tests for Office Automation domain (use office)."""

import os
import zipfile
import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.office.runtime import (
    DoomSpreadsheet,
    DoomDocument,
    create_spreadsheet,
    add_spreadsheet_row,
    add_spreadsheet_rows,
    save_spreadsheet,
    create_word_document,
    add_document_heading,
    add_document_paragraph,
    save_word_document,
)


def test_office_runtime_direct(tmp_path):
    # Spreadsheet (.xlsx and .csv)
    sheet = create_spreadsheet()
    add_spreadsheet_row(sheet, ["Product", "Price", "Qty"])
    add_spreadsheet_rows(sheet, [["Apples", 2.5, 10], ["Bananas", 1.2, 20]])

    xlsx_path = str(tmp_path / "sales.xlsx")
    save_spreadsheet(sheet, xlsx_path)
    assert os.path.exists(xlsx_path)
    # Check that xlsx is a valid zip containing [Content_Types].xml and xl/worksheets/sheet1.xml
    with zipfile.ZipFile(xlsx_path, "r") as z:
        namelist = z.namelist()
        assert "[Content_Types].xml" in namelist
        assert "xl/worksheets/sheet1.xml" in namelist

    csv_path = str(tmp_path / "sales.csv")
    save_spreadsheet(sheet, csv_path)
    assert os.path.exists(csv_path)
    with open(csv_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Apples" in content

    # Document (.docx)
    doc = create_word_document()
    add_document_heading(doc, "Project Status", level=1)
    add_document_paragraph(doc, "The automated deployment succeeded without issues.")
    docx_path = str(tmp_path / "report.docx")
    save_word_document(doc, docx_path)
    assert os.path.exists(docx_path)
    with zipfile.ZipFile(docx_path, "r") as z:
        namelist = z.namelist()
        assert "word/document.xml" in namelist


def test_office_domain_script_execution(tmp_path):
    sheet_out = str(tmp_path / "budget.xlsx").replace("\\", "/")
    doc_out = str(tmp_path / "memo.docx").replace("\\", "/")
    source = f"""use office

create spreadsheet into budget_sheet
add row ["Category", "Amount"] to budget_sheet
add rows [["Engineering", 50000], ["Design", 20000]] to budget_sheet
save spreadsheet budget_sheet to "{sheet_out}"

create word document into memo_doc
add heading "Executive Memo" with level 1 to memo_doc
add paragraph "Please review the quarterly financial allocation." to memo_doc
save word document memo_doc to "{doc_out}"
"""
    env = execute(source)
    assert os.path.exists(sheet_out)
    assert os.path.exists(doc_out)
    assert len(env["budget_sheet"].rows) == 3
    assert len(env["memo_doc"].elements) == 2


def test_office_domain_python_export():
    source = """use office

create spreadsheet into s
add row ["A", 1] to s
save spreadsheet s to "out.xlsx"
"""
    py_code = export_to_python(source)
    assert "create_spreadsheet" in py_code
    assert "add_spreadsheet_row" in py_code
    assert "save_spreadsheet" in py_code
