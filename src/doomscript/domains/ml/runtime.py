"""Runtime engine and model manager for the Machine Learning domain."""

import math
import os
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.ml.spec import ModelSpec, EvaluationReport
from doomscript.domains.ml.fallback import (
    NativeLinearRegression,
    NativeLogisticRegression,
    NativeDecisionTree,
    NativeRandomForest,
    NativeKMeans,
    train_test_split,
    accuracy_score,
    mean_squared_error,
    r2_score,
)
from doomscript.domains.data.runtime import _to_record_list


class ModelContainer:
    """Encapsulates a defined/trained ML model, its spec, data splits, and status."""

    def __init__(self, spec: ModelSpec):
        self.spec = spec
        self.name = spec.name
        self.algorithm = spec.algorithm.lower()
        self.model: Any = None
        self.is_trained: bool = False
        self.X_train: List[List[float]] = []
        self.X_test: List[List[float]] = []
        self.y_train: List[Any] = []
        self.y_test: List[Any] = []
        self.last_evaluation: Optional[Dict[str, Any]] = None

    def __repr__(self) -> str:
        status = "trained" if self.is_trained else "defined"
        return f"<Model {self.name} ({self.algorithm}, status={status})>"


class MLModelRuntime(DomainRuntime):
    """Coordinates ML model lifecycles: definition, training, evaluation, inference."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> ModelContainer:
        if not isinstance(ir, ModelSpec):
            raise TypeError(f"MLModelRuntime expects ModelSpec, got {type(ir).__name__}")
        container = ModelContainer(ir)
        scope[ir.name] = container
        return container


def _extract_dataset_matrices(
    data: Any, features: List[str], target: Optional[str] = None
) -> Tuple[List[List[float]], List[Any]]:
    """Extracts numeric feature matrix X and target vector y from dataset rows."""
    rows = _to_record_list(data)
    X: List[List[float]] = []
    y: List[Any] = []

    for r in rows:
        row_features = []
        for f in features:
            val = r.get(f, 0.0)
            try:
                row_features.append(float(val) if val is not None else 0.0)
            except (ValueError, TypeError):
                row_features.append(0.0)
        X.append(row_features)

        if target:
            y.append(r.get(target))
    return X, y


def _resolve_model(model_or_name: Any, scope: Optional[Dict[str, Any]] = None) -> ModelContainer:
    """Finds the ModelContainer from direct reference or variable name in scope."""
    if isinstance(model_or_name, ModelContainer):
        return model_or_name
    if isinstance(model_or_name, str) and scope and model_or_name in scope:
        val = scope[model_or_name]
        if isinstance(val, ModelContainer):
            return val
    raise ValueError(f"Unknown or invalid ML model: {model_or_name}")


def train_model(model_or_name: Any, scope: Optional[Dict[str, Any]] = None) -> ModelContainer:
    """Level 2: Trains the model on its specified dataset."""
    if scope is None:
        import sys
        caller_frame = sys._getframe(1)
        scope = dict(caller_frame.f_globals)
        scope.update(caller_frame.f_locals)
    container = _resolve_model(model_or_name, scope)
    spec = container.spec

    # 1. Resolve dataset
    dataset_name = spec.dataset
    dataset = scope.get(dataset_name) if scope else None
    if dataset is None:
        raise ValueError(f"Dataset '{dataset_name}' not found in scope for training model '{spec.name}'")

    X, y = _extract_dataset_matrices(dataset, spec.features, spec.target)
    if not X:
        raise ValueError(f"Dataset '{dataset_name}' contains no rows to train on")

    # 2. Split dataset
    if spec.split_train < 1.0 and len(X) >= 4:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, train_ratio=spec.split_train, seed=42
        )
    else:
        X_train, X_test, y_train, y_test = X, X, y, y

    container.X_train = X_train
    container.X_test = X_test
    container.y_train = y_train
    container.y_test = y_test

    # 3. Instantiate and fit algorithm
    algo = spec.algorithm.lower()
    if algo in ("linear_regression", "ols"):
        model = NativeLinearRegression()
        model.fit(X_train, [float(v) for v in y_train])
    elif algo in ("logistic_regression", "classification"):
        model = NativeLogisticRegression()
        model.fit(X_train, y_train)
    elif algo in ("decision_tree", "tree"):
        model = NativeDecisionTree()
        model.fit(X_train, y_train)
    elif algo in ("random_forest", "forest"):
        model = NativeRandomForest()
        model.fit(X_train, y_train)
    elif algo in ("k_means", "kmeans", "clustering"):
        k = spec.hyperparameters.get("k", 3)
        model = NativeKMeans(k=k)
        model.fit(X_train)
    else:
        # Default to NativeRandomForest for general robustness
        model = NativeRandomForest()
        model.fit(X_train, y_train)

    container.model = model
    container.is_trained = True
    return container


def evaluate_model(model_or_name: Any, scope: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Level 2: Evaluates a trained model against its test split and computes metrics."""
    if scope is None:
        import sys
        caller_frame = sys._getframe(1)
        scope = dict(caller_frame.f_globals)
        scope.update(caller_frame.f_locals)
    container = _resolve_model(model_or_name, scope)
    if not container.is_trained or container.model is None:
        # Auto-train if not yet trained
        train_model(container, scope)

    X_eval = container.X_test or container.X_train
    y_eval = container.y_test or container.y_train

    preds = container.model.predict(X_eval)
    algo = container.algorithm

    metrics = {}
    if algo in ("linear_regression", "ols"):
        task_type = "regression"
        y_float = [float(v) for v in y_eval]
        preds_float = [float(p) for p in preds]
        mse = mean_squared_error(y_float, preds_float)
        metrics["mse"] = round(mse, 4)
        metrics["rmse"] = round(math.sqrt(mse), 4)
        metrics["r2"] = round(r2_score(y_float, preds_float), 4)
    elif algo in ("k_means", "kmeans", "clustering"):
        task_type = "clustering"
        metrics["clusters"] = len(set(preds))
        metrics["cluster_counts"] = {c: preds.count(c) for c in set(preds)}
    else:
        task_type = "classification"
        acc = accuracy_score(y_eval, preds)
        metrics["accuracy"] = round(acc, 4)
        correct_count = sum(1 for yt, yp in zip(y_eval, preds) if yt == yp)
        metrics["correct"] = correct_count
        metrics["total"] = len(y_eval)

    report = {
        "model": container.name,
        "algorithm": container.algorithm,
        "task_type": task_type,
        "test_samples": len(X_eval),
        "metrics": metrics,
    }
    container.last_evaluation = report
    return report


def predict_model(
    model_or_name: Any, features_data: Any, scope: Optional[Dict[str, Any]] = None
) -> List[Any]:
    """Level 2: Generates predictions on new feature samples."""
    if scope is None:
        import sys
        caller_frame = sys._getframe(1)
        scope = dict(caller_frame.f_globals)
        scope.update(caller_frame.f_locals)
    container = _resolve_model(model_or_name, scope)
    if not container.is_trained or container.model is None:
        train_model(container, scope)

    # Check if features_data is a variable name in scope
    if isinstance(features_data, str) and scope and features_data in scope:
        features_data = scope[features_data]

    # Convert features to matrix
    if isinstance(features_data, list):
        if features_data and isinstance(features_data[0], list):
            X = features_data
        else:
            X, _ = _extract_dataset_matrices(features_data, container.spec.features)
    elif isinstance(features_data, dict):
        X, _ = _extract_dataset_matrices([features_data], container.spec.features)
    else:
        X = []

    return container.model.predict(X)


def inspect_model(model_or_name: Any, scope: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Level 1: Summarizes model architecture, hyperparameters, features, and status."""
    if scope is None:
        import sys
        caller_frame = sys._getframe(1)
        scope = dict(caller_frame.f_globals)
        scope.update(caller_frame.f_locals)
    container = _resolve_model(model_or_name, scope)
    spec = container.spec
    return {
        "name": container.name,
        "algorithm": container.algorithm,
        "dataset": spec.dataset,
        "target": spec.target,
        "features": list(spec.features),
        "is_trained": container.is_trained,
        "train_samples": len(container.X_train),
        "test_samples": len(container.X_test),
        "last_evaluation": container.last_evaluation,
    }
