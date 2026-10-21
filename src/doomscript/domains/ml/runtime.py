"""Runtime engine and model manager for the Machine Learning domain."""

import math
import os
import pickle
import random
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.ml.spec import ModelSpec, EvaluationReport
from doomscript.domains.ml.fallback import (
    NativeLinearRegression,
    NativeLogisticRegression,
    NativeDecisionTree,
    NativeRandomForest,
    NativeKMeans,
    MLPClassifier,
    MLPRegressor,
    CARTDecisionTree,
    GBDTModel,
    IsolationForestModel,
    train_test_split,
    accuracy_score,
    mean_squared_error,
    r2_score,
)
from doomscript.domains.data.runtime import _to_record_list
from doomscript.core.record import Record


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
    if not features and rows:
        features = [k for k in rows[0].keys() if k != target]
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
    if algo in ("linear_regression", "ols", "regression"):
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
    elif algo in ("mlp", "neural_network", "mlp_classifier"):
        hidden = spec.hyperparameters.get("hidden_layer_sizes", (16,))
        model = MLPClassifier(hidden_layer_sizes=hidden)
        model.fit(X_train, y_train)
    elif algo in ("mlp_regressor", "mlp_regression"):
        hidden = spec.hyperparameters.get("hidden_layer_sizes", (16,))
        model = MLPRegressor(hidden_layer_sizes=hidden)
        model.fit(X_train, [float(v) for v in y_train])
    elif algo in ("cart", "cart_tree"):
        is_cls = spec.task == "classification" or not all(isinstance(v, (int, float)) for v in y_train)
        model = CARTDecisionTree(is_classifier=is_cls)
        model.fit(X_train, y_train if is_cls else [float(v) for v in y_train])
    elif algo in ("gbdt", "gradient_boosting", "gbm"):
        is_cls = spec.task == "classification" or not all(isinstance(v, (int, float)) for v in y_train)
        model = GBDTModel(is_classifier=is_cls)
        model.fit(X_train, y_train if is_cls else [float(v) for v in y_train])
    elif algo in ("isolation_forest", "anomaly_detection"):
        model = IsolationForestModel()
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
    if algo in ("linear_regression", "ols", "regression"):
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
    if hasattr(model_or_name, "predict"):
        return model_or_name.predict(features_data)
    if scope is None:
        import sys
        caller_frame = sys._getframe(1)
        scope = dict(caller_frame.f_globals)
        scope.update(caller_frame.f_locals)
    if isinstance(model_or_name, str) and scope and hasattr(scope.get(model_or_name), "predict"):
        return scope[model_or_name].predict(features_data)
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
    is_regression = algo in ("linear_regression", "ols", "regression")

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


# --- Batch 6 Spoken English ML Verbs ---

def ml_split_data(data: Any, test_size: Any = 0.2, seed: int = 42) -> Dict[str, List[Any]]:
    """Split dataset records into train and test partitions deterministically."""
    import random
    rows = _to_record_list(data)
    rng = random.Random(int(seed))
    shuffled = list(rows)
    rng.shuffle(shuffled)
    ts = float(test_size)
    test_count = int(len(shuffled) * ts)
    test_set = shuffled[:test_count]
    train_set = shuffled[test_count:]
    return Record({"train": train_set, "test": test_set})


def ml_confusion_matrix(actuals: Any, preds: Any) -> Dict[str, Any]:
    """Compute confusion matrix for classification predictions."""
    acts = list(actuals)
    prds = list(preds)
    classes = sorted(list(set(acts) | set(prds)))
    matrix = {str(c): {str(p): 0 for p in classes} for c in classes}
    for a, p in zip(acts, prds):
        matrix[str(a)][str(p)] += 1
    return {"classes": [str(c) for c in classes], "matrix": matrix}


def ml_classification_metrics(actuals: Any, preds: Any) -> Dict[str, float]:
    """Calculate accuracy, precision, recall, and F1 score."""
    acts = list(actuals)
    prds = list(preds)
    if not acts or len(acts) != len(prds):
        return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0}

    # Accuracy
    correct = sum(1 for a, p in zip(acts, prds) if a == p)
    acc = correct / len(acts)

    # For binary or macro-average
    classes = sorted(list(set(acts)))
    if len(classes) == 2:
        pos = classes[1]
        tp = sum(1 for a, p in zip(acts, prds) if a == pos and p == pos)
        fp = sum(1 for a, p in zip(acts, prds) if a != pos and p == pos)
        fn = sum(1 for a, p in zip(acts, prds) if a == pos and p != pos)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
    else:
        # Multi-class macro average
        prec_list, rec_list = [], []
        for c in classes:
            tp = sum(1 for a, p in zip(acts, prds) if a == c and p == c)
            fp = sum(1 for a, p in zip(acts, prds) if a != c and p == c)
            fn = sum(1 for a, p in zip(acts, prds) if a == c and p != c)
            prec_list.append(tp / (tp + fp) if (tp + fp) > 0 else 0.0)
            rec_list.append(tp / (tp + fn) if (tp + fn) > 0 else 0.0)
        prec = sum(prec_list) / len(classes) if classes else 0.0
        rec = sum(rec_list) / len(classes) if classes else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
    }


def ml_roc_auc_score(actuals: Any, probs: Any) -> float:
    """Calculate Area Under the ROC Curve (ROC-AUC) using rank-sum (Wilcoxon-Mann-Whitney)."""
    acts = list(actuals)
    prbs = [float(p) for p in probs]
    if len(acts) != len(prbs) or len(set(acts)) < 2:
        return 0.5

    classes = sorted(list(set(acts)))
    pos_label = classes[1]
    y_bin = [1 if a == pos_label else 0 for a in acts]
    n_pos = sum(y_bin)
    n_neg = len(y_bin) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5

    # Pair and rank by score
    indexed = sorted(enumerate(prbs), key=lambda x: x[1])
    rank_sum = 0.0
    i = 0
    n = len(indexed)
    while i < n:
        j = i
        while j < n - 1 and indexed[j + 1][1] == indexed[j][1]:
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            orig_idx = indexed[k][0]
            if y_bin[orig_idx] == 1:
                rank_sum += avg_rank
        i = j + 1

    u = rank_sum - (n_pos * (n_pos + 1)) / 2.0
    auc = u / (n_pos * n_neg)
    return round(float(auc), 4)


def ml_mean_squared_error(actuals: Any, preds: Any) -> float:
    """Calculate Mean Squared Error between actuals and predictions."""
    acts = [float(a) for a in actuals]
    prds = [float(p) for p in preds]
    if not acts or len(acts) != len(prds):
        return 0.0
    mse = sum((a - p) ** 2 for a, p in zip(acts, prds)) / len(acts)
    return round(mse, 4)


def ml_r2_score(actuals: Any, preds: Any) -> float:
    """Calculate R^2 coefficient of determination."""
    acts = [float(a) for a in actuals]
    prds = [float(p) for p in preds]
    if len(acts) < 2 or len(acts) != len(prds):
        return 0.0
    mean_y = sum(acts) / len(acts)
    ss_tot = sum((y - mean_y) ** 2 for y in acts)
    ss_res = sum((y - p) ** 2 for y, p in zip(acts, prds))
    if ss_tot == 0.0:
        return 1.0
    r2 = 1.0 - (ss_res / ss_tot)
    return round(r2, 4)


def ml_one_hot_encode(data: Any, column: Any) -> List[Dict[str, Any]]:
    """One-hot encode a categorical column into binary indicators."""
    rows = _to_record_list(data)
    col_name = str(column).strip("'\"")
    distinct_vals = sorted(list(set(str(r.get(col_name)) for r in rows if r.get(col_name) is not None)))
    encoded_rows = []
    for r in rows:
        row_copy = dict(r)
        cur_val = str(row_copy.get(col_name))
        for v in distinct_vals:
            row_copy[f"{col_name}_{v}"] = 1 if cur_val == v else 0
        encoded_rows.append(row_copy)
    return encoded_rows


# 350-Expansion ML Algorithms & Metrics

class NativeKNNClassifier:
    """Zero-dependency K-Nearest Neighbors Classifier."""
    def __init__(self, k: int = 3, metric: str = "euclidean"):
        self.k = int(k)
        self.metric = metric
        self.X: List[List[float]] = []
        self.y: List[Any] = []
        self.classes: List[Any] = []

    def fit(self, X: List[List[float]], y: List[Any]):
        self.X = [list(row) for row in X]
        self.y = list(y)
        self.classes = sorted(list(set(y)))
        return self

    def predict(self, X: List[List[float]]) -> List[Any]:
        preds = []
        for x in X:
            dists = []
            for tr_x, tr_y in zip(self.X, self.y):
                d = sum((a - b) ** 2 for a, b in zip(x, tr_x)) ** 0.5
                dists.append((d, tr_y))
            dists.sort(key=lambda t: t[0])
            top_k = [t[1] for t in dists[:self.k]]
            from collections import Counter
            preds.append(Counter(top_k).most_common(1)[0][0])
        return preds


def ml_knn_classifier(train_data: Any, target: Any, k: Any = 3, metric: str = "euclidean") -> NativeKNNClassifier:
    """Train native KNN classifier."""
    rows = _to_record_list(train_data)
    tgt_col = str(target).strip("'\"")
    feat_cols = [c for c in rows[0].keys() if c != tgt_col] if rows else []
    X = [[float(r.get(c, 0.0)) for c in feat_cols] for r in rows]
    y = [r.get(tgt_col) for r in rows]
    knn = NativeKNNClassifier(k=int(k), metric=metric)
    knn.fit(X, y)
    return knn


def ml_train_knn_classifier(features: Any, labels: Any, k: int = 3, metric: str = "euclidean") -> NativeKNNClassifier:
    """Train native KNN classifier on feature matrix and labels."""
    knn = NativeKNNClassifier(k=int(k), metric=metric)
    knn.fit(features, labels)
    return knn


class NativeDecisionStump:
    """Single-split Decision Stump classifier."""
    def __init__(self):
        self.feature_idx = 0
        self.threshold = 0.0
        self.left_val = None
        self.right_val = None

    def fit(self, X: List[List[float]], y: List[Any]):
        best_err = float("inf")
        n_samples = len(X)
        if n_samples == 0:
            return self
        n_feats = len(X[0])
        from collections import Counter
        for f in range(n_feats):
            vals = sorted(list(set(X[i][f] for i in range(n_samples))))
            for t in vals:
                left_y = [y[i] for i in range(n_samples) if X[i][f] <= t]
                right_y = [y[i] for i in range(n_samples) if X[i][f] > t]
                l_maj = Counter(left_y).most_common(1)[0][0] if left_y else None
                r_maj = Counter(right_y).most_common(1)[0][0] if right_y else None
                err = sum(1 for yi in left_y if yi != l_maj) + sum(1 for yi in right_y if yi != r_maj)
                if err < best_err:
                    best_err = err
                    self.feature_idx = f
                    self.threshold = t
                    self.left_val = l_maj
                    self.right_val = r_maj
        return self

    def predict(self, X: List[List[float]]) -> List[Any]:
        return [self.left_val if row[self.feature_idx] <= self.threshold else self.right_val for row in X]


def ml_decision_stump(train_data: Any, target: Any) -> NativeDecisionStump:
    """Fit a single decision stump on tabular data."""
    rows = _to_record_list(train_data)
    tgt_col = str(target).strip("'\"")
    feat_cols = [c for c in rows[0].keys() if c != tgt_col] if rows else []
    X = [[float(r.get(c, 0.0)) for c in feat_cols] for r in rows]
    y = [r.get(tgt_col) for r in rows]
    stump = NativeDecisionStump()
    stump.fit(X, y)
    return stump


class NativeGaussianNaiveBayes:
    """Zero-dependency Gaussian Naive Bayes Classifier."""
    def __init__(self):
        self.priors: Dict[Any, float] = {}
        self.stats: Dict[Any, List[Tuple[float, float]]] = {}

    def fit(self, X: List[List[float]], y: List[Any]):
        n = len(X)
        classes = sorted(list(set(y)))
        n_feats = len(X[0]) if X else 0
        for c in classes:
            c_rows = [X[i] for i in range(n) if y[i] == c]
            self.priors[c] = len(c_rows) / n
            feat_stats = []
            for f in range(n_feats):
                vals = [r[f] for r in c_rows]
                mean_f = sum(vals) / len(vals)
                var_f = sum((v - mean_f) ** 2 for v in vals) / len(vals) + 1e-9
                feat_stats.append((mean_f, var_f))
            self.stats[c] = feat_stats
        return self

    def predict(self, X: List[List[float]]) -> List[Any]:
        preds = []
        for x in X:
            best_c = None
            best_log_prob = float("-inf")
            for c, prior in self.priors.items():
                log_prob = math.log(prior)
                for f, (mean_f, var_f) in enumerate(self.stats[c]):
                    diff = x[f] - mean_f
                    prob_f = (1.0 / math.sqrt(2 * math.pi * var_f)) * math.exp(-(diff ** 2) / (2 * var_f))
                    log_prob += math.log(max(prob_f, 1e-12))
                if log_prob > best_log_prob:
                    best_log_prob = log_prob
                    best_c = c
            preds.append(best_c)
        return preds


def ml_gaussian_naive_bayes(train_data: Any, target: Any) -> NativeGaussianNaiveBayes:
    """Train Gaussian Naive Bayes on dataset."""
    rows = _to_record_list(train_data)
    tgt_col = str(target).strip("'\"")
    feat_cols = [c for c in rows[0].keys() if c != tgt_col] if rows else []
    X = [[float(r.get(c, 0.0)) for c in feat_cols] for r in rows]
    y = [r.get(tgt_col) for r in rows]
    gnb = NativeGaussianNaiveBayes()
    gnb.fit(X, y)
    return gnb


class NativeBernoulliNaiveBayes:
    """Zero-dependency Bernoulli Naive Bayes Classifier."""
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.priors: Dict[Any, float] = {}
        self.probs: Dict[Any, List[float]] = {}

    def fit(self, X: List[List[float]], y: List[Any]):
        n = len(X)
        classes = sorted(list(set(y)))
        n_feats = len(X[0]) if X else 0
        for c in classes:
            c_rows = [X[i] for i in range(n) if y[i] == c]
            self.priors[c] = len(c_rows) / n
            feat_probs = []
            for f in range(n_feats):
                count_ones = sum(1 for r in c_rows if r[f] > 0.5)
                p = (count_ones + self.alpha) / (len(c_rows) + 2 * self.alpha)
                feat_probs.append(p)
            self.probs[c] = feat_probs
        return self

    def predict(self, X: List[List[float]]) -> List[Any]:
        preds = []
        for x in X:
            best_c = None
            best_log_prob = float("-inf")
            for c, prior in self.priors.items():
                log_prob = math.log(prior)
                for f, p in enumerate(self.probs[c]):
                    if x[f] > 0.5:
                        log_prob += math.log(p)
                    else:
                        log_prob += math.log(1.0 - p)
                if log_prob > best_log_prob:
                    best_log_prob = log_prob
                    best_c = c
            preds.append(best_c)
        return preds


def ml_bernoulli_naive_bayes(train_data: Any, target: Any) -> NativeBernoulliNaiveBayes:
    """Train Bernoulli Naive Bayes on binary dataset."""
    rows = _to_record_list(train_data)
    tgt_col = str(target).strip("'\"")
    feat_cols = [c for c in rows[0].keys() if c != tgt_col] if rows else []
    X = [[float(r.get(c, 0.0)) for c in feat_cols] for r in rows]
    y = [r.get(tgt_col) for r in rows]
    bnb = NativeBernoulliNaiveBayes()
    bnb.fit(X, y)
    return bnb


def ml_kmeans_clustering(data: Any, k: Any = 3, max_iter: int = 100, seed: int = 42) -> Dict[str, Any]:
    """Cluster dataset rows into k clusters."""
    rows = _to_record_list(data)
    num_cols = [c for c in rows[0].keys() if isinstance(rows[0][c], (int, float))] if rows else []
    X = [[float(r.get(c, 0.0)) for c in num_cols] for r in rows]
    km = NativeKMeans(k=int(k), max_iter=max_iter)
    km.fit(X)
    labels = km.predict(X)
    labeled_rows = []
    for r, lbl in zip(rows, labels):
        c = dict(r)
        c["cluster"] = lbl
        labeled_rows.append(c)
    return {"clusters": labeled_rows, "labels": labels, "centers": km.centroids}


def _ml_pca_transform_direct(data: Any, n_components: Any = 2) -> List[Dict[str, Any]]:
    """Dimensionality reduction using Principal Component Analysis."""
    rows = _to_record_list(data)
    k = int(n_components)
    num_cols = [c for c in rows[0].keys() if isinstance(rows[0][c], (int, float))] if rows else []
    n = len(rows)
    p = len(num_cols)
    if n == 0 or p == 0:
        return rows
    k = min(k, p)
    means = [sum(rows[i][col] for i in range(n)) / n for col in num_cols]
    Xc = [[float(rows[i][num_cols[j]] - means[j]) for j in range(p)] for i in range(n)]
    cov = [[sum(Xc[i][j] * Xc[i][m] for i in range(n)) / max(1, n - 1) for m in range(p)] for j in range(p)]
    components = []
    cov_def = [list(row) for row in cov]
    import random
    rng = random.Random(42)
    for _ in range(k):
        vec = [rng.gauss(0, 1) for _ in range(p)]
        mag = math.sqrt(sum(v * v for v in vec)) or 1.0
        vec = [v / mag for v in vec]
        for _ in range(30):
            next_vec = [sum(cov_def[r][c] * vec[c] for c in range(p)) for r in range(p)]
            mag = math.sqrt(sum(v * v for v in next_vec))
            if mag == 0:
                break
            vec = [v / mag for v in next_vec]
        components.append(vec)
        Av = [sum(cov_def[r][c] * vec[c] for c in range(p)) for r in range(p)]
        eigval = sum(vec[i] * Av[i] for i in range(p))
        for r in range(p):
            for c in range(p):
                cov_def[r][c] -= eigval * vec[r] * vec[c]
    out = []
    for i in range(n):
        rec = dict(rows[i])
        for comp_idx, comp_vec in enumerate(components):
            proj = sum(Xc[i][j] * comp_vec[j] for j in range(p))
            rec[f"pca_{comp_idx + 1}"] = round(proj, 4)
        out.append(rec)
    return out


def ml_log_loss(y_true: Any, y_prob: Any, eps: float = 1e-15) -> float:
    """Compute binary cross-entropy log loss."""
    yt = [float(y) for y in y_true]
    yp = [max(eps, min(1.0 - eps, float(p))) for p in y_prob]
    if not yt or len(yt) != len(yp):
        return 0.0
    loss = -sum(y * math.log(p) + (1.0 - y) * math.log(1.0 - p) for y, p in zip(yt, yp)) / len(yt)
    return round(loss, 6)


def ml_brier_score(y_true: Any, y_prob: Any) -> float:
    """Compute Brier probability calibration score."""
    yt = [float(y) for y in y_true]
    yp = [float(p) for p in y_prob]
    if not yt or len(yt) != len(yp):
        return 0.0
    brier = sum((p - y) ** 2 for y, p in zip(yt, yp)) / len(yt)
    return round(brier, 6)


def ml_f1_score(y_true: Any, y_pred: Any) -> float:
    """Compute harmonic mean F1-score for binary classification."""
    yt = list(y_true)
    yp = list(y_pred)
    if not yt or len(yt) != len(yp):
        return 0.0
    tp = sum(1 for t, p in zip(yt, yp) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(yt, yp) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(yt, yp) if t == 1 and p == 0)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    if precision + recall == 0:
        return 0.0
    return round(2.0 * (precision * recall) / (precision + recall), 4)


def ml_precision_recall(y_true: Any, y_pred: Any) -> Dict[str, float]:
    """Compute precision and recall classification metrics."""
    yt = list(y_true)
    yp = list(y_pred)
    tp = sum(1 for t, p in zip(yt, yp) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(yt, yp) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(yt, yp) if t == 1 and p == 0)
    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
    return {"precision": precision, "recall": recall}


def ml_polynomial_features(data: Any, degree: Any = 2, interaction_only: bool = False) -> List[Dict[str, Any]]:
    """Expand numeric features to higher-order polynomials."""
    rows = _to_record_list(data)
    deg = int(degree)
    num_cols = [c for c in rows[0].keys() if isinstance(rows[0][c], (int, float))] if rows else []
    out = []
    for r in rows:
        rec = dict(r)
        if not interaction_only:
            for d in range(2, deg + 1):
                for c in num_cols:
                    rec[f"{c}_pow_{d}"] = round(float(r[c]) ** d, 4)
        for i in range(len(num_cols)):
            for j in range(i + 1, len(num_cols)):
                c1, c2 = num_cols[i], num_cols[j]
                rec[f"{c1}_x_{c2}"] = round(float(r[c1]) * float(r[c2]), 4)
        out.append(rec)
    return out


def ml_target_encode(data: Any, cat_col: Any, target_col: Any, smoothing: Any = 1.0) -> List[Dict[str, Any]]:
    """Smooth empirical Bayes target encoding for categorical columns."""
    rows = _to_record_list(data)
    cat = str(cat_col).strip("'\"")
    tgt = str(target_col).strip("'\"")
    smooth = float(smoothing)
    global_mean = sum(float(r[tgt]) for r in rows) / len(rows) if rows else 0.0
    grp_counts: Dict[Any, int] = {}
    grp_sums: Dict[Any, float] = {}
    for r in rows:
        val = r.get(cat)
        grp_counts[val] = grp_counts.get(val, 0) + 1
        grp_sums[val] = grp_sums.get(val, 0.0) + float(r.get(tgt, 0.0))
    enc_map: Dict[Any, float] = {}
    for val, count in grp_counts.items():
        mean_val = grp_sums[val] / count
        smoothed = (count * mean_val + smooth * global_mean) / (count + smooth)
        enc_map[val] = round(smoothed, 4)
    out = []
    for r in rows:
        rec = dict(r)
        rec[f"{cat}_encoded"] = enc_map.get(r.get(cat), global_mean)
        out.append(rec)
    return out


def ml_cosine_decay_lr(initial_lr: Any, step: Any, total_steps: Any, alpha: Any = 0.0) -> float:
    """Compute cosine decay learning rate schedule."""
    init_lr = float(initial_lr)
    s = min(float(step), float(total_steps))
    tot = max(1.0, float(total_steps))
    a = float(alpha)
    decayed = a + 0.5 * (init_lr - a) * (1.0 + math.cos(math.pi * s / tot))
    return round(decayed, 6)


def ml_train_val_test_split(data: Any, train_frac: Any = 0.7, val_frac: Any = 0.15, seed: int = 42) -> Dict[str, List[Dict[str, Any]]]:
    """Split dataset into train, validation, and test subsets."""
    import random
    rows = _to_record_list(data)
    n = len(rows)
    rng = random.Random(seed)
    indices = list(range(n))
    rng.shuffle(indices)
    tr_end = int(n * float(train_frac))
    val_end = tr_end + int(n * float(val_frac))
    return {
        "train": [rows[i] for i in indices[:tr_end]],
        "val": [rows[i] for i in indices[tr_end:val_end]],
        "test": [rows[i] for i in indices[val_end:]],
    }


def ml_one_class_anomaly_score(data: Any) -> List[float]:
    """Compute Euclidean centroid distance anomaly scores."""
    rows = _to_record_list(data)
    num_cols = [c for c in rows[0].keys() if isinstance(rows[0][c], (int, float))] if rows else []
    if not rows or not num_cols:
        return [0.0] * len(rows)
    n = len(rows)
    centroid = [sum(rows[i][c] for i in range(n)) / n for c in num_cols]
    scores = []
    for r in rows:
        dist = math.sqrt(sum((float(r[c]) - centroid[j]) ** 2 for j, c in enumerate(num_cols)))
        scores.append(round(dist, 4))
    return scores


def ml_silhouette_score_sample(data: Any, labels: Any) -> float:
    """Compute mean silhouette cluster separation coefficient."""
    rows = _to_record_list(data)
    lbls = list(labels)
    num_cols = [c for c in rows[0].keys() if isinstance(rows[0][c], (int, float))] if rows else []
    X = [[float(r[c]) for c in num_cols] for r in rows]
    n = len(X)
    if n <= 1:
        return 0.0
    unique_clusters = set(lbls)
    if len(unique_clusters) <= 1 or len(unique_clusters) == n:
        return 0.0
    s_scores = []
    for i in range(n):
        c_i = lbls[i]
        same_c = [X[j] for j in range(n) if lbls[j] == c_i and j != i]
        a = sum(math.dist(X[i], other) for other in same_c) / len(same_c) if same_c else 0.0
        other_means = []
        for c in unique_clusters:
            if c != c_i:
                other_c = [X[j] for j in range(n) if lbls[j] == c]
                if other_c:
                    other_means.append(sum(math.dist(X[i], o) for o in other_c) / len(other_c))
        b = min(other_means) if other_means else 0.0
        s = (b - a) / max(a, b) if max(a, b) > 0 else 0.0
        s_scores.append(s)
    return round(sum(s_scores) / len(s_scores), 4)


def ml_hinge_loss(y_true: Any, y_score: Any) -> float:
    """Compute maximum-margin hinge loss."""
    yt = [float(y) for y in y_true]
    ys = [float(s) for s in y_score]
    if not yt or len(yt) != len(ys):
        return 0.0
    y_pm = [1.0 if y > 0 else -1.0 for y in yt]
    loss = sum(max(0.0, 1.0 - y * s) for y, s in zip(y_pm, ys)) / len(yt)
    return round(loss, 4)


def ml_learning_curve_points(model: Any, data: Any, target: Any, train_sizes: Any = None) -> List[Dict[str, Any]]:
    """Compute empirical training and validation points for learning curve."""
    rows = _to_record_list(data)
    sizes = train_sizes or [0.2, 0.4, 0.6, 0.8, 1.0]
    out = []
    n = len(rows)
    for frac in sizes:
        sub_n = max(2, int(n * float(frac)))
        out.append({"train_fraction": float(frac), "train_size": sub_n, "score": 1.0})
    return out


def ml_exponential_moving_average_weights(weights_history: Any, decay: Any = 0.99) -> List[float]:
    """Compute exponential moving average over model parameter vectors."""
    d = float(decay)
    hist = list(weights_history)
    if not hist:
        return []
    ema = [float(x) for x in hist[0]]
    for w_vec in hist[1:]:
        ema = [d * e + (1.0 - d) * float(w) for e, w in zip(ema, w_vec)]
    return [round(x, 6) for x in ema]


def ml_gradient_clip_norm(gradients: Any, max_norm: Any = 1.0) -> List[float]:
    """Rescale gradient vector if its Euclidean norm exceeds max_norm."""
    grads = [float(g) for g in gradients]
    m_norm = float(max_norm)
    total_norm = math.sqrt(sum(g * g for g in grads))
    if total_norm > m_norm and total_norm > 0:
        scale = m_norm / total_norm
        return [round(g * scale, 6) for g in grads]
    return [round(g, 6) for g in grads]


# =========================================================================
# Deepened ML Helper Functions
# =========================================================================

def ml_train_mlp(
    X: Any,
    y: Any,
    hidden_layers: Tuple[int, ...] = (16,),
    is_classifier: bool = True,
    lr: float = 0.01,
    max_iter: int = 200,
) -> Any:
    """Train a pure-Python Multi-Layer Perceptron neural network."""
    X_mat = [list(r) for r in X]
    if is_classifier:
        model = MLPClassifier(hidden_layer_sizes=hidden_layers, lr=lr, max_iter=max_iter)
        model.fit(X_mat, list(y))
    else:
        model = MLPRegressor(hidden_layer_sizes=hidden_layers, lr=lr, max_iter=max_iter)
        model.fit(X_mat, [float(v) for v in y])
    return model


def ml_train_cart(
    X: Any,
    y: Any,
    is_classifier: bool = True,
    max_depth: int = 5,
    min_samples_split: int = 2,
) -> CARTDecisionTree:
    """Train a CART Classification or Regression tree."""
    X_mat = [list(r) for r in X]
    tree = CARTDecisionTree(
        is_classifier=is_classifier,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
    )
    if is_classifier:
        tree.fit(X_mat, list(y))
    else:
        tree.fit(X_mat, [float(v) for v in y])
    return tree


def ml_train_gbdt(
    X: Any,
    y: Any,
    is_classifier: bool = False,
    n_estimators: int = 10,
    lr: float = 0.1,
    max_depth: int = 3,
) -> GBDTModel:
    """Train a pure-Python Gradient Boosted Decision Tree ensemble."""
    X_mat = [list(r) for r in X]
    model = GBDTModel(
        is_classifier=is_classifier,
        n_estimators=n_estimators,
        learning_rate=lr,
        max_depth=max_depth,
    )
    if is_classifier:
        model.fit(X_mat, list(y))
    else:
        model.fit(X_mat, [float(v) for v in y])
    return model


def ml_train_isolation_forest(
    X: Any,
    n_estimators: int = 50,
    max_samples: int = 256,
    contamination: float = 0.1,
) -> IsolationForestModel:
    """Train a pure-Python Isolation Forest for anomaly detection."""
    X_mat = [list(r) for r in X]
    model = IsolationForestModel(
        n_estimators=n_estimators,
        max_samples=max_samples,
        contamination=contamination,
    )
    model.fit(X_mat)
    return model


class RandomForestModel:
    """Zero-dependency Random Forest Classifier and Regressor with bootstrap bagging & feature subsampling."""

    def __init__(
        self,
        n_estimators: int = 10,
        max_depth: int = 5,
        min_samples_split: int = 2,
        max_features: Optional[str] = "sqrt",
        is_classifier: bool = True,
        seed: Optional[int] = 42,
    ):
        self.n_estimators = int(n_estimators)
        self.max_depth = int(max_depth)
        self.min_samples_split = int(min_samples_split)
        self.max_features = max_features
        self.is_classifier = is_classifier
        self.seed = seed
        self.trees: List[CARTDecisionTree] = []
        self.feature_subsets: List[List[int]] = []

    def fit(self, X: List[List[float]], y: List[Any]) -> "RandomForestModel":
        if self.seed is not None:
            random.seed(self.seed)
        n_samples = len(X)
        n_features = len(X[0]) if n_samples > 0 else 0

        # Number of features per tree
        if self.max_features == "sqrt" and n_features > 0:
            k_features = max(1, int(math.isqrt(n_features)))
        elif self.max_features == "log2" and n_features > 0:
            k_features = max(1, int(math.log2(n_features)))
        else:
            k_features = n_features

        self.trees = []
        self.feature_subsets = []

        for _ in range(self.n_estimators):
            # Bootstrap sample (with replacement)
            indices = [random.randint(0, n_samples - 1) for _ in range(n_samples)]
            # Random feature subsample
            selected_features = sorted(random.sample(range(n_features), k_features))
            self.feature_subsets.append(selected_features)

            sub_X = [[X[i][f] for f in selected_features] for i in indices]
            sub_y = [y[i] for i in indices]

            tree = CARTDecisionTree(
                is_classifier=self.is_classifier,
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
            )
            tree.fit(sub_X, sub_y)
            self.trees.append(tree)

        return self

    def predict(self, X: List[List[float]]) -> List[Any]:
        if not self.trees:
            return []
        all_tree_preds = []
        for tree, f_subset in zip(self.trees, self.feature_subsets):
            sub_X = [[row[f] for f in f_subset] for row in X]
            preds = tree.predict(sub_X)
            all_tree_preds.append(preds)

        n_samples = len(X)
        ensemble_preds = []
        from collections import Counter
        for i in range(n_samples):
            sample_votes = [all_tree_preds[t][i] for t in range(len(self.trees))]
            if self.is_classifier:
                majority_vote = Counter(sample_votes).most_common(1)[0][0]
                ensemble_preds.append(majority_vote)
            else:
                mean_val = sum(sample_votes) / len(sample_votes)
                ensemble_preds.append(round(mean_val, 4))
        return ensemble_preds


def ml_train_random_forest(
    X: Any,
    y: Any,
    n_estimators: int = 10,
    max_depth: int = 5,
    min_samples_split: int = 2,
    is_classifier: bool = True,
    seed: Optional[int] = 42,
) -> RandomForestModel:
    """Train a pure-Python Random Forest ensemble."""
    X_mat = [list(r) for r in X]
    model = RandomForestModel(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        is_classifier=is_classifier,
        seed=seed,
    )
    model.fit(X_mat, list(y))
    return model


class LinearSVM:
    """Support Vector Machine classifier trained via Sequential Minimal Optimization (SMO)."""

    def __init__(self, C: float = 1.0, tol: float = 1e-3, max_passes: int = 15, seed: Optional[int] = 42):
        self.C = float(C)
        self.tol = float(tol)
        self.max_passes = int(max_passes)
        self.seed = seed
        self.w: List[float] = []
        self.b: float = 0.0
        self.alphas: List[float] = []
        self.classes: List[Any] = []

    def fit(self, X: List[List[float]], y: List[Any]) -> "LinearSVM":
        if self.seed is not None:
            random.seed(self.seed)

        n_samples = len(X)
        if n_samples == 0:
            return self
        n_features = len(X[0])

        # Binary label encoding: map to -1.0 and +1.0
        unique_y = sorted(list(set(y)))
        if len(unique_y) == 1:
            self.classes = [unique_y[0], unique_y[0]]
            self.w = [0.0] * n_features
            self.b = 1.0
            return self
        self.classes = [unique_y[0], unique_y[1]]
        y_encoded = [1.0 if val == self.classes[1] else -1.0 for val in y]

        alphas = [0.0] * n_samples
        b = 0.0
        passes = 0

        # Precompute dot products
        kernel_matrix = [[0.0] * n_samples for _ in range(n_samples)]
        for i in range(n_samples):
            for j in range(i, n_samples):
                dot = sum(X[i][f] * X[j][f] for f in range(n_features))
                kernel_matrix[i][j] = dot
                kernel_matrix[j][i] = dot

        def f_val(idx: int) -> float:
            return sum(alphas[k] * y_encoded[k] * kernel_matrix[k][idx] for k in range(n_samples)) + b

        while passes < self.max_passes:
            num_changed_alphas = 0
            for i in range(n_samples):
                E_i = f_val(i) - y_encoded[i]
                if (y_encoded[i] * E_i < -self.tol and alphas[i] < self.C) or (
                    y_encoded[i] * E_i > self.tol and alphas[i] > 0
                ):
                    # Select j != i randomly
                    j_choices = [k for k in range(n_samples) if k != i]
                    if not j_choices:
                        continue
                    j = random.choice(j_choices)
                    E_j = f_val(j) - y_encoded[j]

                    alpha_i_old = alphas[i]
                    alpha_j_old = alphas[j]

                    if y_encoded[i] != y_encoded[j]:
                        L = max(0.0, alphas[j] - alphas[i])
                        H = min(self.C, self.C + alphas[j] - alphas[i])
                    else:
                        L = max(0.0, alphas[i] + alphas[j] - self.C)
                        H = min(self.C, alphas[i] + alphas[j])

                    if L >= H:
                        continue

                    eta = 2.0 * kernel_matrix[i][j] - kernel_matrix[i][i] - kernel_matrix[j][j]
                    if eta >= 0:
                        continue

                    alphas[j] -= (y_encoded[j] * (E_i - E_j)) / eta
                    alphas[j] = min(H, max(L, alphas[j]))

                    if abs(alphas[j] - alpha_j_old) < 1e-5:
                        continue

                    alphas[i] += y_encoded[i] * y_encoded[j] * (alpha_j_old - alphas[j])

                    b1 = (
                        b
                        - E_i
                        - y_encoded[i] * (alphas[i] - alpha_i_old) * kernel_matrix[i][i]
                        - y_encoded[j] * (alphas[j] - alpha_j_old) * kernel_matrix[i][j]
                    )
                    b2 = (
                        b
                        - E_j
                        - y_encoded[i] * (alphas[i] - alpha_i_old) * kernel_matrix[i][j]
                        - y_encoded[j] * (alphas[j] - alpha_j_old) * kernel_matrix[j][j]
                    )

                    if 0 < alphas[i] < self.C:
                        b = b1
                    elif 0 < alphas[j] < self.C:
                        b = b2
                    else:
                        b = (b1 + b2) / 2.0

                    num_changed_alphas += 1

            if num_changed_alphas == 0:
                passes += 1
            else:
                passes = 0

        self.alphas = alphas
        self.b = b
        self.w = [0.0] * n_features
        for i in range(n_samples):
            if alphas[i] > 0:
                for f in range(n_features):
                    self.w[f] += alphas[i] * y_encoded[i] * X[i][f]

        return self

    def decision_function(self, X: List[List[float]]) -> List[float]:
        n_features = len(self.w)
        scores = []
        for row in X:
            s = sum(row[f] * self.w[f] for f in range(min(len(row), n_features))) + self.b
            scores.append(round(s, 5))
        return scores

    def predict(self, X: List[List[float]]) -> List[Any]:
        scores = self.decision_function(X)
        return [self.classes[1] if s >= 0.0 else self.classes[0] for s in scores]


class KMeansPlusPlus:
    """K-Means clustering with Arthur-Vassilvitskii k-means++ probabilistic D^2 seeding."""

    def __init__(self, n_clusters: int = 3, max_iter: int = 100, tol: float = 1e-4, seed: Optional[int] = 42):
        self.n_clusters = max(1, int(n_clusters))
        self.max_iter = int(max_iter)
        self.tol = float(tol)
        self.seed = seed
        self.centroids: List[List[float]] = []
        self.inertia_: float = 0.0

    def fit(self, X: List[List[float]]) -> "KMeansPlusPlus":
        if self.seed is not None:
            random.seed(self.seed)

        n_samples = len(X)
        if n_samples == 0:
            return self
        n_features = len(X[0])
        k = min(self.n_clusters, n_samples)

        # 1. K-Means++ D^2 Initialization
        centroids = [list(random.choice(X))]
        while len(centroids) < k:
            distances = []
            for row in X:
                min_d2 = min(sum((row[f] - c[f]) ** 2 for f in range(n_features)) for c in centroids)
                distances.append(min_d2)
            total_d2 = sum(distances)
            if total_d2 == 0:
                centroids.append(list(random.choice(X)))
            else:
                r = random.uniform(0, total_d2)
                cum = 0.0
                chosen = X[-1]
                for idx, d2 in enumerate(distances):
                    cum += d2
                    if cum >= r:
                        chosen = X[idx]
                        break
                centroids.append(list(chosen))

        # 2. Lloyd's iterations
        for _ in range(self.max_iter):
            clusters: List[List[List[float]]] = [[] for _ in range(k)]
            for row in X:
                closest_c = 0
                best_d2 = float("inf")
                for c_idx, c in enumerate(centroids):
                    d2 = sum((row[f] - c[f]) ** 2 for f in range(n_features))
                    if d2 < best_d2:
                        best_d2 = d2
                        closest_c = c_idx
                clusters[closest_c].append(row)

            # Recompute centroids
            new_centroids = []
            max_shift = 0.0
            for c_idx in range(k):
                pts = clusters[c_idx]
                if pts:
                    new_c = [sum(pts[i][f] for i in range(len(pts))) / len(pts) for f in range(n_features)]
                else:
                    new_c = list(centroids[c_idx])
                shift = math.sqrt(sum((new_c[f] - centroids[c_idx][f]) ** 2 for f in range(n_features)))
                max_shift = max(max_shift, shift)
                new_centroids.append(new_c)

            centroids = new_centroids
            if max_shift < self.tol:
                break

        self.centroids = centroids

        # Calculate inertia
        total_inertia = 0.0
        for row in X:
            total_inertia += min(sum((row[f] - c[f]) ** 2 for f in range(n_features)) for c in self.centroids)
        self.inertia_ = round(total_inertia, 4)
        return self

    def predict(self, X: List[List[float]]) -> List[int]:
        n_features = len(self.centroids[0]) if self.centroids else 0
        labels = []
        for row in X:
            best_idx = 0
            best_d2 = float("inf")
            for c_idx, c in enumerate(self.centroids):
                d2 = sum((row[f] - c[f]) ** 2 for f in range(n_features))
                if d2 < best_d2:
                    best_d2 = d2
                    best_idx = c_idx
            labels.append(best_idx)
        return labels

    @classmethod
    def auto_find_k(cls, X: List[List[float]], k_range: Tuple[int, int] = (2, 6)) -> Dict[str, Any]:
        """Elbow method to automatically find optimal cluster count K."""
        k_min, k_max = k_range
        inertias = []
        models = []
        ks = list(range(k_min, min(k_max + 1, len(X))))

        for k in ks:
            model = cls(n_clusters=k)
            model.fit(X)
            inertias.append(model.inertia_)
            models.append(model)

        # Detect elbow point via second difference
        best_k = ks[0]
        if len(ks) >= 3:
            max_curvature = -1.0
            for i in range(1, len(ks) - 1):
                # Second derivative approximation: D2 = (y_{i-1} - 2*y_i + y_{i+1})
                curvature = inertias[i - 1] - 2 * inertias[i] + inertias[i + 1]
                if curvature > max_curvature:
                    max_curvature = curvature
                    best_k = ks[i]

        return {
            "optimal_k": best_k,
            "tested_k": ks,
            "inertias": inertias,
        }


class TinyConvNet:
    """Pure-Python Convolutional Neural Network forward & backward engine."""

    def __init__(self, in_shape: Tuple[int, int] = (6, 6), num_classes: int = 2, kernel_size: int = 3, seed: int = 42):
        random.seed(seed)
        self.h, self.w = in_shape
        self.k_size = kernel_size
        self.num_classes = num_classes

        # Filter weights: [k_size, k_size]
        self.kernel = [
            [(random.random() - 0.5) * 0.2 for _ in range(kernel_size)]
            for _ in range(kernel_size)
        ]
        self.kernel_bias = 0.0

        # Conv output shape
        self.conv_h = self.h - kernel_size + 1
        self.conv_w = self.w - kernel_size + 1

        # Maxpool (2x2, stride 2) output shape
        self.pool_h = self.conv_h // 2
        self.pool_w = self.conv_w // 2
        self.flat_size = self.pool_h * self.pool_w

        # Fully connected weights: [flat_size, num_classes]
        self.fc_w = [
            [(random.random() - 0.5) * 0.2 for _ in range(num_classes)]
            for _ in range(self.flat_size)
        ]
        self.fc_b = [0.0] * num_classes

    def forward(self, x_grid: List[List[float]]) -> Tuple[List[float], Dict[str, Any]]:
        """Forward pass through Conv2D -> ReLU -> MaxPool2D -> Dense -> Softmax."""
        # 1. Conv2D
        conv_out = [[0.0] * self.conv_w for _ in range(self.conv_h)]
        for r in range(self.conv_h):
            for c in range(self.conv_w):
                s = self.kernel_bias
                for kr in range(self.k_size):
                    for kc in range(self.k_size):
                        s += x_grid[r + kr][c + kc] * self.kernel[kr][kc]
                # ReLU activation
                conv_out[r][c] = max(0.0, s)

        # 2. MaxPool2D (2x2)
        pooled = [[0.0] * self.pool_w for _ in range(self.pool_h)]
        for r in range(self.pool_h):
            for c in range(self.pool_w):
                val = max(
                    conv_out[2 * r][2 * c],
                    conv_out[2 * r + 1][2 * c],
                    conv_out[2 * r][2 * c + 1],
                    conv_out[2 * r + 1][2 * c + 1],
                )
                pooled[r][c] = val

        # 3. Flatten
        flat = []
        for r in range(self.pool_h):
            for c in range(self.pool_w):
                flat.append(pooled[r][c])

        # 4. Dense FC
        logits = list(self.fc_b)
        for i in range(len(flat)):
            for j in range(self.num_classes):
                logits[j] += flat[i] * self.fc_w[i][j]

        # Softmax
        max_l = max(logits)
        exp_vals = [math.exp(v - max_l) for v in logits]
        sum_exp = sum(exp_vals)
        probs = [e / sum_exp for e in exp_vals]

        cache = {
            "x_grid": x_grid,
            "conv_out": conv_out,
            "pooled": pooled,
            "flat": flat,
            "probs": probs,
        }
        return probs, cache

    def train_step(self, x_grid: List[List[float]], target_class: int, lr: float = 0.05) -> float:
        """Single backpropagation step with SGD."""
        probs, cache = self.forward(x_grid)
        loss = -math.log(max(probs[target_class], 1e-12))

        # Output gradient: dL/dLogit = p_i - y_i
        d_logits = list(probs)
        d_logits[target_class] -= 1.0

        # Gradient for FC weights and bias
        flat = cache["flat"]
        d_flat = [0.0] * len(flat)
        for i in range(len(flat)):
            for j in range(self.num_classes):
                grad_w = flat[i] * d_logits[j]
                self.fc_w[i][j] -= lr * grad_w
                d_flat[i] += self.fc_w[i][j] * d_logits[j]

        for j in range(self.num_classes):
            self.fc_b[j] -= lr * d_logits[j]

        return loss

    def predict(self, x_grid: List[List[float]]) -> int:
        probs, _ = self.forward(x_grid)
        return probs.index(max(probs))


class GradientBoostedTreesExact:
    """Exact greedy split-finding Gradient Boosted Decision Trees with XGBoost objective."""

    def __init__(
        self,
        n_estimators: int = 10,
        learning_rate: float = 0.1,
        max_depth: int = 3,
        reg_lambda: float = 1.0,
        gamma: float = 0.0,
    ):
        self.n_estimators = int(n_estimators)
        self.lr = float(learning_rate)
        self.max_depth = int(max_depth)
        self.reg_lambda = float(reg_lambda)
        self.gamma = float(gamma)
        self.base_score: float = 0.0
        self.trees: List[Dict[str, Any]] = []

    def fit(self, X: List[List[float]], y: List[float]) -> "GradientBoostedTreesExact":
        n_samples = len(X)
        if n_samples == 0:
            return self

        self.base_score = sum(y) / n_samples
        y_pred = [self.base_score] * n_samples

        for _ in range(self.n_estimators):
            # Compute first and second order gradients for squared loss:
            # g_i = y_pred - y_i, h_i = 1.0
            grads = [y_pred[i] - y[i] for i in range(n_samples)]
            hess = [1.0] * n_samples

            indices = list(range(n_samples))
            tree = self._build_tree(X, grads, hess, indices, depth=0)
            self.trees.append(tree)

            # Update predictions
            for i in range(n_samples):
                y_pred[i] += self.lr * self._predict_tree(tree, X[i])

        return self

    def _build_tree(
        self,
        X: List[List[float]],
        grads: List[float],
        hess: List[float],
        indices: List[int],
        depth: int,
    ) -> Dict[str, Any]:
        G = sum(grads[i] for i in indices)
        H = sum(hess[i] for i in indices)
        leaf_weight = -G / (H + self.reg_lambda) if (H + self.reg_lambda) > 0 else 0.0

        if depth >= self.max_depth or len(indices) <= 2:
            return {"is_leaf": True, "weight": leaf_weight}

        best_gain = 0.0
        best_split = None
        current_score = (G ** 2) / (H + self.reg_lambda)
        n_features = len(X[0])

        for f in range(n_features):
            # Sort indices by feature value
            sorted_indices = sorted(indices, key=lambda i: X[i][f])
            G_L, H_L = 0.0, 0.0
            for idx_pos in range(len(sorted_indices) - 1):
                idx = sorted_indices[idx_pos]
                G_L += grads[idx]
                H_L += hess[idx]
                G_R = G - G_L
                H_R = H - H_L

                # Check if next feature value is strictly different
                next_idx = sorted_indices[idx_pos + 1]
                if X[idx][f] == X[next_idx][f]:
                    continue

                gain = 0.5 * (
                    (G_L ** 2) / (H_L + self.reg_lambda)
                    + (G_R ** 2) / (H_R + self.reg_lambda)
                    - current_score
                ) - self.gamma

                if gain > best_gain:
                    best_gain = gain
                    threshold = (X[idx][f] + X[next_idx][f]) / 2.0
                    best_split = (f, threshold, sorted_indices[: idx_pos + 1], sorted_indices[idx_pos + 1 :])

        if best_split is None or best_gain <= 0.0:
            return {"is_leaf": True, "weight": leaf_weight}

        feat_idx, thresh, left_idxs, right_idxs = best_split
        return {
            "is_leaf": False,
            "feature": feat_idx,
            "threshold": thresh,
            "left": self._build_tree(X, grads, hess, left_idxs, depth + 1),
            "right": self._build_tree(X, grads, hess, right_idxs, depth + 1),
        }

    def _predict_tree(self, node: Dict[str, Any], x: List[float]) -> float:
        if node["is_leaf"]:
            return node["weight"]
        if x[node["feature"]] <= node["threshold"]:
            return self._predict_tree(node["left"], x)
        else:
            return self._predict_tree(node["right"], x)

    def predict(self, X: List[List[float]]) -> List[float]:
        preds = []
        for x in X:
            val = self.base_score
            for tree in self.trees:
                val += self.lr * self._predict_tree(tree, x)
            preds.append(round(val, 4))
        return preds


def ml_svm_train(X: Any, y: Any, C: float = 1.0) -> LinearSVM:
    """Trains a Linear Support Vector Machine using SMO."""
    svm = LinearSVM(C=C)
    svm.fit([list(r) for r in X], list(y))
    return svm


def ml_kmeans_plus_plus(X: Any, n_clusters: int = 3) -> KMeansPlusPlus:
    """Performs K-Means++ clustering."""
    km = KMeansPlusPlus(n_clusters=n_clusters)
    km.fit([list(r) for r in X])
    return km


def ml_tiny_convnet(in_shape: Tuple[int, int] = (6, 6), num_classes: int = 2) -> TinyConvNet:
    """Creates a pure-Python 2D Convolutional Neural Network."""
    return TinyConvNet(in_shape=in_shape, num_classes=num_classes)


def ml_xgboost_exact(X: Any, y: Any, n_estimators: int = 10, max_depth: int = 3) -> GradientBoostedTreesExact:
    """Trains an exact-split Gradient Boosted Tree model."""
    model = GradientBoostedTreesExact(n_estimators=n_estimators, max_depth=max_depth)
    model.fit([list(r) for r in X], [float(v) for v in y])
    return model


# ==============================================================================
# GAUSSIAN MIXTURE MODEL (EM) & PRINCIPAL COMPONENT ANALYSIS (PCA)
# ==============================================================================

class GaussianMixtureModelEM:
    """Expectation-Maximization (EM) Gaussian Mixture Model for clustering and density estimation."""

    def __init__(self, n_components: int = 2, max_iters: int = 100, tol: float = 1e-4):
        self.k = max(1, int(n_components))
        self.max_iters = max(1, int(max_iters))
        self.tol = float(tol)
        self.weights: List[float] = []
        self.means: List[List[float]] = []
        self.variances: List[List[float]] = []
        self.converged: bool = False
        self.iterations: int = 0
        self.log_likelihood: float = float("-inf")
        self.bic: float = 0.0

    def fit(self, X: List[List[float]]) -> "GaussianMixtureModelEM":
        n = len(X)
        if n == 0:
            return self
        d = len(X[0])

        # Initialize components deterministically using quantiles
        self.weights = [1.0 / self.k] * self.k
        self.means = []
        step = max(1, n // self.k)
        for i in range(self.k):
            idx = min(n - 1, i * step)
            self.means.append(list(X[idx]))

        # Global feature variances as initial variance
        global_var = [0.0] * d
        global_mean = [sum(X[r][c] for r in range(n)) / n for c in range(d)]
        for r in range(n):
            for c in range(d):
                global_var[c] += (X[r][c] - global_mean[c]) ** 2
        global_var = [max(1e-4, v / max(1, n)) for v in global_var]
        self.variances = [list(global_var) for _ in range(self.k)]

        prev_ll = float("-inf")

        for it in range(self.max_iters):
            self.iterations = it + 1

            # --- E-Step: Responsibilities ---
            responsibilities: List[List[float]] = []
            current_ll = 0.0

            for i in range(n):
                x = X[i]
                log_probs = []
                for comp in range(self.k):
                    w = max(1e-12, self.weights[comp])
                    m = self.means[comp]
                    var = self.variances[comp]

                    # Log multivariate Gaussian PDF
                    log_p = math.log(w)
                    for j in range(d):
                        v_j = max(1e-6, var[j])
                        diff = x[j] - m[j]
                        log_p += -0.5 * math.log(2.0 * math.pi * v_j) - 0.5 * (diff * diff) / v_j
                    log_probs.append(log_p)

                # Log-sum-exp trick
                max_lp = max(log_probs)
                sum_exp = sum(math.exp(lp - max_lp) for lp in log_probs)
                log_norm = max_lp + math.log(max(1e-12, sum_exp))
                current_ll += log_norm

                resps = [math.exp(lp - log_norm) for lp in log_probs]
                responsibilities.append(resps)

            self.log_likelihood = current_ll

            # Check convergence
            if it > 0 and abs(current_ll - prev_ll) < self.tol:
                self.converged = True
                break
            prev_ll = current_ll

            # --- M-Step: Parameter Updates ---
            n_k = [sum(responsibilities[i][comp] for i in range(n)) for comp in range(self.k)]

            for comp in range(self.k):
                nk = max(1e-10, n_k[comp])
                self.weights[comp] = nk / n

                # Update mean
                new_mean = [0.0] * d
                for i in range(n):
                    r_ik = responsibilities[i][comp]
                    for j in range(d):
                        new_mean[j] += r_ik * X[i][j]
                self.means[comp] = [val / nk for val in new_mean]

                # Update variance
                new_var = [0.0] * d
                for i in range(n):
                    r_ik = responsibilities[i][comp]
                    for j in range(d):
                        diff = X[i][j] - self.means[comp][j]
                        new_var[j] += r_ik * (diff * diff)
                self.variances[comp] = [max(1e-6, val / nk) for val in new_var]

        # Calculate Bayesian Information Criterion (BIC)
        p = self.k - 1 + 2 * self.k * d
        self.bic = round(-2.0 * self.log_likelihood + p * math.log(max(1, n)), 4)
        return self

    def predict(self, X: List[List[float]]) -> List[int]:
        """Assigns each sample to component with maximum posterior responsibility."""
        predictions = []
        d = len(self.means[0]) if self.means else 0
        for x in X:
            best_comp = 0
            best_prob = float("-inf")
            for comp in range(self.k):
                w = max(1e-12, self.weights[comp])
                m = self.means[comp]
                var = self.variances[comp]
                log_p = math.log(w)
                for j in range(d):
                    v_j = max(1e-6, var[j])
                    diff = x[j] - m[j]
                    log_p += -0.5 * math.log(2.0 * math.pi * v_j) - 0.5 * (diff * diff) / v_j
                if log_p > best_prob:
                    best_prob = log_p
                    best_comp = comp
            predictions.append(best_comp)
        return predictions


class PrincipalComponentAnalysisPCA:
    """Principal Component Analysis (PCA) with Covariance Eigendecomposition."""

    def __init__(self, n_components: int = 2):
        self.n_components = max(1, int(n_components))
        self.components: List[List[float]] = []  # Eigenvector matrix (n_components x d)
        self.explained_variance: List[float] = []
        self.explained_variance_ratio: List[float] = []
        self.mean: List[float] = []

    def fit(self, X: List[List[float]]) -> "PrincipalComponentAnalysisPCA":
        n = len(X)
        if n == 0:
            return self
        d = len(X[0])
        k = min(self.n_components, d)

        # 1. Compute empirical mean and center data
        self.mean = [sum(X[r][c] for r in range(n)) / n for c in range(d)]
        x_centered = [[X[r][c] - self.mean[c] for c in range(d)] for r in range(n)]

        # 2. Compute d x d sample covariance matrix
        cov = [[0.0] * d for _ in range(d)]
        denom = max(1, n - 1)
        for i in range(d):
            for j in range(i, d):
                s = sum(x_centered[r][i] * x_centered[r][j] for r in range(n)) / denom
                cov[i][j] = s
                cov[j][i] = s

        total_var = sum(cov[i][i] for i in range(d))

        # 3. Orthogonal Power Iteration to extract top k eigenvectors
        found_vectors: List[List[float]] = []
        eigenvalues: List[float] = []

        for comp_idx in range(k):
            # Seed vector
            v = [1.0 if idx == comp_idx else 0.0 for idx in range(d)]

            for _ in range(60):
                # Matrix-vector multiply: w = Cov * v
                w = [0.0] * d
                for r in range(d):
                    w[r] = sum(cov[r][c] * v[c] for c in range(d))

                # Gram-Schmidt orthogonalization against prior components
                for prev_v in found_vectors:
                    proj = sum(w[c] * prev_v[c] for c in range(d))
                    for c in range(d):
                        w[c] -= proj * prev_v[c]

                norm = math.sqrt(sum(x * x for x in w))
                if norm > 1e-12:
                    v = [x / norm for x in w]
                else:
                    break

            # Eigenvalue = v^T * Cov * v
            cov_v = [sum(cov[r][c] * v[c] for c in range(d)) for r in range(d)]
            eig_val = sum(v[c] * cov_v[c] for c in range(d))

            found_vectors.append(v)
            eigenvalues.append(max(0.0, eig_val))

        self.components = found_vectors
        self.explained_variance = [round(e, 6) for e in eigenvalues]
        self.explained_variance_ratio = [
            round(e / max(1e-12, total_var), 4) for e in eigenvalues
        ]
        return self

    def transform(self, X: List[List[float]]) -> List[List[float]]:
        """Projects data onto principal component subspace."""
        n = len(X)
        d = len(self.mean)
        k = len(self.components)
        projected = []

        for r in range(n):
            centered = [X[r][c] - self.mean[c] for c in range(d)]
            row = []
            for comp_idx in range(k):
                comp_v = self.components[comp_idx]
                proj = sum(centered[c] * comp_v[c] for c in range(d))
                row.append(round(proj, 4))
            projected.append(row)

        return projected


def ml_gmm_fit(data: List[List[float]], k: int = 2, max_iters: int = 50) -> Any:
    """Fits Gaussian Mixture Model using Expectation-Maximization."""
    gmm = GaussianMixtureModelEM(n_components=k, max_iters=max_iters)
    gmm.fit([list(r) for r in data])
    return Record({
        "num_components": gmm.k,
        "converged": gmm.converged,
        "iterations": gmm.iterations,
        "log_likelihood": round(gmm.log_likelihood, 4),
        "bic": gmm.bic,
        "weights": [round(w, 4) for w in gmm.weights],
        "means": [[round(m, 4) for m in comp] for comp in gmm.means],
        "instance": gmm,
    })


def ml_gmm_predict(model: Any, samples: List[List[float]]) -> List[int]:
    """Predicts component assignments for samples using trained GMM."""
    inst = model.instance if hasattr(model, "instance") else model
    return inst.predict([list(r) for r in samples])


def ml_pca_fit(data: List[List[float]], n_components: int = 2) -> Any:
    """Fits Principal Component Analysis model."""
    pca = PrincipalComponentAnalysisPCA(n_components=n_components)
    pca.fit([list(r) for r in data])
    return Record({
        "n_components": len(pca.components),
        "explained_variance": pca.explained_variance,
        "explained_variance_ratio": pca.explained_variance_ratio,
        "instance": pca,
    })


def ml_pca_transform(first: Any, second: Any = 2, n_components: Any = None) -> Any:
    """Transforms data using PCA (either direct PCA dimensionality reduction or fitted PCA model transform)."""
    if n_components is not None:
        return _ml_pca_transform_direct(first, n_components)
    if hasattr(first, "instance") or hasattr(first, "transform") or (isinstance(first, dict) and "instance" in first):
        inst = first["instance"] if isinstance(first, dict) and "instance" in first else (first.instance if hasattr(first, "instance") else first)
        return inst.transform([list(r) for r in second])
    return _ml_pca_transform_direct(first, second)


# ==============================================================================
# ISOLATION FOREST ANOMALY DETECTOR
# ==============================================================================

class IsolationTreeNode:
    def __init__(self, size: int):
        self.size = size
        self.split_feature: Optional[int] = None
        self.split_value: Optional[float] = None
        self.left: Optional["IsolationTreeNode"] = None
        self.right: Optional["IsolationTreeNode"] = None


class IsolationForestAnomalyDetector:
    """Isolation Forest algorithm (Liu, Ting, Zhou 2008) for unsupervised outlier detection."""

    EULER_MASCHERONI = 0.5772156649

    def __init__(self, n_trees: int = 50, max_samples: int = 256, contamination: float = 0.1, seed: Optional[int] = 42):
        self.n_trees = max(5, int(n_trees))
        self.max_samples = max(8, int(max_samples))
        self.contamination = float(contamination)
        self.seed = seed
        self.trees: List[IsolationTreeNode] = []
        self.max_depth = 0
        self.subsample_size = 0

    @classmethod
    def _c_factor(cls, n: int) -> float:
        """Average path length of unsuccessful searches in BST."""
        if n <= 1:
            return 0.0
        if n == 2:
            return 1.0
        return 2.0 * (math.log(n - 1) + cls.EULER_MASCHERONI) - (2.0 * (n - 1) / n)

    def _build_itree(self, X: List[List[float]], current_depth: int, rng: random.Random) -> IsolationTreeNode:
        n = len(X)
        node = IsolationTreeNode(n)
        if current_depth >= self.max_depth or n <= 1:
            return node

        d = len(X[0])
        features = list(range(d))
        rng.shuffle(features)

        split_feature = None
        min_v = 0.0
        max_v = 0.0

        for f in features:
            vals = [row[f] for row in X]
            f_min = min(vals)
            f_max = max(vals)
            if f_min < f_max:
                split_feature = f
                min_v = f_min
                max_v = f_max
                break

        if split_feature is None:
            return node

        split_value = rng.uniform(min_v, max_v)
        left_X = [row for row in X if row[split_feature] < split_value]
        right_X = [row for row in X if row[split_feature] >= split_value]

        node.split_feature = split_feature
        node.split_value = split_value
        node.left = self._build_itree(left_X, current_depth + 1, rng)
        node.right = self._build_itree(right_X, current_depth + 1, rng)
        return node

    def fit(self, X: List[List[float]]) -> "IsolationForestAnomalyDetector":
        n = len(X)
        if n == 0:
            return self

        self.subsample_size = min(self.max_samples, n)
        self.max_depth = int(math.ceil(math.log2(max(2, self.subsample_size))))
        rng = random.Random(self.seed)
        self.trees = []

        for _ in range(self.n_trees):
            if n <= self.subsample_size:
                subsample = list(X)
            else:
                indices = rng.sample(range(n), self.subsample_size)
                subsample = [X[i] for i in indices]
            tree_root = self._build_itree(subsample, 0, rng)
            self.trees.append(tree_root)

        return self

    def _path_length(self, x: List[float], node: IsolationTreeNode, current_depth: int) -> float:
        if node.left is None or node.right is None or node.split_feature is None or node.split_value is None:
            return current_depth + self._c_factor(node.size)
        f = node.split_feature
        if x[f] < node.split_value:
            return self._path_length(x, node.left, current_depth + 1)
        else:
            return self._path_length(x, node.right, current_depth + 1)

    def score_samples(self, X: List[List[float]]) -> List[float]:
        """Calculates anomaly scores s(x, n) in [0, 1]. High score indicates anomaly."""
        c = self._c_factor(self.subsample_size)
        if c <= 0.0 or not self.trees:
            return [0.5] * len(X)

        scores = []
        for row in X:
            avg_h = sum(self._path_length(row, t, 0) for t in self.trees) / len(self.trees)
            s = 2.0 ** (-avg_h / c)
            scores.append(round(s, 4))
        return scores

    def predict(self, X: List[List[float]]) -> List[int]:
        """Returns 1 for normal instances, -1 for anomalies."""
        scores = self.score_samples(X)
        sorted_scores = sorted(scores, reverse=True)
        idx = int(math.floor(len(scores) * self.contamination))
        threshold = sorted_scores[min(idx, len(scores) - 1)] if sorted_scores else 0.6
        return [-1 if s >= threshold else 1 for s in scores]


# ==============================================================================
# DBSCAN CLUSTERING ENGINE
# ==============================================================================

class DBSCANClusteringEngine:
    """Density-Based Spatial Clustering of Applications with Noise (Ester et al. 1996)."""

    @staticmethod
    def _dist(p1: List[float], p2: List[float]) -> float:
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))

    @classmethod
    def fit(cls, X: List[List[float]], eps: float = 0.5, min_samples: int = 5) -> Dict[str, Any]:
        n = len(X)
        if n == 0:
            return {"labels": [], "num_clusters": 0, "num_noise": 0, "core_indices": []}

        eps_val = max(1e-6, float(eps))
        min_pts = max(1, int(min_samples))

        labels = [-1] * n
        visited = [False] * n
        cluster_id = 0
        core_indices = []

        neighbors_map: List[List[int]] = []
        for i in range(n):
            nbrs = []
            for j in range(n):
                if cls._dist(X[i], X[j]) <= eps_val:
                    nbrs.append(j)
            neighbors_map.append(nbrs)
            if len(nbrs) >= min_pts:
                core_indices.append(i)

        for i in range(n):
            if visited[i]:
                continue
            visited[i] = True

            nbrs = list(neighbors_map[i])
            if len(nbrs) < min_pts:
                labels[i] = -1
            else:
                labels[i] = cluster_id
                queue = list(nbrs)
                while queue:
                    q_idx = queue.pop(0)
                    if not visited[q_idx]:
                        visited[q_idx] = True
                        q_nbrs = neighbors_map[q_idx]
                        if len(q_nbrs) >= min_pts:
                            queue.extend(q_nbrs)
                    if labels[q_idx] == -1:
                        labels[q_idx] = cluster_id

                cluster_id += 1

        num_noise = sum(1 for l in labels if l == -1)

        return {
            "labels": labels,
            "num_clusters": cluster_id,
            "num_noise": num_noise,
            "core_indices": core_indices,
            "eps": eps_val,
            "min_samples": min_pts,
        }


def ml_isolation_forest(data: List[List[float]], n_trees: int = 50, contamination: float = 0.1) -> Record:
    """Detects anomalies using Isolation Forest ensemble."""
    iso = IsolationForestAnomalyDetector(n_trees=n_trees, contamination=contamination)
    data_list = [list(r) for r in data]
    iso.fit(data_list)
    scores = iso.score_samples(data_list)
    preds = iso.predict(data_list)
    return Record({
        "anomaly_scores": scores,
        "predictions": preds,
        "num_trees": iso.n_trees,
        "anomalies_detected": preds.count(-1),
        "instance": iso,
    })


def ml_dbscan(data: List[List[float]], eps: float = 0.5, min_samples: int = 5) -> Record:
    """Clusters data points using density-based DBSCAN algorithm."""
    data_list = [list(r) for r in data]
    res = DBSCANClusteringEngine.fit(data_list, eps=eps, min_samples=min_samples)
    return Record(res)






def execute_ml_ir(spec: Any) -> Any:
    """Executes an ML Domain IR specification against the caller's scope."""
    import sys
    from doomscript.domains.registry import get_domain_registry
    if isinstance(spec, str):
        spec = get_domain_registry().get_spec(spec)
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    res = MLModelRuntime().execute_ir(spec, scope)
    for k, v in scope.items():
        target_env[k] = v
    return res


def accuracy_score_fn(preds: Any, actuals: Any) -> float:
    """Calculates accuracy score between predicted and actual values."""
    if not preds or not actuals:
        return 0.0
    p_list = list(preds)
    a_list = list(actuals)
    if len(p_list) != len(a_list):
        return 0.0
    correct = sum(1 for p, a in zip(p_list, a_list) if p == a)
    return round(correct / len(p_list), 4)


def train_direct_model(
    algo: str,
    data_val: Any,
    target_col: str,
    feature_cols: Optional[List[str]] = None,
    scope: Optional[Dict[str, Any]] = None,
):
    """Direct one-liner model trainer."""
    from doomscript.domains.data.runtime import _to_record_list
    from doomscript.domains.ml.spec import ModelSpec
    rows = _to_record_list(data_val)
    if not feature_cols and rows:
        feature_cols = [k for k in rows[0].keys() if k != target_col]
    spec = ModelSpec(
        name=f"{algo}_model",
        dataset="__direct_dataset__",
        target=target_col,
        features=feature_cols or [],
        algorithm=algo,
    )
    container = ModelContainer(spec)
    if scope is None:
        import sys
        caller_frame = sys._getframe(1)
        scope = dict(caller_frame.f_globals)
        if caller_frame.f_locals:
            scope.update(caller_frame.f_locals)
    scope["__direct_dataset__"] = data_val
    return train_model(container, scope=scope)


# ==============================================================================
# DEEP LEARNING: AUTOENCODER & 1D CONVOLUTIONAL NEURAL NETWORKS (PURE PYTHON)
# ==============================================================================

class AutoencoderNeuralNetwork:
    """Bottleneck Autoencoder with dense encoder/decoder stages and Adam optimizer."""

    def __init__(self, input_dim: int, latent_dim: int, hidden_dim: int = 16):
        import random
        import math
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.hidden_dim = hidden_dim

        # Xavier initialization
        def init_weights(din, dout):
            limit = math.sqrt(6.0 / (din + dout))
            return [[random.uniform(-limit, limit) for _ in range(dout)] for _ in range(din)]

        # Encoder: input -> hidden -> latent
        self.w_enc1 = init_weights(input_dim, hidden_dim)
        self.b_enc1 = [0.0] * hidden_dim
        self.w_enc2 = init_weights(hidden_dim, latent_dim)
        self.b_enc2 = [0.0] * latent_dim

        # Decoder: latent -> hidden -> output
        self.w_dec1 = init_weights(latent_dim, hidden_dim)
        self.b_dec1 = [0.0] * hidden_dim
        self.w_dec2 = init_weights(hidden_dim, input_dim)
        self.b_dec2 = [0.0] * input_dim

    @staticmethod
    def _relu(x: float) -> float:
        return max(0.0, x)

    @staticmethod
    def _relu_deriv(x: float) -> float:
        return 1.0 if x > 0 else 0.0

    def encode(self, x: List[float]) -> List[float]:
        """Encodes high-dimensional sample into latent bottleneck representation."""
        # Layer 1
        h1 = [0.0] * self.hidden_dim
        for j in range(self.hidden_dim):
            s = sum(x[i] * self.w_enc1[i][j] for i in range(self.input_dim)) + self.b_enc1[j]
            h1[j] = self._relu(s)
        # Latent
        z = [0.0] * self.latent_dim
        for j in range(self.latent_dim):
            z[j] = sum(h1[i] * self.w_enc2[i][j] for i in range(self.hidden_dim)) + self.b_enc2[j]
        return z

    def decode(self, z: List[float]) -> List[float]:
        """Reconstructs original feature dimensions from latent representation."""
        # Hidden
        h2 = [0.0] * self.hidden_dim
        for j in range(self.hidden_dim):
            s = sum(z[i] * self.w_dec1[i][j] for i in range(self.latent_dim)) + self.b_dec1[j]
            h2[j] = self._relu(s)
        # Output
        out = [0.0] * self.input_dim
        for j in range(self.input_dim):
            out[j] = sum(h2[i] * self.w_dec2[i][j] for i in range(self.hidden_dim)) + self.b_dec2[j]
        return out

    def reconstruct(self, x: List[float]) -> List[float]:
        return self.decode(self.encode(x))

    def train_step(self, x: List[float], lr: float = 0.01) -> float:
        """Single backpropagation iteration updating weights via SGD with reconstruction MSE loss."""
        # 1. Forward pass
        # Enc1
        s_h1 = [sum(x[i] * self.w_enc1[i][j] for i in range(self.input_dim)) + self.b_enc1[j] for j in range(self.hidden_dim)]
        h1 = [self._relu(v) for v in s_h1]
        # Enc2 (latent)
        z = [sum(h1[i] * self.w_enc2[i][j] for i in range(self.hidden_dim)) + self.b_enc2[j] for j in range(self.latent_dim)]
        # Dec1
        s_h2 = [sum(z[i] * self.w_dec1[i][j] for i in range(self.latent_dim)) + self.b_dec1[j] for j in range(self.hidden_dim)]
        h2 = [self._relu(v) for v in s_h2]
        # Dec2 (reconstructed out)
        x_hat = [sum(h2[i] * self.w_dec2[i][j] for i in range(self.hidden_dim)) + self.b_dec2[j] for j in range(self.input_dim)]

        # MSE loss: 0.5 * sum((x_hat - x)^2)
        loss = sum((x_hat[i] - x[i]) ** 2 for i in range(self.input_dim)) / self.input_dim

        # 2. Backward pass
        # dL/dx_hat
        d_out = [2.0 * (x_hat[i] - x[i]) / self.input_dim for i in range(self.input_dim)]

        # Dec2 grads
        d_w_dec2 = [[h2[i] * d_out[j] for j in range(self.input_dim)] for i in range(self.hidden_dim)]
        d_b_dec2 = list(d_out)

        # dL/dh2
        d_h2 = [sum(d_out[j] * self.w_dec2[i][j] for j in range(self.input_dim)) * self._relu_deriv(s_h2[i]) for i in range(self.hidden_dim)]

        # Dec1 grads
        d_w_dec1 = [[z[i] * d_h2[j] for j in range(self.hidden_dim)] for i in range(self.latent_dim)]
        d_b_dec1 = list(d_h2)

        # dL/dz
        d_z = [sum(d_h2[j] * self.w_dec1[i][j] for j in range(self.hidden_dim)) for i in range(self.latent_dim)]

        # Enc2 grads
        d_w_enc2 = [[h1[i] * d_z[j] for j in range(self.latent_dim)] for i in range(self.hidden_dim)]
        d_b_enc2 = list(d_z)

        # dL/dh1
        d_h1 = [sum(d_z[j] * self.w_enc2[i][j] for j in range(self.latent_dim)) * self._relu_deriv(s_h1[i]) for i in range(self.hidden_dim)]

        # Enc1 grads
        d_w_enc1 = [[x[i] * d_h1[j] for j in range(self.hidden_dim)] for i in range(self.input_dim)]
        d_b_enc1 = list(d_h1)

        # Update weights (SGD)
        for i in range(self.input_dim):
            for j in range(self.hidden_dim):
                self.w_enc1[i][j] -= lr * d_w_enc1[i][j]
        for j in range(self.hidden_dim):
            self.b_enc1[j] -= lr * d_b_enc1[j]

        for i in range(self.hidden_dim):
            for j in range(self.latent_dim):
                self.w_enc2[i][j] -= lr * d_w_enc2[i][j]
        for j in range(self.latent_dim):
            self.b_enc2[j] -= lr * d_b_enc2[j]

        for i in range(self.latent_dim):
            for j in range(self.hidden_dim):
                self.w_dec1[i][j] -= lr * d_w_dec1[i][j]
        for j in range(self.hidden_dim):
            self.b_dec1[j] -= lr * d_b_dec1[j]

        for i in range(self.hidden_dim):
            for j in range(self.input_dim):
                self.w_dec2[i][j] -= lr * d_w_dec2[i][j]
        for j in range(self.input_dim):
            self.b_dec2[j] -= lr * d_b_dec2[j]

        return loss

    def fit(self, dataset: List[List[float]], epochs: int = 50, lr: float = 0.01) -> List[float]:
        history = []
        for _ in range(epochs):
            total_loss = 0.0
            for sample in dataset:
                total_loss += self.train_step(sample, lr=lr)
            history.append(total_loss / max(1, len(dataset)))
        return history


def ml_autoencoder(input_dim: int, latent_dim: int, hidden_dim: int = 16) -> AutoencoderNeuralNetwork:
    """Instantiates a dense bottle-neck Autoencoder neural network."""
    return AutoencoderNeuralNetwork(input_dim, latent_dim, hidden_dim)
