import re
from typing import Optional
from doomscript.domains.base import DomainParser

class AcousticsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_spl = re.match(r"^calculate\s+spl\s+pressure\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_spl:
            return f"set {m_spl.group(2)} to acoustics_spl_db({m_spl.group(1)})"

        m_rt = re.match(r"^calculate\s+sabine\s+rt60\s+volume\s+(.+?)\s+absorption\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rt:
            return f"set {m_rt.group(3)} to acoustics_sabine_rt60({m_rt.group(1)}, {m_rt.group(2)})"

        m_eyring = re.match(r"^calculate\s+eyring\s+rt60\s+volume\s+(.+?)\s+area\s+(.+?)\s+absorption\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_eyring:
            return f"set {m_eyring.group(4)} to acoustics_eyring_rt60({m_eyring.group(1)}, {m_eyring.group(2)}, {m_eyring.group(3)})"

        m_dop = re.match(r"^calculate\s+doppler\s+shift\s+freq\s+(.+?)\s+source_v\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dop:
            return f"set {m_dop.group(3)} to acoustics_doppler_shift({m_dop.group(1)}, {m_dop.group(2)})"

        m_decay = re.match(r"^calculate\s+sound\s+decay\s+spl\s+(.+?)\s+r1\s+(.+?)\s+r2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_decay:
            return f"set {m_decay.group(4)} to acoustics_inverse_square_decay({m_decay.group(1)}, {m_decay.group(2)}, {m_decay.group(3)})"

        m_stl = re.match(r"^calculate\s+sound\s+transmission\s+loss\s+mass\s+(.+?)\s+freq\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_stl:
            return f"set {m_stl.group(3)} to acoustics_sound_transmission_loss({m_stl.group(1)}, {m_stl.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Acoustics domain does not define declarative blocks")
