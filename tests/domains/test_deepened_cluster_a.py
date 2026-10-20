"""Comprehensive test suite for Cluster A: Foundational Computing & Systems.

Covers deepened features across:
- dsa: FibonacciHeap, DisjointSetUnion with rollback, FenwickTree (1D & 2D), BloomFilter & CountingBloomFilter
- graph: Tarjan SCC, Hopcroft-Karp matching, Eulerian paths, Boruvka MST
- compiler: LALR(1) parser generator, SSA form builder, Chaitin register allocator
- automata: Pushdown Automaton, Moore & Mealy FSMs, Büchi Automaton
- net: TLS 1.3 ClientHello parser, SOCKS5 protocol framing, CIDR prefix trie (LPM)
"""

import pytest
from doomscript.domains.dsa.runtime import (
    FibonacciHeap,
    DisjointSetUnion,
    FenwickTree,
    FenwickTree2D,
    BloomFilter,
    CountingBloomFilter,
)
from doomscript.domains.graph.runtime import (
    DoomGraph,
    graph_tarjan_scc,
    graph_hopcroft_karp,
    graph_eulerian_path,
    graph_boruvka_mst,
)
from doomscript.domains.compiler.runtime import (
    LALR1Parser,
    SSAFormBuilder,
    ChaitinRegisterAllocator,
    compiler_lalr1_parse,
    compiler_build_ssa,
    compiler_allocate_registers,
)
from doomscript.domains.automata.runtime import (
    PushdownAutomaton,
    MooreMealyFSM,
    BuchiAutomaton,
    automata_create_pda,
    automata_pda_accepts,
    automata_create_moore_fsm,
    automata_create_mealy_fsm,
    automata_run_fsm,
    automata_create_buchi,
    automata_buchi_accepts_cycle,
)
from doomscript.domains.net.runtime import (
    TLS13ClientHelloParser,
    SOCKS5Protocol,
    CIDRPrefixTrie,
    net_parse_tls_client_hello,
    net_build_socks5_response,
    net_create_cidr_trie,
)


# ============================================================================
# 1. DSA Deepened Tests
# ============================================================================

def test_fibonacci_heap_operations():
    heap = FibonacciHeap()
    assert heap.is_empty()
    assert heap.find_min() is None

    # Insert items
    nodes = {}
    for val in [23, 7, 3, 17, 24, 18, 52, 38, 30, 26, 46, 39, 41, 35]:
        nodes[val] = heap.insert(val, f"data_{val}")

    assert len(heap) == 14
    assert heap.find_min().key == 3

    # Decrease key of 46 to 15
    heap.decrease_key(nodes[46], 15)
    assert heap.find_min().key == 3

    # Decrease key of 35 to 2
    heap.decrease_key(nodes[35], 2)
    assert heap.find_min().key == 2

    # Extract all elements in sorted order
    extracted = []
    while not heap.is_empty():
        min_node = heap.extract_min()
        extracted.append(min_node.key)

    assert extracted == sorted(extracted)
    assert extracted[0] == 2
    assert len(extracted) == 14


def test_fibonacci_heap_union():
    h1 = FibonacciHeap()
    h1.insert(10, "a")
    h1.insert(20, "b")

    h2 = FibonacciHeap()
    h2.insert(5, "c")
    h2.insert(15, "d")

    h1.union(h2)
    assert len(h1) == 4
    assert h1.find_min().key == 5
    assert h1.extract_min().key == 5
    assert h1.extract_min().key == 10


def test_disjoint_set_union_with_rollback():
    dsu = DisjointSetUnion(["A", "B", "C", "D", "E"])
    assert dsu.num_sets == 5

    # Check initial disjointness
    assert not dsu.connected("A", "B")

    # Union A-B and C-D
    assert dsu.union("A", "B")
    assert dsu.union("C", "D")
    assert dsu.connected("A", "B")
    assert dsu.connected("C", "D")
    assert not dsu.connected("A", "C")
    assert dsu.num_sets == 3

    # Checkpoint
    snap1 = dsu.checkpoint()

    # Union B-C
    dsu.union("B", "C")
    assert dsu.connected("A", "D")
    assert dsu.num_sets == 2

    # Rollback to checkpoint
    dsu.rollback(snap1)
    assert dsu.num_sets == 3
    assert not dsu.connected("A", "C")
    assert dsu.connected("A", "B")
    assert dsu.connected("C", "D")


def test_fenwick_trees_1d_and_2d():
    # 1D Fenwick Tree (1-based indexing)
    ft = FenwickTree([1, 3, 5, 7, 9, 11])
    assert ft.prefix_sum(0) == 0
    assert ft.prefix_sum(3) == 1 + 3 + 5  # 9
    assert ft.range_sum(3, 5) == 5 + 7 + 9  # 21

    ft.update(3, 10)  # 1-based index 3 (was 5, now 15)
    assert ft.range_sum(3, 5) == 15 + 7 + 9  # 31

    # 2D Fenwick Tree
    ft2 = FenwickTree2D(4, 4)
    ft2.update(1, 1, 5)
    ft2.update(2, 2, 7)
    ft2.update(1, 2, 3)

    assert ft2.query(2, 2) == 15
    assert ft2.range_query(2, 2, 3, 3) == 7


def test_bloom_filters():
    bf = BloomFilter(capacity=100, error_rate=0.01)
    items = [f"item_{i}" for i in range(50)]
    for it in items:
        bf.add(it)

    for it in items:
        assert it in bf

    # Elements not added should rarely be in bloom filter
    negatives = [f"absent_{i}" for i in range(50)]
    false_positives = sum(1 for it in negatives if it in bf)
    assert false_positives <= 3

    # Counting Bloom Filter (supports removal)
    cbf = CountingBloomFilter(capacity=50, error_rate=0.01)
    cbf.add("test_key")
    assert "test_key" in cbf
    assert cbf.remove("test_key")
    assert "test_key" not in cbf


# ============================================================================
# 2. Graph Deepened Tests
# ============================================================================

def test_tarjan_scc():
    g = DoomGraph(directed=True)
    for n in ["A", "B", "C", "D", "E"]:
        g.add_node(n)

    # Component 1: A -> B -> C -> A
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    g.add_edge("C", "A")

    # Bridge: C -> D
    g.add_edge("C", "D")

    # D -> E
    g.add_edge("D", "E")

    res = graph_tarjan_scc(g)
    sccs = res["sccs"]
    # Expect 3 SCCs: {A, B, C}, {D}, {E}
    scc_sets = [set(c) for c in sccs]
    assert {"A", "B", "C"} in scc_sets
    assert {"D"} in scc_sets
    assert {"E"} in scc_sets


def test_hopcroft_karp_bipartite_matching():
    g = DoomGraph(directed=False)
    # Bipartite sets: {u1, u2, u3} and {v1, v2, v3}
    edges = [
        ("u1", "v1"),
        ("u1", "v2"),
        ("u2", "v1"),
        ("u3", "v2"),
        ("u3", "v3"),
    ]
    for u, v in edges:
        g.add_edge(u, v)

    res = graph_hopcroft_karp(g, partition_u=["u1", "u2", "u3"])
    assert res["matching_size"] == 3
    assert len(res["matches"]) == 3


def test_eulerian_path_and_circuit():
    # Directed Eulerian circuit
    g_dir = DoomGraph(directed=True)
    edges = [("A", "B"), ("B", "C"), ("C", "A")]
    for u, v in edges:
        g_dir.add_edge(u, v)

    res = graph_eulerian_path(g_dir)
    assert res["has_eulerian_path"]
    assert res["has_eulerian_circuit"]
    assert len(res["path"]) == 4  # e.g. A, B, C, A

    # Undirected Eulerian path (2 odd degree vertices)
    g_undir = DoomGraph(directed=False)
    # Path: 1-2, 2-3, 3-4, 4-2
    for u, v in [("1", "2"), ("2", "3"), ("3", "4"), ("4", "2")]:
        g_undir.add_edge(u, v)

    res2 = graph_eulerian_path(g_undir)
    assert res2["has_eulerian_path"]
    assert not res2["has_eulerian_circuit"]


def test_boruvka_mst():
    g = DoomGraph(directed=False)
    weighted_edges = [
        ("A", "B", 4),
        ("A", "C", 2),
        ("B", "C", 1),
        ("B", "D", 5),
        ("C", "D", 8),
        ("C", "E", 10),
        ("D", "E", 2),
    ]
    for u, v, w in weighted_edges:
        g.add_edge(u, v, weight=w)

    res = graph_boruvka_mst(g)
    assert res["is_connected"]
    # MST should pick: (B, C, 1), (A, C, 2), (D, E, 2), (B, D, 5) -> Total = 10
    assert res["total_weight"] == 10.0
    assert len(res["mst_edges"]) == 4


# ============================================================================
# 3. Compiler Deepened Tests
# ============================================================================

def test_lalr1_parser():
    # Arithmetic expression grammar:
    # E -> E + T | T
    # T -> T * F | F
    # F -> ( E ) | id
    grammar = {
        "start": "E",
        "terminals": ["id", "+", "*", "(", ")"],
        "nonterminals": ["E", "T", "F"],
        "rules": [
            ("E", ["E", "+", "T"]),
            ("E", ["T"]),
            ("T", ["T", "*", "F"]),
            ("T", ["F"]),
            ("F", ["(", "E", ")"]),
            ("F", ["id"]),
        ],
    }

    parser = LALR1Parser(grammar)
    # Parse tokens: id + id * id
    res = parser.parse(["id", "+", "id", "*", "id"])
    assert res["success"]
    assert res["tree"] is not None
    assert res["tree"]["symbol"] == "E"

    # Syntax error check
    res_err = parser.parse(["+", "id"])
    assert not res_err["success"]


def test_ssa_form_builder():
    # CFG with diamond control flow:
    # b0 -> b1, b2; b1 -> b3; b2 -> b3
    cfg = {
        "entry": "b0",
        "blocks": {
            "b0": {
                "instructions": [
                    {"op": "assign", "target": "x", "args": ["1"]},
                ],
                "succs": ["b1", "b2"],
            },
            "b1": {
                "instructions": [
                    {"op": "assign", "target": "x", "args": ["2"]},
                ],
                "succs": ["b3"],
            },
            "b2": {
                "instructions": [
                    {"op": "assign", "target": "x", "args": ["3"]},
                ],
                "succs": ["b3"],
            },
            "b3": {
                "instructions": [
                    {"op": "print", "target": None, "args": ["x"]},
                ],
                "succs": [],
            },
        },
    }

    builder = SSAFormBuilder()
    ssa = builder.build_ssa(cfg)

    # b3 should have a phi node for x
    b3_insts = ssa["blocks"]["b3"]["instructions"]
    phi_nodes = [i for i in b3_insts if i.get("op") == "phi"]
    assert len(phi_nodes) == 1
    assert phi_nodes[0]["var"] == "x"

    # Deconstruct SSA
    decon = builder.deconstruct_ssa(ssa)
    assert "b3" in decon["blocks"]


def test_chaitin_register_allocator():
    # Variables a, b, c, d
    instructions = [
        {"id": 0, "def": ["a"], "use": [], "op": "const"},
        {"id": 1, "def": ["b"], "use": ["a"], "op": "add"},
        {"id": 2, "def": ["c"], "use": ["b"], "op": "mul"},
        {"id": 3, "def": ["d"], "use": ["a", "c"], "op": "sub"},
    ]

    allocator = ChaitinRegisterAllocator(k_registers=3)
    res = allocator.allocate(instructions)

    assert "allocations" in res
    assert res["k_registers"] == 3
    # Check that each variable is allocated either to a register or spill slot
    for var in ["a", "b", "c", "d"]:
        assert var in res["allocations"]
        assert res["allocations"][var]["type"] in ("register", "spill")


# ============================================================================
# 4. Automata Deepened Tests
# ============================================================================

def test_pushdown_automaton_balanced_parentheses():
    # PDA for L = { a^n b^n | n >= 1 }
    # Stack alphabet: Z0 (bottom), A
    transitions = {
        ("q0", "a", "Z0"): [("q0", ["Z0", "A"])],
        ("q0", "a", "A"): [("q0", ["A", "A"])],
        ("q0", "b", "A"): [("q1", [])],
        ("q1", "b", "A"): [("q1", [])],
        ("q1", "", "Z0"): [("q_accept", ["Z0"])],
    }

    pda = PushdownAutomaton(
        states={"q0", "q1", "q_accept"},
        input_alphabet={"a", "b"},
        stack_alphabet={"Z0", "A"},
        transitions=transitions,
        start_state="q0",
        start_stack_symbol="Z0",
        accept_states={"q_accept"},
        acceptance_mode="final_state",
    )

    assert pda.accepts("ab")
    assert pda.accepts("aabb")
    assert pda.accepts("aaabbb")

    assert not pda.accepts("a")
    assert not pda.accepts("b")
    assert not pda.accepts("aab")
    assert not pda.accepts("abb")
    assert not pda.accepts("ba")


def test_moore_and_mealy_fsm():
    # Moore machine: 3 states counting modulo 3
    moore = automata_create_moore_fsm(
        states=["s0", "s1", "s2"],
        alphabet=["tick"],
        transitions={
            ("s0", "tick"): "s1",
            ("s1", "tick"): "s2",
            ("s2", "tick"): "s0",
        },
        outputs={"s0": 0, "s1": 1, "s2": 2},
        start_state="s0",
    )

    res = automata_run_fsm(moore, ["tick", "tick", "tick", "tick"])
    assert res["states"] == ["s0", "s1", "s2", "s0", "s1"]
    assert res["outputs"] == [0, 1, 2, 0, 1]

    # Convert to Mealy
    mealy = moore.to_mealy()
    assert mealy.machine_type == "mealy"
    res_mealy = automata_run_fsm(mealy, ["tick", "tick"])
    assert res_mealy["outputs"] == [1, 2]


def test_buchi_automaton_omega_acceptance():
    # Recognizes (a + b)* b^omega (eventually always b)
    transitions = {
        ("q0", "a"): {"q0"},
        ("q0", "b"): {"q0", "q1"},
        ("q1", "b"): {"q1"},
    }
    buchi = BuchiAutomaton(
        states={"q0", "q1"},
        alphabet={"a", "b"},
        transitions=transitions,
        start_state="q0",
        accept_states={"q1"},
    )

    # Prefix "aab", cycle "b" -> infinitely many b's -> accepted!
    assert buchi.accepts_lasso(prefix="aab", cycle="b")

    # Prefix "b", cycle "a" -> eventually only a's -> rejected
    assert not buchi.accepts_lasso(prefix="b", cycle="a")

    # Emptiness test
    empty_res = buchi.is_empty()
    assert not empty_res["is_empty"]
    assert empty_res["accepting_state"] == "q1"


# ============================================================================
# 5. Net Deepened Tests
# ============================================================================

def test_tls13_client_hello_parser():
    # Build mock ClientHello record
    record = TLS13ClientHelloParser.build_mock_client_hello(server_name="api.doomscript.org")
    assert len(record) > 5

    parsed = TLS13ClientHelloParser.parse(record)
    assert parsed["is_tls13"]
    assert parsed["extensions"]["server_name"] == "api.doomscript.org"
    assert "TLS 1.3" in parsed["extensions"]["supported_versions"]
    assert "x25519" in parsed["extensions"]["supported_groups"]


def test_socks5_protocol():
    # Client greeting: version 5, 2 methods (0x00: No auth, 0x02: User/Pass)
    greeting_bytes = bytes([0x05, 0x02, 0x00, 0x02])
    parsed_greeting = SOCKS5Protocol.parse_client_greeting(greeting_bytes)
    assert parsed_greeting["version"] == 5
    assert 0x00 in parsed_greeting["methods"]

    # Server choice
    server_choice = SOCKS5Protocol.build_server_greeting(0x00)
    assert server_choice == bytes([0x05, 0x00])

    # Connect request to IPv4: 127.0.0.1:8080 (0x1F90)
    req_ipv4 = bytes([0x05, 0x01, 0x00, 0x01, 127, 0, 0, 1, 0x1F, 0x90])
    parsed_req = SOCKS5Protocol.parse_request(req_ipv4)
    assert parsed_req["cmd"] == "CONNECT"
    assert parsed_req["dest_address"] == "127.0.0.1"
    assert parsed_req["dest_port"] == 8080

    # Build response: Succeeded, bind to 127.0.0.1:8080
    resp_bytes = SOCKS5Protocol.build_response(rep=0x00, bind_addr="127.0.0.1", bind_port=8080)
    assert len(resp_bytes) == 10
    assert resp_bytes[1] == 0x00  # REP_SUCCESS


def test_cidr_prefix_trie():
    trie = CIDRPrefixTrie()
    trie.insert("0.0.0.0/0", "default_gateway")
    trie.insert("10.0.0.0/8", "corp_net")
    trie.insert("10.1.0.0/16", "engineering_subnet")
    trie.insert("10.1.2.0/24", "lab_rack")

    # Longest prefix match test
    assert trie.lookup("10.1.2.55")["matched_cidr"] == "10.1.2.0/24"
    assert trie.lookup("10.1.2.55")["value"] == "lab_rack"

    assert trie.lookup("10.1.99.1")["matched_cidr"] == "10.1.0.0/16"
    assert trie.lookup("10.1.99.1")["value"] == "engineering_subnet"

    assert trie.lookup("10.200.0.1")["matched_cidr"] == "10.0.0.0/8"
    assert trie.lookup("10.200.0.1")["value"] == "corp_net"

    assert trie.lookup("172.16.0.1")["matched_cidr"] == "0.0.0.0/0"
    assert trie.lookup("172.16.0.1")["value"] == "default_gateway"

    # IPv6 route test
    trie.insert("2001:db8::/32", "ipv6_doc_range")
    v6_match = trie.lookup("2001:db8:0:0:0:0:0:1")
    assert v6_match is not None
    assert v6_match["matched_cidr"] == "2001:db8::/32"
