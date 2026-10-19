"""Machine Learning Domain Specification and Intermediate Representation (IR)."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from doomscript.domains.base import DomainIR


@dataclass
class ModelSpec(DomainIR):
    """Specification for a Machine Learning model definition."""

    name: str
    dataset: str
    target: Optional[str] = None
    features: List[str] = field(default_factory=list)
    algorithm: str = "random_forest"
    split_train: float = 0.8
    split_test: float = 0.2
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    target_var: Optional[str] = None

    def validate(self) -> List[str]:
        errors = []
        if not self.name:
            errors.append("Model name cannot be empty")
        if not self.dataset:
            errors.append("Dataset source cannot be empty")
        if not self.features and self.algorithm != "k_means":
            errors.append("Model requires at least one feature column")
        if self.split_train <= 0 or self.split_train > 1.0:
            errors.append(f"Train split must be between 0 and 1, got {self.split_train}")
        return errors


@dataclass
class EvaluationReport:
    """Metrics report produced by model evaluation."""

    model_name: str
    task_type: str  # "classification" or "regression" or "clustering"
    metrics: Dict[str, float] = field(default_factory=dict)
    sample_count: int = 0
    predictions_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "task_type": self.task_type,
            "metrics": dict(self.metrics),
            "sample_count": self.sample_count,
            "predictions_summary": dict(self.predictions_summary),
        }
