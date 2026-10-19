"""Robotics Kinematics, Trajectory & Kalman Filtering Domain Pack for DoomScript.

Enables native spoken-English forward kinematics (DH parameters), inverse kinematics,
polynomial trajectories, and 2D Kalman filters via 'use robotics'.
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
from doomscript.domains.robotics.runtime import (
    DHParameter,
    ForwardKinematicsChain,
    InverseKinematics2D,
    TrajectoryPlanner,
    ExtendedKalmanFilter2D,
    robotics_forward_kinematics,
    robotics_inverse_kinematics_2link,
    robotics_cubic_trajectory,
    robotics_create_ekf,
)
from doomscript.domains.robotics.parser import RoboticsDomainParser
from doomscript.domains.robotics.exporter import RoboticsASTExporter


class RoboticsRuntime(DomainRuntime):
    """Runtime coordinator for robotics routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


class RoboticsDomain(DomainContract):
    """Domain contract for Robotics & Kinematics."""

    name = "robotics"
    aliases = ["kinematics_arm", "motion_planning"]
    description = "Forward/Inverse kinematics, Denavit-Hartenberg parameters, trajectory planning, and Kalman filtering"
    parser = RoboticsDomainParser()
    runtime = RoboticsRuntime()
    exporter = RoboticsASTExporter()
    capabilities = ["dh_parameters", "forward_kinematics", "inverse_kinematics", "trajectory", "ekf"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="calculate forward kinematics for dh parameters {params:expr} into {target:ident}",
            description="Calculates end-effector position from DH parameter chain",
        ),
        VerbSpec(
            pattern="solve 2link inverse kinematics with link1 {l1:expr} and link2 {l2:expr} for target {x:expr}, {y:expr} into {target:ident}",
            description="Solves analytical inverse kinematics for 2-link planar arm",
        ),
        VerbSpec(
            pattern="create ekf tracker with x {x:expr} and y {y:expr} into {target:ident}",
            description="Initializes 2D Extended Kalman Filter state estimator",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate forward kinematics for dh parameters ")
            or s.startswith("solve 2link inverse kinematics with ")
            or s.startswith("create ekf tracker with ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


ROBOTICS_DOMAIN = RoboticsDomain()
get_domain_registry().register(ROBOTICS_DOMAIN)

__all__ = [
    "RoboticsDomain",
    "ROBOTICS_DOMAIN",
    "RoboticsRuntime",
    "DHParameter",
    "ForwardKinematicsChain",
    "InverseKinematics2D",
    "TrajectoryPlanner",
    "ExtendedKalmanFilter2D",
    "robotics_forward_kinematics",
    "robotics_inverse_kinematics_2link",
    "robotics_cubic_trajectory",
    "robotics_create_ekf",
]
