from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.petroleum.runtime import (
    petro_darcy_radial_flow, petro_archie_water_saturation,
    petro_api_gravity, petro_solution_gor,
    petro_standing_bubble_point, petro_sutton_pseudocritical
)
from doomscript.domains.petroleum.parser import PetroleumDomainParser
from doomscript.domains.petroleum.exporter import PetroleumASTExporter

class PetroleumRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class PetroleumDomain(DomainContract):
    name = "petroleum"
    aliases = ["petro", "oilgas", "reservoir"]
    description = "Petroleum and reservoir engineering: Darcy flow, Archie saturation, API gravity, GOR, Standing bubble point, and Sutton gas properties"
    parser = PetroleumDomainParser()
    runtime = PetroleumRuntime()
    exporter = PetroleumASTExporter()
    capabilities = ["darcy_radial_flow", "archie_water_saturation", "api_gravity", "solution_gor", "standing_bubble_point", "sutton_pseudocritical"]
    verbs = [
        VerbSpec(pattern="calculate darcy radial flow perm {k:expr} pay {h:expr} pres {pr:expr} pwell {pw:expr} visc {mu:expr} re {re:expr} rw {rw:expr} skin {s:expr} into {target:ident}", description="Darcy radial flow rate"),
        VerbSpec(pattern="calculate archie water saturation phi {phi:expr} rt {rt:expr} rw {rw:expr} into {target:ident}", description="Archie water saturation"),
        VerbSpec(pattern="convert specific gravity {sg:expr} to api into {target:ident}", description="Specific gravity to API"),
        VerbSpec(pattern="calculate gas oil ratio gas {g:expr} oil {o:expr} into {target:ident}", description="Gas-Oil Ratio"),
        VerbSpec(pattern="calculate bubble point gor {gor:expr} gas_grav {gg:expr} api {api:expr} temp {t:expr} into {target:ident}", description="Standing bubble point pressure"),
        VerbSpec(pattern="calculate pseudocritical gas grav {gg:expr} into {target:ident}", description="Sutton pseudocritical gas properties")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate darcy radial flow ") or s.startswith("calculate archie water saturation ") or s.startswith("convert specific gravity ") or s.startswith("calculate gas oil ratio ") or s.startswith("calculate bubble point ") or s.startswith("calculate pseudocritical gas ")

PETROLEUM_DOMAIN = PetroleumDomain()
get_domain_registry().register(PETROLEUM_DOMAIN)

__all__ = [
    "PetroleumDomain", "PETROLEUM_DOMAIN", "PetroleumRuntime",
    "petro_darcy_radial_flow", "petro_archie_water_saturation",
    "petro_api_gravity", "petro_solution_gor",
    "petro_standing_bubble_point", "petro_sutton_pseudocritical"
]
