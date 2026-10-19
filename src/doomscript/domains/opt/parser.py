"""Independent Domain Parser for Optimization & Operations Research language constructs."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.opt.spec import LinearProgramSpec, SolveLPSpec


class OptDomainParser(DomainParser):
    """Independent parser for Optimization and Linear Programming syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # solve [linear program] <name> into <target>
        m_solve = re.match(
            r"^solve(?:\s+linear\s+program)?\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_solve:
            lp_name = m_solve.group(1).strip()
            target = m_solve.group(2).strip()
            return f'set {target} to solve_linear_program("{lp_name}")'

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[LinearProgramSpec, str]:
        # direct objective block: maximize/minimize <obj> [into <target>] [where]:
        h_strip = header.strip().rstrip(":")
        direct_m = re.match(r"^(maximize|minimize)\s+(.+)$", h_strip, re.IGNORECASE)
        if direct_m:
            sense = direct_m.group(1).lower()
            rest = direct_m.group(2).strip()
            target = "lp_solution"

            # Check for 'into <target>'
            into_match = re.search(r"\binto\s+([A-Za-z_]\w*)\b", rest, re.IGNORECASE)
            if into_match:
                target = into_match.group(1)
                rest = re.sub(r"\binto\s+[A-Za-z_]\w*\b", "", rest, flags=re.IGNORECASE).strip()

            # Remove optional 'where' keyword
            rest = re.sub(r"\bwhere\b", "", rest, flags=re.IGNORECASE).strip()
            obj_expr = rest

            lp_name = "direct_lp"
            spec = LinearProgramSpec(name=lp_name, target_var=target, sense=sense, objective=obj_expr)
            for _, raw_line in body_lines:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                into_m = re.match(r"^into\s+([A-Za-z_]\w*)$", line, re.IGNORECASE)
                if into_m:
                    target = into_m.group(1)
                    spec.target_var = target
                    continue
                if any(op in line for op in ("<=", ">=", "=", "<", ">")):
                    spec.constraints.append(line)
            errors = spec.validate()
            if errors:
                raise SyntaxError(f"Linear program validation error: {'; '.join(errors)}")
            return spec, target

        # linear program <name> [into <target>]:
        m = re.match(
            r"^(?:linear\s+program|optimize)\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?:?$",
            header.strip(),
            re.IGNORECASE,
        )
        if not m:
            raise SyntaxError(f"Invalid linear program block header: {header}")

        lp_name = m.group(1).strip()
        target = m.group(2) or lp_name

        spec = LinearProgramSpec(name=lp_name, target_var=target)
        in_constraints = False

        for _, raw_line in body_lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # maximize: <expr>
            max_m = re.match(r"^maximize\s*:\s*(.+)$", line, re.IGNORECASE)
            if max_m:
                spec.sense = "maximize"
                spec.objective = max_m.group(1).strip()
                in_constraints = False
                continue

            # minimize: <expr>
            min_m = re.match(r"^minimize\s*:\s*(.+)$", line, re.IGNORECASE)
            if min_m:
                spec.sense = "minimize"
                spec.objective = min_m.group(1).strip()
                in_constraints = False
                continue

            # subject to:
            if re.match(r"^subject\s+to\s*:?$", line, re.IGNORECASE):
                in_constraints = True
                continue

            # constraint line
            if in_constraints or any(op in line for op in ("<=", ">=", "=", "<", ">")):
                spec.constraints.append(line)

        errors = spec.validate()
        if errors:
            raise SyntaxError(f"Linear program validation error for '{lp_name}': {'; '.join(errors)}")

        return spec, target
