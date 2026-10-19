"""
DoomScript Universal Introspection Framework.

Standardizes runtime introspection across all domains and taxonomy values:
- explain(target) -> Record/Dict with metadata, schema, and capabilities
- summary_of(target) -> Statistical or structural summary
- preview_of(target, n=5) -> Representative preview slice
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import statistics
from doomscript.taxonomy import Table, RecordList, ValueKind, classify_value, to_table
from doomscript.runtime import Record


def explain_domain(domain_name: str) -> Record:
    """Introspect a registered domain contract."""
    from doomscript.domains.registry import get_domain_registry
    domain = get_domain_registry().get_domain(domain_name)
    if not domain:
        raise ValueError(f"Domain '{domain_name}' is not registered.")
    
    verb_list = []
    for v in domain.verbs:
        verb_list.append(Record({
            "name": v.name,
            "template": v.pattern,
            "args": v.arg_schema,
            "returns": v.returns,
            "description": v.description,
        }))

    return Record({
        "type": "domain",
        "name": domain.name,
        "version": getattr(domain, "version", "1.0.0"),
        "description": getattr(domain, "description", ""),
        "verbs": verb_list,
        "capabilities": list(getattr(domain, "capabilities", [])),
        "optional_dependencies": list(getattr(domain, "optional_dependencies", [])),
    })


def explain(target: Any) -> Record:
    """Universal explanation and metadata introspection for any runtime object or domain."""
    if isinstance(target, str):
        from doomscript.domains.registry import get_domain_registry
        if get_domain_registry().get_domain(target):
            return explain_domain(target)
    
    if hasattr(target, "__explain__") and callable(target.__explain__):
        res = target.__explain__()
        return res if isinstance(res, Record) else Record(res)
    
    if hasattr(target, "explain") and callable(target.explain):
        res = target.explain()
        return res if isinstance(res, Record) else Record(res)

    kind = classify_value(target)
    
    if kind in (ValueKind.TABLE, ValueKind.RECORD_LIST) or (isinstance(target, list) and target and isinstance(target[0], (dict, Record))):
        tbl = to_table(target)
        missing_counts = {}
        for col in tbl.columns:
            missing_counts[col] = sum(1 for r in tbl.rows if r[tbl.columns.index(col)] is None)
        return Record({
            "type": "table",
            "name": tbl.name,
            "row_count": tbl.row_count,
            "column_count": tbl.column_count,
            "columns": tbl.columns,
            "schema": tbl.schema,
            "missing_counts": Record(missing_counts),
        })

    if kind == ValueKind.PLOT or hasattr(target, "to_spec"):
        spec = target.to_spec() if hasattr(target, "to_spec") else {}
        return Record({
            "type": "plot",
            "kind": getattr(target, "plot_type", spec.get("type", "chart")),
            "title": getattr(target, "title", spec.get("title", "")),
            "layers": getattr(target, "layers", []),
            "mappings": getattr(target, "mappings", {}),
        })

    if kind == ValueKind.GRAPH or hasattr(target, "nodes"):
        nodes_len = len(target.nodes) if hasattr(target, "nodes") else 0
        edges_len = len(target.edges) if hasattr(target, "edges") else 0
        return Record({
            "type": "graph",
            "node_count": nodes_len,
            "edge_count": edges_len,
            "directed": getattr(target, "directed", False),
        })

    if kind == ValueKind.MODEL or hasattr(target, "predict"):
        return Record({
            "type": "model",
            "model_type": type(target).__name__,
            "features": getattr(target, "features", []),
            "target": getattr(target, "target", None),
        })

    if kind == ValueKind.AGENT:
        return Record({
            "type": "agent",
            "role": getattr(target, "role", "assistant"),
            "memory_size": len(getattr(target, "memory", [])),
        })

    return Record({
        "type": type(target).__name__,
        "value_kind": kind.value,
        "repr": repr(target),
    })


def preview_of(target: Any, n: int = 5) -> Any:
    """Return a representative sample or preview slice of the target object."""
    if hasattr(target, "preview") and callable(target.preview):
        return target.preview(n)
    
    if isinstance(target, Table):
        return target.to_records()[:n]
    
    if isinstance(target, (list, tuple)):
        return target[:n]
    
    if isinstance(target, dict):
        keys = list(target.keys())[:n]
        return Record({k: target[k] for k in keys})
    
    if isinstance(target, str):
        return target[:100] + ("..." if len(target) > 100 else "")
    
    return target


def summary_of(target: Any) -> Record:
    """Compute statistical or structural summary of the target object."""
    if hasattr(target, "summary") and callable(target.summary):
        res = target.summary()
        return res if isinstance(res, Record) else Record(res)
    
    kind = classify_value(target)
    if kind in (ValueKind.TABLE, ValueKind.RECORD_LIST) or (isinstance(target, list) and target and isinstance(target[0], (dict, Record))):
        tbl = to_table(target)
        col_summaries = {}
        for col in tbl.columns:
            idx = tbl.columns.index(col)
            vals = [r[idx] for r in tbl.rows if idx < len(r) and r[idx] is not None]
            numeric_vals = [v for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool)]
            if numeric_vals:
                col_summaries[col] = Record({
                    "count": len(vals),
                    "mean": sum(numeric_vals) / len(numeric_vals),
                    "min": min(numeric_vals),
                    "max": max(numeric_vals),
                })
            else:
                col_summaries[col] = Record({
                    "count": len(vals),
                    "distinct": len(set(vals)),
                })
        return Record(col_summaries)

    if isinstance(target, (list, tuple)) and target:
        numeric_vals = [v for v in target if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if len(numeric_vals) == len(target):
            return Record({
                "count": len(target),
                "mean": sum(numeric_vals) / len(numeric_vals),
                "min": min(numeric_vals),
                "max": max(numeric_vals),
            })
        return Record({"count": len(target), "distinct": len(set(target))})

    return Record({"type": type(target).__name__, "value": target})
