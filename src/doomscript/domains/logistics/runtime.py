"""Logistics & Operations Research Runtime: EOQ, Safety Stock, Reorder Point, and Nearest Neighbor TSP."""
import math
from typing import List, Dict, Any

def logistics_eoq(annual_demand: float, order_cost: float, holding_cost_per_unit: float) -> float:
    """Calculates Economic Order Quantity EOQ = sqrt(2 * D * S / H)."""
    d = float(annual_demand)
    s = float(order_cost)
    h = float(holding_cost_per_unit)
    if h <= 0.0 or d <= 0.0:
        return 0.0
    return round(math.sqrt((2.0 * d * s) / h), 2)

def logistics_reorder_point(lead_time_days: float, daily_demand: float, safety_stock: float = 0.0) -> float:
    """Calculates Reorder Point ROP = (Lead Time * Daily Demand) + Safety Stock."""
    lt = float(lead_time_days)
    d = float(daily_demand)
    ss = float(safety_stock)
    return round(lt * d + ss, 2)

def logistics_safety_stock(z_service_factor: float, std_demand: float, lead_time_days: float) -> float:
    """Calculates Safety Stock SS = Z * sigma_d * sqrt(Lead Time)."""
    z = float(z_service_factor)
    sigma = float(std_demand)
    lt = float(lead_time_days)
    return round(z * sigma * math.sqrt(lt), 2)

def logistics_tsp_nearest_neighbor(distance_matrix: List[List[float]]) -> Dict[str, Any]:
    """Solves TSP using nearest neighbor greedy heuristic starting at node 0."""
    n = len(distance_matrix)
    if n == 0:
        return {"tour": [], "total_distance": 0.0}
    visited = [False] * n
    tour = [0]
    visited[0] = True
    total_dist = 0.0
    curr = 0
    for _ in range(n - 1):
        next_node = None
        min_d = float('inf')
        for neighbor in range(n):
            if not visited[neighbor] and distance_matrix[curr][neighbor] < min_d:
                min_d = distance_matrix[curr][neighbor]
                next_node = neighbor
        if next_node is not None:
            visited[next_node] = True
            tour.append(next_node)
            total_dist += min_d
            curr = next_node
    # Return to start
    total_dist += distance_matrix[curr][0]
    tour.append(0)
    return {"tour": tour, "total_distance": round(total_dist, 2)}
