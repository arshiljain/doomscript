from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.petroleum.runtime import (
    PetroleumRuntime, petro_darcy_radial_flow, petro_archie_water_saturation,
    petro_api_gravity, petro_solution_gor, petro_standing_bubble_point,
    petro_sutton_pseudocritical, petro_arps_decline, petro_vogel_ipr,
    petro_dranchuk_z_factor, petro_material_balance_havlena_odeh
)
from doomscript.domains.petroleum.parser import PetroleumDomainParser
from doomscript.domains.petroleum.exporter import PetroleumASTExporter

class PetroleumDomain(DomainContract):
    name = "petroleum"
    aliases = ["petro", "oilgas", "reservoir"]
    description = "Petroleum & reservoir engineering: Darcy radial flow, Archie water saturation, API gravity, GOR, Standing bubble point, Arps decline, Vogel IPR, and gas Z-factor"
    parser = PetroleumDomainParser()
    runtime = PetroleumRuntime()
    exporter = PetroleumASTExporter()
    capabilities = ["darcy_flow", "archie_water_saturation", "api_gravity", "gor", "bubble_point", "pseudocritical", "arps_decline", "vogel_ipr", "z_factor"]
    verbs = [
        VerbSpec(pattern="calculate darcy radial flow perm {k:expr} pay {h:expr} pres {pr:expr} pwell {pw:expr} visc {mu:expr} re {re:expr} rw {rw:expr} skin {s:expr} into {target:ident}", description="Darcy radial flow"),
        VerbSpec(pattern="calculate archie water saturation phi {phi:expr} rt {rt:expr} rw {rw:expr} into {target:ident}", description="Archie water saturation"),
        VerbSpec(pattern="convert specific gravity {sg:expr} to api into {target:ident}", description="Specific gravity to API conversion"),
        VerbSpec(pattern="calculate gas oil ratio gas {g:expr} oil {o:expr} into {target:ident}", description="Gas oil ratio"),
        VerbSpec(pattern="calculate bubble point gor {gor:expr} gas_grav {gg:expr} api {api:expr} temp {t:expr} into {target:ident}", description="Standing bubble point"),
        VerbSpec(pattern="calculate pseudocritical gas grav {sg:expr} into {target:ident}", description="Sutton pseudocritical gas"),
        VerbSpec(pattern="forecast arps decline rate {qi:expr} nominal {d:expr} time {t:expr} b_factor {b:expr} into {target:ident}", description="Arps production decline"),
        VerbSpec(pattern="calculate vogel ipr qmax {qm:expr} pres {pr:expr} pwf {pwf:expr} into {target:ident}", description="Vogel inflow performance"),
        VerbSpec(pattern="calculate gas z factor ppr {ppr:expr} tpr {tpr:expr} into {target:ident}", description="Gas Z factor")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate darcy radial flow ") or
            s.startswith("calculate archie water saturation ") or
            s.startswith("convert specific gravity ") or
            s.startswith("calculate gas oil ratio ") or
            s.startswith("calculate bubble point ") or
            s.startswith("calculate pseudocritical gas ") or
            s.startswith("forecast arps decline ") or
            s.startswith("calculate vogel ipr ") or
            s.startswith("calculate gas z factor ")
        )

PETROLEUM_DOMAIN = PetroleumDomain()
get_domain_registry().register(PETROLEUM_DOMAIN)

__all__ = [
    "PETROLEUM_DOMAIN", "PetroleumDomain", "PetroleumRuntime",
    "petro_darcy_radial_flow", "petro_archie_water_saturation",
    "petro_api_gravity", "petro_solution_gor",
    "petro_standing_bubble_point", "petro_sutton_pseudocritical",
    "petro_arps_decline", "petro_vogel_ipr", "petro_dranchuk_z_factor",
    "petro_material_balance_havlena_odeh"
]
