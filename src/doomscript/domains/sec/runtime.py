"""Cybersecurity, Cryptanalysis & Security Forensics Domain Runtime for DoomScript.

Pure Python standard library implementation of password entropy analysis,
Caesar cipher chi-squared cryptanalysis, Vigenere and XOR ciphers, JWT parsing and verification,
hexdump visualization, CVSS v3.1 score calculation, and service banner analysis.
"""

import base64
import hashlib
import hmac
import json
import math
import re
from typing import Any, Dict, List, Optional, Tuple, Set
from doomscript.domains.base import DomainRuntime, DomainIR


# Standard English letter frequency distribution (%)
ENGLISH_FREQS: Dict[str, float] = {
    "A": 8.167, "B": 1.492, "C": 2.782, "D": 4.253, "E": 12.702,
    "F": 2.228, "G": 2.015, "H": 6.094, "I": 6.966, "J": 0.153,
    "K": 0.772, "L": 4.025, "M": 2.406, "N": 6.749, "O": 7.507,
    "P": 1.929, "Q": 0.095, "R": 5.987, "S": 6.327, "T": 9.056,
    "U": 2.758, "V": 0.978, "W": 2.360, "X": 0.150, "Y": 1.974, "Z": 0.074
}


class SecRuntime(DomainRuntime):
    """Runtime coordinator for cybersecurity routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


def sec_password_entropy(password: Any) -> float:
    """Calculate Shannon password entropy in bits: H = L * log2(pool_size)."""
    p = str(password)
    if not p:
        return 0.0
    pool = 0
    if re.search(r"[a-z]", p):
        pool += 26
    if re.search(r"[A-Z]", p):
        pool += 26
    if re.search(r"[0-9]", p):
        pool += 10
    if re.search(r"[^a-zA-Z0-9]", p):
        pool += 33
    if pool == 0:
        return 0.0
    entropy = len(p) * math.log2(pool)
    return round(entropy, 2)


def sec_password_audit(password: Any) -> Dict[str, Any]:
    """Audit password security, strength score (0-4), entropy, and crack resistance."""
    p = str(password)
    entropy = sec_password_entropy(p)
    issues: List[str] = []

    if len(p) < 8:
        issues.append("Too short (less than 8 characters)")
    if not re.search(r"[0-9]", p):
        issues.append("Missing numeric digits")
    if not re.search(r"[A-Z]", p):
        issues.append("Missing uppercase letters")
    if not re.search(r"[^a-zA-Z0-9]", p):
        issues.append("Missing special symbols")

    if entropy < 28:
        score = 0
        rating = "Very Weak"
    elif entropy < 40:
        score = 1
        rating = "Weak"
    elif entropy < 60:
        score = 2
        rating = "Moderate"
    elif entropy < 80:
        score = 3
        rating = "Strong"
    else:
        score = 4
        rating = "Very Strong"

    return {
        "entropy_bits": entropy,
        "score": score,
        "rating": rating,
        "length": len(p),
        "issues": issues,
    }


def sec_caesar_crack(ciphertext: Any) -> Dict[str, Any]:
    """Break Caesar cipher automatically using common English words + letter frequency analysis."""
    raw_text = str(ciphertext)
    text = raw_text.upper()
    best_shift = 0
    best_score = -1e9
    best_plain = ""

    letters = [ch for ch in text if ch.isalpha()]
    total_letters = len(letters)
    if total_letters == 0:
        return {"shift": 0, "plaintext": raw_text, "confidence": 0.0}

    common_words = {
        "THE", "BE", "TO", "OF", "AND", "A", "IN", "THAT", "HAVE", "I", "IT", "FOR",
        "NOT", "ON", "WITH", "HE", "AS", "YOU", "DO", "AT", "THIS", "BUT", "HIS",
        "BY", "FROM", "THEY", "WE", "SAY", "HER", "SHE", "OR", "AN", "WILL", "MY",
        "ONE", "ALL", "WOULD", "THERE", "THEIR", "WHAT", "SO", "UP", "OUT", "IF",
        "ABOUT", "WHO", "GET", "WHICH", "GO", "ME", "HELLO", "WORLD", "ATTACK", "DAWN", "SECRET"
    }

    for shift in range(26):
        decrypted_chars = []
        counts: Dict[str, int] = {k: 0 for k in ENGLISH_FREQS}

        for orig_ch in raw_text:
            if orig_ch.isalpha():
                base = ord("A") if orig_ch.isupper() else ord("a")
                shifted_ch = chr((ord(orig_ch) - base - shift) % 26 + base)
                decrypted_chars.append(shifted_ch)
                counts[shifted_ch.upper()] += 1
            else:
                decrypted_chars.append(orig_ch)

        candidate_plain = "".join(decrypted_chars)
        cand_upper = candidate_plain.upper()

        chi_sq = 0.0
        for ch, expected_pct in ENGLISH_FREQS.items():
            observed = counts[ch]
            expected = total_letters * (expected_pct / 100.0)
            chi_sq += ((observed - expected) ** 2) / max(0.0001, expected)

        score = -chi_sq
        words = re.findall(r"[A-Z]+", cand_upper)
        for w in words:
            if w in common_words:
                score += 50.0

        if score > best_score:
            best_score = score
            best_shift = shift
            best_plain = candidate_plain

    return {
        "shift": best_shift,
        "plaintext": best_plain,
        "chi_squared": round(-best_score, 2),
    }


def sec_vigenere_encode(plaintext: Any, key: Any) -> str:
    """Encrypt plaintext using polyalphabetic Vigenere cipher."""
    text = str(plaintext)
    k = str(key).upper()
    if not k:
        return text
    res = []
    k_idx = 0
    for ch in text:
        if ch.isalpha():
            is_upper = ch.isupper()
            base = ord("A") if is_upper else ord("a")
            shift = ord(k[k_idx % len(k)]) - ord("A")
            encoded_char = chr((ord(ch) - base + shift) % 26 + base)
            res.append(encoded_char)
            k_idx += 1
        else:
            res.append(ch)
    return "".join(res)


def sec_vigenere_decode(ciphertext: Any, key: Any) -> str:
    """Decrypt ciphertext using polyalphabetic Vigenere cipher."""
    text = str(ciphertext)
    k = str(key).upper()
    if not k:
        return text
    res = []
    k_idx = 0
    for ch in text:
        if ch.isalpha():
            is_upper = ch.isupper()
            base = ord("A") if is_upper else ord("a")
            shift = ord(k[k_idx % len(k)]) - ord("A")
            decoded_char = chr((ord(ch) - base - shift) % 26 + base)
            res.append(decoded_char)
            k_idx += 1
        else:
            res.append(ch)
    return "".join(res)


def sec_caesar_cipher(text: Any, shift: Any = 3) -> str:
    """Encrypt text using Caesar cipher with given shift."""
    res = []
    s = int(shift) % 26
    for ch in str(text):
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            res.append(chr((ord(ch) - base + s) % 26 + base))
        else:
            res.append(ch)
    return "".join(res)


def sec_vigenere_cipher(text: Any, key: Any, encode: bool = True) -> str:
    """Encrypt or decrypt text using Vigenere cipher."""
    if encode:
        return sec_vigenere_encode(text, key)
    else:
        return sec_vigenere_decode(text, key)


def sec_frequency_analysis(text: Any) -> Dict[str, float]:
    """Calculate character frequency percentage across alphabetical text."""
    s = str(text).upper()
    letters = [ch for ch in s if ch.isalpha()]
    total = len(letters)
    if total == 0:
        return {}
    counts: Dict[str, int] = {}
    for ch in letters:
        counts[ch] = counts.get(ch, 0) + 1
    return {k: round((v / total) * 100.0, 3) for k, v in sorted(counts.items(), key=lambda kv: -kv[1])}


def sec_xor_cipher(data: Any, key: Any) -> str:
    """XOR encryption/decryption. If data is hex, decodes back to text; else encodes to hex."""
    k_bytes = str(key).encode("utf-8")
    if not k_bytes:
        return str(data)
    d_str = str(data)
    is_hex = False
    if len(d_str) > 0 and len(d_str) % 2 == 0:
        try:
            d_bytes = bytes.fromhex(d_str)
            is_hex = True
        except ValueError:
            d_bytes = d_str.encode("utf-8")
    else:
        d_bytes = d_str.encode("utf-8")

    xored = bytearray(len(d_bytes))
    for i in range(len(d_bytes)):
        xored[i] = d_bytes[i] ^ k_bytes[i % len(k_bytes)]

    if is_hex:
        try:
            return xored.decode("utf-8")
        except UnicodeDecodeError:
            return xored.hex()
    return xored.hex()


def sec_jwt_decode(token: Any) -> Dict[str, Any]:
    """Decode JWT header and claims payload without cryptographic signature verification."""
    t = str(token).strip()
    parts = t.split(".")
    if len(parts) != 3:
        return {"error": "Invalid JWT format (expected 3 dot-separated parts)"}

    def _b64_decode(seg):
        padded = seg + "=" * ((4 - len(seg) % 4) % 4)
        return json.loads(base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8"))

    try:
        header = _b64_decode(parts[0])
        payload = _b64_decode(parts[1])
        return {"header": header, "payload": payload, "claims": payload, "signature": parts[2]}
    except Exception as e:
        return {"error": f"JWT decode failed: {str(e)}"}


def sec_jwt_verify(token: Any, secret: Any) -> bool:
    """Verify HMAC-SHA256 signature of a JWT token."""
    t = str(token).strip()
    parts = t.split(".")
    if len(parts) != 3:
        return False
    msg = f"{parts[0]}.{parts[1]}".encode("utf-8")
    expected_sig = base64.urlsafe_b64encode(
        hmac.new(str(secret).encode("utf-8"), msg, hashlib.sha256).digest()
    ).decode("utf-8").rstrip("=")
    given_sig = parts[2].rstrip("=")
    return hmac.compare_digest(expected_sig, given_sig)


def sec_hexdump(data: Any, max_bytes: int = 64) -> str:
    """Generate canonical hexdump formatting (offset, hex, ascii)."""
    if isinstance(data, (bytes, bytearray)):
        raw = bytes(data)[:max_bytes]
    else:
        raw = str(data).encode("utf-8")[:max_bytes]

    lines = []
    for offset in range(0, len(raw), 16):
        chunk = raw[offset:offset + 16]
        hex_bytes = " ".join(f"{b:02x}" for b in chunk)
        ascii_chars = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        lines.append(f"{offset:08x}  {hex_bytes:<48}  |{ascii_chars}|")
    return "\n".join(lines)


def sec_cvss_score(metrics: Any, *args) -> float:
    """Calculate CVSS v3.1 Base Score from metric dictionary or numbers."""
    if args:
        vals = [float(metrics)] + [float(a) for a in args]
        return round(min(10.0, max(0.0, vals[0])), 1)
    if not isinstance(metrics, dict):
        try:
            return round(float(metrics), 1)
        except Exception:
            return 0.0

    av_map = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
    ac_map = {"L": 0.77, "H": 0.44}
    pr_map = {"N": 0.85, "L": 0.62, "H": 0.27}
    ui_map = {"N": 0.85, "R": 0.62}
    c_map = {"H": 0.56, "L": 0.22, "N": 0.0}

    av = av_map.get(str(metrics.get("AV", "N")).upper(), 0.85)
    ac = ac_map.get(str(metrics.get("AC", "L")).upper(), 0.77)
    pr = pr_map.get(str(metrics.get("PR", "N")).upper(), 0.85)
    ui = ui_map.get(str(metrics.get("UI", "N")).upper(), 0.85)

    c = c_map.get(str(metrics.get("C", "H")).upper(), 0.56)
    i = c_map.get(str(metrics.get("I", "H")).upper(), 0.56)
    a = c_map.get(str(metrics.get("A", "H")).upper(), 0.56)

    iss = 1.0 - ((1.0 - c) * (1.0 - i) * (1.0 - a))
    impact = 6.42 * iss
    exploitability = 8.22 * av * ac * pr * ui

    if impact <= 0:
        return 0.0
    base_score = min(10.0, impact + exploitability)
    return round(base_score, 1)


def sec_parse_banner(banner_raw: Any) -> Dict[str, Any]:
    """Parse service name, version, and protocol hints from raw socket banner."""
    b = str(banner_raw).strip()
    res: Dict[str, Any] = {"raw": b, "service": "unknown", "version": "unknown"}

    if "SSH-" in b:
        res["service"] = "SSH"
        m = re.search(r"SSH-(\d+\.\d+)-([^\s]+)", b)
        if m:
            res["proto"] = m.group(1)
            res["version"] = m.group(2)
    elif "HTTP/" in b or "Server:" in b:
        res["service"] = "HTTP"
        m = re.search(r"Server:\s*([^\r\n]+)", b, re.IGNORECASE)
        if m:
            res["version"] = m.group(1).strip()
    elif "FTP" in b or "220" in b:
        res["service"] = "FTP"
        res["version"] = b[:40]
    elif "SMTP" in b:
        res["service"] = "SMTP"
        res["version"] = b[:40]

    return res


sec_decode_jwt = sec_jwt_decode
sec_verify_jwt = sec_jwt_verify
sec_entropy = sec_password_entropy
sec_audit_password = sec_password_audit


def execute_sec_ir(spec_id: str) -> Any:
    """Executes a stored Sec IR specification."""
    from doomscript.domains.registry import get_domain_registry
    reg = get_domain_registry()
    spec = reg.get_spec(spec_id)
    if spec is None:
        raise ValueError(f"Unknown sec spec: {spec_id}")
    return SecRuntime().execute_ir(spec, {})
