from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.crypto_zk.runtime import (
    zk_shamir_split, zk_shamir_reconstruct, zk_pedersen_commit,
    zk_pedersen_verify, zk_diffie_hellman
)
from doomscript.domains.crypto_zk.parser import CryptoZkDomainParser
from doomscript.domains.crypto_zk.exporter import Crypto_zkASTExporter

class CryptoZkRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class CryptoZkDomain(DomainContract):
    name = "crypto_zk"
    aliases = ["zk", "zero_knowledge", "secret_sharing"]
    description = "Zero-Knowledge proofs, Shamir secret sharing, and Pedersen commitments"
    parser = CryptoZkDomainParser()
    runtime = CryptoZkRuntime()
    exporter = Crypto_zkASTExporter()
    capabilities = ["shamir_split", "shamir_reconstruct", "pedersen_commit", "diffie_hellman"]
    verbs = [
        VerbSpec(pattern="split secret {s:expr} into {n:expr} shares with threshold {k:expr} into {target:ident}", description="Shamir secret sharing"),
        VerbSpec(pattern="create pedersen commitment for message {m:expr} with blinding {r:expr} into {target:ident}", description="Pedersen commitment")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("split secret ") or s.startswith("reconstruct secret from shares ") or s.startswith("create pedersen commitment ") or s.startswith("perform diffie hellman ")

CRYPTO_ZK_DOMAIN = CryptoZkDomain()
get_domain_registry().register(CRYPTO_ZK_DOMAIN)

__all__ = [
    "CryptoZkDomain", "CRYPTO_ZK_DOMAIN", "CryptoZkRuntime",
    "zk_shamir_split", "zk_shamir_reconstruct", "zk_pedersen_commit",
    "zk_pedersen_verify", "zk_diffie_hellman"
]
