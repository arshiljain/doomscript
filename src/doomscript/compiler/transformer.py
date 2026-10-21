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
    elif isinstance(node, ast.Tuple):
        return ast.Tuple(elts=[to_load(e) for e in node.elts], ctx=ast.Load())
    return node

class DoomToPython(Transformer):
    """Transforms DoomScript CST to Python AST."""

    def __init__(self, line_map=None, visit_tokens=True):
        super().__init__(visit_tokens=visit_tokens)
        self.line_map = line_map or {}

    def _call_userfunc(self, tree, new_children=None):
        res = super()._call_userfunc(tree, new_children)
        if isinstance(res, ast.AST):
            if hasattr(tree, "meta") and getattr(tree.meta, "line", None) is not None:
                orig_line = self.line_map.get(tree.meta.line, tree.meta.line)
                orig_col = max(0, getattr(tree.meta, "column", 1) - 1)
                res.lineno = orig_line
                res.col_offset = orig_col
                end_line = getattr(tree.meta, "end_line", None)
                if end_line is not None:
                    orig_end_line = self.line_map.get(end_line, end_line)
                    res.end_lineno = max(res.lineno, orig_end_line)
                else:
                    res.end_lineno = res.lineno
                end_col = getattr(tree.meta, "end_column", None)
                if end_col is not None:
                    raw_end_col = max(0, end_col - 1)
                    if res.end_lineno == res.lineno:
                        res.end_col_offset = max(res.col_offset, raw_end_col)
                    else:
                        res.end_col_offset = raw_end_col
                else:
                    res.end_col_offset = res.col_offset
        return res

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

    def target_list(self, args):
        return [a for a in args if a is not None]

    def expr_list(self, args):
        return [a for a in args if a is not None]

    def assign(self, args):
        targets, exprs = args
        if isinstance(targets, list) and len(targets) > 1:
            target = ast.Tuple(elts=targets, ctx=ast.Store())
        elif isinstance(targets, list) and len(targets) == 1:
            target = targets[0]
        else:
            target = targets

        if isinstance(exprs, list) and len(exprs) > 1:
            val = ast.Tuple(elts=exprs, ctx=ast.Load())
        elif isinstance(exprs, list) and len(exprs) == 1:
            val = exprs[0]
        else:
            val = exprs

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

    def aug_add(self, args):
        target, val = args
        return ast.AugAssign(target=target, op=ast.Add(), value=val)

    def aug_sub(self, args):
        target, val = args
        return ast.AugAssign(target=target, op=ast.Sub(), value=val)

    def aug_mul(self, args):
        target, val = args
        return ast.AugAssign(target=target, op=ast.Mult(), value=val)

    def aug_div(self, args):
        target, val = args
        return ast.AugAssign(target=target, op=ast.Div(), value=val)

    def aug_floor_div(self, args):
        target, val = args
        return ast.AugAssign(target=target, op=ast.FloorDiv(), value=val)

    def aug_mod(self, args):
        target, val = args
        return ast.AugAssign(target=target, op=ast.Mod(), value=val)

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

    def sort_list_asc(self, args):
        target = args[0]
        call = ast.Call(
            func=ast.Attribute(value=to_load(target), attr='sort', ctx=ast.Load()),
            args=[],
            keywords=[]
        )
        return ast.Expr(value=call)

    def sort_list_desc(self, args):
        target = args[0]
        call = ast.Call(
            func=ast.Attribute(value=to_load(target), attr='sort', ctx=ast.Load()),
            args=[],
            keywords=[ast.keyword(arg='reverse', value=ast.Constant(value=True))]
        )
        return ast.Expr(value=call)

    def reverse_list_stmt(self, args):
        target = args[0]
        call = ast.Call(
            func=ast.Attribute(value=to_load(target), attr='reverse', ctx=ast.Load()),
            args=[],
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
        if isinstance(target, list):
            target = target[0]
        prop_str = str(prop_name)
        var_str = str(var_name)
        elt = ast.Attribute(value=ast.Name(id=var_str, ctx=ast.Load()), attr=prop_str, ctx=ast.Load())
        comp = ast.ListComp(
            elt=elt,
            generators=[ast.comprehension(target=ast.Name(id=var_str, ctx=ast.Store()), iter=collection, ifs=[], is_async=0)]
        )
        return ast.Assign(targets=[target], value=comp)

    def dotted_name(self, args):
        return ".".join(str(a).strip("\"'") for a in args)

    def import_alias(self, args):
        name = str(args[0]).strip("\"'")
        as_name = str(args[1]).strip("\"'") if len(args) > 1 and args[1] is not None else None
        return ast.alias(name=name, asname=as_name)

    def import_module(self, args):
        mod_name = str(args[0]).strip("\"'")
        as_name = str(args[1]).strip("\"'") if len(args) > 1 and args[1] is not None else None
        return ast.Import(names=[ast.alias(name=mod_name, asname=as_name)])

    def import_from_module(self, args):
        mod_name = str(args[0]).strip("\"'")
        aliases = []
        for item in args[1:]:
            if isinstance(item, ast.alias):
                aliases.append(item)
            else:
                aliases.append(ast.alias(name=str(item).strip("\"'"), asname=None))
        return ast.ImportFrom(module=mod_name, names=aliases, level=0)

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

    def expr_split(self, args):
        if len(args) == 2:
            text, delimiter = args
            return ast.Call(
                func=ast.Name(id='str_split', ctx=ast.Load()),
                args=[text, delimiter],
                keywords=[]
            )
        else:
            text = args[0]
            return ast.Call(
                func=ast.Name(id='str_split', ctx=ast.Load()),
                args=[text],
                keywords=[]
            )

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
        return ast.Attribute(value=to_load(val), attr=str(attr), ctx=ast.Store())

    def target_subscript(self, args):
        val, slice_idx = args
        return ast.Subscript(value=to_load(val), slice=to_load(slice_idx), ctx=ast.Store())

    def add_to_list(self, args):
        item, target = args
        load_target = to_load(target)
        call = ast.Call(
            func=ast.Attribute(value=load_target, attr="append", ctx=ast.Load()),
            args=[item],
            keywords=[]
        )
        return ast.Expr(value=call)

    def remove_from_list(self, args):
        item, target = args
        load_target = to_load(target)
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

    def yield_val(self, args):
        val = to_load(args[0]) if args and args[0] is not None else None
        return ast.Expr(value=ast.Yield(value=val))

    def yield_expr(self, args):
        val = to_load(args[0]) if args and args[0] is not None else None
        return ast.Yield(value=val)

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

    def with_stmt(self, args):
        if len(args) == 3:
            context_expr, target, body = args
            if target is None:
                opt_var = None
            else:
                opt_var = target if isinstance(target, ast.AST) else ast.Name(id=str(target), ctx=ast.Store())
        else:
            context_expr, body = args
            opt_var = None
        return ast.With(items=[ast.withitem(context_expr=to_load(context_expr), optional_vars=opt_var)], body=body)

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

    def for_target_names(self, args):
        names = [str(a) for a in args if a is not None]
        if len(names) == 1:
            return ast.Name(id=names[0], ctx=ast.Store())
        return ast.Tuple(elts=[ast.Name(id=n, ctx=ast.Store()) for n in names], ctx=ast.Store())

    def for_where_stmt(self, args):
        target, collection, condition, suite = args
        if isinstance(target, str):
            target = ast.Name(id=target, ctx=ast.Store())
        if_node = ast.If(test=condition, body=suite, orelse=[])
        return ast.For(target=target, iter=collection, body=[if_node], orelse=[])

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
        target, iterable, body = args
        if isinstance(target, str):
            target = ast.Name(id=target, ctx=ast.Store())
        return ast.For(
            target=target,
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

    def arg_name(self, args):
        return str(args[0])

    def arg_kw_reverse(self, _): return "reverse"
    def arg_kw_reversed(self, _): return "reversed"
    def arg_kw_count(self, _): return "count"
    def arg_kw_by(self, _): return "by"
    def arg_kw_of(self, _): return "of"
    def arg_kw_split(self, _): return "split"
    def arg_kw_key(self, _): return "key"
    def arg_kw_type(self, _): return "type"
    def arg_kw_mode(self, _): return "mode"
    def arg_kw_format(self, _): return "format"
    def arg_kw_step(self, _): return "step"
    def arg_kw_start(self, _): return "start"
    def arg_kw_stop(self, _): return "stop"
    def arg_kw_into(self, _): return "into"
    def arg_kw_from(self, _): return "from"
    def arg_kw_to(self, _): return "to"
    def arg_kw_with(self, _): return "with"
    def arg_kw_sort(self, _): return "sort"
    def arg_kw_sorted(self, _): return "sorted"
    def arg_kw_filter(self, _): return "filter"
    def arg_kw_sum(self, _): return "sum"
    def arg_kw_average(self, _): return "average"
    def arg_kw_first(self, _): return "first"
    def arg_kw_last(self, _): return "last"
    def arg_kw_round(self, _): return "round"
    def arg_kw_repeat(self, _): return "repeat"
    def arg_kw_copy(self, _): return "copy"
    def arg_kw_unique(self, _): return "unique"
    def arg_kw_item(self, _): return "item"
    def arg_kw_items(self, _): return "items"
    def arg_kw_when(self, _): return "when"
    def arg_kw_match(self, _): return "match"
    def arg_kw_where(self, _): return "where"
    def arg_kw_file(self, _): return "file"
    def arg_kw_files(self, _): return "files"
    def arg_kw_line(self, _): return "line"
    def arg_kw_lines(self, _): return "lines"
    def arg_kw_word(self, _): return "word"
    def arg_kw_words(self, _): return "words"
    def arg_kw_text(self, _): return "text"
    def arg_kw_number(self, _): return "number"
    def arg_kw_default(self, _): return "default"

    def param_item(self, args):
        name = getattr(args[0], "value", str(args[0]))
        default = args[1] if len(args) > 1 and args[1] is not None else None
        return (str(name), default)

    def param_list(self, args):
        return list(args)

    def kw_call_arg(self, args):
        arg_name = getattr(args[0], "value", str(args[0]))
        return ast.keyword(arg=str(arg_name), value=to_load(args[1]))

    def pos_call_arg(self, args):
        return args[0]

    def call_arg_name(self, args):
        return getattr(args[0], "value", str(args[0]))

    def call_arg(self, args):
        if len(args) == 2 and args[0] is not None:
            arg_name = getattr(args[0], "value", str(args[0]))
            return ast.keyword(arg=str(arg_name), value=to_load(args[1]))
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

    def class_def(self, args):
        name = str(args[0])
        if len(args) == 3:
            parent = str(args[1]) if args[1] is not None else None
            suite = args[2]
        else:
            parent = None
            suite = args[1]

        bases = [ast.Name(id=parent, ctx=ast.Load())] if parent else []
        class_body = []
        has_str = any(isinstance(s, ast.FunctionDef) and s.name == '__str__' for s in suite)

        for stmt in suite:
            if isinstance(stmt, ast.FunctionDef):
                if stmt.name.startswith('_var_'):
                    stmt.name = stmt.name[5:]
                if stmt.name.lower() in ('init', 'initialize', 'create', 'setup', 'constructor', 'start', '__init__'):
                    stmt.name = '__init__'
                arg_names = [a.arg for a in stmt.args.args]
                if not arg_names or arg_names[0] != 'self':
                    stmt.args.args.insert(0, ast.arg(arg='self', annotation=None))
                class_body.append(stmt)
                if stmt.name == '__repr__' and not has_str:
                    str_func = ast.FunctionDef(
                        name='__str__',
                        args=ast.arguments(
                            posonlyargs=[],
                            args=[ast.arg(arg='self', annotation=None)],
                            vararg=None,
                            kwonlyargs=[],
                            kw_defaults=[],
                            kwarg=None,
                            defaults=[]
                        ),
                        body=[ast.Return(value=ast.Call(
                            func=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='__repr__', ctx=ast.Load()),
                            args=[],
                            keywords=[]
                        ))],
                        decorator_list=[]
                    )
                    class_body.append(str_func)
            else:
                class_body.append(stmt)

        return ast.ClassDef(
            name=name,
            bases=bases,
            keywords=[],
            body=class_body if class_body else [ast.Pass()],
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
            "not in": ast.NotIn(),
            "is inside": ast.In(),
            "is in": ast.In(),
            "in": ast.In(),
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

    def is_even(self, args):
        val = to_load(args[0])
        mod = ast.BinOp(left=val, op=ast.Mod(), right=ast.Constant(value=2))
        return ast.Compare(left=mod, ops=[ast.Eq()], comparators=[ast.Constant(value=0)])

    def is_not_even(self, args):
        val = to_load(args[0])
        mod = ast.BinOp(left=val, op=ast.Mod(), right=ast.Constant(value=2))
        return ast.Compare(left=mod, ops=[ast.NotEq()], comparators=[ast.Constant(value=0)])

    def is_odd(self, args):
        val = to_load(args[0])
        mod = ast.BinOp(left=val, op=ast.Mod(), right=ast.Constant(value=2))
        return ast.Compare(left=mod, ops=[ast.NotEq()], comparators=[ast.Constant(value=0)])

    def is_not_odd(self, args):
        val = to_load(args[0])
        mod = ast.BinOp(left=val, op=ast.Mod(), right=ast.Constant(value=2))
        return ast.Compare(left=mod, ops=[ast.Eq()], comparators=[ast.Constant(value=0)])

    def is_positive(self, args):
        val = to_load(args[0])
        return ast.Compare(left=val, ops=[ast.Gt()], comparators=[ast.Constant(value=0)])

    def is_not_positive(self, args):
        val = to_load(args[0])
        return ast.Compare(left=val, ops=[ast.LtE()], comparators=[ast.Constant(value=0)])

    def is_negative(self, args):
        val = to_load(args[0])
        return ast.Compare(left=val, ops=[ast.Lt()], comparators=[ast.Constant(value=0)])

    def is_not_negative(self, args):
        val = to_load(args[0])
        return ast.Compare(left=val, ops=[ast.GtE()], comparators=[ast.Constant(value=0)])

    def is_zero(self, args):
        val = to_load(args[0])
        return ast.Compare(left=val, ops=[ast.Eq()], comparators=[ast.Constant(value=0)])

    def is_not_zero(self, args):
        val = to_load(args[0])
        return ast.Compare(left=val, ops=[ast.NotEq()], comparators=[ast.Constant(value=0)])

    def count_of(self, args):
        target = args[-1]
        return ast.Call(
            func=ast.Name(id='len', ctx=ast.Load()),
            args=[target],
            keywords=[]
        )

    def agg_sum(self, args):
        return ast.Call(func=ast.Name(id='agg_sum', ctx=ast.Load()), args=[args[-1]], keywords=[])

    def agg_avg(self, args):
        return ast.Call(func=ast.Name(id='agg_avg', ctx=ast.Load()), args=[args[-1]], keywords=[])

    def agg_max(self, args):
        return ast.Call(func=ast.Name(id='agg_max', ctx=ast.Load()), args=[args[0]], keywords=[])

    def agg_min(self, args):
        return ast.Call(func=ast.Name(id='agg_min', ctx=ast.Load()), args=[args[0]], keywords=[])

    def agg_first(self, args):
        return ast.Call(func=ast.Name(id='agg_first', ctx=ast.Load()), args=[args[0]], keywords=[])

    def agg_last(self, args):
        return ast.Call(func=ast.Name(id='agg_last', ctx=ast.Load()), args=[args[0]], keywords=[])

    def expr_join(self, args):
        items, delimiter = args[0], args[-1]
        return ast.Call(
            func=ast.Name(id='str_join', ctx=ast.Load()),
            args=[to_load(items), to_load(delimiter)],
            keywords=[]
        )

    def expr_replace(self, args):
        needle, replacement, source = args[0], args[1], args[2]
        return ast.Call(
            func=ast.Name(id='str_replace', ctx=ast.Load()),
            args=[to_load(source), to_load(needle), to_load(replacement)],
            keywords=[]
        )

    def expr_capitalize(self, args):
        return ast.Call(func=ast.Name(id='str_capitalize', ctx=ast.Load()), args=[to_load(args[0])], keywords=[])

    def expr_uppercase(self, args):
        return ast.Call(func=ast.Name(id='str_uppercase', ctx=ast.Load()), args=[args[0]], keywords=[])

    def expr_lowercase(self, args):
        return ast.Call(func=ast.Name(id='str_lowercase', ctx=ast.Load()), args=[args[0]], keywords=[])

    def expr_trim(self, args):
        return ast.Call(func=ast.Name(id='str_trim', ctx=ast.Load()), args=[args[0]], keywords=[])

    def expr_title(self, args):
        return ast.Call(func=ast.Name(id='str_title', ctx=ast.Load()), args=[args[0]], keywords=[])

    def expr_sorted(self, args):
        return ast.Call(func=ast.Name(id='sorted_list', ctx=ast.Load()), args=[args[-1]], keywords=[])

    def expr_reversed(self, args):
        return ast.Call(func=ast.Name(id='reversed_list', ctx=ast.Load()), args=[args[-1]], keywords=[])

    def expr_copy(self, args):
        return ast.Call(func=ast.Name(id='copy_value', ctx=ast.Load()), args=[args[-1]], keywords=[])

    def expr_unique(self, args):
        return ast.Call(func=ast.Name(id='unique_items', ctx=ast.Load()), args=[args[-1]], keywords=[])

    def expr_round(self, args):
        return ast.Call(func=ast.Name(id='math_round', ctx=ast.Load()), args=[args[-1]], keywords=[])

    def expr_round_dec(self, args):
        val = args[1] if len(args) > 2 else args[0]
        dec = args[-1]
        return ast.Call(func=ast.Name(id='math_round', ctx=ast.Load()), args=[val, dec], keywords=[])

    def expr_cast(self, args):
        val, type_tok = args
        t_str = str(type_tok).lower()
        if t_str == 'number':
            return ast.Call(func=ast.Name(id='to_number', ctx=ast.Load()), args=[val], keywords=[])
        elif t_str in ('text', 'string'):
            return ast.Call(func=ast.Name(id='to_text', ctx=ast.Load()), args=[val], keywords=[])
        elif t_str in ('boolean', 'bool'):
            return ast.Call(func=ast.Name(id='bool', ctx=ast.Load()), args=[val], keywords=[])
        return val

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
        return ast.Call(
            func=ast.Name(id="get_field", ctx=ast.Load()),
            args=[to_load(atom), ast.Constant(value=str(attr))],
            keywords=[]
        )

    def attr_access(self, args):
        val, attr = args
        return ast.Attribute(value=to_load(val), attr=str(attr), ctx=ast.Load())

    def call_expr(self, args):
        func = args[0]
        call_items = args[1] if len(args) > 1 and args[1] is not None else []
        pos_args = [to_load(a) for a in call_items if not isinstance(a, ast.keyword)]
        keywords = [a for a in call_items if isinstance(a, ast.keyword)]
        func_node = ast.Name(id=str(func), ctx=ast.Load()) if isinstance(func, str) else to_load(func)
        return ast.Call(
            func=func_node,
            args=pos_args,
            keywords=keywords
        )

    def standard_call(self, args):
        return self.call_expr(args)

    def subscript_expr(self, args):
        val, slice_idx = args
        return ast.Subscript(value=to_load(val), slice=to_load(slice_idx), ctx=ast.Load())

    def var(self, args):
        name = str(args[0])
        if name == "True":
            return ast.Constant(value=True)
        if name == "False":
            return ast.Constant(value=False)
        if name == "None":
            return ast.Constant(value=None)
        return ast.Name(id=name, ctx=ast.Load())

    def num(self, args):
        s = str(args[0])
        val = float(s) if ('.' in s or 'e' in s.lower()) else int(s)
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

    def bitor(self, args):
        return ast.BinOp(left=to_load(args[0]), op=ast.BitOr(), right=to_load(args[1]))

    def bitxor(self, args):
        return ast.BinOp(left=to_load(args[0]), op=ast.BitXor(), right=to_load(args[1]))

    def bitand(self, args):
        return ast.BinOp(left=to_load(args[0]), op=ast.BitAnd(), right=to_load(args[1]))

    def floor_div(self, args):
        return ast.BinOp(left=to_load(args[0]), op=ast.FloorDiv(), right=to_load(args[1]))

    def mod_op(self, args):
        return ast.BinOp(left=to_load(args[0]), op=ast.Mod(), right=to_load(args[1]))

    def pow(self, args):
        return ast.BinOp(left=to_load(args[0]), op=ast.Pow(), right=to_load(args[1]))

    def empty_tuple(self, _):
        return ast.Tuple(elts=[], ctx=ast.Load())

    def tuple_val(self, args):
        elts = [to_load(a) for a in args if a is not None]
        return ast.Tuple(elts=elts, ctx=ast.Load())

    def slice_full(self, args):
        lower = args[0]
        upper = args[1] if len(args) > 1 else None
        step = args[2] if len(args) > 2 else None
        return ast.Slice(
            lower=to_load(lower) if lower is not None else None,
            upper=to_load(upper) if upper is not None else None,
            step=to_load(step) if step is not None else None
        )

    def slice_lead(self, args):
        upper = args[0] if len(args) > 0 else None
        step = args[1] if len(args) > 1 else None
        return ast.Slice(
            lower=None,
            upper=to_load(upper) if upper is not None else None,
            step=to_load(step) if step is not None else None
        )

    def index_expr(self, args):
        return args[0]

    def subscript_indices(self, args):
        items = [a for a in args if a is not None]
        if len(items) == 1:
            return items[0]
        return ast.Tuple(elts=[to_load(i) for i in items], ctx=ast.Load())

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
        if isinstance(k, ast.Name):
            key_node = ast.Constant(value=k.id)
        elif isinstance(k, str):
            key_node = ast.Constant(value=k[1:-1] if k.startswith(('"', "'")) else k)
        elif isinstance(k, ast.Constant):
            key_node = k
        else:
            key_node = to_load(k)
        return ("dict", key_node, to_load(v))

    def set_item(self, args):
        return ("set", to_load(args[0]))

    def brace_items(self, args):
        return [a for a in args if a is not None]

    def dict_or_set_val(self, args):
        items = args[0] if args and args[0] is not None else []
        if not items:
            return ast.Call(
                func=ast.Name(id='Record', ctx=ast.Load()),
                args=[ast.Dict(keys=[], values=[])],
                keywords=[]
            )
        if items[0][0] == "dict":
            keys = [item[1] for item in items]
            vals = [item[2] for item in items]
            raw_dict = ast.Dict(keys=keys, values=vals)
            return ast.Call(
                func=ast.Name(id='Record', ctx=ast.Load()),
                args=[raw_dict],
                keywords=[]
            )
        else:
            elts = [item[1] for item in items]
            return ast.Set(elts=elts)

    def comp_clause(self, args):
        target = args[0]
        iter_expr = args[1]
        cond_expr = args[2] if len(args) > 2 and args[2] is not None else None
        ifs = [to_load(cond_expr)] if cond_expr is not None else []
        return ast.comprehension(target=target, iter=to_load(iter_expr), ifs=ifs, is_async=0)

    def list_comp(self, args):
        elt = to_load(args[0])
        generators = args[1:]
        return ast.ListComp(elt=elt, generators=generators)

    def set_comp(self, args):
        elt = to_load(args[0])
        generators = args[1:]
        return ast.SetComp(elt=elt, generators=generators)

    def dict_comp(self, args):
        key = to_load(args[0])
        val = to_load(args[1])
        generators = args[2:]
        return ast.DictComp(key=key, value=val, generators=generators)

    def lambda_expr(self, args):
        if len(args) == 2:
            target, body = args
        elif len(args) == 1:
            target, body = None, args[0]
        else:
            target, body = None, None

        posargs = []
        if isinstance(target, ast.Name):
            posargs = [ast.arg(arg=target.id)]
        elif isinstance(target, ast.Tuple):
            posargs = [ast.arg(arg=elt.id) for elt in target.elts if isinstance(elt, ast.Name)]
        elif isinstance(target, list):
            posargs = [ast.arg(arg=str(t)) for t in target]

        args_node = ast.arguments(
            posonlyargs=[],
            args=posargs,
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[]
        )
        return ast.Lambda(args=args_node, body=to_load(body))

