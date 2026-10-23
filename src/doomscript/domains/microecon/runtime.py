"""Microeconomics Domain Runtime: Price elasticity, welfare surplus, deadweight loss, Gini coefficient, Cournot duopoly, HHI, Cobb-Douglas optimization, Bertrand competition, monopoly optimum, and Nash equilibria."""
import math
from typing import Dict, Any, List
from doomscript.domains.base import DomainRuntime

def microecon_price_elasticity(q1: float, q2: float, p1: float, p2: float) -> float:
    """Calculates price elasticity of demand using Midpoint formula: (delta_Q / avg_Q) / (delta_P / avg_P)."""
    q1_v, q2_v, p1_v, p2_v = float(q1), float(q2), float(p1), float(p2)
    avg_q = (q1_v + q2_v) / 2.0
    avg_p = (p1_v + p2_v) / 2.0
    if avg_q == 0.0 or (p2_v - p1_v) == 0.0:
        return 0.0
    ped = ((q2_v - q1_v) / avg_q) / ((p2_v - p1_v) / avg_p)
    return round(ped, 3)

def microecon_surplus(p_max: float, p_min: float, market_price: float, quantity: float) -> Dict[str, float]:
    """Calculates Consumer Surplus and Producer Surplus under linear supply and demand."""
    p_max_v = float(p_max)
    p_min_v = float(p_min)
    p = float(market_price)
    q = float(quantity)
    cs = 0.5 * (p_max_v - p) * q if p_max_v >= p else 0.0
    ps = 0.5 * (p - p_min_v) * q if p >= p_min_v else 0.0
    return {"consumer_surplus": round(cs, 2), "producer_surplus": round(ps, 2), "total_welfare": round(cs + ps, 2)}

def microecon_deadweight_loss(tax_per_unit: float, quantity_reduction: float) -> float:
    """Calculates Harberger's Deadweight Loss triangle DWL = 0.5 * tax * delta_Q."""
    return round(0.5 * float(tax_per_unit) * float(quantity_reduction), 2)

def microecon_gini(incomes: List[float]) -> float:
    """Calculates Gini Coefficient (0.0 to 1.0) of economic inequality."""
    if not incomes:
        return 0.0
    sorted_inc = sorted([float(x) for x in incomes])
    n = len(sorted_inc)
    total = sum(sorted_inc)
    if total == 0:
        return 0.0
    cum_sum = 0
    gini_num = 0
    for i, val in enumerate(sorted_inc):
        cum_sum += val
        gini_num += (2 * (i + 1) - n - 1) * val
    return round(gini_num / (n * total), 4)

def microecon_cournot_duopoly(demand_intercept_a: float, demand_slope_b: float, marginal_cost: float) -> Dict[str, float]:
    """Calculates Cournot duopoly equilibrium outputs, market price, and profits."""
    a = float(demand_intercept_a)
    b = float(demand_slope_b)
    c = float(marginal_cost)
    if b <= 0 or a <= c:
        return {"q1": 0.0, "q2": 0.0, "price": 0.0, "profit": 0.0}
    q_firm = (a - c) / (3.0 * b)
    q_total = 2.0 * q_firm
    p = a - b * q_total
    profit = (p - c) * q_firm
    return {"q1": round(q_firm, 2), "q2": round(q_firm, 2), "price": round(p, 2), "profit_per_firm": round(profit, 2)}

def microecon_hhi_concentration(market_shares_pct: List[float]) -> Dict[str, Any]:
    """Calculates Herfindahl-Hirschman Index (HHI) for market concentration."""
    hhi = sum((float(s) ** 2) for s in market_shares_pct)
    classification = "Competitive" if hhi < 1500 else ("Moderately Concentrated" if hhi <= 2500 else "Highly Concentrated")
    return {"hhi": round(hhi, 1), "market_structure": classification}

def microecon_cobb_douglas_optimal(income: float, p_x: float, p_y: float, alpha: float, beta: float) -> Dict[str, float]:
    """Calculates optimal consumer bundle for Cobb-Douglas utility U = x^alpha * y^beta subject to budget."""
    inc = float(income)
    px = float(p_x)
    py = float(p_y)
    a = float(alpha)
    b = float(beta)
    denom = a + b
    if denom == 0 or px <= 0 or py <= 0:
        return {"x_optimal": 0.0, "y_optimal": 0.0, "utility": 0.0, "mrs": 0.0}
    x_opt = (a / denom) * (inc / px)
    y_opt = (b / denom) * (inc / py)
    u_val = (x_opt ** a) * (y_opt ** b)
    mrs = px / py
    return {
        "x_optimal": round(x_opt, 3),
        "y_optimal": round(y_opt, 3),
        "utility": round(u_val, 3),
        "mrs": round(mrs, 3)
    }

def microecon_bertrand_duopoly(demand_intercept_a: float, demand_slope_b: float, mc1: float, mc2: float) -> Dict[str, Any]:
    """Calculates Bertrand price competition equilibrium."""
    a = float(demand_intercept_a)
    b = float(demand_slope_b)
    c1 = float(mc1)
    c2 = float(mc2)
    if c1 == c2:
        p_eq = c1
        q_tot = max(0.0, (a - p_eq) / b) if b > 0 else 0.0
        return {"equilibrium_price": round(p_eq, 2), "q1": round(q_tot / 2.0, 2), "q2": round(q_tot / 2.0, 2), "profit1": 0.0, "profit2": 0.0}
    elif c1 < c2:
        p_eq = c2 - 0.01
        q_tot = max(0.0, (a - p_eq) / b) if b > 0 else 0.0
        profit1 = (p_eq - c1) * q_tot
        return {"equilibrium_price": round(p_eq, 2), "q1": round(q_tot, 2), "q2": 0.0, "profit1": round(profit1, 2), "profit2": 0.0}
    else:
        p_eq = c1 - 0.01
        q_tot = max(0.0, (a - p_eq) / b) if b > 0 else 0.0
        profit2 = (p_eq - c2) * q_tot
        return {"equilibrium_price": round(p_eq, 2), "q1": 0.0, "q2": round(q_tot, 2), "profit1": 0.0, "profit2": round(profit2, 2)}

def microecon_monopoly_optimum(demand_intercept_a: float, demand_slope_b: float, marginal_cost: float, fixed_cost: float = 0.0) -> Dict[str, float]:
    """Calculates profit-maximizing monopoly price, quantity, profit, and Lerner Index."""
    a = float(demand_intercept_a)
    b = float(demand_slope_b)
    mc = float(marginal_cost)
    fc = float(fixed_cost)
    if b <= 0 or a <= mc:
        return {"quantity": 0.0, "price": 0.0, "profit": 0.0, "lerner_index": 0.0, "deadweight_loss": 0.0}
    q_mono = (a - mc) / (2.0 * b)
    p_mono = a - b * q_mono
    profit = (p_mono - mc) * q_mono - fc
    lerner = (p_mono - mc) / p_mono if p_mono > 0 else 0.0
    # Competitive quantity where P = MC: q_comp = (a - mc) / b
    q_comp = (a - mc) / b
    dwl = 0.5 * (p_mono - mc) * (q_comp - q_mono)
    return {
        "monopoly_quantity": round(q_mono, 2),
        "monopoly_price": round(p_mono, 2),
        "profit": round(profit, 2),
        "lerner_index": round(lerner, 4),
        "deadweight_loss": round(dwl, 2)
    }

def microecon_cross_price_elasticity(q1_a: float, q2_a: float, p1_b: float, p2_b: float) -> Dict[str, Any]:
    """Calculates cross-price elasticity of demand between goods A and B."""
    q1 = float(q1_a)
    q2 = float(q2_a)
    p1 = float(p1_b)
    p2 = float(p2_b)
    avg_q = (q1 + q2) / 2.0
    avg_p = (p1 + p2) / 2.0
    if avg_q == 0.0 or (p2 - p1) == 0.0:
        return {"cross_elasticity": 0.0, "relationship": "Independent"}
    x_ped = ((q2 - q1) / avg_q) / ((p2 - p1) / avg_p)
    if x_ped > 0.05:
        rel = "Substitutes"
    elif x_ped < -0.05:
        rel = "Complements"
    else:
        rel = "Independent"
    return {"cross_elasticity": round(x_ped, 3), "relationship": rel}

def microecon_nash_equilibrium_2x2(payoff_row: List[List[float]], payoff_col: List[List[float]]) -> Dict[str, Any]:
    """Finds pure strategy Nash equilibria in a 2x2 normal form game."""
    equilibria = []
    # payoff_row[r][c], payoff_col[r][c] for r in {0, 1}, c in {0, 1}
    for r in range(2):
        for c in range(2):
            r_payoff = payoff_row[r][c]
            r_alt = payoff_row[1 - r][c]
            c_payoff = payoff_col[r][c]
            c_alt = payoff_col[r][1 - c]
            if r_payoff >= r_alt and c_payoff >= c_alt:
                equilibria.append({"row_strategy": r, "col_strategy": c, "payoffs": [r_payoff, c_payoff]})
    return {"pure_nash_equilibria": equilibria, "has_pure_equilibrium": len(equilibria) > 0}

def microecon_income_elasticity(q1: float, q2: float, inc1: float, inc2: float) -> Dict[str, Any]:
    """Calculates income elasticity of demand and classifies normal vs inferior good."""
    q1_v = float(q1)
    q2_v = float(q2)
    i1_v = float(inc1)
    i2_v = float(inc2)
    avg_q = (q1_v + q2_v) / 2.0
    avg_i = (i1_v + i2_v) / 2.0
    if avg_q == 0 or (i2_v - i1_v) == 0:
        return {"income_elasticity": 0.0, "good_type": "Normal"}
    ied = ((q2_v - q1_v) / avg_q) / ((i2_v - i1_v) / avg_i)
    if ied < 0:
        g_type = "Inferior Good"
    elif ied > 1.0:
        g_type = "Luxury / Superior Good"
    else:
        g_type = "Normal Necessity"
    return {"income_elasticity": round(ied, 3), "good_type": g_type}

class MicroeconRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

__all__ = [
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
