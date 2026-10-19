"""Independent Domain Parser for Data Engineering language constructs."""

import re
from typing import Any, Dict, List, Optional, Tuple
import ast
from doomscript.domains.base import DomainParser, DomainIR
from doomscript.domains.data.spec import (
    PipelineSpec,
    ValidationRule,
    DedupeStep,
    FilterStep,
    FillNaStep,
    DeriveStep,
    JoinStep,
    SchemaContractStep,
    WindowStep,
    GroupByStep,
    SortStep,
    SinkStep,
)


class DataDomainParser(DomainParser):
    """Independent parser for Data Engineering syntax (inspect, clean, join, pipeline)."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        # inspect dataset <data> [into <target>]
        m = re.match(
            r"^inspect\s+dataset\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m:
            data_var = m.group(1)
            target = m.group(2) or "dataset_inspection"
            return f"set {target} to inspect_dataset({data_var})"

        # profile <data> into <target>
        m2 = re.match(
            r"^profile\s+(?:dataset\s+)?([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m2:
            data_var = m2.group(1)
            target = m2.group(2) or "dataset_profile"
            return f"set {target} to profile_dataset({data_var})"

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        # clean <data> by removing nulls in "<col>" into <target>
        clean_null_m = re.match(
            r"^clean\s+([A-Za-z_]\w*)\s+by\s+removing\s+nulls\s+in\s+[\"']([^\"']+)[\"'](?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if clean_null_m:
            data_var = clean_null_m.group(1)
            col = clean_null_m.group(2)
            target = clean_null_m.group(3) or data_var
            return f'set {target} to clean_dataset({data_var}, remove_nulls_in="{col}")'

        # clean <data> by removing duplicates by "<col>" into <target>
        clean_dup_m = re.match(
            r"^clean\s+([A-Za-z_]\w*)\s+by\s+removing\s+duplicates(?:\s+by\s+[\"']([^\"']+)[\"'])?(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if clean_dup_m:
            data_var = clean_dup_m.group(1)
            col = clean_dup_m.group(2)
            target = clean_dup_m.group(3) or data_var
            if col:
                return f'set {target} to clean_dataset({data_var}, dedupe_by="{col}")'
            return f"set {target} to clean_dataset({data_var})"

        # remove duplicates from <data> [by "<col>"] [into <target>]
        rem_dup_m = re.match(
            r"^remove\s+duplicates\s+from\s+([A-Za-z_]\w*)(?:\s+by\s+[\"']([^\"']+)[\"'])?(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if rem_dup_m:
            data_var = rem_dup_m.group(1)
            col = rem_dup_m.group(2)
            target = rem_dup_m.group(3) or data_var
            if col:
                return f'set {target} to clean_dataset({data_var}, dedupe_by="{col}")'
            return f"set {target} to clean_dataset({data_var})"

        # remove nulls from <data> in "<col>" [into <target>]
        rem_null_m = re.match(
            r"^remove\s+nulls\s+from\s+([A-Za-z_]\w*)\s+in\s+[\"']([^\"']+)[\"'](?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if rem_null_m:
            data_var = rem_null_m.group(1)
            col = rem_null_m.group(2)
            target = rem_null_m.group(3) or data_var
            return f'set {target} to clean_dataset({data_var}, remove_nulls_in="{col}")'

        # filter <data> where <cond> into <target>
        filter_m = re.match(
            r"^filter\s+([A-Za-z_]\w*)\s+where\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if filter_m:
            data_var = filter_m.group(1)
            cond = filter_m.group(2).strip().replace('"', '\\"')
            target = filter_m.group(3)
            return f'set {target} to filter_dataset({data_var}, "{cond}")'

        # sort <data> by "<col>" [descending|desc] into <target>
        sort_m = re.match(
            r"^sort\s+([A-Za-z_]\w*)\s+by\s+[\"']?([A-Za-z_]\w*)[\"']?(?:\s+(descending|desc|ascending|asc))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if sort_m:
            data_var = sort_m.group(1)
            col = sort_m.group(2)
            direction = sort_m.group(3) or "asc"
            descending = "True" if direction.lower() in ("desc", "descending") else "False"
            target = sort_m.group(4)
            return f'set {target} to sort_dataset({data_var}, "{col}", descending={descending})'

        # group <data> by "<col>" (calculating|with) <agg> "<col2>" into <target>
        group_m = re.match(
            r"^group\s+([A-Za-z_]\w*)\s+by\s+[\"']?([A-Za-z_]\w*)[\"']?\s+(?:calculating|with)\s+([A-Za-z_]\w*)\s+[\"']?([A-Za-z_]\w*)[\"']?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if group_m:
            data_var = group_m.group(1)
            col = group_m.group(2)
            agg_fn = group_m.group(3).lower()
            agg_col = group_m.group(4)
            target = group_m.group(5)
            return f'set {target} to group_dataset({data_var}, "{col}", "{agg_fn}", "{agg_col}")'

        # join <left> (with|and) <right> on "<key>" as (inner|left|right|outer) into <target>
        join_m = re.match(
            r"^join\s+([A-Za-z_]\w*)\s+(?:and|with)\s+([A-Za-z_]\w*)\s+on\s+[\"']([^\"']+)[\"'](?:\s+as\s+(inner|left|right|outer))?(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if join_m:
            l_var = join_m.group(1)
            r_var = join_m.group(2)
            key = join_m.group(3)
            how = join_m.group(4) or "inner"
            target = join_m.group(5) or "joined_dataset"
            return f'set {target} to join_datasets({l_var}, {r_var}, on="{key}", how="{how}")'

        # pipeline (explain|dry-run) <name> [into <target>]
        pipe_diag_m = re.match(
            r"^(?:explain\s+pipeline|pipeline\s+(?:explain|dry-run))\s+[\"']?([A-Za-z_]\w*)[\"']?(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if pipe_diag_m:
            p_name = pipe_diag_m.group(1)
            target = pipe_diag_m.group(2) or "pipeline_plan"
            return f'set {target} to explain_pipeline("{p_name}")'

        # Batch 2: Advanced Spoken English Tabular Operations
        # pivot table <df> with index <idx>, columns <cols>, values <vals>[, agg <agg>] into <target>
        piv_m = re.match(
            r"^pivot\s+table\s+([A-Za-z_]\w*)\s+with\s+index\s+(.+?),\s*columns\s+(.+?),\s*values\s+(.+?)(?:,\s*agg\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if piv_m:
            df, idx, cols, vals, agg, target = piv_m.group(1), piv_m.group(2), piv_m.group(3), piv_m.group(4), piv_m.group(5) or '"sum"', piv_m.group(6)
            return f"set {target} to data_pivot_table({df}, {idx}, {cols}, {vals}, {agg})"

        # melt table <df> with id_vars <ids>, value_vars <vals> into <target>
        melt_m = re.match(
            r"^melt\s+table\s+([A-Za-z_]\w*)\s+with\s+id_vars\s+(.+?),\s*value_vars\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if melt_m:
            df, ids, vals, target = melt_m.group(1), melt_m.group(2), melt_m.group(3), melt_m.group(4)
            return f"set {target} to data_melt_table({df}, {ids}, {vals})"

        # fill missing values in <df> for column <col> with <fill> into <target>
        fill_m = re.match(
            r"^fill\s+missing\s+values\s+in\s+([A-Za-z_]\w*)\s+for\s+column\s+(.+?)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if fill_m:
            df, col, fill, target = fill_m.group(1), fill_m.group(2), fill_m.group(3), fill_m.group(4)
            return f"set {target} to data_fill_missing({df}, {col}, {fill})"

        # drop duplicate rows in <df> [by subset <cols>] into <target>
        drop_m = re.match(
            r"^drop\s+duplicate\s+rows\s+in\s+([A-Za-z_]\w*)(?:\s+by\s+subset\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if drop_m:
            df, cols, target = drop_m.group(1), drop_m.group(2) or "None", drop_m.group(3)
            return f"set {target} to data_drop_duplicates({df}, {cols})"

        # sample <n> rows from <df> stratified by <col> into <target>
        sample_m = re.match(
            r"^sample\s+(.+?)\s+rows\s+from\s+([A-Za-z_]\w*)\s+stratified\s+by\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if sample_m:
            n, df, col, target = sample_m.group(1), sample_m.group(2), sample_m.group(3), sample_m.group(4)
            return f"set {target} to data_stratified_sample({df}, {col}, {n})"

        # rolling mean in <df> for <col> with window <w> into <target>
        roll_m = re.match(
            r"^rolling\s+mean\s+in\s+([A-Za-z_]\w*)\s+for\s+(.+?)\s+with\s+window\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if roll_m:
            df, col, w, target = roll_m.group(1), roll_m.group(2), roll_m.group(3), roll_m.group(4)
            return f"set {target} to data_rolling_mean({df}, {col}, {w})"

        # explode column <col> in <df> into <target>
        exp_m = re.match(
            r"^explode\s+column\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if exp_m:
            col, df, target = exp_m.group(1), exp_m.group(2), exp_m.group(3)
            return f"set {target} to data_explode_column({df}, {col})"

        # merge tables <a> and <b> on <key> with kind <kind> into <target>
        merge_m = re.match(
            r"^merge\s+tables\s+([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)\s+on\s+(.+?)\s+with\s+kind\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if merge_m:
            a, b, key, kind, target = merge_m.group(1), merge_m.group(2), merge_m.group(3), merge_m.group(4), merge_m.group(5)
            return f"set {target} to data_merge_tables({a}, {b}, {key}, {kind})"

        # 350-Expansion Data Operations
        rank_m = re.match(
            r"^rank\s+column\s+(.+?)\s+in\s+([A-Za-z_]\w*)(?:\s+using\s+([A-Za-z_]\w*))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if rank_m:
            col, data_var = rank_m.group(1).strip(), rank_m.group(2).strip()
            method = f'"{rank_m.group(3).strip()}"' if rank_m.group(3) else '"average"'
            target = rank_m.group(4).strip()
            return f"set {target} to data_rank_column({data_var}, {col}, method={method})"

        lag_m = re.match(
            r"^lag\s+column\s+(.+?)\s+in\s+([A-Za-z_]\w*)(?:\s+by\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if lag_m:
            col, data_var = lag_m.group(1).strip(), lag_m.group(2).strip()
            n_shift = lag_m.group(3).strip() if lag_m.group(3) else "1"
            target = lag_m.group(4).strip()
            return f"set {target} to data_lag_column({data_var}, {col}, n={n_shift})"

        lead_m = re.match(
            r"^lead\s+column\s+(.+?)\s+in\s+([A-Za-z_]\w*)(?:\s+by\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if lead_m:
            col, data_var = lead_m.group(1).strip(), lead_m.group(2).strip()
            n_shift = lead_m.group(3).strip() if lead_m.group(3) else "1"
            target = lead_m.group(4).strip()
            return f"set {target} to data_lead_column({data_var}, {col}, n={n_shift})"

        cumsum_m = re.match(
            r"^cumulative\s+sum\s+of\s+column\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if cumsum_m:
            col, data_var, target = cumsum_m.group(1).strip(), cumsum_m.group(2).strip(), cumsum_m.group(3).strip()
            return f"set {target} to data_cumulative_sum({data_var}, {col})"

        cummax_m = re.match(
            r"^cumulative\s+max(?:imum)?\s+of\s+column\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if cummax_m:
            col, data_var, target = cummax_m.group(1).strip(), cummax_m.group(2).strip(), cummax_m.group(3).strip()
            return f"set {target} to data_cumulative_max({data_var}, {col})"

        cummin_m = re.match(
            r"^cumulative\s+min(?:imum)?\s+of\s+column\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if cummin_m:
            col, data_var, target = cummin_m.group(1).strip(), cummin_m.group(2).strip(), cummin_m.group(3).strip()
            return f"set {target} to data_cumulative_min({data_var}, {col})"

        coal_m = re.match(
            r"^coalesce\s+columns\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+into\s+column\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if coal_m:
            cols, data_var = coal_m.group(1).strip(), coal_m.group(2).strip()
            tgt_col = coal_m.group(3).strip()
            target = coal_m.group(4).strip() if coal_m.group(4) else data_var
            return f"set {target} to data_coalesce_columns({data_var}, {cols}, {tgt_col})"

        msort_m = re.match(
            r"^sort\s+table\s+([A-Za-z_]\w*)\s+by\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if msort_m:
            data_var, keys, target = msort_m.group(1).strip(), msort_m.group(2).strip(), msort_m.group(3).strip()
            return f"set {target} to data_multi_sort({data_var}, {keys})"

        cjoin_m = re.match(
            r"^cross\s+join\s+([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if cjoin_m:
            d1, d2, target = cjoin_m.group(1).strip(), cjoin_m.group(2).strip(), cjoin_m.group(3).strip()
            return f"set {target} to data_cross_join({d1}, {d2})"

        vsch_m = re.match(
            r"^validate\s+schema\s+of\s+([A-Za-z_]\w*)\s+against\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if vsch_m:
            data_var, sch, target = vsch_m.group(1).strip(), vsch_m.group(2).strip(), vsch_m.group(3).strip()
            return f"set {target} to data_validate_schema({data_var}, {sch})"

        ren_m = re.match(
            r"^rename\s+columns\s+in\s+([A-Za-z_]\w*)\s+using\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if ren_m:
            data_var, mp, target = ren_m.group(1).strip(), ren_m.group(2).strip(), ren_m.group(3).strip()
            return f"set {target} to data_rename_columns({data_var}, {mp})"

        clip_m = re.match(
            r"^clip\s+column\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if clip_m:
            col, data_var = clip_m.group(1).strip(), clip_m.group(2).strip()
            low, high, target = clip_m.group(3).strip(), clip_m.group(4).strip(), clip_m.group(5).strip()
            return f"set {target} to data_clip_column({data_var}, {col}, {low}, {high})"

        fdate_m = re.match(
            r"^format\s+date\s+column\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+as\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if fdate_m:
            col, data_var = fdate_m.group(1).strip(), fdate_m.group(2).strip()
            fmt, target = fdate_m.group(3).strip(), fdate_m.group(4).strip()
            return f"set {target} to data_format_date_column({data_var}, {col}, {fmt})"

        trim_m = re.match(
            r"^trim\s+whitespace\s+in\s+column\s+(.+?)\s+of\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if trim_m:
            col, data_var, target = trim_m.group(1).strip(), trim_m.group(2).strip(), trim_m.group(3).strip()
            return f"set {target} to data_string_trim({data_var}, {col})"

        upper_m = re.match(
            r"^uppercase\s+text\s+in\s+column\s+(.+?)\s+of\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if upper_m:
            col, data_var, target = upper_m.group(1).strip(), upper_m.group(2).strip(), upper_m.group(3).strip()
            return f"set {target} to data_string_upper({data_var}, {col})"

        lower_m = re.match(
            r"^lowercase\s+text\s+in\s+column\s+(.+?)\s+of\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if lower_m:
            col, data_var, target = lower_m.group(1).strip(), lower_m.group(2).strip(), lower_m.group(3).strip()
            return f"set {target} to data_string_lower({data_var}, {col})"

        ffill_m = re.match(
            r"^forward\s+fill\s+nulls\s+in\s+column\s+(.+?)\s+of\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if ffill_m:
            col, data_var, target = ffill_m.group(1).strip(), ffill_m.group(2).strip(), ffill_m.group(3).strip()
            return f"set {target} to data_fill_null_forward({data_var}, {col})"

        bfill_m = re.match(
            r"^backward\s+fill\s+nulls\s+in\s+column\s+(.+?)\s+of\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if bfill_m:
            col, data_var, target = bfill_m.group(1).strip(), bfill_m.group(2).strip(), bfill_m.group(3).strip()
            return f"set {target} to data_fill_null_backward({data_var}, {col})"

        year_m = re.match(
            r"^extract\s+year\s+from\s+column\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if year_m:
            col, data_var, target = year_m.group(1).strip(), year_m.group(2).strip(), year_m.group(3).strip()
            return f"set {target} to data_extract_year({data_var}, {col})"

        frac_m = re.match(
            r"^sample\s+(.+?)\s+fraction\s+from\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if frac_m:
            frac, data_var, target = frac_m.group(1).strip(), frac_m.group(2).strip(), frac_m.group(3).strip()
            return f"set {target} to data_sample_fraction({data_var}, {frac})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[PipelineSpec, str]:
        # pipeline "<name>" [from <source>] into <target>:
        m = re.match(
            r"^pipeline\s+[\"']?([A-Za-z_]\w*)[\"']?(?:\s+from\s+([^\s:]+))?(?:\s+into\s+([A-Za-z_]\w*))?:?$",
            header.strip(),
            re.IGNORECASE,
        )
        if not m:
            raise SyntaxError(f"Invalid pipeline header: {header}")

        pipe_name = m.group(1)
        source = m.group(2) or "data"
        target = m.group(3) or pipe_name

        spec = PipelineSpec(name=pipe_name, source=source, target=target)

        # Parse body lines
        i = 0
        n = len(body_lines)
        in_validate = False
        in_groupby = False
        cur_groupby: Optional[GroupByStep] = None

        while i < n:
            l_no, raw_line = body_lines[i]
            line = raw_line.strip()
            if not line or line.startswith("#"):
                i += 1
                continue

            # Check read step inside block: read <source> [into <target>]
            read_m = re.match(r"^read\s+[\"']?([^\"'\s]+)[\"']?(?:\s+into\s+([A-Za-z_]\w*))?$", line, re.IGNORECASE)
            if read_m:
                spec.source = read_m.group(1)
                i += 1
                continue

            # Check sub-block switches
            if re.match(r"^validate(?:\s+[A-Za-z_]\w*)?\s*:?$", line, re.IGNORECASE):
                in_validate = True
                in_groupby = False
                i += 1
                continue

            grp_m = re.match(r"^group\s+(?:[A-Za-z_]\w*\s+)?by\s+(.+?):?$", line, re.IGNORECASE)
            if grp_m:
                in_groupby = True
                in_validate = False
                keys = [k.strip().strip("\"'") for k in grp_m.group(1).split(",")]
                cur_groupby = GroupByStep(keys=keys, aggregations={})
                spec.steps.append(cur_groupby)
                i += 1
                continue

            if in_validate:
                # require "<col>" is (text|number|positive number)
                req_m = re.match(r"^require\s+[\"']([^\"']+)[\"']\s+is\s+(text|number|positive\s+number)", line, re.IGNORECASE)
                if req_m:
                    col = req_m.group(1)
                    t_spec = req_m.group(2).lower()
                    rule_type = "positive" if "positive" in t_spec else "type"
                    expected = "number" if "number" in t_spec else "text"
                    spec.validations.append(ValidationRule(rule_type=rule_type, column=col, expected=expected))
                    i += 1
                    continue

                # forbid nulls in "<col>"
                forbid_m = re.match(r"^forbid\s+nulls\s+in\s+[\"']([^\"']+)[\"']", line, re.IGNORECASE)
                if forbid_m:
                    col = forbid_m.group(1)
                    spec.validations.append(ValidationRule(rule_type="forbid_nulls", column=col))
                    i += 1
                    continue

                # If line is not a validation rule, end validation sub-block
                in_validate = False

            if in_groupby and cur_groupby:
                calc_m = re.match(
                    r"^calculate\s+([A-Za-z_]\w*)\s+as\s+(sum|mean|avg|min|max|first|last|count)(?:\s+of\s+([A-Za-z_]\w*))?",
                    line,
                    re.IGNORECASE,
                )
                if calc_m:
                    out_col = calc_m.group(1)
                    agg_fn = calc_m.group(2).lower()
                    src_col = calc_m.group(3) or ""
                    cur_groupby.aggregations[out_col] = (agg_fn, src_col)
                    i += 1
                    continue
                else:
                    in_groupby = False

            # Normal steps:
            # remove duplicate rows [by "<col>"]
            dedupe_m = re.match(r"^remove\s+duplicate\s+rows(?:\s+by\s+[\"']([^\"']+)[\"'])?", line, re.IGNORECASE)
            if dedupe_m:
                by_col = [dedupe_m.group(1)] if dedupe_m.group(1) else []
                spec.steps.append(DedupeStep(by_columns=by_col))
                i += 1
                continue

            # fill missing "<col>" with <val>
            fillna_m = re.match(r"^fill\s+missing\s+[\"']([^\"']+)[\"']\s+with\s+(.+)$", line, re.IGNORECASE)
            if fillna_m:
                col = fillna_m.group(1)
                val_str = fillna_m.group(2).strip()
                try:
                    val = eval(val_str, {}, {})
                except Exception:
                    val = val_str
                spec.steps.append(FillNaStep(column=col, value=val))
                i += 1
                continue

            # validate schema: col as type, ...
            schema_m = re.match(r"^validate\s+schema\s*:\s*(.+)$", line, re.IGNORECASE)
            if schema_m:
                rules_str = schema_m.group(1).strip()
                schema_dict = {}
                for part in rules_str.split(","):
                    if " as " in part:
                        c_name, c_type = part.split(" as ", 1)
                        schema_dict[c_name.strip()] = c_type.strip().lower()
                spec.steps.append(SchemaContractStep(schema=schema_dict))
                i += 1
                continue

            # join / left join with <dataset> on <key>
            join_m = re.match(
                r"^(left|right|outer|cross|inner)?\s*join\s+(?:with\s+)?([A-Za-z_]\w*)\s+on\s+([A-Za-z_]\w*)$",
                line,
                re.IGNORECASE,
            )
            if join_m:
                how = (join_m.group(1) or "inner").lower()
                other_table = join_m.group(2)
                on_key = join_m.group(3)
                spec.steps.append(JoinStep(other_dataset=other_table, on_key=on_key, how=how))
                i += 1
                continue

            # calculate (running_sum|running_avg|row_number|rank) [of <col>] over <col> [partitioned by <col>] into <target>
            win_m = re.match(
                r"^calculate\s+(running_sum|running_avg|row_number|rank|rolling_mean)\s+(?:of\s+([A-Za-z_]\w*)\s+)?over\s+([A-Za-z_]\w*)(?:\s+partitioned\s+by\s+([A-Za-z_]\w*))?(?:\s+into\s+([A-Za-z_]\w*))?$",
                line,
                re.IGNORECASE,
            )
            if win_m:
                func = win_m.group(1).lower()
                src_col = win_m.group(2)
                over_col = win_m.group(3)
                part_by = win_m.group(4)
                target_col = win_m.group(5) or f"{func}_val"
                spec.steps.append(
                    WindowStep(
                        func=func,
                        source_col=src_col,
                        over_col=over_col,
                        partition_by=part_by,
                        target_col=target_col,
                    )
                )
                i += 1
                continue

            # derive "<col>" as <expr>
            derive_m = re.match(r"^derive\s+[\"']([^\"']+)[\"']\s+as\s+(.+)$", line, re.IGNORECASE)
            if derive_m:
                target_col = derive_m.group(1)
                expr = derive_m.group(2).strip()
                spec.steps.append(DeriveStep(target_col=target_col, expression=expr))
                i += 1
                continue

            # filter [rows] where <cond>
            filter_m = re.match(r"^filter\s+(?:rows\s+)?where\s+(.+)$", line, re.IGNORECASE)
            if filter_m:
                cond = filter_m.group(1).strip()
                spec.steps.append(FilterStep(condition=cond))
                i += 1
                continue

            # sort by <col> [descending]
            sort_m = re.match(r"^sort\s+by\s+([A-Za-z_]\w*)(?:\s+(descending|ascending))?", line, re.IGNORECASE)
            if sort_m:
                col = sort_m.group(1)
                desc = (sort_m.group(2) or "").lower() == "descending"
                spec.steps.append(SortStep(column=col, descending=desc))
                i += 1
                continue

            # write to "<path>"
            write_m = re.match(r"^write\s+(?:results\s+)?to\s+[\"']([^\"']+)[\"']", line, re.IGNORECASE)
            if write_m:
                path = write_m.group(1)
                spec.sink = SinkStep(path=path)
                spec.steps.append(spec.sink)
                i += 1
                continue

            i += 1

        return spec, target
