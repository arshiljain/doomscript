"""
Declarative Registry for DoomScript Research Phrases and Dual-Form Grammar Integration.
Single source of truth for research syntax, mappings, and LSP completions.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import re


class ResearchRule:
    """
    Defines a research phrase rule that supports both:
    1. Statement form: `<verb_pattern> into <target>`
    2. Expression form: `<target> = <expr_pattern>` or inline expression
    """

    def __init__(
        self,
        name: str,
        category: str,
        description: str,
        expr_pattern: str,
        py_template: str,
    ):
        self.name = name
        self.category = category
        self.description = description
        self.expr_pattern = expr_pattern
        self.py_template = py_template
        self.compiled_expr = re.compile(f"^\\s*{expr_pattern}\\s*$", re.IGNORECASE)
        self.compiled_into = re.compile(f"^\\s*{expr_pattern}\\s+into\\s+([A-Za-z_]\\w*)\\s*$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Declarative Rule Table
# ---------------------------------------------------------------------------

RESEARCH_RULES: List[ResearchRule] = [
    # --- Statistics & Hypothesis Testing ---
    ResearchRule(
        name="welch_t_test",
        category="stats",
        description="Welch's two-sample t-test for unequal variances",
        expr_pattern=r"test\s+(?:that\s+)?means\s+of\s+([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)\s+are\s+equal\s+using\s+welch\s+t\s+test",
        py_template="welch_t_test({1}, {2})",
    ),
    ResearchRule(
        name="student_t_test",
        category="stats",
        description="Student's two-sample t-test assuming equal variances",
        expr_pattern=r"test\s+(?:that\s+)?means\s+of\s+([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)\s+are\s+equal\s+using\s+student\s+t\s+test",
        py_template="student_t_test({1}, {2})",
    ),
    ResearchRule(
        name="mann_whitney_u_test",
        category="stats",
        description="Mann-Whitney U rank-sum test",
        expr_pattern=r"test\s+(?:that\s+)?distributions\s+of\s+([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)\s+are\s+equal\s+using\s+mann\s+whitney(?:\s+u)?\s+test",
        py_template="mann_whitney_u_test({1}, {2})",
    ),
    ResearchRule(
        name="one_way_anova",
        category="stats",
        description="One-Way Analysis of Variance across groups",
        expr_pattern=r"test\s+(?:that\s+)?means\s+of\s+([A-Za-z_]\w*)\s+are\s+equal\s+using\s+anova",
        py_template="one_way_anova({1})",
    ),
    ResearchRule(
        name="chi_square_test",
        category="stats",
        description="Chi-Square test of independence on contingency table",
        expr_pattern=r"test\s+(?:that\s+)?independence\s+of\s+([A-Za-z_]\w*)\s+using\s+chi\s+square",
        py_template="chi_square_test({1})",
    ),
    ResearchRule(
        name="confidence_interval",
        category="stats",
        description="Confidence interval for sample mean at specified percentage",
        expr_pattern=r"confidence\s+interval\s+of\s+([A-Za-z_]\w*)\s+at\s+(\d+(?:\.\d+)?)\s*(?:%|percent)",
        py_template="confidence_interval({1}, float({2}) / 100.0)",
    ),
    ResearchRule(
        name="wilson_score_interval",
        category="stats",
        description="Wilson score interval for binomial proportions",
        expr_pattern=r"(?:wilson\s+score\s+interval|wilson_score_interval)\s+of\s+([A-Za-z_]\w*|\d+)\s+out\s+of\s+([A-Za-z_]\w*|\d+)\s+at\s+(\d+(?:\.\d+)?)\s*(?:%|percent)",
        py_template="wilson_score_interval({1}, {2}, float({3}) / 100.0)",
    ),
    ResearchRule(
        name="bca_bootstrap",
        category="stats",
        description="Bias-Corrected and Accelerated (BCa) bootstrap interval",
        expr_pattern=r"bootstrap\s+confidence\s+interval\s+of\s+([A-Za-z_]\w*)\s+using\s+([A-Za-z_]\w*)",
        py_template="bca_bootstrap({1}, {2})",
    ),
    ResearchRule(
        name="adjust_p_values_holm",
        category="stats",
        description="Holm-Bonferroni FWER p-value adjustment",
        expr_pattern=r"adjust\s+p\s+values\s+([A-Za-z_]\w*)\s+using\s+holm",
        py_template='adjust_p_values({1}, method="holm")',
    ),
    ResearchRule(
        name="adjust_p_values_bh",
        category="stats",
        description="Benjamini-Hochberg FDR p-value adjustment",
        expr_pattern=r"adjust\s+p\s+values\s+([A-Za-z_]\w*)\s+using\s+(?:benjamini\s+hochberg|bh|fdr)",
        py_template='adjust_p_values({1}, method="benjamini_hochberg")',
    ),
    ResearchRule(
        name="pearson_correlation",
        category="stats",
        description="Pearson correlation coefficient between two numeric lists",
        expr_pattern=r"(?:test\s+)?correlation\s+between\s+([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)\s+using\s+pearson",
        py_template="pearson_correlation({1}, {2})",
    ),
    ResearchRule(
        name="spearman_correlation",
        category="stats",
        description="Spearman rank-order correlation between two numeric lists",
        expr_pattern=r"(?:test\s+)?correlation\s+between\s+([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)\s+using\s+spearman",
        py_template="spearman_correlation({1}, {2})",
    ),
    ResearchRule(
        name="wilcoxon_signed_rank",
        category="stats",
        description="Wilcoxon signed-rank test for paired samples",
        expr_pattern=r"test\s+paired\s+samples\s+([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)\s+using\s+wilcoxon",
        py_template="wilcoxon_signed_rank({1}, {2})",
    ),
    ResearchRule(
        name="fisher_exact_test",
        category="stats",
        description="Fisher's exact test for 2x2 contingency table",
        expr_pattern=r"test\s+(?:that\s+)?independence\s+of\s+([A-Za-z_]\w*)\s+using\s+fisher\s+exact",
        py_template="fisher_exact_test({1})",
    ),
    ResearchRule(
        name="metropolis_hastings",
        category="stats",
        description="Metropolis-Hastings MCMC sampling with diagnostics",
        expr_pattern=r"sample\s+from\s+([A-Za-z_]\w*)\s+using\s+metropolis\s+hastings\s+with\s+initial\s+([A-Za-z_]\w*|\[[^\]]+\])",
        py_template="metropolis_hastings({1}, initial={2})",
    ),

    # --- Graph & Network Algorithms ---
    ResearchRule(
        name="create_graph",
        category="graph",
        description="Instantiate a new directed ResearchGraph",
        expr_pattern=r"(?:create\s+)?(?:a\s+)?(?:new\s+)?research\s+graph",
        py_template="ResearchGraph()",
    ),
    ResearchRule(
        name="dijkstra_shortest_path",
        category="graph",
        description="Shortest path between two nodes via Dijkstra",
        expr_pattern=r"find\s+shortest\s+path\s+from\s+(.+?)\s+to\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+using\s+dijkstra",
        py_template="dijkstra_shortest_path({3}, {1}, {2})",
    ),
    ResearchRule(
        name="bellman_ford",
        category="graph",
        description="Single-source shortest paths via Bellman-Ford",
        expr_pattern=r"find\s+shortest\s+paths\s+from\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+using\s+bellman\s+ford",
        py_template="bellman_ford({2}, {1})",
    ),
    ResearchRule(
        name="floyd_warshall",
        category="graph",
        description="All-pairs shortest paths via Floyd-Warshall",
        expr_pattern=r"find\s+all\s+pairs\s+shortest\s+paths\s+in\s+([A-Za-z_]\w*)\s+using\s+floyd\s+warshall",
        py_template="floyd_warshall({1})",
    ),
    ResearchRule(
        name="topological_sort",
        category="graph",
        description="Topological sort with deterministic insertion-order tie breaking",
        expr_pattern=r"topological\s+sort\s+of\s+([A-Za-z_]\w*)",
        py_template="topological_sort({1})",
    ),
    ResearchRule(
        name="edmonds_karp_max_flow",
        category="graph",
        description="Maximum network flow via Edmonds-Karp",
        expr_pattern=r"(?:maximum|max)\s+flow\s+from\s+(.+?)\s+to\s+(.+?)\s+in\s+([A-Za-z_]\w*)(?:\s+using\s+edmonds\s+karp)?",
        py_template="edmonds_karp_max_flow({3}, {1}, {2})",
    ),

    # --- Dynamic Programming ---
    ResearchRule(
        name="levenshtein_distance",
        category="dp",
        description="Levenshtein edit distance between two strings",
        expr_pattern=r"(?:edit|levenshtein)\s+distance\s+between\s+(.+?)\s+and\s+(.+)",
        py_template="levenshtein_distance({1}, {2})",
    ),
    ResearchRule(
        name="longest_common_subsequence",
        category="dp",
        description="Longest Common Subsequence between two strings",
        expr_pattern=r"longest\s+common\s+subsequence\s+(?:between|of)\s+(.+?)\s+and\s+(.+)",
        py_template="longest_common_subsequence({1}, {2})",
    ),
    ResearchRule(
        name="knapsack_01",
        category="dp",
        description="0/1 Knapsack dynamic programming solver",
        expr_pattern=r"(?:solve\s+)?(?:0\s+1\s+)?knapsack\s+with\s+weights\s+([A-Za-z_]\w*|\[[^\]]+\])\s+(?:and\s+)?values\s+([A-Za-z_]\w*|\[[^\]]+\])\s+(?:at|with)?\s*capacity\s+(\d+|[A-Za-z_]\w*)",
        py_template="knapsack_01({1}, {2}, {3})",
    ),

    # --- Autograd, Tensors & Optimizers ---
    ResearchRule(
        name="scalar_var",
        category="autograd",
        description="Wrap a float into a reverse-mode Scalar autograd variable",
        expr_pattern=r"(?:a\s+)?scalar\s+(?:with\s+value\s+|value\s+)?(.+)",
        py_template="Scalar({1})",
    ),
    ResearchRule(
        name="tensor_var",
        category="autograd",
        description="Wrap an array into a multidimensional Tensor",
        expr_pattern=r"(?:a\s+)?tensor\s+(?:from\s+)?(.+)",
        py_template="Tensor({1})",
    ),
    ResearchRule(
        name="matrix_multiplication",
        category="autograd",
        description="2D matrix multiplication between tensors",
        expr_pattern=r"matrix\s+multiply\s+([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)",
        py_template="{1}.matmul({2})",
    ),
    ResearchRule(
        name="tensor_sum",
        category="autograd",
        description="Sum reduction across a tensor to a single scalar",
        expr_pattern=r"(?:tensor\s+sum\s+of|sum\s+of\s+tensor)\s+([A-Za-z_]\w*)",
        py_template="{1}.sum()",
    ),
    ResearchRule(
        name="adam_optimizer",
        category="optim",
        description="Adam optimizer for a list of Scalar parameters",
        expr_pattern=r"(?:create\s+)?adam\s+optimizer\s+for\s+(.+?)\s+with\s+learning\s+rate\s+([^\s;,\n]+)",
        py_template="Adam({1}, lr={2})",
    ),
    ResearchRule(
        name="sgd_optimizer",
        category="optim",
        description="SGD with momentum optimizer for Scalar parameters",
        expr_pattern=r"(?:create\s+)?sgd\s+optimizer\s+for\s+(.+?)\s+with\s+learning\s+rate\s+([^\s;,\n]+)\s+and\s+momentum\s+([^\s;,\n]+)",
        py_template="SGDMomentum({1}, lr={2}, momentum={3})",
    ),
    ResearchRule(
        name="check_grad",
        category="autograd",
        description="Verify gradients numerically via central differences",
        expr_pattern=r"check\s+gradient\s+of\s+([A-Za-z_]\w*)\s+at\s+([A-Za-z_]\w*|\[[^\]]+\])",
        py_template="check_grad({1}, {2})",
    ),
]


# ---------------------------------------------------------------------------
# Result and Attribute Property Map (Dual Form: "x's attr" and "attr of x")
# ---------------------------------------------------------------------------

RESEARCH_PROPERTIES = {
    "p value": "p_value",
    "test statistic": "statistic",
    "statistic": "statistic",
    "degrees of freedom": "df",
    "effect size": "effect_size",
    "r hat": "r_hat",
    "acceptance rate": "acceptance_rate",
    "effective sample size": "ess",
    "samples": "samples",
    "gradient": "grad",
    "value": "data",
}


def _clean_arg(arg: str) -> str:
    s = arg.strip()
    s = re.sub(r"\b(?:a\s+list\s+of|list\s+of)\s+([^,\)]+)", r"[\1]", s, flags=re.IGNORECASE)
    return s


_STRING_REGEX = re.compile(r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\]|\\.)*"|(?<!\w)\'(?:[^\'\\]|\\.)*\')')


def _mask_strings(text: str) -> Tuple[str, List[str]]:
    strings: List[str] = []
    def repl(m: re.Match) -> str:
        idx = len(strings)
        strings.append(m.group(0))
        return f"__STR_LIT_{idx}__"
    return _STRING_REGEX.sub(repl, text), strings


def _unmask_strings(text: str, strings: List[str]) -> str:
    for idx, s in enumerate(strings):
        text = text.replace(f"__STR_LIT_{idx}__", s)
    return text


def apply_research_normalization(line: str) -> Optional[str]:
    """
    Applies single-source research phrase rules to a single line of code.
    Handles:
    1. Statement forms (`... into target`)
    2. Explicit assignments (`target = ...`)
    3. Action verbs (`compute gradient of ...`, `add edge from ...`, `step opt`)
    4. Attribute / property access (`res's p value`, `p value of res`)
    5. Pure expression replacements
    """
    masked_line, strings = _mask_strings(line)
    cleaned = masked_line.strip()

    # 1. Action verbs without 'into'
    # compute gradient of <expr> -> <expr>.backward()
    grad_m = re.match(r"^compute\s+gradient\s+of\s+(.+)$", cleaned, re.IGNORECASE)
    if grad_m:
        raw_res = f"({grad_m.group(1).strip()}).backward()"
        return _unmask_strings(raw_res, strings)

    # add edge from <u> to <v> [with weight <w>] to <g>
    edge_m = re.match(
        r"^add\s+edge\s+from\s+(.+?)\s+to\s+(.+?)(?:\s+with\s+weight\s+(.+?))?\s+(?:to|in)\s+([A-Za-z_]\w*)$",
        cleaned,
        re.IGNORECASE,
    )
    if edge_m:
        u = _clean_arg(edge_m.group(1))
        v = _clean_arg(edge_m.group(2))
        w = _clean_arg(edge_m.group(3)) if edge_m.group(3) else "1.0"
        g = edge_m.group(4).strip()
        raw_res = f"{g}.add_edge({u}, {v}, {w})"
        return _unmask_strings(raw_res, strings)

    # step <opt> / optimize step with <opt>
    step_m = re.match(r"^(?:step|optimize\s+step\s+with)\s+([A-Za-z_]\w*)$", cleaned, re.IGNORECASE)
    if step_m:
        raw_res = f"{step_m.group(1)}.step()"
        return _unmask_strings(raw_res, strings)

    # zero gradients for <opt> / reset gradients for <opt>
    zero_m = re.match(r"^(?:zero|reset)\s+gradients\s+for\s+([A-Za-z_]\w*)$", cleaned, re.IGNORECASE)
    if zero_m:
        raw_res = f"{zero_m.group(1)}.zero_grad()"
        return _unmask_strings(raw_res, strings)

    # 2. Check each declarative rule for statement form (`... into target`)
    for rule in RESEARCH_RULES:
        m_into = rule.compiled_into.match(cleaned)
        if m_into:
            target = m_into.group(m_into.lastindex)
            # Fill template arguments
            args = [_clean_arg(m_into.group(i)) for i in range(1, m_into.lastindex)]
            py_call = rule.py_template
            for idx, arg in enumerate(args, 1):
                py_call = py_call.replace(f"{{{idx}}}", arg)
            raw_res = f"set {target} to {py_call}"
            return _unmask_strings(raw_res, strings)

    # 3. Check for assignment form: `target = <phrase>`
    assign_m = re.match(r"^([A-Za-z_]\w*)\s*=\s*(.+)$", cleaned)
    if assign_m:
        target = assign_m.group(1).strip()
        rhs = assign_m.group(2).strip()
        for rule in RESEARCH_RULES:
            m_expr = rule.compiled_expr.match(rhs)
            if m_expr:
                args = [_clean_arg(m_expr.group(i)) for i in range(1, len(m_expr.groups()) + 1)]
                py_call = rule.py_template
                for idx, arg in enumerate(args, 1):
                    py_call = py_call.replace(f"{{{idx}}}", arg)
                raw_res = f"set {target} to {py_call}"
                return _unmask_strings(raw_res, strings)

    # 4. In-place statement or expression transformation
    res_line = cleaned
    for rule in RESEARCH_RULES:
        # Replace inline occurrences of the expression
        def repl(match: re.Match) -> str:
            args = [_clean_arg(match.group(i)) for i in range(1, len(match.groups()) + 1)]
            py_call = rule.py_template
            for idx, arg in enumerate(args, 1):
                py_call = py_call.replace(f"{{{idx}}}", arg)
            return py_call

        res_line = re.sub(rule.expr_pattern, repl, res_line, flags=re.IGNORECASE)

    # 5. Dual-form property access: "x's p value", "x[0]'s p value", and "p value of x"
    for eng_prop, py_prop in RESEARCH_PROPERTIES.items():
        # x's prop or x[idx]'s prop
        res_line = re.sub(
            rf"\b([A-Za-z_]\w*(?:\[[^\]]+\])?)'s\s+{re.escape(eng_prop)}\b",
            rf"\1.{py_prop}",
            res_line,
            flags=re.IGNORECASE,
        )
        # prop of x
        res_line = re.sub(
            rf"\b{re.escape(eng_prop)}\s+of\s+([A-Za-z_]\w*(?:\[[^\]]+\])?)\b",
            rf"\1.{py_prop}",
            res_line,
            flags=re.IGNORECASE,
        )

    unmasked = _unmask_strings(res_line, strings)
    return unmasked if unmasked != line.strip() else None

