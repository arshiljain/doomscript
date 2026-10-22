"""Microeconomics Domain Runtime: Price elasticity, Consumer/Producer surplus, Cournot duopoly, and HHI market concentration."""
import math
from typing import Dict, Any, List

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
    # q1 = q2 = (a - c) / (3 * b)
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
