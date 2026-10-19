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
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.net.exporter import NetASTExporter
from doomscript.domains.registry import get_domain_registry


class NetDomain(DomainContract):
    """Web & API Automation domain pack providing HTTP verbs, retries, parsing, and workflow composition."""

    name = "net"
    aliases = ["web_api", "http_api"]
    description = "HTTP networking, REST APIs, JSON parsing, and response validation"
    parser = NetDomainParser()
    runtime = NetRuntime()
    exporter = NetASTExporter()
    capabilities = ["http", "rest", "json", "download", "request"]
    optional_dependencies = ["urllib", "requests"]

    verbs = [
        VerbSpec(
            name="http_request",
            pattern="(get|post|put|delete|patch) {url:expr} [with {params:expr}] into {target:ident}",
            arg_schema={"url": "expr", "target": "ident"},
            returns="Record",
            description="Execute HTTP request to endpoint",
        ),
        VerbSpec(
            name="inspect_response",
            pattern="inspect response {resp:ident} [into {target:ident}]",
            arg_schema={"resp": "ident", "target": "ident"},
            returns="Record",
            description="Inspect HTTP status code, headers, and payload size",
        ),
        VerbSpec(
            name="parse_response",
            pattern="parse [response] {resp:ident} as (json|text|html) into {target:ident}",
            arg_schema={"resp": "ident", "target": "ident"},
            returns="Any",
            description="Parse HTTP response body into Record or string",
        ),
        VerbSpec(
            name="save_response",
            pattern="save response {resp:ident} to {path:expr}",
            arg_schema={"resp": "ident", "path": "expr"},
            returns="str",
            description="Save response payload to local file",
        ),
    ]

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
