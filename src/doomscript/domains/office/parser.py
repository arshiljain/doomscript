"""Independent Domain Parser for Office Automation (Spreadsheets & Documents) domain."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.office.spec import (
    OfficeSpreadsheetSpec,
    OfficeAddRowSpec,
    OfficeSaveSpreadsheetSpec,
    OfficeDocumentSpec,
    OfficeAddHeadingSpec,
    OfficeAddParagraphSpec,
    OfficeSaveDocumentSpec,
)


class OfficeDomainParser(DomainParser):
    """Independent parser for Office Automation syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # create spreadsheet into <target>
        m_sheet = re.match(
            r"^create\s+spreadsheet\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sheet:
            target = m_sheet.group(1).strip()
            return f"set {target} to create_spreadsheet()"

        # add row <row_expr> to [spreadsheet] <sheet_var>
        m_row = re.match(
            r"^add\s+row\s+(.+?)\s+to\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_row:
            row_expr = m_row.group(1).strip()
            sheet_var = m_row.group(2).strip()
            return f"add_spreadsheet_row({sheet_var}, {row_expr})"

        # add rows [from] <rows_expr> to [spreadsheet] <sheet_var>
        m_rows = re.match(
            r"^add\s+rows\s+(?:from\s+)?(.+?)\s+to\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rows:
            rows_expr = m_rows.group(1).strip()
            sheet_var = m_rows.group(2).strip()
            return f"add_spreadsheet_rows({sheet_var}, {rows_expr})"

        # save spreadsheet <sheet_var> to <path_expr>
        m_save_sheet = re.match(
            r"^save\s+spreadsheet\s+([A-Za-z_]\w*)\s+to\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_save_sheet:
            sheet_var = m_save_sheet.group(1).strip()
            path_expr = m_save_sheet.group(2).strip()
            return f"save_spreadsheet({sheet_var}, {path_expr})"

        # create word document into <target>
        m_doc = re.match(
            r"^create\s+word\s+document\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_doc:
            target = m_doc.group(1).strip()
            return f"set {target} to create_word_document()"

        # add heading <text_expr> [(with|at) level <n>] to [document] <doc_var>
        m_heading = re.match(
            r"^add\s+heading\s+(.+?)(?:\s+(?:with|at)\s+level\s+(\d+))?\s+to\s+(?:(?:word\s+)?document\s+)?([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_heading:
            text_expr = m_heading.group(1).strip()
            level = m_heading.group(2).strip() if m_heading.group(2) else "1"
            doc_var = m_heading.group(3).strip()
            return f"add_document_heading({doc_var}, {text_expr}, level={level})"

        # add paragraph <text_expr> to [document] <doc_var>
        m_para = re.match(
            r"^add\s+paragraph\s+(.+?)\s+to\s+(?:(?:word\s+)?document\s+)?([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_para:
            text_expr = m_para.group(1).strip()
            doc_var = m_para.group(2).strip()
            return f"add_document_paragraph({doc_var}, {text_expr})"

        # save word document <doc_var> to <path_expr>
        m_save_doc = re.match(
            r"^save\s+word\s+document\s+([A-Za-z_]\w*)\s+to\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_save_doc:
            doc_var = m_save_doc.group(1).strip()
            path_expr = m_save_doc.group(2).strip()
            return f"save_word_document({doc_var}, {path_expr})"

        # count worksheets in [spreadsheet] <sheet> into <target>
        m_cnt_s = re.match(
            r"^count\s+worksheets\s+in\s+(?:spreadsheet\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cnt_s:
            sheet = m_cnt_s.group(1).strip()
            target = m_cnt_s.group(2).strip()
            return f"set {target} to office_count_worksheets({sheet})"

        # extract text from [word] document <doc> into <target>
        m_ext_t = re.match(
            r"^extract\s+text\s+from\s+(?:word\s+)?document\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ext_t:
            doc = m_ext_t.group(1).strip()
            target = m_ext_t.group(2).strip()
            return f"set {target} to office_extract_text({doc})"

        # add worksheet <name> to [spreadsheet] <sheet> into <target>
        m_add_ws = re.match(
            r"^add\s+worksheet\s+(.+?)\s+to\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_add_ws:
            ws_name = m_add_ws.group(1).strip()
            sheet = m_add_ws.group(2).strip()
            target = m_add_ws.group(3).strip()
            return f"set {target} to office_add_worksheet({sheet}, {ws_name})"

        # convert markdown <md> to document sections/format into <target>
        m_md = re.match(
            r"^convert\s+markdown\s+(.+?)\s+to\s+document\s+(?:sections|format)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_md:
            md_expr = m_md.group(1).strip()
            target = m_md.group(2).strip()
            return f"set {target} to office_markdown_to_sections({md_expr})"

        # merge pdf files <files> [into file <out>] into <target>
        m_pdf = re.match(
            r"^merge\s+pdf\s+files?\s+(.+?)(?:\s+into\s+file\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pdf:
            pdfs = m_pdf.group(1).strip()
            out_f = m_pdf.group(2)
            target = m_pdf.group(3).strip()
            out_arg = f", output_path={out_f.strip()}" if out_f else ""
            return f"set {target} to office_merge_pdfs({pdfs}{out_arg})"

        # count pages in [document] <doc> into <target>
        m_cnt_p = re.match(
            r"^count\s+pages\s+in\s+(?:document\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cnt_p:
            doc = m_cnt_p.group(1).strip()
            target = m_cnt_p.group(2).strip()
            return f"set {target} to office_count_pages({doc})"

        # append table <table> to worksheet <name> in [spreadsheet] <sheet> into <target>
        m_app_t = re.match(
            r"^append\s+table\s+(.+?)\s+to\s+worksheet\s+(.+?)\s+in\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_app_t:
            table = m_app_t.group(1).strip()
            ws_name = m_app_t.group(2).strip()
            sheet = m_app_t.group(3).strip()
            target = m_app_t.group(4).strip()
            return f"set {target} to office_append_table_to_sheet({sheet}, {ws_name}, {table})"

        # calculate sheet summary of column <col> in sheet <sheet_name> of [spreadsheet] <sheet> into <target>
        m_sum = re.match(
            r"^calculate\s+(?:sheet\s+)?summary\s+of\s+column\s+(.+?)\s+in\s+sheet\s+(.+?)\s+of\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sum:
            col = m_sum.group(1).strip()
            sheet_name = m_sum.group(2).strip()
            sheet = m_sum.group(3).strip()
            target = m_sum.group(4).strip()
            return f"set {target} to office_calculate_sheet_summary({sheet}, {sheet_name}, {col})"

        # detect csv delimiter in <csv_path> into <target>
        m_delim = re.match(
            r"^detect\s+csv\s+delimiter\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_delim:
            csv_path = m_delim.group(1).strip()
            target = m_delim.group(2).strip()
            return f"set {target} to office_detect_csv_delimiter({csv_path})"

        # read csv header from <csv_path> into <target>
        m_hdr = re.match(
            r"^read\s+csv\s+header\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hdr:
            csv_path = m_hdr.group(1).strip()
            target = m_hdr.group(2).strip()
            return f"set {target} to office_read_csv_header({csv_path})"

        # add table with headers <headers> and rows <rows> to [document] <doc>
        m_tbl = re.match(
            r"^add\s+table\s+with\s+headers\s+(.+?)\s+and\s+rows\s+(.+?)\s+to\s+(?:(?:word\s+)?document\s+)?([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tbl:
            headers = m_tbl.group(1).strip()
            rows = m_tbl.group(2).strip()
            doc = m_tbl.group(3).strip()
            return f"office_create_table_in_document({doc}, {headers}, {rows})"

        # add bulleted list <items> to [document] <doc>
        m_bullet = re.match(
            r"^add\s+bullet(?:ed)?\s+list\s+(.+?)\s+to\s+(?:(?:word\s+)?document\s+)?([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bullet:
            items = m_bullet.group(1).strip()
            doc = m_bullet.group(2).strip()
            return f"office_add_bulleted_list({doc}, {items})"

        # add numbered list <items> to [document] <doc>
        m_num = re.match(
            r"^add\s+numbered\s+list\s+(.+?)\s+to\s+(?:(?:word\s+)?document\s+)?([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_num:
            items = m_num.group(1).strip()
            doc = m_num.group(2).strip()
            return f"office_add_numbered_list({doc}, {items})"

        # set cell at row <row> col <col> in sheet <sheet_name> of [spreadsheet] <sheet> to <val>
        m_set_cell = re.match(
            r"^set\s+cell\s+at\s+row\s+(.+?)\s+(?:col|column)\s+(.+?)\s+in\s+sheet\s+(.+?)\s+of\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)\s+to\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_set_cell:
            row = m_set_cell.group(1).strip()
            col = m_set_cell.group(2).strip()
            sheet_name = m_set_cell.group(3).strip()
            sheet = m_set_cell.group(4).strip()
            val = m_set_cell.group(5).strip()
            return f"office_set_spreadsheet_cell({sheet}, {sheet_name}, {row}, {col}, {val})"

        # get cell at row <row> col <col> in sheet <sheet_name> of [spreadsheet] <sheet> into <target>
        m_get_cell = re.match(
            r"^get\s+cell\s+at\s+row\s+(.+?)\s+(?:col|column)\s+(.+?)\s+in\s+sheet\s+(.+?)\s+of\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_get_cell:
            row = m_get_cell.group(1).strip()
            col = m_get_cell.group(2).strip()
            sheet_name = m_get_cell.group(3).strip()
            sheet = m_get_cell.group(4).strip()
            target = m_get_cell.group(5).strip()
            return f"set {target} to office_get_spreadsheet_cell({sheet}, {sheet_name}, {row}, {col})"

        # find and replace <find_text> with <replace_text> in [document] <doc> [into <target>]
        m_replace = re.match(
            r"^(?:find\s+and\s+)?replace\s+(.+?)\s+with\s+(.+?)\s+in\s+(?:(?:word\s+)?document\s+)?([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            s,
            re.IGNORECASE,
        )
        if m_replace:
            find_txt = m_replace.group(1).strip()
            rep_txt = m_replace.group(2).strip()
            doc = m_replace.group(3).strip()
            target = m_replace.group(4)
            if target:
                return f"set {target.strip()} to office_find_replace_in_document({doc}, {find_txt}, {rep_txt})"
            return f"office_find_replace_in_document({doc}, {find_txt}, {rep_txt})"

        # list worksheets in [spreadsheet] <sheet> into <target>
        m_list_ws = re.match(
            r"^list\s+worksheet(?:s|\s+names)?\s+in\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_list_ws:
            sheet = m_list_ws.group(1).strip()
            target = m_list_ws.group(2).strip()
            return f"set {target} to office_list_worksheet_names({sheet})"

        # delete worksheet <sheet_name> from [spreadsheet] <sheet>
        m_del_ws = re.match(
            r"^delete\s+worksheet\s+(.+?)\s+from\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_del_ws:
            sheet_name = m_del_ws.group(1).strip()
            sheet = m_del_ws.group(2).strip()
            return f"office_delete_worksheet({sheet}, {sheet_name})"

        # rename worksheet <old_name> to <new_name> in [spreadsheet] <sheet>
        m_ren_ws = re.match(
            r"^rename\s+worksheet\s+(.+?)\s+to\s+(.+?)\s+in\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ren_ws:
            old_name = m_ren_ws.group(1).strip()
            new_name = m_ren_ws.group(2).strip()
            sheet = m_ren_ws.group(3).strip()
            return f"office_rename_worksheet({sheet}, {old_name}, {new_name})"

        # sort sheet <sheet_name> in [spreadsheet] <sheet> by column <col_idx> [descending] into <target>
        m_sort = re.match(
            r"^sort\s+sheet\s+(.+?)\s+in\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)\s+by\s+column\s+(.+?)(?:\s+(descending))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sort:
            sheet_name = m_sort.group(1).strip()
            sheet = m_sort.group(2).strip()
            col_idx = m_sort.group(3).strip()
            desc = "True" if m_sort.group(4) else "False"
            target = m_sort.group(5).strip()
            return f"set {target} to office_sort_spreadsheet_by_column({sheet}, {sheet_name}, {col_idx}, {desc})"

        # filter sheet <sheet_name> in [spreadsheet] <sheet> where column <col_idx> matches <filter_fn> into <target>
        m_filter = re.match(
            r"^filter\s+sheet\s+(.+?)\s+in\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)\s+where\s+column\s+(.+?)\s+matches\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_filter:
            sheet_name = m_filter.group(1).strip()
            sheet = m_filter.group(2).strip()
            col_idx = m_filter.group(3).strip()
            filter_fn = m_filter.group(4).strip()
            target = m_filter.group(5).strip()
            return f"set {target} to office_filter_spreadsheet_rows({sheet}, {sheet_name}, {col_idx}, {filter_fn})"

        # export sheet <sheet_name> in [spreadsheet] <sheet> to json <json_path> [into <target>]
        m_exp_json = re.match(
            r"^export\s+sheet\s+(.+?)\s+in\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)\s+to\s+json\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            s,
            re.IGNORECASE,
        )
        if m_exp_json:
            sheet_name = m_exp_json.group(1).strip()
            sheet = m_exp_json.group(2).strip()
            json_path = m_exp_json.group(3).strip()
            target = m_exp_json.group(4)
            if target:
                return f"set {target.strip()} to office_export_sheet_to_json({sheet}, {sheet_name}, {json_path})"
            return f"office_export_sheet_to_json({sheet}, {sheet_name}, {json_path})"

        # import json <json_path> into sheet <sheet_name> of [spreadsheet] <sheet> [into <target>]
        m_imp_json = re.match(
            r"^import\s+json\s+(.+?)\s+into\s+sheet\s+(.+?)\s+of\s+(?:spreadsheet\s+)?([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            s,
            re.IGNORECASE,
        )
        if m_imp_json:
            json_path = m_imp_json.group(1).strip()
            sheet_name = m_imp_json.group(2).strip()
            sheet = m_imp_json.group(3).strip()
            target = m_imp_json.group(4)
            if target:
                return f"set {target.strip()} to office_import_json_to_sheet({sheet}, {json_path}, {sheet_name})"
            return f"office_import_json_to_sheet({sheet}, {json_path}, {sheet_name})"

        # count words in [document] <doc> into <target>
        m_words = re.match(
            r"^count\s+words\s+in\s+(?:(?:word\s+)?document\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_words:
            doc = m_words.group(1).strip()
            target = m_words.group(2).strip()
            return f"set {target} to office_count_words_in_document({doc})"

        # count characters in [document] <doc> into <target>
        m_chars = re.match(
            r"^count\s+characters\s+in\s+(?:(?:word\s+)?document\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_chars:
            doc = m_chars.group(1).strip()
            target = m_chars.group(2).strip()
            return f"set {target} to office_count_characters_in_document({doc})"

        # extract document metadata from <doc_or_path> into <target>
        m_meta = re.match(
            r"^extract\s+document\s+metadata\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_meta:
            doc_or_path = m_meta.group(1).strip()
            target = m_meta.group(2).strip()
            return f"set {target} to office_extract_document_metadata({doc_or_path})"

        # evaluate spreadsheet dag <cells> into <target>
        m_dag = re.match(
            r"^evaluate\s+spreadsheet\s+dag\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dag:
            cells, target = m_dag.group(1).strip(), m_dag.group(2).strip()
            return f"set {target} to office_spreadsheet_dag_eval({cells})"

        # create multidimensional pivot table from <records> rows <row_dims> values <val_col> [agg <agg_fn>] into <target>
        m_piv = re.match(
            r"^create\s+multidimensional\s+pivot\s+table\s+from\s+(.+?)\s+rows\s+(.+?)\s+values\s+(.+?)(?:\s+agg\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_piv:
            recs = m_piv.group(1).strip()
            rows = m_piv.group(2).strip()
            val = m_piv.group(3).strip()
            agg = m_piv.group(4).strip() if m_piv.group(4) else '"sum"'
            target = m_piv.group(5).strip()
            if not (val.startswith('"') or val.startswith("'")):
                val = f'"{val}"'
            if not (agg.startswith('"') or agg.startswith("'")):
                agg = f'"{agg}"'
            return f"set {target} to office_pivot_table_aggregate({recs}, {rows}, {val}, aggregation={agg})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Office domain does not currently define declarative blocks")
