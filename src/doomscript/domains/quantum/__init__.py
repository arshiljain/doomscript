"""Quantum Computing Simulation Domain Pack for DoomScript.

Enables native spoken-English multi-qubit statevectors, Hadamard, Pauli, CNOT gates,
Bell state entanglement, and projective measurement via 'use quantum'.
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
from doomscript.domains.quantum.runtime import (
    QuantumRuntime,
    QuantumRegister,
    quantum_register_create,
    quantum_apply_hadamard,
    quantum_apply_pauli_x,
    quantum_apply_pauli_y,
    quantum_apply_pauli_z,
    quantum_apply_phase,
    quantum_apply_cnot,
    quantum_measure_qubit,
    quantum_measure_all,
    quantum_state_probabilities,
    quantum_create_bell_state,
    QuantumErrorCorrection,
    GroverSearch,
    QuantumTeleportation,
    DensityMatrixSimulator,
    QuantumFourierTransform,
    VariationalQuantumEigensolver,
    quantum_density_matrix_analyze,
    quantum_apply_qft,
    quantum_vqe_ground_state,
    QuantumPhaseEstimationQPE,
    QuantumKeyDistributionBB84,
    quantum_qpe_estimate,
    quantum_bb84_simulate,
)
from doomscript.domains.quantum.parser import QuantumDomainParser
from doomscript.domains.quantum.exporter import QuantumASTExporter


class QuantumDomain(DomainContract):
    """Domain contract for Quantum Computing Simulation."""

    name = "quantum"
    aliases = ["quantum_computing", "qubit"]
    description = "Quantum computing, statevectors, unitary gates, and measurement"
    parser = QuantumDomainParser()
    runtime = QuantumRuntime()
    exporter = QuantumASTExporter()
    capabilities = ["qubits", "hadamard", "cnot", "pauli", "bell_state", "monte_carlo"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="create quantum register with {n:expr} qubits into {target:ident}",
            description="Initializes a multi-qubit statevector register",
        ),
        VerbSpec(
            pattern="apply hadamard [gate] to qubit {q:expr} in {reg:expr}",
            description="Applies Hadamard superposition gate",
        ),
        VerbSpec(
            pattern="apply cnot [gate] with control {c:expr} and target {t:expr} in {reg:expr}",
            description="Applies Controlled-NOT two-qubit entangling gate",
        ),
        VerbSpec(
            pattern="measure quantum register {reg:expr} with shots {s:expr} into {target:ident}",
            description="Samples computational basis states using Monte Carlo measurement",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("create quantum register with ")
            or s.startswith("apply hadamard ")
            or s.startswith("apply pauli x ")
            or s.startswith("apply pauli y ")
            or s.startswith("apply pauli z ")
            or s.startswith("apply phase ")
            or s.startswith("apply cnot ")
            or s.startswith("measure qubit ")
            or s.startswith("measure quantum register ")
            or s.startswith("calculate state probabilities for ")
            or s.startswith("create bell state in ")
            or s.startswith("grover search ")
            or s.startswith("diagnose steane syndrome ")
            or super().can_handle_line(line)
        )

    def can_handle_block(self, header: str) -> bool:
        return False


QUANTUM_DOMAIN = QuantumDomain()
get_domain_registry().register(QUANTUM_DOMAIN)

__all__ = [
    "QuantumDomain",
    "QUANTUM_DOMAIN",
    "QuantumRuntime",
    "QuantumRegister",
    "QuantumDomainParser",
    "QuantumASTExporter",
    "quantum_register_create",
    "quantum_apply_hadamard",
    "quantum_apply_pauli_x",
    "quantum_apply_pauli_y",
    "quantum_apply_pauli_z",
    "quantum_apply_phase",
    "quantum_apply_cnot",
    "quantum_measure_qubit",
    "quantum_measure_all",
    "quantum_state_probabilities",
    "quantum_create_bell_state",
    "QuantumErrorCorrection",
    "GroverSearch",
    "QuantumTeleportation",
    "DensityMatrixSimulator",
    "QuantumFourierTransform",
    "VariationalQuantumEigensolver",
    "quantum_density_matrix_analyze",
    "quantum_apply_qft",
    "quantum_vqe_ground_state",
    "QuantumPhaseEstimationQPE",
    "QuantumKeyDistributionBB84",
    "quantum_qpe_estimate",
    "quantum_bb84_simulate",
]
