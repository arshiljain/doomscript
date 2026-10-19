"""Quantum Computing Simulation Domain Runtime for DoomScript.

Pure Python standard library implementation of multi-qubit statevector registers,
quantum single-qubit gates (Hadamard, Pauli X/Y/Z, Phase), entangling two-qubit gates (CNOT),
Bell state synthesis, and Monte Carlo projective quantum measurement.
"""

import cmath
import math
import random
from typing import Any, Dict, List, Optional, Tuple, Set
from doomscript.domains.base import DomainRuntime, DomainIR


class QuantumRuntime(DomainRuntime):
    """Runtime coordinator for quantum simulation."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


class QuantumRegister:
    """Multi-qubit quantum state vector simulation engine."""

    def __init__(self, num_qubits: int):
        self.num_qubits = max(1, min(14, int(num_qubits)))
        self.dim = 1 << self.num_qubits
        # Statevector initialized to |0...0>
        self.state: List[complex] = [0.0 + 0.0j] * self.dim
        self.state[0] = 1.0 + 0.0j

    @property
    def amplitudes(self) -> List[complex]:
        return self.state

    def apply_hadamard(self, qubit: int) -> "QuantumRegister":
        """Apply single-qubit Hadamard superposition gate H = 1/sqrt(2) * [[1, 1], [1, -1]]."""
        q = int(qubit)
        if not (0 <= q < self.num_qubits):
            return self
        inv_sqrt2 = 1.0 / math.sqrt(2.0)
        bit = 1 << q
        for i in range(self.dim):
            if (i & bit) == 0:
                j = i | bit
                val_i = self.state[i]
                val_j = self.state[j]
                self.state[i] = inv_sqrt2 * (val_i + val_j)
                self.state[j] = inv_sqrt2 * (val_i - val_j)
        return self

    def apply_pauli_x(self, qubit: int) -> "QuantumRegister":
        """Apply Pauli-X (NOT) gate."""
        q = int(qubit)
        if not (0 <= q < self.num_qubits):
            return self
        bit = 1 << q
        for i in range(self.dim):
            if (i & bit) == 0:
                j = i | bit
                self.state[i], self.state[j] = self.state[j], self.state[i]
        return self

    def apply_pauli_y(self, qubit: int) -> "QuantumRegister":
        """Apply Pauli-Y gate [[0, -i], [i, 0]]."""
        q = int(qubit)
        if not (0 <= q < self.num_qubits):
            return self
        bit = 1 << q
        for i in range(self.dim):
            if (i & bit) == 0:
                j = i | bit
                val_i = self.state[i]
                val_j = self.state[j]
                self.state[i] = -1j * val_j
                self.state[j] = 1j * val_i
        return self

    def apply_pauli_z(self, qubit: int) -> "QuantumRegister":
        """Apply Pauli-Z phase flip gate [[1, 0], [0, -1]]."""
        q = int(qubit)
        if not (0 <= q < self.num_qubits):
            return self
        bit = 1 << q
        for i in range(self.dim):
            if (i & bit) != 0:
                self.state[i] = -self.state[i]
        return self

    def apply_phase(self, qubit: int, theta: float) -> "QuantumRegister":
        """Apply arbitrary phase shift gate [[1, 0], [0, exp(i*theta)]]."""
        q = int(qubit)
        if not (0 <= q < self.num_qubits):
            return self
        phase_factor = cmath.exp(1j * float(theta))
        bit = 1 << q
        for i in range(self.dim):
            if (i & bit) != 0:
                self.state[i] *= phase_factor
        return self

    def apply_cnot(self, control: int, target: int) -> "QuantumRegister":
        """Apply Controlled-NOT (CNOT) entangling two-qubit gate."""
        c = int(control)
        t = int(target)
        if c == t or not (0 <= c < self.num_qubits) or not (0 <= t < self.num_qubits):
            return self
        c_bit = 1 << c
        t_bit = 1 << t
        for i in range(self.dim):
            if (i & c_bit) != 0 and (i & t_bit) == 0:
                j = i | t_bit
                self.state[i], self.state[j] = self.state[j], self.state[i]
        return self

    def probabilities(self) -> List[float]:
        """Compute exact measurement probability distribution across all computational basis states."""
        return [round(abs(amp) ** 2, 6) for amp in self.state]

    def measure_qubit(self, qubit: int) -> int:
        """Measure a single qubit, collapsing state vector and returning 0 or 1."""
        q = int(qubit)
        if not (0 <= q < self.num_qubits):
            return 0
        bit = 1 << q
        p1 = sum(abs(self.state[i]) ** 2 for i in range(self.dim) if (i & bit) != 0)
        measured = 1 if random.random() < p1 else 0

        # Collapse state vector
        norm = math.sqrt(p1 if measured == 1 else (1.0 - p1))
        if norm > 1e-9:
            for i in range(self.dim):
                if ((i & bit) != 0) == (measured == 1):
                    self.state[i] /= norm
                else:
                    self.state[i] = 0.0 + 0.0j
        return measured

    def measure_all(self, shots: int = 1024) -> Dict[str, int]:
        """Sample computational basis bitstrings using Monte Carlo measurement."""
        shots = max(1, int(shots))
        probs = self.probabilities()
        basis_labels = [bin(i)[2:].zfill(self.num_qubits) for i in range(self.dim)]
        samples = random.choices(basis_labels, weights=probs, k=shots)

        counts: Dict[str, int] = {}
        for bitstring in samples:
            counts[bitstring] = counts.get(bitstring, 0) + 1
        return dict(sorted(counts.items()))


def quantum_register_create(num_qubits: Any) -> QuantumRegister:
    """Create a new quantum register with num_qubits."""
    return QuantumRegister(int(num_qubits))


def quantum_apply_hadamard(qreg: Any, qubit: Any) -> Any:
    if isinstance(qreg, QuantumRegister):
        qreg.apply_hadamard(int(qubit))
    return qreg


def quantum_apply_pauli_x(qreg: Any, qubit: Any) -> Any:
    if isinstance(qreg, QuantumRegister):
        qreg.apply_pauli_x(int(qubit))
    return qreg


def quantum_apply_pauli_y(qreg: Any, qubit: Any) -> Any:
    if isinstance(qreg, QuantumRegister):
        qreg.apply_pauli_y(int(qubit))
    return qreg


def quantum_apply_pauli_z(qreg: Any, qubit: Any) -> Any:
    if isinstance(qreg, QuantumRegister):
        qreg.apply_pauli_z(int(qubit))
    return qreg


def quantum_apply_phase(qreg: Any, qubit: Any, theta: Any) -> Any:
    if isinstance(qreg, QuantumRegister):
        qreg.apply_phase(int(qubit), float(theta))
    return qreg


def quantum_apply_cnot(qreg: Any, control: Any, target: Any) -> Any:
    if isinstance(qreg, QuantumRegister):
        qreg.apply_cnot(int(control), int(target))
    return qreg


def quantum_measure_qubit(qreg: Any, qubit: Any) -> int:
    if isinstance(qreg, QuantumRegister):
        return qreg.measure_qubit(int(qubit))
    return 0


def quantum_measure_all(qreg: Any, shots: Any = 1024) -> Dict[str, int]:
    if isinstance(qreg, QuantumRegister):
        return qreg.measure_all(int(shots))
    return {}


def quantum_state_probabilities(qreg: Any) -> List[float]:
    if isinstance(qreg, QuantumRegister):
        return qreg.probabilities()
    return []


def quantum_create_bell_state(qreg: Any) -> Any:
    """Entangle qubits 0 and 1 into Bell state |Phi+> = (|00> + |11>) / sqrt(2)."""
    if isinstance(qreg, QuantumRegister) and qreg.num_qubits >= 2:
        qreg.apply_hadamard(0)
        qreg.apply_cnot(0, 1)
    return qreg


quantum_apply_h = quantum_apply_hadamard
quantum_apply_x = quantum_apply_pauli_x
quantum_apply_y = quantum_apply_pauli_y
quantum_apply_z = quantum_apply_pauli_z
quantum_measure = quantum_measure_qubit
quantum_sample = quantum_measure_all
quantum_create_register = quantum_register_create


def quantum_bell_state(name: str = "phi_plus") -> QuantumRegister:
    """Prepare a standard Bell state (|Phi+>, |Phi->, |Psi+>, |Psi->)."""
    reg = QuantumRegister(2)
    reg.apply_hadamard(0)
    reg.apply_cnot(0, 1)
    n = str(name).lower()
    if n in ("phi_minus", "phi-"):
        reg.apply_pauli_z(0)
    elif n in ("psi_plus", "psi+"):
        reg.apply_pauli_x(1)
    elif n in ("psi_minus", "psi-"):
        reg.apply_pauli_x(1)
        reg.apply_pauli_z(0)
    return reg


def quantum_state_vector(qreg: Any) -> List[float]:
    """Return the real-valued state vector or amplitudes magnitude."""
    if isinstance(qreg, QuantumRegister):
        return [float(abs(amp)) for amp in qreg.amplitudes]
    return []


def execute_quantum_ir(spec_id: str) -> Any:
    """Executes a stored Quantum IR specification."""
    from doomscript.domains.registry import get_domain_registry
    reg = get_domain_registry()
    spec = reg.get_spec(spec_id)
    if spec is None:
        raise ValueError(f"Unknown quantum spec: {spec_id}")
    return QuantumRuntime().execute_ir(spec, {})
