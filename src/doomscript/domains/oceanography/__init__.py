from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.oceanography.runtime import (
    ocean_seawater_density, ocean_coriolis_parameter,
    ocean_gravity_wave_speed, ocean_hydrostatic_pressure,
    ocean_sound_speed_mackenzie, ocean_wind_stress
)
from doomscript.domains.oceanography.parser import OceanographyDomainParser
from doomscript.domains.oceanography.exporter import OceanographyASTExporter

class OceanographyRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class OceanographyDomain(DomainContract):
    name = "oceanography"
    aliases = ["marine_science", "ocean_dynamics", "ocean_waves"]
    description = "Ocean physics & dynamics: seawater equation of state density, Coriolis parameter, surface gravity waves, Mackenzie sound speed, and wind stress"
    parser = OceanographyDomainParser()
    runtime = OceanographyRuntime()
    exporter = OceanographyASTExporter()
    capabilities = ["seawater_density", "coriolis_parameter", "gravity_wave_speed", "hydrostatic_pressure", "sound_speed_mackenzie", "wind_stress"]
    verbs = [
        VerbSpec(pattern="calculate seawater density temp {t:expr} salinity {s:expr} into {target:ident}", description="UNESCO seawater density"),
        VerbSpec(pattern="calculate coriolis parameter lat {lat:expr} into {target:ident}", description="Coriolis frequency parameter"),
        VerbSpec(pattern="calculate ocean wave speed wavelength {l:expr} depth {d:expr} into {target:ident}", description="Gravity wave phase velocity"),
        VerbSpec(pattern="calculate depth pressure depth {d:expr} into {target:ident}", description="Hydrostatic pressure"),
        VerbSpec(pattern="calculate seawater sound speed temp {t:expr} salinity {s:expr} depth {d:expr} into {target:ident}", description="Mackenzie underwater sound speed"),
        VerbSpec(pattern="calculate wind stress speed {u:expr} into {target:ident}", description="Wind shear stress on ocean surface")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate seawater density ") or s.startswith("calculate coriolis parameter ") or s.startswith("calculate ocean wave speed ") or s.startswith("calculate depth pressure ") or s.startswith("calculate seawater sound speed ") or s.startswith("calculate wind stress ")

OCEANOGRAPHY_DOMAIN = OceanographyDomain()
get_domain_registry().register(OCEANOGRAPHY_DOMAIN)

__all__ = [
    "OceanographyDomain", "OCEANOGRAPHY_DOMAIN", "OceanographyRuntime",
    "ocean_seawater_density", "ocean_coriolis_parameter",
    "ocean_gravity_wave_speed", "ocean_hydrostatic_pressure",
    "ocean_sound_speed_mackenzie", "ocean_wind_stress"
]
