"""Office Automation (Spreadsheets & Documents) Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.office.spec import (
    OfficeSpreadsheetSpec,
    OfficeAddRowSpec,
    OfficeSaveSpreadsheetSpec,
    OfficeDocumentSpec,
    OfficeAddHeadingSpec,
    OfficeAddParagraphSpec,
    OfficeSaveDocumentSpec,
)
from doomscript.domains.office.parser import OfficeDomainParser
from doomscript.domains.office.runtime import (
    DoomSpreadsheet,
    DoomDocument,
    OfficeRuntime,
    create_spreadsheet,
    add_spreadsheet_row,
    add_spreadsheet_rows,
    save_spreadsheet,
    create_word_document,
    add_document_heading,
    add_document_paragraph,
    save_word_document,
    execute_office_ir,
    office_count_worksheets,
    office_extract_text,
    office_add_worksheet,
    office_markdown_to_sections,
    office_merge_pdfs,
    office_count_pages,
    office_append_table_to_sheet,
    office_calculate_sheet_summary,
    office_detect_csv_delimiter,
    office_read_csv_header,
    office_create_table_in_document,
    office_add_bulleted_list,
    office_add_numbered_list,
    office_set_spreadsheet_cell,
    office_get_spreadsheet_cell,
    office_find_replace_in_document,
    office_list_worksheet_names,
    office_delete_worksheet,
    office_rename_worksheet,
    office_sort_spreadsheet_by_column,
    office_filter_spreadsheet_rows,
    office_export_sheet_to_json,
    office_import_json_to_sheet,
    office_count_words_in_document,
    office_count_characters_in_document,
    office_extract_document_metadata,
    PureXlsxWorkbook,
    PureDocxDocument,
    PurePptxPresentation,
)
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.office.exporter import OfficeASTExporter
from doomscript.domains.registry import get_domain_registry


class OfficeDomain(DomainContract):
    """Office Automation domain pack."""

    name = "office"
    aliases = ["sheet", "spreadsheet", "document", "docx"]
    description = "Office automation for spreadsheets (.xlsx/.csv) and Word documents (.docx)"
    parser = OfficeDomainParser()
    runtime = OfficeRuntime()
    exporter = OfficeASTExporter()
    capabilities = ["spreadsheet", "xlsx", "csv", "docx", "word"]
    optional_dependencies = ["openpyxl", "python-docx"]

    verbs = [
        VerbSpec(
            name="create_spreadsheet",
            pattern="create spreadsheet into {target:ident}",
            arg_schema={"target": "ident"},
            returns="Spreadsheet",
            description="Create a new in-memory spreadsheet workbook",
        ),
        VerbSpec(
            name="add_row",
            pattern="add row {row_expr:expr} to [spreadsheet] {sheet_var:ident}",
            arg_schema={"row_expr": "expr", "sheet_var": "ident"},
            returns="None",
            description="Append single row to spreadsheet",
        ),
        VerbSpec(
            name="add_rows",
            pattern="add rows [from] {rows_expr:expr} to [spreadsheet] {sheet_var:ident}",
            arg_schema={"rows_expr": "expr", "sheet_var": "ident"},
            returns="None",
            description="Append multiple rows or Table records to spreadsheet",
        ),
        VerbSpec(
            name="save_spreadsheet",
            pattern="save spreadsheet {sheet_var:ident} to {path_expr:expr}",
            arg_schema={"sheet_var": "ident", "path_expr": "expr"},
            returns="str",
            description="Export spreadsheet workbook to .xlsx or .csv on disk",
        ),
        VerbSpec(
            name="create_word_document",
            pattern="create word document into {target:ident}",
            arg_schema={"target": "ident"},
            returns="Document",
            description="Create a new Word document",
        ),
        VerbSpec(
            name="add_heading",
            pattern="add heading {text_expr:expr} to [document] {doc_var:ident} [at level {level:int}]",
            arg_schema={"text_expr": "expr", "doc_var": "ident", "level": "int"},
            defaults={"level": 1},
            returns="None",
            description="Add heading section to Word document",
        ),
        VerbSpec(
            name="add_paragraph",
            pattern="add paragraph {text_expr:expr} to [document] {doc_var:ident}",
            arg_schema={"text_expr": "expr", "doc_var": "ident"},
            returns="None",
            description="Add paragraph body text to Word document",
        ),
        VerbSpec(
            name="save_word_document",
            pattern="save word document {doc_var:ident} to {path_expr:expr}",
            arg_schema={"doc_var": "ident", "path_expr": "expr"},
            returns="str",
            description="Export Word document to .docx file",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        if (
            s.startswith("create spreadsheet ")
            or s.startswith("create word document ")
            or s.startswith("save spreadsheet ")
            or s.startswith("save word document ")
            or s.startswith("count worksheets in ")
            or s.startswith("extract text from ")
            or s.startswith("add worksheet ")
            or s.startswith("convert markdown ")
            or s.startswith("merge pdf ")
            or s.startswith("count pages in ")
            or s.startswith("append table ")
            or s.startswith("calculate sheet summary ")
            or s.startswith("calculate summary ")
            or s.startswith("detect csv delimiter ")
            or s.startswith("read csv header ")
            or s.startswith("set cell at row ")
            or s.startswith("get cell at row ")
            or s.startswith("find and replace ")
            or (s.startswith("replace ") and " in " in s and ("document" in s or "doc" in s))
            or s.startswith("list worksheet ")
            or s.startswith("list worksheets ")
            or s.startswith("delete worksheet ")
            or s.startswith("rename worksheet ")
            or s.startswith("sort sheet ")
            or s.startswith("filter sheet ")
            or s.startswith("export sheet ")
            or s.startswith("import json ")
            or s.startswith("count words in ")
            or s.startswith("count characters in ")
            or s.startswith("extract document metadata ")
        ):
            return True

        from doomscript.domains.registry import get_domain_registry
        is_active = get_domain_registry().is_active("office")

        if is_active:
            if (s.startswith("add row ") or s.startswith("add rows ")) and " to " in s:
                return True
            if s.startswith("add heading ") and " to " in s:
                return True
            if s.startswith("add paragraph ") and " to " in s:
                return True
            if s.startswith("add table with headers ") and " to " in s:
                return True
            if s.startswith("add bulleted list ") and " to " in s:
                return True
            if s.startswith("add numbered list ") and " to " in s:
                return True
        else:
            if (s.startswith("add row ") or s.startswith("add rows ")) and (" to sheet" in s or " to spreadsheet" in s):
                return True
            if s.startswith("add heading ") and (" to word" in s or " to docx" in s):
                return True
            if s.startswith("add paragraph ") and (" to word" in s or " to docx" in s):
                return True
            if s.startswith("add table with headers ") and (" to word" in s or " to docx" in s):
                return True
            if s.startswith("add bulleted list ") and (" to word" in s or " to docx" in s):
                return True
            if s.startswith("add numbered list ") and (" to word" in s or " to docx" in s):
                return True

        return False

    def can_handle_block(self, header: str) -> bool:
        return False


# Register with central registry
OFFICE_DOMAIN = OfficeDomain()
get_domain_registry().register(OFFICE_DOMAIN)

__all__ = [
    "OfficeDomain",
    "OFFICE_DOMAIN",
    "OfficeSpreadsheetSpec",
    "OfficeAddRowSpec",
    "OfficeSaveSpreadsheetSpec",
    "OfficeDocumentSpec",
    "OfficeAddHeadingSpec",
    "OfficeAddParagraphSpec",
    "OfficeSaveDocumentSpec",
    "OfficeDomainParser",
    "OfficeRuntime",
    "OfficeASTExporter",
    "DoomSpreadsheet",
    "DoomWordDocument",
    "DoomOfficeDocument",
    "DoomDocument",
    "create_spreadsheet",
    "add_spreadsheet_row",
    "add_spreadsheet_rows",
    "save_spreadsheet",
    "create_word_document",
    "add_document_heading",
    "add_document_paragraph",
    "save_word_document",
    "execute_office_ir",
    "office_count_worksheets",
    "office_extract_text",
    "office_add_worksheet",
    "office_markdown_to_sections",
    "office_merge_pdfs",
    "office_count_pages",
    "office_append_table_to_sheet",
    "office_calculate_sheet_summary",
    "office_detect_csv_delimiter",
    "office_read_csv_header",
    "office_create_table_in_document",
    "office_add_bulleted_list",
    "office_add_numbered_list",
    "office_set_spreadsheet_cell",
    "office_get_spreadsheet_cell",
    "office_find_replace_in_document",
    "office_list_worksheet_names",
    "office_delete_worksheet",
    "office_rename_worksheet",
    "office_sort_spreadsheet_by_column",
    "office_filter_spreadsheet_rows",
    "office_export_sheet_to_json",
    "office_import_json_to_sheet",
    "office_count_words_in_document",
    "office_count_characters_in_document",
    "office_extract_document_metadata",
    "PureXlsxWorkbook",
    "PureDocxDocument",
    "PurePptxPresentation",
]
