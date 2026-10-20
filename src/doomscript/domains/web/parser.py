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

        # select css <sel> from [html] <html_var> into <target>
        m_css = re.match(
            r"^select\s+css\s+(.+?)\s+(?:from|in)(?:\s+html)?\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_css:
            sel, html_txt, target = m_css.group(1).strip(), m_css.group(2).strip(), m_css.group(3).strip()
            return f"set {target} to web_css_select({html_txt}, {sel})"

        # create cookie jar into <target>
        m_jar = re.match(
            r"^create\s+cookie\s+jar\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_jar:
            target = m_jar.group(1).strip()
            return f"set {target} to web_cookie_jar()"

        # select all <sel> in html <html_var> into <target>
        # select all <sel> [elements] in/from [html] <html_var> into <target>
        m_sel = re.match(
            r"^select\s+all\s+(.+?)(?:\s+elements)?\s+(?:in\s+html|from\s+html|from)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sel:
            sel, html_var, target = m_sel.group(1).strip(), m_sel.group(2).strip(), m_sel.group(3).strip()
            return f"set {target} to web_select_all({html_var}, {sel})"

        # extract [all] [html] tables from <html_var> into <target>
        m_etbl = re.match(
            r"^extract\s+(?:all\s+)?(?:html\s+)?tables\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_etbl:
            html_var, target = m_etbl.group(1).strip(), m_etbl.group(2).strip()
            return f"set {target} to web_extract_tables({html_var})"

        # parse query params of url/from <url> into <target>
        m_pqp = re.match(
            r"^parse\s+query\s+params\s+(?:of\s+url\s+|from\s+)(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pqp:
            url_var, target = m_pqp.group(1).strip(), m_pqp.group(2).strip()
            return f"set {target} to web_parse_query_params({url_var})"

        # build url <base> with params <params> into <target>
        m_burl = re.match(
            r"^build\s+url\s+(.+?)\s+with\s+params\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_burl:
            base, params, target = m_burl.group(1).strip(), m_burl.group(2).strip(), m_burl.group(3).strip()
            return f"set {target} to web_build_url({base}, {params})"

        # strip html tags from <text> into <target>
        m_strip = re.match(
            r"^strip\s+html\s+tags\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_strip:
            text_var, target = m_strip.group(1).strip(), m_strip.group(2).strip()
            return f"set {target} to web_strip_tags({text_var})"

        # extract meta tags from [html] <html_var> into <target>
        m_meta = re.match(
            r"^extract\s+meta\s+tags\s+from\s+(?:html\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_meta:
            html_var, target = m_meta.group(1).strip(), m_meta.group(2).strip()
            return f"set {target} to web_extract_meta_tags({html_var})"

        # check if response <resp> is successful into <target>
        m_succ = re.match(
            r"^(?:check\s+if\s+)?response\s+(.+?)\s+is\s+successful\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_succ:
            resp_var, target = m_succ.group(1).strip(), m_succ.group(2).strip()
            return f"set {target} to web_response_is_successful({resp_var})"

        # extract images from [html] <html_var> into <target>
        m_imgs = re.match(
            r"^extract\s+images\s+from\s+(?:html\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_imgs:
            h, target = m_imgs.group(1).strip(), m_imgs.group(2).strip()
            return f"set {target} to web_extract_images({h})"

        # extract forms from [html] <html_var> into <target>
        m_forms = re.match(
            r"^extract\s+forms\s+from\s+(?:html\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_forms:
            h, target = m_forms.group(1).strip(), m_forms.group(2).strip()
            return f"set {target} to web_extract_forms({h})"

        # encode form data <params> into <target>
        m_enc_f = re.match(
            r"^encode\s+form\s+data\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_enc_f:
            p, target = m_enc_f.group(1).strip(), m_enc_f.group(2).strip()
            return f"set {target} to web_encode_form_data({p})"

        # decode form data <query_str> into <target>
        m_dec_f = re.match(
            r"^decode\s+form\s+data\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dec_f:
            q, target = m_dec_f.group(1).strip(), m_dec_f.group(2).strip()
            return f"set {target} to web_decode_form_data({q})"

        # parse sitemap [xml] <sitemap_var> into <target>
        m_sm = re.match(
            r"^parse\s+sitemap\s+(?:xml\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sm:
            sm, target = m_sm.group(1).strip(), m_sm.group(2).strip()
            return f"set {target} to web_parse_sitemap_xml({sm})"

        # check robots txt <robots_var> for user agent <ua> and path <p> into <target>
        m_rob = re.match(
            r"^(?:check\s+robots\s+txt|evaluate\s+robots\s+txt)\s+(.+?)\s+for\s+user\s+agent\s+(.+?)\s+and\s+path\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rob:
            rob, ua, p, target = m_rob.group(1).strip(), m_rob.group(2).strip(), m_rob.group(3).strip(), m_rob.group(4).strip()
            return f"set {target} to web_parse_robots_txt({rob}, user_agent={ua}, path={p})"

        # canonicalize url <base> with <relative> into <target>
        m_canon = re.match(
            r"^canonicalize\s+url\s+(.+?)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_canon:
            b, rel, target = m_canon.group(1).strip(), m_canon.group(2).strip(), m_canon.group(3).strip()
            return f"set {target} to web_canonicalize_url({b}, {rel})"

        # extract meta description from [html] <html_var> into <target>
        m_mdesc = re.match(
            r"^extract\s+meta\s+description\s+from\s+(?:html\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mdesc:
            h, target = m_mdesc.group(1).strip(), m_mdesc.group(2).strip()
            return f"set {target} to web_extract_meta_description({h})"

        # extract headings from [html] <html_var> into <target>
        m_head = re.match(
            r"^extract\s+headings\s+from\s+(?:html\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_head:
            h, target = m_head.group(1).strip(), m_head.group(2).strip()
            return f"set {target} to web_extract_headings({h})"

        # check ssl expiry for <domain> into <target>
        m_ssl = re.match(
            r"^check\s+ssl\s+expiry\s+(?:for|of)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ssl:
            dom, target = m_ssl.group(1).strip(), m_ssl.group(2).strip()
            return f"set {target} to web_check_ssl_expiry({dom})"

        # parse cookie header <header_str> into <target>
        m_pcook = re.match(
            r"^parse\s+cookie\s+header\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pcook:
            hdr, target = m_pcook.group(1).strip(), m_pcook.group(2).strip()
            return f"set {target} to web_parse_cookie_header({hdr})"

        # build cookie header from <cookies_dict> into <target>
        m_bcook = re.match(
            r"^build\s+cookie\s+header\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bcook:
            cd, target = m_bcook.group(1).strip(), m_bcook.group(2).strip()
            return f"set {target} to web_build_cookie_header({cd})"

        # extract json ld from [html] <html_var> into <target>
        m_jld = re.match(
            r"^extract\s+json\s+ld\s+from\s+(?:html\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_jld:
            h, target = m_jld.group(1).strip(), m_jld.group(2).strip()
            return f"set {target} to web_extract_json_ld({h})"

        # strip query parameters from <url> into <target>
        m_sqp = re.match(
            r"^strip\s+query\s+(?:params|parameters)\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sqp:
            u, target = m_sqp.group(1).strip(), m_sqp.group(2).strip()
            return f"set {target} to web_strip_query_params({u})"

        # count tag <tag_name> in [html] <html_var> into <target>
        m_ctag = re.match(
            r"^count\s+(?:element\s+)?tag\s+(.+?)\s+in\s+(?:html\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ctag:
            tag, h, target = m_ctag.group(1).strip(), m_ctag.group(2).strip(), m_ctag.group(3).strip()
            return f"set {target} to web_count_element_tags({h}, {tag})"

        # extract text with class <cls> from [html] <html_var> into <target>
        m_tcls = re.match(
            r"^extract\s+text\s+(?:with|by)\s+class\s+(.+?)\s+from\s+(?:html\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tcls:
            cls_name, h, target = m_tcls.group(1).strip(), m_tcls.group(2).strip(), m_tcls.group(3).strip()
            return f"set {target} to web_extract_text_by_class({h}, {cls_name})"

        # extract element with id <id> from [html] <html_var> into <target>
        m_eid = re.match(
            r"^extract\s+element\s+(?:with|by)\s+id\s+(.+?)\s+from\s+(?:html\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_eid:
            id_name, h, target = m_eid.group(1).strip(), m_eid.group(2).strip(), m_eid.group(3).strip()
            return f"set {target} to web_extract_element_by_id({h}, {id_name})"

        # parse content type header <header_str> into <target>
        m_pcth = re.match(
            r"^parse\s+content\s+type\s+(?:header\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pcth:
            hdr, target = m_pcth.group(1).strip(), m_pcth.group(2).strip()
            return f"set {target} to web_parse_content_type({hdr})"

        # check if url <url> is valid into <target>
        m_vurl = re.match(
            r"^(?:check\s+if\s+)?url\s+(.+?)\s+is\s+valid\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vurl:
            u, target = m_vurl.group(1).strip(), m_vurl.group(2).strip()
            return f"set {target} to web_is_valid_url({u})"

        # generate curl command for <method> to <url> into <target>
        m_curl = re.match(
            r"^generate\s+curl\s+command\s+for\s+(.+?)\s+to\s+(.+?)(?:\s+with\s+headers\s+(.+?))?(?:\s+and\s+body\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_curl:
            method, url, hdrs, body, target = m_curl.group(1).strip(), m_curl.group(2).strip(), m_curl.group(3), m_curl.group(4), m_curl.group(5).strip()
            h_arg = f", headers={hdrs.strip()}" if hdrs else ""
            b_arg = f", body={body.strip()}" if body else ""
            return f"set {target} to web_generate_curl_command({method}, {url}{h_arg}{b_arg})"

        # encode multipart form fields <fields> into <target>
        m_mp = re.match(
            r"^encode\s+multipart\s+form\s+fields\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mp:
            fields, target = m_mp.group(1).strip(), m_mp.group(2).strip()
            return f"set {target} to web_multipart_encode({fields})"

        # negotiate content type for header <header> from <supported> into <target>
        m_neg = re.match(
            r"^negotiate\s+content\s+type\s+for\s+header\s+(.+?)\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_neg:
            hdr, supp, target = m_neg.group(1).strip(), m_neg.group(2).strip(), m_neg.group(3).strip()
            return f"set {target} to web_content_negotiate({hdr}, {supp})"

        # expand uri template <template> with variables <variables> into <target>
        m_uri = re.match(
            r"^expand\s+uri\s+template\s+(.+?)\s+with\s+variables\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_uri:
            tmpl, vars_dict, target = m_uri.group(1).strip(), m_uri.group(2).strip(), m_uri.group(3).strip()
            return f"set {target} to web_uri_template_expand({tmpl}, {vars_dict})"

        # encode websocket frame payload <payload> [opcode <op>] [masked <bool>] into <target>
        m_ws_enc = re.match(
            r"^encode\s+websocket\s+frame\s+payload\s+(.+?)(?:\s+opcode\s+(\d+))?(?:\s+masked\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ws_enc:
            payload = m_ws_enc.group(1).strip()
            op = m_ws_enc.group(2) or "1"
            masked = m_ws_enc.group(3).strip() if m_ws_enc.group(3) else "False"
            target = m_ws_enc.group(4).strip()
            return f"set {target} to web_websocket_encode({payload}, opcode={op}, mask={masked})"

        # decode websocket frame bytes <bytes> into <target>
        m_ws_dec = re.match(
            r"^decode\s+websocket\s+frame\s+bytes\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ws_dec:
            fb, target = m_ws_dec.group(1).strip(), m_ws_dec.group(2).strip()
            return f"set {target} to web_websocket_decode({fb})"

        # encode chunked transfer chunks <chunks> [with trailers <trailers>] into <target>
        m_chk_enc = re.match(
            r"^encode\s+chunked\s+transfer\s+chunks\s+(.+?)(?:\s+with\s+trailers\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_chk_enc:
            chunks, trailers, target = m_chk_enc.group(1).strip(), m_chk_enc.group(2), m_chk_enc.group(3).strip()
            tr_arg = f", trailers={trailers.strip()}" if trailers else ""
            return f"set {target} to web_chunked_encode({chunks}{tr_arg})"

        # decode chunked transfer body <chunked_str> into <target>
        m_chk_dec = re.match(
            r"^decode\s+chunked\s+transfer\s+body\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_chk_dec:
            c_str, target = m_chk_dec.group(1).strip(), m_chk_dec.group(2).strip()
            return f"set {target} to web_chunked_decode({c_str})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Web domain does not currently define declarative blocks")
