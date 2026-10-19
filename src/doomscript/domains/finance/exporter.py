"""Native Python AST Exporter for Quantitative Finance domain."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.finance.spec import (
    FinanceFetchSpec,
    FinanceMavSpec,
    FinanceRsiSpec,
    FinanceReturnsSpec,
    FinanceSharpeSpec,
    FinanceBacktestSpec,
)


class FinanceASTExporter(DomainASTExporter):
    """Translates Finance Domain IR into Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        imports: Set[str] = {"math"}
        stmts: List[ast.stmt] = []

        if isinstance(ir, FinanceFetchSpec):
            call_node = ast.Call(
                func=ast.Name(id="fetch_stock_prices", ctx=ast.Load()),
                args=[ast.Constant(value=ir.symbol)],
                keywords=[
                    ast.keyword(arg="start_date", value=ast.Constant(value=ir.start_date)),
                    ast.keyword(arg="end_date", value=ast.Constant(value=ir.end_date)),
                ],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, FinanceMavSpec):
            call_node = ast.Call(
                func=ast.Name(id="moving_average", ctx=ast.Load()),
                args=[ast.Name(id=ir.series_var, ctx=ast.Load())],
                keywords=[
                    ast.keyword(arg="window", value=ast.Constant(value=ir.window)),
                    ast.keyword(arg="kind", value=ast.Constant(value=ir.kind)),
                ],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, FinanceRsiSpec):
            call_node = ast.Call(
                func=ast.Name(id="relative_strength_index", ctx=ast.Load()),
                args=[ast.Name(id=ir.series_var, ctx=ast.Load())],
                keywords=[ast.keyword(arg="period", value=ast.Constant(value=ir.period))],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, FinanceReturnsSpec):
            call_node = ast.Call(
                func=ast.Name(id="calculate_daily_returns", ctx=ast.Load()),
                args=[ast.Name(id=ir.series_var, ctx=ast.Load())],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, FinanceSharpeSpec):
            call_node = ast.Call(
                func=ast.Name(id="calculate_sharpe_ratio", ctx=ast.Load()),
                args=[ast.Name(id=ir.returns_var, ctx=ast.Load())],
                keywords=[ast.keyword(arg="risk_free_rate", value=ast.Constant(value=ir.risk_free_rate))],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        return imports, stmts
