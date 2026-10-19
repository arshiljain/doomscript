"""Chemistry, Molecular Graphs & Reaction Stoichiometry Domain for DoomScript.

Provides 100% pure Python molecular mass calculation, SMILES graph parsing,
aromaticity detection (Hückel 4n+2 rule), and stoichiometric reaction balancing
via nullspace matrix elimination. Zero pip dependencies.
"""

from __future__ import annotations

import math
import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Set, Tuple, Union


# Standard Atomic Weights (IUPAC standard values)
PERIODIC_TABLE: Dict[str, float] = {
    "H": 1.008, "He": 4.0026, "Li": 6.94, "Be": 9.0122, "B": 10.81,
    "C": 12.011, "N": 14.007, "O": 15.999, "F": 18.998, "Ne": 20.180,
    "Na": 22.990, "Mg": 24.305, "Al": 26.982, "Si": 28.085, "P": 30.974,
    "S": 32.06, "Cl": 35.45, "Ar": 39.948, "K": 39.098, "Ca": 40.078,
    "Sc": 44.956, "Ti": 47.867, "V": 50.942, "Cr": 51.996, "Mn": 54.938,
    "Fe": 55.845, "Co": 58.933, "Ni": 58.693, "Cu": 63.546, "Zn": 65.38,
    "Ga": 69.723, "Ge": 72.630, "As": 74.922, "Se": 78.971, "Br": 79.904,
    "Kr": 83.798, "Rb": 85.468, "Sr": 87.62, "Y": 88.906, "Zr": 91.224,
    "Nb": 92.906, "Mo": 95.95, "Tc": 98.0, "Ru": 101.07, "Rh": 102.91,
    "Pd": 106.42, "Ag": 107.87, "Cd": 112.41, "In": 114.82, "Sn": 118.71,
    "Sb": 121.76, "Te": 127.60, "I": 126.90, "Xe": 131.29, "Cs": 132.91,
    "Ba": 137.33, "La": 138.91, "Ce": 140.12, "Pr": 140.91, "Nd": 144.24,
    "W": 183.84, "Pt": 195.08, "Au": 196.97, "Hg": 200.59, "Pb": 207.2,
    "Bi": 208.98, "Th": 232.04, "U": 238.03,
}


class FormulaParser:
    """Parses chemical formulas with nested brackets, parentheses, and hydrates."""

    @staticmethod
    def parse(formula: str) -> Dict[str, int]:
        """Parses a chemical formula string into a dict of {Element: count}.
        
        Handles parentheses like Ca(OH)2, brackets [Cu(NH3)4]SO4, and hydrates like CuSO4*5H2O.
        """
        formula = formula.strip()
        if not formula:
            return {}

        # Handle hydrates separated by * or .
        if "*" in formula or "." in formula:
            parts = re.split(r"[\*\.]", formula)
            main_part = parts[0]
            total_counts = FormulaParser.parse(main_part)
            for part in parts[1:]:
                m = re.match(r"^(\d+)?(.*)$", part)
                if m:
                    mult = int(m.group(1)) if m.group(1) else 1
                    sub_counts = FormulaParser.parse(m.group(2))
                    for el, count in sub_counts.items():
                        total_counts[el] = total_counts.get(el, 0) + count * mult
            return total_counts

        tokens = FormulaParser._tokenize(formula)
        counts, _ = FormulaParser._parse_group(tokens, 0)
        return counts

    @staticmethod
    def _tokenize(s: str) -> List[str]:
        token_spec = [
            ("LPAREN", r"[\(\[\{]"),
            ("RPAREN", r"[\)\]\}]"),
            ("ELEMENT", r"[A-Z][a-z]?"),
            ("NUMBER", r"\d+"),
            ("SKIP", r"\s+"),
        ]
        tok_regex = "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in token_spec)
        tokens = []
        for mo in re.finditer(tok_regex, s):
            kind = mo.lastgroup
            val = mo.group()
            if kind != "SKIP":
                tokens.append((kind, val))
        return tokens

    @staticmethod
    def _parse_group(tokens: List[Tuple[str, str]], idx: int) -> Tuple[Dict[str, int], int]:
        counts: Dict[str, int] = {}
        n = len(tokens)

        while idx < n:
            kind, val = tokens[idx]
            if kind == "LPAREN":
                sub_counts, idx = FormulaParser._parse_group(tokens, idx + 1)
                mult = 1
                if idx < n and tokens[idx][0] == "NUMBER":
                    mult = int(tokens[idx][1])
                    idx += 1
                for el, cnt in sub_counts.items():
                    counts[el] = counts.get(el, 0) + cnt * mult
            elif kind == "RPAREN":
                return counts, idx + 1
            elif kind == "ELEMENT":
                el = val
                idx += 1
                cnt = 1
                if idx < n and tokens[idx][0] == "NUMBER":
                    cnt = int(tokens[idx][1])
                    idx += 1
                counts[el] = counts.get(el, 0) + cnt
            else:
                idx += 1

        return counts, idx

    @staticmethod
    def molecular_weight(formula: str) -> float:
        """Calculates molecular weight in g/mol from a formula."""
        counts = FormulaParser.parse(formula)
        total_mw = 0.0
        for el, cnt in counts.items():
            if el not in PERIODIC_TABLE:
                raise ValueError(f"Unknown chemical element '{el}' in formula '{formula}'")
            total_mw += PERIODIC_TABLE[el] * cnt
        return round(total_mw, 4)

    @staticmethod
    def mass_composition(formula: str) -> Dict[str, float]:
        """Calculates percentage composition by mass for each element."""
        counts = FormulaParser.parse(formula)
        mw = FormulaParser.molecular_weight(formula)
        if mw == 0:
            return {}
        return {
            el: round((PERIODIC_TABLE[el] * cnt / mw) * 100.0, 3)
            for el, cnt in counts.items()
        }


class Atom:
    """Represents an atom in a molecular graph."""

    def __init__(self, atom_id: int, symbol: str, is_aromatic: bool = False, charge: int = 0):
        self.atom_id = atom_id
        self.symbol = symbol.capitalize()
        self.is_aromatic = is_aromatic
        self.charge = charge
        self.neighbors: List[int] = []

    def __repr__(self) -> str:
        arom = ":" if self.is_aromatic else ""
        return f"Atom({self.atom_id}, '{arom}{self.symbol}', charge={self.charge})"


class Bond:
    """Represents a chemical bond between two atoms."""

    def __init__(self, u: int, v: int, order: float = 1.0):
        self.u = min(u, v)
        self.v = max(u, v)
        self.order = order  # 1.0 = single, 2.0 = double, 3.0 = triple, 1.5 = aromatic

    def __repr__(self) -> str:
        return f"Bond({self.u}-{self.v}, order={self.order})"


class MoleculeGraph:
    """Graph structure representing chemical connectivity and topology."""

    def __init__(self):
        self.atoms: Dict[int, Atom] = {}
        self.bonds: List[Bond] = []

    def add_atom(self, symbol: str, is_aromatic: bool = False, charge: int = 0) -> int:
        atom_id = len(self.atoms)
        self.atoms[atom_id] = Atom(atom_id, symbol, is_aromatic, charge)
        return atom_id

    def add_bond(self, u: int, v: int, order: float = 1.0) -> None:
        if u not in self.atoms or v not in self.atoms:
            raise IndexError("Atom IDs out of range")
        self.bonds.append(Bond(u, v, order))
        self.atoms[u].neighbors.append(v)
        self.atoms[v].neighbors.append(u)

    def find_rings(self) -> List[List[int]]:
        """Finds elementary cycles (rings) in the molecular graph."""
        rings: List[List[int]] = []
        visited = set()

        def dfs(u: int, parent: Optional[int], path: List[int]):
            visited.add(u)
            path.append(u)
            for v in self.atoms[u].neighbors:
                if v == parent:
                    continue
                if v in path:
                    idx = path.index(v)
                    cycle = path[idx:]
                    if len(cycle) >= 3:
                        cycle_sorted = sorted(cycle)
                        if cycle_sorted not in [sorted(r) for r in rings]:
                            rings.append(cycle)
                elif v not in visited:
                    dfs(v, u, path)
            path.pop()

        for atom_id in self.atoms:
            if atom_id not in visited:
                dfs(atom_id, None, [])

        return rings

    def check_aromaticity(self) -> List[Dict[str, Any]]:
        """Applies Hückel's 4n+2 rule to all identified cyclic subgraphs."""
        rings = self.find_rings()
        results = []
        for ring in rings:
            pi_electrons = 0
            is_planar_candidate = True
            for atom_id in ring:
                atom = self.atoms[atom_id]
                sym = atom.symbol
                # Count pi-electrons contributed to aromatic conjugated system
                if sym == "C":
                    pi_electrons += 1
                elif sym == "N":
                    # Pyridine-type N contributes 1, pyrrole-type N contributes 2
                    deg = len(atom.neighbors)
                    pi_electrons += 2 if deg == 3 else 1
                elif sym in ("O", "S"):
                    # Furan/Thiophene heteroatoms contribute 2 pi electrons (lone pair)
                    pi_electrons += 2
                else:
                    is_planar_candidate = False

            # Hückel's rule: 4n + 2
            is_aromatic = False
            if is_planar_candidate and pi_electrons >= 2:
                n = (pi_electrons - 2) / 4.0
                if n.is_integer() and n >= 0:
                    is_aromatic = True

            results.append({
                "ring_atoms": ring,
                "size": len(ring),
                "pi_electrons": pi_electrons,
                "is_aromatic": is_aromatic,
            })
        return results


class SMILESParser:
    """Simplified SMILES (Simplified Molecular Input Line Entry System) parser."""

    @staticmethod
    def parse(smiles: str) -> MoleculeGraph:
        graph = MoleculeGraph()
        stack: List[int] = []
        ring_closures: Dict[str, Tuple[int, float]] = {}
        current_atom: Optional[int] = None
        current_bond_order = 1.0

        i = 0
        n = len(smiles)

        while i < n:
            ch = smiles[i]

            if ch == "(":
                if current_atom is not None:
                    stack.append(current_atom)
                i += 1
            elif ch == ")":
                if stack:
                    current_atom = stack.pop()
                i += 1
            elif ch == "=":
                current_bond_order = 2.0
                i += 1
            elif ch == "#":
                current_bond_order = 3.0
                i += 1
            elif ch in "0123456789":
                # Ring closure digit
                ring_id = ch
                if ring_id in ring_closures:
                    prev_atom, b_order = ring_closures.pop(ring_id)
                    order = max(b_order, current_bond_order)
                    graph.add_bond(prev_atom, current_atom, order)
                    current_bond_order = 1.0
                else:
                    ring_closures[ring_id] = (current_atom, current_bond_order)
                    current_bond_order = 1.0
                i += 1
            elif ch == "[":
                # Bracketed atom e.g. [NH4+]
                end_idx = smiles.find("]", i)
                if end_idx == -1:
                    raise ValueError(f"Unclosed bracket at index {i} in SMILES")
                content = smiles[i + 1 : end_idx]
                m = re.match(r"^([A-Z][a-z]?)([\+\-]\d*)?$", content)
                if not m:
                    raise ValueError(f"Cannot parse bracket atom: {content}")
                sym = m.group(1)
                chg_str = m.group(2)
                chg = 0
                if chg_str:
                    if chg_str == "+":
                        chg = 1
                    elif chg_str == "-":
                        chg = -1
                    else:
                        chg = int(chg_str)
                new_atom = graph.add_atom(sym, is_aromatic=False, charge=chg)
                if current_atom is not None:
                    graph.add_bond(current_atom, new_atom, current_bond_order)
                    current_bond_order = 1.0
                current_atom = new_atom
                i = end_idx + 1
            elif ch.isalpha():
                # Element symbol or aromatic lowercase
                is_arom = ch.islower()
                sym = ch.upper()
                # Check for 2-letter elements (Cl, Br)
                if i + 1 < n and smiles[i : i + 2] in ("Cl", "Br"):
                    sym = smiles[i : i + 2]
                    i += 1
                new_atom = graph.add_atom(sym, is_aromatic=is_arom)
                if current_atom is not None:
                    order = 1.5 if (is_arom and graph.atoms[current_atom].is_aromatic) else current_bond_order
                    graph.add_bond(current_atom, new_atom, order)
                    current_bond_order = 1.0
                current_atom = new_atom
                i += 1
            else:
                i += 1

        return graph


class ReactionBalancer:
    """Balances chemical reaction stoichiometry using exact rational nullspace computation."""

    @staticmethod
    def balance(reactants: List[str], products: List[str]) -> Dict[str, Any]:
        """Calculates smallest positive integer coefficients for reaction:
        reactants -> products.
        """
        all_compounds = list(reactants) + list(products)
        num_reactants = len(reactants)
        num_compounds = len(all_compounds)

        # Collect all unique elements
        compound_compositions = [FormulaParser.parse(c) for c in all_compounds]
        elements = sorted(list({el for comp in compound_compositions for el in comp}))

        # Construct conservation matrix A: rows = elements, cols = compounds
        # Reactants have positive sign, products have negative sign: sum(a_ij * c_j) = 0
        matrix: List[List[Fraction]] = []
        for el in elements:
            row: List[Fraction] = []
            for j, comp in enumerate(compound_compositions):
                cnt = comp.get(el, 0)
                sign = 1 if j < num_reactants else -1
                row.append(Fraction(sign * cnt))
            matrix.append(row)

        # Solve Ax = 0 for nullspace using Gaussian Elimination (RREF)
        null_vector = ReactionBalancer._find_nullspace_vector(matrix, num_compounds)
        if not null_vector:
            raise ValueError("Could not balance chemical equation (independent or trivial system)")

        # Convert rational vector to minimal positive integers
        # Find LCM of denominators
        denominators = [frac.denominator for frac in null_vector]
        lcm_val = 1
        for d in denominators:
            lcm_val = (lcm_val * d) // math.gcd(lcm_val, d)

        int_coeffs = [int(frac * lcm_val) for frac in null_vector]

        # Check all positive
        if any(c <= 0 for c in int_coeffs):
            # Invert signs if all negative
            if all(c < 0 for c in int_coeffs):
                int_coeffs = [-c for c in int_coeffs]
            else:
                raise ValueError("Reaction has no strictly positive stoichiometric solution")

        # Reduce by GCD of all coefficients
        common_gcd = int_coeffs[0]
        for c in int_coeffs[1:]:
            common_gcd = math.gcd(common_gcd, c)
        final_coeffs = [c // common_gcd for c in int_coeffs]

        reactant_map = {reactants[i]: final_coeffs[i] for i in range(len(reactants))}
        product_map = {products[i]: final_coeffs[len(reactants) + i] for i in range(len(products))}

        lhs = " + ".join(f"{reactant_map[r]} {r}" if reactant_map[r] > 1 else r for r in reactants)
        rhs = " + ".join(f"{product_map[p]} {p}" if product_map[p] > 1 else p for p in products)
        equation = f"{lhs} -> {rhs}"

        return {
            "reactants": reactant_map,
            "products": product_map,
            "equation": equation,
        }

    @staticmethod
    def _find_nullspace_vector(matrix: List[List[Fraction]], num_cols: int) -> Optional[List[Fraction]]:
        rows = len(matrix)
        cols = num_cols

        # Gaussian Elimination over Fractions
        r = 0
        pivot_cols = []
        for c in range(cols):
            if r >= rows:
                break
            # Find non-zero pivot
            pivot_row = None
            for i in range(r, rows):
                if matrix[i][c] != 0:
                    pivot_row = i
                    break
            if pivot_row is None:
                continue

            matrix[r], matrix[pivot_row] = matrix[pivot_row], matrix[r]
            pivot_val = matrix[r][c]
            matrix[r] = [val / pivot_val for val in matrix[r]]

            for i in range(rows):
                if i != r and matrix[i][c] != 0:
                    factor = matrix[i][c]
                    matrix[i] = [matrix[i][k] - factor * matrix[r][k] for k in range(cols)]

            pivot_cols.append(c)
            r += 1

        free_cols = [c for c in range(cols) if c not in pivot_cols]
        if not free_cols:
            return None

        # Pick the last free variable and set it to 1
        free_var = free_cols[-1]
        x = [Fraction(0)] * cols
        x[free_var] = Fraction(1)

        for i, p_col in enumerate(pivot_cols):
            x[p_col] = -matrix[i][free_var]

        return x


# --- Public High-Level Runtime Functions for DoomScript ---

def chem_molecular_weight(formula: str) -> float:
    """Calculates molecular weight of a chemical formula."""
    return FormulaParser.molecular_weight(formula)


def chem_elemental_composition(formula: str) -> Dict[str, float]:
    """Calculates percentage mass composition for each element."""
    return FormulaParser.mass_composition(formula)


def chem_parse_smiles(smiles: str) -> Dict[str, Any]:
    """Parses a SMILES string into atom-bond connectivity and aromatic ring analysis."""
    g = SMILESParser.parse(smiles)
    rings = g.check_aromaticity()
    return {
        "num_atoms": len(g.atoms),
        "num_bonds": len(g.bonds),
        "atoms": [{"id": a.atom_id, "symbol": a.symbol, "aromatic": a.is_aromatic} for a in g.atoms.values()],
        "bonds": [{"u": b.u, "v": b.v, "order": b.order} for b in g.bonds],
        "rings": rings,
    }


def chem_balance_reaction(reactants: List[str], products: List[str]) -> Dict[str, Any]:
    """Balances a chemical reaction using exact stoichiometric nullspace."""
    return ReactionBalancer.balance(reactants, products)
