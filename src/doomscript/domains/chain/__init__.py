"""Blockchain, Merkle Trees & Cryptoeconomics Domain Pack for DoomScript.

Enables native spoken-English Merkle tree construction & proofs, Proof-of-Work mining,
UTXO ledgers, and EIP-55 address checksumming via 'use chain'.
"""

from typing import List, Optional
from doomscript.domains.base import (
    DomainContract,
    DomainParser,
    DomainRuntime,
    DomainASTExporter,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.chain.runtime import (
    ChainRuntime,
    MerkleTree,
    UtxoLedger,
    chain_merkle_tree_create,
    chain_merkle_root,
    chain_merkle_proof_verify,
    chain_mine_block,
    chain_verify_block,
    chain_utxo_ledger_create,
    chain_process_tx,
    chain_get_balance,
    chain_checksum_address,
    PatriciaMerkleTrie,
    SchnorrZKProtocol,
    RaftConsensusEngine,
    MerklePatriciaTrie,
    ProofOfStakeValidator,
    chain_mpt_create,
    chain_mpt_root,
    chain_pos_create,
    chain_pos_proposer,
    chain_pos_vote,
    EVMBytecodeInterpreterStackMachine,
    ThresholdSignatureSchemeShamir,
    chain_evm_execute,
    chain_threshold_split,
    chain_threshold_reconstruct,
    chain_threshold_aggregate_sign,
)
from doomscript.domains.chain.parser import ChainDomainParser
from doomscript.domains.chain.exporter import ChainASTExporter


class ChainDomain(DomainContract):
    """Domain contract for Blockchain & Distributed Ledgers."""

    name = "chain"
    aliases = ["blockchain", "crypto_ledger", "web3"]
    description = "Blockchain, Merkle trees, Proof-of-Work, UTXO ledgers, and EIP-55 addresses"
    parser = ChainDomainParser()
    runtime = ChainRuntime()
    exporter = ChainASTExporter()
    capabilities = ["merkle_tree", "pow_mining", "utxo_ledger", "eip55_address"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="create merkle tree from {leaves:expr} into {target:ident}",
            description="Constructs a cryptographic binary Merkle tree",
        ),
        VerbSpec(
            pattern="get merkle root of {tree:expr} into {target:ident}",
            description="Extracts the root hash of a Merkle tree",
        ),
        VerbSpec(
            pattern="verify merkle proof for item {leaf:expr} with root {root:expr} and proof {proof:expr} into {target:ident}",
            description="Cryptographically verifies a Merkle inclusion proof",
        ),
        VerbSpec(
            pattern="mine block with data {data:expr} and difficulty {diff:expr} into {target:ident}",
            description="Mines a Proof-of-Work block searching for target difficulty nonce",
        ),
        VerbSpec(
            pattern="create utxo ledger into {target:ident}",
            description="Initializes a UTXO balance state machine",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("create merkle tree from ")
            or s.startswith("get merkle root of ")
            or s.startswith("verify merkle proof for ")
            or s.startswith("mine block with data ")
            or s.startswith("verify block hash ")
            or s.startswith("create utxo ledger into ")
            or s.startswith("process transaction ")
            or s.startswith("get balance for address ")
            or s.startswith("generate checksum address from ")
            or s.startswith("prove knowledge of secret ")
            or s.startswith("prove schnorr secret ")
            or s.startswith("verify proof ")
            or s.startswith("verify schnorr proof ")
            or s.startswith("execute evm bytecode ")
            or s.startswith("split secret ")
            or s.startswith("reconstruct secret from shares ")
            or s.startswith("threshold sign message ")
            or super().can_handle_line(line)
        )

    def can_handle_block(self, header: str) -> bool:
        return False


CHAIN_DOMAIN = ChainDomain()
get_domain_registry().register(CHAIN_DOMAIN)

__all__ = [
    "ChainDomain",
    "CHAIN_DOMAIN",
    "ChainRuntime",
    "MerkleTree",
    "UtxoLedger",
    "ChainDomainParser",
    "ChainASTExporter",
    "chain_merkle_tree_create",
    "chain_merkle_root",
    "chain_merkle_proof_verify",
    "chain_mine_block",
    "chain_verify_block",
    "chain_utxo_ledger_create",
    "chain_process_tx",
    "chain_get_balance",
    "chain_checksum_address",
    "PatriciaMerkleTrie",
    "SchnorrZKProtocol",
    "RaftConsensusEngine",
    "MerklePatriciaTrie",
    "ProofOfStakeValidator",
    "chain_mpt_create",
    "chain_mpt_root",
    "chain_pos_create",
    "chain_pos_proposer",
    "chain_pos_vote",
    "EVMBytecodeInterpreterStackMachine",
    "ThresholdSignatureSchemeShamir",
    "chain_evm_execute",
    "chain_threshold_split",
    "chain_threshold_reconstruct",
    "chain_threshold_aggregate_sign",
]
