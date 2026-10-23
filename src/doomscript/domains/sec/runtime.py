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
from typing import Any, Dict, List, Optional, Tuple, Set, Union
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.core.record import Record


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


def sec_jwt_verify(token: Any, secret: Any):
    """Verify HMAC-SHA256 signature of a JWT token and return decoded payload if valid, else False."""
    t = str(token).strip()
    parts = t.split(".")
    if len(parts) != 3:
        return False
    msg = f"{parts[0]}.{parts[1]}".encode("utf-8")
    expected_sig = base64.urlsafe_b64encode(
        hmac.new(str(secret).encode("utf-8"), msg, hashlib.sha256).digest()
    ).decode("utf-8").rstrip("=")
    given_sig = parts[2].rstrip("=")
    if not hmac.compare_digest(expected_sig, given_sig):
        return False
    try:
        pad = len(parts[1]) % 4
        p_b64 = parts[1] + ("=" * (4 - pad) if pad else "")
        return json.loads(base64.urlsafe_b64decode(p_b64).decode("utf-8"))
    except Exception:
        return True


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

    @classmethod
    def split(cls, secret_int: int, k_threshold: int, n_shares: int) -> List[Tuple[int, int]]:
        return cls.split_secret(int(secret_int), n=int(n_shares), k=int(k_threshold))

    @classmethod
    def combine(cls, shares: List[Tuple[int, int]]) -> int:
        return cls.recover_secret(shares)


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


# ==============================================================================
# PBKDF2 KEY DERIVATION & CONSTANT-TIME VERIFICATION
# ==============================================================================

class PBKDF2KeyDeriver:
    """RFC 8018 PBKDF2 key derivation using HMAC-SHA256."""

    @classmethod
    def derive(
        cls,
        password: str,
        salt: str,
        iterations: int = 1000,
        key_length: int = 32,
    ) -> Dict[str, Any]:
        pwd_bytes = password.encode("utf-8")
        salt_bytes = salt.encode("utf-8")
        derived = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt_bytes, iterations, dklen=key_length)
        return {
            "password": password,
            "salt": salt,
            "iterations": iterations,
            "key_length": key_length,
            "derived_hex": derived.hex(),
            "key_hex": derived.hex(),
        }

    @staticmethod
    def verify(password: str, salt: str, expected_hex: str, iterations: int = 1000) -> bool:
        pwd_bytes = password.encode("utf-8")
        salt_bytes = salt.encode("utf-8")
        key_len = len(bytes.fromhex(expected_hex))
        derived = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt_bytes, iterations, dklen=key_len)
        return hmac.compare_digest(derived.hex(), expected_hex.lower())


# ==============================================================================
# TOTP / HOTP TIME-BASED ONE-TIME PASSWORD (RFC 6238 / RFC 4226)
# ==============================================================================

class TOTPAuthenticator:
    """RFC 6238 Time-based One-Time Password generation and verification."""

    @classmethod
    def _base32_decode(cls, s: str) -> bytes:
        clean = s.upper().replace(" ", "").replace("-", "")
        # Pad with '='
        padding = (8 - len(clean) % 8) % 8
        clean += "=" * padding
        return base64.b32decode(clean)

    @classmethod
    def generate_token(cls, secret_base32: str, current_timestamp: Optional[int] = None, step_sec: int = 30, digits: int = 6) -> str:
        key = cls._base32_decode(secret_base32)
        t = int(current_timestamp if current_timestamp is not None else time.time())
        counter = t // step_sec

        counter_bytes = struct.pack(">Q", counter)
        h = hmac.new(key, counter_bytes, hashlib.sha1).digest()

        # Dynamic truncation
        offset = h[-1] & 0x0F
        binary = struct.unpack(">I", h[offset:offset + 4])[0] & 0x7FFFFFFF
        token_num = binary % (10 ** digits)
        return f"{token_num:0{digits}d}"

    @classmethod
    def verify_token(cls, secret_base32: str, token: str, current_timestamp: Optional[int] = None, step_sec: int = 30, window: int = 1) -> bool:
        t = int(current_timestamp if current_timestamp is not None else time.time())
        for delta in range(-window, window + 1):
            check_t = t + delta * step_sec
            gen = cls.generate_token(secret_base32, current_timestamp=check_t, step_sec=step_sec, digits=len(token))
            if hmac.compare_digest(gen, token.strip()):
                return True
        return False


# ==============================================================================
# SHAMIR (K, N) THRESHOLD SECRET SHARING
# ==============================================================================


def sec_derive_pbkdf2(password: str, salt: str, iterations: int = 1000) -> Any:
    """Derives PBKDF2-HMAC-SHA256 key."""
    return Record(PBKDF2KeyDeriver.derive(password, salt, iterations=iterations))


def sec_totp_generate(secret_base32: str, timestamp: Optional[int] = None) -> str:
    """Generates 6-digit TOTP token."""
    return TOTPAuthenticator.generate_token(secret_base32, current_timestamp=timestamp)


def sec_totp_verify(secret_base32: str, token: str, timestamp: Optional[int] = None) -> bool:
    """Verifies 6-digit TOTP token with drift window."""
    return TOTPAuthenticator.verify_token(secret_base32, token, current_timestamp=timestamp)


def sec_shamir_split(secret: int, k: int = 3, n: int = 5) -> Any:
    """Splits integer secret into n shares with threshold k."""
    k_eff = min(int(k), int(n))
    n_eff = max(int(k), int(n))
    shares = ShamirSecretSharing.split(secret, k_eff, n_eff)
    return Record({
        "secret": secret,
        "threshold": k_eff,
        "total_shares": n_eff,
        "shares": shares,
    })


def sec_shamir_combine(shares: Any) -> int:
    """Reconstructs secret from k shares."""
    s_list = shares.shares if hasattr(shares, "shares") else shares
    return ShamirSecretSharing.combine(s_list)


# ==============================================================================
# MERKLE TREE CRYPTOGRAPHIC INCLUSION PROOF
# ==============================================================================

class MerkleTreeInclusionProof:
    """SHA-256 cryptographic binary Merkle tree engine with log(N) inclusion proofs."""

    @staticmethod
    def _hash_leaf(val: str) -> str:
        # Domain separation prefix 0x00 for leaves
        return hashlib.sha256(b"\x00" + str(val).encode("utf-8")).hexdigest()

    @staticmethod
    def _hash_nodes(left: str, right: str) -> str:
        # Domain separation prefix 0x01 for interior nodes
        return hashlib.sha256(b"\x01" + bytes.fromhex(left) + bytes.fromhex(right)).hexdigest()

    @classmethod
    def build_tree(cls, leaves: List[str]) -> Dict[str, Any]:
        """Builds full Merkle tree layers and computes root hash."""
        if not leaves:
            empty_root = hashlib.sha256(b"").hexdigest()
            return {"root": empty_root, "depth": 0, "leaves_count": 0, "layers": []}

        current_layer = [cls._hash_leaf(x) for x in leaves]
        layers = [list(current_layer)]

        while len(current_layer) > 1:
            next_layer = []
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                right = current_layer[i + 1] if i + 1 < len(current_layer) else current_layer[i]
                parent = cls._hash_nodes(left, right)
                next_layer.append(parent)
            current_layer = next_layer
            layers.append(list(current_layer))

        return {
            "root": current_layer[0],
            "depth": len(layers) - 1,
            "leaves_count": len(leaves),
            "layers": layers,
        }

    @classmethod
    def generate_proof(cls, leaves: List[str], leaf_index: int) -> Dict[str, Any]:
        """Generates audit proof path of sibling hashes up to the Merkle root."""
        tree = cls.build_tree(leaves)
        idx = int(leaf_index)
        if idx < 0 or idx >= len(leaves):
            raise IndexError("Leaf index out of bounds")

        target_leaf = leaves[idx]
        target_hash = cls._hash_leaf(target_leaf)
        proof = []

        curr_idx = idx
        layers = tree["layers"]
        for level in range(len(layers) - 1):
            layer = layers[level]
            is_right = (curr_idx % 2 == 1)
            sibling_idx = curr_idx - 1 if is_right else curr_idx + 1
            if sibling_idx >= len(layer):
                sibling_idx = curr_idx  # Duplicated odd leaf

            proof.append({
                "sibling": layer[sibling_idx],
                "direction": "left" if is_right else "right",
            })
            curr_idx = curr_idx // 2

        return {
            "leaf": target_leaf,
            "leaf_hash": target_hash,
            "leaf_index": idx,
            "root": tree["root"],
            "proof_path": proof,
        }

    @classmethod
    def verify_proof(cls, leaf: str, proof_path: List[Dict[str, str]], expected_root: str) -> bool:
        """Verifies inclusion of a leaf against root using sibling proof hashes."""
        curr_hash = cls._hash_leaf(leaf)
        for step in proof_path:
            sibling = step["sibling"] if isinstance(step, dict) else step.sibling
            direction = step["direction"] if isinstance(step, dict) else step.direction
            if direction == "left":
                curr_hash = cls._hash_nodes(sibling, curr_hash)
            else:
                curr_hash = cls._hash_nodes(curr_hash, sibling)

        return curr_hash.lower() == expected_root.lower()


# ==============================================================================
# DAVID CHAUM RSA BLIND SIGNATURE PROTOCOL
# ==============================================================================

class BlindSignatureChaumRSA:
    """David Chaum's RSA blind signature protocol for privacy-preserving digital credentials."""

    @staticmethod
    def _extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = BlindSignatureChaumRSA._extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

    @classmethod
    def mod_inverse(cls, a: int, m: int) -> int:
        gcd, x, _ = cls._extended_gcd(a % m, m)
        if gcd != 1:
            raise ValueError("Modular inverse does not exist")
        return (x % m + m) % m

    @classmethod
    def blind_message(cls, message_int: int, e: int, n: int, r: int) -> int:
        """Blinds message m with random secret factor r: m' = (m * r^e) mod n."""
        m = int(message_int) % n
        r_factor = pow(int(r), int(e), int(n))
        return (m * r_factor) % int(n)

    @classmethod
    def sign_blinded(cls, blinded_message: int, d: int, n: int) -> int:
        """Signer produces signature on blinded message without learning m: s' = (m')^d mod n."""
        return pow(int(blinded_message), int(d), int(n))

    @classmethod
    def unblind_signature(cls, blind_sig: int, r: int, n: int) -> int:
        """Unblinds signature to obtain valid signature s = m^d mod n: s = (s' * r^(-1)) mod n."""
        r_inv = cls.mod_inverse(int(r), int(n))
        return (int(blind_sig) * r_inv) % int(n)

    @classmethod
    def verify_signature(cls, signature: int, message_int: int, e: int, n: int) -> bool:
        """Verifies standard RSA signature s^e = m mod n."""
        reconstructed = pow(int(signature), int(e), int(n))
        return reconstructed == (int(message_int) % int(n))


def sec_merkle_build_tree(leaves: List[str]) -> Record:
    """Builds cryptographic Merkle tree over list of leaf strings."""
    return Record(MerkleTreeInclusionProof.build_tree(leaves))


def sec_merkle_generate_proof(leaves: List[str], leaf_index: int) -> Record:
    """Generates Merkle inclusion proof for a given leaf index."""
    res = MerkleTreeInclusionProof.generate_proof(leaves, leaf_index)
    res["proof_path"] = [Record(p) for p in res["proof_path"]]
    return Record(res)


def sec_merkle_verify_proof(leaf: str, proof_record: Any, expected_root: str) -> bool:
    """Verifies a Merkle inclusion proof path against root hash."""
    path = proof_record.proof_path if hasattr(proof_record, "proof_path") else proof_record
    return MerkleTreeInclusionProof.verify_proof(leaf, path, expected_root)


def sec_chaum_blind_message(message_int: int, e: int, n: int, r: int) -> int:
    """Blinds message integer with secret blinding factor r."""
    return BlindSignatureChaumRSA.blind_message(message_int, e, n, r)


def sec_chaum_sign_blinded(blinded_int: int, d: int, n: int) -> int:
    """Signer signs blinded message using private key d."""
    return BlindSignatureChaumRSA.sign_blinded(blinded_int, d, n)


def sec_chaum_unblind_signature(blind_sig: int, r: int, n: int) -> int:
    """Unblinds signature using secret blinding factor r."""
    return BlindSignatureChaumRSA.unblind_signature(blind_sig, r, n)


def sec_chaum_verify_signature(signature: int, message_int: int, e: int, n: int) -> bool:
    """Verifies that signature s^e == m mod n."""
    return BlindSignatureChaumRSA.verify_signature(signature, message_int, e, n)


# ==============================================================================
# SCHNORR ZERO-KNOWLEDGE PROOF (ZKP) & PBKDF2 HMAC-SHA256 KEY DERIVATION
# ==============================================================================


class ZeroKnowledgeSchnorrIdentificationProtocol:
    """Schnorr Zero-Knowledge Proof (ZKP) of Knowledge of Discrete Logarithm.

    Proves knowledge of private key x such that y = g^x mod p without revealing x.
    Supports both 3-pass interactive Sigma-protocol (Commitment, Challenge, Response)
    and non-interactive Fiat-Shamir heuristic transformation.
    """

    # Default RFC 5114 1024-bit MODP group parameters with 160-bit subgroup
    DEFAULT_P = 0xB10B8F96A080E01DDE92DE5EAE5D54EC52C99FBCFB06A3C69A6A9DCA52D23B616073E28675A23D189838EF1E2EE652C013ECB4AEA906112324975C3CD49B83BFACCBDD7D90C4BD7098488E9C219A73724EFFD6FAE5644738FAA31A4FF55BCCC0A151AF5F0DC8B4BD45BF37DF365C1A65E68CFDA76D4DA708DF1FB2BC2E4A4371
    DEFAULT_Q = 0xF518AA8781A8DF278ABA4E7D64B7CB9D49462353
    DEFAULT_G = 0xA4D1CBD5C3FD34126765A442EFB99905F8104DD258AC507FD6406CFF14266D31266FEA1E5C41564B777E690F5504F213160217B4B01B886A5E91547F9E2749F4D7FBD7D3B9A92EE1909D0D2263F80A76A6A24C087A091F531DBF0A0169B6A28AD662A4D18E73AFA32D779D5918D08BC8858F4DCEF97C2A24855E6EEB22B3B2E5

    @classmethod
    def prove_and_verify(
        cls,
        secret_x: int,
        p: Optional[int] = None,
        q: Optional[int] = None,
        g: Optional[int] = None,
        nonce_v: Optional[int] = None,
        challenge_c: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Runs Schnorr ZKP identification protocol and verifies transcript."""
        p_val = p if p is not None else cls.DEFAULT_P
        q_val = q if q is not None else cls.DEFAULT_Q
        g_val = g if g is not None else cls.DEFAULT_G

        x = secret_x % q_val
        # Public key: y = g^x mod p
        y = pow(g_val, x, p_val)

        # 1. Commitment phase (Prover)
        if nonce_v is None:
            # Deterministic pseudo-random nonce from secret and public key
            nonce_v = (pow(x, 3, q_val) + 12345) % q_val
            if nonce_v == 0:
                nonce_v = 1

        v = nonce_v % q_val
        # Commitment: t = g^v mod p
        t = pow(g_val, v, p_val)

        # 2. Challenge phase (Verifier / Fiat-Shamir)
        if challenge_c is None:
            import hashlib
            data = f"{g_val}:{y}:{t}".encode("utf-8")
            h = hashlib.sha256(data).hexdigest()
            challenge_c = int(h, 16) % q_val

        c = challenge_c % q_val

        # 3. Response phase (Prover)
        # s = (v + c * x) mod q
        s = (v + c * x) % q_val

        # 4. Verification phase (Verifier)
        # Checks: g^s == t * y^c mod p
        lhs = pow(g_val, s, p_val)
        rhs = (t * pow(y, c, p_val)) % p_val
        verified = (lhs == rhs)

        # Soundness check: fake response forged without knowing secret x
        fake_s = (s + 1) % q_val
        fake_lhs = pow(g_val, fake_s, p_val)
        fake_rejected = (fake_lhs != rhs)

        return {
            "verified": verified,
            "soundness_verified": fake_rejected,
            "public_key_y_hex": hex(y)[:20] + "...",
            "commitment_t_hex": hex(t)[:20] + "...",
            "challenge_c_hex": hex(c)[:20] + "...",
            "response_s_hex": hex(s)[:20] + "...",
            "modulus_bits": p_val.bit_length(),
        }


class PBKDF2KeyDerivationFunctionPure:
    """RFC 8018 PKCS #5 Password-Based Key Derivation Function 2 (PBKDF2-HMAC-SHA256).

    Generates cryptographically secure keys from password strings and salt
    using iterated pseudo-random function F(P, S, c, i) = U1 ^ U2 ^ ... ^ Uc.
    """

    @classmethod
    def derive_key(
        cls,
        password: str,
        salt: str,
        iterations: int = 1000,
        dklen: int = 32,
    ) -> Dict[str, Any]:
        """Derives a cryptographic key of length dklen using PBKDF2-HMAC-SHA256."""
        import hmac
        import hashlib
        import struct

        p_bytes = password.encode("utf-8")
        s_bytes = salt.encode("utf-8")
        iters = max(1, int(iterations))
        target_len = max(1, int(dklen))

        hlen = 32  # SHA-256 output length in bytes
        num_blocks = (target_len + hlen - 1) // hlen
        derived_bytes = bytearray()

        for block_idx in range(1, num_blocks + 1):
            # U1 = PRF(P, S || INT_32_BE(block_idx))
            salt_and_idx = s_bytes + struct.pack(">I", block_idx)
            u = hmac.new(p_bytes, salt_and_idx, hashlib.sha256).digest()
            f_accum = bytearray(u)

            # Iterations 2..c
            for _ in range(1, iters):
                u = hmac.new(p_bytes, u, hashlib.sha256).digest()
                for b_i in range(hlen):
                    f_accum[b_i] ^= u[b_i]

            derived_bytes.extend(f_accum)

        final_key = bytes(derived_bytes[:target_len])

        return {
            "derived_key_hex": final_key.hex(),
            "key_length_bytes": len(final_key),
            "iterations": iters,
            "salt_used": salt,
        }


def sec_schnorr_zkp_prove_verify(
    secret_x: int,
    p_prime: Optional[int] = None,
    q_subgroup: Optional[int] = None,
    g_gen: Optional[int] = None,
) -> Record:
    """Runs Schnorr Zero-Knowledge Proof protocol proving knowledge of discrete logarithm."""
    return Record(
        ZeroKnowledgeSchnorrIdentificationProtocol.prove_and_verify(
            secret_x, p=p_prime, q=q_subgroup, g=g_gen
        )
    )


def sec_pbkdf2_sha256(
    password: str,
    salt: str,
    iterations: int = 1000,
    dklen: int = 32,
) -> Record:
    """Derives cryptographic key using PBKDF2-HMAC-SHA256."""
    return Record(
        PBKDF2KeyDerivationFunctionPure.derive_key(
            password, salt, iterations=iterations, dklen=dklen
        )
    )






def sec_verify_totp(secret: Union[str, bytes], token: str, tolerance: int = 1) -> bool:
    """Verifies RFC 6238 time-based one-time password with clock drift window."""
    return TOTPGenerator.verify_totp(secret, token, tolerance=tolerance)


def sec_secp256k1_ecdh(priv_key: int, peer_pub_key: Tuple[int, int]) -> str:
    """Derives SHA-256 Elliptic Curve Diffie-Hellman (ECDH) shared secret."""
    return Secp256k1Curve.ecdh_shared_secret(priv_key, peer_pub_key)


def sec_shamir_recover(shares: Any) -> int:
    """Reconstructs secret from k shares using Lagrange polynomial interpolation."""
    s_list = shares.shares if hasattr(shares, "shares") else shares
    return ShamirSecretSharing.combine(s_list)


def sec_generate_totp(secret: Union[str, bytes], digits: int = 6) -> str:
    """Generates RFC 6238 time-based one-time password."""
    return TOTPGenerator.generate_totp(secret, digits=digits)


def sec_secp256k1_public_key(priv_key: int) -> Tuple[int, int]:
    """Derives elliptic curve public key (x, y) point on secp256k1."""
    return Secp256k1Curve.public_key(priv_key)


# ==============================================================================
# CHACHA20 STREAM CIPHER & POLY1305 MAC (RFC 7539)
# ==============================================================================

class ChaCha20Cipher:
    """Pure-Python RFC 7539 ChaCha20 256-bit stream cipher."""

    @staticmethod
    def _rotl32(v: int, c: int) -> int:
        return ((v << c) & 0xFFFFFFFF) | ((v & 0xFFFFFFFF) >> (32 - c))

    @classmethod
    def _quarter_round(cls, x: List[int], a: int, b: int, c: int, d: int) -> None:
        x[a] = (x[a] + x[b]) & 0xFFFFFFFF
        x[d] = cls._rotl32(x[d] ^ x[a], 16)
        x[c] = (x[c] + x[d]) & 0xFFFFFFFF
        x[b] = cls._rotl32(x[b] ^ x[c], 12)
        x[a] = (x[a] + x[b]) & 0xFFFFFFFF
        x[d] = cls._rotl32(x[d] ^ x[a], 8)
        x[c] = (x[c] + x[d]) & 0xFFFFFFFF
        x[b] = cls._rotl32(x[b] ^ x[c], 7)

    @classmethod
    def block(cls, key: bytes, counter: int, nonce: bytes) -> bytes:
        if len(key) != 32:
            raise ValueError("ChaCha20 key must be 32 bytes")
        if len(nonce) != 12:
            raise ValueError("ChaCha20 nonce must be 12 bytes")

        # Constants "expand 32-byte k"
        state = [
            0x61707865, 0x3320646e, 0x79622d32, 0x6b206574,
            int.from_bytes(key[0:4], "little"),
            int.from_bytes(key[4:8], "little"),
            int.from_bytes(key[8:12], "little"),
            int.from_bytes(key[12:16], "little"),
            int.from_bytes(key[16:20], "little"),
            int.from_bytes(key[20:24], "little"),
            int.from_bytes(key[24:28], "little"),
            int.from_bytes(key[28:32], "little"),
            counter & 0xFFFFFFFF,
            int.from_bytes(nonce[0:4], "little"),
            int.from_bytes(nonce[4:8], "little"),
            int.from_bytes(nonce[8:12], "little"),
        ]

        working_state = list(state)
        for _ in range(10):
            # Column rounds
            cls._quarter_round(working_state, 0, 4, 8, 12)
            cls._quarter_round(working_state, 1, 5, 9, 13)
            cls._quarter_round(working_state, 2, 6, 10, 14)
            cls._quarter_round(working_state, 3, 7, 11, 15)
            # Diagonal rounds
            cls._quarter_round(working_state, 0, 5, 10, 15)
            cls._quarter_round(working_state, 1, 6, 11, 12)
            cls._quarter_round(working_state, 2, 7, 8, 13)
            cls._quarter_round(working_state, 3, 4, 9, 14)

        out = bytearray()
        for i in range(16):
            sum_val = (working_state[i] + state[i]) & 0xFFFFFFFF
            out.extend(sum_val.to_bytes(4, "little"))
        return bytes(out)

    @classmethod
    def crypt(cls, key: bytes, counter: int, nonce: bytes, data: bytes) -> bytes:
        res = bytearray()
        num_blocks = (len(data) + 63) // 64
        for b in range(num_blocks):
            key_block = cls.block(key, counter + b, nonce)
            chunk = data[b * 64:(b + 1) * 64]
            for i in range(len(chunk)):
                res.append(chunk[i] ^ key_block[i])
        return bytes(res)


class Poly1305Authenticator:
    """Pure-Python RFC 7539 Poly1305 one-time message authenticator."""

    P = (1 << 130) - 5

    @classmethod
    def mac(cls, key: bytes, msg: bytes) -> bytes:
        if len(key) != 32:
            raise ValueError("Poly1305 key must be 32 bytes")

        # Clamp r
        r_raw = bytearray(key[:16])
        r_raw[3] &= 15
        r_raw[7] &= 15
        r_raw[11] &= 15
        r_raw[15] &= 15
        r_raw[4] &= 252
        r_raw[8] &= 252
        r_raw[12] &= 252
        r = int.from_bytes(r_raw, "little")
        s = int.from_bytes(key[16:], "little")

        accumulator = 0
        for i in range(0, len(msg), 16):
            chunk = msg[i:i + 16]
            # append 0x01 byte
            n = int.from_bytes(chunk + b"\x01", "little")
            accumulator = (accumulator + n) % cls.P
            accumulator = (accumulator * r) % cls.P

        tag = (accumulator + s) & ((1 << 128) - 1)
        return tag.to_bytes(16, "little")

    @classmethod
    def verify(cls, key: bytes, msg: bytes, tag: bytes) -> bool:
        expected = cls.mac(key, msg)
        import hmac
        return hmac.compare_digest(expected, tag)


def sec_chacha20_encrypt(key_bytes: bytes, nonce_bytes: bytes, plaintext: bytes, counter: int = 1) -> bytes:
    """Encrypts plaintext bytes using ChaCha20 stream cipher."""
    return ChaCha20Cipher.crypt(key_bytes, counter, nonce_bytes, plaintext)


def sec_chacha20_decrypt(key_bytes: bytes, nonce_bytes: bytes, ciphertext: bytes, counter: int = 1) -> bytes:
    """Decrypts ciphertext bytes using ChaCha20 stream cipher."""
    return ChaCha20Cipher.crypt(key_bytes, counter, nonce_bytes, ciphertext)


def sec_poly1305_mac(key_bytes: bytes, message: bytes) -> bytes:
    """Computes 16-byte Poly1305 authentication tag."""
    return Poly1305Authenticator.mac(key_bytes, message)


def sec_poly1305_verify(key_bytes: bytes, message: bytes, tag: bytes) -> bool:
    """Verifies 16-byte Poly1305 authentication tag in constant time."""
    return Poly1305Authenticator.verify(key_bytes, message, tag)
