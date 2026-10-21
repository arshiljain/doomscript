"""Robotics Kinematics, Trajectory & Kalman Filtering Domain Pack for DoomScript.

Enables native spoken-English forward kinematics (DH parameters), inverse kinematics,
polynomial trajectories, and 2D Kalman filters via 'use robotics'.
"""

from typing import List, Optional, Dict, Any
from doomscript.core.record import Record
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
    RRTNode,
    RRTPlanner2D,
    ArtificialPotentialField2D,
    DifferentialDriveKinematics,
    PurePursuitController,
    StewartPlatformIK,
    TrapezoidalVelocityProfile,
    robotics_forward_kinematics,
    robotics_inverse_kinematics_2link,
    robotics_cubic_trajectory,
    robotics_create_ekf,
    robotics_rrt_plan,
    robotics_rrt_star_plan,
    robotics_apf_forces,
    robotics_diff_drive_forward,
    robotics_diff_drive_odometry,
    robotics_pure_pursuit,
    robotics_stewart_platform_ik,
    robotics_trapezoidal_profile,
    DubinsCarShortestPath,
    OccupancyGridMap2D,
    robotics_dubins_path,
    robotics_occupancy_grid_update,
    RapidlyExploringRandomTreeStar3D,
    DynamicWindowApproachDWA,
    robotics_rrt_star_3d,
    robotics_dwa_velocity,
    SixDOFManipulatorKinematics,
    StateLatticeMotionPlanner,
    robotics_6dof_fk,
    robotics_6dof_ik,
    robotics_state_lattice_plan,
    robotics_move_arm,
    robotics_read_lidar,
    RoboticsTrajectoryIR,
    execute_robotics_ir,
)
from doomscript.domains.robotics.parser import RoboticsDomainParser
from doomscript.domains.robotics.exporter import RoboticsASTExporter


class RoboticsRuntime(DomainRuntime):
    """Runtime coordinator for robotics routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        from doomscript.domains.robotics.runtime import (
            RoboticsTrajectoryIR,
            robotics_dubins_path,
            robotics_rrt_plan,
            robotics_rrt_star_plan,
            robotics_cubic_trajectory,
        )
        if isinstance(ir, RoboticsTrajectoryIR):
            start = ir.start if ir.start is not None else [0.0, 0.0, 0.0]
            goal = ir.goal if ir.goal is not None else [5.0, 5.0, 0.0]
            method = ir.method.lower()
            if method == "dubins":
                s3 = (start[0], start[1], start[2] if len(start) > 2 else 0.0)
                g3 = (goal[0], goal[1], goal[2] if len(goal) > 2 else 0.0)
                res = robotics_dubins_path(s3, g3, turning_radius=float(ir.turning_radius))
                if isinstance(res, Record):
                    res["name"] = ir.name
                    res["total_waypoints"] = res.get("waypoints_count", len(res.get("waypoints", [])))
                return res
            elif method == "rrt":
                bounds = [[-50.0, 50.0], [-50.0, 50.0]]
                return robotics_rrt_plan(start[:2], goal[:2], bounds=bounds, obstacles=ir.obstacles, step_size=float(ir.step_size))
            elif method == "rrt_star":
                bounds = [[-50.0, 50.0], [-50.0, 50.0]]
                return robotics_rrt_star_plan(start[:2], goal[:2], bounds=bounds, obstacles=ir.obstacles, search_radius=float(ir.search_radius))
            elif method == "cubic":
                q0 = start[0] if isinstance(start, (list, tuple)) else float(start)
                q1 = goal[0] if isinstance(goal, (list, tuple)) else float(goal)
                return robotics_cubic_trajectory(q0, q1, 0.0, 0.0, 0.0, 1.0, 50)
            else:
                s3 = (start[0], start[1], start[2] if len(start) > 2 else 0.0)
                g3 = (goal[0], goal[1], goal[2] if len(goal) > 2 else 0.0)
                return robotics_dubins_path(s3, g3, turning_radius=float(ir.turning_radius))
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
            pattern="move arm to x: {x:expr}, y: {y:expr} into {target:ident}",
            description="Computes arm joint configuration to reach Cartesian coordinate",
        ),
        VerbSpec(
            pattern="read lidar sensor into {target:ident}",
            description="Reads range-bearing distance scans from lidar sensor",
        ),
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
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("calculate forward kinematics for dh parameters ")
            or s.startswith("solve 2link inverse kinematics with ")
            or s.startswith("create ekf tracker with ")
        )

    def can_handle_block(self, header: str) -> bool:
        s = header.strip().lower()
        return s.startswith("trajectory ") or self.parser.can_handle_block(header)


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
    "DubinsCarShortestPath",
    "OccupancyGridMap2D",
    "robotics_dubins_path",
    "robotics_occupancy_grid_update",
    "RapidlyExploringRandomTreeStar3D",
    "DynamicWindowApproachDWA",
    "robotics_rrt_star_3d",
    "robotics_dwa_velocity",
    "SixDOFManipulatorKinematics",
    "StateLatticeMotionPlanner",
    "robotics_6dof_fk",
    "robotics_6dof_ik",
    "robotics_state_lattice_plan",
    "robotics_move_arm",
    "robotics_read_lidar",
    "RoboticsTrajectoryIR",
    "execute_robotics_ir",
]
