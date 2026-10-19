"""Declarative specifications and Intermediate Representation for Office Automation domain."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from doomscript.domains.base import DomainIR


@dataclass
class OfficeSpreadsheetSpec(DomainIR):
    target_var: str = "sheet"

    def validate(self) -> List[str]:
        return []


@dataclass
class OfficeAddRowSpec(DomainIR):
    sheet_var: str
    row_data: Any

    def validate(self) -> List[str]:
        return []


@dataclass
class OfficeSaveSpreadsheetSpec(DomainIR):
    sheet_var: str
    path_expr: str

    def validate(self) -> List[str]:
        errors = []
        if not self.path_expr:
            errors.append("OfficeSaveSpreadsheetSpec requires a destination file path")
        return errors


@dataclass
class OfficeDocumentSpec(DomainIR):
    target_var: str = "doc"

    def validate(self) -> List[str]:
        return []


@dataclass
class OfficeAddHeadingSpec(DomainIR):
    doc_var: str
    text: str
    level: int = 1

    def validate(self) -> List[str]:
        return []


@dataclass
class OfficeAddParagraphSpec(DomainIR):
    doc_var: str
    text: str

    def validate(self) -> List[str]:
        return []


@dataclass
class OfficeSaveDocumentSpec(DomainIR):
    doc_var: str
    path_expr: str

    def validate(self) -> List[str]:
        errors = []
        if not self.path_expr:
            errors.append("OfficeSaveDocumentSpec requires a destination file path")
        return errors
