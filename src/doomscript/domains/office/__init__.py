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
)
from doomscript.domains.office.exporter import OfficeASTExporter
from doomscript.domains.registry import get_domain_registry


class OfficeDomain(DomainContract):
    """Office Automation domain pack."""

    name = "office"
    aliases = ["sheet", "spreadsheet", "document", "docx"]
    parser = OfficeDomainParser()
    runtime = OfficeRuntime()
    exporter = OfficeASTExporter()

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        if (
            s.startswith("create spreadsheet ")
            or s.startswith("create word document ")
            or s.startswith("save spreadsheet ")
            or s.startswith("save word document ")
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
        else:
            if (s.startswith("add row ") or s.startswith("add rows ")) and (" to sheet" in s or " to spreadsheet" in s):
                return True
            if s.startswith("add heading ") and (" to word" in s or " to docx" in s):
                return True
            if s.startswith("add paragraph ") and (" to word" in s or " to docx" in s):
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
]
