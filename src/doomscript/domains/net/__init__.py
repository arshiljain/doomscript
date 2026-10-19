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
    net_ping_host,
    net_resolve_dns,
    net_check_port,
    net_create_basic_auth,
    net_create_bearer_auth,
    net_is_connected,
    net_cidr_to_netmask,
    net_ip_in_subnet,
    net_expand_cidr_range,
    net_is_valid_ipv4,
    net_is_valid_ipv6,
    net_format_mac_address,
    net_whois_domain,
    net_http_status_message,
    net_build_query_string,
    net_parse_url_components,
    net_exponential_backoff_delay,
    net_check_multiple_ports,
    net_reverse_dns_lookup,
    net_generate_multipart_boundary,
    net_encode_basic_auth_header,
    net_decode_basic_auth_header,
    net_parse_http_headers,
    net_format_http_headers,
    net_is_private_ip,
    net_download_file,
    HTTP2FrameParser,
    PacketDissector,
    WebSocketCodec,
    DNSWireProtocol,
    net_dns_build_query,
    net_dns_parse_packet,
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
            or s.startswith("ping host ")
            or s.startswith("resolve dns ")
            or s.startswith("check port ")
            or s.startswith("create basic auth ")
            or s.startswith("create bearer auth ")
            or s.startswith("check connectivity")
            or s.startswith("check internet connectivity")
            or s.startswith("convert cidr ")
            or s.startswith("cidr ")
            or s.startswith("check if ip ")
            or s.startswith("is ip ")
            or s.startswith("ip ")
            or s.startswith("expand cidr ")
            or s.startswith("expand subnet ")
            or s.startswith("validate ipv4 ")
            or s.startswith("is valid ipv4 ")
            or s.startswith("validate ipv6 ")
            or s.startswith("is valid ipv6 ")
            or s.startswith("normalize mac address ")
            or s.startswith("format mac address ")
            or s.startswith("whois lookup ")
            or s.startswith("whois domain ")
            or s.startswith("http status message ")
            or s.startswith("http status text ")
            or s.startswith("build query string ")
            or s.startswith("parse url ")
            or s.startswith("calculate backoff delay ")
            or s.startswith("scan ports ")
            or s.startswith("reverse dns lookup ")
            or s.startswith("generate multipart boundary")
            or s.startswith("encode basic auth header ")
            or s.startswith("decode basic auth header ")
            or s.startswith("parse raw http headers ")
            or s.startswith("format http headers ")
            or s.startswith("check if private ip ")
            or s.startswith("is private ip ")
            or s.startswith("private ip ")
            or s.startswith("download file from ")
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
    "net_ping_host",
    "net_resolve_dns",
    "net_check_port",
    "net_create_basic_auth",
    "net_create_bearer_auth",
    "net_is_connected",
    "net_cidr_to_netmask",
    "net_ip_in_subnet",
    "net_expand_cidr_range",
    "net_is_valid_ipv4",
    "net_is_valid_ipv6",
    "net_format_mac_address",
    "net_whois_domain",
    "net_http_status_message",
    "net_build_query_string",
    "net_parse_url_components",
    "net_exponential_backoff_delay",
    "net_check_multiple_ports",
    "net_reverse_dns_lookup",
    "net_generate_multipart_boundary",
    "net_encode_basic_auth_header",
    "net_decode_basic_auth_header",
    "net_parse_http_headers",
    "net_format_http_headers",
    "net_is_private_ip",
    "net_download_file",
    "HTTP2FrameParser",
    "PacketDissector",
    "WebSocketCodec",
    "DNSWireProtocol",
    "net_dns_build_query",
    "net_dns_parse_packet",
]
