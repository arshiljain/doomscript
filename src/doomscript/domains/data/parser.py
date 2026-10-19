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

        # join <left> and <right> on "<key>" as (inner|left|right|outer) into <target>
        join_m = re.match(
            r"^join\s+([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)\s+on\s+[\"']([^\"']+)[\"'](?:\s+as\s+(inner|left|right|outer))?(?:\s+into\s+([A-Za-z_]\w*))?$",
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
