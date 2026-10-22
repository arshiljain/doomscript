import re
from typing import Optional
from doomscript.domains.base import DomainParser

class CryptoZkDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_split = re.match(r"^split\s+secret\s+(.+?)\s+into\s+(\d+|[A-Za-z_]\w*)\s+shares\s+with\s+threshold\s+(\d+|[A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_split:
            return f"set {m_split.group(4)} to zk_shamir_split({m_split.group(1)}, {m_split.group(2)}, {m_split.group(3)})"

        m_rec = re.match(r"^reconstruct\s+secret\s+from\s+shares\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rec:
            return f"set {m_rec.group(2)} to zk_shamir_reconstruct({m_rec.group(1)})"

        m_ped = re.match(r"^create\s+pedersen\s+commitment\s+for\s+message\s+(.+?)\s+with\s+blinding\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ped:
            return f"set {m_ped.group(3)} to zk_pedersen_commit({m_ped.group(1)}, {m_ped.group(2)})"

        m_dh = re.match(r"^perform\s+diffie\s+hellman\s+between\s+private\s+(.+?)\s+and\s+public\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dh:
            return f"set {m_dh.group(3)} to zk_diffie_hellman({m_dh.group(1)}, {m_dh.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Crypto ZK domain does not define declarative blocks")
