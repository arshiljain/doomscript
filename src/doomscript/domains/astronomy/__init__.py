"""Astronomy, Celestial Mechanics & Astrodynamics Domain Pack for DoomScript.

Enables native spoken-English Julian date calculations, Keplerian orbit state vectors,
equatorial-to-horizontal coordinates, and Hohmann transfer delta-v via 'use astronomy'.
"""

from typing import List, Optional, Dict, Any
from doomscript.domains.base import (
    DomainContract,
    DomainParser,
    DomainRuntime,
    DomainASTExporter,
    DomainIR,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.astronomy.runtime import (
    CelestialTime,
    KeplerianOrbit,
    CelestialCoordinates,
    Astrodynamics,
    astronomy_julian_date,
    astronomy_kepler_orbit,
    astronomy_eq_to_horiz,
    astronomy_hohmann_transfer,
    PlanetaryEphemeris,
    EclipsePredictor,
    AtmosphericRefraction,
    astronomy_planet_position,
    astronomy_planet_geocentric,
    astronomy_predict_eclipse,
    astronomy_atmospheric_refraction,
    NBodySimulator,
    OrbitalTransfer,
    IAUPrecessionNutation,
    CelestialRiseSetTransit,
    astronomy_simulate_n_body,
    astronomy_calculate_hohmann,
    astronomy_calculate_bi_elliptic,
    astronomy_precession_j2000_to_date,
    astronomy_calculate_rise_set,
)
from doomscript.domains.astronomy.parser import AstronomyDomainParser
from doomscript.domains.astronomy.exporter import AstronomyASTExporter


class AstronomyRuntime(DomainRuntime):
    """Runtime coordinator for astronomy routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


class AstronomyDomain(DomainContract):
    """Domain contract for Astronomy & Astrodynamics."""

    name = "astronomy"
    aliases = ["astrodynamics", "celestial", "orbits"]
    description = "Keplerian orbits, celestial coordinate transformations, Julian dates, and Hohmann transfers"
    parser = AstronomyDomainParser()
    runtime = AstronomyRuntime()
    exporter = AstronomyASTExporter()
    capabilities = ["julian_date", "kepler_orbit", "equatorial_coords", "hohmann_transfer"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="calculate julian date for year {y:expr} month {m:expr} day {d:expr} into {target:ident}",
            description="Converts calendar date to astronomical Julian Date",
        ),
        VerbSpec(
            pattern="calculate hohmann transfer from radius {r1:expr} to {r2:expr} into {target:ident}",
            description="Calculates orbital transfer delta-v and flight duration",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("calculate julian date for ")
            or s.startswith("calculate hohmann transfer ")
            or s.startswith("simulate n body system ")
            or s.startswith("calculate bi-elliptic transfer ")
            or s.startswith("precess coordinates ")
            or s.startswith("calculate celestial rise and set ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


ASTRONOMY_DOMAIN = AstronomyDomain()
get_domain_registry().register(ASTRONOMY_DOMAIN)

__all__ = [
    "AstronomyDomain",
    "ASTRONOMY_DOMAIN",
    "AstronomyRuntime",
    "CelestialTime",
    "KeplerianOrbit",
    "CelestialCoordinates",
    "Astrodynamics",
    "astronomy_julian_date",
    "astronomy_kepler_orbit",
    "astronomy_eq_to_horiz",
    "astronomy_hohmann_transfer",
    "PlanetaryEphemeris",
    "EclipsePredictor",
    "AtmosphericRefraction",
    "astronomy_planet_position",
    "astronomy_planet_geocentric",
    "astronomy_predict_eclipse",
    "astronomy_atmospheric_refraction",
    "NBodySimulator",
    "OrbitalTransfer",
    "IAUPrecessionNutation",
    "CelestialRiseSetTransit",
    "astronomy_simulate_n_body",
    "astronomy_calculate_hohmann",
    "astronomy_calculate_bi_elliptic",
    "astronomy_precession_j2000_to_date",
    "astronomy_calculate_rise_set",
]
