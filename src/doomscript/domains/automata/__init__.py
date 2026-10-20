"""Formal Automata & Computation Theory Domain Pack for DoomScript.

Enables native spoken-English DFA execution, Hopcroft state minimization, Thompson regex compilation,
and Turing Machines via 'use automata'.
"""

from typing import List, Optional, Dict, Any
from doomscript.domains.base import (
    DomainContract,
    DomainRuntime,
    DomainIR,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.automata.runtime import (
    DFA,
    NFA,
    ThompsonRegex,
    TuringMachine,
    PushdownAutomaton,
    MooreMealyFSM,
    BuchiAutomaton,
    automata_create_dfa,
    automata_dfa_accepts,
    automata_minimize_dfa,
    automata_regex_to_dfa,
    automata_run_turing_machine,
    automata_create_pda,
    automata_pda_accepts,
    automata_create_moore_fsm,
    automata_create_mealy_fsm,
    automata_run_fsm,
    automata_create_buchi,
    automata_buchi_accepts_cycle,
    CellularAutomata1D,
    GameOfLife2D,
    automata_simulate_rule,
    automata_simulate_life,
    MultiTapeTuringMachineSimulator,
    ContextFreeGrammarCYKParser,
    automata_run_multitape_tm,
    automata_cyk_parse,
)
from doomscript.domains.automata.parser import AutomataDomainParser
from doomscript.domains.automata.exporter import AutomataASTExporter


class AutomataRuntime(DomainRuntime):
    """Runtime coordinator for automata routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


class AutomataDomain(DomainContract):
    """Domain contract for Formal Automata & Computation Theory."""

    name = "automata"
    aliases = ["dfa", "nfa", "turing", "fsm", "regex"]
    description = "Deterministic/Nondeterministic finite automata, Hopcroft state minimization, regex-to-DFA, and Turing machines"
    parser = AutomataDomainParser()
    runtime = AutomataRuntime()
    exporter = AutomataASTExporter()
    capabilities = ["dfa", "nfa", "minimize", "regex", "turing"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="compile regex {regex:expr} to dfa into {target:ident}",
            description="Compiles regular expression into a minimized DFA",
        ),
        VerbSpec(
            pattern="minimize dfa {dfa:expr} into {target:ident}",
            description="Minimizes DFA states using Hopcroft's algorithm",
        ),
        VerbSpec(
            pattern="check if dfa {dfa:expr} accepts {input_str:expr} into {target:ident}",
            description="Evaluates whether DFA accepts the input sequence",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("compile regex ")
            or s.startswith("minimize dfa ")
            or s.startswith("check if dfa ")
            or s.startswith("simulate cellular rule ")
            or s.startswith("simulate game of life ")
            or s.startswith("simulate multitape turing machine ")
            or s.startswith("parse cyk grammar ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


AUTOMATA_DOMAIN = AutomataDomain()
get_domain_registry().register(AUTOMATA_DOMAIN)

__all__ = [
    "AutomataDomain",
    "AUTOMATA_DOMAIN",
    "AutomataRuntime",
    "DFA",
    "NFA",
    "ThompsonRegex",
    "TuringMachine",
    "PushdownAutomaton",
    "MooreMealyFSM",
    "BuchiAutomaton",
    "CellularAutomata1D",
    "GameOfLife2D",
    "automata_create_dfa",
    "automata_dfa_accepts",
    "automata_minimize_dfa",
    "automata_regex_to_dfa",
    "automata_run_turing_machine",
    "automata_create_pda",
    "automata_pda_accepts",
    "automata_create_moore_fsm",
    "automata_create_mealy_fsm",
    "automata_run_fsm",
    "automata_create_buchi",
    "automata_buchi_accepts_cycle",
    "automata_simulate_rule",
    "automata_simulate_life",
    "MultiTapeTuringMachineSimulator",
    "ContextFreeGrammarCYKParser",
    "automata_run_multitape_tm",
    "automata_cyk_parse",
]
