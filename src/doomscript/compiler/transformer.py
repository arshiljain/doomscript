"""
DoomScript AST Transformer
Transforms Lark Parse Tree into Python Standard AST nodes.
"""

import ast
import re
from lark import Transformer

def to_load(node):
    if isinstance(node, ast.Name):
        return ast.Name(id=f"{node.id}", ctx=ast.Load())
    elif isinstance(node, ast.Attribute):
        return ast.Attribute(value=to_load(node.value), attr=f"{node.attr}", ctx=ast.Load())
    elif isinstance(node, ast.Subscript):
        return ast.Subscript(value=to_load(node.value), slice=node.slice, ctx=ast.Load())
    return node

class DoomToPython(Transformer):
    """Transforms DoomScript CST to Python AST."""

    def start(self, stmts):
        body = [s for s in stmts if s is not None]
        mod = ast.Module(body=body, type_ignores=[])
        ast.fix_missing_locations(mod)
        return mod

    def post_if(self, args):
        stmt, test = args
        return ast.If(test=test, body=[stmt], orelse=[])

    def post_unless(self, args):
        stmt, test = args
        return ast.If(test=ast.UnaryOp(op=ast.Not(), operand=test), body=[stmt], orelse=[])

    def say(self, args):
        expr = args[0]
        call = ast.Call(
            func=ast.Name(id='print', ctx=ast.Load()),
            args=[expr],
            keywords=[]
        )
        return ast.Expr(value=call)

    def say_multi(self, args):
        call = ast.Call(
            func=ast.Name(id='print', ctx=ast.Load()),
            args=list(args),
            keywords=[]
        )
        return ast.Expr(value=call)

    def assign(self, args):
        target, val = args
        return ast.Assign(targets=[target], value=val)

    def set_var(self, args):
        target, val = args
        return ast.Assign(targets=[target], value=val)

    def increase_var(self, args):
        target, val = args
        return ast.AugAssign(target=target, op=ast.Add(), value=val)

    def decrease_var(self, args):
        target, val = args
        return ast.AugAssign(target=target, op=ast.Sub(), value=val)

    def ask_input(self, args):
        if len(args) == 2:
            prompt, target = args
        else:
            target = args[0]
            prompt = ast.Constant(value="")
        call = ast.Call(
            func=ast.Name(id='ask_input', ctx=ast.Load()),
            args=[prompt],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def write_file(self, args):
        content, filepath = args
        call = ast.Call(
            func=ast.Name(id='write_file', ctx=ast.Load()),
            args=[filepath, content],
            keywords=[]
        )
        return ast.Expr(value=call)

    def append_file(self, args):
        content, filepath = args
        call = ast.Call(
            func=ast.Name(id='append_file', ctx=ast.Load()),
            args=[filepath, content],
            keywords=[]
        )
        return ast.Expr(value=call)

    def read_file(self, args):
        filepath, target = args
        call = ast.Call(
            func=ast.Name(id='read_file', ctx=ast.Load()),
            args=[filepath],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def ask_choice(self, args):
        prompt, options, target = args
        call = ast.Call(
            func=ast.Name(id='ask_choice', ctx=ast.Load()),
            args=[prompt, options],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def ask_number(self, args):
        prompt, target = args
        call = ast.Call(func=ast.Name(id='ask_number', ctx=ast.Load()), args=[prompt], keywords=[])
        return ast.Assign(targets=[target], value=call)

    def ask_boolean(self, args):
        prompt, target = args
        call = ast.Call(func=ast.Name(id='ask_boolean', ctx=ast.Load()), args=[prompt], keywords=[])
        return ast.Assign(targets=[target], value=call)

    def read_csv(self, args):
        filepath, target = args
        call = ast.Call(func=ast.Name(id='read_csv', ctx=ast.Load()), args=[filepath], keywords=[])
        return ast.Assign(targets=[target], value=call)

    def write_csv(self, args):
        rows, filepath = args
        call = ast.Call(func=ast.Name(id='write_csv', ctx=ast.Load()), args=[filepath, rows], keywords=[])
        return ast.Expr(value=call)

    def append_csv(self, args):
        row, filepath = args
        call = ast.Call(func=ast.Name(id='append_csv', ctx=ast.Load()), args=[filepath, row], keywords=[])
        return ast.Expr(value=call)

    def parse_json(self, args):
        raw_text, target = args
        call = ast.Call(func=ast.Name(id='parse_json', ctx=ast.Load()), args=[raw_text], keywords=[])
        return ast.Assign(targets=[target], value=call)

    def stringify_json(self, args):
        obj, target = args
        call = ast.Call(func=ast.Name(id='stringify_json', ctx=ast.Load()), args=[obj], keywords=[])
        return ast.Assign(targets=[target], value=call)

    def get_env_var(self, args):
        var_name, target = args
        call = ast.Call(func=ast.Name(id='get_env_var', ctx=ast.Load()), args=[var_name], keywords=[])
        return ast.Assign(targets=[target], value=call)

    def run_cmd(self, args):
        cmd, target = args
        call = ast.Call(func=ast.Name(id='run_command', ctx=ast.Load()), args=[cmd], keywords=[])
        return ast.Assign(targets=[target], value=call)

    def insert_list(self, args):
        item, index, target = args
        call = ast.Call(func=ast.Name(id='insert_list', ctx=ast.Load()), args=[to_load(target), index, item], keywords=[])
        return ast.Expr(value=call)

    def sort_records(self, args):
        target = args[0]
        field = f"{args[1]}"
        desc = len(args) > 2 and args[2] is not None
        call = ast.Call(
            func=ast.Name(id='sort_records', ctx=ast.Load()),
            args=[to_load(target), ast.Constant(value=field), ast.Constant(value=bool(desc))],
            keywords=[]
        )
        return ast.Expr(value=call)

    def group_by_stmt(self, args):
        collection, field, target = args
        call = ast.Call(
            func=ast.Name(id='group_by', ctx=ast.Load()),
            args=[collection, ast.Constant(value=str(field))],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def filter_records_stmt(self, args):
        collection, field_name, cmp_op, val, target = args
        field_str = str(field_name)
        if field_str.lower() in ("item", "it"):
            left = ast.Name(id='_x', ctx=ast.Load())
        else:
            left = ast.Attribute(value=ast.Name(id='_x', ctx=ast.Load()), attr=field_str, ctx=ast.Load())
        op_map = {
            "is at least": ast.GtE(),
            "is at most": ast.LtE(),
            "is greater than": ast.Gt(),
            "is over": ast.Gt(),
            "is less than": ast.Lt(),
            "is under": ast.Lt(),
            "is not": ast.NotEq(),
            "isn't": ast.NotEq(),
            "equals": ast.Eq(),
            "is inside": ast.In(),
            "is in": ast.In(),
            "is": ast.Eq(),
        }
        cmp_ast = op_map.get(str(cmp_op), ast.Eq()) if not isinstance(cmp_op, ast.cmpop) else cmp_op
        test = ast.Compare(left=left, ops=[cmp_ast], comparators=[val])
        comp = ast.ListComp(
            elt=ast.Name(id='_x', ctx=ast.Load()),
            generators=[ast.comprehension(target=ast.Name(id='_x', ctx=ast.Store()), iter=collection, ifs=[test], is_async=0)]
        )
        return ast.Assign(targets=[target], value=comp)

    def comp_assign(self, args):
        target, prop_name, var_name, collection = args
        prop_str = str(prop_name)
        var_str = str(var_name)
        elt = ast.Attribute(value=ast.Name(id=var_str, ctx=ast.Load()), attr=prop_str, ctx=ast.Load())
        comp = ast.ListComp(
            elt=elt,
            generators=[ast.comprehension(target=ast.Name(id=var_str, ctx=ast.Store()), iter=collection, ifs=[], is_async=0)]
        )
        return ast.Assign(targets=[target], value=comp)

    def import_module(self, args):
        mod_name = str(args[0])
        return ast.Import(names=[ast.alias(name=mod_name)])

    def import_from_module(self, args):
        mod_name = str(args[0])
        names = [str(a) for a in args[1:]]
        return ast.ImportFrom(module=mod_name, names=[ast.alias(name=n) for n in names], level=0)

    def import_doom_file(self, args):
        filepath = args[0]
        call = ast.Call(func=ast.Name(id='load_doom_file', ctx=ast.Load()), args=[filepath], keywords=[])
        return ast.Expr(value=call)

    def copy_file(self, args):
        src, dst = args
        call = ast.Call(
            func=ast.Name(id='copy_file', ctx=ast.Load()),
            args=[src, dst],
            keywords=[]
        )
        return ast.Expr(value=call)

    def delete_file(self, args):
        filepath = args[0]
        call = ast.Call(
            func=ast.Name(id='delete_file', ctx=ast.Load()),
            args=[filepath],
            keywords=[]
        )
        return ast.Expr(value=call)

    def create_dir(self, args):
        dirpath = args[0]
        call = ast.Call(
            func=ast.Name(id='create_dir', ctx=ast.Load()),
            args=[dirpath],
            keywords=[]
        )
        return ast.Expr(value=call)

    def list_files(self, args):
        dirpath, target = args
        call = ast.Call(
            func=ast.Name(id='list_files', ctx=ast.Load()),
            args=[dirpath],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def check_file_exists(self, args):
        filepath, target = args
        call = ast.Call(
            func=ast.Name(id='file_exists', ctx=ast.Load()),
            args=[filepath],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def file_exists_factor(self, args):
        filepath = args[0]
        return ast.Call(
            func=ast.Name(id='file_exists', ctx=ast.Load()),
            args=[filepath],
            keywords=[]
        )

    def string_replace(self, args):
        needle, replacement, source, target = args
        call = ast.Call(
            func=ast.Name(id='str_replace', ctx=ast.Load()),
            args=[source, needle, replacement],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def string_split(self, args):
        text, delimiter, target = args
        call = ast.Call(
            func=ast.Name(id='str_split', ctx=ast.Load()),
            args=[text, delimiter],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def string_join(self, args):
        items, delimiter, target = args
        call = ast.Call(
            func=ast.Name(id='str_join', ctx=ast.Load()),
            args=[items, delimiter],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def string_uppercase(self, args):
        text, target = args
        call = ast.Call(
            func=ast.Name(id='str_uppercase', ctx=ast.Load()),
            args=[text],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def string_lowercase(self, args):
        text, target = args
        call = ast.Call(
            func=ast.Name(id='str_lowercase', ctx=ast.Load()),
            args=[text],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def string_capitalize(self, args):
        text, target = args
        call = ast.Call(
            func=ast.Name(id='str_capitalize', ctx=ast.Load()),
            args=[text],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def string_trim(self, args):
        text, target = args
        call = ast.Call(
            func=ast.Name(id='str_trim', ctx=ast.Load()),
            args=[text],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def str_starts_with(self, args):
        text, prefix = args[0], args[-1]
        return ast.Call(
            func=ast.Name(id='str_starts_with', ctx=ast.Load()),
            args=[text, prefix],
            keywords=[]
        )

    def str_ends_with(self, args):
        text, suffix = args[0], args[-1]
        return ast.Call(
            func=ast.Name(id='str_ends_with', ctx=ast.Load()),
            args=[text, suffix],
            keywords=[]
        )

    def str_matches_pattern(self, args):
        text, pattern = args[0], args[-1]
        return ast.Call(
            func=ast.Name(id='str_matches_pattern', ctx=ast.Load()),
            args=[text, pattern],
            keywords=[]
        )

    def spawn_thread_args(self, args):
        func_name = str(args[0])
        arg_items = args[1] if isinstance(args[1], list) else [args[1]]
        clean_args = []
        for a in arg_items:
            if isinstance(a, ast.Name) and isinstance(a.ctx, ast.Store):
                a = ast.Name(id=a.id, ctx=ast.Load())
            clean_args.append(a)
        target = args[2]
        call = ast.Call(
            func=ast.Name(id='spawn_thread', ctx=ast.Load()),
            args=[ast.Name(id=func_name, ctx=ast.Load())] + clean_args,
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def spawn_thread_noargs(self, args):
        func_name = str(args[0])
        target = args[1]
        call = ast.Call(
            func=ast.Name(id='spawn_thread', ctx=ast.Load()),
            args=[ast.Name(id=func_name, ctx=ast.Load())],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def wait_for_thread(self, args):
        target = args[0]
        call = ast.Call(
            func=ast.Name(id='wait_for_thread', ctx=ast.Load()),
            args=[target],
            keywords=[]
        )
        return ast.Expr(value=call)

    def add_route(self, args):
        method, path, handler = args
        call = ast.Call(
            func=ast.Name(id='add_route', ctx=ast.Load()),
            args=[ast.Constant(value=str(method)), path, ast.Name(id=str(handler), ctx=ast.Load())],
            keywords=[]
        )
        return ast.Expr(value=call)

    def start_server_bg(self, args):
        port, target = args
        call = ast.Call(
            func=ast.Name(id='start_server', ctx=ast.Load()),
            args=[port, ast.Constant(value=True)],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def start_server_fg(self, args):
        port = args[0]
        call = ast.Call(
            func=ast.Name(id='start_server', ctx=ast.Load()),
            args=[port, ast.Constant(value=False)],
            keywords=[]
        )
        return ast.Expr(value=call)

    def stop_server(self, args):
        server = args[0]
        call = ast.Call(
            func=ast.Name(id='stop_server', ctx=ast.Load()),
            args=[server],
            keywords=[]
        )
        return ast.Expr(value=call)

    def display_colored(self, args):
        text, color = args
        call = ast.Call(
            func=ast.Name(id='display_colored', ctx=ast.Load()),
            args=[text, color],
            keywords=[]
        )
        return ast.Expr(value=call)

    def pause_terminal(self, _):
        call = ast.Call(func=ast.Name(id='pause_terminal', ctx=ast.Load()), args=[], keywords=[])
        return ast.Expr(value=call)

    def math_round(self, args):
        val, decimals, target = args
        call = ast.Call(
            func=ast.Name(id='math_round', ctx=ast.Load()),
            args=[val, decimals],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def math_clamp(self, args):
        val, min_val, max_val, target = args
        call = ast.Call(
            func=ast.Name(id='math_clamp', ctx=ast.Load()),
            args=[val, min_val, max_val],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def verify_assertion(self, args):
        test, msg = args
        return ast.Assert(test=test, msg=msg)

    def fetch_json(self, args):
        url, target = args
        call = ast.Call(
            func=ast.Name(id='fetch_json', ctx=ast.Load()),
            args=[url],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def fetch_text(self, args):
        url, target = args
        call = ast.Call(
            func=ast.Name(id='fetch_text', ctx=ast.Load()),
            args=[url],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def download_file(self, args):
        url, filepath = args
        call = ast.Call(
            func=ast.Name(id='download_file', ctx=ast.Load()),
            args=[url, filepath],
            keywords=[]
        )
        return ast.Expr(value=call)

    def random_range(self, args):
        low, high, target = args
        call = ast.Call(
            func=ast.Name(id='random_range', ctx=ast.Load()),
            args=[low, high],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def pick_random(self, args):
        coll, target = args
        call = ast.Call(
            func=ast.Name(id='pick_random', ctx=ast.Load()),
            args=[coll],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def shuffle_list(self, args):
        target = args[0]
        load_target = ast.Name(id=target.id, ctx=ast.Load()) if isinstance(target, ast.Name) else target
        call = ast.Call(
            func=ast.Name(id='shuffle_list', ctx=ast.Load()),
            args=[load_target],
            keywords=[]
        )
        return ast.Expr(value=call)

    def db_save(self, args):
        record, db_path, table = args
        call = ast.Call(
            func=ast.Name(id='db_save', ctx=ast.Load()),
            args=[record, db_path, table],
            keywords=[]
        )
        return ast.Expr(value=call)

    def db_load(self, args):
        db_path, table, target = args
        call = ast.Call(
            func=ast.Name(id='db_load', ctx=ast.Load()),
            args=[db_path, table],
            keywords=[]
        )
        return ast.Assign(targets=[target], value=call)

    def beep_action(self, args):
        freq = args[0]
        dur = args[1]
        call = ast.Call(
            func=ast.Name(id='beep', ctx=ast.Load()),
            args=[freq, dur],
            keywords=[]
        )
        return ast.Expr(value=call)

    def play_sound_action(self, args):
        sound_path = args[0]
        call = ast.Call(
            func=ast.Name(id='play_sound', ctx=ast.Load()),
            args=[sound_path],
            keywords=[]
        )
        return ast.Expr(value=call)

    def open_window(self, args):
        title, width, height = args
        call = ast.Call(
            func=ast.Name(id='open_window', ctx=ast.Load()),
            args=[title, width, height],
            keywords=[]
        )
        return ast.Expr(value=call)

    def draw_circle(self, args):
        x, y, radius, color = args
        call = ast.Call(
            func=ast.Name(id='draw_circle', ctx=ast.Load()),
            args=[x, y, radius, color],
            keywords=[]
        )
        return ast.Expr(value=call)

    def draw_rect(self, args):
        x, y, width, height, color = args
        call = ast.Call(
            func=ast.Name(id='draw_rectangle', ctx=ast.Load()),
            args=[x, y, width, height, color],
            keywords=[]
        )
        return ast.Expr(value=call)

    def draw_text(self, args):
        text_expr, x, y, size, color = args
        call = ast.Call(
            func=ast.Name(id='draw_text', ctx=ast.Load()),
            args=[text_expr, x, y, size, color],
            keywords=[]
        )
        return ast.Expr(value=call)

    def clear_screen(self, _):
        call = ast.Call(func=ast.Name(id='clear_screen', ctx=ast.Load()), args=[], keywords=[])
        return ast.Expr(value=call)

    def refresh_screen(self, _):
        call = ast.Call(func=ast.Name(id='refresh_screen', ctx=ast.Load()), args=[], keywords=[])
        return ast.Expr(value=call)

    def target_var(self, args):
        return ast.Name(id=str(args[0]), ctx=ast.Store())

    def target_attr(self, args):
        val, attr = args
        return ast.Attribute(value=val, attr=str(attr), ctx=ast.Store())

    def add_to_list(self, args):
        item, target = args
        load_target = ast.Name(id=target.id, ctx=ast.Load()) if isinstance(target, ast.Name) else target
        call = ast.Call(
            func=ast.Attribute(value=load_target, attr="append", ctx=ast.Load()),
            args=[item],
            keywords=[]
        )
        return ast.Expr(value=call)

    def remove_from_list(self, args):
        item, target = args
        load_target = ast.Name(id=target.id, ctx=ast.Load()) if isinstance(target, ast.Name) else target
        call = ast.Call(
            func=ast.Attribute(value=load_target, attr="remove", ctx=ast.Load()),
            args=[item],
            keywords=[]
        )
        return ast.Expr(value=call)

    def wait_seconds(self, args):
        sec = args[0]
        call = ast.Call(
            func=ast.Name(id="sleep", ctx=ast.Load()),
            args=[sec],
            keywords=[]
        )
        return ast.Expr(value=call)

    def return_val(self, args):
        val = args[0] if args else None
        return ast.Return(value=val)

    def stop_stmt(self, _):
        return ast.Break()

    def skip_stmt(self, _):
        return ast.Continue()

    def call_stmt(self, args):
        func_name = str(args[0])
        remaining = args[1:]
        all_args = []
        keywords = []
        for r in remaining:
            if r is None:
                continue
            if isinstance(r, list):
                for item in r:
                    if isinstance(item, ast.keyword):
                        keywords.append(item)
                    else:
                        if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Store):
                            item = ast.Name(id=item.id, ctx=ast.Load())
                        all_args.append(item)
            elif isinstance(r, ast.keyword):
                keywords.append(r)
            else:
                if isinstance(r, ast.Name) and isinstance(r.ctx, ast.Store):
                    r = ast.Name(id=r.id, ctx=ast.Load())
                elif isinstance(r, ast.Attribute) and isinstance(r.ctx, ast.Store):
                    r = ast.Attribute(value=r.value, attr=r.attr, ctx=ast.Load())
                all_args.append(r)

        call = ast.Call(
            func=ast.Name(id=func_name, ctx=ast.Load()),
            args=all_args,
            keywords=keywords
        )
        return ast.Expr(value=call)

    def expr_stmt(self, args):
        return ast.Expr(value=args[0])

    def if_stmt(self, args):
        test = args[0]
        body = args[1]
        rest = args[2:]
        elifs = [r for r in rest if isinstance(r, tuple) and r[0] == 'elif']
        else_block = next((r[1] for r in rest if isinstance(r, tuple) and r[0] == 'else'), [])
        orelse = else_block
        for _, elif_test, elif_body in reversed(elifs):
            orelse = [ast.If(test=elif_test, body=elif_body, orelse=orelse)]
        return ast.If(test=test, body=body, orelse=orelse)

    def elif_clause(self, args):
        return ('elif', args[0], args[1])

    def else_clause(self, args):
        return ('else', args[0])

    def unless_stmt(self, args):
        test = ast.UnaryOp(op=ast.Not(), operand=args[0])
        body = args[1]
        orelse = []
        if len(args) > 2 and isinstance(args[2], tuple) and args[2][0] == 'else':
            orelse = args[2][1]
        return ast.If(test=test, body=body, orelse=orelse)

    def try_stmt(self, args):
        try_body = args[0]
        problem_name = None
        fail_body = []
        always_body = []
        idx = 1
        while idx < len(args):
            arg = args[idx]
            if isinstance(arg, list):
                if not fail_body:
                    fail_body = arg
                else:
                    always_body = arg
            elif isinstance(arg, str):
                problem_name = f"{arg}"
            idx += 1
        handler = ast.ExceptHandler(
            type=ast.Name(id='Exception', ctx=ast.Load()),
            name=f"{problem_name}" if problem_name else None,
            body=fail_body
        )
        return ast.Try(body=try_body, handlers=[handler], orelse=[], finalbody=always_body)

    def repeat_range_stmt(self, args):
        var_name = args[0]
        start = args[1]
        stop = args[2]
        step = args[3] if len(args) > 4 and args[3] is not None else ast.Constant(value=1)
        suite = args[-1]
        call = ast.Call(
            func=ast.Name(id='range_inclusive', ctx=ast.Load()),
            args=[start, stop, step],
            keywords=[]
        )
        return ast.For(target=ast.Name(id=f"{var_name}", ctx=ast.Store()), iter=call, body=suite, orelse=[])

    def for_where_stmt(self, args):
        var_name, collection, condition, suite = args
        if_node = ast.If(test=condition, body=suite, orelse=[])
        return ast.For(target=ast.Name(id=f"{var_name}", ctx=ast.Store()), iter=collection, body=[if_node], orelse=[])

    def repeat_stmt(self, args):
        times, body = args
        iter_call = ast.Call(
            func=ast.Name(id='range', ctx=ast.Load()),
            args=[times],
            keywords=[]
        )
        return ast.For(
            target=ast.Name(id='_', ctx=ast.Store()),
            iter=iter_call,
            body=body,
            orelse=[]
        )

    def repeat_while_stmt(self, args):
        test, body = args
        return ast.While(test=test, body=body, orelse=[])

    def repeat_until_stmt(self, args):
        test, body = args
        not_test = ast.UnaryOp(op=ast.Not(), operand=test)
        return ast.While(test=not_test, body=body, orelse=[])

    def for_stmt(self, args):
        var_name, iterable, body = args
        return ast.For(
            target=ast.Name(id=str(var_name), ctx=ast.Store()),
            iter=iterable,
            body=body,
            orelse=[]
        )

    def attempt_stmt(self, args):
        try_body, fail_body = args
        handler = ast.ExceptHandler(
            type=ast.Name(id='Exception', ctx=ast.Load()),
            name=None,
            body=fail_body
        )
        return ast.Try(
            body=try_body,
            handlers=[handler],
            orelse=[],
            finalbody=[]
        )

    def param_item(self, args):
        name = str(args[0])
        default = args[1] if len(args) > 1 and args[1] is not None else None
        return (name, default)

    def param_list(self, args):
        return list(args)

    def call_arg(self, args):
        if len(args) == 2 and args[0] is not None:
            return ast.keyword(arg=str(args[0]), value=args[1])
        elif len(args) == 2:
            return args[1]
        return args[0]

    def call_arg_list(self, args):
        return list(args)

    def func_def(self, args):
        func_name = str(args[0])
        body = args[-1]

        middle = args[1:-1]
        params = []
        for item in middle:
            if item is None:
                continue
            if isinstance(item, list):
                params.extend(item)
            else:
                params.append(item)

        arg_nodes = []
        defaults = []
        for p in params:
            if isinstance(p, tuple):
                pname, pdef = p
                arg_nodes.append(ast.arg(arg=str(pname)))
                if pdef is not None:
                    defaults.append(pdef)
            else:
                arg_nodes.append(ast.arg(arg=str(p)))

        arguments_node = ast.arguments(
            posonlyargs=[],
            args=arg_nodes,
            kwonlyargs=[],
            kw_defaults=[],
            defaults=defaults
        )
        return ast.FunctionDef(
            name=func_name,
            args=arguments_node,
            body=body,
            decorator_list=[]
        )

    def arg_list(self, args):
        return list(args)

    def suite(self, stmts):
        return [s for s in stmts if s is not None]

    def compare(self, args):
        left, op_tok, right = args
        op_str = str(op_tok)
        op_map = {
            "<=": ast.LtE(),
            ">=": ast.GtE(),
            "!=": ast.NotEq(),
            "==": ast.Eq(),
            "<": ast.Lt(),
            ">": ast.Gt(),
            "is at least": ast.GtE(),
            "is at most": ast.LtE(),
            "is greater than": ast.Gt(),
            "is over": ast.Gt(),
            "is less than": ast.Lt(),
            "is under": ast.Lt(),
            "is not": ast.NotEq(),
            "isn't": ast.NotEq(),
            "equals": ast.Eq(),
            "is not inside": ast.NotIn(),
            "is not in": ast.NotIn(),
            "is inside": ast.In(),
            "is in": ast.In(),
            "is": ast.Eq(),
        }
        return ast.Compare(left=left, ops=[op_map[op_str]], comparators=[right])

    def is_between(self, args):
        if len(args) == 4:
            val, _, low, high = args
        else:
            val, low, high = args
        return ast.Compare(left=low, ops=[ast.LtE(), ast.LtE()], comparators=[val, high])

    def is_one_of(self, args):
        if len(args) == 3:
            val, _, coll = args
        else:
            val, coll = args
        return ast.Compare(left=val, ops=[ast.In()], comparators=[coll])

    def is_type_number(self, args):
        val = args[0]
        types_tuple = ast.Tuple(elts=[ast.Name(id='int', ctx=ast.Load()), ast.Name(id='float', ctx=ast.Load())], ctx=ast.Load())
        return ast.Call(func=ast.Name(id='isinstance', ctx=ast.Load()), args=[val, types_tuple], keywords=[])

    def is_type_not_number(self, args):
        val = args[0]
        types_tuple = ast.Tuple(elts=[ast.Name(id='int', ctx=ast.Load()), ast.Name(id='float', ctx=ast.Load())], ctx=ast.Load())
        call = ast.Call(func=ast.Name(id='isinstance', ctx=ast.Load()), args=[val, types_tuple], keywords=[])
        return ast.UnaryOp(op=ast.Not(), operand=call)

    def is_type_text(self, args):
        val = args[0]
        return ast.Call(func=ast.Name(id='isinstance', ctx=ast.Load()), args=[val, ast.Name(id='str', ctx=ast.Load())], keywords=[])

    def is_type_not_text(self, args):
        val = args[0]
        call = ast.Call(func=ast.Name(id='isinstance', ctx=ast.Load()), args=[val, ast.Name(id='str', ctx=ast.Load())], keywords=[])
        return ast.UnaryOp(op=ast.Not(), operand=call)

    def is_type_boolean(self, args):
        val = args[0]
        return ast.Call(func=ast.Name(id='isinstance', ctx=ast.Load()), args=[val, ast.Name(id='bool', ctx=ast.Load())], keywords=[])

    def is_type_not_boolean(self, args):
        val = args[0]
        call = ast.Call(func=ast.Name(id='isinstance', ctx=ast.Load()), args=[val, ast.Name(id='bool', ctx=ast.Load())], keywords=[])
        return ast.UnaryOp(op=ast.Not(), operand=call)

    def is_type_list(self, args):
        val = args[0]
        return ast.Call(func=ast.Name(id='isinstance', ctx=ast.Load()), args=[val, ast.Name(id='list', ctx=ast.Load())], keywords=[])

    def is_type_not_list(self, args):
        val = args[0]
        call = ast.Call(func=ast.Name(id='isinstance', ctx=ast.Load()), args=[val, ast.Name(id='list', ctx=ast.Load())], keywords=[])
        return ast.UnaryOp(op=ast.Not(), operand=call)

    def is_type_record(self, args):
        val = args[0]
        return ast.Call(func=ast.Name(id='isinstance', ctx=ast.Load()), args=[val, ast.Name(id='dict', ctx=ast.Load())], keywords=[])

    def is_type_not_record(self, args):
        val = args[0]
        call = ast.Call(func=ast.Name(id='isinstance', ctx=ast.Load()), args=[val, ast.Name(id='dict', ctx=ast.Load())], keywords=[])
        return ast.UnaryOp(op=ast.Not(), operand=call)

    def contains(self, args):
        container, item = args
        return ast.Compare(left=item, ops=[ast.In()], comparators=[container])

    def is_empty(self, args):
        target = args[0]
        len_call = ast.Call(
            func=ast.Name(id='len', ctx=ast.Load()),
            args=[target],
            keywords=[]
        )
        return ast.Compare(left=len_call, ops=[ast.Eq()], comparators=[ast.Constant(value=0)])

    def is_not_empty(self, args):
        target = args[0]
        len_call = ast.Call(
            func=ast.Name(id='len', ctx=ast.Load()),
            args=[target],
            keywords=[]
        )
        return ast.Compare(left=len_call, ops=[ast.Gt()], comparators=[ast.Constant(value=0)])

    def count_of(self, args):
        target = args[0]
        return ast.Call(
            func=ast.Name(id='len', ctx=ast.Load()),
            args=[target],
            keywords=[]
        )

    def agg_sum(self, args):
        return ast.Call(func=ast.Name(id='agg_sum', ctx=ast.Load()), args=[args[0]], keywords=[])

    def agg_avg(self, args):
        return ast.Call(func=ast.Name(id='agg_avg', ctx=ast.Load()), args=[args[0]], keywords=[])

    def agg_max(self, args):
        return ast.Call(func=ast.Name(id='agg_max', ctx=ast.Load()), args=[args[0]], keywords=[])

    def agg_min(self, args):
        return ast.Call(func=ast.Name(id='agg_min', ctx=ast.Load()), args=[args[0]], keywords=[])

    def agg_first(self, args):
        return ast.Call(func=ast.Name(id='agg_first', ctx=ast.Load()), args=[args[0]], keywords=[])

    def agg_last(self, args):
        return ast.Call(func=ast.Name(id='agg_last', ctx=ast.Load()), args=[args[0]], keywords=[])

    def field_total(self, args):
        field, coll = args
        elt = ast.Attribute(value=ast.Name(id='_x', ctx=ast.Load()), attr=str(field), ctx=ast.Load())
        comp = ast.ListComp(elt=elt, generators=[ast.comprehension(target=ast.Name(id='_x', ctx=ast.Store()), iter=coll, ifs=[], is_async=0)])
        return ast.Call(func=ast.Name(id='agg_sum', ctx=ast.Load()), args=[comp], keywords=[])

    def field_average(self, args):
        field, coll = args
        elt = ast.Attribute(value=ast.Name(id='_x', ctx=ast.Load()), attr=str(field), ctx=ast.Load())
        comp = ast.ListComp(elt=elt, generators=[ast.comprehension(target=ast.Name(id='_x', ctx=ast.Store()), iter=coll, ifs=[], is_async=0)])
        return ast.Call(func=ast.Name(id='agg_avg', ctx=ast.Load()), args=[comp], keywords=[])

    def field_highest(self, args):
        field, coll = args
        elt = ast.Attribute(value=ast.Name(id='_x', ctx=ast.Load()), attr=str(field), ctx=ast.Load())
        comp = ast.ListComp(elt=elt, generators=[ast.comprehension(target=ast.Name(id='_x', ctx=ast.Store()), iter=coll, ifs=[], is_async=0)])
        return ast.Call(func=ast.Name(id='agg_max', ctx=ast.Load()), args=[comp], keywords=[])

    def field_lowest(self, args):
        field, coll = args
        elt = ast.Attribute(value=ast.Name(id='_x', ctx=ast.Load()), attr=str(field), ctx=ast.Load())
        comp = ast.ListComp(elt=elt, generators=[ast.comprehension(target=ast.Name(id='_x', ctx=ast.Store()), iter=coll, ifs=[], is_async=0)])
        return ast.Call(func=ast.Name(id='agg_min', ctx=ast.Load()), args=[comp], keywords=[])

    def item_of_list(self, args):
        idx, coll = args
        return ast.Call(func=ast.Name(id='item_of', ctx=ast.Load()), args=[idx, coll], keywords=[])

    def first_n_items(self, args):
        n, coll = args
        return ast.Call(func=ast.Name(id='first_n_items', ctx=ast.Load()), args=[n, coll], keywords=[])

    def last_n_items(self, args):
        n, coll = args
        return ast.Call(func=ast.Name(id='last_n_items', ctx=ast.Load()), args=[n, coll], keywords=[])

    def sorted_list(self, args):
        return ast.Call(func=ast.Name(id='sorted_list', ctx=ast.Load()), args=[args[0]], keywords=[])

    def reversed_list(self, args):
        return ast.Call(func=ast.Name(id='reversed_list', ctx=ast.Load()), args=[args[0]], keywords=[])

    def unique_items(self, args):
        return ast.Call(func=ast.Name(id='unique_items', ctx=ast.Load()), args=[args[0]], keywords=[])

    def math_abs(self, args):
        return ast.Call(func=ast.Name(id='math_abs', ctx=ast.Load()), args=[args[0]], keywords=[])

    def math_sqrt(self, args):
        return ast.Call(func=ast.Name(id='math_sqrt', ctx=ast.Load()), args=[args[0]], keywords=[])

    def date_today(self, _):
        return ast.Call(func=ast.Name(id='date_today', ctx=ast.Load()), args=[], keywords=[])

    def date_now(self, _):
        return ast.Call(func=ast.Name(id='date_now', ctx=ast.Load()), args=[], keywords=[])

    def result_of_call(self, args):
        func_name = str(args[0])
        call_args = args[1:] if isinstance(args[1], list) else [args[1]]
        return ast.Call(func=ast.Name(id=func_name, ctx=ast.Load()), args=call_args, keywords=[])

    def time_future(self, args):
        amount, unit = args
        return ast.Call(
            func=ast.Name(id='time_future', ctx=ast.Load()),
            args=[amount, ast.Constant(value=str(unit))],
            keywords=[]
        )

    def time_past(self, args):
        amount, unit = args
        return ast.Call(
            func=ast.Name(id='time_past', ctx=ast.Load()),
            args=[amount, ast.Constant(value=str(unit))],
            keywords=[]
        )

    def logic_and(self, args):
        return ast.BoolOp(op=ast.And(), values=[args[0], args[1]])

    def logic_or(self, args):
        return ast.BoolOp(op=ast.Or(), values=[args[0], args[1]])

    def logic_not(self, args):
        return ast.UnaryOp(op=ast.Not(), operand=args[0])

    def neg(self, args):
        return ast.UnaryOp(op=ast.USub(), operand=args[0])

    def add(self, args):
        return ast.BinOp(left=args[0], op=ast.Add(), right=args[1])

    def sub(self, args):
        return ast.BinOp(left=args[0], op=ast.Sub(), right=args[1])

    def mul(self, args):
        return ast.BinOp(left=args[0], op=ast.Mult(), right=args[1])

    def div(self, args):
        return ast.BinOp(left=args[0], op=ast.Div(), right=args[1])

    def percent_of(self, args):
        num_tok, target = args
        num_val = float(num_tok) if '.' in str(num_tok) else int(num_tok)
        pct = ast.BinOp(left=ast.Constant(value=num_val), op=ast.Div(), right=ast.Constant(value=100.0))
        return ast.BinOp(left=target, op=ast.Mult(), right=pct)

    def possessive(self, args):
        atom, attr = args
        return ast.Attribute(value=atom, attr=str(attr), ctx=ast.Load())

    def standard_call(self, args):
        func_name = str(args[0])
        call_items = args[1] if len(args) > 1 and args[1] is not None else []
        pos_args = [a for a in call_items if not isinstance(a, ast.keyword)]
        keywords = [a for a in call_items if isinstance(a, ast.keyword)]
        return ast.Call(
            func=ast.Name(id=func_name, ctx=ast.Load()),
            args=pos_args,
            keywords=keywords
        )

    def var(self, args):
        return ast.Name(id=str(args[0]), ctx=ast.Load())

    def num(self, args):
        val = float(args[0]) if '.' in str(args[0]) else int(args[0])
        return ast.Constant(value=val)

    def str(self, args):
        raw = str(args[0])
        if raw.startswith(('"""', "'''")):
            val = raw[3:-3]
        else:
            val = raw[1:-1]
        var_pattern = re.compile(r"\{([A-Za-z_]\w*(?:\s*(?:'s|\.)\s*[A-Za-z_]\w*)*)\}")
        if var_pattern.search(val):
            parts = []
            last_end = 0
            has_interpolation = False
            for m in var_pattern.finditer(val):
                if m.start() > last_end:
                    parts.append(ast.Constant(value=val[last_end:m.start()]))
                expr_text = m.group(1).strip()
                if "'s" in expr_text or "." in expr_text:
                    sub_parts = re.split(r"(?:'s|\.)", expr_text)
                    curr = ast.Name(id=f"{sub_parts[0].strip()}", ctx=ast.Load())
                    for sp in sub_parts[1:]:
                        curr = ast.Attribute(value=curr, attr=f"{sp.strip()}", ctx=ast.Load())
                    parts.append(ast.FormattedValue(value=curr, conversion=-1))
                else:
                    parts.append(ast.FormattedValue(value=ast.Name(id=f"{expr_text}", ctx=ast.Load()), conversion=-1))
                last_end = m.end()
                has_interpolation = True
            if last_end < len(val):
                parts.append(ast.Constant(value=val[last_end:]))
            if has_interpolation:
                return ast.JoinedStr(values=parts)
        return ast.Constant(value=val)

    def const_true(self, _):
        return ast.Constant(value=True)

    def const_false(self, _):
        return ast.Constant(value=False)

    def const_none(self, _):
        return ast.Constant(value=None)

    def list_val(self, args):
        elts = [a for a in args if a is not None]
        return ast.List(elts=elts, ctx=ast.Load())

    def dict_val(self, args):
        pairs = [p for p in args if p is not None]
        keys = [k for k, _ in pairs]
        vals = [v for _, v in pairs]
        raw_dict = ast.Dict(keys=keys, values=vals)
        return ast.Call(
            func=ast.Name(id='Record', ctx=ast.Load()),
            args=[raw_dict],
            keywords=[]
        )

    def dict_pair(self, args):
        k, v = args
        key_node = ast.Constant(value=str(k)[1:-1] if str(k).startswith(('"', "'")) else str(k))
        return (key_node, v)
