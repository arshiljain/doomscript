"""Microeconomics Domain for DoomScript."""
from typing import Any, Dict
from doomscript.domains.base import DomainContract, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.microecon.runtime import (
    MicroeconRuntime,
    microecon_price_elasticity,
    microecon_surplus,
    microecon_deadweight_loss,
    microecon_gini,
    microecon_cournot_duopoly,
    microecon_hhi_concentration,
    microecon_cobb_douglas_optimal,
    microecon_bertrand_duopoly,
    microecon_monopoly_optimum,
    microecon_cross_price_elasticity,
    microecon_nash_equilibrium_2x2,
    microecon_income_elasticity
)
from doomscript.domains.microecon.parser import MicroeconDomainParser
from doomscript.domains.microecon.exporter import MicroeconASTExporter

class MicroeconDomain(DomainContract):
    name = "microecon"
    aliases = ["microeconomics", "supply_demand", "welfare_economics"]
    description = "Microeconomics: Price elasticity, welfare surplus, deadweight loss, Gini coefficient, Cournot & Bertrand duopolies, Cobb-Douglas optimization, and game theory"
    parser = MicroeconDomainParser()
    runtime = MicroeconRuntime()
    exporter = MicroeconASTExporter()
    capabilities = [
        "price_elasticity",
        "surplus",
        "deadweight_loss",
        "gini",
        "cournot_duopoly",
        "hhi",
        "cobb_douglas_optimal",
        "bertrand_duopoly",
        "monopoly_optimum",
        "cross_price_elasticity",
        "nash_equilibrium",
        "income_elasticity"
    ]
    verbs = [
        VerbSpec(pattern="calculate price elasticity for q1 {q1:expr} q2 {q2:expr} p1 {p1:expr} p2 {p2:expr} into {target:ident}", description="Price elasticity of demand"),
        VerbSpec(pattern="calculate surplus for p_max {p_max:expr} p_min {p_min:expr} price {p:expr} quantity {q:expr} into {target:ident}", description="Consumer and producer surplus"),
        VerbSpec(pattern="calculate deadweight loss for tax {tax:expr} quantity reduction {dq:expr} into {target:ident}", description="Harberger deadweight loss triangle"),
        VerbSpec(pattern="calculate gini coefficient for incomes {inc:expr} into {target:ident}", description="Gini inequality coefficient"),
        VerbSpec(pattern="calculate cournot duopoly demand intercept {a:expr} slope {b:expr} marginal cost {c:expr} into {target:ident}", description="Cournot duopoly equilibrium"),
        VerbSpec(pattern="calculate hhi for shares {shares:expr} into {target:ident}", description="Herfindahl-Hirschman market concentration index"),
        VerbSpec(pattern="calculate cobb douglas optimal income {inc:expr} px {px:expr} py {py:expr} alpha {a:expr} beta {b:expr} into {target:ident}", description="Utility-maximizing consumption bundle"),
        VerbSpec(pattern="calculate bertrand duopoly demand intercept {a:expr} slope {b:expr} mc1 {c1:expr} mc2 {c2:expr} into {target:ident}", description="Bertrand price competition equilibrium"),
        VerbSpec(pattern="calculate monopoly optimum demand intercept {a:expr} slope {b:expr} marginal cost {mc:expr} into {target:ident}", description="Monopoly profit-maximizing price and quantity"),
        VerbSpec(pattern="calculate cross elasticity q1 {q1:expr} q2 {q2:expr} p1 {p1:expr} p2 {p2:expr} into {target:ident}", description="Cross-price elasticity of demand"),
        VerbSpec(pattern="find nash equilibrium row {row:expr} col {col:expr} into {target:ident}", description="Pure strategy Nash equilibria in 2x2 game"),
        VerbSpec(pattern="calculate income elasticity q1 {q1:expr} q2 {q2:expr} inc1 {i1:expr} inc2 {i2:expr} into {target:ident}", description="Income elasticity of demand")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate price elasticity ") or
            s.startswith("calculate surplus ") or
            s.startswith("calculate deadweight loss ") or
            s.startswith("calculate gini coefficient ") or
            s.startswith("calculate cournot duopoly ") or
            s.startswith("calculate hhi ") or
            s.startswith("calculate cobb douglas optimal ") or
            s.startswith("calculate bertrand duopoly ") or
            s.startswith("calculate monopoly optimum ") or
            s.startswith("calculate cross elasticity ") or
            s.startswith("find nash equilibrium ") or
            s.startswith("calculate income elasticity ")
        )

MICROECON_DOMAIN = MicroeconDomain()
get_domain_registry().register(MICROECON_DOMAIN)

__all__ = [
    "MICROECON_DOMAIN",
    "MicroeconDomain",
    "MicroeconRuntime",
    "microecon_price_elasticity",
    "microecon_surplus",
    "microecon_deadweight_loss",
    "microecon_gini",
    "microecon_cournot_duopoly",
    "microecon_hhi_concentration",
    "microecon_cobb_douglas_optimal",
    "microecon_bertrand_duopoly",
    "microecon_monopoly_optimum",
    "microecon_cross_price_elasticity",
    "microecon_nash_equilibrium_2x2",
    "microecon_income_elasticity"
]
