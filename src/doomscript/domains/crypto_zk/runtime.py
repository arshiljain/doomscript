"""Zero-Knowledge and Advanced Cryptography: Shamir secret sharing, Pedersen commitments, Diffie-Hellman."""
import random
import hashlib
from typing import List, Tuple, Dict, Any

# Standard prime for finite field operations
FIELD_PRIME = 2**127 - 1  # Mersenne prime M127

def zk_shamir_split(secret: int, n: int, k: int) -> List[Tuple[int, int]]:
    """Splits an integer secret into n shares with threshold k using Shamir Secret Sharing."""
    secret = int(secret) % FIELD_PRIME
    n = int(n)
    k = int(k)
    coeffs = [secret] + [random.randint(1, FIELD_PRIME - 1) for _ in range(k - 1)]
    shares = []
    for x in range(1, n + 1):
        y = sum(c * pow(x, exp, FIELD_PRIME) for exp, c in enumerate(coeffs)) % FIELD_PRIME
        shares.append((x, y))
    return shares

def zk_shamir_reconstruct(shares: List[Tuple[int, int]]) -> int:
    """Reconstructs the original secret from k shares using Lagrange interpolation."""
    secret = 0
    for i, (xi, yi) in enumerate(shares):
        num = 1
        den = 1
        for j, (xj, _) in enumerate(shares):
            if i != j:
                num = (num * (-xj)) % FIELD_PRIME
                den = (den * (xi - xj)) % FIELD_PRIME
        inv_den = pow(den, FIELD_PRIME - 2, FIELD_PRIME)
        li = (num * inv_den) % FIELD_PRIME
        secret = (secret + yi * li) % FIELD_PRIME
    return secret

def zk_pedersen_commit(m: int, r: int, g: int = 5, h: int = 7) -> int:
    """Creates a Pedersen commitment c = (g^m * h^r) mod FIELD_PRIME."""
    m = int(m)
    r = int(r)
    return (pow(g, m, FIELD_PRIME) * pow(h, r, FIELD_PRIME)) % FIELD_PRIME

def zk_pedersen_verify(c: int, m: int, r: int, g: int = 5, h: int = 7) -> bool:
    """Verifies that commitment c opens to message m with blinding factor r."""
    return int(c) == zk_pedersen_commit(m, r, g, h)

def zk_diffie_hellman(priv_a: int, pub_b: int, p: int = FIELD_PRIME) -> int:
    """Derives shared secret s = pub_b ^ priv_a mod p."""
    return pow(int(pub_b), int(priv_a), int(p))
