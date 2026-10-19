"""Independent Domain Parser for Cloud & Object Storage domain."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.cloud.spec import (
    CloudConnectSpec,
    CloudUploadSpec,
    CloudDownloadSpec,
    CloudListSpec,
    CloudSignedUrlSpec,
)


class CloudDomainParser(DomainParser):
    """Independent parser for Cloud & Object Storage syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # list all files in [bucket] <b_var> [matching <pat>] into <target>
        m_list = re.match(
            r"^list\s+all\s+files\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)(?:\s+matching\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_list:
            b_var = m_list.group(1).strip()
            pat = m_list.group(2).strip() if m_list.group(2) else '""'
            target = m_list.group(3).strip()
            return f"set {target} to list_cloud_files({b_var}, pattern={pat})"

        # generate signed url for <remote> in [bucket] <b_var> [with expiry <sec> seconds] into <target>
        m_url = re.match(
            r"^generate\s+signed\s+url\s+for\s+(.+?)\s+in\s+(?:bucket\s+)?([A-Za-z_]\w*)(?:\s+with\s+expiry\s+(\d+)\s+seconds?)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_url:
            remote_expr = m_url.group(1).strip()
            b_var = m_url.group(2).strip()
            expiry = m_url.group(3).strip() if m_url.group(3) else "3600"
            target = m_url.group(4).strip()
            return f"set {target} to generate_cloud_signed_url({b_var}, {remote_expr}, expiry={expiry})"

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # connect to bucket <name> (as|into) <target>
        m_conn = re.match(
            r"^connect\s+to\s+bucket\s+(.+?)\s+(?:as|into)\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_conn:
            b_name = m_conn.group(1).strip()
            target = m_conn.group(2).strip()
            return f"set {target} to connect_to_bucket({b_name})"

        # upload file <local> to [bucket] <b_var> as <remote>
        m_up = re.match(
            r"^upload\s+file\s+(.+?)\s+to\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+as\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_up:
            local_expr = m_up.group(1).strip()
            b_var = m_up.group(2).strip()
            remote_expr = m_up.group(3).strip()
            return f"upload_cloud_file({b_var}, {local_expr}, {remote_expr})"

        # download file <remote> from [bucket] <b_var> to <local>
        m_down = re.match(
            r"^download\s+file\s+(.+?)\s+from\s+(?:bucket\s+)?([A-Za-z_]\w*)\s+to\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_down:
            remote_expr = m_down.group(1).strip()
            b_var = m_down.group(2).strip()
            local_expr = m_down.group(3).strip()
            return f"download_cloud_file({b_var}, {remote_expr}, {local_expr})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Cloud domain does not currently define declarative blocks")
