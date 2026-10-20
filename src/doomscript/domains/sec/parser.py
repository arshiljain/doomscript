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

        # derive pbkdf2 key for <pwd> with salt <salt> [with iterations <iter>] into <target>
        m_pbk = re.match(
            r"^derive\s+pbkdf2\s+key\s+for\s+(.+?)\s+with\s+salt\s+(.+?)(?:\s+with\s+iterations\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pbk:
            pwd = m_pbk.group(1).strip()
            salt = m_pbk.group(2).strip()
            iters = m_pbk.group(3) if m_pbk.group(3) else "1000"
            target = m_pbk.group(4).strip()
            return f"set {target} to sec_derive_pbkdf2({pwd}, {salt}, iterations={iters})"

        # generate totp token for secret <sec> [at timestamp <ts>] into <target>
        m_totp_g = re.match(
            r"^generate\s+totp\s+token\s+for\s+secret\s+(.+?)(?:\s+at\s+timestamp\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_totp_g:
            secret = m_totp_g.group(1).strip()
            ts = m_totp_g.group(2).strip() if m_totp_g.group(2) else "None"
            target = m_totp_g.group(3).strip()
            return f"set {target} to sec_totp_generate({secret}, timestamp={ts})"

        # verify totp token <tok> for secret <sec> into <target>
        m_totp_v = re.match(
            r"^verify\s+totp\s+token\s+(.+?)\s+for\s+secret\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_totp_v:
            tok = m_totp_v.group(1).strip()
            secret = m_totp_v.group(2).strip()
            target = m_totp_v.group(3).strip()
            return f"set {target} to sec_totp_verify({secret}, {tok})"

        # split secret <sec> with threshold <k> total <n> into <target>
        m_sham_s = re.match(
            r"^split\s+secret\s+(.+?)\s+with\s+threshold\s+(.+?)\s+total\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sham_s:
            sec_val = m_sham_s.group(1).strip()
            k = m_sham_s.group(2).strip()
            n = m_sham_s.group(3).strip()
            target = m_sham_s.group(4).strip()
            return f"set {target} to sec_shamir_split({sec_val}, {k}, {n})"

        # combine secret shares <shares> into <target>
        m_sham_c = re.match(
            r"^combine\s+secret\s+shares\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sham_c:
            shares = m_sham_c.group(1).strip()
            target = m_sham_c.group(2).strip()
            return f"set {target} to sec_shamir_combine({shares})"

        # build merkle tree for leaves <leaves> into <target>
        m_mt_b = re.match(
            r"^build\s+merkle\s+tree\s+for\s+leaves\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mt_b:
            leaves, target = m_mt_b.group(1).strip(), m_mt_b.group(2).strip()
            return f"set {target} to sec_merkle_build_tree({leaves})"

        # generate merkle proof for leaf index <idx> from <leaves> into <target>
        m_mt_g = re.match(
            r"^generate\s+merkle\s+proof\s+for\s+leaf\s+index\s+(.+?)\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mt_g:
            idx, leaves, target = m_mt_g.group(1).strip(), m_mt_g.group(2).strip(), m_mt_g.group(3).strip()
            return f"set {target} to sec_merkle_generate_proof({leaves}, {idx})"

        # verify merkle proof for leaf <leaf> proof <proof> root <root> into <target>
        m_mt_v = re.match(
            r"^verify\s+merkle\s+proof\s+for\s+leaf\s+(.+?)\s+proof\s+(.+?)\s+root\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mt_v:
            leaf, proof, root, target = m_mt_v.group(1).strip(), m_mt_v.group(2).strip(), m_mt_v.group(3).strip(), m_mt_v.group(4).strip()
            return f"set {target} to sec_merkle_verify_proof({leaf}, {proof}, {root})"

        # blind message <msg> with e <e> n <n> r <r> into <target>
        m_ch_b = re.match(
            r"^blind\s+message\s+(.+?)\s+with\s+e\s+(.+?)\s+n\s+(.+?)\s+r\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ch_b:
            msg, e, n, r, target = m_ch_b.group(1).strip(), m_ch_b.group(2).strip(), m_ch_b.group(3).strip(), m_ch_b.group(4).strip(), m_ch_b.group(5).strip()
            return f"set {target} to sec_chaum_blind_message({msg}, {e}, {n}, {r})"

        # sign blinded message <msg> with d <d> n <n> into <target>
        m_ch_s = re.match(
            r"^sign\s+blinded\s+message\s+(.+?)\s+with\s+d\s+(.+?)\s+n\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ch_s:
            msg, d, n, target = m_ch_s.group(1).strip(), m_ch_s.group(2).strip(), m_ch_s.group(3).strip(), m_ch_s.group(4).strip()
            return f"set {target} to sec_chaum_sign_blinded({msg}, {d}, {n})"

        # unblind signature <sig> with r <r> n <n> into <target>
        m_ch_u = re.match(
            r"^unblind\s+signature\s+(.+?)\s+with\s+r\s+(.+?)\s+n\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ch_u:
            sig, r, n, target = m_ch_u.group(1).strip(), m_ch_u.group(2).strip(), m_ch_u.group(3).strip(), m_ch_u.group(4).strip()
            return f"set {target} to sec_chaum_unblind_signature({sig}, {r}, {n})"

        # verify blind signature <sig> for message <msg> with e <e> n <n> into <target>
        m_ch_v = re.match(
            r"^verify\s+blind\s+signature\s+(.+?)\s+for\s+message\s+(.+?)\s+with\s+e\s+(.+?)\s+n\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ch_v:
            sig, msg, e, n, target = m_ch_v.group(1).strip(), m_ch_v.group(2).strip(), m_ch_v.group(3).strip(), m_ch_v.group(4).strip(), m_ch_v.group(5).strip()
            return f"set {target} to sec_chaum_verify_signature({sig}, {msg}, {e}, {n})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Sec domain does not define declarative blocks")
