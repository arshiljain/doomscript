"""Crypto ZK Domain Runtime: Shamir Secret Sharing, Pedersen Commitments, Diffie-Hellman, Merkle Trees, and Schnorr ZK."""
import hashlib
import random
from typing import List, Dict, Any, Tuple

PRIME = 2147483647  # Mersenne prime 2^31 - 1

def crypto_shamir_split(secret: int, num_shares: int, threshold: int) -> List[Tuple[int, int]]:
    """Splits an integer secret into N polynomial shares with given reconstruction threshold."""
    secret = int(secret)
    coeffs = [secret] + [random.randint(1, PRIME - 1) for _ in range(threshold - 1)]
    shares = []
    for x in range(1, num_shares + 1):
        y = sum(c * (x ** exp) for exp, c in enumerate(coeffs)) % PRIME
        shares.append((x, y))
    return shares

def crypto_shamir_reconstruct(shares: List[Tuple[int, int]]) -> int:
    """Reconstructs the secret from polynomial shares using Lagrange interpolation."""
    secret = 0
    for i, (x_i, y_i) in enumerate(shares):
        num = 1
        den = 1
        for j, (x_j, _) in enumerate(shares):
            if i != j:
                num = (num * (-x_j)) % PRIME
                den = (den * (x_i - x_j)) % PRIME
        inv_den = pow(den, PRIME - 2, PRIME)
        basis = (num * inv_den) % PRIME
        secret = (secret + y_i * basis) % PRIME
    return secret

def crypto_pedersen_commit(message: int, blinding: int, g: int = 4, h: int = 9, p: int = PRIME) -> int:
    """Computes Pedersen Commitment C = g^m * h^r mod p."""
    m = int(message)
    r = int(blinding)
    return (pow(g, m, p) * pow(h, r, p)) % p

def crypto_diffie_hellman(private_a: int, public_b: int, p: int = PRIME) -> int:
    """Computes Diffie-Hellman shared key = (B^a) mod p."""
    return pow(int(public_b), int(private_a), p)

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def crypto_merkle_tree(leaf_values: List[Any]) -> Dict[str, Any]:
    """Builds a binary Merkle Tree from a list of leaf values."""
    if not leaf_values:
        return {"root": "", "levels": []}
    current_level = [_sha256(str(v)) for v in leaf_values]
    levels = [current_level]
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1] if i + 1 < len(current_level) else left
            next_level.append(_sha256(left + right))
        levels.append(next_level)
        current_level = next_level
    return {"root": current_level[0], "levels": levels}

def crypto_merkle_verify(leaf_value: Any, proof_hashes: List[str], proof_directions: List[str], expected_root: str) -> bool:
    """Verifies a Merkle inclusion proof."""
    curr = _sha256(str(leaf_value))
    for sibling, direction in zip(proof_hashes, proof_directions):
        if direction == "left":
            curr = _sha256(sibling + curr)
        else:
            curr = _sha256(curr + sibling)
    return curr == expected_root

def crypto_schnorr_prove(secret_x: int, g: int = 3, p: int = PRIME) -> Dict[str, int]:
    """Non-interactive Schnorr zero-knowledge proof of knowledge of discrete log (Fiat-Shamir)."""
    x = int(secret_x)
    y = pow(g, x, p)
    v = random.randint(1, p - 2)
    t = pow(g, v, p)
    # Fiat-Shamir hash challenge
    c = int(hashlib.sha256(f"{g}:{y}:{t}".encode()).hexdigest(), 16) % (p - 1)
    r = (v - c * x) % (p - 1)
    return {"public_y": y, "t": t, "c": c, "r": r}

def crypto_schnorr_verify_proof(proof: Dict[str, int], g: int = 3, p: int = PRIME) -> bool:
    """Verifies a non-interactive Schnorr zero-knowledge proof."""
    y = int(proof["public_y"])
    t = int(proof["t"])
    c = int(proof["c"])
    r = int(proof["r"])
    # Check if g^r * y^c mod p == t
    lhs = (pow(g, r, p) * pow(y, c, p)) % p
    calc_c = int(hashlib.sha256(f"{g}:{y}:{t}".encode()).hexdigest(), 16) % (p - 1)
    return lhs == t and calc_c == c
