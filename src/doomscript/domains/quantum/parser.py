"""Quantum Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class QuantumDomainParser(DomainParser):
    """Parses spoken-English quantum statevector, gates, and measurement statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # create quantum register with <n> qubits into <target>
        m_qreg = re.match(
            r"^create\s+quantum\s+register\s+with\s+(.+?)\s+qubits?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_qreg:
            n = m_qreg.group(1).strip()
            target = m_qreg.group(2).strip()
            return f"set {target} to quantum_register_create({n})"

        # apply hadamard gate to qubit <q> in <qreg>
        m_h = re.match(
            r"^apply\s+hadamard\s+(?:gate\s+)?to\s+qubit\s+(.+?)\s+in\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_h:
            q = m_h.group(1).strip()
            reg = m_h.group(2).strip()
            return f"quantum_apply_hadamard({reg}, {q})"

        # apply pauli x gate to qubit <q> in <qreg>
        m_x = re.match(
            r"^apply\s+pauli\s*x\s+(?:gate\s+)?to\s+qubit\s+(.+?)\s+in\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_x:
            q = m_x.group(1).strip()
            reg = m_x.group(2).strip()
            return f"quantum_apply_pauli_x({reg}, {q})"

        # apply pauli y gate to qubit <q> in <qreg>
        m_y = re.match(
            r"^apply\s+pauli\s*y\s+(?:gate\s+)?to\s+qubit\s+(.+?)\s+in\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_y:
            q = m_y.group(1).strip()
            reg = m_y.group(2).strip()
            return f"quantum_apply_pauli_y({reg}, {q})"

        # apply pauli z gate to qubit <q> in <qreg>
        m_z = re.match(
            r"^apply\s+pauli\s*z\s+(?:gate\s+)?to\s+qubit\s+(.+?)\s+in\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_z:
            q = m_z.group(1).strip()
            reg = m_z.group(2).strip()
            return f"quantum_apply_pauli_z({reg}, {q})"

        # apply phase gate to qubit <q> with angle <theta> in <qreg>
        m_ph = re.match(
            r"^apply\s+phase\s+(?:gate\s+)?to\s+qubit\s+(.+?)\s+with\s+angle\s+(.+?)\s+in\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_ph:
            q = m_ph.group(1).strip()
            theta = m_ph.group(2).strip()
            reg = m_ph.group(3).strip()
            return f"quantum_apply_phase({reg}, {q}, {theta})"

        # apply cnot gate with control <c> and target <t> in <qreg>
        m_cnot = re.match(
            r"^apply\s+cnot\s+(?:gate\s+)?with\s+control\s+(.+?)\s+and\s+target\s+(.+?)\s+in\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_cnot:
            c = m_cnot.group(1).strip()
            t = m_cnot.group(2).strip()
            reg = m_cnot.group(3).strip()
            return f"quantum_apply_cnot({reg}, {c}, {t})"

        # measure qubit <q> in <qreg> into <target>
        m_mq = re.match(
            r"^measure\s+qubit\s+(.+?)\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mq:
            q = m_mq.group(1).strip()
            reg = m_mq.group(2).strip()
            target = m_mq.group(3).strip()
            return f"set {target} to quantum_measure_qubit({reg}, {q})"

        # measure quantum register <qreg> with shots <shots> into <target>
        m_mreg = re.match(
            r"^measure\s+quantum\s+register\s+(.+?)\s+with\s+shots\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mreg:
            reg = m_mreg.group(1).strip()
            shots = m_mreg.group(2).strip()
            target = m_mreg.group(3).strip()
            return f"set {target} to quantum_measure_all({reg}, {shots})"

        # calculate state probabilities for <qreg> into <target>
        m_probs = re.match(
            r"^calculate\s+state\s+probabilities\s+for\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_probs:
            reg = m_probs.group(1).strip()
            target = m_probs.group(2).strip()
            return f"set {target} to quantum_state_probabilities({reg})"

        # create bell state in <qreg> into <target>
        m_bell = re.match(
            r"^create\s+bell\s+state\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bell:
            reg = m_bell.group(1).strip()
            target = m_bell.group(2).strip()
            return f"set {target} to quantum_create_bell_state({reg})"

        # grover search [with] <n> qubits for target <t> into <target>
        m_grover = re.match(
            r"^grover\s+search\s+(?:with\s+)?(\d+)\s+qubits?\s+for\s+target\s+(\d+)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_grover:
            n = m_grover.group(1).strip()
            t = m_grover.group(2).strip()
            target = m_grover.group(3).strip()
            return f"set {target} to quantum_grover_search(num_qubits={n}, target={t})"

        # analyze density matrix for <n> qubits into <target>
        m_dm = re.match(
            r"^analyze\s+density\s+matrix\s+for\s+(.+?)\s+qubits?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dm:
            n, target = m_dm.group(1).strip(), m_dm.group(2).strip()
            return f"set {target} to quantum_density_matrix_analyze({n})"

        # apply qft to <reg> [inverse] into <target>
        m_qft = re.match(
            r"^apply\s+qft\s+to\s+(.+?)(?:\s+(inverse))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_qft:
            reg = m_qft.group(1).strip()
            is_inv = "True" if m_qft.group(2) else "False"
            target = m_qft.group(3).strip()
            return f"set {target} to quantum_apply_qft({reg}, inverse={is_inv})"

        # solve vqe ground state for hamiltonian <h_terms> [with iterations <iters>] into <target>
        m_vqe = re.match(
            r"^solve\s+vqe\s+ground\s+state\s+for\s+hamiltonian\s+(.+?)(?:\s+with\s+iterations\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vqe:
            h_terms = m_vqe.group(1).strip()
            iters = m_vqe.group(2) if m_vqe.group(2) else "40"
            target = m_vqe.group(3).strip()
            return f"set {target} to quantum_vqe_ground_state({h_terms}, iterations={iters})"

        # estimate quantum phase for theta <theta> [with <t> qubits] into <target>
        m_qpe = re.match(
            r"^estimate\s+quantum\s+phase\s+for\s+theta\s+(.+?)(?:\s+with\s+(\d+)\s+qubits?)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_qpe:
            th = m_qpe.group(1).strip()
            t_qubits = m_qpe.group(2) or "4"
            target = m_qpe.group(3).strip()
            return f"set {target} to quantum_qpe_estimate({th}, counting_qubits={t_qubits})"

        # simulate bb84 protocol [with <n> bits] [with eve <eve>] into <target>
        m_bb84 = re.match(
            r"^simulate\s+bb84\s+protocol(?:\s+with\s+(\d+)\s+bits?)?(?:\s+with\s+eve\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bb84:
            n_bits = m_bb84.group(1) or "64"
            eve = m_bb84.group(2) or "False"
            target = m_bb84.group(3).strip()
            return f"set {target} to quantum_bb84_simulate(num_bits={n_bits}, eve_present={eve})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Quantum domain does not define declarative blocks")
