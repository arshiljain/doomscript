"""Epidemiology Domain Parser: Translates natural epidemiological and disease spread expressions into DoomScript calls."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class EpidemiologyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # Existing syntax
        m_r0 = re.match(r"^calculate\s+reproduction\s+number\s+r0\s+for\s+beta\s+(.+?)\s+gamma\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_r0:
            return f"set {m_r0.group(3)} to epi_r0({m_r0.group(1)}, {m_r0.group(2)})"

        m_hit = re.match(r"^calculate\s+herd\s+immunity\s+threshold\s+for\s+r0\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hit:
            return f"set {m_hit.group(2)} to epi_herd_immunity_threshold({m_hit.group(1)})"

        m_sir = re.match(r"^step\s+sir\s+model\s+s\s+(.+?)\s+i\s+(.+?)\s+r\s+(.+?)\s+beta\s+(.+?)\s+gamma\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sir:
            return f"set {m_sir.group(6)} to epi_sir_step({m_sir.group(1)}, {m_sir.group(2)}, {m_sir.group(3)}, {m_sir.group(4)}, {m_sir.group(5)})"

        m_seir = re.match(r"^step\s+seir\s+model\s+s\s+(.+?)\s+e\s+(.+?)\s+i\s+(.+?)\s+r\s+(.+?)\s+beta\s+(.+?)\s+sigma\s+(.+?)\s+gamma\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_seir:
            return f"set {m_seir.group(8)} to epi_seir_step({m_seir.group(1)}, {m_seir.group(2)}, {m_seir.group(3)}, {m_seir.group(4)}, {m_seir.group(5)}, {m_seir.group(6)}, {m_seir.group(7)})"

        m_cfr = re.match(r"^calculate\s+cfr\s+for\s+cases\s+(.+?)\s+deaths\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cfr:
            return f"set {m_cfr.group(3)} to epi_fatality_rates({m_cfr.group(1)}, {m_cfr.group(2)})"

        # Deepened syntax
        m_rt = re.match(r"^calculate\s+effective\s+rt\s+r0\s+(.+?)\s+susceptible\s+(.+?)(?:\s+reduction\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rt:
            red = m_rt.group(3) if m_rt.group(3) else "0.0"
            return f"set {m_rt.group(4)} to epi_effective_reproduction_rt({m_rt.group(1)}, {m_rt.group(2)}, {red})"

        m_final = re.match(r"^calculate\s+final\s+epidemic\s+size\s+r0\s+(.+?)(?:\s+s0\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_final:
            s0_v = m_final.group(2) if m_final.group(2) else "0.999"
            return f"set {m_final.group(3)} to epi_final_size_relation({m_final.group(1)}, {s0_v})"

        m_vac = re.match(r"^calculate\s+vaccination\s+threshold\s+r0\s+(.+?)\s+efficacy\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_vac:
            return f"set {m_vac.group(3)} to epi_vaccination_critical_coverage({m_vac.group(1)}, {m_vac.group(2)})"

        m_double = re.match(r"^calculate\s+epidemic\s+doubling\s+time\s+r0\s+(.+?)\s+generation\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_double:
            return f"set {m_double.group(3)} to epi_generation_time_doubling({m_double.group(1)}, {m_double.group(2)})"

        m_or = re.match(r"^calculate\s+outbreak\s+odds\s+ratio\s+exp_cases\s+(.+?)\s+exp_healthy\s+(.+?)\s+unexp_cases\s+(.+?)\s+unexp_healthy\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_or:
            return f"set {m_or.group(5)} to epi_attack_rate_odds_ratio({m_or.group(1)}, {m_or.group(2)}, {m_or.group(3)}, {m_or.group(4)})"

        m_sar = re.match(r"^calculate\s+secondary\s+attack\s+rate\s+cases\s+(.+?)\s+contacts\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sar:
            return f"set {m_sar.group(3)} to epi_secondary_attack_rate({m_sar.group(1)}, {m_sar.group(2)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Epidemiology domain does not define declarative blocks")
