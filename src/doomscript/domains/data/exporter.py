"""Native Python AST Exporter for Data Engineering pipelines."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.data.spec import (
    PipelineSpec,
    DedupeStep,
    FilterStep,
    FillNaStep,
    DeriveStep,
    JoinStep,
    GroupByStep,
    SortStep,
    SinkStep,
)


class DataASTExporter(DomainASTExporter):
    """Translates PipelineSpec IR into idiomatic native Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        if not isinstance(ir, PipelineSpec):
            raise TypeError(f"DataASTExporter expects PipelineSpec, got {type(ir).__name__}")

        imports: Set[str] = {"pandas"}
        stmts: List[ast.stmt] = []

        # 1. Resolve source: df = pd.DataFrame(source) or pd.read_csv(source)
        src = ir.source
        target_df = f"{var_name}_df"

        if src.endswith(".csv"):
            load_call = ast.Call(
                func=ast.Attribute(value=ast.Name(id="pd", ctx=ast.Load()), attr="read_csv", ctx=ast.Load()),
                args=[ast.Constant(value=src)],
                keywords=[],
            )
        else:
            load_call = ast.Call(
                func=ast.Attribute(value=ast.Name(id="pd", ctx=ast.Load()), attr="DataFrame", ctx=ast.Load()),
                args=[ast.Name(id=src, ctx=ast.Load())],
                keywords=[],
            )

        stmts.append(ast.Assign(targets=[ast.Name(id=target_df, ctx=ast.Store())], value=load_call))

        # 2. Sequential pipeline transformations
        for step in ir.steps:
            if isinstance(step, DedupeStep):
                kw = [ast.keyword(arg="subset", value=ast.Constant(value=step.by_columns))] if step.by_columns else []
                drop_call = ast.Call(
                    func=ast.Attribute(value=ast.Name(id=target_df, ctx=ast.Load()), attr="drop_duplicates", ctx=ast.Load()),
                    args=[],
                    keywords=kw,
                )
                stmts.append(ast.Assign(targets=[ast.Name(id=target_df, ctx=ast.Store())], value=drop_call))

            elif isinstance(step, FillNaStep):
                fill_call = ast.Call(
                    func=ast.Attribute(
                        value=ast.Subscript(
                            value=ast.Name(id=target_df, ctx=ast.Load()),
                            slice=ast.Constant(value=step.column),
                            ctx=ast.Load(),
                        ),
                        attr="fillna",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Constant(value=step.value)],
                    keywords=[],
                )
                stmts.append(
                    ast.Assign(
                        targets=[
                            ast.Subscript(
                                value=ast.Name(id=target_df, ctx=ast.Load()),
                                slice=ast.Constant(value=step.column),
                                ctx=ast.Store(),
                            )
                        ],
                        value=fill_call,
                    )
                )

            elif isinstance(step, DeriveStep):
                # E.g. target_df['net'] = target_df['amount'] * (1.0 - target_df['discount'])
                # Using df.eval for clean pandas expressions
                eval_call = ast.Call(
                    func=ast.Attribute(value=ast.Name(id=target_df, ctx=ast.Load()), attr="eval", ctx=ast.Load()),
                    args=[ast.Constant(value=step.expression)],
                    keywords=[],
                )
                stmts.append(
                    ast.Assign(
                        targets=[
                            ast.Subscript(
                                value=ast.Name(id=target_df, ctx=ast.Load()),
                                slice=ast.Constant(value=step.target_col),
                                ctx=ast.Store(),
                            )
                        ],
                        value=eval_call,
                    )
                )

            elif isinstance(step, FilterStep):
                cond_str = step.condition.strip()
                replacements = [
                    (r"\bis\s+greater\s+than\s+or\s+equal\s+to\b", ">="),
                    (r"\bis\s+less\s+than\s+or\s+equal\s+to\b", "<="),
                    (r"\bis\s+strictly\s+greater\s+than\b", ">"),
                    (r"\bis\s+strictly\s+less\s+than\b", "<"),
                    (r"\bis\s+at\s+least\b", ">="),
                    (r"\bis\s+at\s+most\b", "<="),
                    (r"\bis\s+greater\s+than\b", ">"),
                    (r"\bis\s+less\s+than\b", "<"),
                    (r"\bis\s+more\s+than\b", ">"),
                    (r"\bis\s+over\b", ">"),
                    (r"\bis\s+under\b", "<"),
                    (r"\bis\s+above\b", ">"),
                    (r"\bis\s+below\b", "<"),
                    (r"\bis\s+equal\s+to\b", "=="),
                    (r"\bis\s+identical\s+to\b", "=="),
                    (r"\bis\s+the\s+same\s+as\b", "=="),
                    (r"\bequals\b", "=="),
                    (r"\bdoes\s+not\s+equal\b", "!="),
                    (r"\bis\s+not\s+equal\s+to\b", "!="),
                    (r"\bis\s+not\b", "!="),
                ]
                import re
                for pat, rep in replacements:
                    cond_str = re.sub(pat, rep, cond_str, flags=re.IGNORECASE)

                query_call = ast.Call(
                    func=ast.Attribute(value=ast.Name(id=target_df, ctx=ast.Load()), attr="query", ctx=ast.Load()),
                    args=[ast.Constant(value=cond_str)],
                    keywords=[],
                )
                stmts.append(ast.Assign(targets=[ast.Name(id=target_df, ctx=ast.Store())], value=query_call))

            elif isinstance(step, GroupByStep):
                # agg_dict = {'amount': 'sum', ...}
                agg_keys = [ast.Constant(value=src_col) for _, (_, src_col) in step.aggregations.items()]
                agg_vals = [ast.Constant(value=agg_fn.lower()) for _, (agg_fn, _) in step.aggregations.items()]
                agg_dict = ast.Dict(keys=agg_keys, values=agg_vals)

                group_call = ast.Call(
                    func=ast.Attribute(
                        value=ast.Call(
                            func=ast.Attribute(value=ast.Name(id=target_df, ctx=ast.Load()), attr="groupby", ctx=ast.Load()),
                            args=[ast.Constant(value=step.keys[0] if len(step.keys) == 1 else step.keys)],
                            keywords=[ast.keyword(arg="as_index", value=ast.Constant(value=False))],
                        ),
                        attr="agg",
                        ctx=ast.Load(),
                    ),
                    args=[agg_dict],
                    keywords=[],
                )
                stmts.append(ast.Assign(targets=[ast.Name(id=target_df, ctx=ast.Store())], value=group_call))

            elif isinstance(step, SortStep):
                sort_call = ast.Call(
                    func=ast.Attribute(value=ast.Name(id=target_df, ctx=ast.Load()), attr="sort_values", ctx=ast.Load()),
                    args=[ast.Constant(value=step.column)],
                    keywords=[ast.keyword(arg="ascending", value=ast.Constant(value=not step.descending))],
                )
                stmts.append(ast.Assign(targets=[ast.Name(id=target_df, ctx=ast.Store())], value=sort_call))

        # 3. Sink
        if ir.sink:
            to_csv_call = ast.Call(
                func=ast.Attribute(value=ast.Name(id=target_df, ctx=ast.Load()), attr="to_csv", ctx=ast.Load()),
                args=[ast.Constant(value=ir.sink.path)],
                keywords=[ast.keyword(arg="index", value=ast.Constant(value=False))],
            )
            stmts.append(ast.Expr(value=to_csv_call))

        # 4. Final assignment to target variable: var_name = target_df.to_dict(orient='records')
        to_dict_call = ast.Call(
            func=ast.Attribute(value=ast.Name(id=target_df, ctx=ast.Load()), attr="to_dict", ctx=ast.Load()),
            args=[],
            keywords=[ast.keyword(arg="orient", value=ast.Constant(value="records"))],
        )
        stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=to_dict_call))

        return imports, stmts
