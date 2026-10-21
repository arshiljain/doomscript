import pytest
from doomscript.compiler.engine import execute
from doomscript.exceptions import DoomScriptSyntaxError
from doomscript.compiler.advisor import DidYouMeanAdvisor, extract_known_variables


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


def test_token_level_typo_lenght():
    # Ordinary typo 'lenght' inside a longer line
    code = """words = ["hello", "world"]
say lenght of words
"""
    with pytest.raises(DoomScriptSyntaxError) as exc_info:
        execute(code)
    err_msg = str(exc_info.value)
    assert "Did you mean:" in err_msg
    assert "say length of words" in err_msg


def test_token_level_variable_typo():
    # Typo in a previously assigned variable where parsing fails
    code = """score = 100
set scroe = 100
"""
    with pytest.raises(DoomScriptSyntaxError) as exc_info:
        execute(code)
    err_msg = str(exc_info.value)
    assert "Did you mean:" in err_msg
    assert "score" in err_msg


def test_token_level_keyword_typos():
    # Typos in statement keywords
    code1 = """repeta 5 times:
    say "looping"
"""
    with pytest.raises(DoomScriptSyntaxError) as exc_info1:
        execute(code1)
    err1 = str(exc_info1.value)
    assert "Did you mean:" in err1
    assert "repeat 5 times:" in err1

    code2 = """whlie count > 0:
    count -= 1
"""
    with pytest.raises(DoomScriptSyntaxError) as exc_info2:
        execute(code2)
    err2 = str(exc_info2.value)
    assert "Did you mean:" in err2
    assert "while count > 0:" in err2
