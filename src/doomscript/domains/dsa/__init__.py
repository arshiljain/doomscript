"""Testing & Algorithm Analysis (DSA) Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.dsa.spec import BenchmarkSpec, ComplexityReport
from doomscript.domains.dsa.parser import DsaDomainParser
from doomscript.domains.dsa.runtime import (
    DsaRuntime,
    run_benchmark,
    fit_complexity,
    profile_memory_of_function,
)
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.dsa.exporter import DsaASTExporter
from doomscript.domains.registry import get_domain_registry


class DsaDomain(DomainContract):
    """Testing & Algorithm Analysis domain pack providing empirical complexity fitting and benchmarking."""

    name = "dsa"
    aliases = ["algo", "algorithms", "dsa_benchmark", "analysis"]
    description = "Data structures, algorithm benchmarking, empirical Big-O fitting, and memory profiling"
    parser = DsaDomainParser()
    runtime = DsaRuntime()
    exporter = DsaASTExporter()
    capabilities = [
        "complexity", "benchmarking", "profiling", "heaps", "queues",
        "grids", "connected_components", "graphs", "topological_sort",
        "memoization", "intervals", "sliding_window"
    ]
    optional_dependencies = ["matplotlib", "scipy"]

    verbs = [
        VerbSpec(
            name="complexity_of",
            pattern="[empirical] complexity of {fn_name:ident} [on sizes {sizes:expr}] into {target:ident}",
            arg_schema={"fn_name": "ident", "sizes": "expr", "target": "ident"},
            returns="Record",
            description="Empirical curve fitting for Big-O asymptotic runtime complexity",
        ),
        VerbSpec(
            name="profile_memory",
            pattern="profile memory of {fn_name:ident} [with {arg:expr}] into {target:ident}",
            arg_schema={"fn_name": "ident", "target": "ident"},
            returns="Record",
            description="Measure peak memory consumption and allocation",
        ),
        VerbSpec(
            name="benchmark_sizes",
            pattern="benchmark {fn_name:ident} (with|on) sizes {sizes:expr} into {target:ident}",
            arg_schema={"fn_name": "ident", "sizes": "expr", "target": "ident"},
            returns="Table",
            description="Measure execution time across input problem sizes",
        ),
        VerbSpec(
            name="pop_from",
            pattern="pop (min|max|left|first|right|last) from {coll:ident} into {target:ident}",
            arg_schema={"coll": "ident", "target": "ident"},
            returns="Any",
            description="Remove and retrieve extreme element from heap or queue",
        ),
        VerbSpec(
            name="create_grid",
            pattern="create [2d] grid with {rows:expr} rows and {cols:expr} columns [filled with {fill:expr}] into {target:ident}",
            arg_schema={"rows": "expr", "cols": "expr", "target": "ident"},
            returns="List",
            description="Create safely initialized 2D matrix without shallow reference sharing",
        ),
        VerbSpec(
            name="connected_components_grid",
            pattern="find [(4-way|8-way)] connected components in {grid:ident} where cell is {cell_val:expr} into {target:ident}",
            arg_schema={"grid": "ident", "cell_val": "expr", "target": "ident"},
            returns="List",
            description="Find all connected groups of coordinates in a 2D grid",
        ),
        VerbSpec(
            name="create_heap",
            pattern="create (min|max) heap into {target:ident}",
            arg_schema={"target": "ident"},
            returns="DsaHeap",
            description="Create universal min or max priority queue",
        ),
        VerbSpec(
            name="build_graph",
            pattern="build [(directed|undirected)] graph from {edges:expr} into {target:ident}",
            arg_schema={"edges": "expr", "target": "ident"},
            returns="DsaGraph",
            description="Construct algorithmic graph supporting cycle checks and topological sort",
        ),
        VerbSpec(
            name="graph_cycle",
            pattern="[check if] {graph:ident} has cycle into {target:ident}",
            arg_schema={"graph": "ident", "target": "ident"},
            returns="Boolean",
            description="Detect whether graph contains cycles using 3-color DFS",
        ),
        VerbSpec(
            name="topological_sort",
            pattern="topological (sort|order) of {graph:ident} into {target:ident}",
            arg_schema={"graph": "ident", "target": "ident"},
            returns="List",
            description="Compute topological sequence of vertices using Kahn's algorithm",
        ),
        VerbSpec(
            name="memoize_function",
            pattern="memoize [function] {fn:ident}",
            arg_schema={"fn": "ident"},
            returns="None",
            description="Automatically cache function outputs with deep argument hashing",
        ),
        VerbSpec(
            name="merge_intervals",
            pattern="merge overlapping intervals in {intervals:expr} into {target:ident}",
            arg_schema={"intervals": "expr", "target": "ident"},
            returns="List",
            description="Sort and merge overlapping interval pairs",
        ),
        VerbSpec(
            name="sliding_window_max",
            pattern="sliding window maximum of {arr:expr} with size {k:expr} into {target:ident}",
            arg_schema={"arr": "expr", "k": "expr", "target": "ident"},
            returns="List",
            description="Compute optimal O(n) monotonic sliding window maxima",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("complexity of ")
            or s.startswith("empirical complexity of ")
            or s.startswith("profile memory of ")
            or s.startswith("trace ")
            or (s.startswith("benchmark ") and (" with sizes " in s or " on sizes " in s))
            or s.startswith("push ")
            or s.startswith("pop min from ")
            or s.startswith("pop max from ")
            or s.startswith("pop left from ")
            or s.startswith("pop first from ")
            or s.startswith("pop right from ")
            or s.startswith("pop last from ")
            or s.startswith("peek ")
            or s.startswith("create min heap into ")
            or s.startswith("create max heap into ")
            or s.startswith("create deque into ")
            or s.startswith("create queue into ")
            or s.startswith("create grid ")
            or s.startswith("create 2d grid ")
            or s.startswith("create dp table ")
            or s.startswith("find connected components in ")
            or s.startswith("find 4-way connected components in ")
            or s.startswith("find 8-way connected components in ")
            or s.startswith("count connected components in ")
            or s.startswith("count 4-way connected components in ")
            or s.startswith("count 8-way connected components in ")
            or s.startswith("build graph from ")
            or s.startswith("build directed graph from ")
            or s.startswith("build undirected graph from ")
            or ((" has cycle into " in s) or s.startswith("check if "))
            or s.startswith("topological sort of ")
            or s.startswith("topological order of ")
            or s.startswith("shortest path in ")
            or s.startswith("connected components of ")
            or s.startswith("memoize ")
            or s.startswith("merge overlapping intervals in ")
            or s.startswith("intersect intervals ")
            or s.startswith("frequency map of ")
            or s.startswith("frequencies of ")
            or s.startswith("sliding window maximum of ")
            or s.startswith("create trie into ")
            or (s.startswith("insert ") and " into " in s)
            or (" contains " in s and " into " in s)
            or (" starts with " in s and " into " in s)
            or s.startswith("all words in ")
            or s.startswith("create disjoint set ")
            or s.startswith("union ")
            or s.startswith("find root of ")
            or (" are connected in " in s)
            or s.startswith("count of disjoint sets in ")
            or s.startswith("build binary tree from ")
            or s.startswith("level order traversal of ")
            or s.startswith("preorder traversal of ")
            or s.startswith("inorder traversal of ")
            or s.startswith("postorder traversal of ")
            or s.startswith("maximum depth of ")
            or s.startswith("invert binary tree ")
            or s.startswith("binary search target ")
            or s.startswith("lower bound of ")
            or s.startswith("upper bound of ")
            or s.startswith("next greater elements in ")
            or s.startswith("next smaller elements in ")
            or s.startswith("previous greater elements in ")
            or s.startswith("all permutations of ")
            or s.startswith("all combinations of ")
            or s.startswith("power set of ")
            or s.startswith("build linked list from ")
            or s.startswith("reverse linked list ")
            or ("linked list " in s and " has cycle into " in s)
            or s.startswith("convert linked list ")
            or s.startswith("maximum subarray sum of ")
            or s.startswith("maximum subarray in ")
            or s.startswith("prefix sums of ")
            or s.startswith("range sum in ")
            or s.startswith("create 2d prefix sums of ")
            or s.startswith("query 2d range sum in ")
            or s.startswith("find pair with sum ")
            or s.startswith("find all triplets with sum ")
            or s.startswith("minimum spanning tree ")
            or s.startswith("solve 0-1 knapsack with weights ")
            or s.startswith("minimum coins to make ")
            or s.startswith("count ways to make ")
            or s.startswith("find pattern ")
            or s.startswith("longest palindromic substring of ")
            or (" is palindrome into " in s)
            or s.startswith("create segment tree from ")
            or s.startswith("query range sum in segment tree ")
            or s.startswith("update point in segment tree ")
            or s.startswith("create fenwick tree from ")
            or s.startswith("prefix sum in fenwick tree ")
            or s.startswith("update fenwick tree ")
            or (s.startswith("sample ") and " using reservoir into " in s)
            or s.startswith("longest common subsequence of ")
            or s.startswith("correlation between ")
            or s.startswith("linear regression of ")
            or s.startswith("moving median of ")
            or (s.startswith("percentile ") and " into " in s)
            or s.startswith("z-score normalize ")
            or s.startswith("min-max scale ")
            or s.startswith("empirical cdf of ")
            or s.startswith("create prefix tree into ")
            or s.startswith("insert word ")
            or s.startswith("search word ")
            or s.startswith("create union find ")
            or s.startswith("union sets ")
            or s.startswith("create lru cache ")
            or s.startswith("get key ")
            or s.startswith("put key ")
            or s.startswith("binary search leftmost ")
            or s.startswith("binary search rightmost ")
            or s.startswith("quickselect ")
            or s.startswith("maximum sum 2d subgrid in ")
            or s.startswith("count inversions in ")
            or s.startswith("next lexicographical permutation of ")
            or s.startswith("previous lexicographical permutation of ")
            or s.startswith("rabin karp search for ")
            or s.startswith("longest palindromic substring in ")
            or s.startswith("find bridges in graph ")
        )

    def can_handle_block(self, header: str) -> bool:
        s = header.strip().lower()
        return s.startswith("benchmark ") and (":" in s)


# Register with central registry
DSA_DOMAIN = DsaDomain()
get_domain_registry().register(DSA_DOMAIN)

__all__ = [
    "DsaDomain",
    "DSA_DOMAIN",
    "BenchmarkSpec",
    "ComplexityReport",
    "DsaDomainParser",
    "DsaRuntime",
    "DsaASTExporter",
    "run_benchmark",
    "fit_complexity",
    "profile_memory_of_function",
    "AVLTree",
    "AVLNode",
    "dsa_avl_create",
    "dsa_avl_insert",
    "dsa_avl_delete",
    "dsa_avl_contains",
    "dsa_avl_inorder",
    "dsa_avl_height",
    "SuffixAutomaton",
    "dsa_suffix_automaton_create",
    "dsa_sam_contains_substring",
    "dsa_sam_distinct_substrings",
    "dsa_sam_longest_common_substring",
    "AhoCorasick",
    "dsa_aho_corasick_create",
    "dsa_aho_corasick_search",
    "Treap",
    "TreapNode",
    "dsa_treap_create",
    "dsa_treap_insert",
    "dsa_treap_contains",
    "dsa_treap_to_list",
    "DinicMaxFlow",
    "dsa_dinic_max_flow",
]
