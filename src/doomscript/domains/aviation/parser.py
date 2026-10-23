"""Aviation Domain Parser: Translates natural flight operations expressions into DoomScript calls."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class AviationDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # Existing syntax
        m_pa = re.match(r"^calculate\s+pressure\s+altitude\s+altimeter\s+(.+?)\s+elevation\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_pa:
            return f"set {m_pa.group(3)} to aviation_pressure_altitude({m_pa.group(1)}, {m_pa.group(2)})"

        m_da = re.match(r"^calculate\s+density\s+altitude\s+pressure_alt\s+(.+?)\s+oat\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_da:
            return f"set {m_da.group(3)} to aviation_density_altitude({m_da.group(1)}, {m_da.group(2)})"

        m_wind = re.match(r"^calculate\s+wind\s+components\s+wind_speed\s+(.+?)\s+wind_dir\s+(.+?)\s+runway\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_wind:
            return f"set {m_wind.group(4)} to aviation_wind_components({m_wind.group(1)}, {m_wind.group(2)}, {m_wind.group(3)})"

        m_turn = re.match(r"^calculate\s+turn\s+radius\s+tas\s+(.+?)\s+bank\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_turn:
            return f"set {m_turn.group(3)} to aviation_turn_radius({m_turn.group(1)}, {m_turn.group(2)})"

        m_stall = re.match(r"^calculate\s+banked\s+stall\s+speed\s+vs0\s+(.+?)\s+bank\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_stall:
            return f"set {m_stall.group(3)} to aviation_banked_stall_speed({m_stall.group(1)}, {m_stall.group(2)})"

        m_climb = re.match(r"^calculate\s+climb\s+gradient\s+roc\s+(.+?)\s+tas\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_climb:
            return f"set {m_climb.group(3)} to aviation_climb_gradient({m_climb.group(1)}, {m_climb.group(2)})"

        # Deepened syntax
        m_tas = re.match(r"^calculate\s+true\s+airspeed\s+cas\s+(.+?)\s+pressure_alt\s+(.+?)\s+oat\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tas:
            return f"set {m_tas.group(4)} to aviation_tas_from_cas({m_tas.group(1)}, {m_tas.group(2)}, {m_tas.group(3)})"

        m_glide = re.match(r"^calculate\s+glide\s+performance\s+ratio\s+(.+?)\s+altitude\s+(.+?)(?:\s+wind\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_glide:
            w = m_glide.group(3) if m_glide.group(3) else "0.0"
            return f"set {m_glide.group(4)} to aviation_glide_performance({m_glide.group(1)}, {m_glide.group(2)}, {w})"

        m_hold = re.match(r"^calculate\s+holding\s+pattern\s+drift\s+wind_speed\s+(.+?)\s+wind_dir\s+(.+?)\s+course\s+(.+?)\s+tas\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hold:
            return f"set {m_hold.group(5)} to aviation_holding_pattern_drift({m_hold.group(1)}, {m_hold.group(2)}, {m_hold.group(3)}, {m_hold.group(4)})"

        m_wb = re.match(r"^calculate\s+weight\s+and\s+balance\s+empty_weight\s+(.+?)\s+empty_arm\s+(.+?)\s+stations\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_wb:
            return f"set {m_wb.group(4)} to aviation_weight_and_balance({m_wb.group(1)}, {m_wb.group(2)}, {m_wb.group(3)})"

        m_mach = re.match(r"^calculate\s+critical\s+mach\s+sweep\s+(.+?)\s+thickness\s+(.+?)(?:\s+cl\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mach:
            cl = m_mach.group(3) if m_mach.group(3) else "0.3"
            return f"set {m_mach.group(4)} to aviation_critical_mach_drag_divergence({m_mach.group(1)}, {m_mach.group(2)}, {cl})"

        m_std = re.match(r"^calculate\s+standard\s+rate\s+turn\s+tas\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_std:
            return f"set {m_std.group(2)} to aviation_standard_rate_turn({m_std.group(1)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Aviation domain does not define declarative blocks")
