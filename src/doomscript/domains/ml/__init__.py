"""Machine Learning Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.ml.spec import ModelSpec, EvaluationReport
from doomscript.domains.ml.parser import MLDomainParser
from doomscript.domains.ml.runtime import (
    MLModelRuntime,
    ModelContainer,
    train_model,
    evaluate_model,
    predict_model,
    inspect_model,
)
from doomscript.domains.ml.exporter import MLASTExporter
from doomscript.domains.registry import get_domain_registry


class MLDomain(DomainContract):
    """Machine Learning domain pack providing model definition, training, evaluation, and inference."""

    name = "ml"
    aliases = ["machine_learning", "models"]
    parser = MLDomainParser()
    runtime = MLModelRuntime()
    exporter = MLASTExporter()

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("train ")
            or s.startswith("evaluate ")
            or s.startswith("predict with ")
            or s.startswith("inspect model ")
            or s.startswith("summary of model ")
        )

    def can_handle_block(self, header: str) -> bool:
        s = header.strip().lower()
        return s.startswith("model ") and " from " in s


# Register with central registry
ML_DOMAIN = MLDomain()
get_domain_registry().register(ML_DOMAIN)

__all__ = [
    "MLDomain",
    "ML_DOMAIN",
    "ModelSpec",
    "EvaluationReport",
    "ModelContainer",
    "MLDomainParser",
    "MLModelRuntime",
    "MLASTExporter",
    "train_model",
    "evaluate_model",
    "predict_model",
    "inspect_model",
]
