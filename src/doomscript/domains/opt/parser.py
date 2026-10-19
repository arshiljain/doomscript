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
