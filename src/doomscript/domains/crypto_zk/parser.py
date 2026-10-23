"""Crypto ZK Domain Natural Language Parser."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class Crypto_zkDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # split secret <sec> into <n> shares with threshold <t> into <target>
        m_split = re.match(r"^split\s+secret\s+(.+?)\s+into\s+(\d+|[A-Za-z_]\w*)\s+shares\s+with\s+threshold\s+(\d+|[A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_split:
            return f"set {m_split.group(4)} to crypto_shamir_split({m_split.group(1)}, {m_split.group(2)}, {m_split.group(3)})"

        # reconstruct secret from shares <shares> into <target>
        m_rec = re.match(r"^reconstruct\s+secret\s+from\s+shares\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rec:
            return f"set {m_rec.group(2)} to crypto_shamir_reconstruct({m_rec.group(1)})"

        # create pedersen commitment for message <m> blinding <r> into <target>
        m_ped = re.match(r"^create\s+pedersen\s+commitment\s+for\s+message\s+(.+?)\s+(?:with\s+)?blinding\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ped:
            return f"set {m_ped.group(3)} to crypto_pedersen_commit({m_ped.group(1)}, {m_ped.group(2)})"

        # perform diffie hellman private <a> public <b> into <target>
        m_dh = re.match(r"^perform\s+diffie\s+hellman\s+(?:between\s+)?private\s+(.+?)\s+(?:and\s+)?public\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dh:
            return f"set {m_dh.group(3)} to crypto_diffie_hellman({m_dh.group(1)}, {m_dh.group(2)})"

        # build merkle tree for leaves <leaves> into <target>
        m_mt = re.match(r"^build\s+merkle\s+tree\s+for\s+leaves\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mt:
            return f"set {m_mt.group(2)} to crypto_merkle_tree({m_mt.group(1)})"

        # generate schnorr zk proof for secret <s> into <target>
        m_zk = re.match(r"^generate\s+schnorr\s+zk\s+proof\s+for\s+secret\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_zk:
            return f"set {m_zk.group(2)} to crypto_schnorr_prove({m_zk.group(1)})"

        # verify schnorr zk proof <proof> into <target>
        m_vr = re.match(r"^verify\s+schnorr\s+zk\s+proof\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_vr:
            return f"set {m_vr.group(2)} to crypto_schnorr_verify_proof({m_vr.group(1)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Crypto ZK domain does not define declarative blocks")
