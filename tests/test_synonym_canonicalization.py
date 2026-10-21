import pytest
from doomscript.grammar.phrases import canonicalize_synonyms
from doomscript.compiler.engine import execute


def test_canonicalize_synonyms_transforms_keywords():
    code = 'calculate f1 score between y_test and y_pred into score'
    result = canonicalize_synonyms(code)
    assert result.startswith('compute f1 score')


def test_canonicalize_synonyms_preserves_strings():
    code = 'say "calculate total price" and calculate 10 + 20'
    result = canonicalize_synonyms(code)
    assert '"calculate total price"' in result
    assert 'compute 10 + 20' in result


def test_canonicalize_synonyms_end_to_end():
    # Both calculate and compute execute identically on geo distance
    code1 = """use geo
calculate haversine distance from 40.7128, -74.0060 to 51.5074, -0.1278 into d1
"""
    code2 = """use geo
compute haversine distance from 40.7128, -74.0060 to 51.5074, -0.1278 into d2
"""
    env1 = execute(code1)
    env2 = execute(code2)
    assert env1["d1"] == env2["d2"]


def test_canonicalize_synonyms_other_verbs():
    assert canonicalize_synonyms("evaluate model accuracy") == "compute model accuracy"
    assert canonicalize_synonyms("construct graph") == "create graph"
    assert canonicalize_synonyms("sort items by score desc") == "sort items by score descending"
    assert canonicalize_synonyms("sort items by score asc") == "sort items by score ascending"
    assert canonicalize_synonyms("forward fill missing values in df") == "forward fill missing in df"
    assert canonicalize_synonyms("preview table customers") == "inspect table customers"
