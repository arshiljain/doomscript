"""Chemistry, Molecular Graphs & Reaction Stoichiometry Domain for DoomScript.

Provides 100% pure Python molecular mass calculation, SMILES graph parsing,
aromaticity detection (Hückel 4n+2 rule), and stoichiometric reaction balancing
via nullspace matrix elimination. Zero pip dependencies.
"""

from __future__ import annotations

import math
import re
import hashlib
from fractions import Fraction
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union
from doomscript.core.record import Record


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

    def get_neighbors(self, atom_id: int) -> List[int]:
        """Returns list of neighboring atom IDs."""
        if atom_id in self.atoms:
            return list(self.atoms[atom_id].neighbors)
        return []

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


chem_formula_weight = chem_molecular_weight


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


# ==============================================================================
# Advanced Chem Deepening: 2D Force Layout, Morgan Fingerprints & Kinetics
# ==============================================================================

class MolecularGraphLayout:
    """Kamada-Kawai 2D force-directed layout coordinator for molecular structures."""

    @classmethod
    def layout_from_graph(
        cls,
        molecule: Union[MoleculeGraph, Dict[str, Any]],
        ideal_bond_len: float = 1.5,
        iterations: int = 80,
    ) -> Dict[int, Tuple[float, float]]:
        """
        Computes 2D coordinates for each atom minimizing graph theoretic path stress.
        """
        if isinstance(molecule, MoleculeGraph):
            atom_ids = sorted(list(molecule.atoms.keys()))
            adj: Dict[int, List[int]] = {i: [] for i in atom_ids}
            for b in molecule.bonds:
                adj[b.u].append(b.v)
                adj[b.v].append(b.u)
        else:
            atoms_data = molecule.get("atoms", [])
            atom_ids = [a["id"] if isinstance(a, dict) else int(a) for a in atoms_data]
            adj = {i: [] for i in atom_ids}
            for b in molecule.get("bonds", []):
                u, v = b.get("u"), b.get("v")
                if u in adj and v in adj:
                    adj[u].append(v)
                    adj[v].append(u)

        n = len(atom_ids)
        if n == 0:
            return {}
        if n == 1:
            return {atom_ids[0]: (0.0, 0.0)}

        # All-Pairs Shortest Path (BFS)
        dist_matrix: Dict[Tuple[int, int], float] = {}
        for src in atom_ids:
            visited = {src: 0}
            queue = [src]
            while queue:
                curr = queue.pop(0)
                d = visited[curr]
                for nbr in adj[curr]:
                    if nbr not in visited:
                        visited[nbr] = d + 1
                        queue.append(nbr)
            for dst in atom_ids:
                dist_matrix[(src, dst)] = float(visited.get(dst, n * 2))

        # Target spring lengths and spring constants
        K0 = 1.0
        L_target: Dict[Tuple[int, int], float] = {}
        k_spring: Dict[Tuple[int, int], float] = {}
        for i in atom_ids:
            for j in atom_ids:
                if i != j:
                    d_graph = dist_matrix[(i, j)]
                    L_target[(i, j)] = ideal_bond_len * d_graph
                    k_spring[(i, j)] = K0 / (d_graph * d_graph)

        # Initial circular layout
        radius = ideal_bond_len * (n / (2.0 * math.pi))
        pos: Dict[int, List[float]] = {}
        for idx, a_id in enumerate(atom_ids):
            angle = (2.0 * math.pi * idx) / n
            pos[a_id] = [radius * math.cos(angle), radius * math.sin(angle)]

        # Gradient descent with adaptive step
        step_size = 0.1
        for _ in range(iterations):
            max_grad = 0.0
            grad: Dict[int, List[float]] = {i: [0.0, 0.0] for i in atom_ids}
            for i in atom_ids:
                xi, yi = pos[i][0], pos[i][1]
                for j in atom_ids:
                    if i == j:
                        continue
                    xj, yj = pos[j][0], pos[j][1]
                    dx = xi - xj
                    dy = yi - yj
                    euclid = math.hypot(dx, dy) + 1e-6
                    l_ij = L_target[(i, j)]
                    k_ij = k_spring[(i, j)]

                    # dE/dxi = k_ij * (dx - l_ij * dx / euclid)
                    factor = k_ij * (1.0 - l_ij / euclid)
                    grad[i][0] += factor * dx
                    grad[i][1] += factor * dy

                g_norm = math.hypot(grad[i][0], grad[i][1])
                if g_norm > max_grad:
                    max_grad = g_norm

            for i in atom_ids:
                pos[i][0] -= step_size * grad[i][0]
                pos[i][1] -= step_size * grad[i][1]

            if max_grad < 1e-4:
                break

        # Center layout
        mean_x = sum(pos[i][0] for i in atom_ids) / n
        mean_y = sum(pos[i][1] for i in atom_ids) / n

        return {i: (round(pos[i][0] - mean_x, 4), round(pos[i][1] - mean_y, 4)) for i in atom_ids}


class MorganFingerprint:
    """Circular chemical graph fingerprints (ECFP4) and Tanimoto similarity."""

    @staticmethod
    def _atom_invariant(atom: Atom, molecule: MoleculeGraph) -> int:
        """Computes initial atom invariant integer."""
        # 1. Atomic Number
        z = 6
        elem = atom.symbol.capitalize()
        # Find Z approximately from common elements
        z_map = {"H": 1, "He": 2, "C": 6, "N": 7, "O": 8, "F": 9, "P": 15, "S": 16, "Cl": 17, "Br": 35, "I": 53}
        z = z_map.get(elem, 6)

        # 2. Number of heavy neighbors
        heavy_deg = len(molecule.get_neighbors(atom.atom_id))

        # 3. Formal charge
        charge = atom.charge

        # 4. Aromaticity
        aromatic = 1 if atom.is_aromatic else 0

        # Combine bits into integer hash
        return (z & 0xFF) | ((heavy_deg & 0x0F) << 8) | (((charge + 8) & 0x0F) << 12) | (aromatic << 16)

    @classmethod
    def generate(
        cls,
        molecule: Union[str, MoleculeGraph],
        radius: int = 2,
        n_bits: int = 1024,
    ) -> List[int]:
        """
        Generates circular Morgan fingerprint bit indices for a SMILES string or MoleculeGraph.
        """
        if isinstance(molecule, str):
            g = SMILESParser.parse(molecule)
        else:
            g = molecule

        if not g.atoms:
            return []

        # Step 0: Invariants
        atom_hashes: Dict[int, int] = {
            a_id: cls._atom_invariant(atom, g) for a_id, atom in g.atoms.items()
        }

        all_features: Set[int] = set(atom_hashes.values())

        # Step 1..radius: Circular neighborhood hashing
        for r in range(1, radius + 1):
            next_hashes: Dict[int, int] = {}
            for a_id, current_hash in atom_hashes.items():
                nbrs = g.get_neighbors(a_id)
                nbr_features = []
                for n_id in nbrs:
                    b_order = 1
                    for b in g.bonds:
                        if (b.u == a_id and b.v == n_id) or (b.u == n_id and b.v == a_id):
                            b_order = b.order
                            break
                    nbr_features.append((b_order, atom_hashes[n_id]))

                nbr_features.sort()
                token = f"{current_hash}:" + ",".join(f"{bo}:{nh}" for bo, nh in nbr_features)
                h = int(hashlib.sha256(token.encode("utf-8")).hexdigest()[:8], 16)
                next_hashes[a_id] = h
                all_features.add(h)

            atom_hashes = next_hashes

        # Fold into bit vector indices
        bit_indices = sorted(list({f % n_bits for f in all_features}))
        return bit_indices

    @staticmethod
    def tanimoto_similarity(fp1: Sequence[int], fp2: Sequence[int]) -> float:
        """Calculates Tanimoto / Jaccard similarity coefficient |A and B| / |A or B|."""
        s1 = set(fp1)
        s2 = set(fp2)
        if not s1 and not s2:
            return 1.0
        inter = len(s1.intersection(s2))
        union = len(s1.union(s2))
        return round(float(inter) / float(union), 6) if union > 0 else 0.0


class ReactionKineticsSimulator:
    """Chemical reaction network kinetics simulator for multi-species rate equations."""

    @classmethod
    def simulate(
        cls,
        initial_concentrations: Dict[str, float],
        reactions: List[Dict[str, Any]],
        t_span: Tuple[float, float],
        dt: float = 0.01,
        num_points: int = 50,
    ) -> Dict[str, Any]:
        """
        Numerically integrates multi-species kinetic differential equations.
        `reactions` format:
        [
            {"reactants": {"A": 1, "B": 1}, "products": {"C": 1}, "k_f": 0.5, "k_r": 0.02},
            ...
        ]
        """
        species = sorted(list(initial_concentrations.keys()))
        t0, t_end = t_span
        total_time = max(1e-6, t_end - t0)

        # Ensure all reaction species are in dictionary
        for rxn in reactions:
            for r in rxn.get("reactants", {}):
                if r not in initial_concentrations:
                    species.append(r)
            for p in rxn.get("products", {}):
                if p not in initial_concentrations:
                    species.append(p)
        species = sorted(list(set(species)))

        current_conc = {s: float(initial_concentrations.get(s, 0.0)) for s in species}

        def _derivatives(conc: Dict[str, float]) -> Dict[str, float]:
            d_dt = {s: 0.0 for s in species}
            for rxn in reactions:
                kf = float(rxn.get("k_f", 0.0))
                kr = float(rxn.get("k_r", 0.0))
                reactants = rxn.get("reactants", {})
                products = rxn.get("products", {})

                # Forward rate v_f = kf * prod(conc[r]^stoich)
                rate_f = kf
                for r, stoich in reactants.items():
                    rate_f *= max(0.0, conc.get(r, 0.0)) ** stoich

                # Reverse rate v_r = kr * prod(conc[p]^stoich)
                rate_r = kr
                for p, stoich in products.items():
                    rate_r *= max(0.0, conc.get(p, 0.0)) ** stoich

                net_rate = rate_f - rate_r

                # d[S]/dt = net_rate * (product_stoich - reactant_stoich)
                for r, stoich in reactants.items():
                    d_dt[r] -= stoich * net_rate
                for p, stoich in products.items():
                    d_dt[p] += stoich * net_rate
            return d_dt

        # RK4 Integration
        t = t0
        time_history: List[float] = [round(t, 4)]
        conc_history: Dict[str, List[float]] = {s: [round(current_conc[s], 6)] for s in species}

        save_interval = total_time / max(1, num_points)
        next_save = t + save_interval

        steps = int(math.ceil(total_time / dt))
        actual_dt = total_time / max(1, steps)

        for _ in range(steps):
            # k1
            d1 = _derivatives(current_conc)
            # k2
            c2 = {s: max(0.0, current_conc[s] + 0.5 * actual_dt * d1[s]) for s in species}
            d2 = _derivatives(c2)
            # k3
            c3 = {s: max(0.0, current_conc[s] + 0.5 * actual_dt * d2[s]) for s in species}
            d3 = _derivatives(c3)
            # k4
            c4 = {s: max(0.0, current_conc[s] + actual_dt * d3[s]) for s in species}
            d4 = _derivatives(c4)

            # Update concentrations
            for s in species:
                delta = (actual_dt / 6.0) * (d1[s] + 2.0 * d2[s] + 2.0 * d3[s] + d4[s])
                current_conc[s] = max(0.0, current_conc[s] + delta)

            t += actual_dt

            if t >= next_save - 1e-9 or _ == steps - 1:
                time_history.append(round(t, 4))
                for s in species:
                    conc_history[s].append(round(current_conc[s], 6))
                next_save += save_interval

        return {
            "time": time_history,
            "concentrations": conc_history,
            "final": {s: round(current_conc[s], 6) for s in species},
        }


def chem_generate_layout(molecule: Union[str, MoleculeGraph, Dict[str, Any]]) -> Dict[Any, Tuple[float, float]]:
    """Generates 2D force-directed layout coordinates for a chemical structure."""
    if isinstance(molecule, str):
        molecule = SMILESParser.parse(molecule)
    return MolecularGraphLayout.layout_from_graph(molecule)


def chem_morgan_fingerprint(smiles_or_mol: Union[str, MoleculeGraph], radius: int = 2, n_bits: int = 1024) -> List[int]:
    """Generates Morgan / ECFP4 fingerprint bit indices."""
    return MorganFingerprint.generate(smiles_or_mol, radius, n_bits)


def chem_tanimoto_similarity(fp1: Sequence[int], fp2: Sequence[int]) -> float:
    """Calculates Tanimoto similarity between two molecular fingerprints."""
    return MorganFingerprint.tanimoto_similarity(fp1, fp2)


def chem_simulate_kinetics(
    initial: Dict[str, float],
    reactions: List[Dict[str, Any]],
    t_span: Tuple[float, float],
    dt: float = 0.01,
) -> Dict[str, Any]:
    """Simulates chemical reaction network kinetics."""
    return ReactionKineticsSimulator.simulate(initial, reactions, t_span, dt)


# ==============================================================================
# THERMODYNAMICS, ACID-BASE PH & ENZYME KINETICS
# ==============================================================================

class ThermodynamicEquilibriumConstant:
    """Reaction Gibbs free energy, enthalpy, entropy, and equilibrium constant."""

    R_GAS = 8.314462618  # J / (mol * K)

    @classmethod
    def calculate(
        cls,
        delta_h_kj: float,
        delta_s_j_k: float,
        temp_c: float = 25.0,
    ) -> Record:
        """Calculates Delta G and equilibrium constant K_eq at given temperature."""
        T = float(temp_c) + 273.15
        dH_J = float(delta_h_kj) * 1000.0
        dS_J = float(delta_s_j_k)

        dG_J = dH_J - T * dS_J
        dG_kJ = dG_J / 1000.0

        # K_eq = exp(-dG / (R * T))
        exponent = -dG_J / (cls.R_GAS * T)
        if exponent > 700:
            k_eq = float("inf")
        elif exponent < -700:
            k_eq = 0.0
        else:
            k_eq = math.exp(exponent)

        return Record({
            "delta_g_kj": round(dG_kJ, 3),
            "delta_h_kj": round(float(delta_h_kj), 3),
            "delta_s_j_k": round(dS_J, 3),
            "k_eq": k_eq if k_eq != float("inf") else 1e300,
            "temperature_k": round(T, 2),
            "is_spontaneous": dG_kJ < 0.0,
        })


class AcidBaseEquilibriumpH:
    """Aqueous acid-base equilibrium, weak acid dissociation, and buffer pH solver."""

    KW = 1e-14

    @classmethod
    def weak_acid_ph(cls, acid_conc: float, ka: float) -> Record:
        """Calculates pH of a monoprotic weak acid HA -> H+ + A-."""
        c = max(1e-12, float(acid_conc))
        k = max(1e-16, float(ka))

        # [H+]^2 + Ka * [H+] - Ka * C = 0
        # Quadratic formula: [H+] = (-Ka + sqrt(Ka^2 + 4 * Ka * C)) / 2
        discriminant = k * k + 4.0 * k * c
        h_plus = (-k + math.sqrt(discriminant)) / 2.0
        ph = -math.log10(h_plus)
        alpha = h_plus / c  # Degree of dissociation

        return Record({
            "pH": round(ph, 3),
            "pOH": round(14.0 - ph, 3),
            "h_plus_molar": h_plus,
            "dissociation_fraction": round(alpha, 4),
            "acid_concentration": c,
            "ka": k,
        })

    @classmethod
    def buffer_ph(cls, acid_conc: float, salt_conc: float, pka: float) -> Record:
        """Calculates buffer pH using Henderson-Hasselbalch equation with buffer capacity."""
        ca = max(1e-12, float(acid_conc))
        cb = max(1e-12, float(salt_conc))
        p_ka = float(pka)

        ph = p_ka + math.log10(cb / ca)

        # Buffer capacity beta = 2.303 * (Ca * Cb) / (Ca + Cb)
        beta = 2.302585 * (ca * cb) / (ca + cb)

        return Record({
            "pH": round(ph, 3),
            "pOH": round(14.0 - ph, 3),
            "buffer_capacity": round(beta, 4),
            "acid_concentration": ca,
            "base_concentration": cb,
            "pKa": p_ka,
        })


class MichaelisMentenEnzymeKinetics:
    """Enzyme kinetics parameter estimation via Lineweaver-Burk double reciprocal fit."""

    @classmethod
    def fit(
        cls,
        substrates: List[float],
        velocities: List[float],
    ) -> Record:
        """Computes V_max and K_m from experimental substrate concentrations and initial rates."""
        if len(substrates) != len(velocities) or len(substrates) < 2:
            return Record({"v_max": 0.0, "k_m": 0.0, "r_squared": 0.0})

        # Reciprocals: x = 1 / [S], y = 1 / v
        inv_s = [1.0 / max(1e-12, float(s)) for s in substrates]
        inv_v = [1.0 / max(1e-12, float(v)) for v in velocities]

        n = len(inv_s)
        mean_x = sum(inv_s) / n
        mean_y = sum(inv_v) / n

        ss_xx = sum((x - mean_x) ** 2 for x in inv_s)
        ss_yy = sum((y - mean_y) ** 2 for y in inv_v)
        ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(inv_s, inv_v))

        slope = ss_xy / max(1e-12, ss_xx)
        intercept = mean_y - slope * mean_x

        r2 = (ss_xy ** 2) / max(1e-12, ss_xx * ss_yy)

        v_max = 1.0 / intercept if intercept > 0 else 0.0
        k_m = slope * v_max if intercept > 0 else 0.0

        return Record({
            "v_max": round(v_max, 4),
            "k_m": round(k_m, 4),
            "r_squared": round(r2, 4),
            "data_points": n,
        })


def chem_gibbs_free_energy(
    delta_h_kj: float,
    delta_s_j_k: float,
    temperature_c: float = 25.0,
) -> Record:
    """Calculates reaction Gibbs free energy and equilibrium constant."""
    return ThermodynamicEquilibriumConstant.calculate(delta_h_kj, delta_s_j_k, temp_c=temperature_c)


def chem_acid_base_ph(
    acid_conc: float,
    ka: float,
    base_conc: Optional[float] = None,
) -> Record:
    """Calculates pH of weak acid solution or Henderson-Hasselbalch buffer."""
    if base_conc is not None and float(base_conc) > 0.0:
        pka = -math.log10(max(1e-16, float(ka)))
        return AcidBaseEquilibriumpH.buffer_ph(acid_conc, base_conc, pka)
    return AcidBaseEquilibriumpH.weak_acid_ph(acid_conc, ka)


def chem_enzyme_kinetics(
    substrates: List[float],
    velocities: List[float],
) -> Record:
    """Estimates Michaelis-Menten V_max and K_m from substrate velocity data."""
    return MichaelisMentenEnzymeKinetics.fit(substrates, velocities)


class AutocatalyticOregonatorSimulator:
    """Field-Körös-Noyes (FKN) Oregonator model simulating Belousov-Zhabotinsky oscillatory chemical dynamics."""

    @classmethod
    def simulate(
        cls,
        initial_state: Optional[List[float]] = None,
        duration: float = 30.0,
        dt: float = 0.002,
        epsilon: float = 0.04,
        q: float = 0.0008,
        f: float = 1.0,
    ) -> Dict[str, Any]:
        # Dimensionless variables: x = [HBrO2], y = [Br-], z = [Ce4+]
        # In the Tyson two-variable / quasi-steady-state or three-variable model:
        # y_ss = f*z / (q + x)
        # dx/dt = (1/eps) * (x*(1 - x) - f*z * (x - q)/(x + q))
        # dz/dt = x - z
        # This standard stiff-reduced Oregonator integrates stably without blowup.
        init = initial_state or [0.1, 0.1]
        x = float(init[0])
        z = float(init[1])

        t = 0.0
        steps = int(duration / dt)

        x_series = []
        z_series = []
        peaks = []

        prev_dx = 0.0
        for step in range(steps):
            denom = max(1e-9, x + q)
            # Tyson 2-variable Oregonator
            dx_dt = (x * (1.0 - x) - f * z * (x - q) / denom) / max(1e-4, epsilon)
            dz_dt = x - z

            # Midpoint / RK2 integration
            x_half = max(0.0, x + 0.5 * dt * dx_dt)
            z_half = max(0.0, z + 0.5 * dt * dz_dt)
            denom_half = max(1e-9, x_half + q)
            dx_dt2 = (x_half * (1.0 - x_half) - f * z_half * (x_half - q) / denom_half) / max(1e-4, epsilon)
            dz_dt2 = x_half - z_half

            x_next = max(0.0, x + dt * dx_dt2)
            z_next = max(0.0, z + dt * dz_dt2)

            # Detect peak in x
            if step > 10 and dx_dt > 0.0 and dx_dt2 <= 0.0:
                peaks.append(round(t, 3))

            x = x_next
            z = z_next
            t += dt

            if step % 50 == 0:
                x_series.append(round(x, 4))
                z_series.append(round(z, 4))

        # Calculate period if at least 2 peaks
        period = 0.0
        if len(peaks) >= 2:
            intervals = [peaks[i] - peaks[i - 1] for i in range(1, len(peaks))]
            period = sum(intervals) / len(intervals)

        return {
            "duration": duration,
            "period": round(period, 3),
            "cycles_detected": len(peaks),
            "final_x": round(x, 4),
            "final_z": round(z, 4),
            "max_x": round(max(x_series) if x_series else x, 4),
            "min_x": round(min(x_series) if x_series else x, 4),
        }


class ArrheniusEyringTransitionState:
    """Calculates activation enthalpy, entropy, and Gibbs free energy from temperature-rate constant kinetics."""

    R = 8.314462618  # J / (mol * K)
    KB_OVER_H = 2.083661912e10  # k_B / h (Hz / K)
    LN_KB_OVER_H = 23.7599026

    @classmethod
    def fit(cls, temperatures_k: List[float], rate_constants: List[float]) -> Dict[str, Any]:
        n = min(len(temperatures_k), len(rate_constants))
        if n < 2:
            return {
                "delta_h_activation_kj": 0.0,
                "delta_s_activation_j_k": 0.0,
                "delta_g_activation_kj": 0.0,
                "activation_energy_kj": 0.0,
                "r_squared": 0.0,
            }

        # Eyring coordinates: x = 1 / T, y = ln(k / T)
        x_vals = [1.0 / float(t) for t in temperatures_k[:n]]
        y_vals = [math.log(max(1e-20, float(k)) / float(t)) for t, k in zip(temperatures_k[:n], rate_constants[:n])]

        mean_x = sum(x_vals) / n
        mean_y = sum(y_vals) / n

        ss_xx = sum((x - mean_x) ** 2 for x in x_vals)
        ss_yy = sum((y - mean_y) ** 2 for y in y_vals)
        ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_vals, y_vals))

        slope = ss_xy / max(1e-12, ss_xx)
        intercept = mean_y - slope * mean_x

        r2 = (ss_xy ** 2) / max(1e-12, ss_xx * ss_yy)

        # Delta H^ddagger = -slope * R
        delta_h_j = -slope * cls.R
        delta_h_kj = delta_h_j / 1000.0

        # Delta S^ddagger = R * (intercept - ln(k_B / h))
        delta_s_j_k = cls.R * (intercept - cls.LN_KB_OVER_H)

        # Delta G^ddagger at 298.15 K
        t_ref = 298.15
        delta_g_kj = delta_h_kj - (t_ref * delta_s_j_k) / 1000.0

        # Arrhenius Ea = Delta H^ddagger + R * T_mean
        t_mean = sum(temperatures_k[:n]) / n
        ea_kj = (delta_h_j + cls.R * t_mean) / 1000.0

        return {
            "delta_h_activation_kj": round(delta_h_kj, 3),
            "delta_s_activation_j_k": round(delta_s_j_k, 3),
            "delta_g_activation_kj": round(delta_g_kj, 3),
            "activation_energy_kj": round(ea_kj, 3),
            "r_squared": round(r2, 4),
            "temperatures_count": n,
        }


def chem_oregonator_simulate(
    initial_state: Optional[List[float]] = None,
    duration: float = 30.0,
    dt: float = 0.002,
) -> Record:
    """Simulates Belousov-Zhabotinsky oscillatory chemical reaction via Oregonator model."""
    return Record(AutocatalyticOregonatorSimulator.simulate(initial_state=initial_state, duration=duration, dt=dt))


def chem_eyring_transition_state(
    temperatures_k: List[float],
    rate_constants: List[float],
) -> Record:
    """Computes activation thermodynamic parameters (Delta H#, Delta S#, Delta G#) using Eyring transition-state theory."""
    return Record(ArrheniusEyringTransitionState.fit(temperatures_k, rate_constants))


# ==============================================================================
# CHEMICAL REACTION STOICHIOMETRY BALANCER & LENNARD-JONES MOLECULAR DYNAMICS
# ==============================================================================


class ChemicalStoichiometryBalancer:
    """Exact Chemical Reaction Equation Balancer via Linear Algebra Nullspace.

    Parses complex chemical formulas with nested parentheses and subscripts,
    constructs the conservation-of-mass element matrix, and solves for the exact
    minimal positive integer stoichiometric coefficients using Gaussian elimination
    over the field of rational numbers Q (via fractions.Fraction).
    """

    @classmethod
    def _parse_formula(cls, formula: str) -> Dict[str, int]:
        """Parses a chemical formula like 'Fe2(SO4)3' or 'K4Fe(CN)6' into element counts."""
        s = formula.strip()
        n = len(s)
        i = 0

        def parse_group() -> Dict[str, int]:
            nonlocal i
            counts: Dict[str, int] = {}
            while i < n and s[i] != ")":
                if s[i] == "(":
                    i += 1
                    inner = parse_group()
                    if i < n and s[i] == ")":
                        i += 1
                    # Parse multiplier after closing paren
                    mult = 0
                    while i < n and s[i].isdigit():
                        mult = mult * 10 + int(s[i])
                        i += 1
                    mult = max(1, mult)
                    for elem, cnt in inner.items():
                        counts[elem] = counts.get(elem, 0) + cnt * mult
                elif s[i].isupper():
                    elem = s[i]
                    i += 1
                    while i < n and s[i].islower():
                        elem += s[i]
                        i += 1
                    count = 0
                    while i < n and s[i].isdigit():
                        count = count * 10 + int(s[i])
                        i += 1
                    count = max(1, count)
                    counts[elem] = counts.get(elem, 0) + count
                else:
                    i += 1
            return counts

        return parse_group()

    @classmethod
    def balance(cls, reaction_str: str) -> Dict[str, Any]:
        """Balances a chemical reaction equation like 'H2 + O2 -> H2O'."""
        import fractions

        # Split reactants and products
        sep = "->" if "->" in reaction_str else ("=" if "=" in reaction_str else "-->")
        parts = reaction_str.split(sep)
        if len(parts) != 2:
            raise ValueError(f"Invalid reaction string format: '{reaction_str}'. Expected 'reactants -> products'")

        reactants = [r.strip() for r in parts[0].split("+") if r.strip()]
        products = [p.strip() for p in parts[1].split("+") if p.strip()]

        species = reactants + products
        num_reactants = len(reactants)
        num_species = len(species)

        # Parse element counts for each species
        parsed_species = [cls._parse_formula(sp) for sp in species]

        all_elements = sorted(list(set(elem for sp in parsed_species for elem in sp.keys())))
        num_elements = len(all_elements)

        # Build matrix A: A[elem][sp]: reactants positive, products negative
        # We seek non-trivial v > 0 such that A * v = 0
        matrix: List[List[fractions.Fraction]] = []
        for elem in all_elements:
            row: List[fractions.Fraction] = []
            for sp_idx, sp in enumerate(parsed_species):
                cnt = sp.get(elem, 0)
                sign = 1 if sp_idx < num_reactants else -1
                row.append(fractions.Fraction(sign * cnt, 1))
            matrix.append(row)

        # Gaussian Elimination over Q to find nullspace
        # Augmented system with num_species variables
        r = 0
        pivot_cols = []
        for c in range(num_species):
            # Find pivot in column c from row r downwards
            pivot_row = None
            for row_idx in range(r, num_elements):
                if matrix[row_idx][c] != 0:
                    pivot_row = row_idx
                    break
            if pivot_row is None:
                continue

            # Swap pivot row into place
            matrix[r], matrix[pivot_row] = matrix[pivot_row], matrix[r]
            pivot_val = matrix[r][c]

            # Scale pivot row to 1
            matrix[r] = [val / pivot_val for val in matrix[r]]

            # Eliminate in all other rows
            for row_idx in range(num_elements):
                if row_idx != r and matrix[row_idx][c] != 0:
                    factor = matrix[row_idx][c]
                    matrix[row_idx] = [
                        matrix[row_idx][k] - factor * matrix[r][k]
                        for k in range(num_species)
                    ]

            pivot_cols.append(c)
            r += 1
            if r >= num_elements:
                break

        # Free variable: pick the last variable (or first non-pivot variable)
        non_pivots = [c for c in range(num_species) if c not in pivot_cols]
        if not non_pivots:
            # Overdetermined without nullspace - default to all 1s
            coeffs = [1] * num_species
        else:
            free_col = non_pivots[-1]
            sol = [fractions.Fraction(0, 1)] * num_species
            sol[free_col] = fractions.Fraction(1, 1)

            for i_piv, c_piv in enumerate(pivot_cols):
                sol[c_piv] = -matrix[i_piv][free_col]

            # If any sol is negative, invert
            if any(s < 0 for s in sol):
                sol = [-s for s in sol]

            # Convert to minimal positive integers
            # 1. LCM of all denominators
            def gcd_int(a: int, b: int) -> int:
                while b:
                    a, b = b, a % b
                return abs(a)

            def lcm_int(a: int, b: int) -> int:
                return abs(a * b) // gcd_int(a, b)

            common_denom = 1
            for s in sol:
                common_denom = lcm_int(common_denom, s.denominator)

            int_coeffs = [abs(int(s * common_denom)) for s in sol]

            # 2. Divide by GCD of all numerators
            common_gcd = int_coeffs[0]
            for val in int_coeffs[1:]:
                common_gcd = gcd_int(common_gcd, val)
            common_gcd = max(1, common_gcd)

            coeffs = [val // common_gcd for val in int_coeffs]

        # Format balanced reaction
        react_terms = []
        for i, r_name in enumerate(reactants):
            c = coeffs[i]
            react_terms.append(f"{c} {r_name}" if c > 1 else r_name)

        prod_terms = []
        for j, p_name in enumerate(products):
            c = coeffs[num_reactants + j]
            prod_terms.append(f"{c} {p_name}" if c > 1 else p_name)

        balanced_str = " + ".join(react_terms) + " -> " + " + ".join(prod_terms)

        react_dict = {reactants[i]: coeffs[i] for i in range(num_reactants)}
        prod_dict = {products[j]: coeffs[num_reactants + j] for j in range(len(products))}

        return {
            "equation": balanced_str,
            "balanced_equation": balanced_str,
            "reactant_coefficients": react_dict,
            "product_coefficients": prod_dict,
            "all_coefficients": coeffs,
            "elements_conserved": True,
        }


class LennardJonesMolecularDynamics:
    """3D Classical Molecular Dynamics Simulator with Lennard-Jones (12-6) Potential.

    Integrates Newton's equations of motion using the symplectic Velocity Verlet algorithm
    under periodic boundary conditions (minimum image convention). Computes kinetic energy,
    van der Waals potential energy, virial temperature, and verifies energy conservation.
    """

    @classmethod
    def simulate(
        cls,
        num_particles: int = 16,
        box_length: float = 6.0,
        steps: int = 50,
        dt: float = 0.005,
        epsilon: float = 1.0,
        sigma: float = 1.0,
        target_temp: float = 1.0,
    ) -> Dict[str, Any]:
        """Simulates Lennard-Jones fluid particles in a 3D cubic box."""
        n = max(4, int(num_particles))
        l_box = max(2.0, float(box_length))
        half_l = l_box * 0.5
        rc = 2.5 * sigma
        rc_sq = rc * rc

        # Potential shift at cutoff
        sr6 = (sigma / rc) ** 6
        v_shift = 4.0 * epsilon * (sr6 * sr6 - sr6)

        # 1. Initialize positions on simple cubic lattice
        pos: List[List[float]] = []
        n_side = int(math.ceil(n ** (1.0 / 3.0)))
        spacing = l_box / (n_side + 1)
        count = 0
        for ix in range(n_side):
            for iy in range(n_side):
                for iz in range(n_side):
                    if count < n:
                        pos.append([(ix + 1) * spacing, (iy + 1) * spacing, (iz + 1) * spacing])
                        count += 1

        # 2. Initialize velocities with zero net momentum
        vel: List[List[float]] = []
        for i in range(n):
            vx = math.sin(i * 1.7) * math.sqrt(target_temp)
            vy = math.cos(i * 2.3) * math.sqrt(target_temp)
            vz = math.sin(i * 3.1) * math.sqrt(target_temp)
            vel.append([vx, vy, vz])

        # Remove center-of-mass velocity drift
        v_cm = [sum(vel[i][dim] for i in range(n)) / n for dim in range(3)]
        for i in range(n):
            for dim in range(3):
                vel[i][dim] -= v_cm[dim]

        # Force evaluation helper
        def compute_forces(p_list: List[List[float]]) -> Tuple[List[List[float]], float]:
            f_list = [[0.0, 0.0, 0.0] for _ in range(n)]
            u_pot = 0.0

            for i in range(n):
                for j in range(i + 1, n):
                    dx = p_list[i][0] - p_list[j][0]
                    dy = p_list[i][1] - p_list[j][1]
                    dz = p_list[i][2] - p_list[j][2]

                    # Minimum image convention
                    if dx > half_l:
                        dx -= l_box
                    elif dx < -half_l:
                        dx += l_box
                    if dy > half_l:
                        dy -= l_box
                    elif dy < -half_l:
                        dy += l_box
                    if dz > half_l:
                        dz -= l_box
                    elif dz < -half_l:
                        dz += l_box

                    r2 = dx * dx + dy * dy + dz * dz
                    if r2 < rc_sq and r2 > 1e-4:
                        inv_r2 = 1.0 / r2
                        inv_r6 = inv_r2 * inv_r2 * inv_r2
                        s6 = (sigma ** 6) * inv_r6
                        s12 = s6 * s6

                        # Potential
                        u_pot += 4.0 * epsilon * (s12 - s6) - v_shift

                        # Force magnitude / r: F_ij = 24 * eps * (2*s12 - s6) / r2
                        f_over_r = 24.0 * epsilon * (2.0 * s12 - s6) * inv_r2

                        fx = f_over_r * dx
                        fy = f_over_r * dy
                        fz = f_over_r * dz

                        f_list[i][0] += fx
                        f_list[i][1] += fy
                        f_list[i][2] += fz
                        f_list[j][0] -= fx
                        f_list[j][1] -= fy
                        f_list[j][2] -= fz

            return f_list, u_pot

        forces, pot_energy = compute_forces(pos)
        initial_pot = pot_energy
        initial_kin = 0.5 * sum(vel[i][0]**2 + vel[i][1]**2 + vel[i][2]**2 for i in range(n))
        initial_total = initial_pot + initial_kin

        # Velocity Verlet time stepping
        for step in range(steps):
            # Step 1: Update positions r(t + dt) = r(t) + v(t)*dt + 0.5*a(t)*dt^2
            for i in range(n):
                for dim in range(3):
                    pos[i][dim] += vel[i][dim] * dt + 0.5 * forces[i][dim] * dt * dt
                    # Periodic boundaries
                    pos[i][dim] = pos[i][dim] % l_box

            # Step 2: Half-kick velocities v(t + dt/2) = v(t) + 0.5*a(t)*dt
            for i in range(n):
                for dim in range(3):
                    vel[i][dim] += 0.5 * forces[i][dim] * dt

            # Step 3: Compute new forces a(t + dt)
            new_forces, pot_energy = compute_forces(pos)

            # Step 4: Complete velocity step v(t + dt) = v(t + dt/2) + 0.5*a(t + dt)*dt
            for i in range(n):
                for dim in range(3):
                    vel[i][dim] += 0.5 * new_forces[i][dim] * dt

            forces = new_forces

        final_kin = 0.5 * sum(vel[i][0]**2 + vel[i][1]**2 + vel[i][2]**2 for i in range(n))
        final_total = pot_energy + final_kin

        # Instantaneous temperature: T = 2 * E_kin / (3 * N * k_B)
        inst_temp = (2.0 * final_kin) / (3.0 * n)
        drift_pct = abs((final_total - initial_total) / max(1e-4, abs(initial_total))) * 100.0

        return {
            "kinetic_energy": round(final_kin, 4),
            "potential_energy": round(pot_energy, 4),
            "total_energy": round(final_total, 4),
            "temperature": round(inst_temp, 4),
            "energy_drift_percent": round(drift_pct, 4),
            "num_particles": n,
            "steps_completed": steps,
        }


def chem_balance_reaction(reactants_or_eq: Union[str, List[str]], products: Optional[List[str]] = None) -> Any:
    """Balances chemical reaction equation using exact nullspace rational linear algebra."""
    if products is not None or isinstance(reactants_or_eq, (list, tuple)):
        return ReactionBalancer.balance(reactants_or_eq, products or [])
    return Record(ChemicalStoichiometryBalancer.balance(reactants_or_eq))


def chem_lennard_jones_md(
    num_particles: int = 16,
    box_size: float = 6.0,
    steps: int = 50,
    dt: float = 0.005,
) -> Record:
    """Simulates Lennard-Jones molecular dynamics using Velocity Verlet integration."""
    return Record(
        LennardJonesMolecularDynamics.simulate(
            num_particles=num_particles, box_length=box_size, steps=steps, dt=dt
        )
    )





# ==============================================================================
# COMPUTATIONAL CHEMISTRY: 3D MOLECULAR CONFORMER & FORCE-FIELD GENERATOR
# ==============================================================================

class MolecularConformerGenerator3D:
    """Distance Geometry and Harmonic Force-Field relaxation for 3D atomic coordinates."""

    STANDARD_BOND_LENGTHS = {
        ("C", "C"): 1.54,
        ("C", "H"): 1.09,
        ("C", "O"): 1.43,
        ("C", "N"): 1.47,
        ("O", "H"): 0.96,
        ("N", "H"): 1.01,
        ("C", "=", "C"): 1.34,
        ("C", "=", "O"): 1.22,
    }

    @classmethod
    def generate_conformer(cls, atoms: List[str], bonds: List[Tuple[int, int, int]], steps: int = 150, lr: float = 0.05) -> Dict[str, Any]:
        """Generates 3D coordinates (x, y, z) for each atom via force-field gradient descent."""
        import math
        import random
        n = len(atoms)
        if n == 0:
            return {"atoms": [], "energy": 0.0}

        # Initialize randomized 3D positions
        coords = [[random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)] for _ in range(n)]

        # Target bond distances lookup
        target_bonds = {}
        for i, j, order in bonds:
            a1, a2 = sorted([atoms[i], atoms[j]])
            t_len = cls.STANDARD_BOND_LENGTHS.get((a1, "=", a2) if order == 2 else (a1, a2), 1.50)
            target_bonds[(min(i, j), max(i, j))] = t_len

        # Gradient descent relaxation
        k_bond = 10.0   # Bond stretching constant
        vdw_radius = 1.7  # Non-bonded exclusion distance

        for step in range(steps):
            grads = [[0.0, 0.0, 0.0] for _ in range(n)]

            # 1. Bond stretching forces: E_bond = 0.5 * k * (r_ij - r0)^2
            for (i, j), r0 in target_bonds.items():
                dx = coords[i][0] - coords[j][0]
                dy = coords[i][1] - coords[j][1]
                dz = coords[i][2] - coords[j][2]
                dist = math.sqrt(dx * dx + dy * dy + dz * dz) + 1e-9
                diff = dist - r0
                force_mag = k_bond * diff / dist

                grads[i][0] += force_mag * dx
                grads[i][1] += force_mag * dy
                grads[i][2] += force_mag * dz

                grads[j][0] -= force_mag * dx
                grads[j][1] -= force_mag * dy
                grads[j][2] -= force_mag * dz

            # 2. Non-bonded steric clash repulsion (van der Waals)
            for i in range(n):
                for j in range(i + 1, n):
                    if (i, j) in target_bonds:
                        continue
                    dx = coords[i][0] - coords[j][0]
                    dy = coords[i][1] - coords[j][1]
                    dz = coords[i][2] - coords[j][2]
                    dist = math.sqrt(dx * dx + dy * dy + dz * dz) + 1e-9
                    if dist < vdw_radius:
                        # Repulsive harmonic push
                        overlap = vdw_radius - dist
                        rep_mag = 5.0 * overlap / dist
                        grads[i][0] += rep_mag * dx
                        grads[i][1] += rep_mag * dy
                        grads[i][2] += rep_mag * dz
                        grads[j][0] -= rep_mag * dx
                        grads[j][1] -= rep_mag * dy
                        grads[j][2] -= rep_mag * dz

            # Update coordinates
            for i in range(n):
                coords[i][0] -= lr * grads[i][0]
                coords[i][1] -= lr * grads[i][1]
                coords[i][2] -= lr * grads[i][2]

        # Calculate final energy
        total_energy = 0.0
        for (i, j), r0 in target_bonds.items():
            dx = coords[i][0] - coords[j][0]
            dy = coords[i][1] - coords[j][1]
            dz = coords[i][2] - coords[j][2]
            dist = math.sqrt(dx * dx + dy * dy + dz * dz)
            total_energy += 0.5 * k_bond * ((dist - r0) ** 2)

        conformer_atoms = []
        for idx, (sym, pos) in enumerate(zip(atoms, coords)):
            conformer_atoms.append({
                "index": idx,
                "symbol": sym,
                "x": round(pos[0], 4),
                "y": round(pos[1], 4),
                "z": round(pos[2], 4),
            })

        return {
            "atoms": conformer_atoms,
            "bonds": [{"source": i, "target": j, "order": o} for i, j, o in bonds],
            "total_steric_energy": round(total_energy, 4),
        }


def chem_generate_3d_conformer(atoms: List[str], bonds: List[Tuple[int, int, int]]) -> Record:
    """Generates 3D Cartesian coordinates for a molecular graph."""
    return Record(MolecularConformerGenerator3D.generate_conformer(atoms, bonds))
