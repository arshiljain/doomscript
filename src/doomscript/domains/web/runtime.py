"""Runtime execution engine for Web Scraping & Document Extraction domain."""

from typing import Any, Dict, List, Optional, Tuple, Union
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
