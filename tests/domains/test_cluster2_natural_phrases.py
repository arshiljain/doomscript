"""Tests for Cluster 2 (Data, Math & AI) natural English phrases:
data, ml, nlp, research, math3d, opt, symbolic, viz
"""

from doomscript.compiler.engine import execute


def test_cluster2_ml_and_data(capsys):
    code = """
use ml
dataset = [{"x": 1, "y": 10}, {"x": 2, "y": 20}, {"x": 3, "y": 30}, {"x": 4, "y": 40}]
split dataset dataset into train and test with test size 0.25 into split_data
say count of split_data.train >= 2

use data
piv_data = [{"dept": "eng", "quarter": "Q1", "cost": 100}, {"dept": "eng", "quarter": "Q2", "cost": 150}]
pivot dataset piv_data on index "dept" columns "quarter" values "cost" into piv_table
say count of piv_table > 0
"""
    execute(code)
    out = capsys.readouterr().out.strip().splitlines()
    assert out[0] == "True"
    assert out[1] == "True"


def test_cluster2_nlp_research_math3d_opt(capsys):
    code = """
use nlp
corpus = ["hello world", "doomscript natural english", "test language"]
train bpe tokenizer on corpus with vocab size 50 into bpe
say count of bpe.vocab > 0

use research
mat = [[1.0, 0.0], [0.0, 2.0]]
compute svd of mat into svd_res
say count of svd_res.singular_values == 2

use math3d
create quaternion from euler pitch 0.0 yaw 90.0 roll 0.0 into q
say q.w > 0
create vector3 x 0.0 y 2.0 z 0.0 into v
calculate sdf sphere at v with radius 1.0 into dist
say dist > 0

use opt
cost_mat = [[4.0, 2.0], [3.0, 1.0]]
solve assignment problem with cost matrix cost_mat into assign_res
say assign_res.total_cost > 0
"""
    execute(code)
    out = capsys.readouterr().out.strip().splitlines()
    assert out[0] == "True"
    assert out[1] == "True"
    assert out[2] == "True"
    assert out[3] == "True"
    assert out[4] == "True"
