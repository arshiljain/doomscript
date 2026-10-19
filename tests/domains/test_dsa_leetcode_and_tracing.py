"""Unit and integration tests for DSA LeetCode-compatible export target and recursion execution tracing."""

import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.dsa.runtime import ListNode, TreeNode, trace_recursion


def test_listnode_and_treenode_primitives():
    # ListNode tests
    head = ListNode(1, ListNode(2, ListNode(3)))
    assert head.to_list() == [1, 2, 3]
    from_arr = ListNode.from_list([4, 5, 6])
    assert from_arr.to_list() == [4, 5, 6]

    # TreeNode tests
    root = TreeNode(10, TreeNode(5), TreeNode(15))
    assert root.inorder() == [5, 10, 15]


def test_dsa_recursion_tracing():
    source = """use dsa

to fib with n:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

trace fib on 4 into fib_trace
"""
    env = execute(source)
    assert "fib_trace" in env
    trace = env["fib_trace"]
    assert "call_count" in trace
    assert trace["call_count"] == 9  # fib(4) has 9 calls
    assert trace["max_depth"] == 4
    assert trace["result"] == 3
    assert len(trace["events"]) > 0


def test_leetcode_compatible_export():
    source = """use dsa
target leetcode

to two_sum with nums, target:
    seen = {}
    for i, n in enumerate(nums):
        diff = target - n
        if diff in seen:
            return [seen[diff], i]
        seen[n] = i
    return []
"""
    py_code = export_to_python(source)
    assert "class Solution:" in py_code
    assert "def twoSum(self" in py_code or "def two_sum(self" in py_code
    assert "class ListNode:" in py_code
    assert "class TreeNode:" in py_code

    # Execute exported python code and test with Solution()
    exec_env = {}
    exec(py_code, exec_env)
    assert "Solution" in exec_env
    sol = exec_env["Solution"]()
    # Call method
    method_name = "twoSum" if hasattr(sol, "twoSum") else "two_sum"
    fn = getattr(sol, method_name)
    assert fn([2, 7, 11, 15], 9) == [0, 1]
