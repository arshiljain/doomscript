from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.control.runtime import (
    control_state_space_step, control_kalman_1d_step, control_pid_step,
    control_complementary_filter, control_routh_hurwitz_stable
)
from doomscript.domains.control.parser import ControlDomainParser
from doomscript.domains.control.exporter import ControlASTExporter

class ControlRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class ControlDomain(DomainContract):
    name = "control"
    aliases = ["control_systems", "feedback", "pid"]
    description = "Feedback control: State-space, Kalman filter, PID tuning, sensor fusion, and Routh-Hurwitz stability"
    parser = ControlDomainParser()
    runtime = ControlRuntime()
    exporter = ControlASTExporter()
    capabilities = ["state_space", "kalman_filter", "pid", "complementary_filter", "routh_hurwitz"]
    verbs = [
        VerbSpec(pattern="step state space a {a:expr} b {b:expr} state {x:expr} input {u:expr} into {target:ident}", description="State-space step"),
        VerbSpec(pattern="step kalman filter prior {x:expr} cov {p:expr} measurement {z:expr} noise {r:expr} into {target:ident}", description="Kalman step"),
        VerbSpec(pattern="check stability for polynomial {coeffs:expr} into {target:ident}", description="Routh-Hurwitz stability")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("step state space ") or s.startswith("step kalman filter ") or s.startswith("calculate pid step ") or s.startswith("fuse gyro ") or s.startswith("check stability ")

CONTROL_DOMAIN = ControlDomain()
get_domain_registry().register(CONTROL_DOMAIN)

__all__ = [
    "ControlDomain", "CONTROL_DOMAIN", "ControlRuntime",
    "control_state_space_step", "control_kalman_1d_step", "control_pid_step",
    "control_complementary_filter", "control_routh_hurwitz_stable"
]
