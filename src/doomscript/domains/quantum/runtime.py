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
    from doomscript.runtime import Record
    return Record(GroverSearch(int(num_qubits), int(target)).run_optimal())
