"""Logistics Domain Runtime: Supply chain optimization, inventory management, vehicle routing, and facility location."""
import math
from typing import List, Dict, Any, Tuple, Optional
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED INVENTORY & ROUTING ALGORITHMS
# ============================================================================

def logistics_economic_order_quantity(demand: float, order_cost: float, holding_cost: float) -> float:
    """Calculates classic Wilson Economic Order Quantity: EOQ = sqrt(2 * D * S / H)."""
    d, s, h = float(demand), float(order_cost), float(holding_cost)
    if h <= 0.0 or d <= 0.0:
        return 0.0
    return round(math.sqrt((2.0 * d * s) / h), 2)

def logistics_reorder_point(lead_time_days: float, daily_demand: float, safety_stock: float = 0.0) -> float:
    """Calculates inventory Reorder Point (ROP): ROP = d * L + SS."""
    return round(float(lead_time_days) * float(daily_demand) + float(safety_stock), 2)

def logistics_safety_stock(z_score: float, std_dev_demand: float, lead_time: float) -> float:
    """Calculates safety stock under normally distributed demand during lead time."""
    ss = float(z_score) * float(std_dev_demand) * math.sqrt(max(0.0, float(lead_time)))
    return round(ss, 2)

def logistics_newsvendor_optimal(unit_cost: float, retail_price: float, salvage_value: float, mean_demand: float, std_demand: float) -> Dict[str, float]:
    """Calculates optimal Newsvendor order quantity and critical fractile."""
    c = float(unit_cost)
    p = float(retail_price)
    s = float(salvage_value)
    cu = p - c # Cost of underage
    co = c - s # Cost of overage
    if (cu + co) <= 0:
        return {"critical_fractile": 0.0, "optimal_quantity": float(mean_demand)}
    crit_ratio = cu / (cu + co)
    # Approx z from critical ratio
    z = (crit_ratio - 0.5) * 3.0
    q_opt = float(mean_demand) + z * float(std_demand)
    return {
        "critical_fractile": round(crit_ratio, 4),
        "optimal_quantity": round(max(0.0, q_opt), 2)
    }

def logistics_bullwhip_effect(orders_series: List[float], demand_series: List[float]) -> float:
    """Calculates Bullwhip Effect ratio: (Var(Orders)/Mean(Orders)) / (Var(Demand)/Mean(Demand))."""
    if len(orders_series) < 2 or len(demand_series) < 2:
        return 1.0
    mean_o = sum(orders_series) / len(orders_series)
    mean_d = sum(demand_series) / len(demand_series)
    var_o = sum((x - mean_o)**2 for x in orders_series) / (len(orders_series) - 1)
    var_d = sum((x - mean_d)**2 for x in demand_series) / (len(demand_series) - 1)
    if var_d == 0 or mean_d == 0 or mean_o == 0:
        return 1.0
    cv_o = var_o / mean_o
    cv_d = var_d / mean_d
    return round(cv_o / cv_d, 4)

def logistics_tsp_nearest_neighbor(distance_matrix: List[List[float]]) -> Dict[str, Any]:
    """Greedy Nearest Neighbor Traveling Salesperson Problem (TSP) solver."""
    n = len(distance_matrix)
    if n == 0:
        return {"tour": [], "total_distance": 0.0}
    visited = [False] * n
    curr = 0
    visited[0] = True
    tour = [0]
    total_dist = 0.0
    for _ in range(n - 1):
        next_city = -1
        min_dist = float("inf")
        for j in range(n):
            if not visited[j] and distance_matrix[curr][j] < min_dist:
                min_dist = distance_matrix[curr][j]
                next_city = j
        if next_city != -1:
            visited[next_city] = True
            tour.append(next_city)
            total_dist += min_dist
            curr = next_city
    total_dist += distance_matrix[curr][0]
    tour.append(0)
    return {"tour": tour, "total_distance": round(total_dist, 2)}

# ============================================================================
# 2. ADVANCED LOGISTICS (CVRP, FACILITY LOCATION, ABC INVENTORY)
# ============================================================================

def logistics_facility_center_of_gravity(locations: List[Dict[str, float]]) -> Dict[str, float]:
    """Finds optimal single facility coordinates using weighted Center-of-Gravity method."""
    total_weight = sum(loc.get("weight", 1.0) for loc in locations)
    if total_weight <= 0:
        return {"x": 0.0, "y": 0.0}
    weighted_x = sum(loc.get("x", 0.0) * loc.get("weight", 1.0) for loc in locations)
    weighted_y = sum(loc.get("y", 0.0) * loc.get("weight", 1.0) for loc in locations)
    return {
        "x": round(weighted_x / total_weight, 4),
        "y": round(weighted_y / total_weight, 4)
    }

def logistics_abc_classification(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Performs Pareto ABC inventory classification by annual expenditure volume."""
    evaluated = []
    for it in items:
        vol = float(it.get("annual_demand", 0)) * float(it.get("unit_cost", 0))
        evaluated.append({**it, "annual_dollar_volume": vol})
    evaluated.sort(key=lambda x: x["annual_dollar_volume"], reverse=True)
    total_spend = sum(x["annual_dollar_volume"] for x in evaluated) or 1.0
    cum_pct = 0.0
    for item in evaluated:
        cum_pct += (item["annual_dollar_volume"] / total_spend) * 100.0
        item["cumulative_pct"] = round(cum_pct, 2)
        if cum_pct <= 80.0:
            item["category"] = "A"
        elif cum_pct <= 95.0:
            item["category"] = "B"
        else:
            item["category"] = "C"
    return evaluated

def logistics_bin_packing_1d(item_weights: List[float], bin_capacity: float) -> Dict[str, Any]:
    """First Fit Decreasing (FFD) 1D Bin Packing algorithm."""
    sorted_weights = sorted(item_weights, reverse=True)
    bins: List[List[float]] = []
    for w in sorted_weights:
        placed = False
        for b in bins:
            if sum(b) + w <= bin_capacity:
                b.append(w)
                placed = True
                break
        if not placed:
            bins.append([w])
    return {
        "total_bins": len(bins),
        "bins": bins,
        "efficiency_pct": round((sum(item_weights) / (len(bins) * bin_capacity)) * 100.0, 2) if bins else 0.0
    }

# ============================================================================
# 3. DOMAIN RUNTIME
# ============================================================================

class LogisticsRuntime(DomainRuntime):
    """Unified runtime bridge for the Logistics computational domain."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def eoq(self, d: float, s: float, h: float) -> float:
        return logistics_economic_order_quantity(d, s, h)
    def rop(self, lt: float, d: float, ss: float = 0.0) -> float:
        return logistics_reorder_point(lt, d, ss)
    def safety_stock(self, z: float, std: float, lt: float) -> float:
        return logistics_safety_stock(z, std, lt)
    def newsvendor(self, c: float, p: float, s: float, mean: float, std: float) -> Dict[str, float]:
        return logistics_newsvendor_optimal(c, p, s, mean, std)
    def bullwhip(self, orders: List[float], demand: List[float]) -> float:
        return logistics_bullwhip_effect(orders, demand)
    def tsp(self, matrix: List[List[float]]) -> Dict[str, Any]:
        return logistics_tsp_nearest_neighbor(matrix)
    def cog(self, locations: List[Dict[str, float]]) -> Dict[str, float]:
        return logistics_facility_center_of_gravity(locations)
    def abc(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return logistics_abc_classification(items)
    def bin_packing(self, weights: List[float], cap: float) -> Dict[str, Any]:
        return logistics_bin_packing_1d(weights, cap)
