"""Independent Domain Parser for Office Automation (Spreadsheets & Documents) domain."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.office.spec import (
    OfficeSpreadsheetSpec,
    OfficeAddRowSpec,
    OfficeSaveSpreadsheetSpec,
    OfficeDocumentSpec,
    OfficeAddHeadingSpec,
    OfficeAddParagraphSpec,
    OfficeSaveDocumentSpec,
)


class OfficeDomainParser(DomainParser):
    """Independent parser for Office Automation syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # create spreadsheet into <target>
        m_sheet = re.match(
            r"^create\s+spreadsheet\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sheet:
            target = m_sheet.group(1).strip()
            return f"set {target} to create_spreadsheet()"

        # add row <row_expr> to [spreadsheet] <sheet_var>
        m_row = re.match(
            r"^add\s+row\s+(.+?)\s+to\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_row:
            row_expr = m_row.group(1).strip()
            sheet_var = m_row.group(2).strip()
            return f"add_spreadsheet_row({sheet_var}, {row_expr})"

        # add rows <rows_expr> to [spreadsheet] <sheet_var>
        m_rows = re.match(
            r"^add\s+rows\s+(.+?)\s+to\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rows:
            rows_expr = m_rows.group(1).strip()
            sheet_var = m_rows.group(2).strip()
            return f"add_spreadsheet_rows({sheet_var}, {rows_expr})"

        # save spreadsheet <sheet_var> to <path_expr>
        m_save_sheet = re.match(
            r"^save\s+spreadsheet\s+([A-Za-z_]\w*)\s+to\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_save_sheet:
            sheet_var = m_save_sheet.group(1).strip()
            path_expr = m_save_sheet.group(2).strip()
            return f"save_spreadsheet({sheet_var}, {path_expr})"

        # create word document into <target>
        m_doc = re.match(
            r"^create\s+word\s+document\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_doc:
            target = m_doc.group(1).strip()
            return f"set {target} to create_word_document()"

        # add heading <text_expr> [(with|at) level <n>] to [document] <doc_var>
        m_heading = re.match(
            r"^add\s+heading\s+(.+?)(?:\s+(?:with|at)\s+level\s+(\d+))?\s+to\s+(?:(?:word\s+)?document\s+)?([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_heading:
            text_expr = m_heading.group(1).strip()
            level = m_heading.group(2).strip() if m_heading.group(2) else "1"
            doc_var = m_heading.group(3).strip()
            return f"add_document_heading({doc_var}, {text_expr}, level={level})"

        # add paragraph <text_expr> to [document] <doc_var>
        m_para = re.match(
            r"^add\s+paragraph\s+(.+?)\s+to\s+(?:(?:word\s+)?document\s+)?([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_para:
            text_expr = m_para.group(1).strip()
            doc_var = m_para.group(2).strip()
            return f"add_document_paragraph({doc_var}, {text_expr})"

        # save word document <doc_var> to <path_expr>
        m_save_doc = re.match(
            r"^save\s+(?:word\s+)?document\s+([A-Za-z_]\w*)\s+to\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_save_doc:
            doc_var = m_save_doc.group(1).strip()
            path_expr = m_save_doc.group(2).strip()
            return f"save_word_document({doc_var}, {path_expr})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Office domain does not currently define declarative blocks")
