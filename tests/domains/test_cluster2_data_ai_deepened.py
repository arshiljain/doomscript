"""Comprehensive test suite verifying natural spoken English phrasings and declarative blocks
for all 8 domains in Cluster 2: Data, Math & AI
(data, ml, nlp, research, math3d, opt, symbolic, viz)
"""

import pytest
from doomscript.compiler.engine import execute


def test_data_natural_phrases():
    code = """
use data

piv_data = [{"dept": "eng", "quarter": "Q1", "cost": 100}, {"dept": "eng", "quarter": "Q2", "cost": 150}]
pivot dataset piv_data on index "dept" columns "quarter" values "cost" into piv_table
say count of piv_table > 0

users = [{"id": 1, "name": "Alice"}, {"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
clean users by removing duplicates by "id" into deduped
say count of deduped == 2
"""
    res = execute(code)
    assert len(res.get("piv_table")) > 0
    assert len(res.get("deduped")) == 2


def test_ml_natural_phrases_and_blocks():
    code = """
use ml

dataset = [{"size": 100, "price": 200}, {"size": 200, "price": 400}, {"size": 300, "price": 600}]

# Natural Level 2 verb
train regression model on dataset with target "price" into reg_model
say reg_model.is_trained

# Level 3 declarative model block
model house_model from dataset:
    target: "price"
    algorithm: regression

train house_model
say house_model.is_trained
"""
    res = execute(code)
    assert res.get("reg_model").is_trained is True
    assert res.get("house_model").is_trained is True


def test_nlp_natural_phrases():
    code = """
use nlp

corpus = ["hello world", "doomscript natural english", "test language"]
train bpe tokenizer on corpus with vocab size 50 into bpe
say count of bpe.vocab > 0

sentiment of "This new language feature is wonderful and amazing!" into sent
say sent["compound"] > 0
"""
    res = execute(code)
    assert len(res.get("bpe").vocab) > 0
    assert res.get("sent")["compound"] > 0


def test_research_natural_phrases():
    code = """
use research

mat = [[1.0, 0.0], [0.0, 2.0]]
compute svd of mat into svd_res
say count of svd_res.singular_values == 2
"""
    res = execute(code)
    assert len(res.get("svd_res")["singular_values"]) == 2


def test_math3d_natural_phrases():
    code = """
use math3d

create quaternion from euler pitch 0.0 yaw 90.0 roll 0.0 into q
say q.w > 0

create vector3 x 0.0 y 2.0 z 0.0 into v
calculate sdf sphere at v with radius 1.0 into dist
say dist > 0
"""
    res = execute(code)
    assert res.get("q").w > 0
    assert res.get("dist") > 0


def test_opt_natural_phrases():
    code = """
use opt

cost_mat = [[4.0, 2.0], [3.0, 1.0]]
solve assignment problem with cost matrix cost_mat into assign_res
say assign_res.total_cost > 0
"""
    res = execute(code)
    assert res.get("assign_res")["total_cost"] > 0


def test_symbolic_natural_phrases():
    code = """
use symbolic

differentiate "x^3 + 2*x" with respect to x into deriv
say deriv is not None

expand taylor series for "sin(x)" var x center 0.0 order 4 into taylor
say taylor is not None
"""
    res = execute(code)
    assert res.get("deriv") is not None
    assert res.get("taylor") is not None


def test_viz_natural_phrases():
    code = """
use viz

render ascii boxplot for data [1, 2, 5, 8, 12, 15, 20] into bplot
say bplot is not empty

render ascii bar chart labels ["A", "B", "C"] values [10, 25, 15] into bchart
say bchart is not empty
"""
    res = execute(code)
    assert len(res.get("bplot")) > 0
    assert len(res.get("bchart")) > 0
