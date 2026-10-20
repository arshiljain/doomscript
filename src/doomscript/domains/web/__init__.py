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
    web_extract_images,
    web_extract_forms,
    web_encode_form_data,
    web_decode_form_data,
    web_parse_sitemap_xml,
    web_parse_robots_txt,
    web_canonicalize_url,
    web_extract_meta_description,
    web_extract_headings,
    web_check_ssl_expiry,
    web_parse_cookie_header,
    web_build_cookie_header,
    web_extract_json_ld,
    web_strip_query_params,
    web_count_element_tags,
    web_extract_text_by_class,
    web_extract_element_by_id,
    web_parse_content_type,
    web_is_valid_url,
    web_generate_curl_command,
    DOMNode,
    HTMLDOMSelector,
    web_extract_metadata,
    RobotsTxtParser,
    DOMElement,
    CSSSelectorEngine,
    RFC6265CookieJar,
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
            or s.startswith("select all ")
            or s.startswith("extract all tables from ")
            or s.startswith("extract html tables from ")
            or s.startswith("extract tables from ")
            or s.startswith("parse query params ")
            or s.startswith("build url ")
            or s.startswith("strip html tags from ")
            or s.startswith("extract meta tags from ")
            or ("response " in s and " is successful into " in s)
            or s.startswith("extract images from ")
            or s.startswith("extract forms from ")
            or s.startswith("encode form data ")
            or s.startswith("decode form data ")
            or s.startswith("parse sitemap ")
            or s.startswith("check robots txt ")
            or s.startswith("evaluate robots txt ")
            or s.startswith("canonicalize url ")
            or s.startswith("extract meta description from ")
            or s.startswith("extract headings from ")
            or s.startswith("check ssl expiry ")
            or s.startswith("parse cookie header ")
            or s.startswith("build cookie header from ")
            or s.startswith("extract json ld from ")
            or s.startswith("strip query ")
            or s.startswith("count tag ")
            or s.startswith("count element tag ")
            or s.startswith("extract text with class ")
            or s.startswith("extract text by class ")
            or s.startswith("extract element with id ")
            or s.startswith("extract element by id ")
            or s.startswith("parse content type ")
            or ("url " in s and " is valid into " in s)
            or s.startswith("generate curl command for ")
            or s.startswith("select css ")
            or s.startswith("create cookie jar ")
            or super().can_handle_line(line)
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
    "web_extract_images",
    "web_extract_forms",
    "web_encode_form_data",
    "web_decode_form_data",
    "web_parse_sitemap_xml",
    "web_parse_robots_txt",
    "web_canonicalize_url",
    "web_extract_meta_description",
    "web_extract_headings",
    "web_check_ssl_expiry",
    "web_parse_cookie_header",
    "web_build_cookie_header",
    "web_extract_json_ld",
    "web_strip_query_params",
    "web_count_element_tags",
    "web_extract_text_by_class",
    "web_extract_element_by_id",
    "web_parse_content_type",
    "web_is_valid_url",
    "web_generate_curl_command",
    "DOMNode",
    "HTMLDOMSelector",
    "web_extract_metadata",
    "RobotsTxtParser",
    "DOMElement",
    "CSSSelectorEngine",
    "RFC6265CookieJar",
]
