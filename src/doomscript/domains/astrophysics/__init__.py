from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.astrophysics.runtime import (
    AstrophysicsRuntime, astro_schwarzschild_radius,
    astro_stefan_boltzmann_luminosity, astro_eddington_luminosity,
    astro_hubble_velocity, astro_jeans_mass,
    astro_friedmann_critical_density, astro_hawking_radiation,
    astro_einstein_radius, astro_stellar_lifetime_years
)
from doomscript.domains.astrophysics.parser import AstrophysicsDomainParser
from doomscript.domains.astrophysics.exporter import AstrophysicsASTExporter

class AstrophysicsDomain(DomainContract):
    name = "astrophysics"
    aliases = ["stellar_physics", "cosmology", "black_holes"]
    description = "Deepened Astrophysics domain: Schwarzschild event horizons, Stefan-Boltzmann luminosity, Eddington limits, Jeans collapse, Hubble expansion, and Hawking radiation"
    parser = AstrophysicsDomainParser()
    runtime = AstrophysicsRuntime()
    exporter = AstrophysicsASTExporter()
    capabilities = ["schwarzschild_radius", "stellar_luminosity", "eddington_luminosity", "hubble_velocity", "jeans_mass", "critical_density", "hawking_radiation", "einstein_radius"]
    verbs = [
        VerbSpec(pattern="calculate schwarzschild radius mass {m:expr} into {target:ident}", description="Gravitational event horizon radius"),
        VerbSpec(pattern="calculate stellar luminosity radius {r:expr} temp {t:expr} into {target:ident}", description="Stefan-Boltzmann stellar luminosity"),
        VerbSpec(pattern="calculate eddington luminosity mass {m:expr} into {target:ident}", description="Eddington radiation accretion limit"),
        VerbSpec(pattern="calculate hubble velocity distance {d:expr} into {target:ident}", description="Hubble cosmic expansion velocity"),
        VerbSpec(pattern="calculate jeans mass temp {t:expr} density {n:expr} into {target:ident}", description="Jeans gravitational collapse mass"),
        VerbSpec(pattern="calculate critical density h0 {h0:expr} into {target:ident}", description="Friedmann cosmological critical density"),
        VerbSpec(pattern="calculate hawking radiation mass {m:expr} into {target:ident}", description="Hawking radiation temperature and lifetime")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate schwarzschild radius ") or
            s.startswith("calculate stellar luminosity ") or
            s.startswith("calculate eddington luminosity ") or
            s.startswith("calculate hubble velocity ") or
            s.startswith("calculate jeans mass ") or
            s.startswith("calculate critical density ") or
            s.startswith("calculate hawking radiation ")
        )

ASTROPHYSICS_DOMAIN = AstrophysicsDomain()
get_domain_registry().register(ASTROPHYSICS_DOMAIN)

__all__ = [
    "ASTROPHYSICS_DOMAIN", "AstrophysicsDomain", "AstrophysicsRuntime",
    "astro_schwarzschild_radius", "astro_stefan_boltzmann_luminosity",
    "astro_eddington_luminosity", "astro_hubble_velocity",
    "astro_jeans_mass", "astro_friedmann_critical_density",
    "astro_hawking_radiation", "astro_einstein_radius",
    "astro_stellar_lifetime_years"
]
