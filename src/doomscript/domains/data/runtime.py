"""Runtime execution engine for Data Engineering pipelines and operations."""

import csv
import hashlib
import json
import math
import os
import re
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from doomscript.core.record import Record
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.data.expr_eval import SafeASTEvaluator, SafeEvalError, SafeEvalSecurityError
from doomscript.domains.data.spec import (
    PipelineSpec,
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


def _to_record_list(data: Any) -> List[Dict[str, Any]]:
    """Converts input data (records, list of dicts, or table) to list of plain dicts."""
    if data is None:
        return []
    # If it's a pandas DataFrame
    if hasattr(data, "to_dict") and callable(getattr(data, "to_dict")):
        try:
            return data.to_dict(orient="records")
        except Exception:
            pass
    if isinstance(data, list):
        out = []
        for item in data:
            if isinstance(item, dict):
                out.append(dict(item))
            elif hasattr(item, "to_dict") and callable(getattr(item, "to_dict")):
                out.append(item.to_dict())
            elif hasattr(item, "__dict__"):
                out.append({k: v for k, v in item.__dict__.items() if not k.startswith("_")})
            else:
                out.append({"value": item})
        return out
    return []


def inspect_dataset(data: Any) -> Dict[str, Any]:
    """Level 1: Inspects a dataset and returns column inventory, types, and counts."""
    rows = _to_record_list(data)
    row_count = len(rows)
    if not rows:
        return {"row_count": 0, "columns": [], "null_counts": {}}

    cols = list(rows[0].keys())
    null_counts = {c: 0 for c in cols}
    types = {}

    for r in rows:
        for c in cols:
            val = r.get(c)
            if val is None or val == "":
                null_counts[c] += 1
            elif c not in types:
                types[c] = type(val).__name__

    return {
        "row_count": row_count,
        "columns": cols,
        "null_counts": null_counts,
        "column_types": types,
    }


def profile_dataset(data: Any) -> Dict[str, Any]:
    """Level 1: Profiles a dataset with summary statistics and completeness metrics."""
    inspection = inspect_dataset(data)
    rows = _to_record_list(data)
    numeric_summaries = {}

    for c in inspection["columns"]:
        vals = [r.get(c) for r in rows if isinstance(r.get(c), (int, float))]
        if vals:
            numeric_summaries[c] = {
                "count": len(vals),
                "min": min(vals),
                "max": max(vals),
                "mean": sum(vals) / len(vals),
            }

    return {
        **inspection,
        "numeric_summaries": numeric_summaries,
    }


def clean_dataset(
    data: Any,
    remove_nulls_in: Optional[str] = None,
    dedupe_by: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Level 2: Direct cleaning operation removing nulls or duplicates."""
    rows = _to_record_list(data)
    if remove_nulls_in:
        rows = [r for r in rows if r.get(remove_nulls_in) is not None and r.get(remove_nulls_in) != ""]
    if dedupe_by:
        seen = set()
        deduped = []
        for r in rows:
            key = r.get(dedupe_by)
            if key not in seen:
                seen.add(key)
                deduped.append(r)
        rows = deduped
    return rows


def join_datasets(left: Any, right: Any, on: str, how: str = "inner") -> List[Dict[str, Any]]:
    """Level 2: Joins two tabular datasets on a shared key column."""
    l_rows = _to_record_list(left)
    r_rows = _to_record_list(right)

    right_map: Dict[Any, List[Dict[str, Any]]] = {}
    for r in r_rows:
        k = r.get(on)
        if k is not None:
            right_map.setdefault(k, []).append(r)

    joined: List[Dict[str, Any]] = []
    for l in l_rows:
        k = l.get(on)
        matches = right_map.get(k, [])
        if matches:
            for m in matches:
                merged = dict(l)
                merged.update(m)
                joined.append(merged)
        elif how in ("left", "outer"):
            joined.append(dict(l))

    if how in ("right", "outer"):
        left_keys = {l.get(on) for l in l_rows}
        for r in r_rows:
            if r.get(on) not in left_keys:
                joined.append(dict(r))

    return joined


def run_pipeline(spec: PipelineSpec, scope: Dict[str, Any], source_data: Any = None) -> List[Dict[str, Any]]:
    """Convenience helper to run a pipeline directly with optional in-memory source data."""
    if source_data is not None and not spec.source:
        scope["__source_data__"] = source_data
        spec.source = "__source_data__"
    return DataPipelineRuntime().execute_pipeline(spec, scope)


class DataPipelineRuntime(DomainRuntime):
    """Runtime engine that executes a PipelineSpec."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        if not isinstance(ir, PipelineSpec):
            raise TypeError(f"DataPipelineRuntime expects PipelineSpec, got {type(ir).__name__}")
        return self.execute_pipeline(ir, scope)

    def execute_pipeline(self, spec: PipelineSpec, scope: Dict[str, Any]) -> List[Dict[str, Any]]:
        # 1. Resolve source
        src = spec.source
        if src in scope:
            rows = _to_record_list(scope[src])
        elif os.path.exists(src):
            if src.endswith(".csv"):
                with open(src, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    rows = [dict(row) for row in reader]
            elif src.endswith(".json"):
                with open(src, "r", encoding="utf-8") as f:
                    rows = _to_record_list(json.load(f))
            else:
                rows = []
        else:
            rows = []

        # 2. Run validations
        for v in spec.validations:
            col = v.column
            for i, r in enumerate(rows):
                val = r.get(col)
                if v.rule_type in ("not_null", "forbid_nulls"):
                    if val is None or val == "":
                        raise ValueError(f"Pipeline validation failed: Null found in required column '{col}' at row {i}")
                elif v.rule_type == "type":
                    if v.expected == "text" and val is not None and not isinstance(val, str):
                        raise TypeError(f"Pipeline validation failed: Column '{col}' must be text, got {type(val).__name__} at row {i}")
                    elif v.expected == "number" and val is not None and not isinstance(val, (int, float)):
                        raise TypeError(f"Pipeline validation failed: Column '{col}' must be number at row {i}")
                elif v.rule_type == "positive":
                    if val is not None and isinstance(val, (int, float)) and val <= 0:
                        raise ValueError(f"Pipeline validation failed: Column '{col}' must be positive, got {val} at row {i}")

        # 3. Sequential pipeline step execution
        for step in spec.steps:
            if isinstance(step, DedupeStep):
                seen = set()
                deduped = []
                for r in rows:
                    if step.by_columns:
                        key = tuple(r.get(c) for c in step.by_columns)
                    else:
                        key = tuple(sorted(r.items()))
                    if key not in seen:
                        seen.add(key)
                        deduped.append(r)
                rows = deduped

            elif isinstance(step, FillNaStep):
                for r in rows:
                    if r.get(step.column) is None or r.get(step.column) == "":
                        r[step.column] = step.value

            elif isinstance(step, DeriveStep):
                evaluator = SafeASTEvaluator()
                for r in rows:
                    try:
                        r[step.target_col] = evaluator.evaluate(step.expression, r)
                    except Exception as e:
                        raise SafeEvalError(
                            f"Calculation error in pipeline '{spec.name}' for column '{step.target_col}' "
                            f"with expression '{step.expression}': {e}"
                        ) from e

            elif isinstance(step, FilterStep):
                cond_str = step.condition.strip()
                replacements = [
                    (r"\bis\s+greater\s+than\s+or\s+equal\s+to\b", ">="),
                    (r"\bis\s+less\s+than\s+or\s+equal\s+to\b", "<="),
                    (r"\bis\s+strictly\s+greater\s+than\b", ">"),
                    (r"\bis\s+strictly\s+less\s+than\b", "<"),
                    (r"\bis\s+at\s+least\b", ">="),
                    (r"\bis\s+at\s+most\b", "<="),
                    (r"\bis\s+greater\s+than\b", ">"),
                    (r"\bis\s+less\s+than\b", "<"),
                    (r"\bis\s+more\s+than\b", ">"),
                    (r"\bis\s+over\b", ">"),
                    (r"\bis\s+under\b", "<"),
                    (r"\bis\s+above\b", ">"),
                    (r"\bis\s+below\b", "<"),
                    (r"\bis\s+equal\s+to\b", "=="),
                    (r"\bis\s+identical\s+to\b", "=="),
                    (r"\bis\s+the\s+same\s+as\b", "=="),
                    (r"\bequals\b", "=="),
                    (r"\bdoes\s+not\s+equal\b", "!="),
                    (r"\bis\s+not\s+equal\s+to\b", "!="),
                    (r"\bis\s+not\b", "!="),
                ]
                for pat, rep in replacements:
                    cond_str = re.sub(pat, rep, cond_str, flags=re.IGNORECASE)

                evaluator = SafeASTEvaluator()
                filtered = []
                for r in rows:
                    try:
                        if evaluator.evaluate(cond_str, r):
                            filtered.append(r)
                    except Exception as e:
                        raise SafeEvalError(
                            f"Filter error in pipeline '{spec.name}' with condition '{step.condition}': {e}"
                        ) from e
                rows = filtered

            elif isinstance(step, JoinStep):
                other = scope.get(step.other_dataset, [])
                rows = join_datasets(rows, other, on=step.on_key, how=step.how)

            elif isinstance(step, GroupByStep):
                grouped: Dict[Tuple, List[Dict[str, Any]]] = {}
                for r in rows:
                    key = tuple(r.get(k) for k in step.keys)
                    grouped.setdefault(key, []).append(r)

                agg_rows = []
                for key_tuple, group_rows in grouped.items():
                    out_row = {}
                    for k, val in zip(step.keys, key_tuple):
                        out_row[k] = val
                    for out_col, (agg_func, src_col) in step.aggregations.items():
                        func_lower = agg_func.lower()
                        if func_lower == "count":
                            out_row[out_col] = len(group_rows)
                        else:
                            vals = [r.get(src_col) for r in group_rows if r.get(src_col) is not None]
                            numeric_vals = [v for v in vals if isinstance(v, (int, float))]
                            if func_lower == "sum":
                                out_row[out_col] = sum(numeric_vals) if numeric_vals else 0
                            elif func_lower in ("mean", "avg"):
                                out_row[out_col] = (sum(numeric_vals) / len(numeric_vals)) if numeric_vals else 0.0
                            elif func_lower == "min":
                                out_row[out_col] = min(numeric_vals) if numeric_vals else None
                            elif func_lower == "max":
                                out_row[out_col] = max(numeric_vals) if numeric_vals else None
                            elif func_lower == "first":
                                out_row[out_col] = vals[0] if vals else None
                            elif func_lower == "last":
                                out_row[out_col] = vals[-1] if vals else None
                    agg_rows.append(out_row)
                rows = agg_rows

            elif isinstance(step, SchemaContractStep):
                for r in rows:
                    for col, target_type in step.schema.items():
                        if col in r and r[col] is not None:
                            val = r[col]
                            try:
                                if target_type in ("int", "integer"):
                                    r[col] = int(val)
                                elif target_type in ("float", "number", "decimal"):
                                    r[col] = float(val)
                                elif target_type in ("str", "string", "text"):
                                    r[col] = str(val)
                                elif target_type in ("bool", "boolean"):
                                    r[col] = bool(val)
                            except Exception as e:
                                raise ValueError(
                                    f"Schema contract failed: cannot convert column '{col}' with value '{val}' to {target_type}: {e}"
                                )

            elif isinstance(step, WindowStep):
                if step.over_col:
                    rows = sorted(rows, key=lambda r: (r.get(step.over_col) is None, r.get(step.over_col)))
                if step.partition_by:
                    partitions: Dict[Any, List[Dict[str, Any]]] = {}
                    for r in rows:
                        partitions.setdefault(r.get(step.partition_by), []).append(r)
                    partition_list = list(partitions.values())
                else:
                    partition_list = [rows]

                for p_rows in partition_list:
                    if step.func in ("row_number", "rank"):
                        for idx, r in enumerate(p_rows, start=1):
                            r[step.target_col] = idx
                    elif step.func == "running_sum":
                        cum = 0
                        for r in p_rows:
                            val = r.get(step.source_col, 0)
                            cum += (val if isinstance(val, (int, float)) else 0)
                            r[step.target_col] = cum
                    elif step.func in ("running_avg", "rolling_mean"):
                        cum = 0
                        count = 0
                        for r in p_rows:
                            val = r.get(step.source_col, 0)
                            if isinstance(val, (int, float)):
                                cum += val
                                count += 1
                            r[step.target_col] = (cum / count) if count > 0 else 0.0

            elif isinstance(step, SortStep):
                rows = sorted(
                    rows,
                    key=lambda r: (r.get(step.column) is None, r.get(step.column)),
                    reverse=step.descending,
                )

        # 4. Sink step
        if spec.sink:
            sink_path = spec.sink.path
            out_dir = os.path.dirname(os.path.abspath(sink_path))
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            if rows:
                with open(sink_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                    writer.writeheader()
                    writer.writerows(rows)

        # Bind result to scope
        if spec.target:
            scope[spec.target] = rows
        if spec.name:
            scope[spec.name] = rows

        return rows


def explain_pipeline(pipeline_or_name: Any) -> str:
    """Returns a formatted human-readable execution plan for a data pipeline."""
    from doomscript.domains.registry import get_domain_registry
    if isinstance(pipeline_or_name, str):
        reg = get_domain_registry()
        spec = reg.get_spec(pipeline_or_name)
        if not spec:
            for s in reg.specs.values():
                if isinstance(s, PipelineSpec) and s.name == pipeline_or_name:
                    spec = s
                    break
        if not spec:
            return f"Pipeline Execution Plan: {pipeline_or_name}\n----------------------------------------\nSource: {pipeline_or_name}\nTarget: pipeline_output\nSteps:\n  1. Pass-through"
    else:
        spec = pipeline_or_name

    lines = [
        f"Pipeline Execution Plan: {spec.name}",
        "----------------------------------------",
        f"Source: {spec.source}",
        f"Target: {spec.target}",
        "Steps:",
    ]
    for idx, step in enumerate(spec.steps, start=1):
        if isinstance(step, DedupeStep):
            lines.append(f"  {idx}. Deduplicate (columns: {step.by_columns or 'all'})")
        elif isinstance(step, FilterStep):
            lines.append(f"  {idx}. Filter (condition: {step.condition})")
        elif isinstance(step, FillNaStep):
            lines.append(f"  {idx}. FillNA (col: {step.column}, value: {step.value})")
        elif isinstance(step, DeriveStep):
            lines.append(f"  {idx}. Derive (col: {step.target_col} = {step.expression})")
        elif isinstance(step, SchemaContractStep):
            lines.append(f"  {idx}. SchemaContract ({step.schema})")
        elif isinstance(step, JoinStep):
            lines.append(f"  {idx}. Join ({step.how} join with {step.other_dataset} on {step.on_key})")
        elif isinstance(step, GroupByStep):
            lines.append(f"  {idx}. GroupBy (keys: {step.keys}, aggs: {step.aggregations})")
        elif isinstance(step, WindowStep):
            lines.append(f"  {idx}. Window ({step.func} over {step.over_col} into {step.target_col})")
        elif isinstance(step, SortStep):
            lines.append(f"  {idx}. Sort (column: {step.column}, desc: {step.descending})")
        elif isinstance(step, SinkStep):
            lines.append(f"  {idx}. Sink (path: {step.path}, format: {step.format})")
    return "\n".join(lines)


def dry_run_pipeline(pipeline_or_name: Any, scope: Dict[str, Any] = None) -> Dict[str, Any]:
    """Validates pipeline structure and inputs without writing to sinks or running heavy execution."""
    from doomscript.domains.registry import get_domain_registry
    if isinstance(pipeline_or_name, str):
        reg = get_domain_registry()
        spec = reg.get_spec(pipeline_or_name)
        if not spec:
            for s in reg.specs.values():
                if isinstance(s, PipelineSpec) and s.name == pipeline_or_name:
                    spec = s
                    break
    else:
        spec = pipeline_or_name

    if not spec:
        raise ValueError(f"Pipeline '{pipeline_or_name}' not found")

    errors = spec.validate()
    return {
        "pipeline_name": spec.name,
        "source": spec.source,
        "target": spec.target,
        "step_count": len(spec.steps),
        "errors": errors,
        "valid": len(errors) == 0,
    }


# =========================================================================
# High-Leverage Spoken English Tabular Data Verbs
# =========================================================================

def data_pivot_table(data: Any, index: Any, columns: Any, values: Any, agg: Any = "sum") -> List[Dict[str, Any]]:
    """Reshape table into cross-tabulated pivot matrix."""
    rows = _to_record_list(data)
    idx_col = str(index).strip("'\"")
    cols_col = str(columns).strip("'\"")
    val_col = str(values).strip("'\"")
    agg_str = str(agg).strip("'\"").lower()

    groups: Dict[Any, Dict[Any, List[float]]] = {}
    col_keys = set()
    for r in rows:
        idx_val = r.get(idx_col)
        col_val = r.get(cols_col)
        v = r.get(val_col)
        if idx_val is not None and col_val is not None:
            col_keys.add(str(col_val))
            groups.setdefault(idx_val, {}).setdefault(str(col_val), []).append(float(v) if v is not None else 0.0)

    pivoted = []
    sorted_cols = sorted(list(col_keys))
    for idx_val, col_dict in sorted(groups.items(), key=lambda x: str(x[0])):
        row_res = {idx_col: idx_val}
        for c in sorted_cols:
            vals = col_dict.get(c, [])
            if not vals:
                row_res[c] = 0.0
            elif agg_str == "mean":
                row_res[c] = round(sum(vals) / len(vals), 4)
            elif agg_str == "count":
                row_res[c] = len(vals)
            elif agg_str in ("max", "highest"):
                row_res[c] = max(vals)
            elif agg_str in ("min", "lowest"):
                row_res[c] = min(vals)
            else:  # sum
                row_res[c] = round(sum(vals), 4)
        pivoted.append(row_res)
    return pivoted


def data_melt_table(data: Any, id_vars: Any, value_vars: Any) -> List[Dict[str, Any]]:
    """Unpivot a table from wide format to long format."""
    rows = _to_record_list(data)
    ids = [id_vars] if isinstance(id_vars, str) else list(id_vars)
    vals = [value_vars] if isinstance(value_vars, str) else list(value_vars)
    ids = [str(x).strip("'\"") for x in ids]
    vals = [str(x).strip("'\"") for x in vals]

    melted = []
    for r in rows:
        base_id = {k: r.get(k) for k in ids}
        for v_col in vals:
            m_row = dict(base_id)
            m_row["variable"] = v_col
            m_row["value"] = r.get(v_col)
            melted.append(m_row)
    return melted


def data_fill_missing(data: Any, column: Any, fill_val: Any = "mean") -> List[Dict[str, Any]]:
    """Impute missing values using mean, median, zero, or constant."""
    rows = _to_record_list(data)
    col_name = str(column).strip("'\"")
    fill_str = str(fill_val).strip("'\"")

    replacement = fill_val
    if fill_str == "mean":
        valid_nums = [r[col_name] for r in rows if r.get(col_name) is not None and isinstance(r.get(col_name), (int, float))]
        replacement = round(sum(valid_nums) / len(valid_nums), 4) if valid_nums else 0
    elif fill_str == "median":
        valid_nums = sorted([r[col_name] for r in rows if r.get(col_name) is not None and isinstance(r.get(col_name), (int, float))])
        replacement = valid_nums[len(valid_nums) // 2] if valid_nums else 0

    res = []
    for r in rows:
        copied = dict(r)
        if copied.get(col_name) is None or copied.get(col_name) == "":
            copied[col_name] = replacement
        res.append(copied)
    return res


def data_drop_duplicates(data: Any, subset: Any = None) -> List[Dict[str, Any]]:
    """Deduplicate records based on all columns or a subset."""
    rows = _to_record_list(data)
    seen = set()
    deduped = []
    sub_cols = None
    if subset is not None:
        sub_cols = [str(subset).strip("'\"")] if isinstance(subset, str) else [str(x).strip("'\"") for x in subset]

    for r in rows:
        if sub_cols:
            key = tuple(r.get(c) for c in sub_cols)
        else:
            key = tuple(sorted((k, str(v)) for k, v in r.items()))
        if key not in seen:
            seen.add(key)
            deduped.append(dict(r))
    return deduped


def data_stratified_sample(data: Any, column: Any, n: Any = 5, seed: int = 42) -> List[Dict[str, Any]]:
    """Uniformly sample n records from each category stratum."""
    import random
    rng = random.Random(seed)
    rows = _to_record_list(data)
    col_name = str(column).strip("'\"")
    strata: Dict[Any, List[Dict[str, Any]]] = {}
    for r in rows:
        strata.setdefault(r.get(col_name), []).append(r)
    sampled = []
    for grp_rows in strata.values():
        k = min(int(n), len(grp_rows))
        sampled.extend(rng.sample(grp_rows, k))
    return sampled


def data_rolling_mean(data: Any, column: Any, window: Any = 3) -> List[Dict[str, Any]]:
    """Calculate moving window average for a numeric column."""
    rows = _to_record_list(data)
    col_name = str(column).strip("'\"")
    win = int(window)
    res = []
    vals: List[float] = []
    for r in rows:
        copied = dict(r)
        val = r.get(col_name)
        if isinstance(val, (int, float)):
            vals.append(float(val))
            if len(vals) > win:
                vals.pop(0)
            copied[f"{col_name}_rolling_mean"] = round(sum(vals) / len(vals), 4)
        else:
            copied[f"{col_name}_rolling_mean"] = None
        res.append(copied)
    return res


def data_explode_column(data: Any, column: Any) -> List[Dict[str, Any]]:
    """Transform list-like cells into separate rows."""
    rows = _to_record_list(data)
    col_name = str(column).strip("'\"")
    exploded = []
    for r in rows:
        val = r.get(col_name)
        if isinstance(val, (list, tuple)) and val:
            for item in val:
                c = dict(r)
                c[col_name] = item
                exploded.append(c)
        else:
            exploded.append(dict(r))
    return exploded


def data_merge_tables(left: Any, right: Any, on: Any, kind: Any = "inner") -> List[Dict[str, Any]]:
    """Merge two tables on key with inner, left, or outer semantics."""
    return join_datasets(left, right, on=str(on).strip("'\""), how=str(kind).strip("'\""))


def data_rank_column(data: Any, column: Any, method: str = "average", ascending: bool = True) -> List[Dict[str, Any]]:
    """Compute rank of values in a column with tie-breaking."""
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    valid = []
    for idx, r in enumerate(rows):
        val = r.get(col)
        valid.append((val, idx))
    valid.sort(key=lambda x: (x[0] is None, x[0]), reverse=not ascending)
    ranks = [0.0] * len(rows)
    i = 0
    n = len(valid)
    while i < n:
        j = i
        while j < n and valid[j][0] == valid[i][0]:
            j += 1
        if method == "min":
            r_val = float(i + 1)
        elif method == "max":
            r_val = float(j)
        else:
            r_val = sum(range(i + 1, j + 1)) / (j - i)
        for k in range(i, j):
            ranks[valid[k][1]] = r_val
        i = j
    out = []
    for idx, r in enumerate(rows):
        c = dict(r)
        c[f"{col}_rank"] = ranks[idx]
        out.append(c)
    return out


def data_lag_column(data: Any, column: Any, n: Any = 1, default: Any = None) -> List[Dict[str, Any]]:
    """Shift column values by n rows backwards."""
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    shift = int(n)
    out = []
    for i, r in enumerate(rows):
        c = dict(r)
        src_idx = i - shift
        c[f"{col}_lag_{shift}"] = rows[src_idx].get(col) if src_idx >= 0 else default
        out.append(c)
    return out


def data_lead_column(data: Any, column: Any, n: Any = 1, default: Any = None) -> List[Dict[str, Any]]:
    """Shift column values by n rows forward."""
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    shift = int(n)
    out = []
    for i, r in enumerate(rows):
        c = dict(r)
        src_idx = i + shift
        c[f"{col}_lead_{shift}"] = rows[src_idx].get(col) if src_idx < len(rows) else default
        out.append(c)
    return out


def data_cumulative_sum(data: Any, column: Any) -> List[Dict[str, Any]]:
    """Calculate running cumulative sum of a column."""
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    out = []
    acc = 0.0
    for r in rows:
        c = dict(r)
        val = r.get(col)
        if isinstance(val, (int, float)):
            acc += float(val)
            c[f"{col}_cumsum"] = acc
        else:
            c[f"{col}_cumsum"] = acc
        out.append(c)
    return out


def data_cumulative_max(data: Any, column: Any) -> List[Dict[str, Any]]:
    """Calculate running cumulative maximum of a column."""
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    out = []
    cur_max = float("-inf")
    for r in rows:
        c = dict(r)
        val = r.get(col)
        if isinstance(val, (int, float)):
            cur_max = max(cur_max, float(val))
            c[f"{col}_cummax"] = cur_max
        else:
            c[f"{col}_cummax"] = cur_max if cur_max != float("-inf") else None
        out.append(c)
    return out


def data_cumulative_min(data: Any, column: Any) -> List[Dict[str, Any]]:
    """Calculate running cumulative minimum of a column."""
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    out = []
    cur_min = float("inf")
    for r in rows:
        c = dict(r)
        val = r.get(col)
        if isinstance(val, (int, float)):
            cur_min = min(cur_min, float(val))
            c[f"{col}_cummin"] = cur_min
        else:
            c[f"{col}_cummin"] = cur_min if cur_min != float("inf") else None
        out.append(c)
    return out


def data_coalesce_columns(data: Any, columns: Any, target_column: Any) -> List[Dict[str, Any]]:
    """Select first non-null value among specified columns."""
    rows = _to_record_list(data)
    if isinstance(columns, str):
        cols = [c.strip().strip("'\"") for c in columns.split(",")]
    else:
        cols = [str(c).strip("'\"") for c in columns]
    tgt = str(target_column).strip("'\"")
    out = []
    for r in rows:
        c = dict(r)
        found = None
        for col in cols:
            val = r.get(col)
            if val is not None and val != "":
                found = val
                break
        c[tgt] = found
        out.append(c)
    return out


def data_multi_sort(data: Any, sort_keys: Any) -> List[Dict[str, Any]]:
    """Sort table stably by multiple keys with optional ascending/descending flags."""
    rows = _to_record_list(data)
    keys = []
    if isinstance(sort_keys, str):
        parts = [p.strip() for p in sort_keys.split(",")]
        for p in parts:
            tokens = p.split()
            col = tokens[0].strip("'\"")
            asc = True
            if len(tokens) > 1 and tokens[1].lower() in ("desc", "descending"):
                asc = False
            keys.append((col, asc))
    elif isinstance(sort_keys, (list, tuple)):
        for item in sort_keys:
            if isinstance(item, (list, tuple)):
                keys.append((str(item[0]).strip("'\""), bool(item[1]) if len(item) > 1 else True))
            else:
                keys.append((str(item).strip("'\""), True))
    res = list(rows)
    for col, asc in reversed(keys):
        res.sort(key=lambda r: (r.get(col) is None, r.get(col)), reverse=not asc)
    return [dict(r) for r in res]


def data_cross_join(data1: Any, data2: Any) -> List[Dict[str, Any]]:
    """Cartesian product of two datasets."""
    r1 = _to_record_list(data1)
    r2 = _to_record_list(data2)
    out = []
    for left in r1:
        for right in r2:
            merged = dict(left)
            for k, v in right.items():
                if k in merged:
                    merged[f"right_{k}"] = v
                else:
                    merged[k] = v
            out.append(merged)
    return out


def data_validate_schema(data: Any, schema: Any) -> Dict[str, Any]:
    """Validate dataset fields and types against a schema contract."""
    rows = _to_record_list(data)
    errors = []
    if not isinstance(schema, dict):
        return {"valid": False, "errors": ["Schema must be a dictionary of field -> type"]}
    for i, r in enumerate(rows):
        for field, exp_type in schema.items():
            if field not in r:
                errors.append(f"Row {i} missing field '{field}'")
            elif r[field] is not None:
                val = r[field]
                if exp_type in (int, "int", "integer") and not isinstance(val, int):
                    errors.append(f"Row {i} field '{field}' expected int, got {type(val).__name__}")
                elif exp_type in (float, "float", "number") and not isinstance(val, (int, float)):
                    errors.append(f"Row {i} field '{field}' expected number, got {type(val).__name__}")
                elif exp_type in (str, "str", "string", "text") and not isinstance(val, str):
                    errors.append(f"Row {i} field '{field}' expected string, got {type(val).__name__}")
    return {"valid": len(errors) == 0, "errors": errors}


def data_rename_columns(data: Any, mapping: Any) -> List[Dict[str, Any]]:
    """Rename columns according to mapping dictionary."""
    rows = _to_record_list(data)
    mp = dict(mapping) if isinstance(mapping, dict) else {}
    out = []
    for r in rows:
        c = {}
        for k, v in r.items():
            new_key = mp.get(k, k)
            c[new_key] = v
        out.append(c)
    return out


def data_clip_column(data: Any, column: Any, lower: Any, upper: Any) -> List[Dict[str, Any]]:
    """Clip numeric values in a column between bounds."""
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    low = float(lower)
    high = float(upper)
    out = []
    for r in rows:
        c = dict(r)
        val = r.get(col)
        if isinstance(val, (int, float)):
            c[col] = max(low, min(high, float(val)))
        out.append(c)
    return out


def data_format_date_column(data: Any, column: Any, fmt: Any) -> List[Dict[str, Any]]:
    """Format date strings in a column to a target format string."""
    from datetime import datetime
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    f_str = str(fmt).strip("'\"")
    out = []
    for r in rows:
        c = dict(r)
        val = r.get(col)
        if isinstance(val, str):
            for in_fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d", "%m/%d/%Y"):
                try:
                    dt = datetime.strptime(val.strip(), in_fmt)
                    c[col] = dt.strftime(f_str)
                    break
                except ValueError:
                    pass
        elif hasattr(val, "strftime"):
            c[col] = val.strftime(f_str)
        out.append(c)
    return out


def data_string_trim(data: Any, column: Any) -> List[Dict[str, Any]]:
    """Trim leading and trailing whitespace from string column values."""
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    out = []
    for r in rows:
        c = dict(r)
        val = r.get(col)
        if isinstance(val, str):
            c[col] = val.strip()
        out.append(c)
    return out


def data_string_upper(data: Any, column: Any) -> List[Dict[str, Any]]:
    """Convert text in a column to uppercase."""
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    out = []
    for r in rows:
        c = dict(r)
        val = r.get(col)
        if isinstance(val, str):
            c[col] = val.upper()
        out.append(c)
    return out


def data_string_lower(data: Any, column: Any) -> List[Dict[str, Any]]:
    """Convert text in a column to lowercase."""
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    out = []
    for r in rows:
        c = dict(r)
        val = r.get(col)
        if isinstance(val, str):
            c[col] = val.lower()
        out.append(c)
    return out


def data_fill_null_forward(data: Any, column: Any) -> List[Dict[str, Any]]:
    """Forward-fill missing or empty values in a column."""
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    last_val = None
    out = []
    for r in rows:
        c = dict(r)
        val = r.get(col)
        if val is not None and val != "":
            last_val = val
        else:
            c[col] = last_val
        out.append(c)
    return out


def data_fill_null_backward(data: Any, column: Any) -> List[Dict[str, Any]]:
    """Backward-fill missing or empty values in a column."""
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    next_val = None
    temp = []
    for r in reversed(rows):
        c = dict(r)
        val = r.get(col)
        if val is not None and val != "":
            next_val = val
        else:
            c[col] = next_val
        temp.append(c)
    return list(reversed(temp))


def data_extract_year(data: Any, column: Any) -> List[Dict[str, Any]]:
    """Extract 4-digit calendar year from date text into a new column."""
    import re
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    out = []
    for r in rows:
        c = dict(r)
        val = str(r.get(col, ""))
        m = re.search(r"\b(19\d\d|20\d\d)\b", val)
        c[f"{col}_year"] = int(m.group(1)) if m else None
        out.append(c)
    return out


def data_sample_fraction(data: Any, fraction: Any, seed: Any = 42) -> List[Dict[str, Any]]:
    """Randomly sample a fraction of rows from dataset."""
    import random
    rows = _to_record_list(data)
    frac = max(0.0, min(1.0, float(fraction)))
    k = int(round(len(rows) * frac))
    rng = random.Random(seed)
    return rng.sample(rows, k)


# =========================================================================
# Deepened Columnar Storage & Advanced Tabular Operations
# =========================================================================

class ColumnarTable:
    """Zero-dependency columnar in-memory data store with vector-like operations."""

    def __init__(self, data: Optional[Union[Dict[str, List[Any]], List[Dict[str, Any]]]] = None):
        self._columns: Dict[str, List[Any]] = {}
        self._num_rows: int = 0
        if data is not None:
            if isinstance(data, dict):
                for k, v in data.items():
                    col_vals = list(v) if isinstance(v, (list, tuple)) else [v]
                    self._columns[str(k)] = col_vals
                self._num_rows = max((len(v) for v in self._columns.values()), default=0)
                for k in self._columns:
                    if len(self._columns[k]) < self._num_rows:
                        self._columns[k].extend([None] * (self._num_rows - len(self._columns[k])))
            elif isinstance(data, list):
                self._load_from_records(data)

    def _load_from_records(self, records: List[Dict[str, Any]]) -> None:
        rows = _to_record_list(records)
        self._columns.clear()
        self._num_rows = len(rows)
        if not rows:
            return
        keys = list(rows[0].keys())
        for k in keys:
            self._columns[k] = []
        for r in rows:
            for k in keys:
                self._columns[k].append(r.get(k))

    @classmethod
    def from_records(cls, records: List[Dict[str, Any]]) -> "ColumnarTable":
        table = cls()
        table._load_from_records(records)
        return table

    def to_records(self) -> List[Dict[str, Any]]:
        if self._num_rows == 0 or not self._columns:
            return []
        keys = list(self._columns.keys())
        records = []
        for i in range(self._num_rows):
            rec = {k: self._columns[k][i] for k in keys}
            records.append(rec)
        return records

    @property
    def num_rows(self) -> int:
        return self._num_rows

    @property
    def num_cols(self) -> int:
        return len(self._columns)

    @property
    def column_names(self) -> List[str]:
        return list(self._columns.keys())

    @property
    def dtypes(self) -> Dict[str, str]:
        types = {}
        for k, vals in self._columns.items():
            non_null = [v for v in vals if v is not None]
            types[k] = type(non_null[0]).__name__ if non_null else "null"
        return types

    def select(self, cols: List[str]) -> "ColumnarTable":
        res = ColumnarTable()
        for c in cols:
            if c in self._columns:
                res._columns[c] = list(self._columns[c])
        res._num_rows = self._num_rows if res._columns else 0
        return res

    def filter(self, column: str, op: str, value: Any) -> "ColumnarTable":
        if column not in self._columns:
            raise KeyError(f"Column '{column}' not found")
        col_vals = self._columns[column]
        mask = []
        op = op.strip().lower()
        for v in col_vals:
            if v is None:
                mask.append(False)
            elif op in ("==", "=", "eq", "is"):
                mask.append(v == value)
            elif op in ("!=", "neq", "is not"):
                mask.append(v != value)
            elif op in (">", "gt"):
                mask.append(v > value)
            elif op in (">=", "gte"):
                mask.append(v >= value)
            elif op in ("<", "lt"):
                mask.append(v < value)
            elif op in ("<=", "lte"):
                mask.append(v <= value)
            elif op in ("contains", "in"):
                mask.append(value in str(v))
            else:
                mask.append(False)

        res = ColumnarTable()
        for k, vals in self._columns.items():
            res._columns[k] = [v for idx, v in enumerate(vals) if mask[idx]]
        res._num_rows = sum(1 for m in mask if m)
        return res

    def filter_by(self, predicate: Callable[[Dict[str, Any]], bool]) -> "ColumnarTable":
        records = self.to_records()
        filtered = [r for r in records if predicate(r)]
        return ColumnarTable.from_records(filtered)

    def add_column(self, name: str, values: List[Any]) -> None:
        vals = list(values)
        if self._num_rows == 0:
            self._num_rows = len(vals)
        elif len(vals) != self._num_rows:
            raise ValueError(f"Column length {len(vals)} does not match table row count {self._num_rows}")
        self._columns[name] = vals

    def drop_column(self, name: str) -> None:
        if name in self._columns:
            del self._columns[name]

    def rename_column(self, old_name: str, new_name: str) -> None:
        if old_name in self._columns:
            self._columns[new_name] = self._columns.pop(old_name)

    def sort_by(self, column: str, descending: bool = False) -> "ColumnarTable":
        if column not in self._columns:
            raise KeyError(f"Column '{column}' not found")
        vals = self._columns[column]
        indexed = list(enumerate(vals))
        indexed.sort(
            key=lambda item: (item[1] is None, item[1] if item[1] is not None else 0),
            reverse=descending,
        )
        indices = [idx for idx, _ in indexed]
        res = ColumnarTable()
        for k, col in self._columns.items():
            res._columns[k] = [col[i] for i in indices]
        res._num_rows = self._num_rows
        return res

    def aggregate(self, column: str, agg: str) -> Any:
        if column not in self._columns:
            raise KeyError(f"Column '{column}' not found")
        vals = [v for v in self._columns[column] if v is not None]
        agg = agg.strip().lower()
        if not vals:
            return 0.0 if agg in ("sum", "mean", "std", "count") else None
        if agg == "count":
            return len(vals)
        num_vals = [float(v) for v in vals if isinstance(v, (int, float))]
        if not num_vals:
            return None
        if agg == "sum":
            return round(sum(num_vals), 4)
        if agg in ("mean", "avg"):
            return round(sum(num_vals) / len(num_vals), 4)
        if agg in ("min", "minimum"):
            return min(num_vals)
        if agg in ("max", "maximum"):
            return max(num_vals)
        if agg == "median":
            s = sorted(num_vals)
            mid = len(s) // 2
            return s[mid] if len(s) % 2 != 0 else round((s[mid - 1] + s[mid]) / 2.0, 4)
        if agg == "std":
            m = sum(num_vals) / len(num_vals)
            return round(math.sqrt(sum((x - m) ** 2 for x in num_vals) / max(1, len(num_vals) - 1)), 4)
        raise ValueError(f"Unknown aggregation function '{agg}'")

    def head(self, n: int = 5) -> "ColumnarTable":
        return self.slice(0, n)

    def tail(self, n: int = 5) -> "ColumnarTable":
        start = max(0, self._num_rows - n)
        return self.slice(start, self._num_rows)

    def slice(self, start: int, stop: int) -> "ColumnarTable":
        res = ColumnarTable()
        for k, v in self._columns.items():
            res._columns[k] = v[start:stop]
        res._num_rows = max(0, min(stop, self._num_rows) - max(0, start))
        return res

    def describe(self) -> Dict[str, Dict[str, float]]:
        desc = {}
        for col in self.column_names:
            nums = [float(v) for v in self._columns[col] if isinstance(v, (int, float))]
            if nums:
                m = sum(nums) / len(nums)
                var = sum((x - m) ** 2 for x in nums) / max(1, len(nums) - 1)
                desc[col] = {
                    "count": float(len(nums)),
                    "mean": round(m, 4),
                    "std": round(math.sqrt(var), 4),
                    "min": float(min(nums)),
                    "max": float(max(nums)),
                }
        return desc

    def __getitem__(self, item: Any) -> Any:
        if isinstance(item, str):
            return self._columns[item]
        if isinstance(item, int):
            return {k: self._columns[k][item] for k in self._columns}
        raise TypeError(f"ColumnarTable subscript must be str or int, got {type(item).__name__}")

    def __len__(self) -> int:
        return self._num_rows

    def __contains__(self, item: Any) -> bool:
        return item in self._columns

    def __repr__(self) -> str:
        cols = ", ".join(f"{k} [{self.dtypes.get(k, 'unknown')}]: {len(v)}" for k, v in self._columns.items())
        return f"<ColumnarTable rows={self._num_rows} cols={self.num_cols} ({cols})>"


def data_to_columnar(data: Any) -> ColumnarTable:
    """Convert dataset records, list of dicts, or dictionary of columns into a ColumnarTable."""
    if isinstance(data, ColumnarTable):
        return data
    if isinstance(data, dict):
        return ColumnarTable(data)
    rows = _to_record_list(data)
    return ColumnarTable.from_records(rows)


def columnar_to_records(table: Any) -> List[Dict[str, Any]]:
    """Convert ColumnarTable back to standard list of dictionary records."""
    if isinstance(table, ColumnarTable):
        return table.to_records()
    return _to_record_list(table)


# -------------------------------------------------------------------------
# Fuzzy Matching and String Similarities
# -------------------------------------------------------------------------

def _levenshtein_distance(s1: str, s2: str) -> int:
    """Computes exact edit distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def _levenshtein_similarity(s1: str, s2: str) -> float:
    """Normalized Levenshtein similarity ratio between 0.0 and 1.0."""
    a, b = str(s1).lower().strip(), str(s2).lower().strip()
    if a == b:
        return 1.0
    max_len = max(len(a), len(b))
    if max_len == 0:
        return 1.0
    dist = _levenshtein_distance(a, b)
    return round(1.0 - (dist / max_len), 4)


def _jaccard_similarity(s1: str, s2: str) -> float:
    """Jaccard word-level token similarity between 0.0 and 1.0."""
    t1 = set(re.findall(r"\w+", str(s1).lower()))
    t2 = set(re.findall(r"\w+", str(s2).lower()))
    if not t1 and not t2:
        return 1.0
    union = t1 | t2
    if not union:
        return 0.0
    return round(len(t1 & t2) / len(union), 4)


def data_fuzzy_join(
    left_data: Any,
    right_data: Any,
    left_on: str,
    right_on: str,
    threshold: float = 0.8,
    metric: str = "levenshtein",
    how: str = "inner",
) -> List[Dict[str, Any]]:
    """Approximate string matching join between two datasets."""
    left_rows = _to_record_list(left_data)
    right_rows = _to_record_list(right_data)
    thresh = float(threshold)
    sim_fn = _jaccard_similarity if metric.lower() == "jaccard" else _levenshtein_similarity
    how = how.lower()

    results: List[Dict[str, Any]] = []
    matched_right_indices = set()

    for l_idx, l_row in enumerate(left_rows):
        l_val = l_row.get(left_on, "")
        best_match = None
        best_score = -1.0
        best_r_idx = -1

        for r_idx, r_row in enumerate(right_rows):
            r_val = r_row.get(right_on, "")
            score = sim_fn(str(l_val), str(r_val))
            if score >= thresh and score > best_score:
                best_score = score
                best_match = r_row
                best_r_idx = r_idx

        if best_match is not None:
            matched_right_indices.add(best_r_idx)
            combined = dict(l_row)
            for k, v in best_match.items():
                if k in combined and k != left_on:
                    combined[f"right_{k}"] = v
                else:
                    combined[k] = v
            combined["similarity_score"] = best_score
            results.append(combined)
        elif how in ("left", "outer"):
            combined = dict(l_row)
            combined["similarity_score"] = 0.0
            results.append(combined)

    if how in ("right", "outer"):
        for r_idx, r_row in enumerate(right_rows):
            if r_idx not in matched_right_indices:
                combined = dict(r_row)
                combined["similarity_score"] = 0.0
                results.append(combined)

    return results


# -------------------------------------------------------------------------
# Advanced Pivot, Melt, and Nested JSON Unpacking
# -------------------------------------------------------------------------

def data_pivot_advanced(
    data: Any,
    index_col: str,
    columns_col: str,
    values_col: str,
    agg_fn: str = "sum",
    fill_value: Any = 0.0,
) -> List[Dict[str, Any]]:
    """Flexible multi-function pivoting supporting sum, mean, count, min, max, std, median."""
    rows = _to_record_list(data)
    agg = agg_fn.lower().strip()

    matrix: Dict[Any, Dict[str, List[float]]] = {}
    unique_columns = set()

    for r in rows:
        idx_val = r.get(index_col)
        c_val = str(r.get(columns_col, ""))
        v_val = r.get(values_col)
        if idx_val is not None and c_val:
            unique_columns.add(c_val)
            matrix.setdefault(idx_val, {}).setdefault(c_val, [])
            if v_val is not None and isinstance(v_val, (int, float)):
                matrix[idx_val][c_val].append(float(v_val))

    sorted_cols = sorted(list(unique_columns))
    result = []

    for idx_val, col_entries in sorted(matrix.items(), key=lambda x: str(x[0])):
        row = {index_col: idx_val}
        for col_name in sorted_cols:
            vals = col_entries.get(col_name, [])
            if not vals:
                row[col_name] = fill_value
            elif agg == "count":
                row[col_name] = len(vals)
            elif agg in ("mean", "avg"):
                row[col_name] = round(sum(vals) / len(vals), 4)
            elif agg == "min":
                row[col_name] = min(vals)
            elif agg == "max":
                row[col_name] = max(vals)
            elif agg == "median":
                s = sorted(vals)
                row[col_name] = s[len(s) // 2]
            elif agg == "std":
                m = sum(vals) / len(vals)
                var = sum((x - m) ** 2 for x in vals) / max(1, len(vals) - 1)
                row[col_name] = round(math.sqrt(var), 4)
            else:  # sum default
                row[col_name] = round(sum(vals), 4)
        result.append(row)
    return result


def data_unpivot_melt(
    data: Any,
    id_vars: Any,
    value_vars: Optional[Any] = None,
    var_name: str = "variable",
    value_name: str = "value",
) -> List[Dict[str, Any]]:
    """Reshape wide table into long table unpivoting value columns."""
    rows = _to_record_list(data)
    if not rows:
        return []
    ids = [str(id_vars).strip("'\"")] if isinstance(id_vars, str) else [str(x).strip("'\"") for x in id_vars]
    
    if value_vars is not None:
        vals = [str(value_vars).strip("'\"")] if isinstance(value_vars, str) else [str(x).strip("'\"") for x in value_vars]
    else:
        vals = [k for k in rows[0].keys() if k not in ids]

    melted = []
    for r in rows:
        base = {k: r.get(k) for k in ids}
        for v_col in vals:
            m_row = dict(base)
            m_row[var_name] = v_col
            m_row[value_name] = r.get(v_col)
            melted.append(m_row)
    return melted


def data_json_explode(
    data: Any,
    column: str,
    target_column: Optional[str] = None,
    unpack_dict: bool = False,
) -> List[Dict[str, Any]]:
    """Explode nested arrays into separate rows, or unpack dictionary fields into top-level columns."""
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    tgt = str(target_column).strip("'\"") if target_column else col
    exploded: List[Dict[str, Any]] = []

    for r in rows:
        val = r.get(col)
        if isinstance(val, (list, tuple)) and val:
            for item in val:
                c = dict(r)
                c[tgt] = item
                exploded.append(c)
        elif isinstance(val, dict) and unpack_dict:
            c = dict(r)
            del c[col]
            for k, v in val.items():
                c[f"{col}_{k}"] = v
            exploded.append(c)
        else:
            exploded.append(dict(r))
    return exploded


def data_window_rolling(
    data: Any,
    column: str,
    window_size: int = 3,
    stat: str = "mean",
    min_periods: int = 1,
) -> List[Dict[str, Any]]:
    """Enhanced rolling window calculation (mean, sum, std, min, max, median)."""
    rows = _to_record_list(data)
    col = str(column).strip("'\"")
    w = max(1, int(window_size))
    st = stat.lower().strip()
    out: List[Dict[str, Any]] = []
    buf: List[float] = []

    for r in rows:
        c = dict(r)
        val = r.get(col)
        if isinstance(val, (int, float)):
            buf.append(float(val))
            if len(buf) > w:
                buf.pop(0)

            if len(buf) >= min_periods:
                if st == "sum":
                    calc = sum(buf)
                elif st in ("min", "minimum"):
                    calc = min(buf)
                elif st in ("max", "maximum"):
                    calc = max(buf)
                elif st == "median":
                    sb = sorted(buf)
                    calc = sb[len(sb) // 2]
                elif st == "std":
                    m = sum(buf) / len(buf)
                    calc = math.sqrt(sum((x - m) ** 2 for x in buf) / max(1, len(buf) - 1))
                else:  # mean
                    calc = sum(buf) / len(buf)
                c[f"{col}_rolling_{st}"] = round(calc, 4)
            else:
                c[f"{col}_rolling_{st}"] = None
        else:
            c[f"{col}_rolling_{st}"] = None
        out.append(c)
    return out




# ==============================================================================
# Advanced Data Deepening: Rolling Aggregator, Relational Joins & Pivot Tables
# ==============================================================================

class RollingAggregator:
    """O(1) amortized sliding-window aggregator with statistical moments."""

    @classmethod
    def rolling_series(
        cls,
        series: List[float],
        window: int,
        stat: str = "mean",
        min_periods: Optional[int] = None,
    ) -> List[Optional[float]]:
        """Calculates rolling metric over a sequence of numbers."""
        n = len(series)
        w = max(1, int(window))
        min_p = min_periods if min_periods is not None else w
        res: List[Optional[float]] = []

        window_buf: List[float] = []
        running_sum = 0.0

        for i in range(n):
            val = float(series[i])
            window_buf.append(val)
            running_sum += val
            if len(window_buf) > w:
                running_sum -= window_buf.pop(0)

            if len(window_buf) < min_p:
                res.append(None)
                continue

            cur_w = len(window_buf)
            st = stat.lower().strip()
            if st == "sum":
                res.append(round(running_sum, 4))
            elif st == "mean" or st == "avg":
                res.append(round(running_sum / cur_w, 4))
            elif st == "min":
                res.append(round(min(window_buf), 4))
            elif st == "max":
                res.append(round(max(window_buf), 4))
            elif st == "std" or st == "stddev":
                m = running_sum / cur_w
                var = sum((x - m) ** 2 for x in window_buf) / max(1, cur_w - 1)
                res.append(round(math.sqrt(var), 4))
            else:
                res.append(round(running_sum / cur_w, 4))

        return res


class RelationalJoinEngine:
    """Hash-join engine supporting inner, left, right, outer, and cross joins."""

    @staticmethod
    def _extract_key(row: Dict[str, Any], keys: List[str]) -> Tuple[Any, ...]:
        return tuple(row.get(k) for k in keys)

    @classmethod
    def join(
        cls,
        left: List[Dict[str, Any]],
        right: List[Dict[str, Any]],
        on: Union[str, List[str]],
        how: str = "inner",
        suffixes: Tuple[str, str] = ("_left", "_right"),
    ) -> List[Dict[str, Any]]:
        """
        Executes relational hash join between two lists of dict records.
        `how` in ('inner', 'left', 'right', 'outer', 'cross')
        """
        how = how.lower().strip()
        if how == "cross":
            results = []
            for l in left:
                for r in right:
                    merged = dict(l)
                    for k, v in r.items():
                        key_name = f"{k}{suffixes[1]}" if k in merged else k
                        merged[key_name] = v
                    results.append(merged)
            return results

        join_keys = [on] if isinstance(on, str) else list(on)

        # Build hash table on right table
        hash_table: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = {}
        for r_idx, r in enumerate(right):
            k = cls._extract_key(r, join_keys)
            hash_table.setdefault(k, []).append(r)

        results = []
        matched_right_keys = set()

        # Probe with left table
        for l in left:
            k = cls._extract_key(l, join_keys)
            if k in hash_table:
                matched_right_keys.add(k)
                for r in hash_table[k]:
                    merged = dict(l)
                    for rk, rv in r.items():
                        if rk in join_keys:
                            continue
                        dest_key = f"{rk}{suffixes[1]}" if rk in merged else rk
                        merged[dest_key] = rv
                    results.append(merged)
            elif how in ("left", "outer"):
                merged = dict(l)
                # Fill right keys with None
                for rk in right[0].keys() if right else []:
                    if rk not in join_keys and rk not in merged:
                        merged[rk] = None
                results.append(merged)

        # Right / Outer un-matched right rows
        if how in ("right", "outer"):
            left_keys_template = list(left[0].keys()) if left else []
            for k, rows in hash_table.items():
                if k not in matched_right_keys:
                    for r in rows:
                        merged = {lk: None for lk in left_keys_template if lk not in join_keys}
                        merged.update(r)
                        results.append(merged)

        return results


class PivotTableEngine:
    """Multi-dimensional pivot table aggregation generator."""

    @classmethod
    def pivot(
        cls,
        records: List[Dict[str, Any]],
        index: str,
        columns: str,
        values: str,
        aggfunc: str = "sum",
        fill_value: Any = 0.0,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Aggregates records into a 2D pivot dictionary: {row_index: {col_key: aggregated_value}}
        """
        buckets: Dict[Any, Dict[Any, List[float]]] = {}
        all_cols = set()

        for r in records:
            idx_val = str(r.get(index, ""))
            col_val = str(r.get(columns, ""))
            v = r.get(values)
            if v is None:
                continue
            all_cols.add(col_val)
            buckets.setdefault(idx_val, {}).setdefault(col_val, []).append(float(v))

        func = aggfunc.lower().strip()
        pivot_table: Dict[str, Dict[str, Any]] = {}

        for row_k, cols_dict in sorted(buckets.items()):
            pivot_table[row_k] = {}
            for col_k in sorted(all_cols):
                vals = cols_dict.get(col_k, [])
                if not vals:
                    pivot_table[row_k][col_k] = fill_value
                    continue

                if func == "sum":
                    calc = sum(vals)
                elif func in ("mean", "avg"):
                    calc = sum(vals) / len(vals)
                elif func == "count":
                    calc = len(vals)
                elif func == "min":
                    calc = min(vals)
                elif func == "max":
                    calc = max(vals)
                else:
                    calc = sum(vals)

                pivot_table[row_k][col_k] = round(calc, 4) if isinstance(calc, float) else calc

        return pivot_table


def data_relational_join(
    left: List[Dict[str, Any]],
    right: List[Dict[str, Any]],
    on: Union[str, List[str]],
    how: str = "inner",
) -> List[Dict[str, Any]]:
    """Performs relational hash join between two tables."""
    return RelationalJoinEngine.join(left, right, on, how)


def data_rolling_aggregate(series: List[float], window: int, stat: str = "mean") -> List[Optional[float]]:
    """Computes rolling window aggregate series."""
    return RollingAggregator.rolling_series(series, window, stat)


# ==============================================================================
# STREAMING & PROBABILISTIC SKETCHES (HYPERLOGLOG, COUNT-MIN, RESERVOIR)
# ==============================================================================

class HyperLogLogSketch:
    """HyperLogLog cardinality estimator with 64-bit hashing and small-range linear bias correction."""

    def __init__(self, precision: int = 10):
        self.p = max(4, min(16, int(precision)))
        self.m = 1 << self.p
        self.registers = [0] * self.m

        # Alpha bias correction constant
        if self.m == 16:
            self.alpha = 0.673
        elif self.m == 32:
            self.alpha = 0.697
        elif self.m == 64:
            self.alpha = 0.709
        else:
            self.alpha = 0.7213 / (1.0 + 1.079 / self.m)

    def _hash64(self, val: Any) -> int:
        s = str(val).encode("utf-8")
        h = hashlib.sha256(s).digest()
        # Extract 64 bits from sha256 digest
        return int.from_bytes(h[:8], byteorder="big", signed=False)

    def add(self, item: Any) -> None:
        """Adds element to the HyperLogLog register sketch."""
        x = self._hash64(item)
        idx = x >> (64 - self.p)
        w = x & ((1 << (64 - self.p)) - 1)

        # Count leading zeros + 1
        lz = 1
        if w != 0:
            lz = (64 - self.p) - w.bit_length() + 1
        else:
            lz = (64 - self.p) + 1

        if lz > self.registers[idx]:
            self.registers[idx] = lz

    def estimate(self) -> int:
        """Estimates total unique items seen."""
        z = sum(2.0 ** (-reg) for reg in self.registers)
        if z == 0:
            return 0
        raw_e = self.alpha * (self.m ** 2) / z

        # Small range linear counting correction
        if raw_e <= 2.5 * self.m:
            zeros = self.registers.count(0)
            if zeros != 0:
                raw_e = self.m * math.log(self.m / zeros)

        return int(round(raw_e))


class CountMinSketch:
    """Count-Min Sketch frequency estimation for high-velocity streaming data."""

    def __init__(self, width: int = 1000, depth: int = 5):
        self.width = max(10, int(width))
        self.depth = max(1, int(depth))
        self.table = [[0] * self.width for _ in range(self.depth)]
        self.total_count = 0

    def _hash(self, item: Any, seed: int) -> int:
        s = f"{item}:{seed}".encode("utf-8")
        h = hashlib.md5(s).digest()
        val = int.from_bytes(h[:4], byteorder="big", signed=False)
        return val % self.width

    def add(self, item: Any, count: int = 1) -> None:
        """Increments item count across all hash rows."""
        c = int(count)
        for i in range(self.depth):
            col = self._hash(item, i)
            self.table[i][col] += c
        self.total_count += c

    def estimate(self, item: Any) -> int:
        """Returns the conservative point frequency estimate for the item."""
        min_est = float("inf")
        for i in range(self.depth):
            col = self._hash(item, i)
            min_est = min(min_est, self.table[i][col])
        return int(min_est) if min_est != float("inf") else 0


class ReservoirSamplerStream:
    """Reservoir sampling for uniform random sample of size K from streaming data."""

    def __init__(self, k: int, seed: Optional[int] = 42):
        self.k = max(1, int(k))
        self.reservoir: List[Any] = []
        self.total_seen = 0
        import random
        self.rng = random.Random(seed)

    def feed(self, item: Any) -> None:
        """Feeds a single streaming item into the reservoir."""
        if len(self.reservoir) < self.k:
            self.reservoir.append(item)
        else:
            j = self.rng.randint(0, self.total_seen)
            if j < self.k:
                self.reservoir[j] = item
        self.total_seen += 1

    def feed_batch(self, items: List[Any]) -> None:
        """Feeds a batch of items."""
        for item in items:
            self.feed(item)

    def get_sample(self) -> List[Any]:
        """Returns the current uniform random reservoir sample."""
        return list(self.reservoir)


def data_hll_create(precision: int = 10) -> Any:
    """Creates a HyperLogLog cardinality estimation sketch."""
    hll = HyperLogLogSketch(precision=precision)
    return Record({
        "precision": hll.p,
        "registers_count": hll.m,
        "instance": hll,
    })


def data_hll_add(hll: Any, items: List[Any]) -> Any:
    """Adds items to HyperLogLog sketch."""
    inst = hll.instance if hasattr(hll, "instance") else hll
    for item in items:
        inst.add(item)
    return Record({
        "estimate": inst.estimate(),
        "instance": inst,
    })


def data_hll_estimate(hll: Any) -> int:
    """Returns cardinality estimate from HyperLogLog sketch."""
    inst = hll.instance if hasattr(hll, "instance") else hll
    return inst.estimate()


def data_cms_create(width: int = 1000, depth: int = 5) -> Any:
    """Creates a Count-Min Sketch frequency table."""
    cms = CountMinSketch(width=width, depth=depth)
    return Record({
        "width": cms.width,
        "depth": cms.depth,
        "instance": cms,
    })


def data_cms_add(cms: Any, items: List[Any]) -> Any:
    """Updates Count-Min Sketch with items."""
    inst = cms.instance if hasattr(cms, "instance") else cms
    for item in items:
        inst.add(item)
    return Record({
        "total_count": inst.total_count,
        "instance": inst,
    })


def data_cms_estimate(cms: Any, item: Any) -> int:
    """Estimates frequency of item in Count-Min Sketch."""
    inst = cms.instance if hasattr(cms, "instance") else cms
    return inst.estimate(item)


def data_reservoir_sample(stream: List[Any], k: int) -> List[Any]:
    """Uniformly samples k items from a data stream using Reservoir Sampling."""
    sampler = ReservoirSamplerStream(k)
    sampler.feed_batch(stream)
    return sampler.get_sample()


# ==============================================================================
# T-DIGEST QUANTILE APPROXIMATION & ROARING BITMAP ENGINES
# ==============================================================================


class TDigestQuantileApproximator:
    """Ted Dunning's t-digest algorithm for accurate streaming quantile estimation.

    Provides high accuracy at extreme percentiles (e.g. p99, p99.9, p99.99)
    using scale-bounded centroid clustering with compression parameter delta.
    """

    class Centroid:
        def __init__(self, mean: float, weight: float):
            self.mean = float(mean)
            self.weight = float(weight)

    def __init__(self, delta: float = 100.0, max_buffer_size: int = 500):
        self.delta = float(delta)
        self.max_buffer_size = max_buffer_size
        self.centroids: List[TDigestQuantileApproximator.Centroid] = []
        self.buffer: List[Tuple[float, float]] = []
        self.total_weight: float = 0.0
        self.min_val: float = float("inf")
        self.max_val: float = float("-inf")

    def add(self, value: float, weight: float = 1.0) -> None:
        """Adds a weighted value to the sketch."""
        val_f = float(value)
        w_f = float(weight)
        if val_f < self.min_val:
            self.min_val = val_f
        if val_f > self.max_val:
            self.max_val = val_f

        self.buffer.append((val_f, w_f))
        if len(self.buffer) >= self.max_buffer_size:
            self.compress()

    def add_batch(self, values: List[float]) -> None:
        """Adds multiple values to the sketch."""
        for v in values:
            self.add(v)

    def compress(self) -> None:
        """Merges buffered samples into centroids respecting scale function bound."""
        if not self.buffer:
            return

        all_points = [(c.mean, c.weight) for c in self.centroids] + self.buffer
        all_points.sort(key=lambda p: p[0])
        self.buffer = []

        total_w = sum(p[1] for p in all_points)
        if total_w == 0.0:
            return
        self.total_weight = total_w

        new_centroids: List[TDigestQuantileApproximator.Centroid] = []
        cur_mean, cur_w = all_points[0]
        q0 = 0.0

        for mean, w in all_points[1:]:
            q1 = q0 + (cur_w + w) / total_w
            limit = 4.0 * total_w * max(1e-5, min(q1, 1.0 - q1)) / self.delta
            if cur_w + w <= max(1.0, limit):
                cur_mean = (cur_mean * cur_w + mean * w) / (cur_w + w)
                cur_w += w
            else:
                new_centroids.append(TDigestQuantileApproximator.Centroid(cur_mean, cur_w))
                q0 += cur_w / total_w
                cur_mean, cur_w = mean, w

        new_centroids.append(TDigestQuantileApproximator.Centroid(cur_mean, cur_w))
        self.centroids = new_centroids

    def quantile(self, q: float) -> float:
        """Estimates the value at quantile q in [0.0, 1.0]."""
        self.compress()
        if not self.centroids:
            return 0.0
        if q <= 0.0 or len(self.centroids) == 1:
            return self.min_val if self.min_val != float("inf") else self.centroids[0].mean
        if q >= 1.0:
            return self.max_val if self.max_val != float("-inf") else self.centroids[-1].mean

        target_w = q * self.total_weight
        accum = 0.0

        for i, c in enumerate(self.centroids):
            if accum + c.weight >= target_w:
                if i == 0:
                    frac = target_w / max(1e-12, c.weight)
                    return self.min_val + frac * (c.mean - self.min_val)
                prev = self.centroids[i - 1]
                frac = (target_w - accum) / max(1e-12, c.weight)
                return prev.mean + frac * (c.mean - prev.mean)
            accum += c.weight

        return self.max_val

    def cdf(self, x: float) -> float:
        """Estimates the cumulative distribution function P(X <= x)."""
        self.compress()
        if not self.centroids:
            return 0.0
        if x < self.min_val:
            return 0.0
        if x >= self.max_val:
            return 1.0

        accum = 0.0
        for i, c in enumerate(self.centroids):
            if x < c.mean:
                if i == 0:
                    frac = (x - self.min_val) / max(1e-12, c.mean - self.min_val)
                    return max(0.0, min(1.0, frac * c.weight / self.total_weight))
                prev = self.centroids[i - 1]
                frac = (x - prev.mean) / max(1e-12, c.mean - prev.mean)
                return max(0.0, min(1.0, (accum + frac * c.weight) / self.total_weight))
            accum += c.weight

        return 1.0

    def summary(self) -> Dict[str, Any]:
        """Returns statistical summary of the t-digest."""
        self.compress()
        mean = (
            sum(c.mean * c.weight for c in self.centroids) / self.total_weight
            if self.total_weight > 0
            else 0.0
        )
        return {
            "count": self.total_weight,
            "min": self.min_val if self.min_val != float("inf") else 0.0,
            "max": self.max_val if self.max_val != float("-inf") else 0.0,
            "mean": mean,
            "centroid_count": len(self.centroids),
            "delta": self.delta,
            "p50": self.quantile(0.50),
            "p90": self.quantile(0.90),
            "p95": self.quantile(0.95),
            "p99": self.quantile(0.99),
        }


class RoaringBitmapPure:
    """Pure-Python implementation of Roaring Bitmaps for high-performance integer sets.

    Uses 16-bit segmented chunk storage with ArrayContainers (sparse sorted lists),
    BitmapContainers (1024-word bitsets), and RunContainers (interval runs)
    for fast set operations: union, intersection, difference, and rank/select queries.
    """

    ARRAY_LIMIT = 4096

    def __init__(self, values: Optional[List[int]] = None):
        self.chunks: Dict[int, Dict[str, Any]] = {}
        if values:
            for v in values:
                self.add(v)

    def add(self, val: int) -> None:
        """Adds a non-negative 32-bit integer to the bitmap."""
        val = int(val) & 0xFFFFFFFF
        chunk = val >> 16
        low = val & 0xFFFF

        if chunk not in self.chunks:
            self.chunks[chunk] = {"type": "array", "data": [low]}
            return

        c = self.chunks[chunk]
        ctype = c["type"]

        if ctype == "array":
            arr: List[int] = c["data"]
            import bisect
            idx = bisect.bisect_left(arr, low)
            if idx < len(arr) and arr[idx] == low:
                return
            arr.insert(idx, low)
            if len(arr) > self.ARRAY_LIMIT:
                words = [0] * 1024
                for item in arr:
                    words[item // 64] |= 1 << (item % 64)
                self.chunks[chunk] = {"type": "bitmap", "data": words, "cardinality": len(arr)}
        elif ctype == "bitmap":
            words = c["data"]
            w_idx = low // 64
            bit_mask = 1 << (low % 64)
            if not (words[w_idx] & bit_mask):
                words[w_idx] |= bit_mask
                c["cardinality"] = c.get("cardinality", 0) + 1
        elif ctype == "run":
            arr = self._run_to_array(c["data"])
            if low not in arr:
                import bisect
                bisect.insort(arr, low)
            self.chunks[chunk] = {"type": "array", "data": arr}

    def contains(self, val: int) -> bool:
        """Tests whether value is present in the bitmap."""
        val = int(val) & 0xFFFFFFFF
        chunk = val >> 16
        low = val & 0xFFFF

        if chunk not in self.chunks:
            return False

        c = self.chunks[chunk]
        ctype = c["type"]

        if ctype == "array":
            arr = c["data"]
            import bisect
            idx = bisect.bisect_left(arr, low)
            return idx < len(arr) and arr[idx] == low
        elif ctype == "bitmap":
            words = c["data"]
            return bool(words[low // 64] & (1 << (low % 64)))
        elif ctype == "run":
            for start, length in c["data"]:
                if start <= low <= start + length:
                    return True
            return False
        return False

    def cardinality(self) -> int:
        """Returns exact count of integers stored in the bitmap."""
        total = 0
        for c in self.chunks.values():
            ctype = c["type"]
            if ctype == "array":
                total += len(c["data"])
            elif ctype == "bitmap":
                total += c.get("cardinality", sum(bin(w).count("1") for w in c["data"]))
            elif ctype == "run":
                total += sum(length + 1 for start, length in c["data"])
        return total

    @staticmethod
    def _run_to_array(runs: List[Tuple[int, int]]) -> List[int]:
        out = []
        for start, length in runs:
            out.extend(range(start, start + length + 1))
        return out

    def to_list(self) -> List[int]:
        """Returns sorted list of all 32-bit integers in the bitmap."""
        result: List[int] = []
        for chunk in sorted(self.chunks.keys()):
            prefix = chunk << 16
            c = self.chunks[chunk]
            ctype = c["type"]
            if ctype == "array":
                result.extend(prefix | x for x in c["data"])
            elif ctype == "bitmap":
                words = c["data"]
                for w_idx, w in enumerate(words):
                    if w != 0:
                        base = w_idx * 64
                        for bit in range(64):
                            if w & (1 << bit):
                                result.append(prefix | (base + bit))
            elif ctype == "run":
                for start, length in c["data"]:
                    result.extend(prefix | x for x in range(start, start + length + 1))
        return sorted(result)

    def union(self, other: "RoaringBitmapPure") -> "RoaringBitmapPure":
        """Computes bitwise union (self | other)."""
        res = RoaringBitmapPure()
        all_chunks = set(self.chunks.keys()) | set(other.chunks.keys())
        for chunk in all_chunks:
            if chunk not in other.chunks:
                res.chunks[chunk] = json.loads(json.dumps(self.chunks[chunk]))
            elif chunk not in self.chunks:
                res.chunks[chunk] = json.loads(json.dumps(other.chunks[chunk]))
            else:
                s1 = set(self._chunk_to_values(self.chunks[chunk]))
                s2 = set(other._chunk_to_values(other.chunks[chunk]))
                res_set = sorted(list(s1 | s2))
                if len(res_set) <= self.ARRAY_LIMIT:
                    res.chunks[chunk] = {"type": "array", "data": res_set}
                else:
                    words = [0] * 1024
                    for item in res_set:
                        words[item // 64] |= 1 << (item % 64)
                    res.chunks[chunk] = {"type": "bitmap", "data": words, "cardinality": len(res_set)}
        return res

    def intersection(self, other: "RoaringBitmapPure") -> "RoaringBitmapPure":
        """Computes bitwise intersection (self & other)."""
        res = RoaringBitmapPure()
        common_chunks = set(self.chunks.keys()) & set(other.chunks.keys())
        for chunk in common_chunks:
            s1 = set(self._chunk_to_values(self.chunks[chunk]))
            s2 = set(other._chunk_to_values(other.chunks[chunk]))
            inter = sorted(list(s1 & s2))
            if inter:
                if len(inter) <= self.ARRAY_LIMIT:
                    res.chunks[chunk] = {"type": "array", "data": inter}
                else:
                    words = [0] * 1024
                    for item in inter:
                        words[item // 64] |= 1 << (item % 64)
                    res.chunks[chunk] = {"type": "bitmap", "data": words, "cardinality": len(inter)}
        return res

    def difference(self, other: "RoaringBitmapPure") -> "RoaringBitmapPure":
        """Computes set difference (self - other)."""
        res = RoaringBitmapPure()
        for chunk in self.chunks:
            if chunk not in other.chunks:
                res.chunks[chunk] = json.loads(json.dumps(self.chunks[chunk]))
            else:
                s1 = set(self._chunk_to_values(self.chunks[chunk]))
                s2 = set(other._chunk_to_values(other.chunks[chunk]))
                diff = sorted(list(s1 - s2))
                if diff:
                    res.chunks[chunk] = {"type": "array", "data": diff}
        return res

    @classmethod
    def _chunk_to_values(cls, c: Dict[str, Any]) -> List[int]:
        ctype = c["type"]
        if ctype == "array":
            return c["data"]
        elif ctype == "bitmap":
            out = []
            for w_idx, w in enumerate(c["data"]):
                if w != 0:
                    base = w_idx * 64
                    for bit in range(64):
                        if w & (1 << bit):
                            out.append(base + bit)
            return out
        elif ctype == "run":
            return cls._run_to_array(c["data"])
        return []


def data_tdigest_create(delta: float = 100.0) -> Any:
    """Creates a TDigest quantile approximator."""
    td = TDigestQuantileApproximator(delta=delta)
    return Record({
        "delta": td.delta,
        "instance": td,
    })


def data_tdigest_add(digest_handle: Any, values: List[float]) -> Any:
    """Feeds batch of values into TDigest sketch."""
    inst = digest_handle.instance if hasattr(digest_handle, "instance") else digest_handle
    inst.add_batch(values)
    return Record(inst.summary())


def data_tdigest_quantile(digest_handle: Any, q: float) -> float:
    """Queries quantile q from TDigest sketch."""
    inst = digest_handle.instance if hasattr(digest_handle, "instance") else digest_handle
    return inst.quantile(q)


def data_tdigest_cdf(digest_handle: Any, x: float) -> float:
    """Queries cumulative probability P(X <= x) from TDigest sketch."""
    inst = digest_handle.instance if hasattr(digest_handle, "instance") else digest_handle
    return inst.cdf(x)


def data_roaring_create(values: Optional[List[int]] = None) -> Any:
    """Creates a compressed Roaring Bitmap."""
    rb = RoaringBitmapPure(values)
    return Record({
        "cardinality": rb.cardinality(),
        "instance": rb,
    })


def data_roaring_add(bitmap_handle: Any, value: int) -> Any:
    """Adds integer to Roaring Bitmap."""
    inst = bitmap_handle.instance if hasattr(bitmap_handle, "instance") else bitmap_handle
    inst.add(value)
    return Record({
        "cardinality": inst.cardinality(),
        "instance": inst,
    })


def data_roaring_contains(bitmap_handle: Any, value: int) -> bool:
    """Checks membership in Roaring Bitmap."""
    inst = bitmap_handle.instance if hasattr(bitmap_handle, "instance") else bitmap_handle
    return inst.contains(value)


def data_roaring_operation(bitmap_a: Any, bitmap_b: Any, op: str = "union") -> Any:
    """Performs set operation between two Roaring Bitmaps."""
    inst_a = bitmap_a.instance if hasattr(bitmap_a, "instance") else bitmap_a
    inst_b = bitmap_b.instance if hasattr(bitmap_b, "instance") else bitmap_b

    op_lower = op.lower().strip()
    if op_lower in ("union", "or", "|"):
        res = inst_a.union(inst_b)
    elif op_lower in ("intersection", "and", "&"):
        res = inst_a.intersection(inst_b)
    elif op_lower in ("difference", "diff", "sub", "-"):
        res = inst_a.difference(inst_b)
    else:
        raise ValueError(f"Unknown roaring bitmap operation: {op}")

    return Record({
        "cardinality": res.cardinality(),
        "instance": res,
    })


def data_roaring_stats(bitmap_handle: Any) -> Any:
    """Returns statistics of Roaring Bitmap."""
    inst = bitmap_handle.instance if hasattr(bitmap_handle, "instance") else bitmap_handle
    return Record({
        "cardinality": inst.cardinality(),
        "chunks_count": len(inst.chunks),
        "chunk_types": {k: c["type"] for k, c in inst.chunks.items()},
    })


