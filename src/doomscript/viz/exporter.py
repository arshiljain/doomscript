"""Native Python Code Exporter for Lets-Plot.

Translates PlotSpec IR into clean, idiomatic native Python code
using lets_plot functions (ggplot, aes, geom_*, theme_*, etc.)
constructed safely via typed Python AST.
"""

import ast
from typing import Any, List, Optional, Set, Tuple
from doomscript.viz.spec import PlotSpec


class LetsPlotExporter:
    """Translates PlotSpec IR into idiomatic native Python lets_plot statements via AST."""

    def to_ast(
        self,
        spec: PlotSpec,
        var_name: str = "p",
        data_node: Optional[ast.expr] = None,
    ) -> Tuple[Set[str], ast.Assign]:
        """Translates a PlotSpec into a native Python AST Assign statement and set of imports.

        Returns (imported_symbols, assign_node).
        """
        imports: Set[str] = {"ggplot"}

        # 1. Resolve data node
        if data_node is None:
            if isinstance(spec.data, str):
                if spec.data.isidentifier():
                    data_node = ast.Name(id=spec.data, ctx=ast.Load())
                else:
                    data_node = ast.parse(spec.data, mode="eval").body
            elif isinstance(spec.data, (int, float, bool)):
                data_node = ast.Constant(value=spec.data)
            else:
                data_node = ast.parse(repr(spec.data), mode="eval").body

        # 2. Global aes mappings
        aes_pairs: List[ast.keyword] = []
        mapping_keys = [
            ("x", spec.mapping.x),
            ("y", spec.mapping.y),
            ("color", spec.mapping.color),
            ("fill", spec.mapping.fill),
            ("size", spec.mapping.size),
            ("shape", spec.mapping.shape),
            ("alpha", spec.mapping.alpha),
            ("group", spec.mapping.group),
            ("slice", spec.mapping.slice),
            ("weight", spec.mapping.value),
        ]
        for k, v in mapping_keys:
            if v is not None:
                aes_pairs.append(ast.keyword(arg=k, value=ast.Constant(value=v)))

        if aes_pairs:
            imports.add("aes")
            aes_call = ast.Call(
                func=ast.Name(id="aes", ctx=ast.Load()),
                args=[],
                keywords=aes_pairs,
            )
            expr: ast.expr = ast.Call(
                func=ast.Name(id="ggplot", ctx=ast.Load()),
                args=[data_node, aes_call],
                keywords=[],
            )
        else:
            expr = ast.Call(
                func=ast.Name(id="ggplot", ctx=ast.Load()),
                args=[data_node],
                keywords=[],
            )

        # 3. Layers
        for layer in spec.layers:
            g = layer.geom
            if g == "scatter":
                g = "point"
            func_name = f"geom_{g}"
            imports.add(func_name)

            kw: List[ast.keyword] = []
            if layer.stat:
                kw.append(ast.keyword(arg="stat", value=ast.Constant(value=layer.stat)))
            for k, v in layer.params.items():
                if isinstance(v, (int, float, str, bool)) or v is None:
                    v_node = ast.Constant(value=v)
                else:
                    v_node = ast.parse(repr(v), mode="eval").body
                kw.append(ast.keyword(arg=k, value=v_node))

            layer_call = ast.Call(
                func=ast.Name(id=func_name, ctx=ast.Load()),
                args=[],
                keywords=kw,
            )
            expr = ast.BinOp(left=expr, op=ast.Add(), right=layer_call)

        # 4. Facets
        if spec.facet:
            if spec.facet.type == "wrap" and spec.facet.facets:
                imports.add("facet_wrap")
                kw = [ast.keyword(arg="facets", value=ast.Constant(value=spec.facet.facets))]
                if spec.facet.scales:
                    kw.append(ast.keyword(arg="scales", value=ast.Constant(value=spec.facet.scales)))
                call = ast.Call(func=ast.Name(id="facet_wrap", ctx=ast.Load()), args=[], keywords=kw)
                expr = ast.BinOp(left=expr, op=ast.Add(), right=call)
            elif spec.facet.type == "grid":
                imports.add("facet_grid")
                kw = []
                if spec.facet.col:
                    kw.append(ast.keyword(arg="x", value=ast.Constant(value=spec.facet.col)))
                if spec.facet.row:
                    kw.append(ast.keyword(arg="y", value=ast.Constant(value=spec.facet.row)))
                if spec.facet.scales:
                    kw.append(ast.keyword(arg="scales", value=ast.Constant(value=spec.facet.scales)))
                call = ast.Call(func=ast.Name(id="facet_grid", ctx=ast.Load()), args=[], keywords=kw)
                expr = ast.BinOp(left=expr, op=ast.Add(), right=call)

        # 5. Labels
        if spec.labels.title:
            imports.add("ggtitle")
            call = ast.Call(
                func=ast.Name(id="ggtitle", ctx=ast.Load()),
                args=[ast.Constant(value=spec.labels.title)],
                keywords=[],
            )
            expr = ast.BinOp(left=expr, op=ast.Add(), right=call)
        if spec.labels.x:
            imports.add("xlab")
            call = ast.Call(
                func=ast.Name(id="xlab", ctx=ast.Load()),
                args=[ast.Constant(value=spec.labels.x)],
                keywords=[],
            )
            expr = ast.BinOp(left=expr, op=ast.Add(), right=call)
        if spec.labels.y:
            imports.add("ylab")
            call = ast.Call(
                func=ast.Name(id="ylab", ctx=ast.Load()),
                args=[ast.Constant(value=spec.labels.y)],
                keywords=[],
            )
            expr = ast.BinOp(left=expr, op=ast.Add(), right=call)

        labs_kw: List[ast.keyword] = []
        for lab_attr in ("subtitle", "caption", "color", "fill"):
            val = getattr(spec.labels, lab_attr, None)
            if val:
                labs_kw.append(ast.keyword(arg=lab_attr, value=ast.Constant(value=val)))
        if labs_kw:
            imports.add("labs")
            call = ast.Call(func=ast.Name(id="labs", ctx=ast.Load()), args=[], keywords=labs_kw)
            expr = ast.BinOp(left=expr, op=ast.Add(), right=call)

        # 6. Themes
        theme_name = spec.theme.name
        if theme_name in ("minimal", "classic", "bw", "light", "void", "grey", "gray", "dark"):
            if theme_name in ("grey", "gray"):
                th_func = "theme_grey"
            elif theme_name == "dark":
                th_func = "theme_minimal"
            else:
                th_func = f"theme_{theme_name}"
            imports.add(th_func)
            call = ast.Call(func=ast.Name(id=th_func, ctx=ast.Load()), args=[], keywords=[])
            expr = ast.BinOp(left=expr, op=ast.Add(), right=call)
            if theme_name == "dark" or spec.theme.dark_mode:
                imports.add("flavor_darcula")
                call = ast.Call(func=ast.Name(id="flavor_darcula", ctx=ast.Load()), args=[], keywords=[])
                expr = ast.BinOp(left=expr, op=ast.Add(), right=call)

        # 7. Scales
        for s in spec.scales:
            if s.target == "color" and s.type == "palette":
                imports.add("scale_color_viridis")
                kw = [ast.keyword(arg="option", value=ast.Constant(value=s.palette_name))] if s.palette_name else []
                call = ast.Call(func=ast.Name(id="scale_color_viridis", ctx=ast.Load()), args=[], keywords=kw)
                expr = ast.BinOp(left=expr, op=ast.Add(), right=call)
            elif s.target == "fill" and s.type == "palette":
                imports.add("scale_fill_viridis")
                kw = [ast.keyword(arg="option", value=ast.Constant(value=s.palette_name))] if s.palette_name else []
                call = ast.Call(func=ast.Name(id="scale_fill_viridis", ctx=ast.Load()), args=[], keywords=kw)
                expr = ast.BinOp(left=expr, op=ast.Add(), right=call)
            elif s.target == "x" and s.type == "log":
                imports.add("scale_x_log10")
                call = ast.Call(func=ast.Name(id="scale_x_log10", ctx=ast.Load()), args=[], keywords=[])
                expr = ast.BinOp(left=expr, op=ast.Add(), right=call)
            elif s.target == "y" and s.type == "log":
                imports.add("scale_y_log10")
                call = ast.Call(func=ast.Name(id="scale_y_log10", ctx=ast.Load()), args=[], keywords=[])
                expr = ast.BinOp(left=expr, op=ast.Add(), right=call)
            elif s.target == "y" and s.type == "reverse":
                imports.add("scale_y_reverse")
                call = ast.Call(func=ast.Name(id="scale_y_reverse", ctx=ast.Load()), args=[], keywords=[])
                expr = ast.BinOp(left=expr, op=ast.Add(), right=call)

        # 8. Annotations
        for ann in spec.annotations:
            imports.add("geom_text")
            kw = [
                ast.keyword(arg="label", value=ast.Constant(value=ann.text)),
                ast.keyword(
                    arg="x",
                    value=ast.Constant(value=ann.x)
                    if isinstance(ann.x, (int, float, str, bool))
                    else ast.parse(repr(ann.x), mode="eval").body,
                ),
                ast.keyword(
                    arg="y",
                    value=ast.Constant(value=ann.y)
                    if isinstance(ann.y, (int, float, str, bool))
                    else ast.parse(repr(ann.y), mode="eval").body,
                ),
            ]
            if ann.color is not None:
                kw.append(ast.keyword(arg="color", value=ast.Constant(value=ann.color)))
            if ann.size is not None:
                kw.append(ast.keyword(arg="size", value=ast.Constant(value=ann.size)))
            if ann.alpha is not None:
                kw.append(ast.keyword(arg="alpha", value=ast.Constant(value=ann.alpha)))
            call = ast.Call(func=ast.Name(id="geom_text", ctx=ast.Load()), args=[], keywords=kw)
            expr = ast.BinOp(left=expr, op=ast.Add(), right=call)

        assign_node = ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=expr)
        ast.fix_missing_locations(assign_node)
        return imports, assign_node

    def to_statements(
        self,
        spec: PlotSpec,
        var_name: str = "p",
        data_node: Optional[ast.expr] = None,
    ) -> List[ast.stmt]:
        """Returns import and assignment statements for the plot specification."""
        imports, assign_node = self.to_ast(spec, var_name, data_node=data_node)
        import_stmt = ast.ImportFrom(
            module="lets_plot",
            names=[ast.alias(name=n) for n in sorted(imports)],
            level=0,
        )
        ast.fix_missing_locations(import_stmt)
        return [import_stmt, assign_node]

    def to_python(self, spec: PlotSpec, var_name: str = "p") -> str:
        """Translates PlotSpec into runnable native Python source code."""
        stmts = self.to_statements(spec, var_name)
        mod = ast.Module(body=stmts, type_ignores=[])
        ast.fix_missing_locations(mod)
        return ast.unparse(mod)


def eval_ast_arg(node: ast.AST) -> Any:
    """Helper to evaluate simple constant or identifier arguments from AST."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return node.id
    try:
        return ast.literal_eval(node)
    except Exception:
        return ast.unparse(node)


def transform_viz_ast(module: ast.Module) -> Tuple[ast.Module, Set[str]]:
    """Rewrites PlotBuilder AST statements into native lets_plot statements.

    Replaces:
    - `p = PlotBuilder(...).kind(...)`
    - `p = PlotBuilder(...); if True: ...; p.draw(...)`
    - `save_plot(p, path, ...)` -> `ggsave(p, filename=..., path='.')`
    - `show_plot(p)` -> `p.show()`
    """
    from doomscript.viz.builder import PlotBuilder

    new_body: List[ast.stmt] = []
    all_imports: Set[str] = set()
    i = 0
    stmts = module.body
    n = len(stmts)

    while i < n:
        stmt = stmts[i]

        # Case 1: Single-line plot: p = PlotBuilder(...).kind(...)
        if (
            isinstance(stmt, ast.Assign)
            and len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Name)
            and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Attribute)
            and stmt.value.func.attr == "kind"
            and isinstance(stmt.value.func.value, ast.Call)
            and isinstance(stmt.value.func.value.func, ast.Name)
            and stmt.value.func.value.func.id == "PlotBuilder"
        ):
            var_name = stmt.targets[0].id
            builder_call = stmt.value.func.value
            data_node = builder_call.args[0] if builder_call.args else None
            title = None
            for kw in builder_call.keywords:
                if kw.arg == "title":
                    title = eval_ast_arg(kw.value)

            builder = PlotBuilder(data="placeholder", title=title)
            kind_args = [eval_ast_arg(a) for a in stmt.value.args]
            kind_kwargs = {kw.arg: eval_ast_arg(kw.value) for kw in stmt.value.keywords}
            builder.kind(*kind_args, **kind_kwargs)

            exporter = LetsPlotExporter()
            imps, assign = exporter.to_ast(builder.spec(), var_name=var_name, data_node=data_node)
            all_imports.update(imps)
            new_body.append(assign)
            i += 1
            continue

        # Case 2: Block plot: p = PlotBuilder(...) followed by if True: block and optional draw
        if (
            isinstance(stmt, ast.Assign)
            and len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Name)
            and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Name)
            and stmt.value.func.id == "PlotBuilder"
        ):
            var_name = stmt.targets[0].id
            data_node = stmt.value.args[0] if stmt.value.args else None
            title = None
            for kw in stmt.value.keywords:
                if kw.arg == "title":
                    title = eval_ast_arg(kw.value)

            builder = PlotBuilder(data="placeholder", title=title)

            # Consume subsequent if True: configuration block and draw statements
            i += 1
            while i < n:
                next_stmt = stmts[i]
                if (
                    isinstance(next_stmt, ast.If)
                    and isinstance(next_stmt.test, ast.Constant)
                    and next_stmt.test.value is True
                ):
                    def apply_calls(body_list):
                        for item in body_list:
                            if isinstance(item, ast.Expr) and isinstance(item.value, ast.Call):
                                call = item.value
                                if (
                                    isinstance(call.func, ast.Attribute)
                                    and isinstance(call.func.value, ast.Name)
                                    and call.func.value.id == var_name
                                ):
                                    method = getattr(builder, call.func.attr, None)
                                    if method:
                                        c_args = [eval_ast_arg(a) for a in call.args]
                                        c_kwargs = {kw.arg: eval_ast_arg(kw.value) for kw in call.keywords}
                                        method(*c_args, **c_kwargs)
                            elif (
                                isinstance(item, ast.If)
                                and isinstance(item.test, ast.Constant)
                                and item.test.value is True
                            ):
                                apply_calls(item.body)

                    apply_calls(next_stmt.body)
                    i += 1
                elif (
                    isinstance(next_stmt, ast.Expr)
                    and isinstance(next_stmt.value, ast.Call)
                    and isinstance(next_stmt.value.func, ast.Attribute)
                    and isinstance(next_stmt.value.func.value, ast.Name)
                    and next_stmt.value.func.value.id == var_name
                    and next_stmt.value.func.attr == "draw"
                ):
                    call = next_stmt.value
                    c_args = [eval_ast_arg(a) for a in call.args]
                    c_kwargs = {kw.arg: eval_ast_arg(kw.value) for kw in call.keywords}
                    builder.draw(*c_args, **c_kwargs)
                    i += 1
                else:
                    break

            exporter = LetsPlotExporter()
            imps, assign = exporter.to_ast(builder.spec(), var_name=var_name, data_node=data_node)
            all_imports.update(imps)
            new_body.append(assign)
            continue

        # Case 3: save_plot(p, path, ...) -> ggsave(p, filename=..., path='.')
        if (
            isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Name)
            and stmt.value.func.id == "save_plot"
            and len(stmt.value.args) >= 2
        ):
            p_node = stmt.value.args[0]
            path_node = stmt.value.args[1]
            all_imports.add("ggsave")

            ggsave_args = [p_node, path_node]
            ggsave_kw: List[ast.keyword] = [
                ast.keyword(arg="path", value=ast.Constant(value="."))
            ]
            for kw in stmt.value.keywords:
                ggsave_kw.append(kw)

            stmt.value = ast.Call(
                func=ast.Name(id="ggsave", ctx=ast.Load()),
                args=ggsave_args,
                keywords=ggsave_kw,
            )
            new_body.append(stmt)
            i += 1
            continue

        # Case 4: show_plot(p) -> p.show()
        if (
            isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Name)
            and stmt.value.func.id == "show_plot"
            and len(stmt.value.args) == 1
        ):
            p_node = stmt.value.args[0]
            stmt.value = ast.Call(
                func=ast.Attribute(value=p_node, attr="show", ctx=ast.Load()),
                args=[],
                keywords=[],
            )
            new_body.append(stmt)
            i += 1
            continue

        new_body.append(stmt)
        i += 1

    if all_imports:
        import_stmt = ast.ImportFrom(
            module="lets_plot",
            names=[ast.alias(name=n) for n in sorted(all_imports)],
            level=0,
        )
        new_body.insert(0, import_stmt)

    new_mod = ast.Module(body=new_body, type_ignores=[])
    ast.fix_missing_locations(new_mod)
    return new_mod, all_imports
