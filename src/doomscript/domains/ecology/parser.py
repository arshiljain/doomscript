import re
from typing import Optional
from doomscript.domains.base import DomainParser

class EcologyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate shannon diversity abundances <abundances> into <target>
        m_shan = re.match(r"^calculate\s+shannon\s+diversity\s+(?:for\s+)?abundances\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_shan:
            return f"set {m_shan.group(2)} to ecology_shannon_diversity({m_shan.group(1)})"

        # calculate simpson diversity abundances <abundances> into <target>
        m_simp = re.match(r"^calculate\s+simpson\s+diversity\s+(?:for\s+)?abundances\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_simp:
            return f"set {m_simp.group(2)} to ecology_simpson_diversity({m_simp.group(1)})"

        # calculate pielou evenness abundances <abundances> into <target>
        m_piel = re.match(r"^calculate\s+pielou\s+evenness\s+(?:for\s+)?abundances\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_piel:
            return f"set {m_piel.group(2)} to ecology_pielou_evenness({m_piel.group(1)})"

        # calculate island biogeography area <a> constant <c> exponent <z> into <target>
        m_isl = re.match(r"^calculate\s+island\s+biogeography\s+area\s+(.+?)\s+constant\s+(.+?)\s+exponent\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_isl:
            return f"set {m_isl.group(4)} to ecology_island_biogeography({m_isl.group(1)}, {m_isl.group(2)}, {m_isl.group(3)})"

        # step lotka volterra prey <x> pred <y> alpha <a> beta <b> gamma <g> delta <d> dt <dt> into <target>
        m_lv = re.match(r"^step\s+lotka\s+volterra\s+prey\s+(.+?)\s+(?:pred|predator)\s+(.+?)\s+alpha\s+(.+?)\s+beta\s+(.+?)\s+gamma\s+(.+?)\s+delta\s+(.+?)(?:\s+dt\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_lv:
            dt_arg = m_lv.group(7) if m_lv.group(7) is not None else "0.1"
            return f"set {m_lv.group(8)} to ecology_lotka_volterra_step({m_lv.group(1)}, {m_lv.group(2)}, {m_lv.group(3)}, {m_lv.group(4)}, {m_lv.group(5)}, {m_lv.group(6)}, {dt_arg})"

        # calculate logistic growth n0 <n0> rate <r> capacity <k> time <t> into <target>
        m_log = re.match(r"^calculate\s+logistic\s+growth\s+(?:for\s+)?n0\s+(.+?)\s+(?:r|rate)\s+(.+?)\s+(?:k|capacity)\s+(.+?)\s+time\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_log:
            return f"set {m_log.group(5)} to ecology_logistic_growth({m_log.group(1)}, {m_log.group(2)}, {m_log.group(3)}, {m_log.group(4)})"

        # estimate population mark recapture n1 <n1> n2 <n2> m2 <m2> into <target>
        m_mr = re.match(r"^(?:estimate\s+population\s+mark\s+recapture\s+n1\s+(.+?)\s+n2\s+(.+?)\s+m2\s+(.+?)|estimate\s+population\s+marked\s+(.+?)\s+captured\s+(.+?)\s+recaptured\s+(.+?))\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mr:
            if m_mr.group(1):
                return f"set {m_mr.group(7)} to ecology_lincoln_petersen_estimate({m_mr.group(1)}, {m_mr.group(2)}, {m_mr.group(3)})"
            else:
                return f"set {m_mr.group(7)} to ecology_lincoln_petersen_estimate({m_mr.group(4)}, {m_mr.group(5)}, {m_mr.group(6)})"

        
        m_simp_alt = re.match(r"^calculate\s+simpson\s+diversity\s+for\s+abundances\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_simp_alt:
            return f"set {m_simp_alt.group(2)} to ecology_simpson_diversity({m_simp_alt.group(1)})"

        m_piel_alt = re.match(r"^calculate\s+pielou\s+evenness\s+for\s+shannon\s+(.+?)\s+species\s+count\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_piel_alt:
            return f"set {m_piel_alt.group(3)} to ecology_pielou_evenness_from_h({m_piel_alt.group(1)}, {m_piel_alt.group(2)})"

        m_lv_alt = re.match(r"^step\s+lotka\s+volterra\s+prey\s+(.+?)\s+predator\s+(.+?)\s+alpha\s+(.+?)\s+beta\s+(.+?)\s+gamma\s+(.+?)\s+delta\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_lv_alt:
            return f"set {m_lv_alt.group(7)} to ecology_lotka_volterra_step({m_lv_alt.group(1)}, {m_lv_alt.group(2)}, {m_lv_alt.group(3)}, {m_lv_alt.group(4)}, {m_lv_alt.group(5)}, {m_lv_alt.group(6)})"

        m_log_alt = re.match(r"^step\s+logistic\s+growth\s+population\s+(.+?)\s+r\s+(.+?)\s+k\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_log_alt:
            return f"set {m_log_alt.group(4)} to ecology_logistic_growth_step({m_log_alt.group(1)}, {m_log_alt.group(2)}, {m_log_alt.group(3)})"

        m_mr_alt = re.match(r"^calculate\s+lincoln\s+peterson\s+marked\s+(.+?)\s+captured\s+(.+?)\s+recaptured\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mr_alt:
            return f"set {m_mr_alt.group(4)} to ecology_lincoln_petersen_estimator({m_mr_alt.group(1)}, {m_mr_alt.group(2)}, {m_mr_alt.group(3)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Ecology domain does not define declarative blocks")
