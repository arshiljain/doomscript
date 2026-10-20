"""Electronics, Logic Gates & IoT Domain Pack for DoomScript.

Enables native spoken-English Ohm's Law formulas, resistor color decoding,
voltage dividers, 555 timers, truth table logic evaluators, and GPIO pins via 'use circuit'.
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
from doomscript.domains.circuit.runtime import (
    CircuitRuntime,
    CircuitBoard,
    circuit_ohm_voltage,
    circuit_ohm_current,
    circuit_ohm_resistance,
    circuit_power,
    circuit_decode_resistor_bands,
    circuit_voltage_divider,
    circuit_555_timer_freq,
    circuit_rc_time_constant,
    circuit_evaluate_truth_table,
    circuit_pwm_duty_cycle,
    circuit_gpio_set,
    circuit_gpio_read,
    ModifiedNodalAnalysis,
    BodePlotAnalyzer,
    OpAmpModel,
    circuit_mna_dc_solve,
    circuit_bode_plot,
    circuit_opamp_amplify,
    NonlinearDiodeSolver,
    TransmissionLineRLGC,
    StateSpaceRLCSimulator,
    circuit_solve_diode,
    circuit_transmission_line,
    circuit_simulate_rlc_step,
    ActiveSallenKeyFilterDesigner,
    RLCTransientLaplaceSolver,
    circuit_design_sallen_key,
    circuit_rlc_laplace_transient,
)
from doomscript.domains.circuit.parser import CircuitDomainParser
from doomscript.domains.circuit.exporter import CircuitASTExporter


class CircuitDomain(DomainContract):
    """Domain contract for Electronics & IoT."""

    name = "circuit"
    aliases = ["electronics", "iot", "hardware"]
    description = "Electronics, Ohm's law, resistor decoding, logic gates, and GPIO pins"
    parser = CircuitDomainParser()
    runtime = CircuitRuntime()
    exporter = CircuitASTExporter()
    capabilities = ["ohms_law", "resistor_bands", "voltage_divider", "timer_555", "gpio", "logic_gates"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="calculate voltage with current {i:expr} and resistance {r:expr} into {target:ident}",
            description="Calculates voltage using Ohm's Law (V = I * R)",
        ),
        VerbSpec(
            pattern="decode resistor colors {colors:expr} into {target:ident}",
            description="Decodes 4-band or 5-band EIA resistor color codes",
        ),
        VerbSpec(
            pattern="evaluate logic truth table for {expr:expr} into {target:ident}",
            description="Evaluates boolean logic truth table over all variable permutations",
        ),
        VerbSpec(
            pattern="calculate pwm duty cycle for high time {ht:expr} and period {p:expr} into {target:ident}",
            description="Calculates PWM duty cycle percentage",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("calculate voltage with current ")
            or s.startswith("calculate current with voltage ")
            or s.startswith("calculate resistance with voltage ")
            or s.startswith("calculate power with voltage ")
            or s.startswith("decode resistor colors ")
            or s.startswith("decode resistor color ")
            or s.startswith("calculate voltage divider ")
            or s.startswith("calculate 555 timer frequency ")
            or s.startswith("calculate rc time constant ")
            or s.startswith("evaluate logic truth table ")
            or s.startswith("calculate pwm duty cycle ")
            or s.startswith("set gpio pin ")
            or s.startswith("read gpio pin ")
            or s.startswith("solve diode circuit ")
            or s.startswith("analyze transmission line ")
            or s.startswith("simulate rlc step response ")
            or s.startswith("design sallen key filter ")
            or s.startswith("solve rlc laplace transient ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


CIRCUIT_DOMAIN = CircuitDomain()
get_domain_registry().register(CIRCUIT_DOMAIN)

__all__ = [
    "CircuitDomain",
    "CIRCUIT_DOMAIN",
    "CircuitRuntime",
    "CircuitBoard",
    "CircuitDomainParser",
    "CircuitASTExporter",
    "circuit_ohm_voltage",
    "circuit_ohm_current",
    "circuit_ohm_resistance",
    "circuit_power",
    "circuit_decode_resistor_bands",
    "circuit_voltage_divider",
    "circuit_555_timer_freq",
    "circuit_rc_time_constant",
    "circuit_evaluate_truth_table",
    "circuit_pwm_duty_cycle",
    "circuit_gpio_set",
    "circuit_gpio_read",
    "ModifiedNodalAnalysis",
    "BodePlotAnalyzer",
    "OpAmpModel",
    "circuit_mna_dc_solve",
    "circuit_bode_plot",
    "circuit_opamp_amplify",
    "NonlinearDiodeSolver",
    "TransmissionLineRLGC",
    "StateSpaceRLCSimulator",
    "circuit_solve_diode",
    "circuit_transmission_line",
    "circuit_simulate_rlc_step",
    "ActiveSallenKeyFilterDesigner",
    "RLCTransientLaplaceSolver",
    "circuit_design_sallen_key",
    "circuit_rlc_laplace_transient",
]
