"""Permanent regression test suite verifying spoken English .doom syntax
across all 41 registered DoomScript domains.
"""

import pytest
from doomscript.compiler.engine import execute


DOMAIN_SNIPPETS = {
    "agent": """use agent
create agent "researcher" with tools ["search"] into my_agent
tell agent my_agent "hello"
""",
    "astronomy": """use astronomy
calculate julian date for year 2024 month 10 day 20 into jd
""",
    "audio": """use audio
create blank audio of 2 seconds into a
""",
    "automata": """use automata
compile regex "a*b" to dfa into my_dfa
check if dfa my_dfa accepts "aaab" into ok
""",
    "bio": """use bio
calculate gc content of "ACGTGC" into gc
transcribe dna "ACGT" into rna
""",
    "chain": """use chain
create merkle tree from ["tx1", "tx2"] into tree
get merkle root of tree into root
""",
    "chem": """use chem
calculate molecular weight of "H2O" into mw
""",
    "circuit": """use circuit
calculate voltage with current 2 and resistance 5 into v
""",
    "cloud": """use cloud
connect to bucket "my-bucket" into b
""",
    "compiler": """use compiler
assemble bytecode from text "LOAD_CONST 10\\nRETURN" into prog
execute bytecode program prog into res
""",
    "compression": """use compression
compress text "hello world" with huffman into huff
""",
    "data": """use data
items = [{"a": 1}, {"a": 2}]
items where a is greater than 1 into filtered
""",
    "db": """use db
query "sqlite_master" into tables
""",
    "dsa": """use dsa
create segment tree from [1, 2, 3, 4] into seg
""",
    "finance": """use finance
fetch stock prices for "AAPL" into quotes
""",
    "game": """use game
create 2d grid width 10 height 10 into grid
""",
    "geo": """use geo
point at lat 40.7128 and lon -74.006 into pt
""",
    "graph": """use graph
create empty graph into g
add node "A" to graph g
""",
    "graphics": """use graphics
create canvas width 800 height 600 into c
""",
    "image": """use image
create blank image of 100 by 100 into img
""",
    "math3d": """use math3d
create vector3 x 1.0 y 2.0 z 3.0 into v
""",
    "metrics": """use metrics
create counter "api_requests" into cnt
""",
    "ml": """use ml
ds = [{"x": 1.0, "y": 2.0}, {"x": 2.0, "y": 4.0}]
train model on ds predicting y using linear_regression into m
""",
    "net": """use net
format ip 3232235521 into ip_str
""",
    "neuro": """use neuro
create lif neuron with tau 20.0 into n
""",
    "nlp": """use nlp
tokenize text "Hello world this is doom" into tokens
""",
    "office": """use office
create spreadsheet into sheet
""",
    "opt": """use opt
create linear program into lp
""",
    "physics": """use physics
calculate kinetic energy with mass 10 and velocity 5 into ke
""",
    "quantum": """use quantum
create quantum register with 2 qubits into qreg
""",
    "research": """use research
simulate distribution normal with [0.0, 1.0] into dist
""",
    "robotics": """use robotics
solve 2link inverse kinematics with link1 5 and link2 5 for target 3, 4 into ik
""",
    "sec": """use sec
calculate password entropy for "secretPass123!" into ent
""",
    "signals": """use signals
decompose signal [1.0, 2.0, 3.0, 4.0] using haar wavelet into sig_dec
""",
    "sim": """use sim
sample 10 from normal with [0.0, 1.0] into samples
""",
    "spatial_audio": """use spatial_audio
spatialize audio [0.1, 0.2] at azimuth 45 into spat
""",
    "symbolic": """use symbolic
simplify expression "x + x" into simp
""",
    "telecom": """use telecom
calculate crc32 of "hello" into crc
""",
    "time_series": """use time_series
decompose time series [1, 2, 3, 2, 1, 2, 3, 2] with period 4 into ts_dec
""",
    "viz": """use viz
data = [{"x": 1, "y": 2}]
plot data as scatter with {"x": "x", "y": "y"} into p
""",
    "web": """use web
parse html "<html><body><h1>Title</h1></body></html>" into doc
"""
}


@pytest.mark.parametrize("domain_name", sorted(DOMAIN_SNIPPETS.keys()))
def test_domain_spoken_english_execution(domain_name):
    code = DOMAIN_SNIPPETS[domain_name]
    env = execute(code)
    assert env is not None


def test_vspython_deepened_examples_31_to_35():
    # Example 31: Finance
    ex31 = """use finance
calculate analytical greeks for spot 100.0 strike 100.0 expiry 1.0 rate 0.05 vol 0.2 into greeks
calculate binomial price for spot 80.0 strike 100.0 expiry 1.0 rate 0.10 vol 0.2 steps 100 type "put" american into amer_put
"""
    env31 = execute(ex31)
    assert round(env31["greeks"]["delta"], 2) == 0.64
    assert round(env31["amer_put"]["price"], 1) == 20.0

    # Example 32: Zero-Knowledge Cryptography
    ex32 = """use chain
secret_x = 987654321
public_y = chain_schnorr_public_key(secret_x)
prove knowledge of secret secret_x for public public_y into proof
verify proof proof for public public_y into is_valid
"""
    env32 = execute(ex32)
    assert env32["is_valid"] is True

    # Example 33: Quantum Error Correction & Grover
    ex33 = """use quantum
encoded = QuantumErrorCorrection's encode_bit_flip(0.6, 0.8)
corrupted = QuantumErrorCorrection's inject_error(encoded, "X", target_qubit=1)
recovered, error_qubit = QuantumErrorCorrection's detect_and_correct_bit_flip(corrupted)
grover search with 3 qubits for target 6 into search_res
"""
    env33 = execute(ex33)
    assert env33["error_qubit"] == 1
    assert env33["search_res"]["target_probability"] > 0.9

    # Example 34: Web CSS & Cookie Jar
    ex34 = """use web
html_text = "<html><body><div id='main'><ul><li class='active'>Item 1</li></ul></div></body></html>"
select css "div#main ul > li.active" from html html_text into elements
create cookie jar into jar
jar.set_cookie("session=token123; Domain=example.com; Path=/; Secure", "https://example.com/api")
cookie_header = jar.get_cookie_header("https://example.com/api/v1", is_secure=True)
"""
    env34 = execute(ex34)
    assert len(env34["elements"]) > 0
    assert "session=token123" in env34["cookie_header"]

    # Example 35: DB WAL & MVCC Engine
    ex35 = """use db
create wal logger into wal
wal.begin_tx(1)
wal.write_update(1, page_id=10, old_val="A", new_val="B")
wal.commit_tx(1)

create mvcc engine into mvcc
tx1 = mvcc.begin()
tx2 = mvcc.begin()
mvcc.write(tx2, "key", "v2")
mvcc.commit(tx2)
val = mvcc.read(tx1, "key")
"""
    env35 = execute(ex35)
    assert env35["wal"] is not None
    assert env35["val"] is None
