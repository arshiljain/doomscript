"""Independent Domain Parser for Databases and SQL language constructs."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.db.spec import QuerySpec, WhereClause


class DBDomainParser(DomainParser):
    """Independent parser for Databases and SQL syntax (inspect table, execute sql, query blocks)."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        # inspect table <name> [into <target>]
        m = re.match(
            r"^inspect\s+table\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m:
            tbl_name = m.group(1)
            target = m.group(2) or "table_schema"
            return f'set {target} to inspect_table_schema("{tbl_name}")'

        # schema of <table> [into <target>]
        m2 = re.match(
            r"^schema\s+of\s+(?:table\s+)?([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m2:
            tbl_name = m2.group(1)
            target = m2.group(2) or "table_schema"
            return f'set {target} to inspect_table_schema("{tbl_name}")'

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        # execute sql / query db / query sql "<query>" [with <params>] [into <target>]
        # OR query "<table_or_query>" [into <target>] / query <table_or_query> [into <target>]
        m = re.match(
            r'^(?:execute\s+sql|query(?:\s+(?:db|sql))?)\s+(?:"(.*?)"|\'(.*?)\'|([A-Za-z_]\w*))(?:\s+with\s+(.+?))?(?:\s+into\s+([A-Za-z_]\w*))?$',
            line.strip(),
            re.IGNORECASE,
        )
        if m:
            sql_str = m.group(1) if m.group(1) is not None else (m.group(2) if m.group(2) is not None else m.group(3))
            params = m.group(4)
            target = m.group(5)
            s_upper = sql_str.upper().strip()
            if not any(k in s_upper for k in ("SELECT ", "INSERT ", "UPDATE ", "DELETE ", "CREATE ", "DROP ", "PRAGMA ")):
                clean_sql = f"SELECT * FROM {sql_str}".replace('"', '\\"')
            else:
                clean_sql = sql_str.replace('"', '\\"')
            call_expr = (
                f'execute_raw_sql("{clean_sql}", params={params})'
                if params
                else f'execute_raw_sql("{clean_sql}")'
            )
            if target:
                return f"set {target} to {call_expr}"
            return call_expr

        # create wal logger into <target>
        m_wal = re.match(
            r"^create\s+wal\s+(?:logger|log)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_wal:
            target = m_wal.group(1).strip()
            return f"set {target} to db_wal_create()"

        # create mvcc engine into <target>
        m_mvcc = re.match(
            r"^create\s+mvcc\s+(?:engine|store)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_mvcc:
            target = m_mvcc.group(1).strip()
            return f"set {target} to db_mvcc_create()"

        # insert into <table> values <expr>
        ins_m = re.match(
            r"^insert\s+into\s+([A-Za-z_]\w*)\s+values\s+(.+)$",
            line.strip(),
            re.IGNORECASE,
        )
        if ins_m:
            tbl = ins_m.group(1)
            expr = ins_m.group(2).strip()
            return f'insert_rows("{tbl}", {expr})'

        # find (all)? rows in <table> [where <cond>] into <target>
        find_m = re.match(
            r"^find\s+(?:all\s+)?rows\s+in\s+([A-Za-z_]\w*)(?:\s+where\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if find_m:
            tbl = find_m.group(1)
            where_part = find_m.group(2)
            target = find_m.group(3)
            if where_part:
                clean_where = where_part.strip().replace('"', '\\"')
                return f'set {target} to db_find_rows("{tbl}", "{clean_where}")'
            return f'set {target} to db_find_rows("{tbl}")'

        # query <table> where <cond> into <target>
        q_where_m = re.match(
            r"^query\s+([A-Za-z_]\w*)\s+where\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if q_where_m:
            tbl = q_where_m.group(1)
            cond = q_where_m.group(2).strip().replace('"', '\\"')
            target = q_where_m.group(3)
            return f'set {target} to db_find_rows("{tbl}", "{cond}")'

        # count rows in <table> into <target>
        count_m = re.match(
            r"^count\s+rows\s+in\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if count_m:
            tbl = count_m.group(1)
            target = count_m.group(2)
            return f'set {target} to db_count_rows("{tbl}")'

        # connect to (sqlite|database) <path> [into <target>]
        conn_m = re.match(
            r"^connect\s+to\s+(?:sqlite|database)\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if conn_m:
            path, target = conn_m.group(1).strip(), conn_m.group(2)
            call = f"db_connect({path})"
            return f"set {target} to {call}" if target else call

        # count rows in table <tbl> [where <cond>] [using <db>] into <target>
        count_w_m = re.match(
            r"^count\s+rows\s+in\s+table\s+([A-Za-z_]\w*|[\"'][^\"']+[\"'])(?:\s+where\s+(.+?))?(?:\s+using\s+([A-Za-z_]\w*))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if count_w_m:
            tbl, cond, db_var, target = count_w_m.group(1).strip().strip("'\""), count_w_m.group(2), count_w_m.group(3), count_w_m.group(4)
            cond_expr = cond.strip() if cond else '"1=1"'
            db_arg = f", db={db_var}" if db_var else ""
            return f'set {target} to db_count_rows_where("{tbl}", {cond_expr}{db_arg})'

        # upsert record <data> into table <tbl> (on conflict|with key) <col> [using <db>] [into <target>]
        upsert_m = re.match(
            r"^upsert\s+record\s+(.+?)\s+into\s+table\s+([A-Za-z_]\w*|[\"'][^\"']+[\"'])\s+(?:on\s+conflict|with\s+key)\s+(.+?)(?:\s+using\s+([A-Za-z_]\w*))?(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if upsert_m:
            data = upsert_m.group(1).strip()
            tbl = upsert_m.group(2).strip().strip("'\"")
            col = upsert_m.group(3).strip()
            db_var = upsert_m.group(4)
            target = upsert_m.group(5)
            db_arg = f", db={db_var}" if db_var else ""
            call_expr = f'db_upsert_record({data}, "{tbl}", {col}{db_arg})'
            return f"set {target} to {call_expr}" if target else call_expr

        # optimize database [using <db>] [into <target>]
        opt_m = re.match(
            r"^optimize\s+database(?:\s+using\s+([A-Za-z_]\w*))?(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if opt_m:
            db_var = opt_m.group(1) or "None"
            target = opt_m.group(2)
            call_expr = f"db_optimize({db_var})"
            return f"set {target} to {call_expr}" if target else call_expr

        # backup database [<db>] to <path> [into <target>]
        backup_m = re.match(
            r"^backup\s+database(?:\s+([A-Za-z_]\w*))?\s+to\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if backup_m:
            db_var = backup_m.group(1) or "None"
            path = backup_m.group(2).strip()
            target = backup_m.group(3)
            call_expr = f"db_backup({db_var}, {path})"
            return f"set {target} to {call_expr}" if target else call_expr

        # truncate table <tbl> [using <db>] [into <target>]
        trunc_m = re.match(
            r"^truncate\s+table\s+([A-Za-z_]\w*|[\"'][^\"']+[\"'])(?:\s+using\s+([A-Za-z_]\w*))?(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if trunc_m:
            tbl = trunc_m.group(1).strip().strip("'\"")
            db_var = trunc_m.group(2)
            target = trunc_m.group(3)
            db_arg = f", db={db_var}" if db_var else ""
            call_expr = f'db_truncate_table("{tbl}"{db_arg})'
            return f"set {target} to {call_expr}" if target else call_expr

        # inspect (database\s+schema\s+of|schema\s+of\s+table)\s+(.+?)\s+into\s+([A-Za-z_]\w*)
        schema_m = re.match(
            r"^(?:inspect\s+database\s+schema\s+of|inspect\s+schema\s+of|schema\s+of\s+table|inspect\s+schema\s+of\s+table)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if schema_m:
            target_expr, target_var = schema_m.group(1).strip(), schema_m.group(2).strip()
            return f"set {target_var} to db_inspect_schema({target_expr})"

        # create index <idx> on <table> (<col>) [into <target>]
        m_cidx = re.match(
            r"^create\s+index\s+(.+?)\s+on\s+(.+?)\s*\(\s*(.+?)\s*\)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_cidx:
            idx, tbl, col, target = m_cidx.group(1).strip(), m_cidx.group(2).strip(), m_cidx.group(3).strip(), m_cidx.group(4)
            call = f"db_create_index(None, {tbl}, {col}, {idx})"
            return f"set {target} to {call}" if target else call

        # drop index <idx> [into <target>]
        m_didx = re.match(
            r"^drop\s+index\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_didx:
            idx, target = m_didx.group(1).strip(), m_didx.group(2)
            call = f"db_drop_index(None, {idx})"
            return f"set {target} to {call}" if target else call

        # add column <col> [of type <type>] to table <table>
        m_acol = re.match(
            r"^add\s+column\s+(.+?)(?:\s+of\s+type\s+(.+?))?\s+to\s+table\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_acol:
            col, ctype, tbl, target = m_acol.group(1).strip(), m_acol.group(2), m_acol.group(3).strip(), m_acol.group(4)
            ct_arg = f", {ctype.strip()}" if ctype else ""
            call = f"db_add_column(None, {tbl}, {col}{ct_arg})"
            return f"set {target} to {call}" if target else call

        # drop column <col> from table <table>
        m_dcol = re.match(
            r"^drop\s+column\s+(.+?)\s+from\s+table\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_dcol:
            col, tbl, target = m_dcol.group(1).strip(), m_dcol.group(2).strip(), m_dcol.group(3)
            call = f"db_drop_column_sqlite(None, {tbl}, {col})"
            return f"set {target} to {call}" if target else call

        # vacuum database
        m_vac = re.match(
            r"^vacuum\s+database(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_vac:
            target = m_vac.group(1)
            call = "db_vacuum(None)"
            return f"set {target} to {call}" if target else call

        # analyze database
        m_ana = re.match(
            r"^analyze\s+database(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_ana:
            target = m_ana.group(1)
            call = "db_analyze(None)"
            return f"set {target} to {call}" if target else call

        # list tables [in database] into <target>
        m_lt = re.match(
            r"^list\s+tables(?:\s+in\s+database)?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_lt:
            target = m_lt.group(1).strip()
            return f"set {target} to db_list_tables(None)"

        # list views [in database] into <target>
        m_lv = re.match(
            r"^list\s+views(?:\s+in\s+database)?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_lv:
            target = m_lv.group(1).strip()
            return f"set {target} to db_list_views(None)"

        # list indices [for table <table>] into <target>
        m_li = re.match(
            r"^list\s+indices(?:\s+for\s+table\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_li:
            tbl, target = m_li.group(1), m_li.group(2).strip()
            tbl_arg = f", {tbl.strip()}" if tbl else ""
            return f"set {target} to db_list_indices(None{tbl_arg})"

        # check if table <table> exists into <target>
        m_te = re.match(
            r"^(?:check\s+if\s+)?table\s+(.+?)\s+exists\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_te:
            tbl, target = m_te.group(1).strip(), m_te.group(2).strip()
            return f"set {target} to db_table_exists(None, {tbl})"

        # bulk insert <records> into table <table> [with chunk size <cs>] into <target>
        m_bi = re.match(
            r"^bulk\s+insert\s+(.+?)\s+into\s+table\s+(.+?)(?:\s+with\s+chunk\s+size\s+(\d+))?(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bi:
            recs, tbl, cs, target = m_bi.group(1).strip(), m_bi.group(2).strip(), m_bi.group(3), m_bi.group(4)
            cs_arg = f", {cs}" if cs else ""
            call = f"db_bulk_insert(None, {tbl}, {recs}{cs_arg})"
            return f"set {target} to {call}" if target else call

        # export table <table> to csv <path> into <target>
        m_ecsv = re.match(
            r"^export\s+table\s+(.+?)\s+to\s+csv\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_ecsv:
            tbl, path, target = m_ecsv.group(1).strip(), m_ecsv.group(2).strip(), m_ecsv.group(3)
            call = f"db_export_table_to_csv(None, {tbl}, {path})"
            return f"set {target} to {call}" if target else call

        # import csv <path> into table <table> into <target>
        m_icsv = re.match(
            r"^import\s+csv\s+(.+?)\s+into\s+table\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_icsv:
            path, tbl, target = m_icsv.group(1).strip(), m_icsv.group(2).strip(), m_icsv.group(3)
            call = f"db_import_csv_to_table(None, {path}, {tbl})"
            return f"set {target} to {call}" if target else call

        # get foreign keys for table <table> into <target>
        m_gfk = re.match(
            r"^get\s+foreign\s+keys\s+for\s+table\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_gfk:
            tbl, target = m_gfk.group(1).strip(), m_gfk.group(2).strip()
            return f"set {target} to db_get_foreign_keys(None, {tbl})"

        # check foreign key integrity into <target>
        m_cfk = re.match(
            r"^check\s+foreign\s+key\s+integrity\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_cfk:
            target = m_cfk.group(1).strip()
            return f"set {target} to db_check_foreign_key_integrity(None)"

        # export ddl for table <table> into <target>
        m_eddl = re.match(
            r"^export\s+ddl\s+for\s+table\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_eddl:
            tbl, target = m_eddl.group(1).strip(), m_eddl.group(2).strip()
            return f"set {target} to db_export_ddl(None, {tbl})"

        # column types for table <table> into <target>
        m_cty = re.match(
            r"^column\s+types\s+for\s+table\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_cty:
            tbl, target = m_cty.group(1).strip(), m_cty.group(2).strip()
            return f"set {target} to db_table_column_types(None, {tbl})"

        # database size in bytes into <target>
        m_dsz = re.match(
            r"^(?:get\s+)?database\s+size\s+in\s+bytes\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_dsz:
            target = m_dsz.group(1).strip()
            return f"set {target} to db_database_size_bytes(None)"

        # count distinct <col> in table <table> into <target>
        m_cdist = re.match(
            r"^count\s+distinct\s+(.+?)\s+in\s+table\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_cdist:
            col, tbl, target = m_cdist.group(1).strip(), m_cdist.group(2).strip(), m_cdist.group(3).strip()
            return f"set {target} to db_count_distinct_values(None, {tbl}, {col})"

        # clone schema of table <src> into <dst> [into <target>]
        m_cln = re.match(
            r"^clone\s+schema\s+of\s+table\s+(.+?)\s+into\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_cln:
            src, dst, target = m_cln.group(1).strip(), m_cln.group(2).strip(), m_cln.group(3)
            call = f"db_clone_table_schema(None, {src}, {dst})"
            return f"set {target} to {call}" if target else call

        # create bplus tree index [with order <order>] into <target>
        m_bpt = re.match(
            r"^create\s+bplus\s+tree\s+index(?:\s+with\s+order\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bpt:
            order = m_bpt.group(1) or "4"
            target = m_bpt.group(2).strip()
            return f"set {target} to db_bplus_tree_create({order})"

        # insert key <key> with value <val> into bplus tree <tree>
        m_bpt_ins = re.match(
            r"^insert\s+key\s+(.+?)\s+with\s+value\s+(.+?)\s+into\s+bplus\s+tree\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bpt_ins:
            key, val, tree = m_bpt_ins.group(1).strip(), m_bpt_ins.group(2).strip(), m_bpt_ins.group(3).strip()
            return f"db_bplus_tree_insert({tree}, {key}, {val})"

        # search key <key> in bplus tree <tree> into <target>
        m_bpt_sch = re.match(
            r"^search\s+key\s+(.+?)\s+in\s+bplus\s+tree\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bpt_sch:
            key, tree, target = m_bpt_sch.group(1).strip(), m_bpt_sch.group(2).strip(), m_bpt_sch.group(3).strip()
            return f"set {target} to db_bplus_tree_search({tree}, {key})"

        # scan range from <min_key> to <max_key> in bplus tree <tree> into <target>
        m_bpt_rng = re.match(
            r"^scan\s+range\s+from\s+(.+?)\s+to\s+(.+?)\s+in\s+bplus\s+tree\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bpt_rng:
            min_k, max_k, tree, target = m_bpt_rng.group(1).strip(), m_bpt_rng.group(2).strip(), m_bpt_rng.group(3).strip(), m_bpt_rng.group(4).strip()
            return f"set {target} to db_bplus_tree_range({tree}, {min_k}, {max_k})"

        # compress bitmap <bits> into <target>
        m_bmp_c = re.match(
            r"^compress\s+bitmap\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bmp_c:
            bits, target = m_bmp_c.group(1).strip(), m_bmp_c.group(2).strip()
            return f"set {target} to db_bitmap_compress({bits})"

        # decompress bitmap <comp> into <target>
        m_bmp_d = re.match(
            r"^decompress\s+bitmap\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bmp_d:
            comp, target = m_bmp_d.group(1).strip(), m_bmp_d.group(2).strip()
            return f"set {target} to db_bitmap_decompress({comp})"

        # bitmap and <c1> and <c2> into <target>
        m_bmp_and = re.match(
            r"^bitmap\s+and\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bmp_and:
            c1, c2, target = m_bmp_and.group(1).strip(), m_bmp_and.group(2).strip(), m_bmp_and.group(3).strip()
            return f"set {target} to db_bitmap_and({c1}, {c2})"

        # bitmap or <c1> and <c2> into <target>
        m_bmp_or = re.match(
            r"^bitmap\s+or\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bmp_or:
            c1, c2, target = m_bmp_or.group(1).strip(), m_bmp_or.group(2).strip(), m_bmp_or.group(3).strip()
            return f"set {target} to db_bitmap_or({c1}, {c2})"

        # bitmap not <c1> [with <n> bits] into <target>
        m_bmp_not = re.match(
            r"^bitmap\s+not\s+(.+?)(?:\s+with\s+(\d+)\s+bits)?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bmp_not:
            c1, n_bits, target = m_bmp_not.group(1).strip(), m_bmp_not.group(2), m_bmp_not.group(3).strip()
            nb_arg = f", total_bits={n_bits}" if n_bits else ""
            return f"set {target} to db_bitmap_not({c1}{nb_arg})"

        # query bitmap indices in <comp> into <target>
        m_bmp_q = re.match(
            r"^query\s+bitmap\s+indices\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bmp_q:
            comp, target = m_bmp_q.group(1).strip(), m_bmp_q.group(2).strip()
            return f"set {target} to db_bitmap_query_indices({comp})"

        # create lsm tree [with threshold <thresh>] into <target>
        m_lsm_c = re.match(
            r"^create\s+lsm\s+tree(?:\s+with\s+threshold\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_lsm_c:
            th = m_lsm_c.group(1) or "4"
            target = m_lsm_c.group(2).strip()
            return f"set {target} to db_lsm_create({th})"

        # lsm put <key> with value <val> into <tree>
        m_lsm_p = re.match(
            r"^lsm\s+put\s+(.+?)\s+with\s+value\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_lsm_p:
            k, v, tree = m_lsm_p.group(1).strip(), m_lsm_p.group(2).strip(), m_lsm_p.group(3).strip()
            return f"db_lsm_put({tree}, {k}, {v})"

        # lsm get <key> from <tree> into <target>
        m_lsm_g = re.match(
            r"^lsm\s+get\s+(.+?)\s+from\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_lsm_g:
            k, tree, target = m_lsm_g.group(1).strip(), m_lsm_g.group(2).strip(), m_lsm_g.group(3).strip()
            return f"set {target} to db_lsm_get({tree}, {k})"

        # lsm delete <key> from <tree>
        m_lsm_d = re.match(
            r"^lsm\s+delete\s+(.+?)\s+from\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_lsm_d:
            k, tree = m_lsm_d.group(1).strip(), m_lsm_d.group(2).strip()
            return f"db_lsm_delete({tree}, {k})"

        # lsm compact <tree> into <target>
        m_lsm_cmp = re.match(
            r"^lsm\s+compact\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_lsm_cmp:
            tree, target = m_lsm_cmp.group(1).strip(), m_lsm_cmp.group(2).strip()
            return f"set {target} to db_lsm_compact({tree})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[QuerySpec, str]:
        # query <table> [into <target>]:
        m = re.match(
            r"^query\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?:?$",
            header.strip(),
            re.IGNORECASE,
        )
        if not m:
            raise SyntaxError(f"Invalid query header: {header}")

        tbl_name = m.group(1)
        target = m.group(2) or "query_results"

        spec = QuerySpec(table=tbl_name, target_var=target)

        for l_no, raw_line in body_lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # select <col1>, <col2>, ...
            sel_m = re.match(r"^select\s+(.+)$", line, re.IGNORECASE)
            if sel_m:
                raw_cols = sel_m.group(1).split(",")
                spec.columns = [c.strip().strip("\"'") for c in raw_cols if c.strip()]
                continue

            # where ...
            where_m = re.match(r"^where\s+(.+)$", line, re.IGNORECASE)
            if where_m:
                cond_str = where_m.group(1).strip()
                # Split on ' and '
                conds = re.split(r"\s+and\s+", cond_str, flags=re.IGNORECASE)
                for cond in conds:
                    w = self._parse_single_condition(cond)
                    if w:
                        spec.where.append(w)
                continue

            # order by <col> [descending|ascending]
            ord_m = re.match(
                r"^order\s+by\s+([A-Za-z_]\w*)(?:\s+(descending|ascending|desc|asc))?",
                line,
                re.IGNORECASE,
            )
            if ord_m:
                spec.order_by = ord_m.group(1)
                d_str = (ord_m.group(2) or "").lower()
                spec.order_descending = d_str in ("descending", "desc")
                continue

            # limit <n>
            lim_m = re.match(r"^limit\s+(\d+)$", line, re.IGNORECASE)
            if lim_m:
                spec.limit = int(lim_m.group(1))
                continue

        errors = spec.validate()
        if errors:
            raise SyntaxError(f"Query validation error for '{tbl_name}': {'; '.join(errors)}")

        return spec, target

    def _parse_single_condition(self, cond: str) -> Optional[WhereClause]:
        cond = cond.strip()
        # Patterns:
        # <col> is over / greater than / > <val>
        m_gt = re.match(r"^([A-Za-z_]\w*)\s+(?:is\s+over|is\s+greater\s+than|>)\s+(.+)$", cond, re.IGNORECASE)
        if m_gt:
            return WhereClause(column=m_gt.group(1), operator=">", value=self._eval_value(m_gt.group(2)))

        # <col> is under / less than / < <val>
        m_lt = re.match(r"^([A-Za-z_]\w*)\s+(?:is\s+under|is\s+less\s+than|<)\s+(.+)$", cond, re.IGNORECASE)
        if m_lt:
            return WhereClause(column=m_lt.group(1), operator="<", value=self._eval_value(m_lt.group(2)))

        # <col> is at least / >= <val>
        m_gte = re.match(r"^([A-Za-z_]\w*)\s+(?:is\s+at\s+least|>=)\s+(.+)$", cond, re.IGNORECASE)
        if m_gte:
            return WhereClause(column=m_gte.group(1), operator=">=", value=self._eval_value(m_gte.group(2)))

        # <col> is at most / <= <val>
        m_lte = re.match(r"^([A-Za-z_]\w*)\s+(?:is\s+at\s+most|<=)\s+(.+)$", cond, re.IGNORECASE)
        if m_lte:
            return WhereClause(column=m_lte.group(1), operator="<=", value=self._eval_value(m_lte.group(2)))

        # <col> is not / != <val>
        m_ne = re.match(r"^([A-Za-z_]\w*)\s+(?:is\s+not|!=)\s+(.+)$", cond, re.IGNORECASE)
        if m_ne:
            return WhereClause(column=m_ne.group(1), operator="!=", value=self._eval_value(m_ne.group(2)))

        # <col> equals / is / == <val>
        m_eq = re.match(r"^([A-Za-z_]\w*)\s+(?:equals|is|==|=)\s+(.+)$", cond, re.IGNORECASE)
        if m_eq:
            return WhereClause(column=m_eq.group(1), operator="=", value=self._eval_value(m_eq.group(2)))

        return None

    def _eval_value(self, val_str: str) -> Any:
        val_str = val_str.strip()
        try:
            return eval(val_str, {}, {})
        except Exception:
            return val_str.strip("\"'")
