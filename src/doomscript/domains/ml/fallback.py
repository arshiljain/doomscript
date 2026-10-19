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


# =========================================================================
# Deepened Machine Learning Algorithms (Zero External Dependencies)
# =========================================================================

class MLPClassifier:
    """Zero-dependency Multi-Layer Perceptron Classifier with Adam/SGD backpropagation."""

    def __init__(
        self,
        hidden_layer_sizes: Tuple[int, ...] = (16,),
        lr: float = 0.01,
        max_iter: int = 200,
        batch_size: int = 32,
        random_state: int = 42,
    ):
        self.hidden_sizes = list(hidden_layer_sizes)
        self.lr = lr
        self.max_iter = max_iter
        self.batch_size = batch_size
        self.random_state = random_state
        self.classes: List[Any] = []
        self.weights: List[List[List[float]]] = []
        self.biases: List[List[float]] = []

    def fit(self, X: List[List[float]], y: List[Any]) -> "MLPClassifier":
        if not X or not y:
            return self
        self.classes = sorted(list(set(y)))
        n_samples = len(X)
        n_features = len(X[0])
        n_classes = len(self.classes)
        rng = random.Random(self.random_state)

        layer_dims = [n_features] + self.hidden_sizes + [n_classes if n_classes > 2 else 1]

        # Xavier initialization
        self.weights = []
        self.biases = []
        for i in range(len(layer_dims) - 1):
            fan_in = layer_dims[i]
            fan_out = layer_dims[i + 1]
            limit = math.sqrt(6.0 / (fan_in + fan_out))
            w = [[rng.uniform(-limit, limit) for _ in range(fan_out)] for _ in range(fan_in)]
            b = [0.0] * fan_out
            self.weights.append(w)
            self.biases.append(b)

        # One-hot or binary target
        if n_classes == 2:
            y_targets = [[1.0] if yi == self.classes[1] else [0.0] for yi in y]
        else:
            y_targets = []
            for yi in y:
                target_vec = [0.0] * n_classes
                target_vec[self.classes.index(yi)] = 1.0
                y_targets.append(target_vec)

        # Adam optimizer state
        m_w = [[[0.0] * len(w[0]) for _ in range(len(w))] for w in self.weights]
        v_w = [[[0.0] * len(w[0]) for _ in range(len(w))] for w in self.weights]
        m_b = [[0.0] * len(b) for b in self.biases]
        v_b = [[0.0] * len(b) for b in self.biases]
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        t = 0

        # Optimization loop
        for epoch in range(self.max_iter):
            indices = list(range(n_samples))
            rng.shuffle(indices)

            for b_start in range(0, n_samples, self.batch_size):
                b_indices = indices[b_start : b_start + self.batch_size]
                if not b_indices:
                    continue
                t += 1

                # Accumulate gradients
                grad_w = [[[0.0] * len(w[0]) for _ in range(len(w))] for w in self.weights]
                grad_b = [[0.0] * len(b) for b in self.biases]

                for idx in b_indices:
                    x_i = X[idx]
                    y_i = y_targets[idx]

                    # Forward pass
                    activations = [x_i]
                    zs = []
                    cur = x_i
                    for l_idx in range(len(self.weights)):
                        w = self.weights[l_idx]
                        b = self.biases[l_idx]
                        z = [sum(cur[k] * w[k][j] for k in range(len(cur))) + b[j] for j in range(len(b))]
                        zs.append(z)
                        if l_idx == len(self.weights) - 1:
                            if n_classes == 2:
                                a = [1.0 / (1.0 + math.exp(-max(-20.0, min(20.0, z[0]))))]
                            else:
                                max_z = max(z)
                                exp_z = [math.exp(val - max_z) for val in z]
                                sum_exp = sum(exp_z) or 1.0
                                a = [val / sum_exp for val in exp_z]
                        else:
                            a = [max(0.0, val) for val in z]  # ReLU
                        cur = a
                        activations.append(a)

                    # Backward pass
                    delta = [a - y for a, y in zip(activations[-1], y_i)]
                    for l_idx in reversed(range(len(self.weights))):
                        a_prev = activations[l_idx]
                        w = self.weights[l_idx]
                        for k in range(len(a_prev)):
                            for j in range(len(delta)):
                                grad_w[l_idx][k][j] += a_prev[k] * delta[j]
                        for j in range(len(delta)):
                            grad_b[l_idx][j] += delta[j]

                        if l_idx > 0:
                            # Propagate delta back through ReLU
                            z_prev = zs[l_idx - 1]
                            new_delta = [0.0] * len(z_prev)
                            for k in range(len(z_prev)):
                                s = sum(w[k][j] * delta[j] for j in range(len(delta)))
                                new_delta[k] = s if z_prev[k] > 0 else 0.0
                            delta = new_delta

                batch_len = len(b_indices)
                # Apply Adam updates
                for l_idx in range(len(self.weights)):
                    for k in range(len(self.weights[l_idx])):
                        for j in range(len(self.weights[l_idx][k])):
                            g = grad_w[l_idx][k][j] / batch_len
                            m_w[l_idx][k][j] = beta1 * m_w[l_idx][k][j] + (1 - beta1) * g
                            v_w[l_idx][k][j] = beta2 * v_w[l_idx][k][j] + (1 - beta2) * (g * g)
                            m_hat = m_w[l_idx][k][j] / (1 - beta1 ** t)
                            v_hat = v_w[l_idx][k][j] / (1 - beta2 ** t)
                            self.weights[l_idx][k][j] -= self.lr * m_hat / (math.sqrt(v_hat) + eps)

                    for j in range(len(self.biases[l_idx])):
                        g = grad_b[l_idx][j] / batch_len
                        m_b[l_idx][j] = beta1 * m_b[l_idx][j] + (1 - beta1) * g
                        v_b[l_idx][j] = beta2 * v_b[l_idx][j] + (1 - beta2) * (g * g)
                        m_hat = m_b[l_idx][j] / (1 - beta1 ** t)
                        v_hat = v_b[l_idx][j] / (1 - beta2 ** t)
                        self.biases[l_idx][j] -= self.lr * m_hat / (math.sqrt(v_hat) + eps)

        return self

    def predict_proba(self, X: List[List[float]]) -> List[List[float]]:
        probas = []
        n_classes = len(self.classes)
        for x_i in X:
            cur = x_i
            for l_idx in range(len(self.weights)):
                w = self.weights[l_idx]
                b = self.biases[l_idx]
                z = [sum(cur[k] * w[k][j] for k in range(len(cur))) + b[j] for j in range(len(b))]
                if l_idx == len(self.weights) - 1:
                    if n_classes == 2:
                        p1 = 1.0 / (1.0 + math.exp(-max(-20.0, min(20.0, z[0]))))
                        cur = [1.0 - p1, p1]
                    else:
                        max_z = max(z)
                        exp_z = [math.exp(val - max_z) for val in z]
                        sum_exp = sum(exp_z) or 1.0
                        cur = [val / sum_exp for val in exp_z]
                else:
                    cur = [max(0.0, val) for val in z]
            probas.append(cur)
        return probas

    def predict(self, X: List[List[float]]) -> List[Any]:
        if not self.classes:
            return [None] * len(X)
        probas = self.predict_proba(X)
        preds = []
        for p in probas:
            best_idx = max(range(len(p)), key=lambda i: p[i])
            preds.append(self.classes[best_idx])
        return preds


class MLPRegressor:
    """Zero-dependency Multi-Layer Perceptron Regressor with Adam backpropagation."""

    def __init__(
        self,
        hidden_layer_sizes: Tuple[int, ...] = (16,),
        lr: float = 0.01,
        max_iter: int = 200,
        batch_size: int = 32,
        random_state: int = 42,
    ):
        self.hidden_sizes = list(hidden_layer_sizes)
        self.lr = lr
        self.max_iter = max_iter
        self.batch_size = batch_size
        self.random_state = random_state
        self.weights: List[List[List[float]]] = []
        self.biases: List[List[float]] = []

    def fit(self, X: List[List[float]], y: List[float]) -> "MLPRegressor":
        if not X or not y:
            return self
        n_samples = len(X)
        n_features = len(X[0])
        rng = random.Random(self.random_state)

        # Standardize target for numeric stability
        self.y_mean = sum(y) / n_samples
        self.y_std = math.sqrt(sum((val - self.y_mean) ** 2 for val in y) / n_samples) or 1.0
        y_scaled = [(val - self.y_mean) / self.y_std for val in y]

        layer_dims = [n_features] + self.hidden_sizes + [1]
        self.weights = []
        self.biases = []
        for i in range(len(layer_dims) - 1):
            fan_in = layer_dims[i]
            fan_out = layer_dims[i + 1]
            limit = math.sqrt(6.0 / (fan_in + fan_out))
            w = [[rng.uniform(-limit, limit) for _ in range(fan_out)] for _ in range(fan_in)]
            b = [0.0] * fan_out
            self.weights.append(w)
            self.biases.append(b)

        m_w = [[[0.0] * len(w[0]) for _ in range(len(w))] for w in self.weights]
        v_w = [[[0.0] * len(w[0]) for _ in range(len(w))] for w in self.weights]
        m_b = [[0.0] * len(b) for b in self.biases]
        v_b = [[0.0] * len(b) for b in self.biases]
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        t = 0

        for epoch in range(self.max_iter):
            indices = list(range(n_samples))
            rng.shuffle(indices)

            for b_start in range(0, n_samples, self.batch_size):
                b_indices = indices[b_start : b_start + self.batch_size]
                if not b_indices:
                    continue
                t += 1

                grad_w = [[[0.0] * len(w[0]) for _ in range(len(w))] for w in self.weights]
                grad_b = [[0.0] * len(b) for b in self.biases]

                for idx in b_indices:
                    x_i = X[idx]
                    y_i = y_scaled[idx]

                    activations = [x_i]
                    zs = []
                    cur = x_i
                    for l_idx in range(len(self.weights)):
                        w = self.weights[l_idx]
                        b = self.biases[l_idx]
                        z = [sum(cur[k] * w[k][j] for k in range(len(cur))) + b[j] for j in range(len(b))]
                        zs.append(z)
                        a = z if l_idx == len(self.weights) - 1 else [max(0.0, val) for val in z]
                        cur = a
                        activations.append(a)

                    delta = [activations[-1][0] - y_i]
                    for l_idx in reversed(range(len(self.weights))):
                        a_prev = activations[l_idx]
                        w = self.weights[l_idx]
                        for k in range(len(a_prev)):
                            for j in range(len(delta)):
                                grad_w[l_idx][k][j] += a_prev[k] * delta[j]
                        for j in range(len(delta)):
                            grad_b[l_idx][j] += delta[j]

                        if l_idx > 0:
                            z_prev = zs[l_idx - 1]
                            new_delta = [0.0] * len(z_prev)
                            for k in range(len(z_prev)):
                                s = sum(w[k][j] * delta[j] for j in range(len(delta)))
                                new_delta[k] = s if z_prev[k] > 0 else 0.0
                            delta = new_delta

                batch_len = len(b_indices)
                for l_idx in range(len(self.weights)):
                    for k in range(len(self.weights[l_idx])):
                        for j in range(len(self.weights[l_idx][k])):
                            g = grad_w[l_idx][k][j] / batch_len
                            m_w[l_idx][k][j] = beta1 * m_w[l_idx][k][j] + (1 - beta1) * g
                            v_w[l_idx][k][j] = beta2 * v_w[l_idx][k][j] + (1 - beta2) * (g * g)
                            m_hat = m_w[l_idx][k][j] / (1 - beta1 ** t)
                            v_hat = v_w[l_idx][k][j] / (1 - beta2 ** t)
                            self.weights[l_idx][k][j] -= self.lr * m_hat / (math.sqrt(v_hat) + eps)

                    for j in range(len(self.biases[l_idx])):
                        g = grad_b[l_idx][j] / batch_len
                        m_b[l_idx][j] = beta1 * m_b[l_idx][j] + (1 - beta1) * g
                        v_b[l_idx][j] = beta2 * v_b[l_idx][j] + (1 - beta2) * (g * g)
                        m_hat = m_b[l_idx][j] / (1 - beta1 ** t)
                        v_hat = v_b[l_idx][j] / (1 - beta2 ** t)
                        self.biases[l_idx][j] -= self.lr * m_hat / (math.sqrt(v_hat) + eps)

        return self

    def predict(self, X: List[List[float]]) -> List[float]:
        preds = []
        for x_i in X:
            cur = x_i
            for l_idx in range(len(self.weights)):
                w = self.weights[l_idx]
                b = self.biases[l_idx]
                z = [sum(cur[k] * w[k][j] for k in range(len(cur))) + b[j] for j in range(len(b))]
                cur = z if l_idx == len(self.weights) - 1 else [max(0.0, val) for val in z]
            unscaled = (cur[0] * self.y_std) + self.y_mean
            preds.append(round(unscaled, 4))
        return preds


class CARTDecisionTree:
    """Zero-dependency CART Decision Tree supporting both Classification (Gini) and Regression (MSE)."""

    def __init__(
        self,
        is_classifier: bool = True,
        max_depth: int = 5,
        min_samples_split: int = 2,
        min_samples_leaf: int = 1,
    ):
        self.is_classifier = is_classifier
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.root: Optional[Dict[str, Any]] = None
        self.feature_importances_: List[float] = []

    def fit(self, X: List[List[float]], y: List[Any]) -> "CARTDecisionTree":
        if not X or not y:
            return self
        n_features = len(X[0])
        self.feature_importances_ = [0.0] * n_features
        self.root = self._grow_tree(X, y, depth=0)
        # Normalize feature importances
        tot_imp = sum(self.feature_importances_)
        if tot_imp > 0:
            self.feature_importances_ = [round(imp / tot_imp, 4) for imp in self.feature_importances_]
        return self

    def _grow_tree(self, X: List[List[float]], y: List[Any], depth: int) -> Dict[str, Any]:
        n_samples = len(y)
        if self.is_classifier:
            counts = {}
            for yi in y:
                counts[yi] = counts.get(yi, 0) + 1
            leaf_val = max(counts.items(), key=lambda it: it[1])[0]
            if len(counts) == 1 or depth >= self.max_depth or n_samples < self.min_samples_split:
                return {"leaf": True, "value": leaf_val}
            base_impurity = self._gini(y)
        else:
            leaf_val = sum(y) / n_samples
            if depth >= self.max_depth or n_samples < self.min_samples_split:
                return {"leaf": True, "value": leaf_val}
            base_impurity = self._variance(y)

        best_gain = 0.0
        best_criteria = None
        best_splits = None

        n_features = len(X[0])
        for feat_idx in range(n_features):
            vals = sorted(list(set(row[feat_idx] for row in X)))
            if len(vals) < 2:
                continue
            for i in range(len(vals) - 1):
                thresh = (vals[i] + vals[i + 1]) / 2.0
                left_X, left_y, right_X, right_y = [], [], [], []
                for row, yi in zip(X, y):
                    if row[feat_idx] <= thresh:
                        left_X.append(row)
                        left_y.append(yi)
                    else:
                        right_X.append(row)
                        right_y.append(yi)

                if len(left_y) < self.min_samples_leaf or len(right_y) < self.min_samples_leaf:
                    continue

                p_left = len(left_y) / n_samples
                if self.is_classifier:
                    child_imp = p_left * self._gini(left_y) + (1.0 - p_left) * self._gini(right_y)
                else:
                    child_imp = p_left * self._variance(left_y) + (1.0 - p_left) * self._variance(right_y)

                gain = base_impurity - child_imp
                if gain > best_gain:
                    best_gain = gain
                    best_criteria = (feat_idx, thresh)
                    best_splits = (left_X, left_y, right_X, right_y)

        if best_gain <= 0.0 or best_criteria is None:
            return {"leaf": True, "value": leaf_val}

        self.feature_importances_[best_criteria[0]] += best_gain * n_samples
        left_node = self._grow_tree(best_splits[0], best_splits[1], depth + 1)
        right_node = self._grow_tree(best_splits[2], best_splits[3], depth + 1)

        return {
            "leaf": False,
            "feature": best_criteria[0],
            "threshold": best_criteria[1],
            "left": left_node,
            "right": right_node,
            "value": leaf_val,
        }

    def _gini(self, y: List[Any]) -> float:
        n = len(y)
        counts = {}
        for yi in y:
            counts[yi] = counts.get(yi, 0) + 1
        return 1.0 - sum((cnt / n) ** 2 for cnt in counts.values())

    def _variance(self, y: List[float]) -> float:
        n = len(y)
        if n < 2:
            return 0.0
        m = sum(y) / n
        return sum((val - m) ** 2 for val in y) / n

    def predict(self, X: List[List[float]]) -> List[Any]:
        return [self._predict_sample(row, self.root) for row in X]

    def _predict_sample(self, row: List[float], node: Optional[Dict[str, Any]]) -> Any:
        if not node:
            return None
        if node["leaf"]:
            return node["value"]
        if row[node["feature"]] <= node["threshold"]:
            return self._predict_sample(row, node["left"])
        return self._predict_sample(row, node["right"])


class GBDTModel:
    """Zero-dependency Gradient Boosted Decision Trees for Classification and Regression."""

    def __init__(
        self,
        is_classifier: bool = False,
        n_estimators: int = 10,
        learning_rate: float = 0.1,
        max_depth: int = 3,
        random_state: int = 42,
    ):
        self.is_classifier = is_classifier
        self.n_estimators = n_estimators
        self.lr = learning_rate
        self.max_depth = max_depth
        self.random_state = random_state
        self.trees: List[CARTDecisionTree] = []
        self.base_pred: float = 0.0
        self.classes: List[Any] = []

    def fit(self, X: List[List[float]], y: List[Any]) -> "GBDTModel":
        if not X or not y:
            return self
        n = len(y)
        self.trees = []

        if self.is_classifier:
            self.classes = sorted(list(set(y)))
            pos_class = self.classes[1] if len(self.classes) > 1 else self.classes[0]
            y_num = [1.0 if yi == pos_class else 0.0 for yi in y]
            p0 = sum(y_num) / n
            p0 = max(0.001, min(0.999, p0))
            self.base_pred = math.log(p0 / (1.0 - p0))

            f_cur = [self.base_pred] * n
            for _ in range(self.n_estimators):
                # Gradient of binary cross-entropy with log-odds
                probs = [1.0 / (1.0 + math.exp(-max(-20.0, min(20.0, val)))) for val in f_cur]
                residuals = [yi - pi for yi, pi in zip(y_num, probs)]
                tree = CARTDecisionTree(is_classifier=False, max_depth=self.max_depth)
                tree.fit(X, residuals)
                self.trees.append(tree)
                preds = tree.predict(X)
                f_cur = [f + self.lr * p for f, p in zip(f_cur, preds)]
        else:
            self.base_pred = sum(y) / n
            f_cur = [self.base_pred] * n
            for _ in range(self.n_estimators):
                residuals = [yi - fi for yi, fi in zip(y, f_cur)]
                tree = CARTDecisionTree(is_classifier=False, max_depth=self.max_depth)
                tree.fit(X, residuals)
                self.trees.append(tree)
                preds = tree.predict(X)
                f_cur = [f + self.lr * p for f, p in zip(f_cur, preds)]

        return self

    def predict(self, X: List[List[float]]) -> List[Any]:
        n = len(X)
        f_cur = [self.base_pred] * n
        for tree in self.trees:
            preds = tree.predict(X)
            f_cur = [f + self.lr * p for f, p in zip(f_cur, preds)]

        if self.is_classifier:
            pos_class = self.classes[1] if len(self.classes) > 1 else self.classes[0]
            neg_class = self.classes[0]
            final = []
            for val in f_cur:
                prob = 1.0 / (1.0 + math.exp(-max(-20.0, min(20.0, val))))
                final.append(pos_class if prob >= 0.5 else neg_class)
            return final
        return [round(f, 4) for f in f_cur]


class IsolationForestModel:
    """Zero-dependency Isolation Forest for Unsupervised Anomaly Detection."""

    def __init__(
        self,
        n_estimators: int = 50,
        max_samples: int = 256,
        contamination: float = 0.1,
        random_state: int = 42,
    ):
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.contamination = contamination
        self.random_state = random_state
        self.trees: List[Dict[str, Any]] = []

    def fit(self, X: List[List[float]]) -> "IsolationForestModel":
        if not X:
            return self
        rng = random.Random(self.random_state)
        n_samples = len(X)
        sub_size = min(self.max_samples, n_samples)
        max_depth = int(math.ceil(math.log2(max(2, sub_size))))

        self.trees = []
        for _ in range(self.n_estimators):
            sample_indices = rng.sample(range(n_samples), sub_size)
            sub_X = [X[i] for i in sample_indices]
            tree = self._build_i_tree(sub_X, depth=0, max_depth=max_depth, rng=rng)
            self.trees.append(tree)

        return self

    def _build_i_tree(
        self, X: List[List[float]], depth: int, max_depth: int, rng: random.Random
    ) -> Dict[str, Any]:
        if depth >= max_depth or len(X) <= 1:
            return {"leaf": True, "size": len(X)}

        n_features = len(X[0])
        feat_idx = rng.randint(0, n_features - 1)
        vals = [row[feat_idx] for row in X]
        min_v = min(vals)
        max_v = max(vals)

        if min_v == max_v:
            return {"leaf": True, "size": len(X)}

        split_v = rng.uniform(min_v, max_v)
        left_X = [row for row in X if row[feat_idx] < split_v]
        right_X = [row for row in X if row[feat_idx] >= split_v]

        return {
            "leaf": False,
            "feature": feat_idx,
            "split": split_v,
            "left": self._build_i_tree(left_X, depth + 1, max_depth, rng),
            "right": self._build_i_tree(right_X, depth + 1, max_depth, rng),
        }

    def _path_length(self, row: List[float], node: Dict[str, Any], current_depth: int) -> float:
        if node["leaf"]:
            size = node["size"]
            return current_depth + self._c(size)
        if row[node["feature"]] < node["split"]:
            return self._path_length(row, node["left"], current_depth + 1)
        return self._path_length(row, node["right"], current_depth + 1)

    @staticmethod
    def _c(n: int) -> float:
        if n <= 1:
            return 0.0
        if n == 2:
            return 1.0
        # Euler-Mascheroni constant = 0.5772156649
        return 2.0 * (math.log(n - 1) + 0.5772156649) - (2.0 * (n - 1) / n)

    def decision_function(self, X: List[List[float]]) -> List[float]:
        """Anomaly scores between 0.0 and 1.0 (higher = more anomalous)."""
        if not self.trees:
            return [0.0] * len(X)
        n = min(self.max_samples, len(X))
        c_n = self._c(n)
        scores = []
        for row in X:
            mean_h = sum(self._path_length(row, t, 0) for t in self.trees) / len(self.trees)
            score = 2.0 ** (-mean_h / c_n) if c_n > 0 else 0.5
            scores.append(round(score, 4))
        return scores

    def predict(self, X: List[List[float]]) -> List[int]:
        """Returns -1 for anomaly and 1 for normal."""
        scores = self.decision_function(X)
        threshold = 1.0 - self.contamination
        return [-1 if s >= threshold else 1 for s in scores]

