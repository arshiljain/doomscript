from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.climate.runtime import (
    climate_dew_point, climate_heat_index, climate_barometric_pressure,
    climate_co2_equivalent
)
from doomscript.domains.climate.parser import ClimateDomainParser
from doomscript.domains.climate.exporter import ClimateASTExporter

class ClimateRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class ClimateDomain(DomainContract):
    name = "climate"
    aliases = ["meteorology", "weather", "carbon"]
    description = "Climate science, meteorology, dew point, heat index, and carbon accounting"
    parser = ClimateDomainParser()
    runtime = ClimateRuntime()
    exporter = ClimateASTExporter()
    capabilities = ["dew_point", "heat_index", "barometric_pressure", "co2_equivalent"]
    verbs = [
        VerbSpec(pattern="calculate dew point for temperature {t:expr} humidity {rh:expr} into {target:ident}", description="Calculate dew point"),
        VerbSpec(pattern="convert emissions {amt:expr} of gas {g:expr} to co2 equivalent into {target:ident}", description="GHG GWP conversion")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate dew point ") or s.startswith("calculate heat index ") or s.startswith("calculate barometric pressure ") or s.startswith("convert emissions ")

CLIMATE_DOMAIN = ClimateDomain()
get_domain_registry().register(CLIMATE_DOMAIN)

__all__ = [
    "ClimateDomain", "CLIMATE_DOMAIN", "ClimateRuntime",
    "climate_dew_point", "climate_heat_index", "climate_barometric_pressure",
    "climate_co2_equivalent"
]
