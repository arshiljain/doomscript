"""Oceanography Domain for DoomScript: Physical oceanography, seawater thermodynamics, fluid dynamics, and wave kinematics."""
from typing import Any, Dict
from doomscript.domains.base import DomainContract, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.oceanography.parser import OceanographyDomainParser
from doomscript.domains.oceanography.runtime import (
    OceanographyRuntime,
    ocean_seawater_density,
    ocean_coriolis_parameter,
    ocean_gravity_wave_speed,
    ocean_hydrostatic_pressure,
    ocean_sound_speed_mackenzie,
    ocean_wind_stress,
    ocean_ekman_depth,
    ocean_brunt_vaisala_frequency,
    ocean_sverdrup_transport,
    ocean_sound_channel_sofar,
    ocean_ts_diagram_analysis,
    ocean_tidal_form_factor
)
from doomscript.domains.oceanography.exporter import OceanographyASTExporter

class OceanographyDomain(DomainContract):
    name = "oceanography"
    aliases = ["marine_science", "ocean_dynamics", "ocean_waves"]
    description = "Physical oceanography, seawater thermodynamics, fluid dynamics, and wave kinematics."
    parser = OceanographyDomainParser()
    runtime = OceanographyRuntime()
    exporter = OceanographyASTExporter()
    capabilities = [
        "seawater_density",
        "coriolis_parameter",
        "gravity_wave_speed",
        "hydrostatic_pressure",
        "sound_speed_mackenzie",
        "wind_stress",
        "ekman_depth",
        "brunt_vaisala_frequency",
        "sverdrup_transport",
        "sound_channel_sofar",
        "ts_diagram_analysis",
        "tidal_form_factor"
    ]
    verbs = [
        VerbSpec(pattern="calculate seawater density temp {t:expr} salinity {s:expr} into {target:ident}", description="Computes UNESCO equation of state seawater density"),
        VerbSpec(pattern="calculate coriolis parameter lat {lat:expr} into {target:ident}", description="Computes planetary Coriolis frequency parameter f"),
        VerbSpec(pattern="calculate ocean wave speed wavelength {lam:expr} depth {d:expr} into {target:ident}", description="Computes surface gravity wave phase velocity"),
        VerbSpec(pattern="calculate depth pressure depth {d:expr} into {target:ident}", description="Computes hydrostatic gauge pressure at depth"),
        VerbSpec(pattern="calculate seawater sound speed temp {t:expr} salinity {s:expr} depth {d:expr} into {target:ident}", description="Computes speed of sound using Mackenzie formula"),
        VerbSpec(pattern="calculate wind stress speed {u10:expr} into {target:ident}", description="Computes surface wind shear stress"),
        VerbSpec(pattern="calculate ekman depth wind {u10:expr} lat {lat:expr} into {target:ident}", description="Computes Ekman boundary layer depth and surface drift"),
        VerbSpec(pattern="calculate buoyancy frequency density {rho:expr} depth {z:expr} into {target:ident}", description="Computes Brunt-Vaisala stratification frequency N^2"),
        VerbSpec(pattern="calculate sverdrup transport curl {c:expr} lat {lat:expr} into {target:ident}", description="Computes wind-driven Sverdrup volume transport"),
        VerbSpec(pattern="analyze sound channel temp {t:expr} salinity {s:expr} depths {z:expr} into {target:ident}", description="Finds SOFAR channel axis depth and acoustic ducting profile"),
        VerbSpec(pattern="classify water mass temp {t:expr} salinity {s:expr} into {target:ident}", description="Analyzes T-S diagram potential density and classifies water mass"),
        VerbSpec(pattern="calculate tidal form factor m2 {m2:expr} s2 {s2:expr} k1 {k1:expr} o1 {o1:expr} into {target:ident}", description="Computes Courtier tidal form factor and regime")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate seawater density ") or
            s.startswith("calculate coriolis parameter ") or
            s.startswith("calculate ocean wave speed ") or
            s.startswith("calculate depth pressure ") or
            s.startswith("calculate seawater sound speed ") or
            s.startswith("calculate wind stress ") or
            s.startswith("calculate ekman depth ") or
            s.startswith("calculate buoyancy frequency ") or
            s.startswith("calculate sverdrup transport ") or
            s.startswith("analyze sound channel ") or
            s.startswith("classify water mass ") or
            s.startswith("calculate tidal form factor ")
        )

OCEANOGRAPHY_DOMAIN = OceanographyDomain()
get_domain_registry().register(OCEANOGRAPHY_DOMAIN)

__all__ = [
    "OCEANOGRAPHY_DOMAIN",
    "OceanographyDomain",
    "OceanographyRuntime",
    "ocean_seawater_density",
    "ocean_coriolis_parameter",
    "ocean_gravity_wave_speed",
    "ocean_hydrostatic_pressure",
    "ocean_sound_speed_mackenzie",
    "ocean_wind_stress",
    "ocean_ekman_depth",
    "ocean_brunt_vaisala_frequency",
    "ocean_sverdrup_transport",
    "ocean_sound_channel_sofar",
    "ocean_ts_diagram_analysis",
    "ocean_tidal_form_factor"
]
