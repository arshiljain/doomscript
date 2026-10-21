import pytest
from doomscript.compiler.engine import execute
from doomscript.exceptions import DoomScriptSyntaxError


def test_did_you_mean_finance_option_suggestion():
    # Missing rate and vol in option pricing phrase
    code = """use finance
price call option with spot 100.0 strike 95.0 expiry 0.5 into call_price
"""
    with pytest.raises(DoomScriptSyntaxError) as exc_info:
        execute(code)
    err_msg = str(exc_info.value)
    assert "Did you mean:" in err_msg
    assert "price" in err_msg
    assert "strike" in err_msg


def test_did_you_mean_ml_classifier_suggestion():
    # Typo / missing parameters in train knn classifier
    code = """use ml
train knn classifier with features X and neighbors 3 into model
"""
    with pytest.raises(DoomScriptSyntaxError) as exc_info:
        execute(code)
    err_msg = str(exc_info.value)
    assert "Did you mean:" in err_msg
    assert "train knn classifier" in err_msg


def test_syntax_error_formatting():
    code = """use sim
simulate markov chain with transitions mat into target
"""
    with pytest.raises(DoomScriptSyntaxError) as exc_info:
        execute(code)
    err_msg = str(exc_info.value)
    assert "Did you mean:" in err_msg
    assert "simulate markov chain" in err_msg
