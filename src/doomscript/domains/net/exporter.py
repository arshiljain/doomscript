"""Native Python AST Exporter for Web & API Automation domain."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.net.spec import ApiWorkflowSpec, RequestStep, ParseStep, SaveStep


class NetASTExporter(DomainASTExporter):
    """Translates ApiWorkflowSpec IR into standard library urllib.request Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        if not isinstance(ir, ApiWorkflowSpec):
            raise TypeError(f"NetASTExporter expects ApiWorkflowSpec, got {type(ir).__name__}")

        imports: Set[str] = {"urllib.request", "json"}
        stmts: List[ast.stmt] = []

        base = ir.base_url.rstrip("/")

        for step in ir.steps:
            if isinstance(step, RequestStep):
                url = step.url_or_endpoint
                if base and not url.startswith("http"):
                    url = f"{base}/{url.lstrip('/')}"

                # req = urllib.request.Request(url, method=method)
                req_var = f"{step.target}_req"
                req_call = ast.Call(
                    func=ast.Attribute(
                        value=ast.Attribute(value=ast.Name(id="urllib", ctx=ast.Load()), attr="request", ctx=ast.Load()),
                        attr="Request",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Constant(value=url)],
                    keywords=[ast.keyword(arg="method", value=ast.Constant(value=step.method))],
                )
                stmts.append(ast.Assign(targets=[ast.Name(id=req_var, ctx=ast.Store())], value=req_call))

                # with urllib.request.urlopen(req) as resp: body = resp.read()
                resp_var = f"{step.target}_raw"
                urlopen_call = ast.Call(
                    func=ast.Attribute(
                        value=ast.Attribute(value=ast.Name(id="urllib", ctx=ast.Load()), attr="request", ctx=ast.Load()),
                        attr="urlopen",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Name(id=req_var, ctx=ast.Load())],
                    keywords=[ast.keyword(arg="timeout", value=ast.Constant(value=ir.timeout))],
                )
                read_call = ast.Call(
                    func=ast.Attribute(value=ast.Name(id=resp_var, ctx=ast.Load()), attr="read", ctx=ast.Load()),
                    args=[],
                    keywords=[],
                )
                with_stmt = ast.With(
                    items=[ast.withitem(context_expr=urlopen_call, optional_vars=ast.Name(id=resp_var, ctx=ast.Store()))],
                    body=[
                        ast.Assign(
                            targets=[ast.Name(id=f"{step.target}_body", ctx=ast.Store())],
                            value=read_call,
                        )
                    ],
                )
                stmts.append(with_stmt)

            elif isinstance(step, ParseStep):
                # target = json.loads(src_body.decode('utf-8'))
                decode_call = ast.Call(
                    func=ast.Attribute(value=ast.Name(id=f"{step.source_resp}_body", ctx=ast.Load()), attr="decode", ctx=ast.Load()),
                    args=[ast.Constant(value="utf-8")],
                    keywords=[],
                )
                json_call = ast.Call(
                    func=ast.Attribute(value=ast.Name(id="json", ctx=ast.Load()), attr="loads", ctx=ast.Load()),
                    args=[decode_call],
                    keywords=[],
                )
                stmts.append(ast.Assign(targets=[ast.Name(id=step.target, ctx=ast.Store())], value=json_call))

        # Assign final output to var_name
        last_step = ir.steps[-1] if ir.steps else None
        last_var = last_step.target if hasattr(last_step, "target") else "None"
        stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=ast.Name(id=last_var, ctx=ast.Load())))

        return imports, stmts
