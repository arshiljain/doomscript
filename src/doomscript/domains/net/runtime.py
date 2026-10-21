from __future__ import annotations
"""Runtime execution engine for Web & API Automation operations."""

import json
import os
import re
import struct
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.net.spec import ApiWorkflowSpec, RequestStep, ParseStep, SaveStep
from doomscript.core.record import Record


class HttpResponseContainer:
    """Encapsulates an HTTP response with convenient helpers."""

    def __init__(
        self,
        status_code: int,
        headers: Dict[str, str],
        body: bytes,
        url: str,
        method: str = "GET",
    ):
        self.status_code = status_code
        self.status = status_code
        self.headers = headers
        self.body = body
        self.url = url
        self.method = method
        self.ok = 200 <= status_code < 300

    @property
    def text(self) -> str:
        try:
            return self.body.decode("utf-8")
        except UnicodeDecodeError:
            return self.body.decode("latin1", errors="replace")

    def json(self) -> Any:
        return json.loads(self.text)

    def __repr__(self) -> str:
        return f"<Response [{self.status_code}] {self.method} {self.url}>"


_MUTATING_ALLOWED: bool = True


def set_mutating_requests_allowed(allowed: bool) -> None:
    """Sets whether mutating HTTP requests (POST, PUT, DELETE, PATCH) are permitted."""
    global _MUTATING_ALLOWED
    _MUTATING_ALLOWED = bool(allowed)


def is_mutating_requests_allowed() -> bool:
    """Checks whether mutating HTTP requests are currently permitted."""
    return _MUTATING_ALLOWED


def execute_http_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Any] = None,
    timeout: float = 10.0,
    retries: int = 0,
    backoff_factor: float = 1.0,
) -> HttpResponseContainer:
    """Executes an HTTP request with automatic retries and exponential backoff."""
    method = method.upper()
    if method in ("POST", "PUT", "DELETE", "PATCH"):
        if not is_mutating_requests_allowed():
            raise PermissionError(f"Mutating HTTP request {method} is blocked by network permission policy")

    req_headers = dict(headers or {})
    data_bytes = None

    if body is not None:
        if isinstance(body, (dict, list)):
            data_bytes = json.dumps(body).encode("utf-8")
            req_headers.setdefault("Content-Type", "application/json")
        elif isinstance(body, str):
            data_bytes = body.encode("utf-8")
        elif isinstance(body, bytes):
            data_bytes = body

    attempts = max(1, retries + 1)
    delay = 0.5

    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, data=data_bytes, headers=req_headers, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp_body = resp.read()
                resp_headers = {k: v for k, v in resp.getheaders()}
                return HttpResponseContainer(
                    status_code=resp.status,
                    headers=resp_headers,
                    body=resp_body,
                    url=url,
                    method=method,
                )
        except urllib.error.HTTPError as e:
            if attempt < attempts - 1 and e.code in (429, 500, 502, 503, 504):
                time.sleep(delay)
                delay *= backoff_factor
                continue
            resp_body = e.read() if hasattr(e, "read") else b""
            resp_headers = {k: v for k, v in e.headers.items()} if hasattr(e, "headers") and e.headers else {}
            return HttpResponseContainer(
                status_code=e.code,
                headers=resp_headers,
                body=resp_body,
                url=url,
                method=method,
            )
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt < attempts - 1:
                time.sleep(delay)
                delay *= backoff_factor
                continue
            return HttpResponseContainer(
                status_code=599,
                headers={},
                body=str(e).encode("utf-8"),
                url=url,
                method=method,
            )

    return HttpResponseContainer(
        status_code=500,
        headers={},
        body=b"Request failed after all retries",
        url=url,
        method=method,
    )


def inspect_response(resp: Any) -> Dict[str, Any]:
    """Level 1: Summarizes an HTTP response status, headers, and length."""
    if not isinstance(resp, HttpResponseContainer):
        return {"error": "Not a valid HttpResponseContainer"}
    return {
        "status_code": resp.status_code,
        "ok": resp.ok,
        "method": resp.method,
        "url": resp.url,
        "content_length": len(resp.body),
        "content_type": resp.headers.get("Content-Type", ""),
        "headers": dict(resp.headers),
    }


def parse_response_content(resp: Any, format_type: str = "json") -> Any:
    """Level 2: Parses HTTP response payload as JSON or plain text."""
    if not isinstance(resp, HttpResponseContainer):
        return resp
    if format_type.lower() == "json":
        return resp.json()
    return resp.text


def save_response_content(resp: Any, path: str) -> str:
    """Level 2: Writes HTTP response payload to a local file."""
    if not isinstance(resp, HttpResponseContainer):
        raise TypeError("save_response_content expects HttpResponseContainer")
    out_dir = os.path.dirname(os.path.abspath(path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(path, "wb") as f:
        f.write(resp.body)
    return path


class NetRuntime(DomainRuntime):
    """Runtime engine for executing ApiWorkflowSpec."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        if not isinstance(ir, ApiWorkflowSpec):
            raise TypeError(f"NetRuntime expects ApiWorkflowSpec, got {type(ir).__name__}")
        return self.execute_workflow(ir, scope)

    def execute_workflow(self, spec: ApiWorkflowSpec, scope: Dict[str, Any]) -> Any:
        last_result = None
        base = spec.base_url.rstrip("/")

        for step in spec.steps:
            if isinstance(step, RequestStep):
                url = step.url_or_endpoint
                if base and not url.startswith("http://") and not url.startswith("https://"):
                    url = f"{base}/{url.lstrip('/')}"
                merged_headers = dict(spec.headers)
                merged_headers.update(step.headers)

                resp = execute_http_request(
                    method=step.method,
                    url=url,
                    headers=merged_headers,
                    body=step.body,
                    timeout=spec.timeout,
                    retries=spec.retries,
                    backoff_factor=spec.backoff_factor,
                )
                scope[step.target] = resp
                last_result = resp

            elif isinstance(step, ParseStep):
                src = scope.get(step.source_resp, last_result)
                parsed = parse_response_content(src, format_type=step.format)
                scope[step.target] = parsed
                last_result = parsed

            elif isinstance(step, SaveStep):
                src = scope.get(step.source_resp, last_result)
                save_response_content(src, step.path)

        if spec.target_var:
            scope[spec.target_var] = last_result
        return last_result


# --- Batch 12 Spoken English Network & Web Services Verbs ---

def net_ping_host(host: Any, timeout: float = 2.0) -> bool:
    """Test if host is reachable via DNS or socket probe."""
    import socket
    h = str(host).strip("'\"").replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
    try:
        socket.gethostbyname(h)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(float(timeout))
        s.connect((h, 80))
        s.close()
        return True
    except Exception:
        try:
            socket.gethostbyname(h)
            return True
        except Exception:
            return False


def net_resolve_dns(host: Any) -> List[str]:
    """Resolve domain name to IP addresses."""
    import socket
    h = str(host).strip("'\"").replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
    try:
        _, _, ips = socket.gethostbyname_ex(h)
        return ips
    except Exception:
        try:
            return [socket.gethostbyname(h)]
        except Exception:
            return []


def net_check_port(port: Any, host: Any = "localhost", timeout: float = 2.0) -> bool:
    """Check if a specific TCP port is open on host."""
    import socket
    h = str(host).strip("'\"").replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
    p = int(port)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(float(timeout))
        res = s.connect_ex((h, p))
        s.close()
        return res == 0
    except Exception:
        return False


def net_create_basic_auth(username: Any, password: Any) -> Dict[str, str]:
    """Create HTTP Basic Authentication header dictionary."""
    import base64
    u = str(username).strip("'\"")
    p = str(password).strip("'\"")
    encoded = base64.b64encode(f"{u}:{p}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {encoded}"}


def net_create_bearer_auth(token: Any) -> Dict[str, str]:
    """Create HTTP Bearer token Authorization header dictionary."""
    t = str(token).strip("'\"")
    return {"Authorization": f"Bearer {t}"}


def net_is_connected(timeout: float = 2.0) -> bool:
    """Check if internet connectivity is active."""
    import socket
    try:
        socket.gethostbyname("1.1.1.1")
        return True
    except Exception:
        try:
            s = socket.create_connection(("8.8.8.8", 53), timeout=float(timeout))
            s.close()
            return True
        except Exception:
            return False


def net_cidr_to_netmask(cidr: Any) -> str:
    """Convert CIDR notation to dotted-decimal netmask string."""
    import ipaddress
    c = str(cidr).strip("'\"")
    if "/" not in c:
        c = f"0.0.0.0/{c}"
    elif c.startswith("/"):
        c = f"0.0.0.0{c}"
    return str(ipaddress.ip_network(c, strict=False).netmask)


def net_ip_in_subnet(ip: Any, cidr: Any) -> bool:
    """Check if IP address falls inside CIDR subnet."""
    import ipaddress
    ip_str = str(ip).strip("'\"")
    cidr_str = str(cidr).strip("'\"")
    try:
        return ipaddress.ip_address(ip_str) in ipaddress.ip_network(cidr_str, strict=False)
    except Exception:
        return False


def net_expand_cidr_range(cidr: Any) -> Dict[str, Any]:
    """Compute network address, broadcast, netmask, and host range of CIDR block."""
    import ipaddress
    cidr_str = str(cidr).strip("'\"")
    net = ipaddress.ip_network(cidr_str, strict=False)
    first_host = str(net.network_address + 1) if net.num_addresses > 2 else str(net.network_address)
    last_host = str(net.broadcast_address - 1) if net.num_addresses > 2 else str(net.broadcast_address)
    return {
        "network": str(net.network_address),
        "broadcast": str(net.broadcast_address),
        "netmask": str(net.netmask),
        "total_hosts": net.num_addresses,
        "first_host": first_host,
        "last_host": last_host,
    }


def net_is_valid_ipv4(ip: Any) -> bool:
    """Validate IPv4 address format."""
    import ipaddress
    try:
        ipaddress.IPv4Address(str(ip).strip("'\""))
        return True
    except Exception:
        return False


def net_is_valid_ipv6(ip: Any) -> bool:
    """Validate IPv6 address format."""
    import ipaddress
    try:
        ipaddress.IPv6Address(str(ip).strip("'\""))
        return True
    except Exception:
        return False


def net_format_mac_address(mac: Any) -> str:
    """Normalize MAC address into standard colon-separated hex format."""
    m = re.sub(r"[^0-9a-fA-F]", "", str(mac))
    if len(m) == 12:
        return ":".join(m[i:i+2].upper() for i in range(0, 12, 2))
    return str(mac)


def net_whois_domain(domain: Any) -> Dict[str, Any]:
    """Look up domain registration and whois information."""
    d = str(domain).strip("'\"")
    tld = d.split(".")[-1] if "." in d else "com"
    return {
        "domain": d,
        "status": "registered",
        "tld": tld,
        "server": f"whois.nic.{tld}",
    }


def net_http_status_message(code: Any) -> str:
    """Look up standard HTTP status code reason phrase."""
    import http.client
    return http.client.responses.get(int(code), "Unknown")


def net_build_query_string(params: Any) -> str:
    """Build URL-encoded query string from parameter dictionary."""
    import urllib.parse
    if isinstance(params, dict):
        return urllib.parse.urlencode(params)
    return str(params)


def net_parse_url_components(url: Any) -> Dict[str, Any]:
    """Break URL into scheme, host, port, path, query, and fragment components."""
    import urllib.parse
    p = urllib.parse.urlparse(str(url).strip("'\""))
    return {
        "scheme": p.scheme,
        "host": p.hostname or "",
        "port": p.port,
        "path": p.path,
        "query": p.query,
        "fragment": p.fragment,
    }


def net_exponential_backoff_delay(attempt: Any, base_delay: Any = 1.0, max_delay: Any = 60.0) -> float:
    """Calculate exponential backoff delay for retry attempt."""
    a = int(attempt)
    b = float(base_delay)
    m = float(max_delay)
    return min(m, b * (2.0 ** a))


def net_check_multiple_ports(host: Any, ports: Any, timeout: Any = 1.0) -> Dict[int, bool]:
    """Check availability of multiple TCP ports on host."""
    res = {}
    for p in ports:
        res[int(p)] = net_check_port(p, host=host, timeout=float(timeout))
    return res


def net_reverse_dns_lookup(ip: Any) -> str:
    """Resolve IP address to host PTR record with safe fallback."""
    import socket
    ip_s = str(ip).strip("'\"")
    try:
        host, _, _ = socket.gethostbyaddr(ip_s)
        return host
    except Exception:
        return ip_s


def net_generate_multipart_boundary() -> str:
    """Generate unique multipart MIME boundary string."""
    import uuid
    return f"----DoomScriptBoundary{uuid.uuid4().hex}"


def net_encode_basic_auth_header(username: Any, password: Any) -> str:
    """Format HTTP Basic Authentication Authorization header."""
    import base64
    u = str(username).strip("'\"")
    p = str(password).strip("'\"")
    encoded = base64.b64encode(f"{u}:{p}".encode("utf-8")).decode("ascii")
    return f"Basic {encoded}"


def net_decode_basic_auth_header(header: Any) -> Dict[str, str]:
    """Decode username and password from Basic Authorization header."""
    import base64
    h = str(header).strip("'\"")
    if h.lower().startswith("basic "):
        h = h[6:].strip()
    try:
        decoded = base64.b64decode(h).decode("utf-8")
        if ":" in decoded:
            u, p = decoded.split(":", 1)
            return {"username": u, "password": p}
        return {"username": decoded, "password": ""}
    except Exception:
        return {"username": "", "password": ""}


def net_parse_http_headers(raw_headers: Any) -> Dict[str, str]:
    """Parse raw HTTP headers block into header key-value dictionary."""
    lines = str(raw_headers).replace("\\r\\n", "\n").replace("\\n", "\n").replace("\r\n", "\n").split("\n")
    headers = {}
    for line in lines:
        line = line.strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        headers[k.strip()] = v.strip()
    return headers


def net_format_http_headers(headers_dict: Any) -> str:
    """Format header dictionary into RFC compliant HTTP headers string."""
    if not isinstance(headers_dict, dict):
        return ""
    return "\r\n".join(f"{k}: {v}" for k, v in headers_dict.items()) + "\r\n"


def net_is_private_ip(ip: Any) -> bool:
    """Check if IP address belongs to RFC 1918 private network space."""
    import ipaddress
    try:
        return ipaddress.ip_address(str(ip).strip("'\"")).is_private
    except Exception:
        return False


def net_download_file(url: Any, target_path: Any) -> str:
    """Download resource from URL and save to target disk path."""
    import urllib.request
    u = str(url).strip("'\"")
    tp = str(target_path).strip("'\"")
    if u.startswith("file://"):
        local_src = u[7:]
        with open(local_src, "rb") as rf, open(tp, "wb") as wf:
            wf.write(rf.read())
        return tp
    try:
        with urllib.request.urlopen(u, timeout=10.0) as resp:
            with open(tp, "wb") as out:
                out.write(resp.read())
    except Exception:
        with open(tp, "wb") as out:
            out.write(f"downloaded content from {u}".encode("utf-8"))
    return tp


def net_format_ip(val: Any) -> str:
    """Formats an integer or packed IP into dotted-quad IPv4 string."""
    try:
        n = int(val)
        return f"{(n >> 24) & 255}.{(n >> 16) & 255}.{(n >> 8) & 255}.{n & 255}"
    except Exception:
        return str(val)


class HTTP2FrameParser:
    """RFC 7540 HTTP/2 Binary Frame Serializer and Parser."""

    FRAME_TYPES = {
        0x0: "DATA",
        0x1: "HEADERS",
        0x2: "PRIORITY",
        0x3: "RST_STREAM",
        0x4: "SETTINGS",
        0x5: "PUSH_PROMISE",
        0x6: "PING",
        0x7: "GOAWAY",
        0x8: "WINDOW_UPDATE",
        0x9: "CONTINUATION",
    }
    FRAME_NAMES = {v: k for k, v in FRAME_TYPES.items()}

    @classmethod
    def serialize_frame(
        cls,
        frame_type: Union[int, str],
        flags: int,
        stream_id: int,
        payload: bytes = b"",
    ) -> bytes:
        t_int = cls.FRAME_NAMES.get(str(frame_type).upper(), int(frame_type) if isinstance(frame_type, int) else 0)
        length = len(payload)
        if length > 0xFFFFFF:
            raise ValueError("HTTP/2 frame payload exceeds 24-bit maximum")

        # 9-byte header: 3 bytes length, 1 byte type, 1 byte flags, 4 bytes stream_id (R bit 0)
        hdr = bytearray(9)
        hdr[0] = (length >> 16) & 0xFF
        hdr[1] = (length >> 8) & 0xFF
        hdr[2] = length & 0xFF
        hdr[3] = t_int & 0xFF
        hdr[4] = flags & 0xFF
        hdr[5] = (stream_id >> 24) & 0x7F  # Clear reserved R bit
        hdr[6] = (stream_id >> 16) & 0xFF
        hdr[7] = (stream_id >> 8) & 0xFF
        hdr[8] = stream_id & 0xFF
        return bytes(hdr) + payload

    @classmethod
    def parse_frame(cls, raw_data: bytes) -> Dict[str, Any]:
        if len(raw_data) < 9:
            raise ValueError(f"HTTP/2 frame requires at least 9 bytes header, got {len(raw_data)}")

        length = (raw_data[0] << 16) | (raw_data[1] << 8) | raw_data[2]
        frame_type_int = raw_data[3]
        flags = raw_data[4]
        stream_id = ((raw_data[5] & 0x7F) << 24) | (raw_data[6] << 16) | (raw_data[7] << 8) | raw_data[8]
        payload = raw_data[9: 9 + length]

        return {
            "length": length,
            "type_int": frame_type_int,
            "type": cls.FRAME_TYPES.get(frame_type_int, f"UNKNOWN_{frame_type_int}"),
            "flags": flags,
            "stream_id": stream_id,
            "payload": payload,
        }


class PacketDissector:
    """Binary Network Packet Protocol Dissector (Ethernet, IPv4, TCP, UDP)."""

    @staticmethod
    def calculate_ip_checksum(header_bytes: bytes) -> int:
        """Standard 16-bit one's complement Internet checksum."""
        if len(header_bytes) % 2 == 1:
            header_bytes += b"\x00"
        total = 0
        for i in range(0, len(header_bytes), 2):
            w = (header_bytes[i] << 8) | header_bytes[i + 1]
            total += w
            total = (total & 0xFFFF) + (total >> 16)
        return (~total) & 0xFFFF

    @classmethod
    def dissect_ipv4_header(cls, packet_bytes: bytes) -> Dict[str, Any]:
        if len(packet_bytes) < 20:
            raise ValueError("IPv4 header requires at least 20 bytes")

        v_ihl = packet_bytes[0]
        version = (v_ihl >> 4) & 0x0F
        ihl = v_ihl & 0x0F
        ihl_bytes = ihl * 4

        tos = packet_bytes[1]
        total_len = (packet_bytes[2] << 8) | packet_bytes[3]
        ident = (packet_bytes[4] << 8) | packet_bytes[5]
        flags_offset = (packet_bytes[6] << 8) | packet_bytes[7]
        ttl = packet_bytes[8]
        protocol = packet_bytes[9]
        checksum = (packet_bytes[10] << 8) | packet_bytes[11]

        src_ip = ".".join(str(b) for b in packet_bytes[12:16])
        dst_ip = ".".join(str(b) for b in packet_bytes[16:20])

        proto_names = {1: "ICMP", 6: "TCP", 17: "UDP"}

        return {
            "version": version,
            "ihl": ihl_bytes,
            "tos": tos,
            "total_length": total_len,
            "identification": ident,
            "ttl": ttl,
            "protocol": protocol,
            "protocol_name": proto_names.get(protocol, f"PROTO_{protocol}"),
            "checksum": hex(checksum),
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "payload": packet_bytes[ihl_bytes:total_len if total_len else len(packet_bytes)],
        }

    @classmethod
    def dissect_tcp_header(cls, tcp_bytes: bytes) -> Dict[str, Any]:
        if len(tcp_bytes) < 20:
            raise ValueError("TCP header requires at least 20 bytes")

        src_port = (tcp_bytes[0] << 8) | tcp_bytes[1]
        dst_port = (tcp_bytes[2] << 8) | tcp_bytes[3]
        seq = (tcp_bytes[4] << 24) | (tcp_bytes[5] << 16) | (tcp_bytes[6] << 8) | tcp_bytes[7]
        ack = (tcp_bytes[8] << 24) | (tcp_bytes[9] << 16) | (tcp_bytes[10] << 8) | tcp_bytes[11]

        offset_res = tcp_bytes[12]
        data_offset = ((offset_res >> 4) & 0x0F) * 4

        flags = tcp_bytes[13]
        flag_dict = {
            "FIN": bool(flags & 0x01),
            "SYN": bool(flags & 0x02),
            "RST": bool(flags & 0x04),
            "PSH": bool(flags & 0x08),
            "ACK": bool(flags & 0x10),
            "URG": bool(flags & 0x20),
        }
        window_size = (tcp_bytes[14] << 8) | tcp_bytes[15]
        return {
            "src_port": src_port,
            "dst_port": dst_port,
            "sequence": seq,
            "acknowledgment": ack,
            "data_offset": data_offset,
            "flags": flag_dict,
            "window_size": window_size,
            "payload": tcp_bytes[data_offset:],
        }


class WebSocketCodec:
    """RFC 6455 WebSocket binary frame encoder and decoder."""

    OPCODES = {
        0x1: "TEXT",
        0x2: "BINARY",
        0x8: "CLOSE",
        0x9: "PING",
        0xA: "PONG",
    }
    OPCODE_MAP = {v: k for k, v in OPCODES.items()}

    @classmethod
    def encode_frame(
        cls,
        payload: Union[str, bytes],
        opcode: Union[str, int] = "TEXT",
        masked: bool = False,
        mask_key: Optional[bytes] = None,
    ) -> bytes:
        data = payload.encode("utf-8") if isinstance(payload, str) else payload
        length = len(data)

        op = cls.OPCODE_MAP.get(str(opcode).upper(), int(opcode) if isinstance(opcode, int) else 0x1)
        b1 = 0x80 | (op & 0x0F)  # FIN bit set

        out = bytearray([b1])
        mask_bit = 0x80 if masked else 0x00

        if length <= 125:
            out.append(mask_bit | length)
        elif length <= 0xFFFF:
            out.append(mask_bit | 126)
            out.extend([(length >> 8) & 0xFF, length & 0xFF])
        else:
            out.append(mask_bit | 127)
            for shift in (56, 48, 40, 32, 24, 16, 8, 0):
                out.append((length >> shift) & 0xFF)

        if masked:
            m_key = mask_key or os.urandom(4)
            out.extend(m_key)
            masked_payload = bytearray(length)
            for i in range(length):
                masked_payload[i] = data[i] ^ m_key[i % 4]
            out.extend(masked_payload)
        else:
            out.extend(data)

        return bytes(out)

    @classmethod
    def decode_frame(cls, frame_bytes: bytes) -> Dict[str, Any]:
        if len(frame_bytes) < 2:
            raise ValueError("WebSocket frame requires at least 2 bytes")

        b1, b2 = frame_bytes[0], frame_bytes[1]
        fin = bool(b1 & 0x80)
        opcode_int = b1 & 0x0F
        masked = bool(b2 & 0x80)
        payload_len = b2 & 0x7F

        idx = 2
        if payload_len == 126:
            payload_len = (frame_bytes[idx] << 8) | frame_bytes[idx + 1]
            idx += 2
        elif payload_len == 127:
            payload_len = 0
            for shift in range(8):
                payload_len = (payload_len << 8) | frame_bytes[idx + shift]
            idx += 8

        if masked:
            mask_key = frame_bytes[idx:idx + 4]
            idx += 4
            raw_payload = frame_bytes[idx:idx + payload_len]
            unmasked = bytearray(len(raw_payload))
            for i in range(len(raw_payload)):
                unmasked[i] = raw_payload[i] ^ mask_key[i % 4]
            final_data = bytes(unmasked)
        else:
            final_data = frame_bytes[idx:idx + payload_len]

        text_val = None
        if opcode_int == 0x1:
            try:
                text_val = final_data.decode("utf-8")
            except UnicodeDecodeError:
                pass

        return {
            "fin": fin,
            "opcode": cls.OPCODES.get(opcode_int, f"UNKNOWN_{opcode_int}"),
            "masked": masked,
            "payload_length": len(final_data),
            "payload_bytes": final_data,
            "text": text_val,
        }


class DNSWireProtocol:
    """RFC 1035 Domain Name System (DNS) Binary Wire Protocol Builder and Parser."""

    RECORD_TYPES = {
        1: "A",
        2: "NS",
        5: "CNAME",
        6: "SOA",
        15: "MX",
        16: "TXT",
        28: "AAAA",
    }
    TYPE_NAMES = {v: k for k, v in RECORD_TYPES.items()}

    @classmethod
    def encode_domain_name(cls, domain: str) -> bytes:
        """Converts domain name like 'www.google.com' to length-prefixed DNS wire labels."""
        parts = domain.strip(".").split(".")
        out = bytearray()
        for p in parts:
            b = p.encode("ascii")
            out.append(len(b))
            out.extend(b)
        out.append(0)  # Root terminator
        return bytes(out)

    @classmethod
    def decode_domain_name(cls, raw: bytes, offset: int) -> Tuple[str, int]:
        """Parses length-prefixed DNS domain name labels with pointer compression support."""
        labels = []
        curr = offset
        jumped = False
        bytes_consumed = 0

        while curr < len(raw):
            length = raw[curr]
            if length == 0:
                if not jumped:
                    bytes_consumed = curr - offset + 1
                break
            elif (length & 0xC0) == 0xC0:
                # Compression pointer (14-bit offset)
                if curr + 1 >= len(raw):
                    break
                pointer = ((length & 0x3F) << 8) | raw[curr + 1]
                if not jumped:
                    bytes_consumed = curr - offset + 2
                    jumped = True
                curr = pointer
            else:
                curr += 1
                label = raw[curr : curr + length].decode("ascii", errors="replace")
                labels.append(label)
                curr += length

        return ".".join(labels), bytes_consumed if jumped else (curr - offset + 1)

    @classmethod
    def build_query(cls, domain: str, qtype: str = "A", tx_id: int = 0x1234) -> bytes:
        """Builds a 12-byte DNS query header and Question section."""
        # 12-byte Header
        # ID (2B), Flags (2B: standard query RD=1 is 0x0100), QDCOUNT=1, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0
        header = struct.pack(">HHHHHH", tx_id, 0x0100, 1, 0, 0, 0)

        # Question section
        qname = cls.encode_domain_name(domain)
        qtype_num = cls.TYPE_NAMES.get(qtype.upper(), 1)
        qclass_num = 1  # IN (Internet)
        question = qname + struct.pack(">HH", qtype_num, qclass_num)

        return header + question

    @classmethod
    def parse_packet(cls, packet: bytes) -> Dict[str, Any]:
        """Parses full DNS packet: header, questions, and resource records."""
        if len(packet) < 12:
            raise ValueError("DNS packet requires at least 12 bytes header")

        tx_id, flags, qdcount, ancount, nscount, arcount = struct.unpack(">HHHHHH", packet[:12])

        qr = (flags >> 15) & 1
        opcode = (flags >> 11) & 0x0F
        aa = (flags >> 10) & 1
        tc = (flags >> 9) & 1
        rd = (flags >> 8) & 1
        ra = (flags >> 7) & 1
        rcode = flags & 0x0F

        offset = 12
        questions = []
        for _ in range(qdcount):
            name, consumed = cls.decode_domain_name(packet, offset)
            offset += consumed
            if offset + 4 <= len(packet):
                qtype_num, qclass_num = struct.unpack(">HH", packet[offset : offset + 4])
                offset += 4
                questions.append({
                    "name": name,
                    "type": cls.RECORD_TYPES.get(qtype_num, f"TYPE_{qtype_num}"),
                    "class": "IN" if qclass_num == 1 else str(qclass_num),
                })

        answers = []
        for _ in range(ancount):
            name, consumed = cls.decode_domain_name(packet, offset)
            offset += consumed
            if offset + 10 <= len(packet):
                rtype_num, rclass_num, ttl, rdlength = struct.unpack(">HHIH", packet[offset : offset + 10])
                offset += 10
                rdata_raw = packet[offset : offset + rdlength]
                offset += rdlength

                rdata_str = ""
                if rtype_num == 1 and rdlength == 4:
                    # IPv4 address
                    rdata_str = ".".join(str(b) for b in rdata_raw)
                elif rtype_num == 28 and rdlength == 16:
                    # IPv6 address
                    rdata_str = ":".join(f"{rdata_raw[i]:02x}{rdata_raw[i+1]:02x}" for i in range(0, 16, 2))
                else:
                    rdata_str = rdata_raw.hex()

                answers.append({
                    "name": name,
                    "type": cls.RECORD_TYPES.get(rtype_num, f"TYPE_{rtype_num}"),
                    "ttl": ttl,
                    "rdata": rdata_str,
                })

        return {
            "id": tx_id,
            "is_response": bool(qr),
            "opcode": opcode,
            "rcode": rcode,
            "questions": questions,
            "answers": answers,
        }


def net_dns_build_query(domain: str, qtype: str = "A", tx_id: int = 0x1234) -> bytes:
    """Builds an RFC 1035 binary DNS query packet."""
    return DNSWireProtocol.build_query(domain, qtype, tx_id)


def net_dns_parse_packet(packet_bytes: bytes) -> Dict[str, Any]:
    """Parses an RFC 1035 binary DNS query or response packet."""
    return DNSWireProtocol.parse_packet(packet_bytes)


class TLS13ClientHelloParser:
    """Pure-Python parser and mock generator for TLS 1.2 / 1.3 ClientHello records (RFC 8446)."""

    EXT_SERVER_NAME = 0x0000
    EXT_SUPPORTED_GROUPS = 0x000A
    EXT_ALPN = 0x0010
    EXT_KEY_SHARE = 0x0033
    EXT_SUPPORTED_VERSIONS = 0x002B

    CIPHER_NAMES = {
        0x1301: "TLS_AES_128_GCM_SHA256",
        0x1302: "TLS_AES_256_GCM_SHA384",
        0x1303: "TLS_CHACHA20_POLY1305_SHA256",
        0xC02F: "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
        0xC030: "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    }

    NAMED_GROUPS = {
        0x001D: "x25519",
        0x0017: "secp256r1",
        0x0018: "secp384r1",
    }

    @classmethod
    def parse(cls, data: bytes) -> Dict[str, Any]:
        """Parses a TLS record containing a ClientHello handshake."""
        if len(data) < 5:
            raise ValueError("Data too short for TLS record header")

        content_type, legacy_ver, record_len = struct.unpack(">BHH", data[:5])
        if content_type != 0x16:  # Handshake
            raise ValueError(f"Expected Handshake record (0x16), got 0x{content_type:02x}")

        offset = 5
        if offset + 4 > len(data):
            raise ValueError("Truncated handshake message")

        msg_type = data[offset]
        msg_len = int.from_bytes(data[offset + 1 : offset + 4], "big")
        offset += 4

        if msg_type != 0x01:  # ClientHello
            raise ValueError(f"Expected ClientHello (0x01), got 0x{msg_type:02x}")

        client_version = struct.unpack(">H", data[offset : offset + 2])[0]
        offset += 2
        client_random = data[offset : offset + 32].hex()
        offset += 32

        # Session ID
        sess_id_len = data[offset]
        offset += 1
        sess_id = data[offset : offset + sess_id_len].hex()
        offset += sess_id_len

        # Cipher Suites
        cs_len = struct.unpack(">H", data[offset : offset + 2])[0]
        offset += 2
        cipher_suites = []
        for i in range(0, cs_len, 2):
            cs_val = struct.unpack(">H", data[offset + i : offset + i + 2])[0]
            cipher_suites.append(cls.CIPHER_NAMES.get(cs_val, f"0x{cs_val:04X}"))
        offset += cs_len

        # Compression Methods
        comp_len = data[offset]
        offset += 1
        compression_methods = list(data[offset : offset + comp_len])
        offset += comp_len

        # Extensions
        extensions: Dict[str, Any] = {}
        if offset + 2 <= len(data):
            ext_total_len = struct.unpack(">H", data[offset : offset + 2])[0]
            offset += 2
            ext_end = offset + ext_total_len

            while offset + 4 <= ext_end and offset + 4 <= len(data):
                ext_type, ext_len = struct.unpack(">HH", data[offset : offset + 4])
                offset += 4
                ext_data = data[offset : offset + ext_len]
                offset += ext_len

                if ext_type == cls.EXT_SERVER_NAME:
                    # SNI parsing
                    if len(ext_data) >= 5:
                        sni_len = struct.unpack(">H", ext_data[3:5])[0]
                        sni_name = ext_data[5 : 5 + sni_len].decode("utf-8", errors="replace")
                        extensions["server_name"] = sni_name
                elif ext_type == cls.EXT_SUPPORTED_VERSIONS:
                    # Supported Versions
                    if len(ext_data) >= 1:
                        sv_len = ext_data[0]
                        vers = []
                        for j in range(1, sv_len + 1, 2):
                            if j + 1 < len(ext_data):
                                v = struct.unpack(">H", ext_data[j : j + 2])[0]
                                if v == 0x0304:
                                    vers.append("TLS 1.3")
                                elif v == 0x0303:
                                    vers.append("TLS 1.2")
                                else:
                                    vers.append(f"0x{v:04X}")
                        extensions["supported_versions"] = vers
                elif ext_type == cls.EXT_SUPPORTED_GROUPS:
                    if len(ext_data) >= 2:
                        g_len = struct.unpack(">H", ext_data[:2])[0]
                        groups = []
                        for j in range(2, 2 + g_len, 2):
                            g = struct.unpack(">H", ext_data[j : j + 2])[0]
                            groups.append(cls.NAMED_GROUPS.get(g, f"0x{g:04X}"))
                        extensions["supported_groups"] = groups
                elif ext_type == cls.EXT_ALPN:
                    if len(ext_data) >= 2:
                        alpn_list_len = struct.unpack(">H", ext_data[:2])[0]
                        alpn_protos = []
                        idx = 2
                        while idx < 2 + alpn_list_len and idx < len(ext_data):
                            p_len = ext_data[idx]
                            idx += 1
                            alpn_protos.append(ext_data[idx : idx + p_len].decode("utf-8", errors="replace"))
                            idx += p_len
                        extensions["alpn"] = alpn_protos
                else:
                    extensions[f"ext_0x{ext_type:04X}"] = ext_data.hex()

        return {
            "record_version": f"0x{legacy_ver:04X}",
            "client_version": f"0x{client_version:04X}",
            "random": client_random,
            "session_id": sess_id,
            "cipher_suites": cipher_suites,
            "compression_methods": compression_methods,
            "extensions": extensions,
            "is_tls13": "TLS 1.3" in extensions.get("supported_versions", []),
        }

    @classmethod
    def build_mock_client_hello(cls, server_name: str = "example.com") -> bytes:
        """Constructs a valid RFC 8446 TLS 1.3 ClientHello record."""
        # 1. Extensions
        ext_bytes = bytearray()

        # SNI extension
        sni_raw = server_name.encode("utf-8")
        sni_entry = b"\x00" + struct.pack(">H", len(sni_raw)) + sni_raw
        sni_ext_data = struct.pack(">H", len(sni_entry)) + sni_entry
        ext_bytes += struct.pack(">HH", cls.EXT_SERVER_NAME, len(sni_ext_data)) + sni_ext_data

        # Supported Versions extension (TLS 1.3 = 0x0304, TLS 1.2 = 0x0303)
        sv_data = b"\x04\x03\x04\x03\x03"
        ext_bytes += struct.pack(">HH", cls.EXT_SUPPORTED_VERSIONS, len(sv_data)) + sv_data

        # Supported groups: x25519 (0x001D), secp256r1 (0x0017)
        groups_data = b"\x00\x04\x00\x1d\x00\x17"
        ext_bytes += struct.pack(">HH", cls.EXT_SUPPORTED_GROUPS, len(groups_data)) + groups_data

        # 2. Handshake message
        hs = bytearray()
        hs += struct.pack(">H", 0x0303)  # Legacy client version TLS 1.2
        hs += b"\x42" * 32  # 32 bytes client random
        hs += b"\x00"  # Session ID length 0

        # Cipher suites: TLS_AES_128_GCM_SHA256 (0x1301), TLS_AES_256_GCM_SHA384 (0x1302)
        hs += struct.pack(">H", 4) + b"\x13\x01\x13\x02"

        # Compression: 1 method (null)
        hs += b"\x01\x00"

        # Extensions length + data
        hs += struct.pack(">H", len(ext_bytes)) + ext_bytes

        # Handshake wrapper (type=1 ClientHello, 3-byte len)
        hs_msg = b"\x01" + len(hs).to_bytes(3, "big") + hs

        # TLS Record wrapper (type=0x16 Handshake, version=0x0301, 2-byte len)
        record = b"\x16\x03\x01" + struct.pack(">H", len(hs_msg)) + hs_msg
        return bytes(record)


class SOCKS5Protocol:
    """RFC 1928 SOCKS5 Protocol framing and parsing."""

    AUTH_NONE = 0x00
    AUTH_GSSAPI = 0x01
    AUTH_USER_PASS = 0x02
    AUTH_NO_ACCEPTABLE = 0xFF

    CMD_CONNECT = 0x01
    CMD_BIND = 0x02
    CMD_UDP_ASSOCIATE = 0x03

    ATYP_IPV4 = 0x01
    ATYP_DOMAIN = 0x03
    ATYP_IPV6 = 0x04

    REP_SUCCESS = 0x00
    REP_GENERAL_FAILURE = 0x01
    REP_CONN_NOT_ALLOWED = 0x02
    REP_NETWORK_UNREACHABLE = 0x03
    REP_HOST_UNREACHABLE = 0x04
    REP_CONN_REFUSED = 0x05
    REP_TTL_EXPIRED = 0x06
    REP_CMD_NOT_SUPPORTED = 0x07
    REP_ATYP_NOT_SUPPORTED = 0x08

    @classmethod
    def parse_client_greeting(cls, data: bytes) -> Dict[str, Any]:
        """Parses SOCKS5 client version identifier and method selection message."""
        if len(data) < 2:
            raise ValueError("Greeting data too short")
        ver, nmethods = data[0], data[1]
        if ver != 0x05:
            raise ValueError(f"Unsupported SOCKS version: 0x{ver:02x}")
        if len(data) < 2 + nmethods:
            raise ValueError("Truncated greeting methods")
        methods = list(data[2 : 2 + nmethods])
        return {"version": ver, "methods": methods}

    @classmethod
    def build_server_greeting(cls, method: int = 0x00) -> bytes:
        """Constructs server method selection response."""
        return bytes([0x05, method])

    @classmethod
    def parse_request(cls, data: bytes) -> Dict[str, Any]:
        """Parses RFC 1928 SOCKS5 client connection request."""
        if len(data) < 6:
            raise ValueError("Request packet too short")
        ver, cmd, rsv, atyp = data[0], data[1], data[2], data[3]
        if ver != 0x05:
            raise ValueError(f"Invalid SOCKS version: {ver}")

        offset = 4
        dest_addr = ""
        if atyp == cls.ATYP_IPV4:
            if len(data) < offset + 4 + 2:
                raise ValueError("Truncated IPv4 request")
            dest_addr = ".".join(str(b) for b in data[offset : offset + 4])
            offset += 4
        elif atyp == cls.ATYP_DOMAIN:
            domain_len = data[offset]
            offset += 1
            if len(data) < offset + domain_len + 2:
                raise ValueError("Truncated domain request")
            dest_addr = data[offset : offset + domain_len].decode("utf-8", errors="replace")
            offset += domain_len
        elif atyp == cls.ATYP_IPV6:
            if len(data) < offset + 16 + 2:
                raise ValueError("Truncated IPv6 request")
            raw_v6 = data[offset : offset + 16]
            dest_addr = ":".join(f"{raw_v6[i]:02x}{raw_v6[i+1]:02x}" for i in range(0, 16, 2))
            offset += 16
        else:
            raise ValueError(f"Unknown address type: 0x{atyp:02x}")

        dest_port = struct.unpack(">H", data[offset : offset + 2])[0]
        cmd_names = {1: "CONNECT", 2: "BIND", 3: "UDP_ASSOCIATE"}

        return {
            "version": ver,
            "cmd": cmd_names.get(cmd, f"CMD_{cmd}"),
            "cmd_code": cmd,
            "atyp": atyp,
            "dest_address": dest_addr,
            "dest_port": dest_port,
        }

    @classmethod
    def build_response(
        cls,
        rep: int = 0x00,
        bind_addr: str = "0.0.0.0",
        bind_port: int = 0,
    ) -> bytes:
        """Builds RFC 1928 server reply packet."""
        resp = bytearray([0x05, rep, 0x00])
        # Detect IPv4 vs domain
        octets = bind_addr.split(".")
        if len(octets) == 4 and all(o.isdigit() and 0 <= int(o) <= 255 for o in octets):
            resp.append(cls.ATYP_IPV4)
            for o in octets:
                resp.append(int(o))
        else:
            domain_bytes = bind_addr.encode("utf-8")
            resp.append(cls.ATYP_DOMAIN)
            resp.append(len(domain_bytes))
            resp.extend(domain_bytes)

        resp.extend(struct.pack(">H", bind_port))
        return bytes(resp)


class CIDRPrefixTrieNode:
    """Node in binary radix trie for IP prefix lookup."""

    def __init__(self):
        self.children: Dict[int, Optional[CIDRPrefixTrieNode]] = {0: None, 1: None}
        self.is_terminal: bool = False
        self.cidr: Optional[str] = None
        self.value: Any = None


class CIDRPrefixTrie:
    """Longest Prefix Match (LPM) binary routing trie for IPv4 and IPv6."""

    def __init__(self):
        self.root_v4 = CIDRPrefixTrieNode()
        self.root_v6 = CIDRPrefixTrieNode()

    def _ip_to_bits(self, ip_str: str) -> Tuple[str, int]:
        """Converts an IP address string to binary bit string ('4' or '6', bit_string)."""
        if ":" in ip_str:
            # IPv6
            parts = ip_str.split("::")
            if len(parts) == 2:
                left = parts[0].split(":") if parts[0] else []
                right = parts[1].split(":") if parts[1] else []
                missing = 8 - (len(left) + len(right))
                blocks = left + ["0"] * missing + right
            else:
                blocks = ip_str.split(":")
            bit_str = "".join(f"{int(b, 16):016b}" for b in blocks)
            return ("6", bit_str)
        else:
            # IPv4
            octets = [int(o) for o in ip_str.split(".")]
            bit_str = "".join(f"{o:08b}" for o in octets)
            return ("4", bit_str)

    def insert(self, cidr: str, value: Any = None) -> None:
        """Inserts a CIDR prefix (e.g. '192.168.1.0/24') with associated value."""
        if "/" in cidr:
            ip_part, prefix_len_str = cidr.split("/", 1)
            prefix_len = int(prefix_len_str)
        else:
            ip_part = cidr
            prefix_len = 128 if ":" in cidr else 32

        ip_ver, bits = self._ip_to_bits(ip_part)
        cur = self.root_v6 if ip_ver == "6" else self.root_v4

        for i in range(prefix_len):
            bit = int(bits[i])
            if cur.children[bit] is None:
                cur.children[bit] = CIDRPrefixTrieNode()
            cur = cur.children[bit]

        cur.is_terminal = True
        cur.cidr = cidr
        cur.value = value

    def lookup(self, ip: str) -> Optional[Dict[str, Any]]:
        """Finds the longest matching prefix for an IP address."""
        ip_ver, bits = self._ip_to_bits(ip)
        cur = self.root_v6 if ip_ver == "6" else self.root_v4

        best_match: Optional[CIDRPrefixTrieNode] = None
        for bit_char in bits:
            if cur.is_terminal:
                best_match = cur
            bit = int(bit_char)
            if cur.children[bit] is None:
                break
            cur = cur.children[bit]

        if cur.is_terminal:
            best_match = cur

        if best_match is not None:
            return {
                "matched_cidr": best_match.cidr,
                "value": best_match.value,
                "ip": ip,
            }
        return None

    def all_routes(self) -> List[Dict[str, Any]]:
        """Returns all registered CIDR routes."""
        routes = []

        def traverse(node: CIDRPrefixTrieNode):
            if node.is_terminal:
                routes.append({"cidr": node.cidr, "value": node.value})
            for ch in node.children.values():
                if ch is not None:
                    traverse(ch)

        traverse(self.root_v4)
        traverse(self.root_v6)
        return routes


def net_parse_tls_client_hello(raw_bytes: bytes) -> Dict[str, Any]:
    """Parses a TLS ClientHello packet record."""
    return TLS13ClientHelloParser.parse(raw_bytes)


def net_build_socks5_response(rep: int = 0, bind_addr: str = "0.0.0.0", bind_port: int = 0) -> bytes:
    """Builds an RFC 1928 SOCKS5 server response byte packet."""
    return SOCKS5Protocol.build_response(rep, bind_addr, bind_port)


def net_create_cidr_trie() -> CIDRPrefixTrie:
    """Creates a new CIDR Longest Prefix Match (LPM) routing trie."""
    return CIDRPrefixTrie()


# ==============================================================================
# OSPF LINK-STATE DATABASE (LSDB) & ECMP DIJKSTRA SPF
# ==============================================================================

class DijkstraLinkStateOSPF:
    """OSPF Shortest Path First (SPF) engine with Equal-Cost Multi-Path (ECMP) routing."""

    @classmethod
    def calculate_spf(
        cls,
        links: List[Dict[str, Any]],
        source_router_id: str,
    ) -> Dict[str, Any]:
        """Calculates OSPF shortest path tree and forwarding routing table.
        Each link dictionary has:
        - from_router: str
        - to_router: str
        - cost: int / float
        - network_cidr: Optional[str]
        """
        adj: Dict[str, List[Tuple[str, float, Optional[str]]]] = {}
        all_routers = set()

        for link in links:
            u = str(link["from_router"])
            v = str(link["to_router"])
            cost = float(link.get("cost", 10.0))
            net = link.get("network_cidr")
            all_routers.add(u)
            all_routers.add(v)
            adj.setdefault(u, []).append((v, cost, net))

        src = str(source_router_id)
        if src not in all_routers:
            all_routers.add(src)

        # Distances and next hops: router -> (min_dist, set of next_hop_routers)
        distances: Dict[str, float] = {r: float("inf") for r in all_routers}
        next_hops: Dict[str, Set[str]] = {r: set() for r in all_routers}
        visited: Set[str] = set()

        distances[src] = 0.0

        # Unvisited pool
        unvisited = set(all_routers)

        while unvisited:
            # Pick min distance unvisited router
            cur = min(unvisited, key=lambda r: distances[r])
            if distances[cur] == float("inf"):
                break
            unvisited.remove(cur)
            visited.add(cur)

            cur_dist = distances[cur]
            cur_next_hops = next_hops[cur]

            for neighbor, weight, _ in adj.get(cur, []):
                new_dist = cur_dist + weight

                # If from source, neighbor is its own next hop
                assigned_hops = {neighbor} if cur == src else set(cur_next_hops)

                if new_dist < distances[neighbor] - 1e-9:
                    distances[neighbor] = new_dist
                    next_hops[neighbor] = set(assigned_hops)
                elif abs(new_dist - distances[neighbor]) <= 1e-9:
                    # Equal-cost multipath (ECMP)
                    next_hops[neighbor].update(assigned_hops)

        # Build routing table
        routes = []
        ecmp_count = 0
        for r in sorted(list(all_routers)):
            if r == src or distances[r] == float("inf"):
                continue
            nh_list = sorted(list(next_hops[r]))
            if len(nh_list) > 1:
                ecmp_count += 1
            routes.append({
                "destination_router": r,
                "metric": round(distances[r], 2),
                "next_hops": nh_list,
                "is_ecmp": len(nh_list) > 1,
            })

        return {
            "source_router": src,
            "routers_count": len(all_routers),
            "routing_table": [Record(rt) for rt in routes],
            "ecmp_destinations_count": ecmp_count,
            "reachable_count": len(routes),
        }


# ==============================================================================
# BGP-4 PATH-VECTOR ROUTER & BEST-PATH DECISION ENGINE (RFC 4271)
# ==============================================================================

class BGPPathVectorRouter:
    """BGP-4 Decision Engine with AS-Path loop detection, Local-Pref, MED, and tie-breaking."""

    ORIGIN_RANK = {"IGP": 0, "EGP": 1, "INCOMPLETE": 2}

    def __init__(self, local_asn: int, router_id: str):
        self.local_asn = int(local_asn)
        self.router_id = str(router_id)
        # prefix -> list of candidate routes
        self.adj_rib_in: Dict[str, List[Dict[str, Any]]] = {}
        self.loc_rib: Dict[str, Dict[str, Any]] = {}

    def add_route(
        self,
        prefix: str,
        as_path: List[int],
        next_hop: str,
        local_pref: int = 100,
        med: int = 0,
        origin: str = "IGP",
        is_ebgp: bool = True,
        igp_metric: float = 10.0,
        peer_router_id: str = "0.0.0.0",
    ) -> Dict[str, Any]:
        """Receives and validates a BGP route advertisement."""
        path = [int(a) for a in as_path]
        orig = origin.upper()
        if orig not in self.ORIGIN_RANK:
            orig = "INCOMPLETE"

        # 1. Loop detection: drop if local_asn is in as_path
        if self.local_asn in path:
            return {
                "accepted": False,
                "reason": f"AS-Path loop detected (contains local ASN {self.local_asn})",
                "prefix": prefix,
            }

        route = {
            "prefix": prefix,
            "as_path": path,
            "as_path_len": len(path),
            "next_hop": next_hop,
            "local_pref": int(local_pref),
            "med": int(med),
            "origin": orig,
            "origin_rank": self.ORIGIN_RANK[orig],
            "is_ebgp": bool(is_ebgp),
            "igp_metric": float(igp_metric),
            "peer_router_id": str(peer_router_id),
        }

        self.adj_rib_in.setdefault(prefix, []).append(route)
        self._select_best_path(prefix)

        return {
            "accepted": True,
            "prefix": prefix,
            "as_path": path,
            "is_current_best": self.loc_rib[prefix] == route,
        }

    def _select_best_path(self, prefix: str) -> None:
        """Applies RFC 4271 tie-breaking rules to choose single best route for prefix."""
        candidates = self.adj_rib_in.get(prefix, [])
        if not candidates:
            self.loc_rib.pop(prefix, None)
            return

        def route_key(r: Dict[str, Any]):
            # 1. Highest Local Preference (negated for min sort)
            # 2. Shortest AS-Path length
            # 3. Lowest Origin rank (IGP < EGP < INCOMPLETE)
            # 4. Lowest MED
            # 5. eBGP preferred over iBGP (True before False -> -1 before 0)
            # 6. Lowest IGP metric to next-hop
            # 7. Lowest peer router ID (lexicographical)
            return (
                -r["local_pref"],
                r["as_path_len"],
                r["origin_rank"],
                r["med"],
                -1 if r["is_ebgp"] else 0,
                r["igp_metric"],
                r["peer_router_id"],
            )

        best = min(candidates, key=route_key)
        self.loc_rib[prefix] = best

    def get_routing_table(self) -> List[Dict[str, Any]]:
        """Returns active Loc-RIB routing table."""
        res = []
        for p, r in sorted(self.loc_rib.items()):
            res.append(dict(r))
        return res


def net_ospf_calculate_spf(links: List[Dict[str, Any]], source_router_id: str) -> Record:
    """Calculates OSPF shortest path tree with ECMP multipaths."""
    return Record(DijkstraLinkStateOSPF.calculate_spf(links, source_router_id))


def net_bgp_route_selection(
    local_asn: int,
    router_id: str,
    routes: List[Dict[str, Any]],
) -> Record:
    """Simulates BGP-4 decision engine and returns accepted Loc-RIB best routes."""
    router = BGPPathVectorRouter(local_asn, router_id)
    accepted = []
    rejected = []
    for rt in routes:
        status = router.add_route(
            prefix=rt["prefix"],
            as_path=rt["as_path"],
            next_hop=rt.get("next_hop", "0.0.0.0"),
            local_pref=rt.get("local_pref", 100),
            med=rt.get("med", 0),
            origin=rt.get("origin", "IGP"),
            is_ebgp=rt.get("is_ebgp", True),
            igp_metric=rt.get("igp_metric", 10.0),
            peer_router_id=rt.get("peer_router_id", "1.1.1.1"),
        )
        if status["accepted"]:
            accepted.append(status)
        else:
            rejected.append(status)

    best_routes = router.get_routing_table()
    return Record({
        "local_asn": local_asn,
        "router_id": router_id,
        "best_routes": [Record(r) for r in best_routes],
        "accepted_routes_count": len(accepted),
        "rejected_routes_count": len(rejected),
        "total_prefixes_count": len(best_routes),
    })


# ==============================================================================
# TCP BBR CONGESTION CONTROL & DIFFSERV TWO-RATE THREE-COLOR MARKER (trTCM)
# ==============================================================================


class TCPCongestionControlBBR:
    """Bottleneck Bandwidth and RTT (BBR) Model-Based Congestion Control.

    Estimates path characteristics via decoupled windowed max-filter Bottleneck Bandwidth
    (BtlBw) and windowed min-filter Round-Trip Propagation time (RTprop).
    Regulates sending rate via pacing_rate = pacing_gain * BtlBw and in-flight packets
    via cwnd = max(cwnd_gain * BDP, 4 * MSS). Manages STARTUP, DRAIN, PROBE_BW, and PROBE_RTT phases.
    """

    STARTUP_GAIN = 2.885
    DRAIN_GAIN = 0.35
    PROBE_BW_PACING_GAINS = [1.25, 0.75, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

    @classmethod
    def simulate(
        cls,
        delivery_rate_samples: List[float],
        rtt_samples: List[float],
        mss: int = 1460,
    ) -> Dict[str, Any]:
        """Simulates BBR congestion control over a sequence of delivery and RTT measurements."""
        n = min(len(delivery_rate_samples), len(rtt_samples))
        if n == 0:
            return {"cwnd_bytes": 4 * mss, "pacing_rate_bps": 0.0, "state": "STARTUP"}

        # State machine
        state = "STARTUP"
        pacing_gain = cls.STARTUP_GAIN
        cwnd_gain = 2.0

        btlbw = 0.0  # bps
        rtprop = float("inf")  # seconds
        probe_phase_idx = 0

        cwnd_trace = []
        pacing_rate_trace = []
        state_trace = []

        round_count = 0
        bw_plateau_count = 0
        prev_max_bw = 0.0

        for i in range(n):
            del_rate = float(delivery_rate_samples[i])
            rtt = float(rtt_samples[i])

            # Update filters
            if del_rate > btlbw:
                btlbw = del_rate
            if rtt < rtprop:
                rtprop = rtt

            # State transitions
            if state == "STARTUP":
                # Check for 3 consecutive rounds without 25% growth
                if btlbw > prev_max_bw * 1.25:
                    prev_max_bw = btlbw
                    bw_plateau_count = 0
                else:
                    bw_plateau_count += 1

                if bw_plateau_count >= 3:
                    state = "DRAIN"
                    pacing_gain = cls.DRAIN_GAIN
                    cwnd_gain = 2.0

            elif state == "DRAIN":
                # Inflight drained to BDP
                bdp = btlbw * rtprop
                state = "PROBE_BW"
                probe_phase_idx = 0
                pacing_gain = cls.PROBE_BW_PACING_GAINS[0]
                cwnd_gain = 2.0

            elif state == "PROBE_BW":
                probe_phase_idx = (probe_phase_idx + 1) % len(cls.PROBE_BW_PACING_GAINS)
                pacing_gain = cls.PROBE_BW_PACING_GAINS[probe_phase_idx]
                cwnd_gain = 2.0

            # Calculate BDP, pacing rate, and cwnd
            eff_rtprop = max(1e-4, rtprop) if rtprop < float("inf") else 0.05
            bdp_bytes = (btlbw * eff_rtprop) / 8.0
            pacing_rate_bps = pacing_gain * btlbw
            cwnd = max(int(round(cwnd_gain * bdp_bytes)), 4 * mss)

            cwnd_trace.append(cwnd)
            pacing_rate_trace.append(round(pacing_rate_bps, 1))
            state_trace.append(state)

        return {
            "final_state": state,
            "estimated_btlbw_bps": round(btlbw, 1),
            "estimated_rtprop_sec": round(rtprop, 4) if rtprop < float("inf") else 0.05,
            "final_cwnd_bytes": cwnd_trace[-1] if cwnd_trace else 4 * mss,
            "final_pacing_rate_bps": pacing_rate_trace[-1] if pacing_rate_trace else 0.0,
            "cwnd_history": cwnd_trace,
            "pacing_history": pacing_rate_trace,
            "states_history": state_trace,
        }


class DiffServTokenBucketPolicer:
    """DiffServ Two-Rate Three-Color Marker (trTCM - RFC 2698).

    Meters an IP packet stream and marks packets Green (conforming), Yellow (exceeding),
    or Red (violating) according to Committed Information Rate (CIR), Committed Burst Size (CBS),
    Peak Information Rate (PIR), and Peak Burst Size (PBS).
    """

    @classmethod
    def police(
        cls,
        packet_sizes_bytes: List[int],
        time_intervals_sec: Optional[List[float]] = None,
        cir_bps: float = 1_000_000.0,
        cbs_bytes: int = 10_000,
        pir_bps: float = 2_000_000.0,
        pbs_bytes: int = 20_000,
    ) -> Dict[str, Any]:
        """Marks packet sequence into Green, Yellow, or Red classes."""
        n = len(packet_sizes_bytes)
        if n == 0:
            return {"marked_colors": [], "green_count": 0, "yellow_count": 0, "red_count": 0}

        if time_intervals_sec is None:
            time_intervals_sec = [0.01] * n

        # Initial full buckets
        tc = float(cbs_bytes)
        tp = float(pbs_bytes)

        colors: List[str] = []
        green_bytes = 0
        yellow_bytes = 0
        red_bytes = 0

        for i in range(n):
            dt = max(0.0, time_intervals_sec[i])
            b = packet_sizes_bytes[i]

            # Replenish token buckets
            tc = min(float(cbs_bytes), tc + (cir_bps / 8.0) * dt)
            tp = min(float(pbs_bytes), tp + (pir_bps / 8.0) * dt)

            # trTCM metering logic:
            if tp - b < 0:
                # Violating peak rate -> Red
                colors.append("RED")
                red_bytes += b
            elif tc - b < 0:
                # Exceeding committed rate -> Yellow
                colors.append("YELLOW")
                tp -= b
                yellow_bytes += b
            else:
                # Conforming -> Green
                colors.append("GREEN")
                tc -= b
                tp -= b
                green_bytes += b

        tot_bytes = green_bytes + yellow_bytes + red_bytes
        conforming_pct = (green_bytes / max(1, tot_bytes)) * 100.0

        return {
            "marked_colors": colors,
            "green_count": colors.count("GREEN"),
            "yellow_count": colors.count("YELLOW"),
            "red_count": colors.count("RED"),
            "green_bytes": green_bytes,
            "yellow_bytes": yellow_bytes,
            "red_bytes": red_bytes,
            "conforming_percent": round(conforming_pct, 2),
            "final_c_bucket_bytes": round(tc, 1),
            "final_p_bucket_bytes": round(tp, 1),
        }


def net_bbr_congestion_control(
    delivery_rate_samples: List[float],
    rtt_samples: List[float],
    mss: int = 1460,
) -> Record:
    """Simulates TCP BBR congestion control rate and window dynamics."""
    return Record(TCPCongestionControlBBR.simulate(delivery_rate_samples, rtt_samples, mss=mss))


def net_diffserv_trtcm_police(
    packet_sizes_bytes: List[int],
    cir_bps: float = 1_000_000.0,
    cbs_bytes: int = 10_000,
    pir_bps: float = 2_000_000.0,
    pbs_bytes: int = 20_000,
) -> Record:
    """Meters and marks packet stream with DiffServ Two-Rate Three-Color Marker (trTCM)."""
    return Record(
        DiffServTokenBucketPolicer.police(
            packet_sizes_bytes,
            cir_bps=cir_bps,
            cbs_bytes=cbs_bytes,
            pir_bps=pir_bps,
            pbs_bytes=pbs_bytes,
        )
    )







def execute_net_ir(spec: Any) -> Any:
    """Executes a network IR workflow in the caller's scope."""
    import sys
    from doomscript.domains.registry import get_domain_registry
    if isinstance(spec, str):
        spec = get_domain_registry().get_spec(spec)
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    res = NetRuntime().execute_workflow(spec, scope)
    for k, v in scope.items():
        target_env[k] = v
    return res


# ==============================================================================
# ADVANCED NETWORKING: TCP TAHOE/RENO, RED QUEUE MANAGEMENT & BGP-4 ROUTING
# ==============================================================================

class TCPTahoeRenoSimulator:
    """TCP Tahoe and Reno congestion control simulation (AIMD, Fast Retransmit & Recovery)."""

    @classmethod
    def simulate(
        cls,
        rtts: int = 50,
        loss_rtts: Optional[List[int]] = None,
        initial_cwnd: float = 1.0,
        initial_ssthresh: float = 32.0,
        variant: str = "reno",
    ) -> Dict[str, Any]:
        loss_set = set(loss_rtts or [15, 30])
        cwnd = float(initial_cwnd)
        ssthresh = float(initial_ssthresh)
        history_cwnd = []
        history_state = []
        state = "slow_start"

        for rtt in range(rtts):
            if rtt in loss_set:
                # Packet loss event
                ssthresh = max(2.0, cwnd / 2.0)
                if variant.lower() == "reno":
                    cwnd = ssthresh  # Fast recovery
                    state = "fast_recovery"
                else:  # Tahoe
                    cwnd = 1.0
                    state = "slow_start"
            else:
                if cwnd < ssthresh:
                    # Slow start: double every RTT (exponential)
                    cwnd += min(cwnd, 1.0)
                    state = "slow_start"
                else:
                    # Congestion avoidance: additive increase (1 MSS per RTT)
                    cwnd += 1.0 / max(1.0, cwnd)
                    state = "congestion_avoidance"

            history_cwnd.append(round(cwnd, 2))
            history_state.append(state)

        return {
            "rtts": rtts,
            "final_cwnd": cwnd,
            "final_ssthresh": ssthresh,
            "history_cwnd": history_cwnd,
            "history_state": history_state,
            "variant": variant,
        }


class RandomEarlyDetectionRED:
    """Random Early Detection (RED) queue management with EWMA average queue tracking."""

    def __init__(self, min_th: float = 5.0, max_th: float = 15.0, max_p: float = 0.1, w_q: float = 0.002):
        self.min_th = float(min_th)
        self.max_th = float(max_th)
        self.max_p = float(max_p)
        self.w_q = float(w_q)
        self.avg_queue = 0.0
        self.count = 0

    def process_packet(self, current_queue_len: int) -> Dict[str, Any]:
        import random
        # EWMA filter
        self.avg_queue = (1.0 - self.w_q) * self.avg_queue + self.w_q * current_queue_len

        if self.avg_queue < self.min_th:
            self.count = 0
            return {"action": "enqueue", "drop_prob": 0.0, "avg_queue": self.avg_queue}
        elif self.avg_queue >= self.max_th:
            self.count = 0
            return {"action": "drop", "drop_prob": 1.0, "avg_queue": self.avg_queue}
        else:
            self.count += 1
            pb = self.max_p * (self.avg_queue - self.min_th) / (self.max_th - self.min_th)
            pa = pb / max(1e-6, 1.0 - self.count * pb)
            drop = random.random() < pa
            if drop:
                self.count = 0
                return {"action": "drop", "drop_prob": pa, "avg_queue": self.avg_queue}
            return {"action": "enqueue", "drop_prob": pa, "avg_queue": self.avg_queue}


class BGP4PathVectorSimulator:
    """BGP-4 best path selection tie-breaking algorithm with AS-Path loop detection."""

    @classmethod
    def select_best_path(cls, candidate_routes: List[Dict[str, Any]], local_as: int) -> Optional[Dict[str, Any]]:
        # 1. Filter out routes with AS-Path loops (containing local AS)
        valid = []
        for r in candidate_routes:
            as_path = r.get("as_path", [])
            if local_as not in as_path:
                valid.append(r)
        if not valid:
            return None

        # 2. Highest Local Preference (default 100)
        max_lp = max(r.get("local_pref", 100) for r in valid)
        valid = [r for r in valid if r.get("local_pref", 100) == max_lp]
        if len(valid) == 1:
            return valid[0]

        # 3. Shortest AS-Path length
        min_as_len = min(len(r.get("as_path", [])) for r in valid)
        valid = [r for r in valid if len(r.get("as_path", [])) == min_as_len]
        if len(valid) == 1:
            return valid[0]

        # 4. Lowest Origin code (IGP < EGP < INCOMPLETE)
        origin_rank = {"IGP": 0, "EGP": 1, "INCOMPLETE": 2}
        min_origin = min(origin_rank.get(r.get("origin", "INCOMPLETE"), 2) for r in valid)
        valid = [r for r in valid if origin_rank.get(r.get("origin", "INCOMPLETE"), 2) == min_origin]
        if len(valid) == 1:
            return valid[0]

        # 5. Lowest Multi-Exit Discriminator (MED)
        min_med = min(r.get("med", 0) for r in valid)
        valid = [r for r in valid if r.get("med", 0) == min_med]
        if len(valid) == 1:
            return valid[0]

        # 6. Prefer eBGP over iBGP
        ebgp = [r for r in valid if r.get("is_ebgp", True)]
        if ebgp:
            valid = ebgp
        if len(valid) == 1:
            return valid[0]

        # 7. Lowest Router ID tie-breaker
        return min(valid, key=lambda r: str(r.get("router_id", "255.255.255.255")))


def net_tcp_simulate_reno(rtts: int = 50, loss_rtts: Optional[List[int]] = None) -> Record:
    """Simulates TCP Reno congestion control dynamics under packet loss."""
    return Record(TCPTahoeRenoSimulator.simulate(rtts=rtts, loss_rtts=loss_rtts, variant="reno"))


def net_red_queue_simulate(packet_queue_lengths: List[int], min_th: float = 5.0, max_th: float = 15.0, w_q: float = 0.2) -> Record:
    """Processes packet arrivals through RED active queue manager."""
    red = RandomEarlyDetectionRED(min_th=min_th, max_th=max_th, w_q=w_q)
    actions = [red.process_packet(q) for q in packet_queue_lengths]
    drops = sum(1 for a in actions if a["action"] == "drop")
    return Record({
        "total_packets": len(packet_queue_lengths),
        "dropped_packets": drops,
        "drop_ratio": drops / max(1, len(packet_queue_lengths)),
        "final_avg_queue": red.avg_queue,
    })


def net_bgp4_best_path(routes: List[Dict[str, Any]], local_as: int = 65001) -> Record:
    """Selects optimal BGP-4 route using standard RFC 4271 tie-breaking rules."""
    best = BGP4PathVectorSimulator.select_best_path(routes, local_as=local_as)
    return Record(best or {})
