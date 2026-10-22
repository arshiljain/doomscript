import re
from typing import Optional
from doomscript.domains.base import DomainParser

class ForensicsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_magic = re.match(r"^identify\s+file\s+type\s+by\s+magic\s+bytes\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_magic:
            return f"set {m_magic.group(2)} to forensics_magic_bytes({m_magic.group(1)})"

        m_ent = re.match(r"^calculate\s+shannon\s+entropy\s+for\s+data\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ent:
            return f"set {m_ent.group(2)} to forensics_shannon_entropy({m_ent.group(1)})"

        m_b64 = re.match(r"^deobfuscate\s+nested\s+base64\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_b64:
            return f"set {m_b64.group(2)} to forensics_deobfuscate_base64({m_b64.group(1)})"

        m_dga = re.match(r"^check\s+dga\s+domain\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dga:
            return f"set {m_dga.group(2)} to forensics_dga_score({m_dga.group(1)})"

        m_sled = re.match(r"^check\s+nop\s+sled\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sled:
            return f"set {m_sled.group(2)} to forensics_detect_shellcode_nop_sled({m_sled.group(1)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Forensics domain does not define declarative blocks")
