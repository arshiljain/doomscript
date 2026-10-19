"""Declarative specifications and Intermediate Representation for the Agent domain."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from doomscript.domains.base import DomainIR


@dataclass
class AgentSpec(DomainIR):
    """Specification for an AI Agent definition."""

    name: str
    role: str = ""
    instructions: str = ""
    model: str = "default"
    tools: List[str] = field(default_factory=list)
    memory: bool = True

    def validate(self) -> List[str]:
        errors = []
        if not self.name or not self.name.strip():
            errors.append("Agent specification must define a non-empty name")
        return errors


@dataclass
class TaskSpec(DomainIR):
    """Specification for an agent task assignment / execution."""

    agent_var: str
    task: str
    context_var: Optional[str] = None
    target_var: str = "output"
    as_json: bool = False

    def validate(self) -> List[str]:
        errors = []
        if not self.agent_var or not self.agent_var.strip():
            errors.append("Task specification requires a target agent variable")
        if not self.task or not self.task.strip():
            errors.append("Task specification requires a non-empty task description")
        return errors


@dataclass
class TeamSpec(DomainIR):
    """Specification for a multi-agent team."""

    team_name: str
    agent_vars: List[str] = field(default_factory=list)
    target_var: str = "team"

    def validate(self) -> List[str]:
        errors = []
        if not self.agent_vars:
            errors.append("Team specification requires at least one member agent")
        return errors
