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
        # allow / block mutating network requests
        if re.match(r"^allow\s+mutating\s+(?:network\s+)?requests$", line.strip(), re.IGNORECASE):
            return "set_mutating_requests_allowed(True)"
        if re.match(r"^(?:block|disallow)\s+mutating\s+(?:network\s+)?requests$", line.strip(), re.IGNORECASE):
            return "set_mutating_requests_allowed(False)"

        # request (GET|POST|PUT|DELETE|PATCH) <url> ... OR directly (GET|POST|PUT|DELETE|PATCH) <url> ...
        line_clean = line.strip()
        req_match = re.match(
            r"^request\s+(GET|POST|PUT|DELETE|PATCH)\s+([\"'][^\"']+[\"']|[A-Za-z_]\w*)(.*)$",
            line_clean,
            re.IGNORECASE,
        )
        if not req_match:
            req_match = re.match(
                r"^(GET|POST|PUT|DELETE|PATCH)\s+([\"'][^\"']+[\"']|https?://\S+|url\b)(.*)$",
                line_clean,
                re.IGNORECASE,
            )
        if req_match:
            method = req_match.group(1).upper()
            url_expr = req_match.group(2)
            rest = req_match.group(3).strip()

            target = "response"
            into_m = re.search(r"(?:^|\s+)into\s+([A-Za-z_]\w*)$", rest, re.IGNORECASE)
            if into_m:
                target = into_m.group(1)
                rest = rest[:into_m.start()].strip()

            timeout_expr = "10.0"
            to_m = re.search(r"with\s+timeout\s+(\d+(?:\.\d+)?)\s*(?:seconds|second|s)?", rest, re.IGNORECASE)
            if to_m:
                timeout_expr = to_m.group(1)
                rest = (rest[:to_m.start()] + " " + rest[to_m.end():]).strip()

            retries_expr = "0"
            ret_m = re.search(r"retry\s+(\d+)\s+times?", rest, re.IGNORECASE)
            if ret_m:
                retries_expr = ret_m.group(1)
                rest = (rest[:ret_m.start()] + " " + rest[ret_m.end():]).strip()

            bearer_token = None
            bt_m = re.search(r"with\s+bearer\s+token\s+([\"'][^\"']+[\"']|[A-Za-z_]\w*)", rest, re.IGNORECASE)
            if bt_m:
                bearer_token = bt_m.group(1)
                rest = (rest[:bt_m.start()] + " " + rest[bt_m.end():]).strip()

            headers_expr = None
            h_m = re.search(r"with\s+headers\s+([^\s]+)", rest, re.IGNORECASE)
            if h_m:
                headers_expr = h_m.group(1)
                rest = (rest[:h_m.start()] + " " + rest[h_m.end():]).strip()

            body_expr = "None"
            b_m = re.search(r"with\s+json\s+(.+)$", rest, re.IGNORECASE)
            if b_m:
                body_expr = b_m.group(1).strip()

            if bearer_token:
                if headers_expr:
                    headers_arg = f"dict({headers_expr}, **{{'Authorization': 'Bearer ' + {bearer_token}}})"
                else:
                    headers_arg = f"{{'Authorization': 'Bearer ' + {bearer_token}}}"
            elif headers_expr:
                headers_arg = headers_expr
            else:
                headers_arg = "{}"

            return (
                f'set {target} to execute_http_request("{method}", {url_expr}, '
                f'headers={headers_arg}, body={body_expr}, timeout={timeout_expr}, retries={retries_expr})'
            )

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

        # format ip <ip> into <target>
        fip_m = re.match(
            r"^format\s+ip\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if fip_m:
            ip_val = fip_m.group(1).strip()
            target = fip_m.group(2).strip()
            return f"set {target} to net_format_ip({ip_val})"

        # ping host <host> [with timeout <to>] into <target>
        ping_m = re.match(
            r"^ping\s+host\s+(.+?)(?:\s+with\s+timeout\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if ping_m:
            host = ping_m.group(1).strip()
            to = ping_m.group(2)
            target = ping_m.group(3).strip()
            to_arg = f", timeout={to.strip()}" if to else ""
            return f"set {target} to net_ping_host({host}{to_arg})"

        # resolve dns [for|of] <host> into <target>
        dns_m = re.match(
            r"^resolve\s+dns(?:\s+(?:for|of))?\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if dns_m:
            host, target = dns_m.group(1).strip(), dns_m.group(2).strip()
            return f"set {target} to net_resolve_dns({host})"

        # check port <port> on [host] <host> [with timeout <to>] into <target>
        port_m = re.match(
            r"^check\s+port\s+(.+?)\s+on\s+(?:host\s+)?(.+?)(?:\s+with\s+timeout\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if port_m:
            p, host, to, target = port_m.group(1).strip(), port_m.group(2).strip(), port_m.group(3), port_m.group(4).strip()
            to_arg = f", timeout={to.strip()}" if to else ""
            return f"set {target} to net_check_port({p}, host={host}{to_arg})"

        # create basic auth header for <user> with <pass> into <target>
        bauth_m = re.match(
            r"^create\s+basic\s+auth\s+header\s+for\s+(.+?)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if bauth_m:
            u, p, target = bauth_m.group(1).strip(), bauth_m.group(2).strip(), bauth_m.group(3).strip()
            return f"set {target} to net_create_basic_auth({u}, {p})"

        # create bearer auth header with token <tok> into <target>
        tok_m = re.match(
            r"^create\s+bearer\s+auth\s+header\s+(?:with|for)\s+(?:token\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if tok_m:
            tok, target = tok_m.group(1).strip(), tok_m.group(2).strip()
            return f"set {target} to net_create_bearer_auth({tok})"

        # check [internet] connectivity into <target>
        conn_m = re.match(
            r"^check\s+(?:internet\s+)?connectivity\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if conn_m:
            target = conn_m.group(1).strip()
            return f"set {target} to net_is_connected()"

        # convert cidr <cidr> to netmask into <target>
        m_c2m = re.match(
            r"^(?:convert\s+)?cidr\s+(.+?)\s+to\s+netmask\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_c2m:
            cidr, target = m_c2m.group(1).strip(), m_c2m.group(2).strip()
            return f"set {target} to net_cidr_to_netmask({cidr})"

        # check if ip <ip> in subnet <cidr> into <target>
        m_insub = re.match(
            r"^(?:check\s+if\s+|is\s+)?ip\s+(.+?)\s+in\s+subnet\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_insub:
            ip, cidr, target = m_insub.group(1).strip(), m_insub.group(2).strip(), m_insub.group(3).strip()
            return f"set {target} to net_ip_in_subnet({ip}, {cidr})"

        # expand cidr|subnet <cidr> into <target>
        m_expc = re.match(
            r"^expand\s+(?:cidr|subnet)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_expc:
            cidr, target = m_expc.group(1).strip(), m_expc.group(2).strip()
            return f"set {target} to net_expand_cidr_range({cidr})"

        # validate ipv4 <ip> into <target>
        m_v4 = re.match(
            r"^(?:validate|is\s+valid)\s+ipv4\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_v4:
            ip, target = m_v4.group(1).strip(), m_v4.group(2).strip()
            return f"set {target} to net_is_valid_ipv4({ip})"

        # validate ipv6 <ip> into <target>
        m_v6 = re.match(
            r"^(?:validate|is\s+valid)\s+ipv6\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_v6:
            ip, target = m_v6.group(1).strip(), m_v6.group(2).strip()
            return f"set {target} to net_is_valid_ipv6({ip})"

        # normalize|format mac address <mac> into <target>
        m_mac = re.match(
            r"^(?:normalize|format)\s+mac\s+address\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_mac:
            mac, target = m_mac.group(1).strip(), m_mac.group(2).strip()
            return f"set {target} to net_format_mac_address({mac})"

        # whois lookup|domain <domain> into <target>
        m_who = re.match(
            r"^whois\s+(?:lookup|domain)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_who:
            dom, target = m_who.group(1).strip(), m_who.group(2).strip()
            return f"set {target} to net_whois_domain({dom})"

        # http status message|text for <code> into <target>
        m_hmsg = re.match(
            r"^http\s+status\s+(?:message|text)\s+for\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_hmsg:
            code, target = m_hmsg.group(1).strip(), m_hmsg.group(2).strip()
            return f"set {target} to net_http_status_message({code})"

        # build query string from <params> into <target>
        m_bqs = re.match(
            r"^build\s+query\s+string\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bqs:
            params, target = m_bqs.group(1).strip(), m_bqs.group(2).strip()
            return f"set {target} to net_build_query_string({params})"

        # parse url [components] <url> into <target>
        m_purl = re.match(
            r"^parse\s+url(?:\s+components)?\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_purl:
            url, target = m_purl.group(1).strip(), m_purl.group(2).strip()
            return f"set {target} to net_parse_url_components({url})"

        # calculate backoff delay for attempt <att> [base <base>] [max <max>] into <target>
        m_boff = re.match(
            r"^calculate\s+backoff\s+delay\s+for\s+attempt\s+(.+?)(?:\s+base\s+(.+?))?(?:\s+max\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_boff:
            att = m_boff.group(1).strip()
            base = m_boff.group(2)
            max_d = m_boff.group(3)
            target = m_boff.group(4).strip()
            b_val = base.strip() if base else "1.0"
            m_val = max_d.strip() if max_d else "60.0"
            return f"set {target} to net_exponential_backoff_delay({att}, {b_val}, {m_val})"

        # scan ports <ports> on host <host> [with timeout <to>] into <target>
        m_scnp = re.match(
            r"^scan\s+ports\s+(.+?)\s+on\s+host\s+(.+?)(?:\s+with\s+timeout\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_scnp:
            ports, host, to, target = m_scnp.group(1).strip(), m_scnp.group(2).strip(), m_scnp.group(3), m_scnp.group(4).strip()
            to_val = to.strip() if to else "1.0"
            return f"set {target} to net_check_multiple_ports({host}, {ports}, {to_val})"

        # reverse dns lookup <ip> into <target>
        m_rdns = re.match(
            r"^reverse\s+dns\s+lookup\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_rdns:
            ip, target = m_rdns.group(1).strip(), m_rdns.group(2).strip()
            return f"set {target} to net_reverse_dns_lookup({ip})"

        # generate multipart boundary into <target>
        m_bnd = re.match(
            r"^generate\s+multipart\s+boundary\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bnd:
            target = m_bnd.group(1).strip()
            return f"set {target} to net_generate_multipart_boundary()"

        # encode basic auth header user <user> password <pw> into <target>
        m_ebauth = re.match(
            r"^encode\s+basic\s+auth\s+header\s+user\s+(.+?)\s+password\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_ebauth:
            user, pw, target = m_ebauth.group(1).strip(), m_ebauth.group(2).strip(), m_ebauth.group(3).strip()
            return f"set {target} to net_encode_basic_auth_header({user}, {pw})"

        # decode basic auth header <hdr> into <target>
        m_dbauth = re.match(
            r"^decode\s+basic\s+auth\s+header\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_dbauth:
            hdr, target = m_dbauth.group(1).strip(), m_dbauth.group(2).strip()
            return f"set {target} to net_decode_basic_auth_header({hdr})"

        # parse raw http headers <raw> into <target>
        m_phdr = re.match(
            r"^parse\s+raw\s+http\s+headers\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_phdr:
            raw, target = m_phdr.group(1).strip(), m_phdr.group(2).strip()
            return f"set {target} to net_parse_http_headers({raw})"

        # format http headers <dict> into <target>
        m_fhdr = re.match(
            r"^format\s+http\s+headers\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_fhdr:
            hdict, target = m_fhdr.group(1).strip(), m_fhdr.group(2).strip()
            return f"set {target} to net_format_http_headers({hdict})"

        # check if private ip <ip> into <target>
        m_priv = re.match(
            r"^(?:check\s+if\s+|is\s+)?private\s+ip\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_priv:
            ip, target = m_priv.group(1).strip(), m_priv.group(2).strip()
            return f"set {target} to net_is_private_ip({ip})"

        # download file from <url> to <path> [into <target>]
        m_dl = re.match(
            r"^download\s+file\s+from\s+(.+?)\s+to\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_dl:
            url, path, target = m_dl.group(1).strip(), m_dl.group(2).strip(), m_dl.group(3)
            call = f"net_download_file({url}, {path})"
            return f"set {target} to {call}" if target else call

        # calculate ospf spf links <links> source <src> into <target>
        m_ospf = re.match(
            r"^calculate\s+ospf\s+spf\s+links\s+(.+?)\s+source\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_ospf:
            links, src, target = m_ospf.group(1).strip(), m_ospf.group(2).strip(), m_ospf.group(3).strip()
            return f"set {target} to net_ospf_calculate_spf({links}, {src})"

        # select bgp routes local_asn <asn> router_id <id> routes <routes> into <target>
        m_bgp = re.match(
            r"^select\s+bgp\s+routes\s+local_asn\s+(.+?)\s+router_id\s+(.+?)\s+routes\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bgp:
            asn, rid, rts, target = m_bgp.group(1).strip(), m_bgp.group(2).strip(), m_bgp.group(3).strip(), m_bgp.group(4).strip()
            return f"set {target} to net_bgp_route_selection({asn}, {rid}, {rts})"

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

            # [request] get|post|put|delete "<endpoint>" into <target>
            verb_m = re.match(
                r"^(?:request\s+)?(get|post|put|delete|patch)\s+[\"']([^\"']+)[\"'](?:\s+with\s+json\s+(.+?))?(?:\s+into\s+([A-Za-z_]\w*))?$",
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
