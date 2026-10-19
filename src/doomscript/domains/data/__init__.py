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
from doomscript.domains.registry import get_domain_registry


class DataDomain(DomainContract):
    """Data Engineering domain pack providing ETL pipelines, cleaning, joins, and aggregations."""

    name = "data"
    aliases = ["etl", "pipeline"]
    parser = DataDomainParser()
    runtime = DataPipelineRuntime()
    exporter = DataASTExporter()

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
