"""Independent Domain Parser for Web & API Automation language constructs."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.net.spec import ApiWorkflowSpec, RequestStep, ParseStep, SaveStep


class NetDomainParser(DomainParser):
    """Independent parser for Web & API Automation syntax (requests, retries, json parsing, api blocks)."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        # inspect response <resp> [into <target>]
        m = re.match(
            r"^inspect\s+response\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m:
            resp_var = m.group(1)
            target = m.group(2) or "response_inspection"
            return f"set {target} to inspect_response({resp_var})"

        # status of <resp> into <target>
        m2 = re.match(
            r"^status\s+of\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m2:
            resp_var = m2.group(1)
            target = m2.group(2) or f"{resp_var}_status"
            return f"set {target} to {resp_var}.status_code"

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        # request (GET|POST|PUT|DELETE|PATCH) "<url>" [with headers <headers>] [with json <body>] into <target>
        req_m = re.match(
            r"^request\s+(GET|POST|PUT|DELETE|PATCH)\s+([\"'][^\"']+[\"']|[A-Za-z_]\w*)(?:\s+with\s+headers\s+([^\s]+))?(?:\s+with\s+json\s+(.+?))?(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if req_m:
            method = req_m.group(1).upper()
            url_expr = req_m.group(2)
            headers_expr = req_m.group(3) or "{}"
            body_expr = req_m.group(4) or "nothing"
            target = req_m.group(5) or "response"
            return f'set {target} to execute_http_request("{method}", {url_expr}, headers={headers_expr}, body={body_expr})'

        # parse <resp> as JSON into <target>
        parse_m = re.match(
            r"^parse\s+([A-Za-z_]\w*)\s+as\s+(JSON|text)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if parse_m:
            src = parse_m.group(1)
            fmt = parse_m.group(2).lower()
            target = parse_m.group(3)
            return f'set {target} to parse_response_content({src}, format_type="{fmt}")'

        # save (response|resp) to "<path>"
        save_m = re.match(
            r"^save\s+(response|resp)\s+to\s+([\"'][^\"']+[\"'])$",
            line.strip(),
            re.IGNORECASE,
        )
        if save_m:
            src = save_m.group(1)
            path = save_m.group(2)
            return f"save_response_content({src}, {path})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[ApiWorkflowSpec, str]:
        # api "<name>":
        m = re.match(
            r"^api\s+[\"']([^\"']+)[\"']:?$",
            header.strip(),
            re.IGNORECASE,
        )
        if not m:
            raise SyntaxError(f"Invalid API workflow header: {header}")

        api_name = m.group(1)
        spec = ApiWorkflowSpec(name=api_name, target_var=api_name)

        for l_no, raw_line in body_lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # base_url: "<url>"
            b_m = re.match(r"^base_url\s*:\s*[\"']([^\"']+)[\"']", line, re.IGNORECASE)
            if b_m:
                spec.base_url = b_m.group(1)
                continue

            # timeout: <n> seconds
            t_m = re.match(r"^timeout\s*:\s*(\d+(?:\.\d+)?)\s*(?:seconds|s)?", line, re.IGNORECASE)
            if t_m:
                spec.timeout = float(t_m.group(1))
                continue

            # retries: <n> times
            r_m = re.match(r"^retries\s*:\s*(\d+)", line, re.IGNORECASE)
            if r_m:
                spec.retries = int(r_m.group(1))
                continue

            # get|post|put|delete "<endpoint>" into <target>
            verb_m = re.match(
                r"^(get|post|put|delete|patch)\s+[\"']([^\"']+)[\"'](?:\s+with\s+json\s+(.+?))?(?:\s+into\s+([A-Za-z_]\w*))?$",
                line,
                re.IGNORECASE,
            )
            if verb_m:
                method = verb_m.group(1).upper()
                endpoint = verb_m.group(2)
                body_expr = verb_m.group(3)
                target = verb_m.group(4) or "response"
                body_val = None
                if body_expr:
                    try:
                        body_val = eval(body_expr, {}, {})
                    except Exception:
                        body_val = body_expr
                spec.steps.append(RequestStep(method=method, url_or_endpoint=endpoint, body=body_val, target=target))
                continue

            # parse <resp> as JSON into <target>
            p_m = re.match(r"^parse\s+([A-Za-z_]\w*)\s+as\s+(JSON|text)\s+into\s+([A-Za-z_]\w*)$", line, re.IGNORECASE)
            if p_m:
                spec.steps.append(ParseStep(source_resp=p_m.group(1), format=p_m.group(2).lower(), target=p_m.group(3)))
                continue

            # save <resp> to "<path>"
            s_m = re.match(r"^save\s+([A-Za-z_]\w*)\s+to\s+[\"']([^\"']+)[\"']$", line, re.IGNORECASE)
            if s_m:
                spec.steps.append(SaveStep(source_resp=s_m.group(1), path=s_m.group(2)))
                continue

        errors = spec.validate()
        if errors:
            raise SyntaxError(f"API workflow validation error for '{api_name}': {'; '.join(errors)}")

        return spec, api_name
