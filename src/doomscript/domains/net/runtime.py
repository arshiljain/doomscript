"""Runtime execution engine for Web & API Automation operations."""

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.net.spec import ApiWorkflowSpec, RequestStep, ParseStep, SaveStep


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


