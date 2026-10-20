"""Chemistry, Molecular Graphs & Reaction Stoichiometry Domain Pack for DoomScript.

Enables native spoken-English molecular mass calculation, SMILES graph parsing,
and stoichiometric reaction balancing via 'use chem'.
"""

from typing import List, Optional, Dict, Any
from doomscript.domains.base import (
    DomainContract,
    DomainRuntime,
    DomainIR,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.chem.runtime import (
    PERIODIC_TABLE,
    FormulaParser,
    Atom,
    Bond,
    MoleculeGraph,
    SMILESParser,
    ReactionBalancer,
    chem_molecular_weight,
    chem_elemental_composition,
    chem_parse_smiles,
    chem_balance_reaction,
    MolecularGraphLayout,
    MorganFingerprint,
    ReactionKineticsSimulator,
    chem_generate_layout,
    chem_morgan_fingerprint,
    chem_tanimoto_similarity,
    chem_simulate_kinetics,
)
from doomscript.domains.chem.parser import ChemDomainParser
from doomscript.domains.chem.exporter import ChemASTExporter


class ChemRuntime(DomainRuntime):
    """Runtime coordinator for chemistry routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


class ChemDomain(DomainContract):
    """Domain contract for Chemistry, Molecular Graphs & Reaction Balancing."""

    name = "chem"
    aliases = ["chemistry", "molecule", "reaction"]
    description = "Molecular formulas, atomic masses, SMILES topology, aromaticity, and stoichiometric reaction balancing"
    parser = ChemDomainParser()
    runtime = ChemRuntime()
    exporter = ChemASTExporter()
    capabilities = ["molecular_weight", "elemental_composition", "parse_smiles", "balance_reaction"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="calculate molecular weight of {formula:expr} into {target:ident}",
            description="Calculates molecular weight in g/mol from a chemical formula",
        ),
        VerbSpec(
            pattern="parse smiles {smiles:expr} into {target:ident}",
            description="Parses SMILES string into molecular graph topology and rings",
        ),
        VerbSpec(
            pattern="balance reaction {reactants:expr} -> {products:expr} into {target:ident}",
            description="Balances reaction coefficients using exact stoichiometric nullspace",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate molecular weight of ")
            or s.startswith("parse smiles ")
            or s.startswith("balance reaction ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


CHEM_DOMAIN = ChemDomain()
get_domain_registry().register(CHEM_DOMAIN)

__all__ = [
    "ChemDomain",
    "CHEM_DOMAIN",
    "ChemRuntime",
    "PERIODIC_TABLE",
    "FormulaParser",
    "Atom",
    "Bond",
    "MoleculeGraph",
    "SMILESParser",
    "ReactionBalancer",
    "chem_molecular_weight",
    "chem_elemental_composition",
    "chem_parse_smiles",
    "chem_balance_reaction",
    "MolecularGraphLayout",
    "MorganFingerprint",
    "ReactionKineticsSimulator",
    "chem_generate_layout",
    "chem_morgan_fingerprint",
    "chem_tanimoto_similarity",
    "chem_simulate_kinetics",
]
