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
    MLPClassifier,
    MLPRegressor,
    CARTDecisionTree,
    GBDTModel,
    IsolationForestModel,
    ml_train_mlp,
    ml_train_cart,
    ml_train_gbdt,
    ml_train_isolation_forest,
)
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.ml.exporter import MLASTExporter
from doomscript.domains.registry import get_domain_registry


class MLDomain(DomainContract):
    """Machine Learning domain pack providing model definition, training, evaluation, and inference."""

    name = "ml"
    aliases = ["machine_learning", "models"]
    description = "Machine Learning classification, regression, evaluation, and cross-validation"
    parser = MLDomainParser()
    runtime = MLModelRuntime()
    exporter = MLASTExporter()
    capabilities = ["training", "evaluation", "inference", "cross_validation", "persistence"]
    optional_dependencies = ["scikit-learn", "numpy"]

    verbs = [
        VerbSpec(
            name="train_model",
            pattern="train [model] {m_var:ident} on {dataset:ident} into {target:ident}",
            arg_schema={"m_var": "ident", "dataset": "ident", "target": "ident"},
            returns="Model",
            description="Train ML model weights on supervised tabular dataset",
        ),
        VerbSpec(
            name="evaluate_model",
            pattern="evaluate [model] {m_var:ident} on {dataset:ident} into {target:ident}",
            arg_schema={"m_var": "ident", "dataset": "ident", "target": "ident"},
            returns="Record",
            description="Evaluate model accuracy, precision, recall, and loss",
        ),
        VerbSpec(
            name="predict_model",
            pattern="predict with [model] {m_var:ident} on {features:expr} into {target:ident}",
            arg_schema={"m_var": "ident", "features": "expr", "target": "ident"},
            returns="Collection",
            description="Generate predictions for unseen input features",
        ),
        VerbSpec(
            name="inspect_model",
            pattern="inspect model {m_var:ident} [into {target:ident}]",
            arg_schema={"m_var": "ident", "target": "ident"},
            returns="Record",
            description="Inspect model architecture, hyper-parameters, and learned coefficients",
        ),
        VerbSpec(
            name="cross_validate",
            pattern="cross validate [model] {m_var:ident} on {dataset:ident} [with {folds:int} folds] into {target:ident}",
            arg_schema={"m_var": "ident", "dataset": "ident", "folds": "int", "target": "ident"},
            defaults={"folds": 5},
            returns="Record",
            description="Perform K-fold cross validation",
        ),
        VerbSpec(
            name="save_model",
            pattern="save model {m_var:ident} to {path:expr}",
            arg_schema={"m_var": "ident", "path": "expr"},
            returns="str",
            description="Serialize trained model weights to disk",
        ),
        VerbSpec(
            name="load_model",
            pattern="load model from {path:expr} into {target:ident}",
            arg_schema={"path": "expr", "target": "ident"},
            returns="Model",
            description="Load serialized model from disk",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("train ")
            or s.startswith("evaluate ")
            or s.startswith("predict ")
            or s.startswith("predict with ")
            or s.startswith("accuracy of ")
            or s.startswith("score of ")
            or s.startswith("inspect model ")
            or s.startswith("summary of model ")
            or s.startswith("cross validate ")
            or s.startswith("save model ")
            or s.startswith("load model ")
            or s.startswith("split data ")
            or s.startswith("confusion matrix of ")
            or s.startswith("classification metrics for ")
            or s.startswith("roc auc score of ")
            or s.startswith("mean squared error between ")
            or s.startswith("r2 score between ")
            or s.startswith("one-hot encode column ")
            or s.startswith("train knn classifier on ")
            or s.startswith("fit decision stump on ")
            or s.startswith("train gaussian naive bayes on ")
            or s.startswith("train bernoulli naive bayes on ")
            or s.startswith("cluster ")
            or s.startswith("reduce dimensionality of ")
            or s.startswith("compute log loss between ")
            or s.startswith("compute brier score between ")
            or s.startswith("compute f1 score between ")
            or s.startswith("compute precision and recall between ")
            or s.startswith("generate polynomial features for ")
            or s.startswith("target encode column ")
            or s.startswith("cosine decay learning rate from ")
            or (s.startswith("split ") and " into train val test" in s)
            or s.startswith("compute anomaly scores in ")
            or s.startswith("compute silhouette score for ")
            or s.startswith("compute hinge loss between ")
            or s.startswith("compute learning curve points for ")
            or s.startswith("exponential moving average of weights ")
            or s.startswith("clip gradients ")
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
    "cross_validate_model",
    "save_model",
    "load_model",
    "MLPClassifier",
    "MLPRegressor",
    "CARTDecisionTree",
    "GBDTModel",
    "IsolationForestModel",
    "ml_train_mlp",
    "ml_train_cart",
    "ml_train_gbdt",
    "ml_train_isolation_forest",
]

