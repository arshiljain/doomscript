from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.crypto_zk.runtime import (
    crypto_shamir_split, crypto_shamir_reconstruct,
    crypto_pedersen_commit, crypto_diffie_hellman,
    crypto_merkle_tree, crypto_merkle_verify,
    crypto_schnorr_prove, crypto_schnorr_verify_proof
)
from doomscript.domains.crypto_zk.parser import Crypto_zkDomainParser
from doomscript.domains.crypto_zk.exporter import Crypto_zkASTExporter

class CryptoZKRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class CryptoZKDomain(DomainContract):
    name = "crypto_zk"
    aliases = ["zkp", "zero_knowledge", "schnorr", "pedersen"]
    description = "Zero-Knowledge Proofs & Cryptography: Shamir secret sharing, Pedersen, Merkle trees, Schnorr ZK"
    parser = Crypto_zkDomainParser()
    runtime = CryptoZKRuntime()
    exporter = Crypto_zkASTExporter()
    capabilities = ["shamir_split", "shamir_reconstruct", "pedersen_commit", "diffie_hellman", "merkle_tree", "schnorr_zk"]
    verbs = [
        VerbSpec(pattern="split secret {sec:expr} into {n:expr} shares with threshold {t:expr} into {target:ident}", description="Shamir split"),
        VerbSpec(pattern="build merkle tree for leaves {leaves:expr} into {target:ident}", description="Merkle tree"),
        VerbSpec(pattern="generate schnorr zk proof for secret {s:expr} into {target:ident}", description="Schnorr proof")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("split secret ") or s.startswith("reconstruct secret ") or s.startswith("create pedersen commitment ") or s.startswith("perform diffie hellman ") or s.startswith("build merkle tree ") or s.startswith("generate schnorr zk proof ") or s.startswith("verify schnorr zk proof ")

CRYPTO_ZK_DOMAIN = CryptoZKDomain()
get_domain_registry().register(CRYPTO_ZK_DOMAIN)

__all__ = [
    "CryptoZKDomain", "CRYPTO_ZK_DOMAIN", "CryptoZKRuntime",
    "crypto_shamir_split", "crypto_shamir_reconstruct",
    "crypto_pedersen_commit", "crypto_diffie_hellman",
    "crypto_merkle_tree", "crypto_merkle_verify",
    "crypto_schnorr_prove", "crypto_schnorr_verify_proof"
]
