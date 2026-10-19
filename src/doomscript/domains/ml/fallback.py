"""Zero-dependency Native ML algorithms and utilities for DoomScript.
Runs anywhere with standard Python without requiring scikit-learn or numpy.
"""

import math
import random
from typing import Any, Dict, List, Optional, Tuple


def train_test_split(
    X: List[List[float]], y: List[Any], train_ratio: float = 0.8, seed: int = 42
) -> Tuple[List[List[float]], List[List[float]], List[Any], List[Any]]:
    """Splits dataset into train and test sets deterministically."""
    combined = list(zip(X, y))
    rng = random.Random(seed)
    rng.shuffle(combined)
    split_idx = int(len(combined) * train_ratio)
    train_part = combined[:split_idx]
    test_part = combined[split_idx:]

    X_train = [p[0] for p in train_part]
    y_train = [p[1] for p in train_part]
    X_test = [p[0] for p in test_part]
    y_test = [p[1] for p in test_part]
    return X_train, X_test, y_train, y_test


class NativeLinearRegression:
    """Zero-dependency Multivariate Linear Regression using Gradient Descent."""

    def __init__(self, lr: float = 0.05, epochs: int = 500):
        self.lr = lr
        self.epochs = epochs
        self.weights: List[float] = []
        self.bias: float = 0.0

    def fit(self, X: List[List[float]], y: List[float]) -> "NativeLinearRegression":
        if not X:
            return self
        n_samples = len(X)
        n_features = len(X[0])

        x_mean = [sum(X[i][j] for i in range(n_samples)) / n_samples for j in range(n_features)]
        x_std = [
            math.sqrt(sum((X[i][j] - x_mean[j]) ** 2 for i in range(n_samples)) / n_samples) or 1.0
            for j in range(n_features)
        ]
        y_mean = sum(y) / n_samples
        y_std = math.sqrt(sum((yi - y_mean) ** 2 for yi in y) / n_samples) or 1.0

        X_norm = [[(X[i][j] - x_mean[j]) / x_std[j] for j in range(n_features)] for i in range(n_samples)]
        y_norm = [(yi - y_mean) / y_std for yi in y]

        w_norm = [0.0] * n_features
        b_norm = 0.0

        for _ in range(self.epochs):
            for i in range(n_samples):
                xi = X_norm[i]
                yi = y_norm[i]
                pred = sum(w * x for w, x in zip(w_norm, xi)) + b_norm
                error = pred - yi
                for j in range(n_features):
                    w_norm[j] -= self.lr * error * xi[j]
                b_norm -= self.lr * error

        # Unscale weights and bias back to original domain
        self.weights = [(w_norm[j] * y_std) / x_std[j] for j in range(n_features)]
        self.bias = y_mean + (y_std * b_norm) - sum(self.weights[j] * x_mean[j] for j in range(n_features))
        return self

    def predict(self, X: List[List[float]]) -> List[float]:
        return [sum(w * x for w, x in zip(self.weights, xi)) + self.bias for xi in X]


class NativeLogisticRegression:
    """Zero-dependency Binary / Multi-class Logistic Regression."""

    def __init__(self, lr: float = 0.05, epochs: int = 400):
        self.lr = lr
        self.epochs = epochs
        self.classes: List[Any] = []
        self.weights: List[float] = []
        self.bias: float = 0.0

    def fit(self, X: List[List[float]], y: List[Any]) -> "NativeLogisticRegression":
        if not X:
            return self
        self.classes = sorted(list(set(y)))
        n_samples = len(X)
        n_features = len(X[0])
        self.weights = [0.0] * n_features
        self.bias = 0.0

        if len(self.classes) <= 1:
            return self

        # Map to 0 and 1 for binary
        positive_class = self.classes[1]
        y_binary = [1.0 if yi == positive_class else 0.0 for yi in y]

        for _ in range(self.epochs):
            for i in range(n_samples):
                xi = X[i]
                yi = y_binary[i]
                z = sum(w * x for w, x in zip(self.weights, xi)) + self.bias
                z = max(min(z, 20.0), -20.0)
                pred = 1.0 / (1.0 + math.exp(-z))
                error = pred - yi
                for j in range(n_features):
                    self.weights[j] -= self.lr * error * xi[j]
                self.bias -= self.lr * error
        return self

    def predict(self, X: List[List[float]]) -> List[Any]:
        if len(self.classes) <= 1:
            return [self.classes[0] if self.classes else None] * len(X)
        positive_class = self.classes[1]
        negative_class = self.classes[0]
        preds = []
        for xi in X:
            z = sum(w * x for w, x in zip(self.weights, xi)) + self.bias
            z = max(min(z, 20.0), -20.0)
            prob = 1.0 / (1.0 + math.exp(-z))
            preds.append(positive_class if prob >= 0.5 else negative_class)
        return preds


class NativeDecisionTree:
    """Zero-dependency Decision Tree Classifier."""

    def __init__(self, max_depth: int = 5, min_samples: int = 2):
        self.max_depth = max_depth
        self.min_samples = min_samples
        self.tree: Optional[Dict[str, Any]] = None

    def fit(self, X: List[List[float]], y: List[Any]) -> "NativeDecisionTree":
        self.tree = self._build_tree(X, y, depth=0)
        return self

    def _build_tree(self, X: List[List[float]], y: List[Any], depth: int) -> Dict[str, Any]:
        if not y:
            return {"leaf": True, "value": None}
        counts = {}
        for yi in y:
            counts[yi] = counts.get(yi, 0) + 1
        majority = max(counts.items(), key=lambda item: item[1])[0]

        if len(counts) == 1 or depth >= self.max_depth or len(y) < self.min_samples:
            return {"leaf": True, "value": majority}

        n_features = len(X[0])
        best_gain = -1.0
        best_criteria = None
        best_splits = None

        current_entropy = self._entropy(y)

        for feat_idx in range(n_features):
            vals = sorted(list(set(row[feat_idx] for row in X)))
            for v_idx in range(len(vals) - 1):
                thresh = (vals[v_idx] + vals[v_idx + 1]) / 2.0
                left_X, left_y, right_X, right_y = [], [], [], []
                for row, yi in zip(X, y):
                    if row[feat_idx] <= thresh:
                        left_X.append(row)
                        left_y.append(yi)
                    else:
                        right_X.append(row)
                        right_y.append(yi)
                if not left_y or not right_y:
                    continue
                p_left = len(left_y) / len(y)
                gain = current_entropy - (p_left * self._entropy(left_y) + (1 - p_left) * self._entropy(right_y))
                if gain > best_gain:
                    best_gain = gain
                    best_criteria = (feat_idx, thresh)
                    best_splits = (left_X, left_y, right_X, right_y)

        if best_gain <= 0.0 or best_criteria is None:
            return {"leaf": True, "value": majority}

        left_node = self._build_tree(best_splits[0], best_splits[1], depth + 1)
        right_node = self._build_tree(best_splits[2], best_splits[3], depth + 1)
        return {
            "leaf": False,
            "feature": best_criteria[0],
            "threshold": best_criteria[1],
            "left": left_node,
            "right": right_node,
            "value": majority,
        }

    def _entropy(self, y: List[Any]) -> float:
        n = len(y)
        counts = {}
        for yi in y:
            counts[yi] = counts.get(yi, 0) + 1
        ent = 0.0
        for count in counts.values():
            p = count / n
            if p > 0:
                ent -= p * math.log2(p)
        return ent

    def predict(self, X: List[List[float]]) -> List[Any]:
        return [self._predict_row(row, self.tree) for row in X]

    def _predict_row(self, row: List[float], node: Optional[Dict[str, Any]]) -> Any:
        if not node:
            return None
        if node["leaf"]:
            return node["value"]
        if row[node["feature"]] <= node["threshold"]:
            return self._predict_row(row, node["left"])
        else:
            return self._predict_row(row, node["right"])


class NativeRandomForest:
    """Zero-dependency Random Forest combining multiple Decision Trees."""

    def __init__(self, n_estimators: int = 5, max_depth: int = 4):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.trees: List[NativeDecisionTree] = []

    def fit(self, X: List[List[float]], y: List[Any]) -> "NativeRandomForest":
        self.trees = []
        n_samples = len(X)
        rng = random.Random(42)
        for _ in range(self.n_estimators):
            # Bootstrap sample
            boot_indices = [rng.randint(0, n_samples - 1) for _ in range(n_samples)]
            boot_X = [X[i] for i in boot_indices]
            boot_y = [y[i] for i in boot_indices]
            dt = NativeDecisionTree(max_depth=self.max_depth)
            dt.fit(boot_X, boot_y)
            self.trees.append(dt)
        return self

    def predict(self, X: List[List[float]]) -> List[Any]:
        all_preds = [tree.predict(X) for tree in self.trees]
        final_preds = []
        for i in range(len(X)):
            sample_preds = [all_preds[t][i] for t in range(len(self.trees))]
            counts = {}
            for sp in sample_preds:
                counts[sp] = counts.get(sp, 0) + 1
            majority = max(counts.items(), key=lambda it: it[1])[0]
            final_preds.append(majority)
        return final_preds


class NativeKMeans:
    """Zero-dependency K-Means Clustering."""

    def __init__(self, k: int = 3, max_iter: int = 100):
        self.k = k
        self.max_iter = max_iter
        self.centroids: List[List[float]] = []

    def fit(self, X: List[List[float]]) -> "NativeKMeans":
        if not X:
            return self
        k = min(self.k, len(X))
        rng = random.Random(42)
        initial_indices = rng.sample(range(len(X)), k)
        self.centroids = [list(X[i]) for i in initial_indices]

        for _ in range(self.max_iter):
            clusters = [[] for _ in range(k)]
            for row in X:
                best_c = min(
                    range(k),
                    key=lambda c: sum((row[f] - self.centroids[c][f]) ** 2 for f in range(len(row))),
                )
                clusters[best_c].append(row)

            new_centroids = []
            for c in range(k):
                if clusters[c]:
                    centroid = [
                        sum(r[f] for r in clusters[c]) / len(clusters[c]) for f in range(len(X[0]))
                    ]
                    new_centroids.append(centroid)
                else:
                    new_centroids.append(self.centroids[c])
            if new_centroids == self.centroids:
                break
            self.centroids = new_centroids
        return self

    def predict(self, X: List[List[float]]) -> List[int]:
        preds = []
        for row in X:
            best_c = min(
                range(len(self.centroids)),
                key=lambda c: sum((row[f] - self.centroids[c][f]) ** 2 for f in range(len(row))),
            )
            preds.append(best_c)
        return preds


# Metrics
def accuracy_score(y_true: List[Any], y_pred: List[Any]) -> float:
    if not y_true:
        return 0.0
    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    return correct / len(y_true)


def mean_squared_error(y_true: List[float], y_pred: List[float]) -> float:
    if not y_true:
        return 0.0
    return sum((yt - yp) ** 2 for yt, yp in zip(y_true, y_pred)) / len(y_true)


def r2_score(y_true: List[float], y_pred: List[float]) -> float:
    if not y_true:
        return 0.0
    mean_y = sum(y_true) / len(y_true)
    ss_tot = sum((yt - mean_y) ** 2 for yt in y_true)
    ss_res = sum((yt - yp) ** 2 for yt, yp in zip(y_true, y_pred))
    return 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 1.0
