"""
Tests for Long Chaining and Cross-Domain Interoperability in DoomScript.
"""
import pytest
from doomscript.compiler.engine import compile_to_ast, execute
from doomscript.domains.registry import get_domain_registry

audit_cases = [
    # PART 1: LONG CHAINING DEPTH
    (
        "CHAIN-01: 2-step chain 'then'",
        """
set x to 5, then add 10 to x
""",
        lambda ns: ns.get("x") == 15,
    ),
    (
        "CHAIN-02: 3-step chain 'then ... and then'",
        """
set x to 5, then add 10 to x, and then multiply x by 2
""",
        lambda ns: ns.get("x") == 30,
    ),
    (
        "CHAIN-03: 4-step chain with comma 'then'",
        """
set x to 2, then add 3 to x, then multiply x by 4, and then decrease x by 5
""",
        lambda ns: ns.get("x") == 15,
    ),
    (
        "CHAIN-04: 5-step chain with diverse verbs",
        """
set x to 1, then add 2 to x, then add 3 to x, then add 4 to x, and then add 5 to x
""",
        lambda ns: ns.get("x") == 15,
    ),
    (
        "CHAIN-05: Semicolon separated multi-action chaining",
        """
set a to 10; set b to 20; set c to a + b
""",
        lambda ns: ns.get("c") == 30,
    ),
    (
        "CHAIN-06: Period separated multi-sentence chaining on one line",
        """
set a to 10. set b to 20. set c to a + b.
""",
        lambda ns: ns.get("c") == 30,
    ),
    (
        "CHAIN-07: Pronoun 'it' across chained statements",
        """
set price to 100, then add 20 to price, and then halve it
""",
        lambda ns: ns.get("price") == 60,
    ),
    (
        "CHAIN-08: Pronoun 'them' and 'their count' across chained statements",
        """
set items to [1, 2, 3], then add 4 to them, and then set total to their count
""",
        lambda ns: ns.get("total") == 4,
    ),
    (
        "CHAIN-09: Pronoun 'its' attribute access across chain",
        """
create a Person with name "Alice", age 30 into user, then set status to "verified", and then set final_age to user's age
""",
        lambda ns: ns.get("final_age") == 30,
    ),
    (
        "CHAIN-10: 1 statement then block header 'then if'",
        """
set x to 10, then if x > 5:
    set result to "yes"
""",
        lambda ns: ns.get("result") == "yes",
    ),
    (
        "CHAIN-11: 2 statements then block header 'then ... then if'",
        """
set x to 2, then add 8 to x, then if x > 5:
    set result to "yes"
""",
        lambda ns: ns.get("result") == "yes",
    ),
    (
        "CHAIN-12: 3 statements then block header 'then ... and then ... then if'",
        """
set x to 1, then add 2 to x, and then add 7 to x, then if x >= 10:
    set result to "yes"
""",
        lambda ns: ns.get("result") == "yes",
    ),
    (
        "CHAIN-13: Chaining inside loop body",
        """
set total to 0
for each n in [1, 2, 3]:
    set step to n * 2, then add step to total
""",
        lambda ns: ns.get("total") == 12,
    ),
    (
        "CHAIN-14: Compound chaining with loop header 'then for each'",
        """
set nums to [1, 2, 3], and then for each n in nums:
    set last_seen to n
""",
        lambda ns: ns.get("last_seen") == 3,
    ),

    # PART 2: CROSS-DOMAIN SYNTAX & INTEROPERABILITY
    (
        "XDOM-01: Single domain activation 'use web'",
        """
use web
parse html "<h1>Hello</h1>" into doc
""",
        lambda ns: ns.get("doc") is not None,
    ),
    (
        "XDOM-02: Comma separated multi-domain activation 'use web, sec'",
        """
use web, sec
parse html "<h1>Hello</h1>" into doc
calculate password entropy for "secretPass123!" into ent
""",
        lambda ns: ns.get("doc") is not None and ns.get("ent") is not None,
    ),
    (
        "XDOM-03: 'and' separated multi-domain activation 'use web and sec'",
        """
use web and sec
parse html "<h1>Hello</h1>" into doc
calculate password entropy for "secretPass123!" into ent
""",
        lambda ns: ns.get("doc") is not None and ns.get("ent") is not None,
    ),
    (
        "XDOM-04: 'using' keyword multi-domain 'using web, sec, bio'",
        """
using web, sec, bio
parse html "<h1>Hello</h1>" into doc
calculate password entropy for "secretPass123!" into ent
transcribe dna "ACGT" into rna
""",
        lambda ns: ns.get("doc") is not None and ns.get("ent") is not None and ns.get("rna") is not None,
    ),
    (
        "XDOM-05: Multiple separate 'use' statements (Web + Sec + Bio)",
        """
use web
use sec
use bio
parse html "<h1>Hello</h1>" into doc
calculate password entropy for "secretPass123!" into ent
transcribe dna "ACGT" into rna
""",
        lambda ns: ns.get("doc") is not None and ns.get("ent") is not None and ns.get("rna") is not None,
    ),
    (
        "XDOM-06: Bio output passed into Sec domain",
        """
use bio
use sec
transcribe dna "ACGT" into rna
calculate password entropy for rna into ent
""",
        lambda ns: ns.get("rna") == "ACGU" and ns.get("ent") is not None,
    ),
    (
        "XDOM-07: Web + Data + NLP multi-domain pipeline",
        """
use nlp
tokenize text "Hello world doomscript" into tokens
set tok_count to count of tokens
""",
        lambda ns: ns.get("tok_count") == 3,
    ),
    (
        "XDOM-08: Cross-Domain Chaining in ONE sentence (Web + Core)",
        """
use web
parse html "<h1>Hello</h1>" into doc, then say "Parsed successfully"
""",
        lambda ns: ns.get("doc") is not None,
    ),
    (
        "XDOM-09: Cross-Domain Chaining in ONE sentence (Bio + Sec)",
        """
use bio
use sec
transcribe dna "ACGT" into rna, then calculate password entropy for rna into ent
""",
        lambda ns: ns.get("rna") == "ACGU" and ns.get("ent") is not None,
    ),
    (
        "XDOM-10: Implicit domain execution without 'use web'",
        """
parse html "<h1>Hello</h1>" into doc
""",
        lambda ns: ns.get("doc") is not None,
    ),
    (
        "XDOM-11: Implicit domain execution without 'use bio'",
        """
transcribe dna "ACGT" into rna
""",
        lambda ns: ns.get("rna") == "ACGU",
    ),
    (
        "XDOM-12: Explicit domain prefix 'bio.transcribe ...'",
        """
bio.transcribe dna "ACGT" into rna
""",
        lambda ns: ns.get("rna") == "ACGU",
    ),
    (
        "XDOM-13: Explicit domain prefix in chained statement",
        """
bio.transcribe dna "ACGT" into rna, then say rna
""",
        lambda ns: ns.get("rna") == "ACGU",
    ),
    (
        "XDOM-14: Scoped domain block 'in bio:'",
        """
in bio:
    transcribe dna "ACGT" into rna
say rna
""",
        lambda ns: ns.get("rna") == "ACGU",
    ),
    (
        "XDOM-15: Consecutive scoped domain blocks",
        """
in bio:
    transcribe dna "ACGT" into rna
in sec:
    calculate password entropy for rna into ent
""",
        lambda ns: ns.get("rna") == "ACGU" and ns.get("ent") is not None,
    ),
]


@pytest.mark.parametrize("name,code,validator", audit_cases, ids=[c[0].split(":")[0] for c in audit_cases])
def test_long_chaining_and_cross_domain(name, code, validator):
    reg = get_domain_registry()
    reg.reset_active()
    ns = {}
    ast = compile_to_ast(code)
    execute(ast, ns)
    assert validator(ns), f"Validation failed for {name} with namespace: {ns}"
