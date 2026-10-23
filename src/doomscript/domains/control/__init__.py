"""Control Systems Domain for DoomScript: Feedback control, state-space systems, PID tuning, Kalman filtering, and stability."""
from typing import Any, Dict
from doomscript.domains.base import DomainContract, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.control.parser import ControlDomainParser
from doomscript.domains.control.runtime import (
    ControlRuntime,
    control_state_space_step,
    control_kalman_1d_step,
    control_pid_step,
    control_complementary_filter,
    control_routh_hurwitz_stable,
    control_bode_second_order,
    control_tustin_bilinear_transform,
    control_lqr_cost_evaluation,
    control_step_response_metrics,
    control_ziegler_nichols_tuning
)
from doomscript.domains.control.exporter import ControlASTExporter

class ControlDomain(DomainContract):
    name = "control"
    aliases = ["control_systems", "feedback", "pid"]
    description = "Feedback control, state-space systems, PID tuning, Kalman filtering, frequency response, and stability analysis."
    parser = ControlDomainParser()
    runtime = ControlRuntime()
    exporter = ControlASTExporter()
    capabilities = [
        "state_space",
        "kalman_filter",
        "pid",
        "complementary_filter",
        "routh_hurwitz",
        "bode_second_order",
        "tustin_transform",
        "lqr_cost",
        "step_response_metrics",
        "ziegler_nichols"
    ]
    verbs = [
        VerbSpec(pattern="step state space a {a:expr} b {b:expr} state {x:expr} input {u:expr} into {target:ident}", description="Calculates next discrete state space update"),
        VerbSpec(pattern="step kalman filter prior {x:expr} cov {p:expr} measurement {z:expr} noise {r:expr} into {target:ident}", description="Calculates single step 1D Kalman filter estimate"),
        VerbSpec(pattern="calculate pid step for error {e:expr} dt {dt:expr} integral {i:expr} prev_err {pe:expr} kp {kp:expr} ki {ki:expr} kd {kd:expr} into {target:ident}", description="Calculates PID output and updated integrator"),
        VerbSpec(pattern="fuse gyro {g:expr} accel {a:expr} prev {p:expr} into {target:ident}", description="Complementary sensor fusion filter"),
        VerbSpec(pattern="check stability for polynomial {coeffs:expr} into {target:ident}", description="Routh-Hurwitz polynomial stability check"),
        VerbSpec(pattern="calculate bode response omega_n {wn:expr} zeta {z:expr} frequencies {w:expr} into {target:ident}", description="Calculates second-order Bode magnitude and phase"),
        VerbSpec(pattern="discretize pole {s:expr} sampling {t:expr} into {target:ident}", description="Tustin bilinear continuous-to-discrete pole mapping"),
        VerbSpec(pattern="calculate lqr cost q {q:expr} r {r:expr} states {x:expr} inputs {u:expr} into {target:ident}", description="Evaluates quadratic LQR cost trajectory"),
        VerbSpec(pattern="evaluate step response times {t:expr} values {v:expr} target {tgt:expr} into {target:ident}", description="Calculates rise time, overshoot, and settling time"),
        VerbSpec(pattern="tune ziegler nichols ku {ku:expr} tu {tu:expr} into {target:ident}", description="Calculates Ziegler-Nichols PID tuning gains")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("step state space ") or
            s.startswith("step kalman filter ") or
            s.startswith("calculate pid step ") or
            s.startswith("fuse gyro ") or
            s.startswith("check stability ") or
            s.startswith("calculate bode response ") or
            s.startswith("discretize pole ") or
            s.startswith("calculate lqr cost ") or
            s.startswith("evaluate step response ") or
            s.startswith("tune ziegler nichols ")
        )

CONTROL_DOMAIN = ControlDomain()
get_domain_registry().register(CONTROL_DOMAIN)

__all__ = [
    "CONTROL_DOMAIN",
    "ControlDomain",
    "ControlRuntime",
    "control_state_space_step",
    "control_kalman_1d_step",
    "control_pid_step",
    "control_complementary_filter",
    "control_routh_hurwitz_stable",
    "control_bode_second_order",
    "control_tustin_bilinear_transform",
    "control_lqr_cost_evaluation",
    "control_step_response_metrics",
    "control_ziegler_nichols_tuning"
]
