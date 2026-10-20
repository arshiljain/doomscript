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
from doomscript.runtime import Record


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


# --- Deepened Quantum Simulation: Error Correction, Grover Search & Teleportation ---

class QuantumErrorCorrection:
    """Simulation of Quantum Error Correcting Codes (QECC) in pure statevector representation."""

    @staticmethod
    def encode_bit_flip(alpha: Any, beta: Any) -> List[complex]:
        """Encodes 1 logical qubit (alpha|0> + beta|1>) into 3 physical qubits: alpha|000> + beta|111>."""
        state = [0.0 + 0.0j] * 8
        state[0] = complex(alpha)  # |000>
        state[7] = complex(beta)   # |111>
        return state

    @staticmethod
    def inject_error(state: List[complex], error_type: str, target_qubit: int) -> List[complex]:
        """Applies Pauli X (bit-flip) or Pauli Z (phase-flip) error to a specific physical qubit."""
        new_state = list(state)
        n_qubits = int(math.log2(len(state)))
        q = target_qubit

        if error_type.upper() == "X":
            # Swap pairs where target bit differs
            res = [0.0 + 0.0j] * len(state)
            for i in range(len(state)):
                flipped_idx = i ^ (1 << (n_qubits - 1 - q))
                res[flipped_idx] = new_state[i]
            return res
        elif error_type.upper() == "Z":
            # Invert phase if target bit is 1
            res = list(state)
            for i in range(len(state)):
                if (i >> (n_qubits - 1 - q)) & 1:
                    res[i] = -res[i]
            return res
        return new_state

    @classmethod
    def detect_and_correct_bit_flip(cls, state: List[complex]) -> Tuple[List[complex], int]:
        """Detects single-qubit bit flip syndrome via parity checks and applies Pauli X recovery."""
        # Parity syndromes:
        # s1 = q0 XOR q1
        # s2 = q1 XOR q2
        # Syndrome mapping:
        # (0, 0) -> no error
        # (1, 0) -> qubit 0 error
        # (1, 1) -> qubit 1 error
        # (0, 1) -> qubit 2 error
        probs = [abs(amp) ** 2 for amp in state]
        max_idx = max(range(len(probs)), key=lambda i: probs[i])

        q0 = (max_idx >> 2) & 1
        q1 = (max_idx >> 1) & 1
        q2 = max_idx & 1

        s1 = q0 ^ q1
        s2 = q1 ^ q2

        error_qubit = -1
        if s1 == 1 and s2 == 0:
            error_qubit = 0
        elif s1 == 1 and s2 == 1:
            error_qubit = 1
        elif s1 == 0 and s2 == 1:
            error_qubit = 2

        corrected = list(state)
        if error_qubit != -1:
            corrected = cls.inject_error(corrected, "X", error_qubit)

        return corrected, error_qubit

    @classmethod
    def encode_phase_flip(cls, alpha: complex, beta: complex) -> List[complex]:
        """Encodes logical qubit into 3 physical qubits using Hadamard basis: alpha|+++> + beta|--->."""
        # |+> = (|0>+|1>)/sqrt(2), |-> = (|0>-|1>)/sqrt(2)
        # alpha|+++> + beta|---> expanded across all 8 basis states
        h = 1.0 / math.sqrt(8.0)
        state = [0.0 + 0.0j] * 8
        for i in range(8):
            # parity of ones in binary representation of i
            parity = bin(i).count("1") % 2
            sign_beta = -1.0 if parity == 1 else 1.0
            state[i] = (alpha + sign_beta * beta) * h
        return state

    @classmethod
    def detect_and_correct_phase_flip(cls, state: List[complex]) -> Tuple[List[complex], int]:
        """Corrects single-qubit phase flip by rotating into computational basis, correcting bit-flip, and rotating back."""
        # Apply Hadamard to all 3 qubits
        def _apply_h_all(st: List[complex]) -> List[complex]:
            dim = len(st)
            inv_sqrt8 = 1.0 / (2.0 * math.sqrt(2.0))
            out = [0.0 + 0.0j] * dim
            for i in range(dim):
                for j in range(dim):
                    dot = bin(i & j).count("1") % 2
                    sign = -1.0 if dot else 1.0
                    out[i] += sign * st[j]
                out[i] *= inv_sqrt8
            return out

        h_state = _apply_h_all(state)
        corrected_h, err_q = cls.detect_and_correct_bit_flip(h_state)
        final_state = _apply_h_all(corrected_h)
        return final_state, err_q


class GroverSearch:
    """Grover's Quantum Search Algorithm simulator with exact statevector evolution."""

    def __init__(self, num_qubits: int, target_state: int):
        self.num_qubits = max(1, min(10, int(num_qubits)))
        self.N = 1 << self.num_qubits
        self.target = target_state % self.N
        self.dim = self.N

        # Initialize uniform superposition |s> = 1/sqrt(N) sum |x>
        amp = 1.0 / math.sqrt(self.N)
        self.state = [complex(amp, 0.0)] * self.dim
        self.step_history: List[Dict[str, float]] = []

    def apply_oracle(self) -> None:
        """Phase inversion oracle: flips amplitude of the marked target state."""
        self.state[self.target] = -self.state[self.target]

    def apply_diffusion(self) -> None:
        """Grover diffusion operator (inversion about average): 2|s><s| - I."""
        avg = sum(self.state) / self.dim
        for i in range(self.dim):
            self.state[i] = 2.0 * avg - self.state[i]

    def step(self) -> Dict[str, float]:
        """Performs one full Grover iteration: Oracle followed by Diffusion."""
        self.apply_oracle()
        self.apply_diffusion()
        target_prob = abs(self.state[self.target]) ** 2
        entry = {
            "target_probability": round(target_prob, 6),
            "target_amplitude_real": round(self.state[self.target].real, 6),
        }
        self.step_history.append(entry)
        return entry

    def run_optimal(self) -> Dict[str, Any]:
        """Runs optimal number of iterations k ~ round(pi / 4 * sqrt(N))."""
        optimal_k = max(1, int(round((math.pi / 4.0) * math.sqrt(self.N))))
        for _ in range(optimal_k):
            self.step()

        probs = [abs(amp) ** 2 for amp in self.state]
        measured_state = max(range(self.dim), key=lambda i: probs[i])

        return {
            "num_qubits": self.num_qubits,
            "search_space_size": self.N,
            "target_state": self.target,
            "iterations_performed": optimal_k,
            "target_probability": round(probs[self.target], 6),
            "measured_state": measured_state,
            "success": (measured_state == self.target),
        }


class QuantumTeleportation:
    """Simulation of quantum state teleportation using Bell-state entanglement and classical feedforward."""

    @classmethod
    def teleport(cls, alpha: complex, beta: complex) -> Dict[str, Any]:
        """Transfers quantum state alpha|0> + beta|1> from Alice to Bob using an EPR pair."""
        # Normalize input state
        norm = math.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
        if norm < 1e-12:
            alpha, beta = 1.0 + 0j, 0.0 + 0j
        else:
            alpha, beta = alpha / norm, beta / norm

        # 3 qubits: Q0 = Alice's message, Q1 = Alice's EPR half, Q2 = Bob's EPR half
        # Initial 8-state vector: (alpha|0> + beta|1>) (x) (|00> + |11>)/sqrt(2)
        inv_sqrt2 = 1.0 / math.sqrt(2.0)
        # States: |000>, |011>, |100>, |111>
        # Qubit ordering: Q0 (msb), Q1, Q2 (lsb)
        state = [0.0 + 0.0j] * 8
        state[0] = alpha * inv_sqrt2  # |000>
        state[3] = alpha * inv_sqrt2  # |011>
        state[4] = beta * inv_sqrt2   # |100>
        state[7] = beta * inv_sqrt2   # |111>

        # Alice applies CNOT between Q0 (control) and Q1 (target)
        # For states with Q0 = 1, flip Q1 (bit 1)
        # |100> (4) -> |110> (6)
        # |111> (7) -> |101> (5)
        state[4], state[6] = state[6], state[4]
        state[7], state[5] = state[5], state[7]

        # Alice applies Hadamard to Q0
        # H on bit 2 (value 4)
        h_state = [0.0 + 0.0j] * 8
        inv_sqrt2 = 1.0 / math.sqrt(2.0)
        for i in range(4):
            # Q0 = 0 is i, Q0 = 1 is i + 4
            u = state[i]
            v = state[i + 4]
            h_state[i] = (u + v) * inv_sqrt2
            h_state[i + 4] = (u - v) * inv_sqrt2
        state = h_state

        # Measure Alice's 2 qubits (Q0 and Q1).
        # Alice obtains classical bits (m0, m1) from {00, 01, 10, 11}.
        # For simulation, each of the 4 outcomes occurs with probability 0.25.
        # Let's inspect Bob's uncollapsed conditional state for each measurement outcome:
        # m0 m1:
        # 00: Bob has alpha|0> + beta|1> (identity)
        # 01: Bob has alpha|1> + beta|0> (apply X)
        # 10: Bob has alpha|0> - beta|1> (apply Z)
        # 11: Bob has alpha|1> - beta|0> (apply X, then Z)

        results = {}
        for m0 in (0, 1):
            for m1 in (0, 1):
                idx0 = (m0 << 2) | (m1 << 1) | 0
                idx1 = (m0 << 2) | (m1 << 1) | 1
                bob_raw = [state[idx0] * 2.0, state[idx1] * 2.0]  # conditional unnormalized amplitude * 2

                # Bob applies corrections:
                if m1 == 1:
                    # Apply X
                    bob_raw[0], bob_raw[1] = bob_raw[1], bob_raw[0]
                if m0 == 1:
                    # Apply Z
                    bob_raw[1] = -bob_raw[1]

                # Fidelity with original (alpha, beta)
                inner = (alpha.conjugate() * bob_raw[0] + beta.conjugate() * bob_raw[1])
                fidelity = abs(inner) ** 2
                results[f"{m0}{m1}"] = {
                    "alice_bits": (m0, m1),
                    "bob_qubit": (complex(round(bob_raw[0].real, 6), round(bob_raw[0].imag, 6)),
                                  complex(round(bob_raw[1].real, 6), round(bob_raw[1].imag, 6))),
                    "fidelity": round(fidelity, 6),
                }

        return {
            "source_state": (alpha, beta),
            "measurement_outcomes": results,
            "perfect_fidelity_achieved": all(v["fidelity"] == 1.0 for v in results.values()),
        }


def quantum_grover_search(num_qubits: int = 3, target: int = 0) -> Any:
    return Record(GroverSearch(int(num_qubits), int(target)).run_optimal())


# ==============================================================================
# DENSITY MATRIX & MIXED STATE ENTANGLEMENT SIMULATOR
# ==============================================================================

class DensityMatrixSimulator:
    """Density matrix representation for pure and mixed quantum states.

    Computes state purity, von Neumann entropy, partial trace, and entanglement.
    """

    def __init__(self, num_qubits: int):
        self.num_qubits = max(1, min(6, int(num_qubits)))
        self.dim = 1 << self.num_qubits
        # Initialize to pure ground state |0...0><0...0|
        self.matrix: List[List[complex]] = [[0.0 + 0.0j] * self.dim for _ in range(self.dim)]
        self.matrix[0][0] = 1.0 + 0.0j

    @classmethod
    def from_statevector(cls, num_qubits: int, state: List[complex]) -> "DensityMatrixSimulator":
        dm = cls(num_qubits)
        dim = 1 << num_qubits
        for i in range(dim):
            for j in range(dim):
                dm.matrix[i][j] = state[i] * state[j].conjugate()
        return dm

    @classmethod
    def maximally_mixed(cls, num_qubits: int) -> "DensityMatrixSimulator":
        dm = cls(num_qubits)
        dim = 1 << num_qubits
        prob = 1.0 / dim
        dm.matrix = [[0.0 + 0.0j] * dim for _ in range(dim)]
        for i in range(dim):
            dm.matrix[i][i] = complex(prob, 0.0)
        return dm

    def trace(self) -> float:
        """Computes Tr(rho)."""
        tr = sum(self.matrix[i][i] for i in range(self.dim))
        return round(tr.real, 6)

    def purity(self) -> float:
        """Computes Tr(rho^2). For pure states = 1.0, for mixed states < 1.0."""
        pur = 0.0
        for i in range(self.dim):
            for j in range(self.dim):
                pur += (self.matrix[i][j] * self.matrix[j][i]).real
        return round(pur, 6)

    def partial_trace_qubit(self, trace_qubit: int) -> List[List[complex]]:
        """Traces out a single qubit to obtain the reduced density matrix."""
        if self.num_qubits <= 1:
            raise ValueError("Cannot partially trace a single qubit system")

        reduced_qubits = self.num_qubits - 1
        reduced_dim = 1 << reduced_qubits
        reduced = [[0.0 + 0.0j] * reduced_dim for _ in range(reduced_dim)]

        shift = trace_qubit
        mask_low = (1 << shift) - 1
        mask_high = ~((1 << (shift + 1)) - 1)

        for i_red in range(reduced_dim):
            for j_red in range(reduced_dim):
                sum_val = 0.0 + 0.0j
                for b in (0, 1):
                    # Reconstruct full indices with qubit 'trace_qubit' set to b
                    i_full = ((i_red & mask_high) << 1) | (b << shift) | (i_red & mask_low)
                    j_full = ((j_red & mask_high) << 1) | (b << shift) | (j_red & mask_low)
                    sum_val += self.matrix[i_full][j_full]
                reduced[i_red][j_red] = sum_val

        return reduced

    def analyze(self) -> Dict[str, Any]:
        pur = self.purity()
        tr = self.trace()
        is_pure = abs(pur - 1.0) < 1e-4

        # 2x2 analytical eigenvalues for 1-qubit reduced subsystem
        entropy = 0.0
        if self.dim == 2:
            a = self.matrix[0][0].real
            d = self.matrix[1][1].real
            bc = (self.matrix[0][1] * self.matrix[1][0]).real
            disc = math.sqrt(max(0.0, ((a - d) ** 2) + 4.0 * bc))
            l1 = max(0.0, min(1.0, 0.5 * (a + d + disc)))
            l2 = max(0.0, min(1.0, 0.5 * (a + d - disc)))
            for lam in (l1, l2):
                if lam > 1e-12:
                    entropy -= lam * math.log2(lam)
        else:
            # Linear entropy approximation S_L = 1 - Tr(rho^2)
            entropy = max(0.0, 1.0 - pur)

        return {
            "num_qubits": self.num_qubits,
            "dimension": self.dim,
            "trace": tr,
            "purity": pur,
            "is_pure": is_pure,
            "entropy": round(entropy, 4),
        }


# ==============================================================================
# QUANTUM FOURIER TRANSFORM (QFT)
# ==============================================================================

class QuantumFourierTransform:
    """Exact Discrete Quantum Fourier Transform and Inverse QFT."""

    @classmethod
    def apply(cls, state: List[complex], inverse: bool = False) -> List[complex]:
        n = len(state)
        if n == 0:
            return []

        sign = -1.0 if inverse else 1.0
        factor = 1.0 / math.sqrt(n)
        result: List[complex] = [0.0 + 0.0j] * n

        for k in range(n):
            acc = 0.0 + 0.0j
            for j in range(n):
                angle = sign * 2.0 * math.pi * j * k / n
                phase = complex(math.cos(angle), math.sin(angle))
                acc += state[j] * phase
            result[k] = acc * factor

        return result

    @classmethod
    def run_on_register(cls, reg: QuantumRegister, inverse: bool = False) -> Dict[str, Any]:
        new_state = cls.apply(reg.state, inverse=inverse)
        reg.state = new_state
        probabilities = [round(abs(amp) ** 2, 6) for amp in new_state]
        peak_idx = probabilities.index(max(probabilities))
        return {
            "num_qubits": reg.num_qubits,
            "peak_index": peak_idx,
            "peak_probability": max(probabilities),
            "inverse": inverse,
            "probabilities": probabilities,
        }


# ==============================================================================
# VARIATIONAL QUANTUM EIGENSOLVER (VQE)
# ==============================================================================

class VariationalQuantumEigensolver:
    """VQE ground state energy solver for 2-qubit molecular/spin Hamiltonians."""

    def __init__(self, h_terms: Dict[str, float]):
        """Hamiltonian specified as dict: e.g. {'II': -1.0, 'ZI': 0.5, 'IZ': 0.5, 'XX': 0.2, 'ZZ': 0.3}"""
        self.h_terms = h_terms

    def _state_from_angles(self, theta: List[float]) -> List[complex]:
        # 2-qubit parameterized state:
        # |00> -> Ry(theta[0]) x Ry(theta[1]) -> CNOT -> Ry(theta[2]) x Ry(theta[3])
        c0, s0 = math.cos(theta[0] / 2.0), math.sin(theta[0] / 2.0)
        c1, s1 = math.cos(theta[1] / 2.0), math.sin(theta[1] / 2.0)

        # After first Ry layer on |00>:
        # [c0*c1, c0*s1, s0*c1, s0*s1]
        s = [c0 * c1, c0 * s1, s0 * c1, s0 * s1]

        # CNOT(0 -> 1): flips target qubit 1 if control qubit 0 is 1
        # |10> (idx 2) <-> |11> (idx 3)
        s[2], s[3] = s[3], s[2]

        # Second Ry layer
        c2, s2 = math.cos(theta[2] / 2.0), math.sin(theta[2] / 2.0)
        c3, s3 = math.cos(theta[3] / 2.0), math.sin(theta[3] / 2.0)

        # Tensor product of rotation matrices Ry(theta2) x Ry(theta3) applied to s
        m00, m01 = c2 * c3, -c2 * s3
        m02, m03 = -s2 * c3, s2 * s3
        # Direct calculation of final amplitudes
        final_state = [0.0] * 4
        # Ry2 on q0: [[c2, -s2], [s2, c2]]
        # Ry3 on q1: [[c3, -s3], [s3, c3]]
        # Combine manually for exact precision:
        q0_u = [[c2, -s2], [s2, c2]]
        q1_u = [[c3, -s3], [s3, c3]]
        for i in range(2):
            for j in range(2):
                idx_out = (i << 1) | j
                acc = 0.0
                for k in range(2):
                    for l in range(2):
                        idx_in = (k << 1) | l
                        acc += q0_u[i][k] * q1_u[j][l] * s[idx_in]
                final_state[idx_out] = acc

        return [complex(val, 0.0) for val in final_state]

    def energy(self, theta: List[float]) -> float:
        """Evaluates expectation value <psi(theta)|H|psi(theta)>."""
        psi = self._state_from_angles(theta)
        total_energy = 0.0

        for pauli, coeff in self.h_terms.items():
            pauli = pauli.upper()
            exp_val = 0.0
            if pauli == "II":
                exp_val = 1.0
            elif pauli == "ZI":
                exp_val = abs(psi[0]) ** 2 + abs(psi[1]) ** 2 - abs(psi[2]) ** 2 - abs(psi[3]) ** 2
            elif pauli == "IZ":
                exp_val = abs(psi[0]) ** 2 - abs(psi[1]) ** 2 + abs(psi[2]) ** 2 - abs(psi[3]) ** 2
            elif pauli == "ZZ":
                exp_val = abs(psi[0]) ** 2 - abs(psi[1]) ** 2 - abs(psi[2]) ** 2 + abs(psi[3]) ** 2
            elif pauli == "XX":
                # X0X1 flips both qubits: 00 <-> 11, 01 <-> 10
                exp_val = 2.0 * (psi[0].conjugate() * psi[3] + psi[1].conjugate() * psi[2]).real
            total_energy += coeff * exp_val

        return total_energy

    def optimize(self, initial_angles: Optional[List[float]] = None, iterations: int = 40, lr: float = 0.2) -> Dict[str, Any]:
        """Gradient descent optimization of ansatz parameters."""
        theta = list(initial_angles) if initial_angles is not None else [0.5, 0.5, 0.5, 0.5]
        best_e = self.energy(theta)
        eps = 1e-4

        for _ in range(iterations):
            grad = [0.0] * 4
            current_e = self.energy(theta)
            for d in range(4):
                theta_plus = list(theta)
                theta_plus[d] += eps
                e_plus = self.energy(theta_plus)
                grad[d] = (e_plus - current_e) / eps

            # Update parameters
            for d in range(4):
                theta[d] -= lr * grad[d]

            new_e = self.energy(theta)
            if new_e < best_e:
                best_e = new_e

        return {
            "optimal_energy": round(best_e, 4),
            "optimal_parameters": [round(th, 4) for th in theta],
            "iterations": iterations,
        }


def quantum_density_matrix_analyze(num_qubits: int, state_vector: Optional[List[complex]] = None) -> Any:
    """Analyzes purity, trace, and entropy of pure or mixed quantum state."""
    if state_vector is not None:
        dm = DensityMatrixSimulator.from_statevector(num_qubits, state_vector)
    else:
        dm = DensityMatrixSimulator(num_qubits)
    return Record(dm.analyze())


def quantum_apply_qft(reg: QuantumRegister, inverse: bool = False) -> Any:
    """Executes Quantum Fourier Transform on quantum register."""
    return Record(QuantumFourierTransform.run_on_register(reg, inverse=inverse))


def quantum_vqe_ground_state(hamiltonian_terms: Dict[str, float], iterations: int = 40) -> Any:
    """Computes ground state energy of Hamiltonian using Variational Quantum Eigensolver."""
    vqe = VariationalQuantumEigensolver(hamiltonian_terms)
    return Record(vqe.optimize(iterations=iterations))


class QuantumPhaseEstimationQPE:
    """Quantum Phase Estimation algorithm estimating eigenphase theta for U|psi> = exp(2*pi*i*theta)|psi>."""

    @classmethod
    def estimate_phase(cls, true_theta: float, counting_qubits: int = 4) -> Dict[str, Any]:
        t = max(2, min(int(counting_qubits), 8))
        dim = 1 << t
        # Counting register state vector in superposition
        state = []
        scale = 1.0 / math.sqrt(dim)
        for k in range(dim):
            angle = 2.0 * math.pi * k * float(true_theta)
            state.append(complex(scale * math.cos(angle), scale * math.sin(angle)))

        # Apply Inverse QFT
        iqft_state = []
        for j in range(dim):
            s = 0.0 + 0.0j
            for k in range(dim):
                angle = -2.0 * math.pi * j * k / float(dim)
                w = complex(math.cos(angle), math.sin(angle))
                s += state[k] * w
            iqft_state.append(s * scale)

        probs = [abs(z) ** 2 for z in iqft_state]
        best_idx = max(range(dim), key=lambda idx: probs[idx])
        estimated_theta = round(best_idx / float(dim), 4)

        return {
            "true_theta": float(true_theta),
            "estimated_theta": estimated_theta,
            "measured_index": best_idx,
            "probability": round(probs[best_idx], 4),
            "counting_qubits": t,
        }


class QuantumKeyDistributionBB84:
    """Bennett-Brassard 1984 (BB84) protocol simulator with sifting and eavesdropping detection."""

    @classmethod
    def simulate(
        cls,
        num_bits: int = 64,
        eve_present: bool = False,
        seed: Optional[int] = 42,
    ) -> Dict[str, Any]:
        rng = random.Random(seed)
        n = max(8, int(num_bits))

        alice_bits = [rng.randint(0, 1) for _ in range(n)]
        alice_bases = [rng.randint(0, 1) for _ in range(n)]

        transmitted_bits = list(alice_bits)

        if eve_present:
            for i in range(n):
                eve_basis = rng.randint(0, 1)
                if eve_basis != alice_bases[i]:
                    transmitted_bits[i] = rng.randint(0, 1)

        bob_bases = [rng.randint(0, 1) for _ in range(n)]
        bob_bits = []
        for i in range(n):
            if bob_bases[i] == alice_bases[i]:
                bob_bits.append(transmitted_bits[i])
            else:
                bob_bits.append(rng.randint(0, 1))

        sifted_alice = []
        sifted_bob = []
        for i in range(n):
            if alice_bases[i] == bob_bases[i]:
                sifted_alice.append(alice_bits[i])
                sifted_bob.append(bob_bits[i])

        m = len(sifted_alice)
        if m == 0:
            return {
                "raw_bits_count": n,
                "sifted_bits_count": 0,
                "qber": 0.0,
                "key_accepted": False,
                "shared_key": [],
                "shared_key_length": 0,
            }

        test_sample_size = max(1, m // 3)
        test_errors = sum(1 for i in range(test_sample_size) if sifted_alice[i] != sifted_bob[i])
        qber = test_errors / float(test_sample_size)

        key = sifted_alice[test_sample_size:]
        key_accepted = (qber < 0.11)

        return {
            "raw_bits_count": n,
            "sifted_bits_count": m,
            "qber": round(qber, 4),
            "key_accepted": key_accepted,
            "shared_key": key if key_accepted else [],
            "shared_key_length": len(key) if key_accepted else 0,
        }


def quantum_qpe_estimate(theta: float, counting_qubits: int = 4) -> Record:
    """Estimates unitary eigenphase using Quantum Phase Estimation."""
    return Record(QuantumPhaseEstimationQPE.estimate_phase(theta, counting_qubits=counting_qubits))


def quantum_bb84_simulate(num_bits: int = 64, eve_present: bool = False, seed: Optional[int] = 42) -> Record:
    """Simulates BB84 quantum key distribution and eavesdropping detection."""
    return Record(QuantumKeyDistributionBB84.simulate(num_bits=num_bits, eve_present=eve_present, seed=seed))


