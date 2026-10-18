import sys
import os
import argparse
import io
import re
import traceback
from pathlib import Path

# Add src to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR / "src"
if SRC_DIR.exists() and str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from doomscript.compiler.engine import compile_to_ast, execute
from doomscript.grammar.phrases import normalize


def parse_corpus(file_path: Path):
    categories = []
    current_category = "general"
    current_case = None

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    case_id_counter = {}

    for line in lines:
        raw_line = line.rstrip("\r\n")
        stripped = raw_line.strip()

        if stripped.startswith(";;"):
            continue

        if stripped.startswith("##"):
            current_category = stripped[2:].strip()
            continue

        if stripped.startswith("@"):
            if current_case:
                categories.append(current_case)
            tier = stripped[1:].strip().upper()
            cat_slug = re.sub(r"[^a-z0-9]+", "-", current_category.lower()).strip("-")
            case_id_counter[cat_slug] = case_id_counter.get(cat_slug, 0) + 1
            cid = f"{cat_slug}-{case_id_counter[cat_slug]:02d}"
            current_case = {
                "id": cid,
                "category": current_category,
                "tier": tier,
                "source_lines": [],
                "stdin": None,
                "expected": [],
            }
            continue

        if current_case is not None:
            if stripped.startswith("<<"):
                stdin_val = stripped[2:].strip()
                if current_case["stdin"] is None:
                    current_case["stdin"] = stdin_val + "\n"
                else:
                    current_case["stdin"] += stdin_val + "\n"
            elif stripped.startswith("=>>"):
                expected_end = stripped[3:].strip()
                current_case["expected"].append(("endswith", expected_end))
            elif stripped.startswith("=>"):
                expected_line = stripped[2:].strip()
                current_case["expected"].append(("exact", expected_line))
            else:
                current_case["source_lines"].append(raw_line)

    if current_case:
        categories.append(current_case)

    # Clean leading/trailing blank lines in source_lines
    for c in categories:
        while c["source_lines"] and not c["source_lines"][0].strip():
            c["source_lines"].pop(0)
        while c["source_lines"] and not c["source_lines"][-1].strip():
            c["source_lines"].pop()

    return categories


def num_equal(a: str, b: str) -> bool:
    try:
        fa = float(a)
        fb = float(b)
        return fa == fb
    except ValueError:
        return a == b


TEMP_FILES = ["a.txt", "b.txt", "d.csv", "e.txt", "t.txt", "o.csv", "nope.txt"]


def cleanup_test_artifacts():
    for fn in TEMP_FILES:
        p = Path(fn)
        if p.exists():
            try:
                p.unlink()
            except OSError:
                pass


def run_single_case(case: dict) -> tuple:
    if case.get("category") == "files":
        cleanup_test_artifacts()
    source = "\n".join(case["source_lines"])
    old_stdin = sys.stdin
    old_stdout = sys.stdout

    stdin_buf = io.StringIO(case["stdin"] if case["stdin"] else "")
    stdout_buf = io.StringIO()

    try:
        sys.stdin = stdin_buf
        sys.stdout = stdout_buf

        # 1. Normalization phase
        try:
            norm = normalize(source)
        except Exception as e:
            return "PARSE_ERROR", f"Normalization error: {e}"

        # 2. Parsing phase
        try:
            tree = compile_to_ast(norm)
        except Exception as e:
            return "PARSE_ERROR", f"{type(e).__name__}: {e}"

        # 3. Execution phase
        try:
            execute(tree)
        except Exception as e:
            return "RUNTIME_ERROR", f"{type(e).__name__}: {e}"

        actual_stdout = stdout_buf.getvalue()
        actual_lines = [l.strip() for l in actual_stdout.strip().splitlines() if l.strip()]

        # Verification
        expected_rules = case["expected"]
        if not expected_rules:
            return "PASS", ""

        if any(r[0] == "endswith" for r in expected_rules):
            for r_type, r_val in expected_rules:
                if r_type == "endswith":
                    trimmed_actual = actual_stdout.strip()
                    if not trimmed_actual.endswith(r_val):
                        return "FAIL", f"Expected stdout to end with '{r_val}', got '{trimmed_actual}'"
            return "PASS", ""

        # Exact line matches
        if len(actual_lines) != len(expected_rules):
            return "FAIL", f"Expected {len(expected_rules)} output lines, got {len(actual_lines)}: {actual_lines}"

        for i, (r_type, exp) in enumerate(expected_rules):
            act = actual_lines[i]
            if not num_equal(act, exp):
                return "FAIL", f"Line {i+1} mismatch: expected '{exp}', got '{act}'"

        return "PASS", ""
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def main():
    parser = argparse.ArgumentParser(description="DoomScript English Corpus Runner")
    parser.add_argument("--corpus", default="english_corpus/corpus.txt", help="Path to corpus.txt")
    parser.add_argument("--tier", choices=["D", "N"], help="Run only tier D or N")
    parser.add_argument("--status", help="Filter by status (PASS, PARSE_ERROR, RUNTIME_ERROR, FAIL)")
    parser.add_argument("--fail-under", type=float, help="Exit with code 1 if pass rate is below this percentage")
    parser.add_argument("--markdown", help="Save markdown report to file")
    args = parser.parse_args()

    corpus_path = Path(args.corpus)
    if not corpus_path.exists():
        alt = SCRIPT_DIR / args.corpus
        if alt.exists():
            corpus_path = alt
        else:
            print(f"Error: {args.corpus} not found.")
            sys.exit(1)

    cases = parse_corpus(corpus_path)
    if args.tier:
        cases = [c for c in cases if c["tier"] == args.tier]

    results = []
    category_stats = {}
    tier_stats = {"D": {"pass": 0, "total": 0}, "N": {"pass": 0, "total": 0}}

    cleanup_test_artifacts()
    for case in cases:
        print(f"[{case['id']}] {case['tier']} ...", flush=True)
        status, detail = run_single_case(case)
        cat = case["category"]
        tier = case["tier"]

        if cat not in category_stats:
            category_stats[cat] = {"pass": 0, "total": 0}
        category_stats[cat]["total"] += 1
        tier_stats[tier]["total"] += 1

        if status == "PASS":
            category_stats[cat]["pass"] += 1
            tier_stats[tier]["pass"] += 1

        results.append({
            "case": case,
            "status": status,
            "detail": detail
        })

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    pass_pct = (passed / total * 100.0) if total > 0 else 0.0

    print(f"\n=======================================================")
    print(f"DoomScript English Corpus Results: {passed}/{total} passed ({pass_pct:.1f}%)")
    print(f"=======================================================")
    for t in ["D", "N"]:
        t_pass = tier_stats[t]["pass"]
        t_tot = tier_stats[t]["total"]
        t_pct = (t_pass / t_tot * 100.0) if t_tot > 0 else 0.0
        print(f"Tier {t}: {t_pass}/{t_tot} ({t_pct:.1f}%)")

    # If status filter specified
    if args.status:
        print(f"\nCases matching status '{args.status}':")
        for r in results:
            if r["status"] == args.status:
                c = r["case"]
                first_l = c["source_lines"][0] if c["source_lines"] else ""
                print(f"  [{c['id']}] {c['tier']} | {first_l[:35]:<35} | {r['detail']}")

    # Markdown export if requested
    if args.markdown:
        md_lines = [
            f"# DoomScript English Corpus Report",
            f"\n**{passed}/{total} passed ({pass_pct:.1f}%)**\n",
            f"- Documented syntax (D): {tier_stats['D']['pass']}/{tier_stats['D']['total']} ({(tier_stats['D']['pass']/max(1, tier_stats['D']['total'])*100):.1f}%)",
            f"- Natural English (N): {tier_stats['N']['pass']}/{tier_stats['N']['total']} ({(tier_stats['N']['pass']/max(1, tier_stats['N']['total'])*100):.1f}%)\n",
            f"## By Category\n",
            f"| Category | Passed | Rate |",
            f"|---|---|---|",
        ]
        for cat, s in category_stats.items():
            rate = (s["pass"] / s["total"] * 100) if s["total"] else 0
            md_lines.append(f"| {cat} | {s['pass']}/{s['total']} | {rate:.1f}% |")

        md_lines.extend([
            f"\n## Failures\n",
            f"| ID | Tier | Status | First line | Detail |",
            f"|---|---|---|---|---|",
        ])
        for r in results:
            if r["status"] != "PASS":
                c = r["case"]
                first_l = c["source_lines"][0] if c["source_lines"] else ""
                md_lines.append(f"| {c['id']} | {c['tier']} | {r['status']} | `{first_l}` | {r['detail'][:80]} |")

        with open(args.markdown, "w", encoding="utf-8") as out_f:
            out_f.write("\n".join(md_lines) + "\n")
        print(f"\nMarkdown report written to {args.markdown}")

    if args.fail_under and pass_pct < args.fail_under:
        print(f"\nFAIL: Pass rate {pass_pct:.1f}% is below required {args.fail_under}%")
        sys.exit(1)


if __name__ == "__main__":
    main()
