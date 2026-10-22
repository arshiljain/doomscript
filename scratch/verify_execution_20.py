import sys
sys.path.insert(0, r"C:\Users\kanha\.gemini\antigravity\scratch\doomscript\src")
from doomscript.compiler.engine import execute

# Test 1: Sequence with then
ns = execute('set x to 10, then increase x by 5, and then double x')
assert ns['x'] == 30, f"Expected 30, got {ns['x']}"

# Test 3: Ingest and transform
ns = execute('split "a,b,c" by "," into items, then reverse items, and join items with "-" into res')
assert ns['items'] == ['c', 'b', 'a'], f"Expected ['c', 'b', 'a'], got {ns['items']}"
assert ns['res'] == "c-b-a", f"Expected 'c-b-a', got {ns['res']}"

# Test 6: Suffix if expression
ns = execute('set score to 120\nset status to "winner" if score > 100 otherwise "try_again"')
assert ns['status'] == "winner", f"Expected 'winner', got {ns['status']}"

ns2 = execute('set score to 80\nset status to "winner" if score > 100 otherwise "try_again"')
assert ns2['status'] == "try_again", f"Expected 'try_again', got {ns2['status']}"

# Test 9: "them" for collections
ns = execute('set nums to [1, 2, 3]\nreverse them into rev_nums')
assert ns['rev_nums'] == [3, 2, 1], f"Expected [3, 2, 1], got {ns['rev_nums']}"

# Test 10: Take from sort
ns = execute('set top_3 to first 3 items of sort [5, 1, 9, 3] descending')
assert ns['top_3'] == [9, 5, 3], f"Expected [9, 5, 3], got {ns['top_3']}"

# Test 11: Sum of filter
ns = execute('set total to sum of filter [1, 2, 3, 4] where item is even')
assert ns['total'] == 6, f"Expected 6, got {ns['total']}"

# Test 12: Join of split
ns = execute('set clean_str to join (split "a-b-c" by "-") with " "')
assert ns['clean_str'] == "a b c", f"Expected 'a b c', got {ns['clean_str']}"

# Test 15: Set filter with whose
class MockUser:
    def __init__(self, name, status):
        self.name = name
        self.status = status

users = [MockUser("Alice", "active"), MockUser("Bob", "inactive"), MockUser("Charlie", "active")]
ns = execute('set active_users to users whose status is "active"', custom_globals={"users": users})
assert len(ns['active_users']) == 2
assert [u.name for u in ns['active_users']] == ["Alice", "Charlie"]

# Test 19: Transfer from X to Y
ns = execute('set account_a to 100\nset account_b to 20\ntransfer 50 from account_a to account_b')
assert ns['account_a'] == 50, f"Expected 50, got {ns['account_a']}"
assert ns['account_b'] == 70, f"Expected 70, got {ns['account_b']}"

print("ALL RUNTIME EXECUTION AND ASSERTIONS PASSED WITH 100% SUCCESS!")
