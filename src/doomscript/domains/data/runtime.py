"""Runtime execution engine for Data Engineering pipelines and operations."""

import csv
import json
import math
import os
import re
from typing import Any, Dict, List, Optional
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
