"""Agronomy Domain for DoomScript: Soil physics, crop modeling, irrigation, fertility, and soil conservation."""
from typing import Any, Dict
from doomscript.domains.base import DomainContract, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.agronomy.parser import AgronomyDomainParser
from doomscript.domains.agronomy.runtime import (
    AgronomyRuntime,
    agronomy_crop_water_requirement,
    agronomy_growing_degree_days,
    agronomy_fertilizer_rate,
    agronomy_cation_exchange_capacity,
    agronomy_soil_porosity,
    agronomy_universal_soil_loss_equation,
    agronomy_available_water_capacity,
    agronomy_nitrogen_mineralization_balance,
    agronomy_irrigation_depth_schedule,
    agronomy_leaf_area_index,
    agronomy_sodium_adsorption_ratio
)
from doomscript.domains.agronomy.exporter import AgronomyASTExporter

class AgronomyDomain(DomainContract):
    name = "agronomy"
    aliases = ["agri", "crop_science", "soil_science"]
    description = "Soil physics, crop water modeling, irrigation, fertility, and soil conservation."
    parser = AgronomyDomainParser()
    runtime = AgronomyRuntime()
    exporter = AgronomyASTExporter()
    capabilities = [
        "crop_water_requirement",
        "growing_degree_days",
        "fertilizer_rate",
        "cation_exchange_capacity",
        "soil_porosity",
        "usle_erosion",
        "available_water_capacity",
        "nitrogen_balance",
        "irrigation_schedule",
        "leaf_area_index",
        "sodium_adsorption_ratio"
    ]
    verbs = [
        VerbSpec(pattern="calculate crop water requirement et0 {et0:expr} kc {kc:expr} into {target:ident}", description="Calculates crop water requirement ETc"),
        VerbSpec(pattern="calculate growing degree days tmax {tmax:expr} tmin {tmin:expr} into {target:ident}", description="Calculates Growing Degree Days GDD"),
        VerbSpec(pattern="calculate fertilizer rate nutrient {n:expr} percent {p:expr} into {target:ident}", description="Calculates bulk fertilizer application rate"),
        VerbSpec(pattern="calculate cation exchange ca {ca:expr} mg {mg:expr} k {k:expr} na {na:expr} into {target:ident}", description="Calculates CEC and base saturation"),
        VerbSpec(pattern="calculate soil porosity bulk {pb:expr} into {target:ident}", description="Calculates soil total porosity fraction"),
        VerbSpec(pattern="calculate usle erosion r {r:expr} k {k:expr} ls {ls:expr} c {c:expr} p {p:expr} into {target:ident}", description="Calculates annual USLE soil erosion loss"),
        VerbSpec(pattern="calculate available water capacity fc {fc:expr} pwp {pwp:expr} depth {d:expr} into {target:ident}", description="Calculates plant available water capacity"),
        VerbSpec(pattern="calculate nitrogen balance om {om:expr} demand {dem:expr} into {target:ident}", description="Estimates soil N mineralization and fertilizer deficit"),
        VerbSpec(pattern="calculate irrigation schedule deficit {def:expr} efficiency {eff:expr} rate {r:expr} into {target:ident}", description="Calculates gross irrigation depth and runtime"),
        VerbSpec(pattern="calculate leaf area index foliage {f:expr} ground {g:expr} into {target:ident}", description="Calculates Leaf Area Index and light interception"),
        VerbSpec(pattern="calculate sar na {na:expr} ca {ca:expr} mg {mg:expr} into {target:ident}", description="Calculates Sodium Adsorption Ratio SAR")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate crop water requirement ") or
            s.startswith("calculate growing degree days ") or
            s.startswith("calculate fertilizer rate ") or
            s.startswith("calculate cation exchange ") or
            s.startswith("calculate soil porosity ") or
            s.startswith("calculate usle erosion ") or
            s.startswith("calculate available water capacity ") or
            s.startswith("calculate nitrogen balance ") or
            s.startswith("calculate irrigation schedule ") or
            s.startswith("calculate leaf area index ") or
            s.startswith("calculate sar ")
        )

AGRONOMY_DOMAIN = AgronomyDomain()
get_domain_registry().register(AGRONOMY_DOMAIN)

__all__ = [
    "AGRONOMY_DOMAIN",
    "AgronomyDomain",
    "AgronomyRuntime",
    "agronomy_crop_water_requirement",
    "agronomy_growing_degree_days",
    "agronomy_fertilizer_rate",
    "agronomy_cation_exchange_capacity",
    "agronomy_soil_porosity",
    "agronomy_universal_soil_loss_equation",
    "agronomy_available_water_capacity",
    "agronomy_nitrogen_mineralization_balance",
    "agronomy_irrigation_depth_schedule",
    "agronomy_leaf_area_index",
    "agronomy_sodium_adsorption_ratio"
]
