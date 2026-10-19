"""Runtime engine and model manager for the Machine Learning domain."""

import math
import os
import pickle
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
        self.scalers: Dict[int, Tuple[float, float]] = {}
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
    seed = spec.seed if spec.seed is not None else 42
    if spec.split_train < 1.0 and len(X) >= 4:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, train_ratio=spec.split_train, seed=seed
        )
    else:
        X_train, X_test, y_train, y_test = [r[:] for r in X], [r[:] for r in X], list(y), list(y)

    # 2b. Preprocessing: scaling
    if spec.scale_features:
        for feat in spec.scale_features:
            if feat in spec.features:
                idx = spec.features.index(feat)
                vals = [r[idx] for r in X_train]
                if vals:
                    mean_val = sum(vals) / len(vals)
                    var_val = sum((v - mean_val) ** 2 for v in vals) / len(vals)
                    std_val = math.sqrt(var_val) if var_val > 1e-9 else 1.0
                    container.scalers[idx] = (mean_val, std_val)
                    for r in X_train:
                        r[idx] = (r[idx] - mean_val) / std_val
                    for r in X_test:
                        r[idx] = (r[idx] - mean_val) / std_val

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
        metrics["r2_score"] = metrics["r2"]
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
        **metrics,
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
            X = [r[:] for r in features_data]
        else:
            X, _ = _extract_dataset_matrices(features_data, container.spec.features)
    elif isinstance(features_data, dict):
        X, _ = _extract_dataset_matrices([features_data], container.spec.features)
    else:
        X = []

    # Apply scalers if present
    if container.scalers:
        for r in X:
            for idx, (mean_val, std_val) in container.scalers.items():
                if idx < len(r):
                    r[idx] = (r[idx] - mean_val) / std_val

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


def cross_validate_model(
    model_or_name: Any, folds: int = 5, scope: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Evaluates model performance across K stratified/sequential folds."""
    if scope is None:
        import sys
        caller_frame = sys._getframe(1)
        scope = dict(caller_frame.f_globals)
        scope.update(caller_frame.f_locals)
    container = _resolve_model(model_or_name, scope)
    spec = container.spec
    dataset = scope.get(spec.dataset)
    if dataset is None:
        raise ValueError(f"Dataset '{spec.dataset}' not found for cross-validation")

    X, y = _extract_dataset_matrices(dataset, spec.features, spec.target)
    n = len(X)
    if n < folds:
        folds = max(2, n)

    fold_size = max(1, n // folds)
    scores: List[float] = []

    algo = spec.algorithm.lower()
    is_regression = algo in ("linear_regression", "ols")

    for k in range(folds):
        val_start = k * fold_size
        val_end = (k + 1) * fold_size if k < folds - 1 else n
        X_val = [r[:] for r in X[val_start:val_end]]
        y_val = list(y[val_start:val_end])
        X_tr = [r[:] for r in X[:val_start] + X[val_end:]]
        y_tr = list(y[:val_start] + y[val_end:])

        if not X_val or not X_tr:
            continue

        # Apply scaling if configured
        if spec.scale_features:
            for feat in spec.scale_features:
                if feat in spec.features:
                    idx = spec.features.index(feat)
                    vals = [r[idx] for r in X_tr]
                    if vals:
                        mean_val = sum(vals) / len(vals)
                        var_val = sum((v - mean_val) ** 2 for v in vals) / len(vals)
                        std_val = math.sqrt(var_val) if var_val > 1e-9 else 1.0
                        for r in X_tr:
                            r[idx] = (r[idx] - mean_val) / std_val
                        for r in X_val:
                            r[idx] = (r[idx] - mean_val) / std_val

        if is_regression:
            m = NativeLinearRegression()
            m.fit(X_tr, [float(v) for v in y_tr])
            preds = m.predict(X_val)
            y_float = [float(v) for v in y_val]
            preds_float = [float(p) for p in preds]
            r2 = r2_score(y_float, preds_float)
            scores.append(r2)
        else:
            if algo in ("decision_tree", "tree"):
                m = NativeDecisionTree()
            elif algo in ("random_forest", "forest"):
                m = NativeRandomForest()
            else:
                m = NativeLogisticRegression()
            m.fit(X_tr, y_tr)
            preds = m.predict(X_val)
            acc = accuracy_score(y_val, preds)
            scores.append(acc)

    mean_s = sum(scores) / len(scores) if scores else 0.0
    var_s = sum((s - mean_s) ** 2 for s in scores) / len(scores) if len(scores) > 1 else 0.0
    std_s = math.sqrt(var_s)

    return {
        "model": container.name,
        "folds": folds,
        "scores": [round(s, 4) for s in scores],
        "mean_score": round(mean_s, 4),
        "std_score": round(std_s, 4),
    }


def save_model(model_or_name: Any, path: str, scope: Optional[Dict[str, Any]] = None) -> str:
    """Serializes a trained model container to disk."""
    if scope is None:
        import sys
        caller_frame = sys._getframe(1)
        scope = dict(caller_frame.f_globals)
        scope.update(caller_frame.f_locals)
    container = _resolve_model(model_or_name, scope)
    clean_path = str(path).strip().strip("'\"")
    parent_dir = os.path.dirname(os.path.abspath(clean_path))
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    with open(clean_path, "wb") as f:
        pickle.dump(container, f)
    return clean_path


def load_model(path: str) -> ModelContainer:
    """Deserializes a trained model container from disk."""
    clean_path = str(path).strip().strip("'\"")
    with open(clean_path, "rb") as f:
        container = pickle.load(f)
    if not isinstance(container, ModelContainer):
        raise TypeError(f"Loaded object is not a ModelContainer: {type(container)}")
    return container
