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
import struct
import time
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


# --- Deepened Cybersecurity: Shamir Secret Sharing, TOTP & Secp256k1 Curve ---

class ShamirSecretSharing:
    """Shamir's (k, n) Threshold Secret Sharing scheme using Lagrange polynomial interpolation over GF(p)."""

    # 256-bit prime modulus
    PRIME = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

    @classmethod
    def split_secret(cls, secret: int, n: int, k: int) -> List[Tuple[int, int]]:
        """Splits integer secret into n shares such that any k shares can reconstruct it."""
        import random
        if k > n:
            raise ValueError("Threshold k cannot exceed total shares n")
        if secret >= cls.PRIME or secret < 0:
            raise ValueError("Secret must be non-negative and less than field prime")

        # Coefficients for polynomial P(x) = secret + a1*x + ... + a_{k-1}*x^{k-1}
        coeffs = [secret] + [random.randint(1, cls.PRIME - 1) for _ in range(k - 1)]

        shares = []
        for x in range(1, n + 1):
            y = 0
            x_pow = 1
            for coeff in coeffs:
                y = (y + coeff * x_pow) % cls.PRIME
                x_pow = (x_pow * x) % cls.PRIME
            shares.append((x, y))

        return shares

    @classmethod
    def recover_secret(cls, shares: List[Tuple[int, int]]) -> int:
        """Recovers secret from k or more shares using Lagrange basis polynomials at x = 0."""
        k = len(shares)
        if k == 0:
            raise ValueError("At least one share required")

        p = cls.PRIME
        secret = 0

        for j in range(k):
            xj, yj = shares[j]
            # Calculate Lagrange basis polynomial l_j(0) = product_{m != j} (-xm) / (xj - xm) mod p
            numerator = 1
            denominator = 1
            for m in range(k):
                if m == j:
                    continue
                xm, _ = shares[m]
                numerator = (numerator * (-xm)) % p
                denominator = (denominator * (xj - xm)) % p

            # Modular inverse using Fermat's Little Theorem: pow(den, p - 2, p)
            inv_den = pow(denominator % p, p - 2, p)
            basis = (numerator * inv_den) % p
            secret = (secret + yj * basis) % p

        return secret

    @classmethod
    def split_bytes(cls, secret_data: bytes, n: int, k: int) -> List[Tuple[int, str]]:
        """Encodes arbitrary bytes into hex shares using Shamir threshold scheme."""
        secret_int = int.from_bytes(secret_data, byteorder="big")
        int_shares = cls.split_secret(secret_int, n, k)
        return [(x, hex(y)) for x, y in int_shares]

    @classmethod
    def recover_bytes(cls, shares: List[Tuple[int, str]]) -> bytes:
        """Recovers raw bytes from hex shares."""
        int_shares = [(x, int(y, 16)) for x, y in shares]
        secret_int = cls.recover_secret(int_shares)
        # Convert integer to bytes
        byte_len = (secret_int.bit_length() + 7) // 8
        return secret_int.to_bytes(max(1, byte_len), byteorder="big")


class TOTPGenerator:
    """RFC 6238 Time-based One-Time Password & RFC 4226 HMAC-based One-Time Password generator."""

    _BASE32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

    @classmethod
    def _base32_decode(cls, s: str) -> bytes:
        """Pure-Python standard Base32 decoding without third-party libraries."""
        clean = s.upper().replace("=", "").strip()
        binary_str = ""
        for char in clean:
            val = cls._BASE32_ALPHABET.find(char)
            if val == -1:
                continue
            binary_str += f"{val:05b}"

        # Group into 8-bit bytes
        byte_arr = bytearray()
        for i in range(0, len(binary_str) - (len(binary_str) % 8), 8):
            byte_arr.append(int(binary_str[i:i + 8], 2))
        return bytes(byte_arr)

    @classmethod
    def generate_hotp(cls, secret_bytes: bytes, counter: int, digits: int = 6) -> str:
        """Generates RFC 4226 HMAC-SHA1 counter-based OTP."""
        # 8-byte big-endian counter
        msg = struct.pack(">Q", counter)
        h = hmac.new(secret_bytes, msg, hashlib.sha1).digest()

        # Dynamic truncation (RFC 4226 section 5.4)
        offset = h[-1] & 0x0F
        binary = (
            ((h[offset] & 0x7F) << 24)
            | ((h[offset + 1] & 0xFF) << 16)
            | ((h[offset + 2] & 0xFF) << 8)
            | (h[offset + 3] & 0xFF)
        )
        otp = binary % (10 ** digits)
        return str(otp).zfill(digits)

    @classmethod
    def generate_totp(
        cls,
        secret: Union[str, bytes],
        time_step: int = 30,
        for_time: Optional[float] = None,
        digits: int = 6,
    ) -> str:
        """Generates RFC 6238 Time-Based OTP."""
        t = time.time() if for_time is None else for_time
        counter = int(t // time_step)
        secret_bytes = cls._base32_decode(secret) if isinstance(secret, str) else secret
        return cls.generate_hotp(secret_bytes, counter, digits=digits)

    @classmethod
    def verify_totp(
        cls,
        secret: Union[str, bytes],
        token: str,
        tolerance: int = 1,
        time_step: int = 30,
        for_time: Optional[float] = None,
    ) -> bool:
        """Verifies token against current time and drift tolerance windows."""
        t = time.time() if for_time is None else for_time
        base_counter = int(t // time_step)
        secret_bytes = cls._base32_decode(secret) if isinstance(secret, str) else secret

        for delta in range(-tolerance, tolerance + 1):
            expected = cls.generate_hotp(secret_bytes, base_counter + delta, digits=len(token))
            if hmac.compare_digest(expected, token.strip()):
                return True
        return False


class Secp256k1Curve:
    """Pure-Python standard library elliptic curve cryptography on secp256k1 (Bitcoin & Ethereum curve)."""

    P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    A = 0
    B = 7
    GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

    Point = Optional[Tuple[int, int]]

    @classmethod
    def is_on_curve(cls, pt: Point) -> bool:
        """Verifies point satisfies curve equation: y^2 = x^3 + 7 mod P."""
        if pt is None:
            return True
        x, y = pt
        return (pow(y, 2, cls.P) - (pow(x, 3, cls.P) + cls.B)) % cls.P == 0

    @classmethod
    def point_add(cls, p1: Point, p2: Point) -> Point:
        """Adds two elliptic curve points."""
        if p1 is None:
            return p2
        if p2 is None:
            return p1

        x1, y1 = p1
        x2, y2 = p2

        if x1 == x2:
            if (y1 + y2) % cls.P == 0:
                return None  # Point at infinity
            return cls.point_double(p1)

        # Slope m = (y2 - y1) / (x2 - x1) mod P
        m = ((y2 - y1) * pow(x2 - x1, cls.P - 2, cls.P)) % cls.P
        x3 = (m * m - x1 - x2) % cls.P
        y3 = (m * (x1 - x3) - y1) % cls.P
        return (x3, y3)

    @classmethod
    def point_double(cls, pt: Point) -> Point:
        """Doubles an elliptic curve point: 2 * P."""
        if pt is None:
            return None
        x, y = pt
        if y == 0:
            return None

        # Slope m = (3 * x^2 + A) / (2 * y) mod P
        m = ((3 * x * x + cls.A) * pow(2 * y, cls.P - 2, cls.P)) % cls.P
        x3 = (m * m - 2 * x) % cls.P
        y3 = (m * (x - x3) - y) % cls.P
        return (x3, y3)

    @classmethod
    def scalar_mult(cls, k: int, pt: Point) -> Point:
        """Multiplies point by scalar k using double-and-add algorithm."""
        k = k % cls.N
        if k == 0 or pt is None:
            return None

        result: Secp256k1Curve.Point = None
        addend = pt

        while k > 0:
            if k & 1:
                result = cls.point_add(result, addend)
            addend = cls.point_double(addend)
            k >>= 1

        return result

    @classmethod
    def public_key(cls, private_key: int) -> Tuple[int, int]:
        """Derives public key (x, y) point from private scalar key d: Q = d * G."""
        if not (1 <= private_key < cls.N):
            raise ValueError("Private key out of valid secp256k1 range")
        pt = cls.scalar_mult(private_key, (cls.GX, cls.GY))
        if pt is None:
            raise ValueError("Invalid public key computation")
        return pt

    @classmethod
    def compress_point(cls, pt: Tuple[int, int]) -> str:
        """Encodes point in compressed 33-byte format: prefix (02 or 03) + 32-byte hex x."""
        x, y = pt
        prefix = "03" if y % 2 != 0 else "02"
        return prefix + f"{x:064x}"

    @classmethod
    def ecdh_shared_secret(cls, private_key: int, peer_public_key: Tuple[int, int]) -> str:
        """Derives Elliptic Curve Diffie-Hellman (ECDH) shared secret hash."""
        shared_pt = cls.scalar_mult(private_key, peer_public_key)
        if shared_pt is None:
            raise ValueError("Point at infinity encountered in ECDH key exchange")
        # SHA-256 of the shared x coordinate
        x_bytes = shared_pt[0].to_bytes(32, byteorder="big")
        return hashlib.sha256(x_bytes).hexdigest()
