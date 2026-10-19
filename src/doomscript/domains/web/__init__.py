"""Web Scraping & Document Extraction Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.web.spec import (
    WebPageSpec,
    WebExtractLinksSpec,
    WebExtractTableSpec,
    WebExtractTextSpec,
    WebDownloadMediaSpec,
)
from doomscript.domains.web.parser import WebDomainParser
from doomscript.domains.web.runtime import (
    WebPage,
    WebRuntime,
    open_webpage,
    parse_html,
    webpage_title,
    webpage_text,
    extract_web_links,
    extract_web_table,
    download_web_media,
    execute_web_ir,
)
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.web.exporter import WebASTExporter
from doomscript.domains.registry import get_domain_registry


class WebDomain(DomainContract):
    """Web Scraping & Document Extraction domain pack."""

    name = "web"
    aliases = ["crawl", "scrape", "browser"]
    description = "Web scraping, DOM parsing, link extraction, HTML table parsing, and media downloading"
    parser = WebDomainParser()
    runtime = WebRuntime()
    exporter = WebASTExporter()
    capabilities = ["scraping", "html", "links", "tables", "media_download"]
    optional_dependencies = ["beautifulsoup4", "requests"]

    verbs = [
        VerbSpec(
            name="open_webpage",
            pattern="open webpage {url:expr} into {target:ident}",
            arg_schema={"url": "expr", "target": "ident"},
            returns="WebPage",
            description="Fetch web page over HTTP and parse DOM structure",
        ),
        VerbSpec(
            name="parse_html",
            pattern="parse html {html_text:expr} into {target:ident}",
            arg_schema={"html_text": "expr", "target": "ident"},
            returns="WebPage",
            description="Parse raw HTML document string into queryable DOM tree",
        ),
        VerbSpec(
            name="webpage_title",
            pattern="title of webpage {page_var:ident} into {target:ident}",
            arg_schema={"page_var": "ident", "target": "ident"},
            returns="str",
            description="Extract <title> meta tag from page",
        ),
        VerbSpec(
            name="webpage_text",
            pattern="text in webpage {page_var:ident} into {target:ident}",
            arg_schema={"page_var": "ident", "target": "ident"},
            returns="str",
            description="Extract cleaned inner text from page body",
        ),
        VerbSpec(
            name="extract_links",
            pattern="extract [all] links from [webpage] {page_var:ident} into {target:ident}",
            arg_schema={"page_var": "ident", "target": "ident"},
            returns="Collection",
            description="Extract all resolved absolute URLs from anchor elements",
        ),
        VerbSpec(
            name="find_table",
            pattern="find table {index:int} in [webpage] {page_var:ident} into {target:ident}",
            arg_schema={"index": "int", "page_var": "ident", "target": "ident"},
            returns="Table",
            description="Parse HTML <table> into structured Table object",
        ),
        VerbSpec(
            name="download_media",
            pattern="download all (images|media) from [webpage] {page_var:ident} to {dest_folder:expr} into {target:ident}",
            arg_schema={"page_var": "ident", "dest_folder": "expr", "target": "ident"},
            returns="Collection",
            description="Download all images and media assets to local folder",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        if (
            s.startswith("open webpage ")
            or s.startswith("scrape webpage ")
            or s.startswith("parse html ")
            or s.startswith("title of webpage ")
            or s.startswith("title of page ")
            or s.startswith("text in webpage ")
            or s.startswith("text in page ")
            or s.startswith("extract all links ")
            or s.startswith("extract links ")
            or (s.startswith("find table ") and " in " in s)
            or s.startswith("download all images ")
            or s.startswith("download all media ")
        ):
            return True

        from doomscript.domains.registry import get_domain_registry
        if get_domain_registry().is_active("web"):
            if s.startswith("title of ") and " into " in s:
                return True
            if s.startswith("text in ") and " into " in s:
                return True

        return False

    def can_handle_block(self, header: str) -> bool:
        return False


# Register with central registry
WEB_DOMAIN = WebDomain()
get_domain_registry().register(WEB_DOMAIN)

__all__ = [
    "WebDomain",
    "WEB_DOMAIN",
    "WebPageSpec",
    "WebExtractLinksSpec",
    "WebExtractTableSpec",
    "WebExtractTextSpec",
    "WebDownloadMediaSpec",
    "WebDomainParser",
    "WebRuntime",
    "WebASTExporter",
    "WebPage",
    "open_webpage",
    "parse_html",
    "webpage_title",
    "webpage_text",
    "extract_web_links",
    "extract_web_table",
    "download_web_media",
    "execute_web_ir",
]
