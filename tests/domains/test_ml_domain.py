"""Unit and integration tests for the Machine Learning domain pack (use ml)."""

import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.ml.spec import ModelSpec
from doomscript.domains.ml.runtime import train_model, evaluate_model, predict_model


def test_model_spec_validation():
    spec = ModelSpec(
        name="churn_model",
        dataset="customers",
        target="churn",
        features=["age", "usage"],
        algorithm="random_forest",
        split_train=0.8,
    )
    errors = spec.validate()
    assert len(errors) == 0

    bad_spec = ModelSpec(name="", dataset="", split_train=1.5)
    bad_errors = bad_spec.validate()
    assert len(bad_errors) >= 3


def test_ml_domain_classification_workflow():
    source = """use ml

customers = [
    {"age": 25, "usage": 10, "churn": 0},
    {"age": 45, "usage": 50, "churn": 1},
    {"age": 22, "usage": 8, "churn": 0},
    {"age": 50, "usage": 60, "churn": 1},
    {"age": 28, "usage": 12, "churn": 0},
    {"age": 42, "usage": 45, "churn": 1}
]

model churn_model from customers:
    target: churn
    features: age, usage
    algorithm: logistic_regression
    split: 70% training, 30% testing

train churn_model
evaluate churn_model into metrics
predict with churn_model on [{"age": 24, "usage": 9}, {"age": 48, "usage": 55}] into preds
inspect model churn_model into model_info
"""
    env = execute(source)
    assert "churn_model" in env
    churn_model = env["churn_model"]
    assert churn_model.is_trained

    # Evaluation
    assert "metrics" in env
    metrics = env["metrics"]
    assert metrics["task_type"] == "classification"
    assert "accuracy" in metrics["metrics"]

    # Prediction
    assert "preds" in env
    preds = env["preds"]
    assert len(preds) == 2
    assert preds[0] == 0
    assert preds[1] == 1

    # Inspection
    assert "model_info" in env
    model_info = env["model_info"]
    assert model_info["name"] == "churn_model"
    assert model_info["features"] == ["age", "usage"]


def test_ml_domain_linear_regression():
    source = """use ml

housing = [
    {"rooms": 1, "sqft": 500, "price": 100000},
    {"rooms": 2, "sqft": 1000, "price": 200000},
    {"rooms": 3, "sqft": 1500, "price": 300000},
    {"rooms": 4, "sqft": 2000, "price": 400000}
]

model price_model from housing:
    target: price
    features: rooms, sqft
    algorithm: linear_regression
    split: 100% training, 0% testing

train price_model
evaluate price_model into eval_res
predict with price_model on [{"rooms": 2.5, "sqft": 1250}] into pred_price
"""
    env = execute(source)
    assert "price_model" in env
    assert env["eval_res"]["task_type"] == "regression"
    assert "rmse" in env["eval_res"]["metrics"]
    assert len(env["pred_price"]) == 1
    # Interpolated price around 250,000
    assert 200000 < env["pred_price"][0] < 300000


def test_ml_ast_export():
    source = """use ml

data = [{"f1": 1, "target": 1}]
model my_model from data:
    target: target
    features: f1
    algorithm: random_forest
"""
    py_code = export_to_python(source)
    assert "RandomForestClassifier" in py_code or "sklearn" in py_code
    assert "my_model" in py_code
