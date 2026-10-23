import re
from typing import Optional
from doomscript.domains.base import DomainParser

class AcousticsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate spl pressure <p> into <target>
        m_spl = re.match(r"^calculate\s+spl\s+pressure\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_spl:
            return f"set {m_spl.group(2)} to acoustics_spl_db({m_spl.group(1)})"

        # calculate sabine rt60 volume <v> absorption <a> into <target>
        m_sab = re.match(r"^calculate\s+sabine\s+rt60\s+volume\s+(.+?)\s+absorption\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sab:
            return f"set {m_sab.group(3)} to acoustics_sabine_rt60({m_sab.group(1)}, {m_sab.group(2)})"

        # calculate eyring rt60 volume <v> area <s> absorption <alpha> into <target>
        m_eyr = re.match(r"^calculate\s+eyring\s+rt60\s+volume\s+(.+?)\s+area\s+(.+?)\s+absorption\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_eyr:
            return f"set {m_eyr.group(4)} to acoustics_eyring_rt60({m_eyr.group(1)}, {m_eyr.group(2)}, {m_eyr.group(3)})"

        # calculate doppler shift freq <f> source_v <vs> into <target>
        m_dop = re.match(r"^calculate\s+doppler\s+shift\s+freq\s+(.+?)\s+source_v\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dop:
            return f"set {m_dop.group(3)} to acoustics_doppler_shift({m_dop.group(1)}, {m_dop.group(2)})"

        # calculate sound decay spl <spl> r1 <r1> r2 <r2> into <target>
        m_dec = re.match(r"^calculate\s+sound\s+decay\s+spl\s+(.+?)\s+r1\s+(.+?)\s+r2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dec:
            return f"set {m_dec.group(4)} to acoustics_inverse_square_decay({m_dec.group(1)}, {m_dec.group(2)}, {m_dec.group(3)})"

        # calculate sound transmission loss mass <m> freq <f> into <target>
        m_stl = re.match(r"^calculate\s+sound\s+transmission\s+loss\s+mass\s+(.+?)\s+freq\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_stl:
            return f"set {m_stl.group(3)} to acoustics_sound_transmission_loss({m_stl.group(1)}, {m_stl.group(2)})"

        # calculate a weighting freq <f> into <target>
        m_aw = re.match(r"^calculate\s+a\s+weighting\s+freq\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_aw:
            return f"set {m_aw.group(2)} to acoustics_a_weighting({m_aw.group(1)})"

        # calculate schroeder frequency volume <v> rt60 <rt> into <target>
        m_sch = re.match(r"^calculate\s+schroeder\s+frequency\s+volume\s+(.+?)\s+rt60\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sch:
            return f"set {m_sch.group(3)} to acoustics_schroeder_frequency({m_sch.group(1)}, {m_sch.group(2)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Acoustics domain does not define declarative blocks")
