"""Intermediate Representation (IR) specifications for Data Engineering domain."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainIR


@dataclass
class ValidationRule:
    """A semantic validation constraint on input data."""
    rule_type: str  # "type", "positive", "not_null", "forbid_nulls"
    column: str
    expected: Optional[Any] = None


@dataclass
class PipelineStep:
    """Base class for sequential pipeline operations."""
    pass


@dataclass
class DedupeStep(PipelineStep):
    """Removes duplicate rows, optionally restricted to specified key columns."""
    by_columns: List[str] = field(default_factory=list)


@dataclass
class FilterStep(PipelineStep):
    """Filters dataset rows matching a boolean expression."""
    condition: str


@dataclass
class FillNaStep(PipelineStep):
    """Fills null/missing values in a column with a default constant value."""
    column: str
    value: Any


@dataclass
class DeriveStep(PipelineStep):
    """Derives a calculated column from an arithmetic expression."""
    target_col: str
    expression: str


@dataclass
class JoinStep(PipelineStep):
    """Joins current dataset with another dataset."""
    other_dataset: str
    on_key: str
    how: str = "inner"  # "inner", "left", "right", "outer"


@dataclass
class GroupByStep(PipelineStep):
    """Groups dataset by keys and computes aggregations."""
    keys: List[str] = field(default_factory=list)
    # Mapping of output_col -> (agg_function, source_col)
    aggregations: Dict[str, Tuple[str, str]] = field(default_factory=dict)


@dataclass
class SortStep(PipelineStep):
    """Sorts dataset rows by column."""
    column: str
    descending: bool = False


@dataclass
class SinkStep(PipelineStep):
    """Writes dataset to disk (CSV or JSON)."""
    path: str
    format: str = "csv"


@dataclass
class PipelineSpec(DomainIR):
    """Top-level typed specification for a Data Engineering ETL pipeline."""
    name: str
    source: str
    target: str = "pipeline_output"
    validations: List[ValidationRule] = field(default_factory=list)
    steps: List[PipelineStep] = field(default_factory=list)
    sink: Optional[SinkStep] = None

    def validate(self) -> List[str]:
        errors: List[str] = []
        if not self.name:
            errors.append("Pipeline must have a non-empty name.")
        if not self.source:
            errors.append("Pipeline must specify a data source.")
        for v in self.validations:
            if not v.column:
                errors.append(f"Validation rule '{v.rule_type}' requires a column name.")
        return errors
