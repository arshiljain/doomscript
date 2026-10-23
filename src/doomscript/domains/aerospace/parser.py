import re
from typing import Optional
from doomscript.domains.base import DomainParser

class AerospaceDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate lift drag density <rho> velocity <v> wing <s> cl <cl> cd <cd> into <target>
        m_ld = re.match(r"^calculate\s+lift\s+drag\s+density\s+(.+?)\s+velocity\s+(.+?)\s+wing\s+(.+?)\s+cl\s+(.+?)\s+cd\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ld:
            return f"set {m_ld.group(6)} to aero_lift_drag({m_ld.group(1)}, {m_ld.group(2)}, {m_ld.group(3)}, {m_ld.group(4)}, {m_ld.group(5)})"

        # calculate mach number velocity <v> temp <t> into <target>
        m_mach = re.match(r"^calculate\s+mach\s+number\s+(?:for\s+)?velocity\s+(.+?)\s+(?:at\s+)?(?:temp|temperature)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mach:
            return f"set {m_mach.group(3)} to aero_mach_number({m_mach.group(1)}, {m_mach.group(2)})"

        # calculate breguet range ld <ld> velocity <v> sfc <sfc> w0 <w0> w1 <w1> into <target>
        m_brg = re.match(r"^calculate\s+breguet\s+range\s+(?:for\s+)?ld\s+(.+?)\s+velocity\s+(.+?)\s+sfc\s+(.+?)\s+w0\s+(.+?)\s+w1\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_brg:
            return f"set {m_brg.group(6)} to aero_breguet_range({m_brg.group(1)}, {m_brg.group(2)}, {m_brg.group(3)}, {m_brg.group(4)}, {m_brg.group(5)})"

        # calculate orbital velocity altitude <alt> [mass <m> radius <r>] into <target>
        m_orb = re.match(r"^calculate\s+orbital\s+velocity\s+(?:for\s+)?altitude\s+(.+?)(?:\s+mass\s+(.+?)\s+radius\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_orb:
            if m_orb.group(2) is not None:
                return f"set {m_orb.group(4)} to aerospace_orbital_velocity({m_orb.group(1)}, {m_orb.group(2)}, {m_orb.group(3)})"
            return f"set {m_orb.group(4)} to aerospace_orbital_velocity({m_orb.group(1)})"

        # calculate hohmann transfer r1 <r1> r2 <r2> into <target>
        m_hoh = re.match(r"^calculate\s+hohmann\s+transfer\s+r1\s+(.+?)\s+r2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hoh:
            return f"set {m_hoh.group(3)} to aerospace_hohmann_transfer({m_hoh.group(1)}, {m_hoh.group(2)})"

        # calculate kepler orbit periapsis <rp> apoapsis <ra> into <target>
        m_kep = re.match(r"^calculate\s+kepler\s+orbit\s+periapsis\s+(.+?)\s+apoapsis\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_kep:
            return f"set {m_kep.group(3)} to aerospace_kepler_orbit({m_kep.group(1)}, {m_kep.group(2)})"

        # calculate rocket delta v isp <isp> m0 <m0> mf <mf> into <target>
        m_tsio = re.match(r"^calculate\s+rocket\s+delta\s+v\s+isp\s+(.+?)\s+m0\s+(.+?)\s+mf\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tsio:
            return f"set {m_tsio.group(4)} to aerospace_tsiolkovsky_rocket({m_tsio.group(1)}, {m_tsio.group(2)}, {m_tsio.group(3)})"

        # calculate normal shock mach <m1> into <target>
        m_shk = re.match(r"^calculate\s+normal\s+shock\s+mach\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_shk:
            return f"set {m_shk.group(2)} to aerospace_normal_shock({m_shk.group(1)})"

        
        m_ld_alt = re.match(r"^calculate\s+lift\s+and\s+drag\s+for\s+density\s+(.+?)\s+velocity\s+(.+?)\s+area\s+(.+?)\s+cl\s+(.+?)\s+cd\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ld_alt:
            return f"set {m_ld_alt.group(6)} to aero_lift_drag({m_ld_alt.group(1)}, {m_ld_alt.group(2)}, {m_ld_alt.group(3)}, {m_ld_alt.group(4)}, {m_ld_alt.group(5)})"

        m_mach_alt = re.match(r"^calculate\s+mach\s+number\s+for\s+velocity\s+(.+?)\s+temperature\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mach_alt:
            return f"set {m_mach_alt.group(3)} to aero_mach_number({m_mach_alt.group(1)}, {m_mach_alt.group(2)})"

        m_brg_alt = re.match(r"^calculate\s+breguet\s+range\s+for\s+velocity\s+(.+?)\s+cl_cd\s+(.+?)\s+sfc\s+(.+?)\s+w_initial\s+(.+?)\s+w_final\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_brg_alt:
            return f"set {m_brg_alt.group(6)} to aero_breguet_range({m_brg_alt.group(2)}, {m_brg_alt.group(1)}, {m_brg_alt.group(3)}, {m_brg_alt.group(4)}, {m_brg_alt.group(5)})"

        m_orb_alt = re.match(r"^calculate\s+orbital\s+velocity\s+for\s+radius\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_orb_alt:
            return f"set {m_orb_alt.group(2)} to aero_circular_orbit_velocity({m_orb_alt.group(1)})"

        m_hoh_alt = re.match(r"^calculate\s+hohmann\s+transfer\s+for\s+r1\s+(.+?)\s+r2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hoh_alt:
            return f"set {m_hoh_alt.group(3)} to aero_hohmann_transfer_dv({m_hoh_alt.group(1)}, {m_hoh_alt.group(2)})"

        m_dv_alt = re.match(r"^calculate\s+rocket\s+delta\s+v\s+for\s+isp\s+(.+?)\s+m0\s+(.+?)\s+mf\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dv_alt:
            return f"set {m_dv_alt.group(4)} to aero_tsiolkovsky_rocket_equation({m_dv_alt.group(1)}, {m_dv_alt.group(2)}, {m_dv_alt.group(3)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Aerospace domain does not define declarative blocks")
