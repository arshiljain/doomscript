"""Declarative specifications and Intermediate Representation for Graph Analytics domain."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from doomscript.domains.base import DomainIR


@dataclass
class GraphCreateSpec(DomainIR):
    directed: bool = False
    target_var: str = "graph"

    def validate(self) -> List[str]:
        return []


@dataclass
class GraphAddNodeSpec(DomainIR):
    graph_var: str
    node_id: str
    attributes: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        errors = []
        if not self.node_id:
            errors.append("GraphAddNodeSpec requires a node ID")
        return errors


@dataclass
class GraphAddEdgeSpec(DomainIR):
    graph_var: str
    u: str
    v: str
    weight: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        errors = []
        if not self.u or not self.v:
            errors.append("GraphAddEdgeSpec requires both source and target node IDs")
        return errors


@dataclass
class GraphShortestPathSpec(DomainIR):
    graph_var: str
    start_node: str
    end_node: str
    target_var: str

    def validate(self) -> List[str]:
        errors = []
        if not self.start_node or not self.end_node:
            errors.append("GraphShortestPathSpec requires start and end node IDs")
        return errors


@dataclass
class GraphPageRankSpec(DomainIR):
    graph_var: str
    target_var: str

    def validate(self) -> List[str]:
        return []


@dataclass
class GraphDegreesSpec(DomainIR):
    graph_var: str
    target_var: str

    def validate(self) -> List[str]:
        return []


@dataclass
class GraphCommunitiesSpec(DomainIR):
    graph_var: str
    target_var: str

    def validate(self) -> List[str]:
        return []
