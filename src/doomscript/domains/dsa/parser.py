"""Independent Domain Parser for Testing & Algorithm Analysis (DSA)."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.dsa.spec import BenchmarkSpec


class DsaDomainParser(DomainParser):
    """Independent parser for Algorithm Analysis, Complexity, and Benchmarking."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        # complexity of <fn> [into <target>]
        m = re.match(
            r"^(?:empirical\s+)?complexity\s+of\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m:
            fn_name = m.group(1)
            target = m.group(2) or f"{fn_name}_complexity"
            return f'set {target} to analyze_complexity("{fn_name}")'

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        # profile memory of <fn> with <input> into <target>
        prof_m = re.match(
            r"^profile\s+memory\s+of\s+([A-Za-z_]\w*)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if prof_m:
            fn = prof_m.group(1)
            inp = prof_m.group(2).strip()
            target = prof_m.group(3)
            return f'set {target} to profile_memory_of_function("{fn}", {inp})'

        # benchmark <fn> with sizes <sizes> into <target>
        bm_m = re.match(
            r"^benchmark\s+([A-Za-z_]\w*)\s+with\s+sizes\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if bm_m:
            fn = bm_m.group(1)
            sizes = bm_m.group(2).strip()
            target = bm_m.group(3) or f"{fn}_bench"
            return f'set {target} to run_benchmark_with_sizes("{fn}", {sizes})'

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[BenchmarkSpec, str]:
        # benchmark <fn_name> [into <target>]:
        m = re.match(
            r"^benchmark\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?:?$",
            header.strip(),
            re.IGNORECASE,
        )
        if not m:
            raise SyntaxError(f"Invalid benchmark header: {header}")

        fn_name = m.group(1)
        target = m.group(2) or f"{fn_name}_benchmark"

        spec = BenchmarkSpec(fn_name=fn_name, target_var=target)

        for l_no, raw_line in body_lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # input_sizes: [100, 1000, 10000]
            sizes_m = re.match(r"^input_sizes\s*:\s*\[(.*?)\]", line, re.IGNORECASE)
            if sizes_m:
                raw_nums = sizes_m.group(1).split(",")
                spec.input_sizes = [int(s.strip()) for s in raw_nums if s.strip()]
                continue

            # repeat: <n>
            rep_m = re.match(r"^repeat\s*:\s*(\d+)", line, re.IGNORECASE)
            if rep_m:
                spec.repeat = int(rep_m.group(1))
                continue

            # measure: execution_time, memory
            meas_m = re.match(r"^measure\s*:\s*(.+)$", line, re.IGNORECASE)
            if meas_m:
                spec.measure_memory = "memory" in meas_m.group(1).lower()
                continue

            # generator: <gen>
            gen_m = re.match(r"^generator\s*:\s*([A-Za-z_]\w*)$", line, re.IGNORECASE)
            if gen_m:
                spec.generator = gen_m.group(1).lower()
                continue

        errors = spec.validate()
        if errors:
            raise SyntaxError(f"Benchmark validation error for '{fn_name}': {'; '.join(errors)}")

        return spec, target
