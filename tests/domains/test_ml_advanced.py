"""Unit and integration tests for advanced ML capabilities:
preprocessing, reproducible split seeds, cross validation, persistence, and export parity.
"""

import os
import pytest
from doomscript.compiler.engine import execute, export_to_python


def test_ml_reproducible_split_seed_and_preprocessing():
    source = """use ml

customers = [
    {"age": 20, "income": 20000, "churn": 0},
    {"age": 30, "income": 35000, "churn": 0},
    {"age": 40, "income": 50000, "churn": 1},
    {"age": 50, "income": 70000, "churn": 1},
    {"age": 60, "income": 90000, "churn": 1},
    {"age": 25, "income": 25000, "churn": 0}
]

model risk_model from customers:
    target: churn
    features: age, income
    scale: age, income
    algorithm: logistic_regression
    split: 70% training, 30% testing with seed 123

train risk_model
evaluate risk_model into ev
"""
    env = execute(source)
    model = env["risk_model"]
    assert model.spec.seed == 123
    assert model.spec.scale_features == ["age", "income"]
    assert model.is_trained
    assert "accuracy" in env["ev"]


def test_ml_cross_validation():
    source = """use ml

data = [
    {"x": 1.0, "y": 2.0},
    {"x": 2.0, "y": 4.0},
    {"x": 3.0, "y": 6.0},
    {"x": 4.0, "y": 8.0},
    {"x": 5.0, "y": 10.0},
    {"x": 6.0, "y": 12.0}
]

model reg from data:
    target: y
    features: x
    algorithm: linear_regression

cross validate reg with 3 folds into cv_res
"""
    env = execute(source)
    assert "cv_res" in env
    cv_res = env["cv_res"]
    assert cv_res["folds"] == 3
    assert len(cv_res["scores"]) == 3
    assert "mean_score" in cv_res


def test_ml_model_persistence(tmp_path):
    model_path = str(tmp_path / "model.pkl").replace("\\", "/")
    source = f"""use ml

data = [
    {{"f1": 1, "f2": 2, "target": 0}},
    {{"f1": 2, "f2": 3, "target": 0}},
    {{"f1": 10, "f2": 20, "target": 1}},
    {{"f1": 12, "f2": 22, "target": 1}}
]

model m from data:
    target: target
    features: f1, f2
    algorithm: logistic_regression

train m
save model m to "{model_path}"
load model from "{model_path}" into loaded_m
predict with loaded_m on [{{"f1": 11, "f2": 21}}] into preds
"""
    env = execute(source)
    assert os.path.exists(model_path)
    assert "loaded_m" in env
    assert env["preds"] == [1]


def test_ml_python_export():
    source = """use ml

customers = [
    {"age": 20, "usage": 10, "churn": 0},
    {"age": 40, "usage": 50, "churn": 1}
]

model churn_model from customers:
    target: churn
    features: age, usage
    scale: age, usage
    algorithm: logistic_regression
    split: 80% training, 20% testing with seed 42
"""
    py_code = export_to_python(source)
    assert "LogisticRegression" in py_code
    assert "random_state=42" in py_code
    assert "StandardScaler" in py_code
    assert ".fit_transform" in py_code
