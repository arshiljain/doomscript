"""Shared Conformance Test Runner verifying semantic parity between execution and Python export."""

from typing import Any, Dict, List, Optional, Tuple
import math
from doomscript.compiler.engine import execute, export_to_python

EXCLUDE_KEYS = {
    "Record", "sleep", "percent_of", "write_file", "append_file", "read_file",
    "count_of", "beep", "play_sound", "open_window", "draw_circle", "draw_rectangle",
    "draw_text", "clear_screen", "refresh_screen", "fetch_json", "fetch_text",
    "download_file", "time_future", "time_past", "random_range", "pick_random",
    "shuffle_list", "db_save", "db_query", "db_delete", "db_count", "log_info",
    "log_warn", "log_error", "ask_text", "ask_number", "ask_boolean", "ask_choice",
    "ds_mean", "ds_median", "ds_std_dev", "ds_variance", "mean", "median",
    "std_dev", "stdev", "stats_stdev", "variance", "stats_variance", "stats_median",
    "PI", "E", "INF", "NAN", "is_nan", "is_inf", "math_sin", "math_cos", "math_tan",
    "math_sqrt", "math_abs", "math_round", "math_clamp", "math_pow", "math_mod",
    "math_floor", "math_ceil", "math_log", "math_log10", "str_lower", "str_upper",
    "str_title", "str_trim", "str_split", "str_join", "str_replace", "str_contains",
    "str_starts_with", "str_ends_with", "str_length", "unique_items", "first_n_items",
    "last_n_items", "sorted_list", "reversed_list", "agg_sum", "agg_avg", "agg_min",
    "agg_max", "agg_count", "date_now", "date_today", "date_format", "date_add_days",
    "date_diff_days", "format_currency", "format_percentage", "format_number",
    "create_table", "table_column", "table_row_count", "table_filter", "table_sort",
    "assert_true", "assert_false", "assert_equals", "assert_not_equals",
    "assert_greater", "assert_less", "assert_contains", "assert_in_range",
    "inspect_dataset", "profile_dataset", "clean_dataset", "join_datasets",
    "execute_data_ir", "execute_ml_ir", "execute_db_ir", "execute_net_ir",
    "execute_sim_ir", "execute_dsa_ir", "run_dsa_benchmark", "math", "sys",
    "pd", "np", "sklearn", "sqlite3", "requests",
}


def _approx_eq(a: Any, b: Any, tol: float = 1e-4) -> bool:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= tol
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return False
        return all(_approx_eq(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return False
        return all(_approx_eq(a[k], b[k], tol) for k in a)
    return a == b


def assert_execution_and_export_parity(
    source: str,
    expected_vars: Optional[List[str]] = None,
    check_approx: bool = False,
    tolerance: float = 1e-4,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Runs source via in-memory interpreter AND exported Python AST, asserting variable parity."""
    # 1. Direct In-Memory Interpretation
    env_direct = execute(source)

    # 2. Python AST Export & Execution
    py_code = export_to_python(source)
    env_export: Dict[str, Any] = {}
    exec(py_code, env_export)

    # 3. Determine target variables to check
    if expected_vars is not None:
        target_keys = expected_vars
    else:
        target_keys = [
            k for k in env_direct.keys()
            if not k.startswith("_") and k not in EXCLUDE_KEYS
        ]

    for k in target_keys:
        assert k in env_direct, f"Variable '{k}' not found in interpreter environment"
        assert k in env_export, f"Variable '{k}' not found in exported Python environment"

        v_direct = env_direct[k]
        v_export = env_export[k]

        if check_approx:
            assert _approx_eq(v_direct, v_export, tolerance), (
                f"Parity mismatch for variable '{k}':\n"
                f"Interpreter: {v_direct}\n"
                f"Exported:    {v_export}"
            )
        else:
            assert v_direct == v_export, (
                f"Parity mismatch for variable '{k}':\n"
                f"Interpreter: {v_direct}\n"
                f"Exported:    {v_export}"
            )

    return env_direct, env_export
