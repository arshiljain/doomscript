import os
import sys
from typing import Dict, Any, List

src_path = os.path.abspath("src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from doomscript.compiler.engine import execute


def test_eq(name: str, code_a: str, code_b: str, var: str) -> Dict[str, Any]:
    res_a, err_a = None, None
    res_b, err_b = None, None
    try:
        dict_a = execute(code_a)
        res_a = dict_a.get(var)
    except Exception as e:
        err_a = f"{type(e).__name__}: {str(e)}"

    try:
        dict_b = execute(code_b)
        res_b = dict_b.get(var)
    except Exception as e:
        err_b = f"{type(e).__name__}: {str(e)}"

    passed = (err_a is None) and (err_b is None) and (res_a == res_b)
    return {
        "name": name,
        "code_a": code_a.strip(),
        "code_b": code_b.strip(),
        "res_a": res_a,
        "err_a": err_a,
        "res_b": res_b,
        "err_b": err_b,
        "passed": passed,
    }


def test_val(name: str, code: str, var: str, expected: Any) -> Dict[str, Any]:
    res, err = None, None
    try:
        out = execute(code)
        res = out.get(var)
    except Exception as e:
        err = f"{type(e).__name__}: {str(e)}"

    passed = (err is None) and (res == expected)
    return {
        "name": name,
        "code": code.strip(),
        "res": res,
        "err": err,
        "expected": expected,
        "passed": passed,
    }


def run():
    tests = []

    # 1. Statements vs Expressions
    tests.append(test_eq("Split statement vs inline expression", 'split "a,b" by "," into res', 'set res to split "a,b" by ","', "res"))
    tests.append(test_eq("Split statement vs suffix expression", 'split "a,b" by "," into res', 'set res to "a,b" split by ","', "res"))
    tests.append(test_eq("Join statement vs inline expression", 'set w to ["a","b"]\njoin w with "-" into res', 'set w to ["a","b"]\nset res to join w with "-"', "res"))
    tests.append(test_eq("Join statement vs suffix expression", 'set w to ["a","b"]\njoin w with "-" into res', 'set w to ["a","b"]\nset res to w joined with "-"', "res"))
    tests.append(test_eq("Sort statement vs inline expression", 'set n to [3, 1]\nsort n into res', 'set n to [3, 1]\nset res to sorted n', "res"))
    tests.append(test_eq("Sort by statement vs inline expression", 'set items to [{"v": 2}, {"v": 1}]\nsort items by v into res', 'set items to [{"v": 2}, {"v": 1}]\nset res to sorted items by v', "res"))
    tests.append(test_eq("Reverse statement vs inline expression", 'set n to [1, 2]\nreverse n into res', 'set n to [1, 2]\nset res to reversed n', "res"))
    tests.append(test_eq("Unique statement vs inline expression", 'set n to [1, 2, 2]\nunique n into res', 'set n to [1, 2, 2]\nset res to unique n', "res"))
    tests.append(test_eq("Unique statement vs unique items of", 'set n to [1, 2, 2]\nunique n into res', 'set n to [1, 2, 2]\nset res to unique items of n', "res"))
    tests.append(test_eq("Trim statement vs inline expression", 'trim " hi " into res', 'set res to trim " hi "', "res"))
    tests.append(test_eq("Uppercase statement vs inline expression", 'uppercase "hi" into res', 'set res to uppercase "hi"', "res"))
    tests.append(test_eq("Lowercase statement vs inline expression", 'lowercase "HI" into res', 'set res to lowercase "HI"', "res"))
    tests.append(test_eq("Take statement vs inline expression", 'set n to [1, 2, 3]\ntake 2 from n into res', 'set n to [1, 2, 3]\nset res to take 2 from n', "res"))
    tests.append(test_eq("Drop statement vs inline expression", 'set n to [1, 2, 3]\ndrop 1 from n into res', 'set n to [1, 2, 3]\nset res to drop 1 from n', "res"))
    tests.append(test_eq("Take statement vs first N items of", 'set n to [1, 2, 3]\nset res to first 2 items of n', 'set n to [1, 2, 3]\ntake 2 from n into res', "res"))
    tests.append(test_eq("Drop statement vs last N items of", 'set n to [1, 2, 3]\nset res to last 2 items of n', 'set n to [1, 2, 3]\ndrop 1 from n into res', "res"))

    # 2. Filtering & Conditionals
    tests.append(test_eq("Filter coll where vs keep only", 'set items to [{"a": 10}, {"a": 2}]\nitems where a > 5 into res', 'set items to [{"a": 10}, {"a": 2}]\nkeep only items where a > 5 into res', "res"))
    tests.append(test_eq("Filter coll where vs filter keyword", 'set items to [{"a": 10}, {"a": 2}]\nitems where a > 5 into res', 'set items to [{"a": 10}, {"a": 2}]\nfilter items where a > 5 into res', "res"))
    tests.append(test_eq("Filter coll where vs set res to coll where", 'set items to [{"a": 10}, {"a": 2}]\nitems where a > 5 into res', 'set items to [{"a": 10}, {"a": 2}]\nset res to items where a > 5', "res"))
    tests.append(test_eq("Filter where is vs equals", 'set items to [{"s": "ok"}, {"s": "no"}]\nitems where s is "ok" into res', 'set items to [{"s": "ok"}, {"s": "no"}]\nitems where s equals "ok" into res', "res"))
    tests.append(test_eq("Filter where is vs equal to", 'set items to [{"s": "ok"}, {"s": "no"}]\nitems where s is "ok" into res', 'set items to [{"s": "ok"}, {"s": "no"}]\nitems where s equal to "ok" into res', "res"))
    tests.append(test_eq("Filter where is vs ==", 'set items to [{"s": "ok"}, {"s": "no"}]\nitems where s is "ok" into res', 'set items to [{"s": "ok"}, {"s": "no"}]\nitems where s == "ok" into res', "res"))
    tests.append(test_eq("Filter where is over vs is greater than", 'set items to [{"a": 10}, {"a": 2}]\nitems where a is over 5 into res', 'set items to [{"a": 10}, {"a": 2}]\nitems where a is greater than 5 into res', "res"))
    tests.append(test_eq("Filter where is under vs is less than", 'set items to [{"a": 10}, {"a": 2}]\nitems where a is under 5 into res', 'set items to [{"a": 10}, {"a": 2}]\nitems where a is less than 5 into res', "res"))
    tests.append(test_eq("Filter where is at least vs >=", 'set items to [{"a": 5}, {"a": 2}]\nitems where a is at least 5 into res', 'set items to [{"a": 5}, {"a": 2}]\nitems where a >= 5 into res', "res"))
    tests.append(test_eq("Filter where is at most vs <=", 'set items to [{"a": 5}, {"a": 10}]\nitems where a is at most 5 into res', 'set items to [{"a": 5}, {"a": 10}]\nitems where a <= 5 into res', "res"))

    # 3. Composition
    tests.append(test_val("Composition: first 2 items of words joined with", 'set w to ["a", "b", "c"]\nset res to first 2 items of w joined with " / "', "res", "a / b"))
    tests.append(test_val("Composition: count of unique items of", 'set w to ["a", "b", "a"]\nset res to count of unique items of w', "res", 2))
    tests.append(test_val("Composition: uppercase of first item of", 'set w to ["hi", "there"]\nset res to uppercase of first item of w', "res", "HI"))
    tests.append(test_val("Composition: lowercase of last item of", 'set w to ["HI", "THERE"]\nset res to lowercase of last item of w', "res", "there"))
    tests.append(test_val("Composition: trim of uppercase of", 'set res to trim of uppercase of "  hello  "', "res", "HELLO"))
    tests.append(test_val("Composition: sum of prices of items", 'set items to [{"p": 10}, {"p": 20}]\nset res to sum of p of items', "res", 30))

    # 4. Quantifiers & Property Predicates
    tests.append(test_val("Quantifier: every x in list is positive", 'set n to [1, 2]\nset res to false\nif every x in n is positive: set res to true', "res", True))
    tests.append(test_val("Quantifier: every x in list has prop equal to val", 'set g to [{"role": "admin"}, {"role": "admin"}]\nset res to false\nif every x in g has role equal to "admin": set res to true', "res", True))
    tests.append(test_val("Quantifier: every x in list has prop val", 'set g to [{"role": "admin"}, {"role": "admin"}]\nset res to false\nif every x in g has role "admin": set res to true', "res", True))
    tests.append(test_val("Quantifier: every x in list has paid", 'set g to [{"paid": true}, {"paid": true}]\nset res to false\nif every x in g has paid: set res to true', "res", True))
    tests.append(test_val("Quantifier: all of list have paid", 'set g to [{"paid": true}, {"paid": true}]\nset res to false\nif all of g have paid: set res to true', "res", True))
    tests.append(test_val("Quantifier: no x in list is negative", 'set n to [1, 2]\nset res to false\nif no x in n is negative: set res to true', "res", True))
    tests.append(test_val("Quantifier: any x in list is even", 'set n to [1, 2]\nset res to false\nif any x in n is even: set res to true', "res", True))

    # 5. In-Place Mutations & Synonyms
    tests.append(test_eq("Mutation: add to vs append to", 'set n to [1]\nadd 2 to n\nset res to n', 'set n to [1]\nappend 2 to n\nset res to n', "res"))
    tests.append(test_eq("Mutation: add to vs push into", 'set n to [1]\nadd 2 to n\nset res to n', 'set n to [1]\npush 2 into n\nset res to n', "res"))
    tests.append(test_eq("Mutation: remove from vs delete from", 'set n to [1, 2]\nremove 2 from n\nset res to n', 'set n to [1, 2]\ndelete 2 from n\nset res to n', "res"))
    tests.append(test_eq("Mutation: clear vs empty", 'set n to [1, 2]\nclear n\nset res to n', 'set n to [1, 2]\nempty n\nset res to n', "res"))
    tests.append(test_eq("Mutation: increase by vs increment by", 'set x to 10\nincrease x by 2\nset res to x', 'set x to 10\nincrement x by 2\nset res to x', "res"))
    tests.append(test_eq("Mutation: decrease by vs decrement by", 'set x to 10\ndecrease x by 2\nset res to x', 'set x to 10\ndecrement x by 2\nset res to x', "res"))
    tests.append(test_eq("Mutation: subtract from vs decrease by", 'set x to 10\nsubtract 2 from x\nset res to x', 'set x to 10\ndecrease x by 2\nset res to x', "res"))

    # 6. Collections & Literals
    tests.append(test_eq("Collections: [] vs empty list", 'set res to []', 'set res to an empty list', "res"))
    tests.append(test_eq("Collections: [] vs new list", 'set res to []', 'set res to a new list', "res"))
    tests.append(test_eq("Collections: {} vs empty dictionary", 'set res to {}', 'set res to an empty dictionary', "res"))
    tests.append(test_eq("Collections: {} vs empty record", 'set res to {}', 'set res to an empty record', "res"))
    tests.append(test_eq("Collections: {} vs new dictionary", 'set res to {}', 'set res to a new dictionary', "res"))

    # 7. Field Access Consistency
    tests.append(test_eq("Field access: name of u vs u's name", 'set u to {"name": "Bob"}\nset res to name of u', 'set u to {"name": "Bob"}\nset res to u\'s name', "res"))
    tests.append(test_eq("Field access: u.name vs u's name", 'set u to {"name": "Bob"}\nset res to u.name', 'set u to {"name": "Bob"}\nset res to u\'s name', "res"))
    tests.append(test_val("Field access in condition: if status of u is", 'set u to {"status": "active"}\nset res to false\nif status of u is "active": set res to true', "res", True))
    tests.append(test_val("Field access in condition: if u's status is", 'set u to {"status": "active"}\nset res to false\nif u\'s status is "active": set res to true', "res", True))

    # 8. Conversational Inquiries & Math
    tests.append(test_val("Inquiry: what is the sum of", 'set n to [1, 2, 3]\nwhat is the sum of n into res', "res", 6))
    tests.append(test_val("Inquiry: what is sum of", 'set n to [1, 2, 3]\nwhat is sum of n into res', "res", 6))
    tests.append(test_val("Inquiry: what is the average of", 'set n to [10, 20]\nwhat is the average of n into res', "res", 15.0))
    tests.append(test_val("Inquiry: how many items in", 'set n to [1, 2, 3]\nhow many items in n into res', "res", 3))
    tests.append(test_val("Inquiry: count of", 'set n to [1, 2, 3]\nset res to count of n', "res", 3))
    tests.append(test_val("Inquiry: length of", 'set n to [1, 2, 3]\nset res to length of n', "res", 3))

    # 9. Membership & Inclusion
    tests.append(test_val("Membership: 5 is in numbers", 'set n to [1, 5, 10]\nset res to false\nif 5 is in n: set res to true', "res", True))
    tests.append(test_val("Membership: numbers contains 5", 'set n to [1, 5, 10]\nset res to false\nif n contains 5: set res to true', "res", True))
    tests.append(test_val("Membership: numbers has 5", 'set n to [1, 5, 10]\nset res to false\nif n has 5: set res to true', "res", True))
    tests.append(test_val("Membership: 99 is not in numbers", 'set n to [1, 5, 10]\nset res to false\nif 99 is not in n: set res to true', "res", True))
    tests.append(test_val("Membership: numbers does not contain 99", 'set n to [1, 5, 10]\nset res to false\nif n does not contain 99: set res to true', "res", True))

    # 10. Math & Arithmetic Synonyms
    tests.append(test_val("Math: double x", 'set x to 10\ndouble x\nset res to x', "res", 20))
    tests.append(test_val("Math: halve x", 'set x to 10\nhalve x\nset res to x', "res", 5.0))
    tests.append(test_val("Math: x squared", 'set x to 4\nset res to x squared', "res", 16))
    tests.append(test_val("Math: square of x", 'set x to 4\nset res to square of x', "res", 16))
    tests.append(test_val("Math: square root of x", 'set x to 16\nset res to square root of x', "res", 4.0))
    tests.append(test_val("Math: sqrt of x", 'set x to 16\nset res to sqrt of x', "res", 4.0))

    # Execute all
    passed = 0
    failed = 0
    print(f"Running Expanded Consistency Audit ({len(tests)} tests)...\\n")
    for idx, t in enumerate(tests, 1):
        if t["passed"]:
            passed += 1
            print(f"[{idx:02d}/{len(tests):02d}] PASS: {t['name']}")
        else:
            failed += 1
            print(f"[{idx:02d}/{len(tests):02d}] FAIL: {t['name']}")
            if "code_a" in t:
                print(f"   A: {t['code_a']} -> {t['res_a']} (err: {t['err_a']})")
                print(f"   B: {t['code_b']} -> {t['res_b']} (err: {t['err_b']})")
            else:
                print(f"   Code: {t['code']} -> {t['res']} (err: {t['err']}, expected: {t['expected']})")

    print(f"\\n============================================================")
    print(f"SUMMARY: {passed}/{len(tests)} PASSED ({passed/len(tests)*100:.1f}%), {failed} FAILED ({failed/len(tests)*100:.1f}%)")
    print(f"============================================================")


if __name__ == "__main__":
    run()
