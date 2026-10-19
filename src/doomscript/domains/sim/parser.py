"""Independent Domain Parser for Simulation & Optimization language constructs."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.sim.spec import SimulationSpec, OptimizationSpec


class SimDomainParser(DomainParser):
    """Independent parser for Simulation & Optimization syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        # inspect simulation <name> [into <target>]
        m = re.match(
            r"^inspect\s+simulation\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m:
            sim_name = m.group(1)
            target = m.group(2) or "sim_inspection"
            return f'set {target} to ({sim_name}["summary"])'

        # summarize uncertainty of <var> [into <target>]
        m_unc = re.match(
            r"^summarize\s+uncertainty\s+of\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_unc:
            var_name = m_unc.group(1)
            target = m_unc.group(2) or f"{var_name}_uncertainty"
            return f"set {target} to summarize_uncertainty({var_name})"

        # summarize <var> [into <target>]
        m2 = re.match(
            r"^summarize\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m2:
            var_name = m2.group(1)
            target = m2.group(2) or f"{var_name}_summary"
            return f"set {target} to summarize_metric({var_name})"

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        # run <n> trials of <sim> [into <target>]
        m_tr = re.match(
            r"^run\s+(\d+)\s+trials\s+of\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_tr:
            trials_cnt = int(m_tr.group(1))
            sim_name = m_tr.group(2)
            target = m_tr.group(3) or f"{sim_name}_trials"
            return f'set {target} to run_trials("{sim_name}", trials={trials_cnt})'

        # sweep <param> over <values> [for <sim>] [into <target>]
        m_sw = re.match(
            r"^sweep\s+([A-Za-z_]\w*)\s+over\s+(.+?)(?:\s+(?:for|on)\s+([A-Za-z_]\w+))?(?:\s+into\s+([A-Za-z_]\w+))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_sw:
            param = m_sw.group(1)
            values = m_sw.group(2).strip()
            sim_name = m_sw.group(3) or ""
            target = m_sw.group(4) or f"{param}_sweep"
            return f'set {target} to sweep_parameter("{sim_name}", "{param}", {values})'

        # sample <dist> with rate <r> [count <n>] into <target>
        s_rate_m = re.match(
            r"^sample\s+([A-Za-z_]\w+)\s+with\s+rate\s+(\d+(?:\.\d+)?)(?:\s+count\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if s_rate_m:
            dist = s_rate_m.group(1).lower()
            rate = float(s_rate_m.group(2))
            count = int(s_rate_m.group(3)) if s_rate_m.group(3) else 1000
            target = s_rate_m.group(4)
            return f'set {target} to sample_distribution("{dist}", {{"rate": {rate}}}, {count})'

        # optimize <fn> [starting at <guess>] into <target>
        opt_m = re.match(
            r"^optimize\s+([A-Za-z_]\w*)(?:\s+starting\s+at\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if opt_m:
            fn_name = opt_m.group(1)
            guess = opt_m.group(2) or "[0.0]"
            target = opt_m.group(3)
            return f'set {target} to optimize_function("{fn_name}", initial_guess={guess})'

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[SimulationSpec, str]:
        # simulate <name> [into <target>]:
        m = re.match(
            r"^simulate\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?:?$",
            header.strip(),
            re.IGNORECASE,
        )
        if not m:
            raise SyntaxError(f"Invalid simulation header: {header}")

        sim_name = m.group(1)
        target = m.group(2) or sim_name

        spec = SimulationSpec(name=sim_name, target_var=target)

        for l_no, raw_line in body_lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # arrivals: (poisson|exponential) with rate <r>
            arr_m = re.match(
                r"^arrivals\s*:\s*([A-Za-z_]\w+)(?:\s+with\s+rate\s+(\d+(?:\.\d+)?))?",
                line,
                re.IGNORECASE,
            )
            if arr_m:
                spec.arrival_dist = arr_m.group(1).lower()
                rate = float(arr_m.group(2)) if arr_m.group(2) else 10.0
                spec.arrival_params = {"rate": rate}
                continue

            # service: (exponential|normal) with rate <r>
            srv_m = re.match(
                r"^service\s*:\s*([A-Za-z_]\w+)(?:\s+with\s+rate\s+(\d+(?:\.\d+)?))?",
                line,
                re.IGNORECASE,
            )
            if srv_m:
                spec.service_dist = srv_m.group(1).lower()
                rate = float(srv_m.group(2)) if srv_m.group(2) else 12.0
                spec.service_params = {"rate": rate}
                continue

            # duration: <n> events
            dur_m = re.match(r"^duration\s*:\s*(\d+)", line, re.IGNORECASE)
            if dur_m:
                spec.duration = int(dur_m.group(1))
                continue

            # servers: <n>
            srv_cnt_m = re.match(r"^servers\s*:\s*(\d+)", line, re.IGNORECASE)
            if srv_cnt_m:
                spec.servers = int(srv_cnt_m.group(1))
                continue

            # seed: <n>
            seed_m = re.match(r"^seed\s*(?::|\s+simulation\s+with)\s*(\d+)", line, re.IGNORECASE)
            if seed_m:
                spec.seed = int(seed_m.group(1))
                continue

        errors = spec.validate()
        if errors:
            raise SyntaxError(f"Simulation validation error for '{sim_name}': {'; '.join(errors)}")

        return spec, target
