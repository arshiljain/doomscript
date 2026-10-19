"""Runtime execution engine for Web & API Automation operations."""

import json
import os
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
