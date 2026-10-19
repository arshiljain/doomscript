"""Runtime execution engine for Office Automation (Spreadsheets & Documents) domain."""

from typing import Any, Dict, List, Optional, Tuple, Union
import csv
import os
import zipfile
from xml.sax.saxutils import escape as xml_escape
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.office.spec import (
    OfficeSpreadsheetSpec,
    OfficeAddRowSpec,
    OfficeSaveSpreadsheetSpec,
    OfficeDocumentSpec,
    OfficeAddHeadingSpec,
    OfficeAddParagraphSpec,
    OfficeSaveDocumentSpec,
)


class DoomSpreadsheet:
    """High-level spreadsheet workbook supporting XLSX and CSV formats with zero dependencies."""

    def __init__(self):
        self.rows: List[List[Any]] = []

    def add_row(self, row_data: Any) -> None:
        if isinstance(row_data, dict):
            self.rows.append(list(row_data.values()))
        elif isinstance(row_data, (list, tuple)):
            self.rows.append(list(row_data))
        else:
            self.rows.append([row_data])

    def add_rows(self, rows_data: Any) -> None:
        if isinstance(rows_data, list):
            for r in rows_data:
                self.add_row(r)

    def save(self, path: str) -> str:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        ext = os.path.splitext(path)[1].lower()
        if ext in (".csv", ".tsv"):
            delimiter = "\t" if ext == ".tsv" else ","
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=delimiter)
                for r in self.rows:
                    writer.writerow(r)
            return path

        # Default or .xlsx: generate true OpenXML zip container
        self._write_xlsx(path)
        return path

    def _write_xlsx(self, path: str) -> None:
        sheet_data_xml = []
        for r_idx, row in enumerate(self.rows, start=1):
            sheet_data_xml.append(f'<row r="{r_idx}">')
            for c_idx, cell in enumerate(row, start=1):
                col_letter = chr(ord('A') + (c_idx - 1) % 26)
                cell_ref = f"{col_letter}{r_idx}"
                if isinstance(cell, (int, float)):
                    sheet_data_xml.append(f'<c r="{cell_ref}"><v>{cell}</v></c>')
                else:
                    text_esc = xml_escape(str(cell))
                    sheet_data_xml.append(f'<c r="{cell_ref}" t="inlineStr"><is><t>{text_esc}</t></is></c>')
            sheet_data_xml.append('</row>')

        sheet_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">\n'
            f'<sheetData>{"".join(sheet_data_xml)}</sheetData>\n'
            '</worksheet>'
        )

        content_types = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
            '<Default Extension="xml" ContentType="application/xml"/>\n'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>\n'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>\n'
            '</Types>'
        )

        workbook_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\n'
            '<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets>\n'
            '</workbook>'
        )

        workbook_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>\n'
            '</Relationships>'
        )

        root_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>\n'
            '</Relationships>'
        )

        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", content_types)
            zf.writestr("_rels/.rels", root_rels)
            zf.writestr("xl/workbook.xml", workbook_xml)
            zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
            zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)

    def __repr__(self) -> str:
        return f"DoomSpreadsheet(rows={len(self.rows)})"


class DoomWordDocument:
    """High-level word document supporting DOCX, Markdown, and text with zero dependencies."""

    def __init__(self):
        self.elements: List[Dict[str, Any]] = []

    def add_heading(self, text: str, level: int = 1) -> None:
        self.elements.append({"type": "heading", "text": str(text), "level": int(level)})

    def add_paragraph(self, text: str) -> None:
        self.elements.append({"type": "paragraph", "text": str(text)})

    def save(self, path: str) -> str:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        ext = os.path.splitext(path)[1].lower()
        if ext in (".md", ".txt"):
            lines = []
            for el in self.elements:
                if el["type"] == "heading":
                    hashes = "#" * max(1, min(6, el["level"]))
                    lines.append(f"{hashes} {el['text']}\n")
                elif el["type"] == "paragraph":
                    lines.append(f"{el['text']}\n")
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return path

        # Default or .docx: generate true OpenXML WordprocessingML zip package
        self._write_docx(path)
        return path

    def _write_docx(self, path: str) -> None:
        body_xml = []
        for el in self.elements:
            text_esc = xml_escape(el["text"])
            if el["type"] == "heading":
                style_id = f"Heading{el['level']}"
                body_xml.append(
                    f'<w:p><w:pPr><w:pStyle w:val="{style_id}"/></w:pPr>'
                    f'<w:r><w:rPr><w:b/></w:rPr><w:t>{text_esc}</w:t></w:r></w:p>'
                )
            elif el["type"] == "paragraph":
                body_xml.append(f'<w:p><w:r><w:t>{text_esc}</w:t></w:r></w:p>')

        doc_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n'
            f'<w:body>{"".join(body_xml)}</w:body>\n'
            '</w:document>'
        )

        content_types = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
            '<Default Extension="xml" ContentType="application/xml"/>\n'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>\n'
            '</Types>'
        )

        root_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>\n'
            '</Relationships>'
        )

        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", content_types)
            zf.writestr("_rels/.rels", root_rels)
            zf.writestr("word/document.xml", doc_xml)

    def __repr__(self) -> str:
        return f"DoomWordDocument(elements={len(self.elements)})"


DoomOfficeDocument = DoomWordDocument
DoomDocument = DoomWordDocument


# Standalone Helper Functions
def create_spreadsheet() -> DoomSpreadsheet:
    return DoomSpreadsheet()


def add_spreadsheet_row(sheet: DoomSpreadsheet, row_data: Any) -> None:
    sheet.add_row(row_data)


def add_spreadsheet_rows(sheet: DoomSpreadsheet, rows_data: Any) -> None:
    sheet.add_rows(rows_data)


def save_spreadsheet(sheet: DoomSpreadsheet, path: str) -> str:
    return sheet.save(path)


def create_word_document() -> DoomWordDocument:
    return DoomWordDocument()


def add_document_heading(doc: DoomWordDocument, text: str, level: int = 1) -> None:
    doc.add_heading(text, level=level)


def add_document_paragraph(doc: DoomWordDocument, text: str) -> None:
    doc.add_paragraph(text)


def save_word_document(doc: DoomWordDocument, path: str) -> str:
    return doc.save(path)


class OfficeRuntime(DomainRuntime):
    """Runtime execution engine for Office specifications."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        errors = ir.validate()
        if errors:
            raise ValueError(f"Office spec validation failed: {'; '.join(errors)}")

        if isinstance(ir, OfficeSpreadsheetSpec):
            return create_spreadsheet()
        elif isinstance(ir, OfficeAddRowSpec):
            sheet = scope.get(ir.sheet_var)
            row = scope.get(ir.row_data, ir.row_data)
            add_spreadsheet_row(sheet, row)
            return sheet
        elif isinstance(ir, OfficeSaveSpreadsheetSpec):
            sheet = scope.get(ir.sheet_var)
            path = scope.get(ir.path_expr, ir.path_expr)
            return save_spreadsheet(sheet, str(path))
        elif isinstance(ir, OfficeDocumentSpec):
            return create_word_document()
        elif isinstance(ir, OfficeAddHeadingSpec):
            doc = scope.get(ir.doc_var)
            add_document_heading(doc, ir.text, level=ir.level)
            return doc
        elif isinstance(ir, OfficeAddParagraphSpec):
            doc = scope.get(ir.doc_var)
            add_document_paragraph(doc, ir.text)
            return doc
        elif isinstance(ir, OfficeSaveDocumentSpec):
            doc = scope.get(ir.doc_var)
            path = scope.get(ir.path_expr, ir.path_expr)
            return save_word_document(doc, str(path))

        raise NotImplementedError(f"Unsupported IR: {type(ir)}")


def execute_office_ir(spec_id: str) -> Any:
    from doomscript.domains.registry import get_domain_registry
    spec = get_domain_registry().get_spec(spec_id)
    if spec is None:
        raise KeyError(f"Office spec not found: {spec_id}")
    return OfficeRuntime().execute_ir(spec, {})
