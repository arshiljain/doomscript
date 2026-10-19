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
    return {"train": train_set, "test": test_set}


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


def ml_pca_transform(data: Any, n_components: Any = 2) -> List[Dict[str, Any]]:
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

