from doomscript.compiler.engine import execute

print("=== 1. Test Filter / Keep only ===")
try:
    code1_a = """
items = [{'amount': 10}, {'amount': 60}]
items where amount is over 50 into qualifying
"""
    env1_a = execute(code1_a)
    print("1A (items where) SUCCESS ->", env1_a.get("qualifying"))
except Exception as e:
    print("1A (items where) FAILED ->", type(e).__name__, e)

try:
    code1_b = """
items = [{'amount': 10}, {'amount': 60}]
keep only items where amount is over 50 into qualifying
"""
    env1_b = execute(code1_b)
    print("1B (keep only) SUCCESS ->", env1_b.get("qualifying"))
except Exception as e:
    print("1B (keep only) FAILED ->", type(e).__name__, e)


print("\n=== 2. Test Composition ===")
try:
    code2 = """
words = ["alpha", "beta", "gamma"]
set short_label to first 2 items of words joined with " / "
"""
    env2 = execute(code2)
    print("2 (composition) SUCCESS ->", env2.get("short_label"))
except Exception as e:
    print("2 (composition) FAILED ->", type(e).__name__, e)

try:
    code2_split = """
words = ["alpha", "beta", "gamma"]
first 2 items of words into short_words
set short_label to short_words joined with " / "
"""
    env2_split = execute(code2_split)
    print("2 (two statements) SUCCESS ->", env2_split.get("short_label"))
except Exception as e:
    print("2 (two statements) FAILED ->", type(e).__name__, e)


print("\n=== 3. Test Pipeline Filter 'is' vs 'equals' ===")
try:
    code3_a = """
use data
items = [{'status': 'active', 'id': 1}, {'status': 'inactive', 'id': 2}]
pipeline 'p1' from items into out_a:
    filter where status is 'active'
"""
    env3_a = execute(code3_a)
    print("3A (filter where status is 'active') SUCCESS ->", env3_a.get("out_a"))
except Exception as e:
    print("3A (filter where status is 'active') FAILED ->", type(e).__name__, e)

try:
    code3_b = """
use data
items = [{'status': 'active', 'id': 1}, {'status': 'inactive', 'id': 2}]
pipeline 'p2' from items into out_b:
    filter where status equals 'active'
"""
    env3_b = execute(code3_b)
    print("3B (filter where status equals 'active') SUCCESS ->", env3_b.get("out_b"))
except Exception as e:
    print("3B (filter where status equals 'active') FAILED ->", type(e).__name__, e)


print("\n=== 4. Test English Quantifiers ===")
try:
    code4 = """
registrations = [{'guest': 'Alice', 'paid': True}, {'guest': 'Bob', 'paid': True}]
if every guest in registrations is paid:
    paid_ok = True
"""
    env4 = execute(code4)
    print("4 (every guest in registrations is paid) SUCCESS ->", env4.get("paid_ok"))
except Exception as e:
    print("4 (every guest in registrations is paid) FAILED ->", type(e).__name__, e)

try:
    code4_b = """
registrations = [{'guest': 'Alice', 'paid': True}, {'guest': 'Bob', 'paid': True}]
if every guest in registrations has paid:
    has_paid_ok = True
"""
    env4_b = execute(code4_b)
    print("4B (every guest in registrations has paid) SUCCESS ->", env4_b.get("has_paid_ok"))
except Exception as e:
    print("4B (every guest in registrations has paid) FAILED ->", type(e).__name__, e)

try:
    code4_c = """
registrations = [{'guest': 'Alice', 'status': 'paid'}, {'guest': 'Bob', 'status': 'paid'}]
if every guest in registrations has status equal to "paid":
    status_paid_ok = True
"""
    env4_c = execute(code4_c)
    print("4C (every guest has status equal to 'paid') SUCCESS ->", env4_c.get("status_paid_ok"))
except Exception as e:
    print("4C (every guest has status equal to 'paid') FAILED ->", type(e).__name__, e)
