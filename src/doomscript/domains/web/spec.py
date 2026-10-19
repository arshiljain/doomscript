"""Declarative specifications and Intermediate Representation for the Web Scraping & Extraction domain."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from doomscript.domains.base import DomainIR


@dataclass
class WebPageSpec(DomainIR):
    """Specification for fetching or loading an HTML web page."""

    url_expr: str
    target_var: str

    def validate(self) -> List[str]:
        errors = []
        if not self.url_expr:
            errors.append("WebPageSpec requires a URL or HTML source")
        if not self.target_var:
            errors.append("WebPageSpec requires a target variable")
        return errors


@dataclass
class WebExtractLinksSpec(DomainIR):
    """Specification for extracting hyperlinks from a parsed page."""

    page_var: str
    target_var: str
    filter_class: Optional[str] = None

    def validate(self) -> List[str]:
        errors = []
        if not self.page_var:
            errors.append("WebExtractLinksSpec requires a source page variable")
        return errors


@dataclass
class WebExtractTableSpec(DomainIR):
    """Specification for extracting HTML tabular data into structured records."""

    page_var: str
    target_var: str
    header_contains: Optional[str] = None
    index: int = 0

    def validate(self) -> List[str]:
        errors = []
        if not self.page_var:
            errors.append("WebExtractTableSpec requires a source page variable")
        return errors


@dataclass
class WebExtractTextSpec(DomainIR):
    """Specification for extracting clean readable text or CSS-selected text."""

    page_var: str
    target_var: str
    selector: Optional[str] = None

    def validate(self) -> List[str]:
        errors = []
        if not self.page_var:
            errors.append("WebExtractTextSpec requires a source page variable")
        return errors


@dataclass
class WebDownloadMediaSpec(DomainIR):
    """Specification for downloading media matching a file extension pattern."""

    page_var: str
    folder_expr: str
    pattern: str = "*.png"
    target_var: str = "downloaded_files"

    def validate(self) -> List[str]:
        errors = []
        if not self.page_var or not self.folder_expr:
            errors.append("WebDownloadMediaSpec requires both page variable and folder expression")
        return errors
