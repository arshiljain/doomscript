"""
DoomScript Compiler Engine
Coordinates parsing, AST transformation, transpilation, and execution.
"""

import ast
from pathlib import Path
from typing import Any, Union, Dict, Optional
from lark import Lark
from lark.indenter import PythonIndenter

import math
from functools import lru_cache
from doomscript.compiler.transformer import DoomToPython
from doomscript.grammar.phrases import normalize, normalize_with_map
from doomscript import runtime

GRAMMAR_PATH = Path(__file__).parent.parent / "grammar" / "doom.lark"

import threading

_THREAD_LOCAL = threading.local()

def get_parser() -> Lark:
    """Returns thread-isolated Lark parser instance to guarantee thread safety during concurrent compilations."""
    parser = getattr(_THREAD_LOCAL, "parser", None)
    if parser is None:
        with open(GRAMMAR_PATH, "r", encoding="utf-8") as f:
            grammar = f.read()
        parser = Lark(
            grammar,
            parser="lalr",
            postlex=PythonIndenter(),
            start="start",
            propagate_positions=True
        )
        _THREAD_LOCAL.parser = parser
    return parser

def compile_to_ast(source: str, filename: str = "<doom>") -> ast.Module:
    """Parses DoomScript source and returns a Python ast.Module."""
    from doomscript.domains.registry import get_domain_registry
    from doomscript.compiler.advisor import DidYouMeanAdvisor
    from doomscript.exceptions import DoomScriptSyntaxError
    import lark.exceptions

    with get_domain_registry().compilation_context():
        get_domain_registry().reset_active()
        normalized_source, line_map = normalize_with_map(source)
        if not normalized_source.endswith("\n"):
            normalized_source += "\n"
        parser = get_parser()
        try:
            tree = parser.parse(normalized_source)
        except (lark.exceptions.UnexpectedInput, lark.exceptions.LarkError) as parse_err:
            norm_line_num = getattr(parse_err, "line", 1)
            orig_line_num = line_map.get(norm_line_num, norm_line_num)
            orig_lines = source.splitlines()
            orig_line = orig_lines[orig_line_num - 1] if 0 < orig_line_num <= len(orig_lines) else ""
            active_dom_names = [d.name for d in get_domain_registry().get_active_domains()]
            col = getattr(parse_err, "column", None)
            failing_token = None
            if hasattr(parse_err, "token"):
                failing_token = getattr(parse_err.token, "value", str(parse_err.token))
            suggestion = DidYouMeanAdvisor.find_suggestion(
                orig_line,
                active_domains=active_dom_names,
                source=source,
                failing_token=failing_token,
                col=col,
            )
            raise DoomScriptSyntaxError(
                f"Syntax error at line {orig_line_num}",
                line=orig_line_num,
                column=col,
                source_line=orig_line.strip(),
                suggestion=suggestion,
                file_path=filename,
            ) from parse_err

        transformer = DoomToPython(line_map=line_map)
        return transformer.transform(tree)

def transpile(source: str) -> str:
    """Transpiles DoomScript source into formatted Python code."""
    py_ast = compile_to_ast(source)
    return ast.unparse(py_ast)

def export_to_python(source: str) -> str:
    """Exports DoomScript source into a self-contained, standalone Python script with runtime imports."""
    import re
    is_leetcode = bool(re.search(r"^\s*target\s+leetcode\b", source, re.MULTILINE | re.IGNORECASE))
    py_ast = compile_to_ast(source)
    try:
        from doomscript.viz.exporter import transform_viz_ast
        py_ast, _ = transform_viz_ast(py_ast)
    except (ImportError, ModuleNotFoundError):
        pass
    except Exception as e:
        from doomscript.exceptions import DoomCompilationError
        raise DoomCompilationError(f"Visualization AST export transformation failed: {e}") from e

    try:
        from doomscript.domains.exporter import transform_domains_ast
        py_ast = transform_domains_ast(py_ast)
    except (ImportError, ModuleNotFoundError):
        pass
    except Exception as e:
        from doomscript.exceptions import DoomCompilationError
        raise DoomCompilationError(f"Domain AST export transformation failed: {e}") from e

    if is_leetcode:
        sol_body = []
        other_body = []
        for stmt in py_ast.body:
            if isinstance(stmt, ast.FunctionDef):
                arg_names = [a.arg for a in stmt.args.args]
                if not arg_names or arg_names[0] != "self":
                    stmt.args.args.insert(0, ast.arg(arg="self", annotation=None))
                sol_body.append(stmt)
                if "_" in stmt.name:
                    parts = stmt.name.split("_")
                    camel_name = parts[0] + "".join(p.capitalize() for p in parts[1:])
                    alias_func = ast.FunctionDef(
                        name=camel_name,
                        args=ast.arguments(
                            posonlyargs=[],
                            args=[ast.arg(arg="self", annotation=None)],
                            vararg=ast.arg(arg="args", annotation=None),
                            kwonlyargs=[],
                            kw_defaults=[],
                            kwarg=ast.arg(arg="kwargs", annotation=None),
                            defaults=[],
                        ),
                        body=[
                            ast.Return(
                                value=ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Name(id="self", ctx=ast.Load()),
                                        attr=stmt.name,
                                        ctx=ast.Load(),
                                    ),
                                    args=[ast.Starred(value=ast.Name(id="args", ctx=ast.Load()), ctx=ast.Load())],
                                    keywords=[ast.keyword(arg=None, value=ast.Name(id="kwargs", ctx=ast.Load()))],
                                )
                            )
                        ],
                        decorator_list=[],
                    )
                    sol_body.append(alias_func)
            else:
                other_body.append(stmt)

        sol_class = ast.ClassDef(
            name="Solution",
            bases=[],
            keywords=[],
            body=sol_body if sol_body else [ast.Pass()],
            decorator_list=[],
        )
        py_ast.body = [sol_class] + other_body
        ast.fix_missing_locations(py_ast)

        code = ast.unparse(py_ast)
        header = (
            "# Generated by DoomScript LeetCode Exporter\n"
            "from typing import List, Optional, Dict, Set, Tuple\n"
            "from doomscript.runtime import *\n"
            "import collections, heapq, math\n\n"
            "# Definition for singly-linked list.\n"
            "class ListNode:\n"
            "    def __init__(self, val=0, next=None):\n"
            "        self.val = val\n"
            "        self.next = next\n\n"
            "# Definition for a binary tree node.\n"
            "class TreeNode:\n"
            "    def __init__(self, val=0, left=None, right=None):\n"
            "        self.val = val\n"
            "        self.left = left\n"
            "        self.right = right\n\n"
        )
        return header + code + "\n"

    code = ast.unparse(py_ast)
    header = (
        "# Generated by DoomScript Exporter\n"
        "from doomscript.runtime import *\n"
        "import math\n\n"
    )
    return header + code + "\n"

def execute(source: Any, custom_globals: dict = None, filename: str = "<doom>") -> dict:
    """Executes DoomScript source code or AST directly and returns the environment dict.

    Security Warning:
        DoomScript executes in-process as native Python bytecode and is
        NOT an isolated security sandbox. Do not execute untrusted scripts
        under the assumption that its English syntax restricts execution capabilities.
    """
    from doomscript.domains.registry import get_domain_registry
    with get_domain_registry().compilation_context():
        return _execute_scoped(source, custom_globals=custom_globals, filename=filename)


def _execute_scoped(source: Any, custom_globals: dict = None, filename: str = "<doom>") -> dict:
    if isinstance(source, ast.AST):
        py_ast = source
    else:
        py_ast = compile_to_ast(source, filename=filename)
    compiled = compile(py_ast, filename=filename, mode="exec")
    
    if custom_globals is not None:
        exec_globals = custom_globals
    else:
        exec_globals = {}
        
    runtime_helpers = {
        "Record": runtime.Record,
        "make_entity": runtime.make_entity,
        "ds_add": runtime.ds_add,
        "ds_remove": runtime.ds_remove,
        "DoomAssertionError": runtime.DoomAssertionError,
        "DoomIndexError": runtime.DoomIndexError,
        "DoomTypeError": runtime.DoomTypeError,
        "DoomValueError": runtime.DoomValueError,
        "DoomAttributeError": runtime.DoomAttributeError,
        "sleep": runtime.sleep,
        "percent_of": runtime.percent_of,
        "write_file": runtime.write_file,
        "append_file": runtime.append_file,
        "read_file": runtime.read_file,
        "count_of": runtime.count_of,
        "beep": runtime.beep,
        "play_sound": runtime.play_sound,
        "open_window": runtime.open_window,
        "draw_circle": runtime.draw_circle,
        "draw_rectangle": runtime.draw_rectangle,
        "draw_text": runtime.draw_text,
        "clear_screen": runtime.clear_screen,
        "refresh_screen": runtime.refresh_screen,
        "fetch_json": runtime.fetch_json,
        "fetch_text": runtime.fetch_text,
        "download_file": runtime.download_file,
        "time_future": runtime.time_future,
        "time_past": runtime.time_past,
        "random_range": runtime.random_range,
        "pick_random": runtime.pick_random,
        "shuffle_list": runtime.shuffle_list,
        "db_save": runtime.db_save,
        "db_load": runtime.db_load,
        "agg_sum": runtime.agg_sum,
        "agg_avg": runtime.agg_avg,
        "agg_max": runtime.agg_max,
        "agg_min": runtime.agg_min,
        "agg_first": runtime.agg_first,
        "agg_last": runtime.agg_last,
        "agg_field": runtime.agg_field,
        "mean": runtime.ds_mean,
        "median": runtime.ds_median,
        "std_dev": runtime.ds_std_dev,
        "stdev": runtime.ds_std_dev,
        "stats_stdev": runtime.ds_std_dev,
        "ds_std_dev": runtime.ds_std_dev,
        "variance": runtime.ds_variance,
        "stats_variance": runtime.ds_variance,
        "ds_variance": runtime.ds_variance,
        "stats_median": runtime.ds_median,
        "PI": math.pi,
        "E": math.e,
        "math": math,
        "INF": float("inf"),
        "min": min,
        "max": max,
        "sum": sum,
        "load_table": runtime.load_table,
        "save_table": runtime.save_table,
        "filter_table": runtime.filter_table,
        "sort_table": runtime.sort_table,
        "group_and_agg_table": runtime.group_and_agg_table,
        "plot_table": runtime.plot_table,
        "str_replace": runtime.str_replace,
        "str_split": runtime.str_split,
        "str_join": runtime.str_join,
        "str_uppercase": runtime.str_uppercase,
        "str_lowercase": runtime.str_lowercase,
        "str_capitalize": runtime.str_capitalize,
        "str_trim": runtime.str_trim,
        "str_starts_with": runtime.str_starts_with,
        "str_ends_with": runtime.str_ends_with,
        "str_matches_pattern": runtime.str_matches_pattern,
        "copy_file": runtime.copy_file,
        "delete_file": runtime.delete_file,
        "create_dir": runtime.create_dir,
        "list_files": runtime.list_files,
        "file_exists": runtime.file_exists,
        "spawn_thread": runtime.spawn_thread,
        "wait_for_thread": runtime.wait_for_thread,
        "add_route": runtime.add_route,
        "start_server": runtime.start_server,
        "stop_server": runtime.stop_server,
        "display_colored": runtime.display_colored,
        "pause_terminal": runtime.pause_terminal,
        "ask_input": runtime.ask_input,
        "ask_choice": runtime.ask_choice,
        "math_round": runtime.math_round,
        "math_clamp": runtime.math_clamp,
        "ask_number": runtime.ask_number,
        "ask_boolean": runtime.ask_boolean,
        "item_of": runtime.item_of,
        "first_n_items": runtime.first_n_items,
        "last_n_items": runtime.last_n_items,
        "sorted_list": runtime.sorted_list,
        "reversed_list": runtime.reversed_list,
        "copy_value": runtime.copy_value,
        "null": None,
        "nil": None,
        "unique_items": runtime.unique_items,
        "insert_list": runtime.insert_list,
        "range_inclusive": runtime.range_inclusive,
        "sort_records": runtime.sort_records,
        "group_by": runtime.group_by,
        "read_csv": runtime.read_csv,
        "write_csv": runtime.write_csv,
        "append_csv": runtime.append_csv,
        "parse_json": runtime.parse_json,
        "stringify_json": runtime.stringify_json,
        "date_today": runtime.date_today,
        "date_now": runtime.date_now,
        "today": runtime.date_today,
        "now": runtime.date_now,
        "date_yesterday": runtime.date_yesterday,
        "date_tomorrow": runtime.date_tomorrow,
        "yesterday": runtime.date_yesterday,
        "tomorrow": runtime.date_tomorrow,
        "to_text": runtime.to_text,
        "to_number": runtime.to_number,
        "str_title": runtime.str_title,
        "math_product": runtime.math_product,
        "math_mod": runtime.math_mod,
        "math_pow": runtime.math_pow,
        "math_median": runtime.math_median,
        "get_field": runtime.get_field,
        "math_abs": runtime.math_abs,
        "math_sqrt": runtime.math_sqrt,
        "get_env_var": runtime.get_env_var,
        "run_command": runtime.run_command,
        "load_doom_file": runtime.load_doom_file,
        "extract_html_text": runtime.extract_html_text,
        "extract_html_links": runtime.extract_html_links,
        "fetch_url": runtime.fetch_url,
        "download_file_url": runtime.download_file_url,
        "combine_tables": runtime.combine_tables,
        "send_email": runtime.send_email,
        "date_now_in": runtime.date_now_in,
        "next_business_day": runtime.next_business_day,
        "is_weekend": runtime.is_weekend,
        "unpack_values": runtime.unpack_values,
        "head_of": runtime.head_of,
        "tail_of": runtime.tail_of,
        "cli_set_description": runtime.cli_set_description,
        "cli_add_option": runtime.cli_add_option,
        "cli_add_flag": runtime.cli_add_flag,
        "cli_parse_arguments": runtime.cli_parse_arguments,
        "spawn_background_task": runtime.spawn_background_task,
        "wait_background_task": runtime.wait_background_task,
        "wait_all_background_tasks": runtime.wait_all_background_tasks,
        "timeout_call": runtime.timeout_call,
        "ask_ai": runtime.ask_ai,
        "ask_ai_json": runtime.ask_ai_json,
        "ask_ai_model": runtime.ask_ai_model,
        "orm_define": runtime.orm_define,
        "orm_save": runtime.orm_save,
        "orm_find_all": runtime.orm_find_all,
        "orm_find_first": runtime.orm_find_first,
        "orm_delete": runtime.orm_delete,
        "doc_create": runtime.doc_create,
        "doc_add_heading": runtime.doc_add_heading,
        "doc_add_paragraph": runtime.doc_add_paragraph,
        "doc_add_table": runtime.doc_add_table,
        "doc_add_list": runtime.doc_add_list,
        "doc_save": runtime.doc_save,
        "doc_render_markdown": runtime.doc_render_markdown,
        "doc_render_html": runtime.doc_render_html,
        "schedule_every_seconds": runtime.schedule_every_seconds,
        "run_scheduler_for": runtime.run_scheduler_for,
        "crypto_hash": runtime.crypto_hash,
        "crypto_token": runtime.crypto_token,
        "crypto_base64_encode": runtime.crypto_base64_encode,
        "crypto_base64_decode": runtime.crypto_base64_decode,
        "crypto_encrypt": runtime.crypto_encrypt,
        "crypto_decrypt": runtime.crypto_decrypt,
        "pipe_pipeline": runtime.pipe_pipeline,
        "stream_file_lines": runtime.stream_file_lines,
        "take_first_n": runtime.take_first_n,
        "drop_first_n": runtime.drop_first_n,
        "batch_items": runtime.batch_items,
        "num_to_hex": runtime.num_to_hex,
        "hex_to_num": runtime.hex_to_num,
        "pack_numbers": runtime.pack_numbers,
        "unpack_numbers": runtime.unpack_numbers,
        "bytes_length": runtime.bytes_length,
        "config_load": runtime.config_load,
        "config_get": runtime.config_get,
        "config_set": runtime.config_set,
        "config_save": runtime.config_save,
        "benchmark_block": runtime.benchmark_block,
    }
    # 1. Populate explicit core runtime exports (no raw modules or internal typing)
    exec_globals.update(runtime.get_runtime_exports())

    # 2. Populate domain runtime exports
    from doomscript.domains.registry import get_domain_registry
    reg = get_domain_registry()
    for d in reg.get_active_domains():
        exec_globals.update(reg.get_domain_exports(d.name))

    # 3. Explicit compiler runtime helpers
    for k, v in runtime_helpers.items():
        exec_globals.setdefault(k, v)
        
    exec(compiled, exec_globals)
    return exec_globals
