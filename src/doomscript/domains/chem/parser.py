"""Chemistry Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class ChemDomainParser(DomainParser):
    """Parses spoken-English chemistry statements, molecular formulas, and reaction balancing."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate molecular weight of <formula> into <target>
        m_mw = re.match(
            r"^calculate\s+molecular\s+weight\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mw:
            formula, target = m_mw.group(1).strip(), m_mw.group(2).strip()
            # If formula is not quoted, quote it
            if not (formula.startswith('"') or formula.startswith("'")):
                formula = f'"{formula}"'
            return f"set {target} to chem_molecular_weight({formula})"

        # parse smiles <smiles> into <target>
        m_smiles = re.match(
            r"^parse\s+smiles\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_smiles:
            smiles, target = m_smiles.group(1).strip(), m_smiles.group(2).strip()
            if not (smiles.startswith('"') or smiles.startswith("'")):
                smiles = f'"{smiles}"'
            return f"set {target} to chem_parse_smiles({smiles})"

        # balance reaction <reactants> -> <products> into <target>
        m_rxn = re.match(
            r"^balance\s+reaction\s+(.+?)\s*->\s*(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rxn:
            reactants_raw, products_raw, target = m_rxn.group(1).strip(), m_rxn.group(2).strip(), m_rxn.group(3).strip()
            # If formatted like [A, B], keep as python list expression, or split by '+'
            if reactants_raw.startswith("[") and reactants_raw.endswith("]"):
                r_expr = reactants_raw
            else:
                r_parts = [f'"{p.strip()}"' for p in reactants_raw.split("+")]
                r_expr = f"[{', '.join(r_parts)}]"

            if products_raw.startswith("[") and products_raw.endswith("]"):
                p_expr = products_raw
            else:
                p_parts = [f'"{p.strip()}"' for p in products_raw.split("+")]
                p_expr = f"[{', '.join(p_parts)}]"

            return f"set {target} to chem_balance_reaction({r_expr}, {p_expr})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Chemistry domain does not define declarative blocks")
