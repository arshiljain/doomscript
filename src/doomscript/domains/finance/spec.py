"""Declarative specifications and Intermediate Representation for Quantitative Finance domain."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from doomscript.domains.base import DomainIR


@dataclass
class FinanceFetchSpec(DomainIR):
    symbol: str
    target_var: str
    start_date: str = "2024-01-01"
    end_date: str = "2024-12-31"

    def validate(self) -> List[str]:
        errors = []
        if not self.symbol:
            errors.append("FinanceFetchSpec requires a stock symbol")
        if not self.target_var:
            errors.append("FinanceFetchSpec requires a target variable")
        return errors


@dataclass
class FinanceMavSpec(DomainIR):
    series_var: str
    window: int
    target_var: str
    kind: str = "sma"

    def validate(self) -> List[str]:
        errors = []
        if self.window <= 0:
            errors.append("Moving average window must be greater than zero")
        return errors


@dataclass
class FinanceRsiSpec(DomainIR):
    series_var: str
    target_var: str
    period: int = 14

    def validate(self) -> List[str]:
        errors = []
        if self.period <= 0:
            errors.append("RSI period must be greater than zero")
        return errors


@dataclass
class FinanceReturnsSpec(DomainIR):
    series_var: str
    target_var: str

    def validate(self) -> List[str]:
        return []


@dataclass
class FinanceSharpeSpec(DomainIR):
    returns_var: str
    target_var: str
    risk_free_rate: float = 0.04

    def validate(self) -> List[str]:
        return []


@dataclass
class FinanceBacktestSpec(DomainIR):
    prices_var: str
    target_var: str
    condition: str = ""

    def validate(self) -> List[str]:
        return []


@dataclass
class FinancePortfolioIR(DomainIR):
    name: str = "portfolio"
    target: str = "portfolio"
    total_value: float = 10000.0
    holdings: Dict[str, float] = field(default_factory=dict)

    def validate(self) -> List[str]:
        return []
