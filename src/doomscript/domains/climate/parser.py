"""Climate Domain Natural Language Parser."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class ClimateDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate dew point for temperature <t> humidity <h> into <target>
        m_dp = re.match(r"^calculate\s+dew\s+point\s+for\s+(?:temp|temperature)\s+(.+?)\s+humidity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dp:
            return f"set {m_dp.group(3)} to climate_dew_point({m_dp.group(1)}, {m_dp.group(2)})"

        # calculate heat index for temperature <t> humidity <h> into <target>
        m_hi = re.match(r"^calculate\s+heat\s+index\s+for\s+(?:temp|temperature)\s+(.+?)\s+humidity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hi:
            return f"set {m_hi.group(3)} to climate_heat_index({m_hi.group(1)}, {m_hi.group(2)})"

        # calculate wind chill for temperature <t> wind <w> into <target>
        m_wc = re.match(r"^calculate\s+wind\s+chill\s+for\s+(?:temp|temperature)\s+(.+?)\s+wind\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_wc:
            return f"set {m_wc.group(3)} to climate_wind_chill({m_wc.group(1)}, {m_wc.group(2)})"

        # calculate vpd for temperature <t> humidity <h> into <target>
        m_vpd = re.match(r"^calculate\s+(?:vapor\s+pressure\s+deficit|vpd)\s+for\s+(?:temp|temperature)\s+(.+?)\s+humidity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_vpd:
            return f"set {m_vpd.group(3)} to climate_vapor_pressure_deficit({m_vpd.group(1)}, {m_vpd.group(2)})"

        # calculate barometric pressure for altitude <alt> into <target>
        m_baro = re.match(r"^calculate\s+barometric\s+pressure\s+(?:for\s+|at\s+)?altitude\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_baro:
            return f"set {m_baro.group(2)} to climate_barometric_altitude({m_baro.group(1)})"

        # convert emissions amount <amt> gas <gas> into <target>
        m_emiss = re.match(r"^(?:convert\s+co2\s+equivalent\s+for\s+gas\s+(.+?)\s+amount\s+(.+?)\s+into\s+([A-Za-z_]\w*)|convert\s+emissions\s+amount\s+(.+?)\s+gas\s+(.+?)\s+into\s+([A-Za-z_]\w*)|convert\s+emissions\s+(.+?)\s+of\s+gas\s+(.+?)\s+to\s+co2\s+equivalent\s+into\s+([A-Za-z_]\w*))$", s, re.IGNORECASE)
        if m_emiss:
            if m_emiss.group(3):
                return f"set {m_emiss.group(3)} to climate_co2_equivalent({m_emiss.group(2)}, {m_emiss.group(1)})"
            elif m_emiss.group(6):
                return f"set {m_emiss.group(6)} to climate_co2_equivalent({m_emiss.group(4)}, {m_emiss.group(5)})"
            elif m_emiss.group(9):
                return f"set {m_emiss.group(9)} to climate_co2_equivalent({m_emiss.group(7)}, {m_emiss.group(8)})"

        # calculate radiative forcing for co2 <ppm> into <target>
        m_rf = re.match(r"^calculate\s+radiative\s+forcing\s+for\s+co2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rf:
            return f"set {m_rf.group(2)} to climate_radiative_forcing({m_rf.group(1)})"

        
        m_co2e_alt = re.match(r"^convert\s+co2\s+equivalent\s+for\s+gas\s+(.+?)\s+amount\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_co2e_alt:
            return f"set {m_co2e_alt.group(3)} to climate_co2_equivalent({m_co2e_alt.group(2)}, {m_co2e_alt.group(1)})"

        m_rf_alt = re.match(r"^calculate\s+radiative\s+forcing\s+for\s+c\s+(.+?)\s+c0\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rf_alt:
            return f"set {m_rf_alt.group(3)} to climate_radiative_forcing({m_rf_alt.group(1)}, {m_rf_alt.group(2)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Climate domain does not define declarative blocks")
