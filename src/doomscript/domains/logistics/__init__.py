from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.logistics.runtime import (
    LogisticsRuntime, logistics_economic_order_quantity,
    logistics_reorder_point, logistics_safety_stock,
    logistics_newsvendor_optimal, logistics_bullwhip_effect,
    logistics_tsp_nearest_neighbor, logistics_facility_center_of_gravity,
    logistics_abc_classification, logistics_bin_packing_1d
)
from doomscript.domains.logistics.parser import LogisticsDomainParser
from doomscript.domains.logistics.exporter import LogisticsASTExporter

class LogisticsDomain(DomainContract):
    name = "logistics"
    aliases = ["supply_chain", "inventory", "warehouse"]
    description = "Supply chain & logistics: EOQ, ROP, safety stock, Newsvendor model, bullwhip effect, TSP, COG, and ABC analysis"
    parser = LogisticsDomainParser()
    runtime = LogisticsRuntime()
    exporter = LogisticsASTExporter()
    capabilities = ["eoq", "reorder_point", "safety_stock", "newsvendor", "bullwhip_effect", "tsp_solver", "center_of_gravity", "abc_analysis", "bin_packing"]
    verbs = [
        VerbSpec(pattern="calculate economic order quantity for demand {d:expr} order cost {s:expr} holding cost {h:expr} into {target:ident}", description="EOQ formula"),
        VerbSpec(pattern="calculate reorder point for lead time {lt:expr} daily demand {d:expr} into {target:ident}", description="Reorder point"),
        VerbSpec(pattern="solve tsp nearest neighbor for matrix {m:expr} into {target:ident}", description="TSP solver"),
        VerbSpec(pattern="calculate safety stock for z {z:expr} std {std:expr} lead time {lt:expr} into {target:ident}", description="Safety stock"),
        VerbSpec(pattern="calculate bullwhip effect for orders {o:expr} demand {d:expr} into {target:ident}", description="Bullwhip effect")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate economic order quantity ") or
            s.startswith("calculate reorder point ") or
            s.startswith("calculate safety stock ") or
            s.startswith("solve tsp nearest neighbor ") or
            s.startswith("calculate newsvendor ") or
            s.startswith("calculate bullwhip effect ")
        )

LOGISTICS_DOMAIN = LogisticsDomain()
get_domain_registry().register(LOGISTICS_DOMAIN)

__all__ = [
    "LogisticsDomain", "LOGISTICS_DOMAIN", "LogisticsRuntime",
    "logistics_economic_order_quantity", "logistics_reorder_point",
    "logistics_safety_stock", "logistics_newsvendor_optimal",
    "logistics_bullwhip_effect", "logistics_tsp_nearest_neighbor",
    "logistics_facility_center_of_gravity", "logistics_abc_classification",
    "logistics_bin_packing_1d"
]
