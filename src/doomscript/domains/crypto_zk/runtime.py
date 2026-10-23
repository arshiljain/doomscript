"""Crypto ZK Domain Runtime: Finite fields, elliptic curves, Shamir secret sharing, Merkle proofs, and Schnorr zero knowledge."""
import math
import hashlib
import random
from typing import List, Dict, Any, Tuple, Optional
from doomscript.domains.base import DomainRuntime

PRIME = 1000000007

# ============================================================================
# 1. FIELD ARITHMETIC & MODULAR INVERSE
# ============================================================================

def mod_inv(a: int, p: int = PRIME) -> int:
    """Computes modular inverse via Extended Euclidean Algorithm: a * x === 1 (mod p)."""
    if a < 0:
        a = (a % p + p) % p
    t, newt = 0, 1
    r, newr = p, a
    while newr != 0:
        quotient = r // newr
        t, newt = newt, t - quotient * newt
        r, newr = newr, r - quotient * newr
    if r > 1:
        raise ValueError("Not invertible")
    if t < 0:
        t += p
    return t

def _sha256(s: str) -> str:
    """Internal SHA-256 helper returning hexadecimal digest."""
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

# ============================================================================
# 2. PRESERVED CRYPTO OPERATIONS
# ============================================================================

def crypto_shamir_split(secret: int, num_shares: int, threshold: int) -> List[Tuple[int, int]]:
    """Splits an integer secret into num_shares with recovery threshold."""
    secret = int(secret) % PRIME
    coeffs = [secret] + [random.randint(1, PRIME - 1) for _ in range(threshold - 1)]
    shares = []
    for x in range(1, int(num_shares) + 1):
        y = 0
        for power, c in enumerate(coeffs):
            y = (y + c * pow(x, power, PRIME)) % PRIME
        shares.append((x, y))
    return shares

def crypto_shamir_reconstruct(shares: List[Tuple[int, int]]) -> int:
    """Reconstructs secret from shares using Lagrange interpolation at x = 0."""
    secret = 0
    k = len(shares)
    for i in range(k):
        xi, yi = shares[i]
        num = 1
        den = 1
        for j in range(k):
            if i != j:
                xj, _ = shares[j]
                num = (num * (-xj)) % PRIME
                den = (den * (xi - xj)) % PRIME
        term = (yi * num * mod_inv(den, PRIME)) % PRIME
        secret = (secret + term) % PRIME
    return (secret + PRIME) % PRIME

def crypto_pedersen_commit(message: int, blinding: int, g: int = 4, h: int = 9, p: int = PRIME) -> int:
    """Pedersen commitment: C = g^m * h^r (mod p)."""
    m = int(message) % p
    r = int(blinding) % p
    gm = pow(g, m, p)
    hr = pow(h, r, p)
    return (gm * hr) % p

def crypto_diffie_hellman(private_a: int, public_b: int, p: int = PRIME) -> int:
    """Computes Diffie-Hellman shared secret: S = B^a (mod p)."""
    return pow(public_b, private_a, p)

def crypto_merkle_tree(leaf_values: List[Any]) -> Dict[str, Any]:
    """Builds binary Merkle tree from leaf values."""
    if not leaf_values:
        return {"root": "", "leaves": []}
    curr = [_sha256(str(v)) for v in leaf_values]
    leaves = list(curr)
    while len(curr) > 1:
        if len(curr) % 2 != 0:
            curr.append(curr[-1])
        nxt = []
        for i in range(0, len(curr), 2):
            nxt.append(_sha256(curr[i] + curr[i+1]))
        curr = nxt
    return {"root": curr[0], "leaves": leaves}

def crypto_merkle_verify(leaf_value: Any, proof_hashes: List[str], proof_directions: List[str], expected_root: str) -> bool:
    """Verifies Merkle branch audit path against expected root."""
    curr = _sha256(str(leaf_value))
    for h, d in zip(proof_hashes, proof_directions):
        if d == "left":
            curr = _sha256(h + curr)
        else:
            curr = _sha256(curr + h)
    return curr == expected_root

def crypto_schnorr_prove(secret_x: int, g: int = 3, p: int = PRIME) -> Dict[str, int]:
    """Generates non-interactive Schnorr zero-knowledge proof of discrete log."""
    y = pow(g, secret_x, p) # Public key
    v = random.randint(1, p - 2)
    t = pow(g, v, p) # Commitment
    c_str = _sha256(f"{g}:{y}:{t}")
    c = int(c_str, 16) % (p - 1) # Challenge via Fiat-Shamir
    r = (v - c * secret_x) % (p - 1) # Response
    return {"public_key": y, "commitment": t, "challenge": c, "response": r}

def crypto_schnorr_verify_proof(proof: Dict[str, int], g: int = 3, p: int = PRIME) -> bool:
    """Verifies Schnorr ZK proof: g^r * y^c === t (mod p)."""
    y = proof["public_key"]
    t = proof["commitment"]
    c = proof["challenge"]
    r = proof["response"]
    gr = pow(g, r, p)
    yc = pow(y, c, p)
    lhs = (gr * yc) % p
    return lhs == (t % p)

# ============================================================================
# 3. ELLIPTIC CURVE ARITHMETIC (WEIERSTRASS & EDWARDS)
# ============================================================================

class EllipticCurve:
    """Weierstrass Elliptic Curve over GF(p): y^2 = x^3 + a*x + b (mod p)."""
    def __init__(self, a: int, b: int, p: int = PRIME):
        self.a = a % p
        self.b = b % p
        self.p = p

    def is_on_curve(self, pt: Optional[Tuple[int, int]]) -> bool:
        if pt is None:
            return True
        x, y = pt
        return (y * y) % self.p == (x ** 3 + self.a * x + self.b) % self.p

    def add(self, p1: Optional[Tuple[int, int]], p2: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        if p1 is None: return p2
        if p2 is None: return p1
        x1, y1 = p1
        x2, y2 = p2
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if x1 == x2 and y1 == y2:
            m = ((3 * x1 * x1 + self.a) * mod_inv(2 * y1, self.p)) % self.p
        else:
            m = ((y2 - y1) * mod_inv(x2 - x1, self.p)) % self.p
        x3 = (m * m - x1 - x2) % self.p
        y3 = (m * (x1 - x3) - y1) % self.p
        return (x3, y3)

    def scalar_mul(self, k: int, pt: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        if pt is None or k == 0:
            return None
        res = None
        curr = pt
        while k > 0:
            if k & 1:
                res = self.add(res, curr)
            curr = self.add(curr, curr)
            k >>= 1
        return res

# ============================================================================
# 4. DOMAIN RUNTIME
# ============================================================================

class CryptoZKRuntime(DomainRuntime):
    """Unified runtime bridge for the Crypto ZK computational domain."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def shamir_split(self, secret: int, n: int, t: int) -> List[Tuple[int, int]]:
        return crypto_shamir_split(secret, n, t)
    def shamir_reconstruct(self, shares: List[Tuple[int, int]]) -> int:
        return crypto_shamir_reconstruct(shares)
    def pedersen(self, m: int, r: int) -> int:
        return crypto_pedersen_commit(m, r)
    def diffie_hellman(self, priv: int, pub: int) -> int:
        return crypto_diffie_hellman(priv, pub)
    def merkle_tree(self, leaves: List[Any]) -> Dict[str, Any]:
        return crypto_merkle_tree(leaves)
    def merkle_verify(self, leaf: Any, proofs: List[str], dirs: List[str], root: str) -> bool:
        return crypto_merkle_verify(leaf, proofs, dirs, root)
    def schnorr_prove(self, secret: int) -> Dict[str, int]:
        return crypto_schnorr_prove(secret)
    def schnorr_verify(self, proof: Dict[str, int]) -> bool:
        return crypto_schnorr_verify_proof(proof)
    def new_curve(self, a: int, b: int, p: int = PRIME) -> EllipticCurve:
        return EllipticCurve(a, b, p)
