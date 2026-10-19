"""Physics, Kinematics & Controls Domain Pack for DoomScript.

Enables native spoken-English ballistic trajectories, aerodynamic drag,
AABB & SAT polygon collisions, spring-damper dynamics, and PID control via 'use physics'.
"""

from typing import List, Optional
from doomscript.domains.base import (
    DomainContract,
    DomainParser,
    DomainRuntime,
    DomainASTExporter,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.physics.runtime import (
    PhysicsRuntime,
    PhysicsPID,
    physics_trajectory,
    physics_ballistic_range,
    physics_projectile_drag,
    physics_aabb_collision,
    physics_sat_polygon_collision,
    physics_spring_damper,
    physics_orbital_velocity,
    physics_escape_velocity,
    physics_pid_create,
    physics_pid_update,
)
from doomscript.domains.physics.parser import PhysicsDomainParser
from doomscript.domains.physics.exporter import PhysicsASTExporter


class PhysicsDomain(DomainContract):
    """Domain contract for Physics, Kinematics & Controls."""

    name = "physics"
    aliases = ["kinematics", "mechanics"]
    description = "Physics, kinematics, ballistics, polygon collisions, and PID controls"
    parser = PhysicsDomainParser()
    runtime = PhysicsRuntime()
    exporter = PhysicsASTExporter()
    capabilities = ["ballistics", "sat_collision", "harmonic_oscillator", "pid_control", "orbital"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="calculate trajectory with velocity {v:expr} and angle {deg:expr} into {target:ident}",
            description="Simulates 2D ballistic trajectory points",
        ),
        VerbSpec(
            pattern="calculate ballistic range with velocity {v:expr} and angle {deg:expr} into {target:ident}",
            description="Calculates flat-ground ideal ballistic range",
        ),
        VerbSpec(
            pattern="check collision between aabb {b1:expr} and {b2:expr} into {target:ident}",
            description="Checks collision between two 2D Axis-Aligned Bounding Boxes",
        ),
        VerbSpec(
            pattern="check polygon collision between {p1:expr} and {p2:expr} using sat into {target:ident}",
            description="Separating Axis Theorem collision check for convex 2D polygons",
        ),
        VerbSpec(
            pattern="create pid controller with kp {kp:expr} and ki {ki:expr} and kd {kd:expr} into {target:ident}",
            description="Instantiates a PID controller",
        ),
        VerbSpec(
            pattern="update pid {pid:expr} with setpoint {sp:expr} and measurement {m:expr} into {target:ident}",
            description="Updates PID controller and returns output control effort",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate trajectory ")
            or s.startswith("calculate ballistic range ")
            or s.startswith("calculate projectile with drag ")
            or s.startswith("check collision between aabb ")
            or s.startswith("check polygon collision between ")
            or s.startswith("simulate spring damper ")
            or s.startswith("orbital velocity for mass ")
            or s.startswith("escape velocity for mass ")
            or s.startswith("create pid controller ")
            or s.startswith("update pid ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


PHYSICS_DOMAIN = PhysicsDomain()
get_domain_registry().register(PHYSICS_DOMAIN)

__all__ = [
    "PhysicsDomain",
    "PHYSICS_DOMAIN",
    "PhysicsRuntime",
    "PhysicsPID",
    "PhysicsDomainParser",
    "PhysicsASTExporter",
    "physics_trajectory",
    "physics_ballistic_range",
    "physics_projectile_drag",
    "physics_aabb_collision",
    "physics_sat_polygon_collision",
    "physics_spring_damper",
    "physics_orbital_velocity",
    "physics_escape_velocity",
    "physics_pid_create",
    "physics_pid_update",
]
