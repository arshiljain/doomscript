"""Native Python AST Exporter for AI Agents & Multi-Agent Workflows domain."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.agent.spec import AgentSpec, TaskSpec, TeamSpec


class AgentASTExporter(DomainASTExporter):
    """Translates Agent Domain IR into Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        imports: Set[str] = {"doomscript.domains.agent.runtime"}
        stmts: List[ast.stmt] = []

        if isinstance(ir, AgentSpec):
            # var_name = create_agent(name=..., role=..., instructions=..., model=..., tools=[...])
            call_node = ast.Call(
                func=ast.Name(id="create_agent", ctx=ast.Load()),
                args=[ast.Constant(value=ir.name)],
                keywords=[
                    ast.keyword(arg="role", value=ast.Constant(value=ir.role)),
                    ast.keyword(arg="instructions", value=ast.Constant(value=ir.instructions)),
                    ast.keyword(arg="model", value=ast.Constant(value=ir.model)),
                    ast.keyword(
                        arg="tools",
                        value=ast.List(
                            elts=[ast.Constant(value=t) for t in ir.tools],
                            ctx=ast.Load(),
                        ),
                    ),
                ],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, TaskSpec):
            call_node = ast.Call(
                func=ast.Name(id="ask_agent", ctx=ast.Load()),
                args=[
                    ast.Name(id=ir.agent_var, ctx=ast.Load()),
                    ast.Constant(value=ir.task),
                ],
                keywords=[
                    ast.keyword(
                        arg="context",
                        value=ast.Name(id=ir.context_var, ctx=ast.Load()) if ir.context_var else ast.Constant(value=None),
                    ),
                    ast.keyword(arg="as_json", value=ast.Constant(value=ir.as_json)),
                ],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, TeamSpec):
            call_node = ast.Call(
                func=ast.Name(id="create_team", ctx=ast.Load()),
                args=[
                    ast.Constant(value=ir.team_name),
                    ast.List(
                        elts=[ast.Name(id=v, ctx=ast.Load()) for v in ir.agent_vars],
                        ctx=ast.Load(),
                    ),
                ],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        return imports, stmts
