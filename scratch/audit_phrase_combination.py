import sys
sys.path.insert(0, r"C:\Users\kanha\.gemini\antigravity\scratch\doomscript\src")
from doomscript.compiler.engine import compile_to_ast, transpile, execute

test_cases = [
    # Category 1: Compound Actions with Conjunctions (and, then, and then)
    ('1. Sequence with then', 'set x to 10, then increase x by 5, and then double x'),
    ('2. Sequence with and', 'read file "input.txt" into text and save text to "output.txt"'),
    ('3. Ingest and transform', 'split "a,b,c" by "," into items, then reverse items, and join items with "-" into res'),

    # Category 2: Suffix Conditionals (do X if Y, do X unless Y)
    ('4. Suffix if statement', 'increase score by 10 if bonus_active is true'),
    ('5. Suffix unless statement', 'delete file "temp.txt" unless preserve_logs is true'),
    ('6. Suffix if expression', 'set status to "winner" if score > 100 otherwise "try_again"'),

    # Category 3: Pronoun & Anaphora Chaining (it, them, the result)
    ('7. Verb on "it"', 'read file "data.txt" into content\nsay it'),
    ('8. Transform "it"', 'set text to "hello world"\nuppercase it into loud_text'),
    ('9. "them" for collections', 'set nums to [1, 2, 3]\nreverse them into rev_nums'),

    # Category 4: Nested / Composed Expressions (verb inside verb)
    ('10. Take from sort', 'set top_3 to first 3 items of sort [5, 1, 9, 3] descending'),
    ('11. Sum of filter', 'set total to sum of filter [1, 2, 3, 4] where item is even'),
    ('12. Join of split', 'set clean_str to join (split "a-b-c" by "-") with " "'),

    # Category 5: Relative Clauses (where, whose, which, that)
    ('13. For each with where', 'for each user in users where user\'s age > 21:\n    say user\'s name'),
    ('14. For each with whose', 'for each item in inventory whose stock < 5:\n    say item\'s name'),
    ('15. Set filter with whose', 'set active_users to users whose status is "active"'),

    # Category 6: Adverbial & Modal Prefixes (always, never, repeatedly, safely)
    ('16. Safely try block', 'safely do: read file "missing.txt" into data otherwise "default"'),
    ('17. Retry prefix', 'retry 3 times: fetch url "http://api.com" into res'),

    # Category 7: Preposition Stacking (to X with Y at Z)
    ('18. Multi-preposition verb', 'copy file "a.txt" to "b.txt" with overwrite true'),
    ('19. Transfer from X to Y', 'transfer 50 from account_a to account_b'),
    ('20. In N time do X', 'in 5 seconds: say "Time is up"')
]

print("="*80)
print("AUDIT OF NATURAL PHRASE COMBINATIONS IN DOOMSCRIPT")
print("="*80)

passed = 0
failed = 0

for label, code in test_cases:
    try:
        py_ast = compile_to_ast(code)
        py_code = transpile(code).strip().replace("\n", " | ")
        print(f"PASS | {label:<30} -> {py_code[:55]}")
        passed += 1
    except Exception as e:
        err_msg = str(e).split("\n")[0][:60]
        print(f"FAIL | {label:<30} -> {e.__class__.__name__}: {err_msg}")
        failed += 1

print("\n" + "="*80)
print(f"Total: {passed}/{len(test_cases)} PASSED ({passed/len(test_cases)*100:.1f}%), {failed} FAILED")
print("="*80)
