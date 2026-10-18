"""
Tests for Phase 3: Classes — English-first OOP (CS2 core)
"""

import pytest
from doomscript.compiler.engine import execute


def test_basic_class_and_methods(capsys):
    code = """
define a Counter:
    to start with initial:
        my count = initial

    to increment:
        my count += 1

    to get_count:
        return my count

c = Counter(10)
c.increment()
c.increment()
say c.get_count()
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip() == "12"


def test_class_inheritance_and_base_start(capsys):
    code = """
define an Animal:
    to start with name:
        my name = name

    to speak:
        return my name + " makes a sound"

define a Dog that is an Animal:
    to start with name, breed:
        base start with name
        my breed = breed

    to speak:
        return my name + " barks"

d = Dog("Rex", "German Shepherd")
say d.speak()
say d.breed
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "Rex barks",
        "German Shepherd"
    ]


def test_english_dunder_methods(capsys):
    code = """
define a Box:
    to start:
        my items = [10, 20, 30]

    to get length:
        return len(my items)

    to get item with index:
        return my items[index]

    to describe:
        return "Box with items"

b = Box()
say len(b)
say b[1]
say str(b)
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "3",
        "20",
        "Box with items"
    ]


def test_python_style_class_syntax(capsys):
    code = """
class Point:
    to start with x, y:
        my x = x
        my y = y

    to coords:
        return (my x, my y)

p = Point(3, 4)
say p.coords()
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip() == "(3, 4)"


def test_cs2_singly_linked_list(capsys):
    code = """
define a Node:
    to start with val:
        my val = val
        my next = none

define a LinkedList:
    to start:
        my head = none

    to append with val:
        new_node = Node(val)
        if my head is none:
            my head = new_node
            return none
        curr = my head
        while curr.next is not none:
            curr = curr.next
        curr.next = new_node

    to find with target:
        curr = my head
        while curr is not none:
            if curr.val == target:
                return true
            curr = curr.next
        return false

    to to_list:
        res = []
        curr = my head
        while curr is not none:
            add curr.val to res
            curr = curr.next
        return res

ll = LinkedList()
ll.append(10)
ll.append(20)
ll.append(30)
say ll.to_list()
say ll.find(20)
say ll.find(99)
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "[10, 20, 30]",
        "True",
        "False"
    ]


def test_cs2_stack(capsys):
    code = """
define a Stack:
    to start:
        my items = []

    to push with x:
        add x to my items

    to pop:
        return pop my items

    to peek:
        return my items[-1]

    to is_empty:
        return len(my items) == 0

st = Stack()
say st.is_empty()
st.push("first")
st.push("second")
say st.peek()
say st.pop()
say st.pop()
say st.is_empty()
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "True",
        "second",
        "second",
        "first",
        "True"
    ]


def test_cs2_queue(capsys):
    code = """
define a Queue:
    to start:
        my items = []

    to enqueue with x:
        add x to my items

    to dequeue:
        first_item = my items[0]
        my items = my items[1:]
        return first_item

    to is_empty:
        return len(my items) == 0

q = Queue()
say q.is_empty()
q.enqueue("A")
q.enqueue("B")
q.enqueue("C")
say q.dequeue()
say q.dequeue()
q.enqueue("D")
say q.dequeue()
say q.dequeue()
say q.is_empty()
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "True",
        "A",
        "B",
        "C",
        "D",
        "True"
    ]


def test_cs2_binary_search_tree(capsys):
    code = """
define a TreeNode:
    to start with val:
        my val = val
        my left = none
        my right = none

define a BST:
    to start:
        my root = none

    to insert with val:
        if my root is none:
            my root = TreeNode(val)
        else:
            my _insert_node(my root, val)

    to _insert_node with node, val:
        if val < node.val:
            if node.left is none:
                node.left = TreeNode(val)
            else:
                my _insert_node(node.left, val)
        else:
            if node.right is none:
                node.right = TreeNode(val)
            else:
                my _insert_node(node.right, val)

    to contains with val:
        return my _contains_node(my root, val)

    to _contains_node with node, val:
        if node is none:
            return false
        if node.val == val:
            return true
        elif val < node.val:
            return my _contains_node(node.left, val)
        else:
            return my _contains_node(node.right, val)

    to inorder:
        res = []
        my _inorder_walk(my root, res)
        return res

    to _inorder_walk with node, res:
        if node is not none:
            my _inorder_walk(node.left, res)
            add node.val to res
            my _inorder_walk(node.right, res)

tree = BST()
tree.insert(50)
tree.insert(30)
tree.insert(70)
tree.insert(20)
tree.insert(40)
tree.insert(60)
tree.insert(80)

say tree.inorder()
say tree.contains(40)
say tree.contains(99)
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "[20, 30, 40, 50, 60, 70, 80]",
        "True",
        "False"
    ]
