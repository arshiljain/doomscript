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

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Quantum domain does not define declarative blocks")
