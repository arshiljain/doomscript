"""Optimization & Operations Research Domain Specification and Intermediate Representation (IR)."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainIR


@dataclass
class LinearProgramSpec(DomainIR):
    """Specification for a linear programming problem (Simplex / Interior Point)."""

    name: str
    sense: str = "maximize"  # "maximize" or "minimize"
    objective: str = ""
    constraints: List[str] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)
    target_var: str = "lp_result"

    def validate(self) -> List[str]:
        errors = []
        if not self.name:
            errors.append("Linear program name cannot be empty")
        if self.sense.lower() not in ("maximize", "minimize"):
            errors.append(f"Invalid sense '{self.sense}', must be 'maximize' or 'minimize'")
        if not self.objective:
            errors.append("Objective function cannot be empty")
        if not self.constraints:
            errors.append("At least one constraint must be specified")
        return errors


@dataclass
class SolveLPSpec(DomainIR):
    """Specification for solving a defined linear program."""

    lp_name: str
    method: str = "simplex"  # "simplex" or "interior_point"
    target_var: str = "solution"

    def validate(self) -> List[str]:
        errors = []
        if not self.lp_name:
            errors.append("Linear program name cannot be empty")
        return errors
