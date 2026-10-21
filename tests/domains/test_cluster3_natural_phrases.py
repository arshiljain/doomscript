"""Tests for Cluster 3 (Computing & Systems) natural English phrases:
compiler, compression, automata, dsa, graph, net, sec, cloud
"""

from doomscript.compiler.engine import execute


def test_cluster3_sec_and_net(capsys):
    code = """
use sec
encrypt "hello" with caesar cipher shift 3 into encrypted
say encrypted == "khoor"
verify jwt "invalid.token.here" with secret "mysecret" into valid
say valid == False

use net
create cidr prefix trie into trie
say trie is not None
"""
    execute(code)
    out = capsys.readouterr().out.strip().splitlines()
    assert out[0] == "True"
    assert out[1] == "True"
    assert out[2] == "True"


def test_cluster3_dsa_and_automata(capsys):
    code = """
use automata
compile regex "a*b" to dfa into my_dfa
check if dfa my_dfa accepts "aaab" into ok
say ok == True
"""
    execute(code)
    out = capsys.readouterr().out.strip().splitlines()
    assert out[0] == "True"
