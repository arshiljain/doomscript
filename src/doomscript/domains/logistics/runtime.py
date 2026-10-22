"""Logistics & Supply Chain Runtime: Wilson EOQ, Reorder Point, Safety Stock, Newsvendor, Bullwhip effect, and TSP heuristics."""
import math
from typing import Dict, Any, List

def logistics_economic_order_quantity(demand: float, order_cost: float, holding_cost: float) -> float:
    """Calculates Wilson Economic Order Quantity EOQ = sqrt((2 * D * S) / H)."""
    d = float(demand)
    s = float(order_cost)
    h = float(holding_cost)
    if h <= 0.0 or d <= 0.0 or s <= 0.0:
        return 0.0
    return round(math.sqrt((2.0 * d * s) / h), 2)

def logistics_reorder_point(lead_time_days: float, daily_demand: float, safety_stock: float = 0.0) -> float:
    """Calculates Reorder Point ROP = (Lead Time * Daily Demand) + Safety Stock."""
    return round(float(lead_time_days) * float(daily_demand) + float(safety_stock), 2)

def logistics_safety_stock(z_score: float, std_dev_demand: float, lead_time: float) -> float:
    """Calculates Safety Stock SS = Z * sigma_d * sqrt(L)."""
    return round(float(z_score) * float(std_dev_demand) * math.sqrt(float(lead_time)), 2)

def logistics_newsvendor_optimal(unit_cost: float, retail_price: float, salvage_value: float, mean_demand: float, std_demand: float) -> Dict[str, float]:
    """Calculates optimal stocking quantity Q* under Newsvendor model critical fractile."""
    p = float(retail_price)
    c = float(unit_cost)
    s = float(salvage_value)
    cu = p - c # Underage cost
    co = c - s # Overage cost
    if (cu + co) <= 0:
        return {"critical_fractile": 0.0, "optimal_quantity": float(mean_demand)}
    cf = cu / (cu + co)
    # Norminv approximation for critical fractile z
    z = (cf - 0.5) * 2.5 # Simple linear approximation
    q_star = max(0.0, float(mean_demand) + z * float(std_demand))
    return {"critical_fractile": round(cf, 4), "optimal_quantity": round(q_star, 1)}

def logistics_bullwhip_effect(orders_series: List[float], demand_series: List[float]) -> float:
    """Calculates the Bullwhip Effect measure (Var(Orders)/Mean(Orders)) / (Var(Demand)/Mean(Demand))."""
    if len(orders_series) < 2 or len(demand_series) < 2:
        return 1.0
    m_o = sum(orders_series) / len(orders_series)
    m_d = sum(demand_series) / len(demand_series)
    if m_o <= 0 or m_d <= 0:
        return 1.0
    v_o = sum((x - m_o) ** 2 for x in orders_series) / (len(orders_series) - 1)
    v_d = sum((x - m_d) ** 2 for x in demand_series) / (len(demand_series) - 1)
    if v_d <= 0:
        return 1.0
    ratio = (v_o / m_o) / (v_d / m_d)
    return round(ratio, 3)

def logistics_tsp_nearest_neighbor(distance_matrix: List[List[float]]) -> Dict[str, Any]:
    """Greedy Nearest Neighbor heuristic for Traveling Salesperson Problem."""
    n = len(distance_matrix)
    if n <= 1:
        return {"tour": [0], "total_distance": 0.0}
    visited = {0}
    tour = [0]
    total_dist = 0.0
    curr = 0
    while len(visited) < n:
        best_next = None
        best_dist = float("inf")
        for nxt in range(n):
            if nxt not in visited:
                d = float(distance_matrix[curr][nxt])
                if d < best_dist:
                    best_dist = d
                    best_next = nxt
        if best_next is not None:
            visited.add(best_next)
            tour.append(best_next)
            total_dist += best_dist
            curr = best_next
    total_dist += float(distance_matrix[curr][0])
    tour.append(0)
    return {"tour": tour, "total_distance": round(total_dist, 2)}
