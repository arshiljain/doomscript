"""Data Engineering Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
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
from doomscript.domains.data.parser import DataDomainParser
from doomscript.domains.data.runtime import (
    DataPipelineRuntime,
    inspect_dataset,
    profile_dataset,
    clean_dataset,
    join_datasets,
)
from doomscript.domains.data.exporter import DataASTExporter
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.registry import get_domain_registry


class DataDomain(DomainContract):
    """Data Engineering domain pack providing ETL pipelines, cleaning, joins, and aggregations."""

    name = "data"
    aliases = ["etl", "pipeline"]
    description = "Data Engineering pipelines, cleaning, relational joins, and aggregations"
    parser = DataDomainParser()
    runtime = DataPipelineRuntime()
    exporter = DataASTExporter()
    capabilities = ["etl", "cleaning", "joins", "profiling", "sorting"]
    optional_dependencies = ["pandas", "pyarrow"]

    verbs = [
        VerbSpec(
            name="read_file",
            pattern="read (csv|json|text) file {path:expr} into {target:ident}",
            arg_schema={"path": "expr", "target": "ident"},
            returns="Table",
            description="Read tabular CSV, JSON, or text data file into Table",
        ),
        VerbSpec(
            name="write_file",
            pattern="write (csv|json) {source:ident} into [file] {path:expr}",
            arg_schema={"source": "ident", "path": "expr"},
            returns="None",
            description="Serialize and write Table/records to file",
        ),
        VerbSpec(
            name="filter",
            pattern="{source:ident} where {condition:expr} into {target:ident}",
            arg_schema={"source": "ident", "condition": "expr", "target": "ident"},
            returns="Table",
            description="Filter table or record list rows matching condition expression",
        ),
        VerbSpec(
            name="sort",
            pattern="sort {source:ident} by {field:ident} [(descending|ascending)]",
            arg_schema={"source": "ident", "field": "ident"},
            returns="Table",
            description="Sort table or record list by column",
        ),
        VerbSpec(
            name="inspect_dataset",
            pattern="inspect dataset {source:ident} [into {target:ident}]",
            arg_schema={"source": "ident", "target": "ident"},
            returns="Record",
            description="Inspect schema, shape, and null counts of a dataset",
        ),
        VerbSpec(
            name="profile_dataset",
            pattern="profile dataset {source:ident} [into {target:ident}]",
            arg_schema={"source": "ident", "target": "ident"},
            returns="Record",
            description="Compute summary statistics and data quality metrics",
        ),
        VerbSpec(
            name="remove_duplicates",
            pattern="remove duplicates from {source:ident} [by {field:ident}] into {target:ident}",
            arg_schema={"source": "ident", "field": "ident", "target": "ident"},
            returns="Table",
            description="Deduplicate rows by primary key or all fields",
        ),
        VerbSpec(
            name="remove_nulls",
            pattern="remove nulls from {source:ident} [in {field:ident}] into {target:ident}",
            arg_schema={"source": "ident", "field": "ident", "target": "ident"},
            returns="Table",
            description="Drop rows containing null or missing values",
        ),
        VerbSpec(
            name="group_by",
            pattern="group {source:ident} by {group_col:ident} calculating {agg_fn:ident} of {val_col:ident} into {target:ident}",
            arg_schema={"source": "ident", "group_col": "ident", "agg_fn": "ident", "val_col": "ident", "target": "ident"},
            returns="Table",
            description="Group dataset by key column and aggregate metric",
        ),
        VerbSpec(
            name="join",
            pattern="join {left:ident} and {right:ident} on {key:ident} as (inner|left|right|outer) into {target:ident}",
            arg_schema={"left": "ident", "right": "ident", "key": "ident", "target": "ident"},
            returns="Table",
            description="Relational join between two datasets",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("inspect dataset")
            or s.startswith("profile dataset")
            or s.startswith("profile ")
            or (s.startswith("clean ") and " by removing " in s)
            or s.startswith("remove duplicates from ")
            or s.startswith("remove nulls from ")
            or (s.startswith("group ") and " calculating " in s)
            or (s.startswith("join ") and (" on " in s and " as " in s))
            or s.startswith("explain pipeline ")
            or s.startswith("pipeline explain ")
            or s.startswith("pipeline dry-run ")
            or s.startswith("pivot table ")
            or s.startswith("melt table ")
            or s.startswith("fill missing values in ")
            or s.startswith("drop duplicate rows in ")
            or (s.startswith("sample ") and " rows from " in s and " stratified by " in s)
            or s.startswith("rolling mean in ")
            or s.startswith("explode column ")
            or s.startswith("merge tables ")
            or s.startswith("rank column ")
            or s.startswith("lag column ")
            or s.startswith("lead column ")
            or s.startswith("cumulative sum of column ")
            or s.startswith("cumulative max of column ")
            or s.startswith("cumulative maximum of column ")
            or s.startswith("cumulative min of column ")
            or s.startswith("cumulative minimum of column ")
            or s.startswith("coalesce columns ")
            or s.startswith("sort table ")
            or s.startswith("cross join ")
            or s.startswith("validate schema of ")
            or s.startswith("rename columns in ")
            or s.startswith("clip column ")
            or s.startswith("format date column ")
            or s.startswith("trim whitespace in column ")
            or s.startswith("uppercase text in column ")
            or s.startswith("lowercase text in column ")
            or s.startswith("forward fill nulls in column ")
            or s.startswith("backward fill nulls in column ")
            or s.startswith("extract year from column ")
            or (s.startswith("sample ") and " fraction from " in s)
        )

    def can_handle_block(self, header: str) -> bool:
        s = header.strip().lower()
        return s.startswith("pipeline ")


# Register with central registry
DATA_DOMAIN = DataDomain()
get_domain_registry().register(DATA_DOMAIN)

__all__ = [
    "DataDomain",
    "DATA_DOMAIN",
    "PipelineSpec",
    "ValidationRule",
    "DedupeStep",
    "FilterStep",
    "FillNaStep",
    "DeriveStep",
    "JoinStep",
    "GroupByStep",
    "SortStep",
    "SinkStep",
    "DataDomainParser",
    "DataPipelineRuntime",
    "DataASTExporter",
    "inspect_dataset",
    "profile_dataset",
    "clean_dataset",
    "join_datasets",
]
