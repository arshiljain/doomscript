from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.biomechanics.runtime import (
    biomech_joint_moment, biomech_center_of_mass,
    biomech_grf_impulse, biomech_muscle_tendon_force,
    biomech_hills_muscle_force_velocity, biomech_segment_moment_of_inertia_cylinder
)
from doomscript.domains.biomechanics.parser import BiomechanicsDomainParser
from doomscript.domains.biomechanics.exporter import BiomechanicsASTExporter

class BiomechanicsRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class BiomechanicsDomain(DomainContract):
    name = "biomechanics"
    aliases = ["biomech", "kinesiology", "human_motion"]
    description = "Biomechanics and kinesiology: joint moment, multi-segment center of mass, GRF impulse, muscle tendon force, Hill's force-velocity, and limb moment of inertia"
    parser = BiomechanicsDomainParser()
    runtime = BiomechanicsRuntime()
    exporter = BiomechanicsASTExporter()
    capabilities = ["joint_moment", "center_of_mass", "grf_impulse", "muscle_tendon_force", "hills_force_velocity", "moment_of_inertia"]
    verbs = [
        VerbSpec(pattern="calculate joint moment force {f:expr} arm {r:expr} angle {a:expr} into {target:ident}", description="Joint moment/torque"),
        VerbSpec(pattern="calculate center of mass masses {m:expr} positions {p:expr} into {target:ident}", description="Center of mass"),
        VerbSpec(pattern="calculate grf impulse forces {f:expr} dt {dt:expr} into {target:ident}", description="GRF impulse"),
        VerbSpec(pattern="calculate muscle tendon force muscle {fm:expr} pennation {a:expr} into {target:ident}", description="Muscle tendon force"),
        VerbSpec(pattern="calculate hill muscle force velocity {v:expr} f0 {f0:expr} param_a {a:expr} param_b {b:expr} into {target:ident}", description="Hill's muscle force-velocity"),
        VerbSpec(pattern="calculate segment inertia mass {m:expr} radius {r:expr} into {target:ident}", description="Segment moment of inertia")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate joint moment ") or s.startswith("calculate center of mass ") or s.startswith("calculate grf impulse ") or s.startswith("calculate muscle tendon force ") or s.startswith("calculate hill muscle force ") or s.startswith("calculate segment inertia ")

BIOMECHANICS_DOMAIN = BiomechanicsDomain()
get_domain_registry().register(BIOMECHANICS_DOMAIN)

__all__ = [
    "BiomechanicsDomain", "BIOMECHANICS_DOMAIN", "BiomechanicsRuntime",
    "biomech_joint_moment", "biomech_center_of_mass",
    "biomech_grf_impulse", "biomech_muscle_tendon_force",
    "biomech_hills_muscle_force_velocity", "biomech_segment_moment_of_inertia_cylinder"
]
