"""Independent Domain Parser for Web Scraping & Document Extraction domain."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.web.spec import (
    WebPageSpec,
    WebExtractLinksSpec,
    WebExtractTableSpec,
    WebExtractTextSpec,
    WebDownloadMediaSpec,
)


class WebDomainParser(DomainParser):
    """Independent parser for Web Scraping & Document Extraction syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # title of [webpage|page] <page_var> into <target>
        m_title = re.match(
            r"^title\s+of\s+(?:webpage\s+|page\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_title:
            p_var = m_title.group(1).strip()
            target = m_title.group(2).strip()
            return f"set {target} to webpage_title({p_var})"

        # text in [webpage|page] <page_var> into <target>
        m_txt = re.match(
            r"^text\s+in\s+(?:webpage\s+|page\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_txt:
            p_var = m_txt.group(1).strip()
            target = m_txt.group(2).strip()
            return f"set {target} to webpage_text({p_var})"

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # open webpage / scrape webpage <url_or_html> into <target>
        m_open = re.match(
            r"^(?:open|scrape)\s+webpage\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_open:
            url_expr = m_open.group(1).strip()
            target = m_open.group(2).strip()
            return f"set {target} to open_webpage({url_expr})"

        # parse html <html_expr> into <target>
        m_parse = re.match(
            r"^parse\s+html\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_parse:
            html_expr = m_parse.group(1).strip()
            target = m_parse.group(2).strip()
            return f"set {target} to parse_html({html_expr})"

        # extract [all] links (from|in) [webpage|page] <page_var> [where class is <class>] into <target>
        m_links = re.match(
            r"^extract\s+(?:all\s+)?links\s+(?:from|in)\s+(?:webpage\s+|page\s+)?([A-Za-z_]\w*)(?:\s+where\s+class\s+is\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_links:
            p_var = m_links.group(1).strip()
            filter_cls = m_links.group(2).strip() if m_links.group(2) else "None"
            target = m_links.group(3).strip()
            return f"set {target} to extract_web_links({p_var}, filter_class={filter_cls})"

        # find table (with header|containing) <hdr> in [webpage|page] <page_var> into <target>
        m_tbl_hdr = re.match(
            r"^find\s+table\s+(?:with\s+header|containing)\s+(.+?)\s+in\s+(?:webpage\s+|page\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tbl_hdr:
            hdr_expr = m_tbl_hdr.group(1).strip()
            p_var = m_tbl_hdr.group(2).strip()
            target = m_tbl_hdr.group(3).strip()
            return f"set {target} to extract_web_table({p_var}, header_contains={hdr_expr})"

        # find table <index> in [webpage|page] <page_var> into <target>
        m_tbl_idx = re.match(
            r"^find\s+table\s+(\d+)\s+in\s+(?:webpage\s+|page\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tbl_idx:
            idx = m_tbl_idx.group(1).strip()
            p_var = m_tbl_idx.group(2).strip()
            target = m_tbl_idx.group(3).strip()
            return f"set {target} to extract_web_table({p_var}, index={idx})"

        # download all (images|media) matching <pat> from [webpage|page] <page_var> to folder <folder> into <target>
        m_dl = re.match(
            r"^download\s+all\s+(?:images|media)\s+matching\s+(.+?)\s+from\s+(?:webpage\s+|page\s+)?([A-Za-z_]\w*)\s+to\s+folder\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dl:
            pat_expr = m_dl.group(1).strip()
            p_var = m_dl.group(2).strip()
            folder_expr = m_dl.group(3).strip()
            target = m_dl.group(4).strip()
            return f"set {target} to download_web_media({p_var}, pattern={pat_expr}, folder={folder_expr})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Web domain does not currently define declarative blocks")
