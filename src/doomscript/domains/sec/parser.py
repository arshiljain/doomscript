"""Cybersecurity Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class SecDomainParser(DomainParser):
    """Parses spoken-English cybersecurity and cryptanalysis statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate password entropy for <pass> into <target>
        m_ent = re.match(
            r"^calculate\s+password\s+entropy\s+for\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ent:
            pwd = m_ent.group(1).strip()
            target = m_ent.group(2).strip()
            return f"set {target} to sec_password_entropy({pwd})"

        # audit password strength for <pass> into <target>
        m_audit = re.match(
            r"^audit\s+password\s+strength\s+for\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_audit:
            pwd = m_audit.group(1).strip()
            target = m_audit.group(2).strip()
            return f"set {target} to sec_password_audit({pwd})"

        # crack caesar cipher <ciphertext> into <target>
        m_caesar = re.match(
            r"^crack\s+caesar\s+cipher\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_caesar:
            ctx = m_caesar.group(1).strip()
            target = m_caesar.group(2).strip()
            return f"set {target} to sec_caesar_crack({ctx})"

        # encode text <text> with vigenere key <key> into <target>
        m_vig_enc = re.match(
            r"^encode\s+text\s+(.+?)\s+with\s+vigenere\s+key\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vig_enc:
            txt = m_vig_enc.group(1).strip()
            k = m_vig_enc.group(2).strip()
            target = m_vig_enc.group(3).strip()
            return f"set {target} to sec_vigenere_encode({txt}, {k})"

        # decode vigenere <text> with key <key> into <target>
        m_vig_dec = re.match(
            r"^decode\s+vigenere\s+(.+?)\s+with\s+key\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vig_dec:
            ctx = m_vig_dec.group(1).strip()
            k = m_vig_dec.group(2).strip()
            target = m_vig_dec.group(3).strip()
            return f"set {target} to sec_vigenere_decode({ctx}, {k})"

        # frequency analysis of <text> into <target>
        m_freq = re.match(
            r"^frequency\s+analysis\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_freq:
            txt = m_freq.group(1).strip()
            target = m_freq.group(2).strip()
            return f"set {target} to sec_frequency_analysis({txt})"

        # xor encrypt <text> with key <key> into <target>
        m_xor = re.match(
            r"^xor\s+encrypt\s+(.+?)\s+with\s+key\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_xor:
            txt = m_xor.group(1).strip()
            k = m_xor.group(2).strip()
            target = m_xor.group(3).strip()
            return f"set {target} to sec_xor_cipher({txt}, {k})"

        # decode jwt token <token> into <target>
        m_jwt_dec = re.match(
            r"^decode\s+jwt\s+token\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_jwt_dec:
            tok = m_jwt_dec.group(1).strip()
            target = m_jwt_dec.group(2).strip()
            return f"set {target} to sec_jwt_decode({tok})"

        # verify jwt token <token> with secret <sec> into <target>
        m_jwt_ver = re.match(
            r"^verify\s+jwt\s+token\s+(.+?)\s+with\s+secret\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_jwt_ver:
            tok = m_jwt_ver.group(1).strip()
            sec = m_jwt_ver.group(2).strip()
            target = m_jwt_ver.group(3).strip()
            return f"set {target} to sec_jwt_verify({tok}, {sec})"

        # generate hexdump of <data> into <target>
        m_hex = re.match(
            r"^generate\s+hexdump\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hex:
            data = m_hex.group(1).strip()
            target = m_hex.group(2).strip()
            return f"set {target} to sec_hexdump({data})"

        # calculate cvss score with metrics <metrics> into <target>
        m_cvss = re.match(
            r"^calculate\s+cvss\s+score\s+with\s+(?:metrics|base_metrics)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cvss:
            met = m_cvss.group(1).strip()
            target = m_cvss.group(2).strip()
            return f"set {target} to sec_cvss_score({met})"

        # parse port banner <banner> into <target>
        m_ban = re.match(
            r"^parse\s+port\s+banner\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ban:
            banner = m_ban.group(1).strip()
            target = m_ban.group(2).strip()
            return f"set {target} to sec_parse_banner({banner})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Sec domain does not define declarative blocks")
