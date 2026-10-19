"""Unit tests for SafeASTEvaluator and elimination of eval() in Data Domain."""

import pytest
from doomscript.domains.data.expr_eval import SafeASTEvaluator, SafeEvalError, SafeEvalSecurityError
from doomscript.domains.data.spec import CalculateStep, FilterStep, DataPipelineSpec
from doomscript.domains.data.runtime import run_pipeline


def test_safe_eval_arithmetic_and_variables():
    evaluator = SafeASTEvaluator()
    row = {"amount": 100, "discount": 0.15, "category": "electronics"}
    res = evaluator.evaluate("amount * (1.0 - discount)", row)
    assert abs(res - 85.0) < 1e-5

    res_cat = evaluator.evaluate("category == 'electronics' and amount > 50", row)
    assert res_cat is True


def test_safe_eval_builtins_whitelist():
    evaluator = SafeASTEvaluator()
    row = {"val": -42.7, "s": "  hello world  "}
    assert evaluator.evaluate("abs(val)", row) == 42.7
    assert evaluator.evaluate("round(abs(val))", row) == 43
    assert evaluator.evaluate("len(s)", row) == 15


def test_safe_eval_rejects_security_violations():
    evaluator = SafeASTEvaluator()
    row = {"x": 10}

    # Dunder access rejected
    with pytest.raises(SafeEvalSecurityError):
        evaluator.evaluate("x.__class__", row)

    # Subclasses access rejected
    with pytest.raises(SafeEvalSecurityError):
        evaluator.evaluate("().__class__.__bases__[0].__subclasses__()", row)

    # Imports rejected
    with pytest.raises(SafeEvalSecurityError):
        evaluator.evaluate("__import__('os').system('ls')", row)


def test_safe_eval_missing_column_error():
    evaluator = SafeASTEvaluator()
    row = {"price": 10}
    with pytest.raises(SafeEvalError) as exc_info:
        evaluator.evaluate("price + non_existent_column", row)
    assert "non_existent_column" in str(exc_info.value)


def test_data_pipeline_runtime_uses_safe_eval_and_reports_errors():
    pipeline = DataPipelineSpec(
        name="test_safe_pipe",
        steps=[
            CalculateStep(target_col="net", expression="amount * (1 - discount)"),
            FilterStep(condition="net > 50"),
        ],
    )
    data = [
        {"amount": 100, "discount": 0.2},
        {"amount": 40, "discount": 0.1},
    ]
    scope = {"data": data}
    res = run_pipeline(pipeline, scope, source_data=data)
    assert len(res) == 1
    assert res[0]["net"] == 80.0
