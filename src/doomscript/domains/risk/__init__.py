from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.risk.runtime import (
    risk_value_at_risk_historical, risk_conditional_var,
    risk_max_drawdown, risk_sharpe_ratio, risk_sortino_ratio
)
from doomscript.domains.risk.parser import RiskDomainParser
from doomscript.domains.risk.exporter import RiskASTExporter

class RiskRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class RiskDomain(DomainContract):
    name = "risk"
    aliases = ["var", "portfolio_risk", "risk_analytics"]
    description = "Quantitative financial risk: VaR, CVaR, Maximum Drawdown, and Sharpe/Sortino ratios"
    parser = RiskDomainParser()
    runtime = RiskRuntime()
    exporter = RiskASTExporter()
    capabilities = ["value_at_risk", "cvar", "max_drawdown", "sharpe_ratio", "sortino_ratio"]
    verbs = [
        VerbSpec(pattern="calculate historical var for returns {ret:expr} confidence {conf:expr} into {target:ident}", description="VaR"),
        VerbSpec(pattern="calculate max drawdown for prices {prices:expr} into {target:ident}", description="Max Drawdown")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate historical var ") or s.startswith("calculate cvar ") or s.startswith("calculate max drawdown ") or s.startswith("calculate sharpe ratio ") or s.startswith("calculate sortino ratio ")

RISK_DOMAIN = RiskDomain()
get_domain_registry().register(RISK_DOMAIN)

__all__ = [
    "RiskDomain", "RISK_DOMAIN", "RiskRuntime",
    "risk_value_at_risk_historical", "risk_conditional_var",
    "risk_max_drawdown", "risk_sharpe_ratio", "risk_sortino_ratio"
]
