"""Web & API Automation Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.net.spec import ApiWorkflowSpec, RequestStep, ParseStep, SaveStep
from doomscript.domains.net.parser import NetDomainParser
from doomscript.domains.net.runtime import (
    NetRuntime,
    HttpResponseContainer,
    execute_http_request,
    inspect_response,
    parse_response_content,
    save_response_content,
    set_mutating_requests_allowed,
    is_mutating_requests_allowed,
)
from doomscript.domains.net.exporter import NetASTExporter
from doomscript.domains.registry import get_domain_registry


class NetDomain(DomainContract):
    """Web & API Automation domain pack providing HTTP verbs, retries, parsing, and workflow composition."""

    name = "net"
    aliases = ["web", "api", "http"]
    parser = NetDomainParser()
    runtime = NetRuntime()
    exporter = NetASTExporter()

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        if (
            s.startswith("inspect response ")
            or s.startswith("status of ")
            or s.startswith("request ")
            or bool(re.match(r"^get\s+[\"']", s))
            or bool(re.match(r"^post\s+[\"']", s))
            or bool(re.match(r"^(?:get|post|put|delete|patch)\s+(?:https?://|api/|url\b)", s))
            or (s.startswith("parse ") and (" as json " in s or " as text " in s))
            or s.startswith("allow mutating ")
            or s.startswith("block mutating ")
            or s.startswith("disallow mutating ")
        ):
            return True
        if re.match(r"^save\s+(?:response|resp)\s+to\s+", s):
            return True
        return False

    def can_handle_block(self, header: str) -> bool:
        s = header.strip().lower()
        return s.startswith("api ") and s.endswith(":")


# Register with central registry
NET_DOMAIN = NetDomain()
get_domain_registry().register(NET_DOMAIN)

__all__ = [
    "NetDomain",
    "NET_DOMAIN",
    "ApiWorkflowSpec",
    "RequestStep",
    "ParseStep",
    "SaveStep",
    "NetDomainParser",
    "NetRuntime",
    "NetASTExporter",
    "HttpResponseContainer",
    "execute_http_request",
    "inspect_response",
    "parse_response_content",
    "save_response_content",
    "set_mutating_requests_allowed",
    "is_mutating_requests_allowed",
]
