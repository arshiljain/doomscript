"""Web & API Automation Domain Specification and Intermediate Representation (IR)."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from doomscript.domains.base import DomainIR


@dataclass
class RequestStep:
    method: str = "GET"
    url_or_endpoint: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Any] = None
    target: str = "response"


@dataclass
class ParseStep:
    source_resp: str
    format: str = "json"  # "json" or "text"
    target: str = "parsed_data"


@dataclass
class SaveStep:
    source_resp: str
    path: str


@dataclass
class ApiWorkflowSpec(DomainIR):
    """Specification for an API client workflow with automatic retries and parsing."""

    name: str
    base_url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: float = 10.0
    retries: int = 3
    backoff_factor: float = 1.5
    steps: List[Any] = field(default_factory=list)
    target_var: str = "api_output"

    def validate(self) -> List[str]:
        errors = []
        if not self.name:
            errors.append("API workflow name cannot be empty")
        if self.timeout <= 0:
            errors.append(f"Timeout must be positive, got {self.timeout}")
        if self.retries < 0:
            errors.append(f"Retries cannot be negative, got {self.retries}")
        return errors
