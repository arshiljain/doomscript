"""Simulation & Optimization Domain Specification and Intermediate Representation (IR)."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from doomscript.domains.base import DomainIR


@dataclass
class SimulationSpec(DomainIR):
    """Specification for a discrete-event simulation (e.g. queueing system, Monte Carlo)."""

    name: str
    arrival_dist: str = "poisson"
    arrival_params: Dict[str, float] = field(default_factory=lambda: {"rate": 10.0})
    service_dist: str = "exponential"
    service_params: Dict[str, float] = field(default_factory=lambda: {"rate": 12.0})
    duration: int = 1000  # number of events or duration
    servers: int = 1
    metrics: List[str] = field(default_factory=lambda: ["waiting_time", "service_time", "queue_length"])
    target_var: str = "sim_results"

    def validate(self) -> List[str]:
        errors = []
        if not self.name:
            errors.append("Simulation name cannot be empty")
        if self.duration <= 0:
            errors.append(f"Simulation duration must be positive, got {self.duration}")
        if self.servers <= 0:
            errors.append(f"Server count must be >= 1, got {self.servers}")
        return errors


@dataclass
class OptimizationSpec(DomainIR):
    """Specification for numerical function optimization."""

    objective: str
    initial_guess: List[float] = field(default_factory=lambda: [0.0])
    tolerance: float = 1e-4
    max_iterations: int = 500
    target_var: str = "opt_results"

    def validate(self) -> List[str]:
        errors = []
        if not self.objective:
            errors.append("Optimization objective function cannot be empty")
        return errors
