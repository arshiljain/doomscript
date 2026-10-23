from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.optics.runtime import (
    OpticsRuntime, optics_thin_lens, optics_snell_refraction,
    optics_fresnel_reflectance, optics_rayleigh_resolution,
    optics_diffraction_grating, optics_brewster_angle,
    optics_fiber_numerical_aperture, optics_abcd_free_space,
    optics_abcd_thin_lens, optics_abcd_multiply, optics_ray_propagate,
    optics_gaussian_beam, optics_malus_law, optics_thin_film_anti_reflective
)
from doomscript.domains.optics.parser import OpticsDomainParser
from doomscript.domains.optics.exporter import OpticsASTExporter

class OpticsDomain(DomainContract):
    name = "optics"
    aliases = ["ray_optics", "wave_optics", "photonics"]
    description = "Geometrical & wave optics: Snell's law, thin lenses, Fresnel reflection, Rayleigh resolution, ABCD matrices, Gaussian beams, and fiber NA"
    parser = OpticsDomainParser()
    runtime = OpticsRuntime()
    exporter = OpticsASTExporter()
    capabilities = [
        "thin_lens", "snell_refraction", "fresnel_reflectance", "rayleigh_resolution",
        "diffraction_grating", "brewster_angle", "fiber_na", "abcd_matrix",
        "gaussian_beam", "malus_law", "ar_coating"
    ]
    verbs = [
        VerbSpec(pattern="calculate thin lens focal {f:expr} distance {do:expr} into {target:ident}", description="Thin lens image distance"),
        VerbSpec(pattern="calculate snell refraction n1 {n1:expr} n2 {n2:expr} angle {theta:expr} into {target:ident}", description="Snell refraction angle"),
        VerbSpec(pattern="calculate fresnel reflectance n1 {n1:expr} n2 {n2:expr} into {target:ident}", description="Fresnel normal reflection"),
        VerbSpec(pattern="calculate rayleigh resolution wavelength {lam:expr} na {na:expr} into {target:ident}", description="Rayleigh optical resolution limit"),
        VerbSpec(pattern="calculate brewster angle n1 {n1:expr} n2 {n2:expr} into {target:ident}", description="Brewster polarizing angle"),
        VerbSpec(pattern="calculate fiber aperture core {n1:expr} clad {n2:expr} into {target:ident}", description="Fiber numerical aperture"),
        VerbSpec(pattern="calculate gaussian beam wavelength {lam:expr} waist {w0:expr} distance {z:expr} into {target:ident}", description="Gaussian beam propagation")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate thin lens ") or
            s.startswith("calculate snell refraction ") or
            s.startswith("calculate fresnel reflectance ") or
            s.startswith("calculate rayleigh resolution ") or
            s.startswith("calculate grating diffraction ") or
            s.startswith("calculate brewster angle ") or
            s.startswith("calculate fiber aperture ") or
            s.startswith("calculate gaussian beam ")
        )

OPTICS_DOMAIN = OpticsDomain()
get_domain_registry().register(OPTICS_DOMAIN)

__all__ = [
    "OpticsDomain", "OPTICS_DOMAIN", "OpticsRuntime",
    "optics_thin_lens", "optics_snell_refraction", "optics_fresnel_reflectance",
    "optics_rayleigh_resolution", "optics_diffraction_grating",
    "optics_brewster_angle", "optics_fiber_numerical_aperture",
    "optics_abcd_free_space", "optics_abcd_thin_lens", "optics_abcd_multiply",
    "optics_ray_propagate", "optics_gaussian_beam", "optics_malus_law",
    "optics_thin_film_anti_reflective"
]
