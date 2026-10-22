"""Microeconomics Domain Runtime: Elasticity, Consumer/Producer Surplus, Deadweight loss, and Gini coefficient."""
from typing import Dict, Any, List

def micro_price_elasticity(q1: float, q2: float, p1: float, p2: float) -> float:
    """Calculates Midpoint Price Elasticity of Demand: (dQ / avg_Q) / (dP / avg_P)."""
    q1, q2 = float(q1), float(q2)
    p1, p2 = float(p1), float(p2)
    avg_q = (q1 + q2) / 2.0
    avg_p = (p1 + p2) / 2.0
    if avg_q == 0.0 or avg_p == 0.0 or (p2 - p1) == 0.0:
        return 0.0
    ped = ((q2 - q1) / avg_q) / ((p2 - p1) / avg_p)
    return round(abs(ped), 3)

def micro_surplus(demand_choke_price: float, supply_choke_price: float, eq_price: float, eq_quantity: float) -> Dict[str, float]:
    """Calculates Consumer Surplus, Producer Surplus, and Total Economic Welfare."""
    p_max = float(demand_choke_price)
    p_min = float(supply_choke_price)
    pe = float(eq_price)
    qe = float(eq_quantity)
    cs = 0.5 * (p_max - pe) * qe
    ps = 0.5 * (pe - p_min) * qe
    return {"consumer_surplus": round(cs, 2), "producer_surplus": round(ps, 2), "total_welfare": round(cs + ps, 2)}

def micro_deadweight_loss(tax_per_unit: float, quantity_reduction: float) -> float:
    """Calculates Deadweight Loss resulting from a market distortion DWL = 0.5 * T * dQ."""
    t = float(tax_per_unit)
    dq = float(quantity_reduction)
    return round(0.5 * t * dq, 2)

def micro_gini_coefficient(incomes: List[float]) -> float:
    """Calculates Gini coefficient (0.0 = perfect equality, 1.0 = total inequality)."""
    if not incomes:
        return 0.0
    sorted_inc = sorted(float(x) for x in incomes)
    n = len(sorted_inc)
    sum_inc = sum(sorted_inc)
    if sum_inc == 0:
        return 0.0
    diff_sum = sum(abs(xi - xj) for xi in sorted_inc for xj in sorted_inc)
    return round(diff_sum / (2.0 * n * sum_inc), 4)
