"""Comprehensive test suite verifying natural spoken English phrasings
for all 8 domains in Cluster 3: Computing, Algorithms & Systems
(compiler, compression, automata, dsa, graph, net, sec, cloud)
"""

import pytest
from doomscript.compiler.engine import execute


def test_compiler_natural_phrases():
    code = """
use compiler

bytecode_text = "LOAD_CONST 10\\nLOAD_CONST 20\\nADD\\nRETURN"
assemble bytecode from text bytecode_text into prog
execute bytecode program prog into res
say res.result == 30
"""
    res = execute(code)
    assert res.get("res")["result"] == 30


def test_compression_natural_phrases():
    code = """
use compression

compress "hello world from doomscript" with huffman into huff
decompress huffman huff into restored
say restored == "hello world from doomscript"

calculate entropy of "aabbccddeeff" into ent
say ent > 0.0
"""
    res = execute(code)
    assert res.get("restored") == "hello world from doomscript"
    assert res.get("ent") > 0.0


def test_automata_natural_phrases():
    code = """
use automata

compile regex "a*b" to dfa into my_dfa
check if dfa my_dfa accepts "aaab" into ok
say ok == True

check if dfa my_dfa accepts "aaa" into not_ok
say not_ok == False
"""
    res = execute(code)
    assert res.get("ok") is True
    assert res.get("not_ok") is False


def test_dsa_natural_phrases():
    code = """
use dsa

create segment tree from [1, 2, 3, 4, 5] into seg
say seg is not None

create trie from ["hello", "world"] into t
say t is not None
"""
    res = execute(code)
    assert res.get("seg") is not None
    assert res.get("t") is not None


def test_graph_natural_phrases():
    code = """
use graph

create empty graph into g
add node "A" to graph g
add node "B" to graph g
add edge from "A" to "B" with weight 2.5 in graph g
shortest path from "A" to "B" in graph g into p
say p is not None
"""
    res = execute(code)
    assert res.get("p") is not None


def test_net_natural_phrases():
    code = """
use net

create cidr prefix trie into trie
say trie is not None
"""
    res = execute(code)
    assert res.get("trie") is not None


def test_sec_natural_phrases():
    code = """
use sec

encrypt "hello" with caesar cipher shift 3 into encrypted
say encrypted == "khoor"

verify jwt "invalid.token" with secret "key" into valid
say valid == False
"""
    res = execute(code)
    assert res.get("encrypted") == "khoor"
    assert res.get("valid") is False


def test_cloud_natural_phrases():
    code = """
use cloud

connect to bucket "my-test-bucket" into b
list all files in b into files
say files is not None
"""
    res = execute(code)
    assert res.get("b") is not None
    assert res.get("files") is not None
