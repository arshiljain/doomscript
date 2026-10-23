"""Biomechanics Domain for DoomScript: Musculoskeletal modeling, kinesiology, inverse dynamics, and human movement kinetics."""
from typing import Any, Dict
from doomscript.domains.base import DomainContract, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.biomechanics.parser import BiomechanicsDomainParser
from doomscript.domains.biomechanics.runtime import (
    BiomechanicsRuntime,
    biomech_joint_moment,
    biomech_center_of_mass,
    biomech_grf_impulse,
    biomech_muscle_tendon_force,
    biomech_hills_muscle_force_velocity,
    biomech_segment_moment_of_inertia_cylinder,
    biomech_inverse_dynamics_2d_segment,
    biomech_muscle_mechanical_work_power,
    biomech_vertical_loading_rate,
    biomech_pennate_muscle_aponeurosis,
    biomech_joint_contact_force,
    biomech_gait_froude_number
)
from doomscript.domains.biomechanics.exporter import BiomechanicsASTExporter

class BiomechanicsDomain(DomainContract):
    name = "biomechanics"
    aliases = ["biomech", "kinesiology", "human_motion"]
    description = "Musculoskeletal modeling, kinesiology, inverse dynamics, and human movement kinetics."
    parser = BiomechanicsDomainParser()
    runtime = BiomechanicsRuntime()
    exporter = BiomechanicsASTExporter()
    capabilities = [
        "joint_moment",
        "center_of_mass",
        "grf_impulse",
        "muscle_tendon_force",
        "hills_force_velocity",
        "moment_of_inertia",
        "inverse_dynamics",
        "work_power",
        "loading_rate",
        "pennation_geometry",
        "joint_contact_force",
        "gait_froude"
    ]
    verbs = [
        VerbSpec(pattern="calculate joint moment force {f:expr} arm {r:expr} into {target:ident}", description="Calculates joint torque/moment in N*m"),
        VerbSpec(pattern="calculate center of mass masses {m:expr} positions {x:expr} into {target:ident}", description="Calculates 1D center of mass"),
        VerbSpec(pattern="calculate grf impulse forces {f:expr} dt {dt:expr} into {target:ident}", description="Calculates ground reaction force linear impulse"),
        VerbSpec(pattern="calculate muscle tendon force muscle {f:expr} pennation {a:expr} into {target:ident}", description="Calculates force transmitted along tendon"),
        VerbSpec(pattern="calculate hill muscle force velocity {v:expr} f0 {f0:expr} param_a {a:expr} param_b {b:expr} into {target:ident}", description="Calculates muscle force from Hill model"),
        VerbSpec(pattern="calculate segment inertia mass {m:expr} radius {r:expr} into {target:ident}", description="Calculates limb segment moment of inertia"),
        VerbSpec(pattern="calculate joint power moment {m:expr} velocity {w:expr} into {target:ident}", description="Calculates joint power and mechanical work"),
        VerbSpec(pattern="calculate loading rate forces {f:expr} rate {sr:expr} weight {bw:expr} into {target:ident}", description="Calculates average and instantaneous vertical loading rates"),
        VerbSpec(pattern="calculate pennation thickness {t:expr} length {l:expr} into {target:ident}", description="Calculates muscle architectural pennation angle"),
        VerbSpec(pattern="calculate joint contact moment {m:expr} arm {r:expr} reaction {rx:expr} into {target:ident}", description="Calculates compressive joint contact force"),
        VerbSpec(pattern="calculate gait froude velocity {v:expr} leg {l:expr} into {target:ident}", description="Calculates Alexander gait Froude number")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate joint moment ") or
            s.startswith("calculate center of mass ") or
            s.startswith("calculate grf impulse ") or
            s.startswith("calculate muscle tendon force ") or
            s.startswith("calculate hill muscle force ") or
            s.startswith("calculate segment inertia ") or
            s.startswith("calculate joint power ") or
            s.startswith("calculate loading rate ") or
            s.startswith("calculate pennation ") or
            s.startswith("calculate joint contact ") or
            s.startswith("calculate gait froude ")
        )

BIOMECHANICS_DOMAIN = BiomechanicsDomain()
get_domain_registry().register(BIOMECHANICS_DOMAIN)

__all__ = [
    "BIOMECHANICS_DOMAIN",
    "BiomechanicsDomain",
    "BiomechanicsRuntime",
    "biomech_joint_moment",
    "biomech_center_of_mass",
    "biomech_grf_impulse",
    "biomech_muscle_tendon_force",
    "biomech_hills_muscle_force_velocity",
    "biomech_segment_moment_of_inertia_cylinder",
    "biomech_inverse_dynamics_2d_segment",
    "biomech_muscle_mechanical_work_power",
    "biomech_vertical_loading_rate",
    "biomech_pennate_muscle_aponeurosis",
    "biomech_joint_contact_force",
    "biomech_gait_froude_number"
]
