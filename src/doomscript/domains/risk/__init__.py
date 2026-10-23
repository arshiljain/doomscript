from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.risk.runtime import (
    RiskRuntime, risk_value_at_risk_historical, risk_conditional_var,
    risk_max_drawdown, risk_sharpe_ratio, risk_sortino_ratio,
    risk_calmar_ratio, risk_portfolio_volatility, risk_altman_z_score,
    risk_var_cornish_fisher, risk_merton_distance_to_default
)
from doomscript.domains.risk.parser import RiskDomainParser
from doomscript.domains.risk.exporter import RiskASTExporter

class RiskDomain(DomainContract):
    name = "risk"
    aliases = ["var", "portfolio_risk", "risk_analytics"]
    description = "Quantitative financial risk: VaR, CVaR, Max Drawdown, Sharpe/Sortino/Calmar ratios, Altman Z, and Merton default"
    parser = RiskDomainParser()
    runtime = RiskRuntime()
    exporter = RiskASTExporter()
    capabilities = [
        "value_at_risk", "cvar", "max_drawdown", "sharpe_ratio", "sortino_ratio",
        "calmar_ratio", "portfolio_volatility", "altman_z", "cornish_fisher", "merton_default"
    ]
    verbs = [
        VerbSpec(pattern="calculate historical var for returns {ret:expr} confidence {conf:expr} into {target:ident}", description="VaR"),
        VerbSpec(pattern="calculate max drawdown for prices {prices:expr} into {target:ident}", description="Max Drawdown"),
        VerbSpec(pattern="calculate portfolio volatility weights {w:expr} covariance {cov:expr} into {target:ident}", description="Portfolio Volatility"),
        VerbSpec(pattern="calculate sharpe ratio for returns {ret:expr} risk free {rf:expr} into {target:ident}", description="Sharpe ratio")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate historical var ") or
            s.startswith("calculate cvar ") or
            s.startswith("calculate max drawdown ") or
            s.startswith("calculate sharpe ratio ") or
            s.startswith("calculate sortino ratio ") or
            s.startswith("calculate calmar ratio ") or
            s.startswith("calculate portfolio volatility ")
        )

RISK_DOMAIN = RiskDomain()
get_domain_registry().register(RISK_DOMAIN)

__all__ = [
    "RiskDomain", "RISK_DOMAIN", "RiskRuntime",
    "risk_value_at_risk_historical", "risk_conditional_var",
    "risk_max_drawdown", "risk_sharpe_ratio", "risk_sortino_ratio",
    "risk_calmar_ratio", "risk_portfolio_volatility", "risk_altman_z_score",
    "risk_var_cornish_fisher", "risk_merton_distance_to_default"
]
