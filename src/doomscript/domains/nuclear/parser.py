"""Nuclear Domain Parser: Translates natural nuclear engineering and physics expressions into DoomScript calls."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class NuclearDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # Existing syntax
        m_dec = re.match(r"^calculate\s+radioactive\s+decay\s+initial\s+(.+?)\s+halflife\s+(.+?)\s+time\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dec:
            return f"set {m_dec.group(4)} to nuclear_radioactive_decay({m_dec.group(1)}, {m_dec.group(2)}, {m_dec.group(3)})"

        m_const = re.match(r"^calculate\s+decay\s+constant\s+halflife\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_const:
            return f"set {m_const.group(2)} to nuclear_decay_constant({m_const.group(1)})"

        m_q = re.match(r"^calculate\s+nuclear\s+q\s+value\s+mass_in\s+(.+?)\s+mass_out\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_q:
            return f"set {m_q.group(3)} to nuclear_reaction_q_value({m_q.group(1)}, {m_q.group(2)})"

        m_shield = re.match(r"^calculate\s+radiation\s+shielding\s+initial\s+(.+?)\s+attenuation\s+(.+?)\s+thickness\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_shield:
            return f"set {m_shield.group(4)} to nuclear_radiation_shielding({m_shield.group(1)}, {m_shield.group(2)}, {m_shield.group(3)})"

        m_4f = re.match(r"^calculate\s+four\s+factor\s+eta\s+(.+?)\s+epsilon\s+(.+?)\s+p\s+(.+?)\s+f\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_4f:
            return f"set {m_4f.group(5)} to nuclear_four_factor_formula({m_4f.group(1)}, {m_4f.group(2)}, {m_4f.group(3)}, {m_4f.group(4)})"

        m_hvl = re.match(r"^calculate\s+half\s+value\s+layer\s+attenuation\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hvl:
            return f"set {m_hvl.group(2)} to nuclear_half_value_layer({m_hvl.group(1)})"

        # Deepened syntax
        m_slab = re.match(r"^calculate\s+critical\s+slab\s+d\s+(.+?)\s+sigma_a\s+(.+?)\s+nu_sigma_f\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_slab:
            return f"set {m_slab.group(4)} to nuclear_critical_slab_thickness({m_slab.group(1)}, {m_slab.group(2)}, {m_slab.group(3)})"

        m_inhour = re.match(r"^calculate\s+inhour\s+period\s+prompt\s+(.+?)\s+beta\s+(.+?)\s+lambda\s+(.+?)\s+rho\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_inhour:
            return f"set {m_inhour.group(5)} to nuclear_inhour_equation({m_inhour.group(1)}, {m_inhour.group(2)}, {m_inhour.group(3)}, {m_inhour.group(4)})"

        m_sec = re.match(r"^calculate\s+secular\s+equilibrium\s+t_parent\s+(.+?)\s+t_daughter\s+(.+?)\s+activity\s+(.+?)\s+time\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sec:
            return f"set {m_sec.group(5)} to nuclear_secular_equilibrium({m_sec.group(1)}, {m_sec.group(2)}, {m_sec.group(3)}, {m_sec.group(4)})"

        m_semf = re.match(r"^calculate\s+binding\s+energy\s+protons\s+(.+?)\s+neutrons\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_semf:
            return f"set {m_semf.group(3)} to nuclear_binding_energy_weizsacker({m_semf.group(1)}, {m_semf.group(2)})"

        m_dose = re.match(r"^calculate\s+gamma\s+dose\s+activity\s+(.+?)\s+energy\s+(.+?)\s+distance\s+(.+?)(?:\s+photons\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dose:
            n_p = m_dose.group(4) if m_dose.group(4) else "1.0"
            return f"set {m_dose.group(5)} to nuclear_dose_rate_gamma({m_dose.group(1)}, {m_dose.group(2)}, {m_dose.group(3)}, {n_p})"

        m_flux = re.match(r"^calculate\s+neutron\s+flux\s+power\s+(.+?)\s+volume\s+(.+?)(?:\s+enrichment\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_flux:
            enr = m_flux.group(3) if m_flux.group(3) else "4.0"
            return f"set {m_flux.group(4)} to nuclear_thermal_neutron_flux({m_flux.group(1)}, {m_flux.group(2)}, {enr})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Nuclear domain does not define declarative blocks")
