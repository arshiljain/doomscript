"""Runtime execution engine for Web Scraping & Document Extraction domain."""

from typing import Any, Dict, List, Optional, Tuple, Union
import json
import re
import os
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from doomscript.runtime import Record
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.web.spec import (
    WebPageSpec,
    WebExtractLinksSpec,
    WebExtractTableSpec,
    WebExtractTextSpec,
    WebDownloadMediaSpec,
)

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


class SimpleHTMLTextParser(HTMLParser):
    """Fallback standard-library HTML parser for text and link extraction."""

    def __init__(self):
        super().__init__()
        self.text_parts: List[str] = []
        self.links: List[Dict[str, str]] = []
        self.title: str = ""
        self._in_title = False
        self._in_script = False
        self._cur_link: Optional[Dict[str, str]] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = dict(attrs)
        tag_lower = tag.lower()
        if tag_lower in ("script", "style", "noscript"):
            self._in_script = True
        elif tag_lower == "title":
            self._in_title = True
        elif tag_lower == "a":
            href = attr_dict.get("href", "")
            cls = attr_dict.get("class", "")
            self._cur_link = {"url": href, "text": "", "class": cls}

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if tag_lower in ("script", "style", "noscript"):
            self._in_script = False
        elif tag_lower == "title":
            self._in_title = False
        elif tag_lower == "a" and self._cur_link:
            self.links.append(self._cur_link)
            self._cur_link = None

    def handle_data(self, data: str):
        if self._in_script:
            return
        if self._in_title:
            self.title += data.strip()
        cleaned = data.strip()
        if cleaned:
            self.text_parts.append(cleaned)
            if self._cur_link:
                self._cur_link["text"] += cleaned


class WebPage:
    """Represents a loaded or scraped HTML webpage."""

    def __init__(self, html: str, url: str = "", status_code: int = 200):
        self.html = html
        self.url = url
        self.status_code = status_code

    @property
    def title(self) -> str:
        if HAS_BS4:
            soup = BeautifulSoup(self.html, "html.parser")
            tag = soup.find("title")
            return tag.get_text().strip() if tag else ""
        parser = SimpleHTMLTextParser()
        parser.feed(self.html)
        return parser.title

    @property
    def text(self) -> str:
        if HAS_BS4:
            soup = BeautifulSoup(self.html, "html.parser")
            for s in soup(["script", "style", "noscript"]):
                s.decompose()
            return re.sub(r"\s+", " ", soup.get_text()).strip()
        parser = SimpleHTMLTextParser()
        parser.feed(self.html)
        return " ".join(parser.text_parts)

    def extract_links(self, filter_class: Optional[str] = None) -> List[Dict[str, str]]:
        """Extracts hyperlinks, optionally filtering by CSS class."""
        if HAS_BS4:
            soup = BeautifulSoup(self.html, "html.parser")
            links = []
            for a in soup.find_all("a", href=True):
                classes = a.get("class", [])
                class_str = " ".join(classes) if isinstance(classes, list) else str(classes)
                if filter_class:
                    if filter_class.lower() not in class_str.lower():
                        continue
                href = a["href"]
                if self.url and not href.startswith(("http://", "https://", "mailto:", "#")):
                    href = urllib.parse.urljoin(self.url, href)
                links.append(
                    {
                        "url": href,
                        "text": a.get_text().strip(),
                        "class": class_str,
                    }
                )
            return links

        parser = SimpleHTMLTextParser()
        parser.feed(self.html)
        res = []
        for l in parser.links:
            if filter_class and filter_class.lower() not in l.get("class", "").lower():
                continue
            res.append(l)
        return res

    def extract_tables(self) -> List[List[Record]]:
        """Extracts all HTML tables into lists of structured Records."""
        tables_res = []
        if HAS_BS4:
            soup = BeautifulSoup(self.html, "html.parser")
            for t in soup.find_all("table"):
                headers = []
                for th in t.find_all("th"):
                    headers.append(th.get_text().strip())

                rows = []
                for tr in t.find_all("tr"):
                    cells = [td.get_text().strip() for td in tr.find_all("td")]
                    if not cells:
                        continue
                    if headers and len(cells) == len(headers):
                        rec_dict = {}
                        for h, val in zip(headers, cells):
                            try:
                                num = float(val) if "." in val else int(val)
                                rec_dict[h] = num
                            except ValueError:
                                rec_dict[h] = val
                        rows.append(Record(rec_dict))
                    else:
                        rows.append(Record({f"col_{i}": c for i, c in enumerate(cells)}))
                if rows:
                    tables_res.append(rows)
            return tables_res

        # Fallback regex table parser
        table_matches = re.findall(r"<table.*?>(.*?)</table>", self.html, re.DOTALL | re.IGNORECASE)
        for tbl in table_matches:
            th_matches = re.findall(r"<th.*?>(.*?)</th>", tbl, re.DOTALL | re.IGNORECASE)
            headers = [re.sub(r"<.*?>", "", th).strip() for th in th_matches]
            tr_matches = re.findall(r"<tr.*?>(.*?)</tr>", tbl, re.DOTALL | re.IGNORECASE)
            rows = []
            for tr in tr_matches:
                tds = re.findall(r"<td.*?>(.*?)</td>", tr, re.DOTALL | re.IGNORECASE)
                cells = [re.sub(r"<.*?>", "", td).strip() for td in tds]
                if cells:
                    if headers and len(cells) == len(headers):
                        rows.append(Record(dict(zip(headers, cells))))
                    else:
                        rows.append(Record({f"col_{i}": c for i, c in enumerate(cells)}))
            if rows:
                tables_res.append(rows)
        return tables_res

    def extract_table(
        self,
        header_contains: Optional[str] = None,
        index: int = 0,
    ) -> List[Record]:
        """Extracts a specific table by matching header text or by table index."""
        tables = self.extract_tables()
        if not tables:
            return []
        if header_contains:
            target_hdr = header_contains.lower()
            for tbl in tables:
                if tbl and any(target_hdr in str(k).lower() for k in tbl[0].keys()):
                    return tbl
        if 0 <= index < len(tables):
            return tables[index]
        return tables[0]

    def download_media(self, pattern: str = "*.png", folder: str = "./downloads") -> List[str]:
        """Finds media links matching pattern and saves them locally."""
        os.makedirs(folder, exist_ok=True)
        pat_clean = pattern.replace("*", "").lower()
        if HAS_BS4:
            soup = BeautifulSoup(self.html, "html.parser")
            srcs = [img["src"] for img in soup.find_all("img", src=True)]
        else:
            srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', self.html, re.IGNORECASE)

        saved = []
        for src in srcs:
            if not pat_clean or pat_clean in src.lower():
                full_url = urllib.parse.urljoin(self.url, src) if self.url else src
                fname = os.path.basename(urllib.parse.urlparse(full_url).path) or f"media_{len(saved)}.dat"
                dest_path = os.path.join(folder, fname)
                try:
                    if full_url.startswith(("http://", "https://")):
                        req = urllib.request.Request(full_url, headers={"User-Agent": "DoomScript/1.0"})
                        with urllib.request.urlopen(req, timeout=10) as resp, open(dest_path, "wb") as f:
                            f.write(resp.read())
                    else:
                        with open(dest_path, "wb") as f:
                            f.write(b"LOCAL_MEDIA_PLACEHOLDER")
                    saved.append(dest_path)
                except Exception:
                    pass
        return saved

    def __repr__(self) -> str:
        return f"WebPage(title='{self.title}', url='{self.url}', status={self.status_code})"


# Standalone Helper Functions
def open_webpage(url_or_html: str) -> WebPage:
    """Loads a webpage from a remote URL or parses local HTML source directly."""
    if url_or_html.strip().startswith(("http://", "https://")):
        req = urllib.request.Request(url_or_html, headers={"User-Agent": "DoomScript/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            status = resp.status
            return WebPage(html=content, url=url_or_html, status_code=status)
    return WebPage(html=url_or_html, url="")


def parse_html(html: str, url: str = "") -> WebPage:
    return WebPage(html=html, url=url)


def webpage_title(page: WebPage) -> str:
    return page.title


def webpage_text(page: WebPage) -> str:
    return page.text


def extract_web_links(page: WebPage, filter_class: Optional[str] = None) -> List[Dict[str, str]]:
    return page.extract_links(filter_class=filter_class)


def extract_web_table(
    page: WebPage,
    header_contains: Optional[str] = None,
    index: int = 0,
) -> List[Record]:
    return page.extract_table(header_contains=header_contains, index=index)


def download_web_media(page: WebPage, pattern: str = "*.png", folder: str = "./downloads") -> List[str]:
    return page.download_media(pattern=pattern, folder=folder)


class WebRuntime(DomainRuntime):
    """Runtime execution engine for Web Scraping specifications."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        errors = ir.validate()
        if errors:
            raise ValueError(f"Web spec validation failed: {'; '.join(errors)}")

        if isinstance(ir, WebPageSpec):
            url_or_src = scope.get(ir.url_expr, ir.url_expr)
            return open_webpage(str(url_or_src))
        elif isinstance(ir, WebExtractLinksSpec):
            page = scope.get(ir.page_var)
            return extract_web_links(page, filter_class=ir.filter_class)
        elif isinstance(ir, WebExtractTableSpec):
            page = scope.get(ir.page_var)
            return extract_web_table(page, header_contains=ir.header_contains, index=ir.index)
        elif isinstance(ir, WebExtractTextSpec):
            page = scope.get(ir.page_var)
            return webpage_text(page)
        elif isinstance(ir, WebDownloadMediaSpec):
            page = scope.get(ir.page_var)
            folder = scope.get(ir.folder_expr, ir.folder_expr)
            return download_web_media(page, pattern=ir.pattern, folder=str(folder))

        raise NotImplementedError(f"Unsupported IR: {type(ir)}")


def execute_web_ir(spec_id: str) -> Any:
    from doomscript.domains.registry import get_domain_registry
    spec = get_domain_registry().get_spec(spec_id)
    if spec is None:
        raise KeyError(f"Web spec not found: {spec_id}")
    return WebRuntime().execute_ir(spec, {})


# --- Batch 9 Spoken English Web Verbs ---

def web_select_all(html_or_page: Any, selector: Any) -> List[str]:
    """CSS selector extraction returning inner text of all matches."""
    html = html_or_page.html if isinstance(html_or_page, WebPage) else str(html_or_page)
    sel_str = str(selector).strip("'\"")
    if HAS_BS4:
        soup = BeautifulSoup(html, "html.parser")
        return [el.get_text().strip() for el in soup.select(sel_str)]
    # Lightweight regex fallback
    if sel_str.startswith("."):
        cls = sel_str[1:]
        return [re.sub(r"<[^>]+>", "", m).strip() for m in re.findall(rf'class="[^"]*{cls}[^"]*"[^>]*>(.*?)<', html, re.DOTALL)]
    tag = sel_str.lstrip("#.")
    return [re.sub(r"<[^>]+>", "", m).strip() for m in re.findall(rf'<{tag}[^>]*>(.*?)</{tag}>', html, re.DOTALL | re.IGNORECASE)]


def web_extract_tables(html_or_page: Any) -> List[List[Dict[str, Any]]]:
    """Extract all HTML tables into structured record lists."""
    html = html_or_page.html if isinstance(html_or_page, WebPage) else str(html_or_page)
    tables = []
    # Find all table blocks
    table_blocks = re.findall(r"<table[^>]*>(.*?)</table>", html, re.DOTALL | re.IGNORECASE)
    for tbl in table_blocks:
        headers = [re.sub(r"<[^>]+>", "", th).strip() for th in re.findall(r"<th[^>]*>(.*?)</th>", tbl, re.DOTALL | re.IGNORECASE)]
        row_blocks = re.findall(r"<tr[^>]*>(.*?)</tr>", tbl, re.DOTALL | re.IGNORECASE)
        records = []
        for r_block in row_blocks:
            cells = [re.sub(r"<[^>]+>", "", td).strip() for td in re.findall(r"<td[^>]*>(.*?)</td>", r_block, re.DOTALL | re.IGNORECASE)]
            if cells:
                if headers and len(cells) == len(headers):
                    records.append({headers[i]: cells[i] for i in range(len(headers))})
                else:
                    records.append({f"col_{i}": cells[i] for i in range(len(cells))})
        if records:
            tables.append(records)
    return tables[0] if len(tables) == 1 else tables


def web_parse_query_params(url: Any) -> Dict[str, Any]:
    """Parse URL query parameters into dictionary."""
    u = urllib.parse.urlparse(str(url).strip("'\""))
    qs = urllib.parse.parse_qs(u.query)
    return {k: v[0] if len(v) == 1 else v for k, v in qs.items()}


def web_build_url(base: Any, params: Any) -> str:
    """Build URL string with encoded parameters dictionary."""
    base_str = str(base).strip("'\"")
    if isinstance(params, dict):
        qs = urllib.parse.urlencode(params)
        sep = "&" if "?" in base_str else "?"
        return f"{base_str}{sep}{qs}"
    return base_str


def web_strip_tags(text: Any) -> str:
    """Strip all HTML tags from markup text."""
    return re.sub(r"<[^>]+>", "", str(text)).strip()


def web_extract_meta_tags(html_or_page: Any) -> Dict[str, str]:
    """Extract document meta tags (name/property -> content)."""
    html = html_or_page.html if isinstance(html_or_page, WebPage) else str(html_or_page)
    meta_dict = {}
    matches = re.findall(r'<meta\s+[^>]*(?:name|property)=["\']([^"\']+)["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
    for name, content in matches:
        meta_dict[name] = content
    # Also inverted order content=... name=...
    inv_matches = re.findall(r'<meta\s+[^>]*content=["\']([^"\']*)["\'][^>]*(?:name|property)=["\']([^"\']+)["\']', html, re.IGNORECASE)
    for content, name in inv_matches:
        meta_dict[name] = content
    return meta_dict


def web_response_is_successful(resp: Any) -> bool:
    """Check if HTTP response indicates success (2xx)."""
    if isinstance(resp, dict):
        status = resp.get("status", resp.get("status_code", 200))
    elif hasattr(resp, "status_code"):
        status = resp.status_code
    elif isinstance(resp, (int, float)):
        status = int(resp)
    else:
        status = 200
    return 200 <= status < 300


# --- 350-Expansion 20 Web Operations ---

def _unwrap_html(html_or_page: Any) -> str:
    if isinstance(html_or_page, WebPage):
        return html_or_page.html
    return str(html_or_page)


def web_extract_images(html_or_page: Any) -> List[Dict[str, str]]:
    """Find all image tags and return list of dicts with src and alt."""
    html = _unwrap_html(html_or_page)
    imgs = []
    for m in re.finditer(r'<img\s+([^>]*?)>', html, re.IGNORECASE):
        attrs = m.group(1)
        src_m = re.search(r'src=["\']([^"\']+)["\']', attrs, re.IGNORECASE)
        alt_m = re.search(r'alt=["\']([^"\']*)["\']', attrs, re.IGNORECASE)
        if src_m:
            imgs.append({"src": src_m.group(1), "alt": alt_m.group(1) if alt_m else ""})
    return imgs


def web_extract_forms(html_or_page: Any) -> List[Dict[str, Any]]:
    """Extract form tags, actions, methods, and input controls."""
    html = _unwrap_html(html_or_page)
    forms = []
    form_matches = re.finditer(r'<form\s*([^>]*)>(.*?)</form>', html, re.DOTALL | re.IGNORECASE)
    for fm in form_matches:
        f_attrs = fm.group(1)
        body = fm.group(2)
        act_m = re.search(r'action=["\']([^"\']*)["\']', f_attrs, re.IGNORECASE)
        meth_m = re.search(r'method=["\']([^"\']*)["\']', f_attrs, re.IGNORECASE)
        action = act_m.group(1) if act_m else ""
        method = meth_m.group(1).upper() if meth_m else "GET"
        inputs = []
        for inp in re.finditer(r'<input\s+([^>]*?)>', body, re.IGNORECASE):
            attrs = inp.group(1)
            nm = re.search(r'name=["\']([^"\']*)["\']', attrs, re.IGNORECASE)
            tm = re.search(r'type=["\']([^"\']*)["\']', attrs, re.IGNORECASE)
            vm = re.search(r'value=["\']([^"\']*)["\']', attrs, re.IGNORECASE)
            if nm:
                inputs.append({
                    "name": nm.group(1),
                    "type": tm.group(1).lower() if tm else "text",
                    "value": vm.group(1) if vm else "",
                })
        forms.append({"action": action, "method": method, "inputs": inputs})
    return forms


def web_encode_form_data(params: Dict[str, Any]) -> str:
    """URL-encode dictionary into application/x-www-form-urlencoded."""
    return urllib.parse.urlencode(params)


def web_decode_form_data(query_str: str) -> Dict[str, Any]:
    """Parse URL-encoded form data into dictionary."""
    s = str(query_str).lstrip("?")
    parsed = urllib.parse.parse_qs(s)
    return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}


def web_parse_sitemap_xml(sitemap_xml: str) -> List[str]:
    """Extract all <loc> entries from an XML sitemap."""
    matches = re.findall(r'<loc\b[^>]*>(.*?)</loc>', str(sitemap_xml), re.DOTALL | re.IGNORECASE)
    return [m.strip() for m in matches if m.strip()]


def web_parse_robots_txt(robots_txt: str, user_agent: str = "*", path: str = "/") -> bool:
    """Evaluate whether path is allowed under robots.txt for user agent."""
    lines = str(robots_txt).replace("\\n", "\n").replace("\\r", "\r").splitlines()
    target_ua = user_agent.lower()
    current_ua = None
    disallowed = []
    allowed = []
    for line in lines:
        line = line.split("#")[0].strip()
        if not line:
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            k = key.strip().lower()
            v = val.strip()
            if k == "user-agent":
                current_ua = v.lower()
            elif current_ua in (target_ua, "*"):
                if k == "disallow":
                    if v:
                        disallowed.append(v)
                elif k == "allow":
                    if v:
                        allowed.append(v)
    # Check allow rules first
    for a in allowed:
        if path.startswith(a):
            return True
    for d in disallowed:
        if path.startswith(d):
            return False
    return True


def web_canonicalize_url(base_url: str, relative_url: str) -> str:
    """Resolve relative link against a base URL."""
    return urllib.parse.urljoin(str(base_url), str(relative_url))


def web_extract_meta_description(html_or_page: Any) -> str:
    """Extract <meta name="description" content="..."> text."""
    html = _unwrap_html(html_or_page)
    m = re.search(r'<meta\s+[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
    if not m:
        m = re.search(r'<meta\s+[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']', html, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def web_extract_headings(html_or_page: Any) -> List[Dict[str, str]]:
    """Extract hierarchical list of all h1-h6 headings."""
    html = _unwrap_html(html_or_page)
    headings = []
    for m in re.finditer(r'<(h[1-6])\b[^>]*>(.*?)</\1>', html, re.DOTALL | re.IGNORECASE):
        tag = m.group(1).lower()
        text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        headings.append({"level": tag, "text": text})
    return headings


def web_check_ssl_expiry(domain: str) -> int:
    """Query TLS socket and return days until certificate expiration."""
    import ssl
    import socket
    from datetime import datetime, timezone
    host = str(domain).strip().split("/")[0].split(":")[0]
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
            s.settimeout(3.0)
            s.connect((host, 443))
            cert = s.getpeercert()
            if cert and "notAfter" in cert:
                expire_date = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                delta = expire_date - datetime.now(timezone.utc).replace(tzinfo=None)
                return max(0, delta.days)
    except Exception:
        pass
    return -1


def web_parse_cookie_header(header_str: str) -> Dict[str, str]:
    """Parse HTTP Cookie or Set-Cookie header into key-value pairs."""
    cookies = {}
    parts = str(header_str).split(";")
    for p in parts:
        p = p.strip()
        if "=" in p:
            k, v = p.split("=", 1)
            cookies[k.strip()] = v.strip()
    return cookies


def web_build_cookie_header(cookies_dict: Dict[str, Any]) -> str:
    """Format dictionary into standard Cookie header value."""
    return "; ".join(f"{k}={v}" for k, v in cookies_dict.items())


def web_extract_json_ld(html_or_page: Any) -> List[Any]:
    """Extract and parse all JSON-LD schemas from HTML script tags."""
    import json
    html = _unwrap_html(html_or_page)
    results = []
    for m in re.finditer(r'<script\s+[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE):
        raw_json = m.group(1).strip()
        if raw_json:
            try:
                results.append(json.loads(raw_json))
            except Exception:
                pass
    return results


def web_strip_query_params(url: str) -> str:
    """Clean URL by removing query strings and anchor fragments."""
    u = urllib.parse.urlparse(str(url))
    return urllib.parse.urlunparse((u.scheme, u.netloc, u.path, '', '', ''))


def web_count_element_tags(html_or_page: Any, tag_name: str) -> int:
    """Count occurrences of a specific HTML tag."""
    html = _unwrap_html(html_or_page)
    tag = str(tag_name).strip().lstrip("<").rstrip(">")
    return len(re.findall(rf'<{tag}\b', html, re.IGNORECASE))


def web_extract_text_by_class(html_or_page: Any, class_name: str) -> List[str]:
    """Extract text from elements having the specified CSS class."""
    html = _unwrap_html(html_or_page)
    cls = str(class_name).strip().lstrip(".")
    pattern = rf'<[^>]+class=["\'][^"\']*\b{re.escape(cls)}\b[^"\']*["\'][^>]*>(.*?)</[^>]+>'
    matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
    return [re.sub(r'<[^>]+>', '', m).strip() for m in matches]


def web_extract_element_by_id(html_or_page: Any, id_name: str) -> str:
    """Extract element inner text by HTML id."""
    html = _unwrap_html(html_or_page)
    el_id = str(id_name).strip().lstrip("#")
    pattern = rf'<[^>]+id=["\']{re.escape(el_id)}["\'][^>]*>(.*?)</[^>]+>'
    m = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    return ""


def web_parse_content_type(header_str: str) -> Dict[str, str]:
    """Extract mime-type and charset from HTTP Content-Type header."""
    s = str(header_str)
    parts = s.split(";")
    mime = parts[0].strip().lower()
    charset = ""
    for p in parts[1:]:
        p = p.strip()
        if p.lower().startswith("charset="):
            charset = p.split("=", 1)[1].strip("'\"")
    return {"mime_type": mime, "charset": charset}


def web_is_valid_url(url: str) -> bool:
    """Validate RFC well-formed URL structure."""
    u = urllib.parse.urlparse(str(url))
    return bool(u.scheme in ("http", "https", "ftp", "ws", "wss") and u.netloc)


def web_generate_curl_command(method: str, url: str, headers: Optional[Dict[str, str]] = None, body: Optional[str] = None) -> str:
    """Format cURL command equivalent string."""
    parts = [f'curl -X {method.upper()} "{url}"']
    if headers:
        for k, v in headers.items():
            parts.append(f'-H "{k}: {v}"')
    if body:
        parts.append(f"-d '{body}'")
    return " ".join(parts)


class DOMNode:
    """Represents a node in the pure-Python HTML DOM tree."""

    def __init__(self, tag: str, attrs: Optional[Dict[str, str]] = None, parent: Optional["DOMNode"] = None):
        self.tag = tag.lower()
        self.attrs = attrs or {}
        self.parent = parent
        self.children: List["DOMNode"] = []
        self.text_content: str = ""

    def append_child(self, child: "DOMNode") -> None:
        child.parent = self
        self.children.append(child)

    @property
    def inner_text(self) -> str:
        parts = [self.text_content]
        for c in self.children:
            parts.append(c.inner_text)
        return " ".join(" ".join(parts).split()).strip()

    def get_attr(self, name: str, default: str = "") -> str:
        return self.attrs.get(name.lower(), default)


class HTMLDOMSelector(HTMLParser):
    """Zero-dependency HTML Parser and CSS selector query engine."""

    def __init__(self, html: str):
        super().__init__()
        self.root = DOMNode("root")
        self.current: DOMNode = self.root
        self.feed(str(html))

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        node = DOMNode(tag, attr_dict, parent=self.current)
        self.current.append_child(node)
        # Void elements do not nest children
        if tag.lower() not in ("img", "br", "hr", "input", "meta", "link"):
            self.current = node

    def handle_endtag(self, tag: str):
        if self.current.parent is not None and self.current.tag == tag.lower():
            self.current = self.current.parent

    def handle_data(self, data: str):
        clean = data.strip()
        if clean:
            if self.current.text_content:
                self.current.text_content += " " + clean
            else:
                self.current.text_content = clean

    def _matches_simple_selector(self, node: DOMNode, sel: str) -> bool:
        if not sel or node.tag == "root":
            return False

        # ID: #id
        if sel.startswith("#"):
            return node.get_attr("id") == sel[1:]

        # Class: .cls
        if sel.startswith("."):
            classes = node.get_attr("class").split()
            return sel[1:] in classes

        # Attribute: [attr] or [attr=val]
        if sel.startswith("[") and sel.endswith("]"):
            inner = sel[1:-1]
            if "=" in inner:
                k, v = inner.split("=", 1)
                return node.get_attr(k.strip()) == v.strip("\"'")
            return k.strip() in node.attrs

        # Tag with class or id: div.card, span#main
        if "." in sel:
            tag, cls = sel.split(".", 1)
            if tag and node.tag != tag.lower():
                return False
            return cls in node.get_attr("class").split()

        if "#" in sel:
            tag, el_id = sel.split("#", 1)
            if tag and node.tag != tag.lower():
                return False
            return node.get_attr("id") == el_id

        # Plain tag name
        return node.tag == sel.lower()

    def query_all(self, selector: str) -> List[DOMNode]:
        """Query DOM tree using CSS selectors (supports descendant combinators)."""
        tokens = selector.strip().split()
        if not tokens:
            return []

        def match_descendant(current_nodes: List[DOMNode], tok_idx: int) -> List[DOMNode]:
            if tok_idx >= len(tokens):
                return current_nodes
            sel = tokens[tok_idx]
            matched: List[DOMNode] = []

            for parent in current_nodes:
                # BFS through descendants
                queue = list(parent.children)
                while queue:
                    child = queue.pop(0)
                    if self._matches_simple_selector(child, sel):
                        matched.append(child)
                    queue.extend(child.children)

            return match_descendant(matched, tok_idx + 1)

        return match_descendant([self.root], 0)

    def query(self, selector: str) -> Optional[DOMNode]:
        res = self.query_all(selector)
        return res[0] if res else None


def web_extract_metadata(html_content: str) -> Dict[str, Any]:
    """Extract OpenGraph, Twitter Cards, JSON-LD, and standard meta descriptions."""
    html = str(html_content)
    res: Dict[str, Any] = {
        "title": "",
        "description": "",
        "open_graph": {},
        "twitter_cards": {},
        "json_ld": [],
    }

    # Title
    m_title = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if m_title:
        res["title"] = m_title.group(1).strip()

    # Meta tags
    meta_tags = re.findall(r"<meta\s+([^>]+)>", html, re.IGNORECASE)
    for tag_str in meta_tags:
        # Extract attributes
        attrs = dict(re.findall(r'(\w+)=["\']([^"\']*)["\']', tag_str, re.IGNORECASE))
        name = attrs.get("name", "").lower()
        prop = attrs.get("property", "").lower()
        content = attrs.get("content", "")

        if name == "description":
            res["description"] = content
        elif prop.startswith("og:"):
            res["open_graph"][prop[3:]] = content
        elif name.startswith("twitter:"):
            res["twitter_cards"][name[8:]] = content

    # JSON-LD scripts
    json_lds = re.findall(r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.IGNORECASE | re.DOTALL)
    for j_str in json_lds:
        try:
            res["json_ld"].append(json.loads(j_str.strip()))
        except Exception:
            pass

    return res


class RobotsTxtParser:
    """Parses robots.txt and verifies URL crawl permissions."""

    def __init__(self, content: str = ""):
        self.rules: List[Dict[str, Any]] = []
        self.sitemaps: List[str] = []
        if content:
            self.parse(content)

    def parse(self, content: str) -> None:
        lines = content.replace("\r\n", "\n").split("\n")
        current_agent = "*"

        for line in lines:
            line = line.split("#")[0].strip()
            if not line:
                continue
            if ":" not in line:
                continue
            field, val = line.split(":", 1)
            field = field.strip().lower()
            val = val.strip()

            if field == "user-agent":
                current_agent = val.lower()
            elif field == "disallow":
                self.rules.append({"agent": current_agent, "type": "disallow", "path": val})
            elif field == "allow":
                self.rules.append({"agent": current_agent, "type": "allow", "path": val})
            elif field == "sitemap":
                self.sitemaps.append(val)

    def is_allowed(self, path: str, user_agent: str = "*") -> bool:
        ua = user_agent.lower()
        clean_path = path.strip()
        matching = [r for r in self.rules if r["agent"] == ua]
        if not matching and ua != "*":
            matching = [r for r in self.rules if r["agent"] == "*"]

        # Sort by longest path first (most specific rule applies per RFC 9309)
        matching.sort(key=lambda r: (len(r["path"]), 1 if r["type"] == "allow" else 0), reverse=True)

        for r in matching:
            rule_path = r["path"]
            if not rule_path:
                continue
            if clean_path.startswith(rule_path):
                return r["type"] == "allow"
        return True





# --- Deepened Web Scraping: CSS Selector Engine & RFC 6265 Cookie Jar ---

class DOMElement:
    """Lightweight representation of an HTML DOM element node."""

    def __init__(self, tag: str, attrs: Optional[Dict[str, str]] = None, parent: Optional["DOMElement"] = None):
        self.tag = tag.lower()
        self.attrs = attrs or {}
        self.classes = set(self.attrs.get("class", "").split())
        self.id = self.attrs.get("id", "")
        self.children: List["DOMElement"] = []
        self.parent = parent
        self.text_content: List[str] = []

    @property
    def text(self) -> str:
        """Recursive inner text of this node and descendants."""
        all_texts = list(self.text_content)
        for child in self.children:
            t = child.text
            if t:
                all_texts.append(t)
        return " ".join(" ".join(all_texts).split())

    def get_attribute(self, name: str) -> Optional[str]:
        return self.attrs.get(name)

    def __repr__(self) -> str:
        attrs_str = " ".join(f'{k}="{v}"' for k, v in self.attrs.items())
        return f"<{self.tag} {attrs_str}>" if attrs_str else f"<{self.tag}>"


class DOMBuilder(HTMLParser):
    """Parses raw HTML into a hierarchically linked DOMElement tree."""

    def __init__(self):
        super().__init__()
        self.root = DOMElement("root")
        self.current = self.root

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        node = DOMElement(tag=tag, attrs=attr_dict, parent=self.current)
        self.current.children.append(node)
        # Avoid nesting self-closing void elements
        if tag.lower() not in ("br", "hr", "img", "input", "meta", "link", "area", "base", "col", "embed", "param", "source", "track", "wbr"):
            self.current = node

    def handle_endtag(self, tag: str):
        t = tag.lower()
        temp = self.current
        while temp is not None and temp.tag != t and temp != self.root:
            temp = temp.parent
        if temp is not None and temp != self.root and temp.parent is not None:
            self.current = temp.parent

    def handle_data(self, data: str):
        clean = data.strip()
        if clean:
            self.current.text_content.append(clean)


class CSSSelectorEngine:
    """Recursive CSS selector matcher supporting tags, classes, IDs, attributes, child, and descendant combinators."""

    @classmethod
    def parse_html(cls, html: str) -> DOMElement:
        builder = DOMBuilder()
        builder.feed(html)
        return builder.root

    @classmethod
    def _matches_compound(cls, elem: DOMElement, selector_part: str) -> bool:
        """Matches a single compound selector (e.g. 'div.container#main[data-x=1]')."""
        if elem.tag == "root":
            return False

        # Extract attributes
        attr_pattern = r"\[([a-zA-Z0-9_\-]+)(?:(=|~=|\^=|\$=|\*=)(?:['\"]?)([^'\"]*)(?:['\"]?))?\]"
        attrs = re.findall(attr_pattern, selector_part)
        cleaned = re.sub(attr_pattern, "", selector_part)

        # Extract ID
        id_match = re.search(r"#([a-zA-Z0-9_\-]+)", cleaned)
        if id_match:
            if elem.id != id_match.group(1):
                return False
            cleaned = re.sub(r"#([a-zA-Z0-9_\-]+)", "", cleaned)

        # Extract classes
        class_matches = re.findall(r"\.([a-zA-Z0-9_\-]+)", cleaned)
        for c in class_matches:
            if c not in elem.classes:
                return False
        cleaned = re.sub(r"\.([a-zA-Z0-9_\-]+)", "", cleaned)

        # Remaining is tag name
        tag = cleaned.strip()
        if tag and tag != "*":
            if elem.tag != tag.lower():
                return False

        # Match attributes
        for name, op, val in attrs:
            if name not in elem.attrs:
                return False
            if op:
                actual = elem.attrs[name]
                if op == "=" and actual != val:
                    return False
                elif op == "^=" and not actual.startswith(val):
                    return False
                elif op == "$=" and not actual.endswith(val):
                    return False
                elif op == "*=" and val not in actual:
                    return False
                elif op == "~=" and val not in actual.split():
                    return False

        return True

    @classmethod
    def select(cls, root: DOMElement, selector: str) -> List[DOMElement]:
        """Queries the DOM hierarchy using standard CSS selector syntax."""
        # Handle comma-separated selector grouping
        if "," in selector:
            results = []
            seen = set()
            for group in selector.split(","):
                for el in cls.select(root, group.strip()):
                    if id(el) not in seen:
                        seen.add(id(el))
                        results.append(el)
            return results

        # Tokenize combinators: child '>' vs descendant ' '
        # Normalize whitespace around '>'
        norm = re.sub(r"\s*>\s*", " > ", selector.strip())
        tokens = norm.split()
        if not tokens:
            return []

        # Start with all elements under root
        def _collect_descendants(node: DOMElement, acc: List[DOMElement]):
            for ch in node.children:
                acc.append(ch)
                _collect_descendants(ch, acc)

        current_candidates: List[DOMElement] = []
        _collect_descendants(root, current_candidates)

        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok == ">":
                # Next token matches direct child of current candidates
                i += 1
                if i >= len(tokens):
                    break
                next_tok = tokens[i]
                next_cands = []
                for parent in current_candidates:
                    for child in parent.children:
                        if cls._matches_compound(child, next_tok):
                            next_cands.append(child)
                current_candidates = next_cands
            else:
                if i == 0:
                    current_candidates = [el for el in current_candidates if cls._matches_compound(el, tok)]
                else:
                    # Descendant combinator
                    descendants = []
                    for cand in current_candidates:
                        sub = []
                        _collect_descendants(cand, sub)
                        for d in sub:
                            if cls._matches_compound(d, tok):
                                descendants.append(d)
                    current_candidates = descendants
            i += 1

        # Deduplicate preserving order
        unique: List[DOMElement] = []
        seen = set()
        for el in current_candidates:
            if id(el) not in seen:
                seen.add(id(el))
                unique.append(el)
        return unique


class RFC6265CookieJar:
    """RFC 6265 compliant HTTP state management (Cookie Jar).
    
    Supports:
    - Path and domain scoping with leading-dot subdomain matching
    - Max-Age and Expires date calculation
    - Secure and HttpOnly flags
    - Deterministic Cookie header generation
    """

    class Cookie:
        def __init__(
            self,
            name: str,
            value: str,
            domain: str,
            path: str = "/",
            expires_at: Optional[float] = None,
            secure: bool = False,
            http_only: bool = False,
        ):
            self.name = name
            self.value = value
            self.domain = domain.lower().lstrip(".")
            self.path = path if path.startswith("/") else "/"
            self.expires_at = expires_at
            self.secure = secure
            self.http_only = http_only

        def is_expired(self, current_time: float) -> bool:
            return self.expires_at is not None and current_time >= self.expires_at

        def matches_domain(self, request_domain: str) -> bool:
            req = request_domain.lower()
            return req == self.domain or req.endswith("." + self.domain)

        def matches_path(self, request_path: str) -> bool:
            if not request_path:
                request_path = "/"
            return request_path == self.path or request_path.startswith(self.path.rstrip("/") + "/")

    def __init__(self):
        self.cookies: List[RFC6265CookieJar.Cookie] = []

    def set_cookie(self, header: str, request_url: str, current_time: Optional[float] = None) -> None:
        """Parses a Set-Cookie header string and adds/updates the cookie."""
        import time
        from urllib.parse import urlparse
        now = time.time() if current_time is None else current_time
        parsed_url = urlparse(request_url)
        default_domain = parsed_url.hostname or "localhost"
        default_path = parsed_url.path or "/"
        if "/" in default_path:
            default_path = default_path.rsplit("/", 1)[0]
        if not default_path:
            default_path = "/"

        parts = [p.strip() for p in header.split(";")]
        if not parts or "=" not in parts[0]:
            return

        name, value = parts[0].split("=", 1)
        domain = default_domain
        path = default_path
        expires_at = None
        secure = False
        http_only = False

        for attr in parts[1:]:
            if "=" in attr:
                k, v = attr.split("=", 1)
                k = k.strip().lower()
                v = v.strip()
                if k == "domain":
                    domain = v
                elif k == "path":
                    path = v
                elif k == "max-age":
                    try:
                        expires_at = now + float(v)
                    except ValueError:
                        pass
            else:
                k = attr.strip().lower()
                if k == "secure":
                    secure = True
                elif k == "httponly":
                    http_only = True

        cookie = self.Cookie(
            name=name.strip(),
            value=value.strip(),
            domain=domain,
            path=path,
            expires_at=expires_at,
            secure=secure,
            http_only=http_only,
        )

        # Replace existing cookie if same name, domain, path
        self.cookies = [
            c for c in self.cookies
            if not (c.name == cookie.name and c.domain == cookie.domain and c.path == cookie.path)
        ]
        self.cookies.append(cookie)

    def get_cookie_header(self, request_url: str, is_secure: bool = False, current_time: Optional[float] = None) -> str:
        """Constructs 'Cookie: name=val; name2=val2' header for the specified request URL."""
        import time
        from urllib.parse import urlparse
        now = time.time() if current_time is None else current_time
        parsed_url = urlparse(request_url)
        req_domain = parsed_url.hostname or "localhost"
        req_path = parsed_url.path or "/"

        valid = []
        for c in self.cookies:
            if c.is_expired(now):
                continue
            if not c.matches_domain(req_domain):
                continue
            if not c.matches_path(req_path):
                continue
            if c.secure and not is_secure:
                continue
            valid.append(f"{c.name}={c.value}")

        return "; ".join(valid)
