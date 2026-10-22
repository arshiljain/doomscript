from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.astrophysics.runtime import (
    astro_schwarzschild_radius, astro_stefan_boltzmann_luminosity,
    astro_eddington_luminosity, astro_hubble_velocity,
    astro_jeans_mass, astro_friedmann_critical_density
)
from doomscript.domains.astrophysics.parser import AstrophysicsDomainParser
from doomscript.domains.astrophysics.exporter import AstrophysicsASTExporter

class AstrophysicsRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class AstrophysicsDomain(DomainContract):
    name = "astrophysics"
    aliases = ["stellar_physics", "cosmology", "black_holes"]
    description = "Theoretical astrophysics & cosmology: Schwarzschild radius, Stefan-Boltzmann luminosity, Eddington limit, Hubble recession, Jeans mass, and Friedmann critical density"
    parser = AstrophysicsDomainParser()
    runtime = AstrophysicsRuntime()
    exporter = AstrophysicsASTExporter()
    capabilities = ["schwarzschild_radius", "stellar_luminosity", "eddington_luminosity", "hubble_velocity", "jeans_mass", "friedmann_density"]
    verbs = [
        VerbSpec(pattern="calculate schwarzschild radius mass {m:expr} into {target:ident}", description="Event horizon radius"),
        VerbSpec(pattern="calculate stellar luminosity radius {r:expr} temp {t:expr} into {target:ident}", description="Stefan-Boltzmann luminosity"),
        VerbSpec(pattern="calculate eddington luminosity mass {m:expr} into {target:ident}", description="Eddington luminosity limit"),
        VerbSpec(pattern="calculate hubble velocity distance {d:expr} into {target:ident}", description="Hubble cosmic velocity"),
        VerbSpec(pattern="calculate jeans mass temp {t:expr} density {n:expr} into {target:ident}", description="Jeans collapse mass"),
        VerbSpec(pattern="calculate critical density h0 {h0:expr} into {target:ident}", description="Friedmann critical universe density")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate schwarzschild radius ") or s.startswith("calculate stellar luminosity ") or s.startswith("calculate eddington luminosity ") or s.startswith("calculate hubble velocity ") or s.startswith("calculate jeans mass ") or s.startswith("calculate critical density ")

ASTROPHYSICS_DOMAIN = AstrophysicsDomain()
get_domain_registry().register(ASTROPHYSICS_DOMAIN)

__all__ = [
    "AstrophysicsDomain", "ASTROPHYSICS_DOMAIN", "AstrophysicsRuntime",
    "astro_schwarzschild_radius", "astro_stefan_boltzmann_luminosity",
    "astro_eddington_luminosity", "astro_hubble_velocity",
    "astro_jeans_mass", "astro_friedmann_critical_density"
]
