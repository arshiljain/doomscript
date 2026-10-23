from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.climate.runtime import (
    ClimateRuntime, climate_dew_point, climate_heat_index,
    climate_wind_chill, climate_vapor_pressure_deficit,
    climate_barometric_altitude, climate_co2_equivalent,
    climate_radiative_forcing, climate_energy_balance_step,
    climate_geostrophic_wind
)
from doomscript.domains.climate.parser import ClimateDomainParser
from doomscript.domains.climate.exporter import ClimateASTExporter

class ClimateDomain(DomainContract):
    name = "climate"
    aliases = ["meteorology", "weather", "atmosphere"]
    description = "Meteorology & climate: Dew point, heat index, wind chill, VPD, radiative forcing, EBM, and geostrophic wind"
    parser = ClimateDomainParser()
    runtime = ClimateRuntime()
    exporter = ClimateASTExporter()
    capabilities = ["dew_point", "heat_index", "wind_chill", "vpd", "barometric_pressure", "co2_equivalent", "radiative_forcing", "ebm", "geostrophic_wind"]
    verbs = [
        VerbSpec(pattern="calculate dew point for temperature {t:expr} humidity {h:expr} into {target:ident}", description="Dew point"),
        VerbSpec(pattern="calculate wind chill for temperature {t:expr} wind {w:expr} into {target:ident}", description="Wind chill"),
        VerbSpec(pattern="calculate vpd for temperature {t:expr} humidity {h:expr} into {target:ident}", description="VPD"),
        VerbSpec(pattern="calculate radiative forcing for co2 {ppm:expr} into {target:ident}", description="Radiative forcing"),
        VerbSpec(pattern="calculate barometric pressure for altitude {alt:expr} into {target:ident}", description="Barometric pressure")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate dew point ") or
            s.startswith("calculate heat index ") or
            s.startswith("calculate wind chill ") or
            s.startswith("calculate vpd ") or
            s.startswith("calculate barometric pressure ") or
            s.startswith("convert emissions ") or
            s.startswith("calculate radiative forcing ")
        )

CLIMATE_DOMAIN = ClimateDomain()
get_domain_registry().register(CLIMATE_DOMAIN)

__all__ = [
    "ClimateDomain", "CLIMATE_DOMAIN", "ClimateRuntime",
    "climate_dew_point", "climate_heat_index", "climate_wind_chill",
    "climate_vapor_pressure_deficit", "climate_barometric_altitude",
    "climate_co2_equivalent", "climate_radiative_forcing",
    "climate_energy_balance_step", "climate_geostrophic_wind"
]
