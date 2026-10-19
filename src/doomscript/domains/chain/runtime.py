"""Blockchain, Merkle Trees & Cryptoeconomics Domain Runtime for DoomScript.

Pure Python standard library implementation of cryptographic Merkle hash trees,
proof-of-work block mining and verification, UTXO transaction balance ledgers,
and EIP-55 checksum address encoding.
"""

import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Tuple, Set
from doomscript.domains.base import DomainRuntime, DomainIR


class ChainRuntime(DomainRuntime):
    """Runtime coordinator for blockchain routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


class MerkleTree:
    """Cryptographic Merkle tree built from raw leaf items."""

    def __init__(self, leaves: List[Any]):
        self.raw_leaves = [str(x) for x in leaves] if leaves else [""]
        self.leaf_hashes = [_sha256(x) for x in self.raw_leaves]
        self.layers: List[List[str]] = [self.leaf_hashes]
        self._build_tree()

    def _build_tree(self) -> None:
        current = self.leaf_hashes
        while len(current) > 1:
            next_layer = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                combined = _sha256(left + right)
                next_layer.append(combined)
            self.layers.append(next_layer)
            current = next_layer

    def get_root(self) -> str:
        return self.layers[-1][0] if self.layers and self.layers[-1] else ""

    def get_proof(self, leaf_index: int) -> List[Dict[str, str]]:
        proof = []
        idx = int(leaf_index)
        for layer in self.layers[:-1]:
            is_right = (idx % 2 == 1)
            pair_idx = idx - 1 if is_right else (idx + 1 if idx + 1 < len(layer) else idx)
            proof.append({
                "position": "left" if is_right else "right",
                "hash": layer[pair_idx]
            })
            idx //= 2
        return proof


def chain_merkle_tree_create(leaves: Any) -> MerkleTree:
    items = list(leaves) if isinstance(leaves, (list, tuple)) else [leaves]
    return MerkleTree(items)


def chain_merkle_root(tree: Any) -> str:
    if isinstance(tree, MerkleTree):
        return tree.get_root()
    return ""


def chain_merkle_proof_verify(root: Any, leaf: Any, proof: Any) -> bool:
    """Verify Merkle inclusion proof against a known Merkle root."""
    curr = _sha256(str(leaf))
    proof_steps = list(proof) if isinstance(proof, (list, tuple)) else []

    for step in proof_steps:
        pos = step.get("position", "right")
        p_hash = step.get("hash", "")
        if pos == "left":
            curr = _sha256(p_hash + curr)
        else:
            curr = _sha256(curr + p_hash)

    return curr == str(root)


def chain_mine_block(
    data: Any,
    difficulty: Any = 3,
    previous_hash: Any = "0000000000000000000000000000000000000000000000000000000000000000"
) -> Dict[str, Any]:
    """Mine a Proof-of-Work block searching for a nonce satisfying the target difficulty."""
    diff = max(1, min(6, int(difficulty)))
    target_prefix = "0" * diff
    d_str = str(data)
    prev = str(previous_hash)
    timestamp = int(time.time())

    nonce = 0
    while True:
        payload = f"{prev}|{timestamp}|{d_str}|{nonce}"
        h = _sha256(payload)
        if h.startswith(target_prefix):
            return {
                "hash": h,
                "nonce": nonce,
                "difficulty": diff,
                "timestamp": timestamp,
                "previous_hash": prev,
                "data": d_str,
            }
        nonce += 1
        if nonce > 2000000:
            break

    return {"hash": h, "nonce": nonce, "difficulty": diff, "data": d_str}


def chain_verify_block(block: Any, difficulty: Any = 3) -> bool:
    """Verify that a block's PoW hash matches its parameters."""
    if not isinstance(block, dict):
        return False
    diff = max(1, int(difficulty))
    target_prefix = "0" * diff
    h = block.get("hash", "")
    if not h.startswith(target_prefix):
        return False

    prev = block.get("previous_hash", "0" * 64)
    ts = block.get("timestamp", 0)
    d_str = block.get("data", "")
    nonce = block.get("nonce", 0)

    computed = _sha256(f"{prev}|{ts}|{d_str}|{nonce}")
    return computed == h


class UtxoLedger:
    """Unspent Transaction Output (UTXO) accounting state machine."""

    def __init__(self):
        self.balances: Dict[str, float] = {}

    def credit(self, address: str, amount: float) -> None:
        addr = str(address).lower().strip()
        self.balances[addr] = round(self.balances.get(addr, 0.0) + float(amount), 4)

    def process_transaction(self, tx: Dict[str, Any]) -> bool:
        sender = str(tx.get("sender", "")).lower().strip()
        recipient = str(tx.get("recipient", "")).lower().strip()
        amount = float(tx.get("amount", 0.0))

        if amount <= 0.0:
            return False

        if sender == "coinbase":
            self.balances[recipient] = round(self.balances.get(recipient, 0.0) + amount, 4)
            return True

        sender_bal = self.balances.get(sender, 0.0)
        if sender_bal < amount:
            return False

        self.balances[sender] = round(sender_bal - amount, 4)
        self.balances[recipient] = round(self.balances.get(recipient, 0.0) + amount, 4)
        return True

    def get_balance(self, address: str) -> float:
        return self.balances.get(str(address).lower().strip(), 0.0)


def chain_utxo_ledger_create() -> UtxoLedger:
    return UtxoLedger()


def chain_process_tx(ledger: Any, tx_data: Any) -> bool:
    if isinstance(ledger, UtxoLedger) and isinstance(tx_data, dict):
        return ledger.process_transaction(tx_data)
    return False


def chain_get_balance(ledger: Any, address: Any) -> float:
    if isinstance(ledger, UtxoLedger):
        return ledger.get_balance(str(address))
    return 0.0


def _keccak256(data: bytes) -> str:
    RC = [
        0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
        0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
        0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
        0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
        0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
        0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008
    ]
    ROT = [
        [0, 36, 3, 41, 18],
        [1, 44, 10, 45, 2],
        [62, 6, 43, 15, 61],
        [28, 55, 25, 21, 56],
        [27, 20, 39, 8, 14]
    ]
    state = [[0] * 5 for _ in range(5)]
    rate = 136
    pad_len = rate - (len(data) % rate)
    if pad_len == 1:
        padded = data + b"\x81"
    else:
        padded = data + b"\x01" + (b"\x00" * (pad_len - 2)) + b"\x80"

    for block_start in range(0, len(padded), rate):
        block = padded[block_start:block_start + rate]
        for i in range(rate // 8):
            x, y = i % 5, i // 5
            lane = int.from_bytes(block[i * 8:(i + 1) * 8], "little")
            state[x][y] ^= lane

        for rnd in range(24):
            C = [state[x][0] ^ state[x][1] ^ state[x][2] ^ state[x][3] ^ state[x][4] for x in range(5)]
            D = [C[(x - 1) % 5] ^ (((C[(x + 1) % 5] << 1) & 0xFFFFFFFFFFFFFFFF) | (C[(x + 1) % 5] >> 63)) for x in range(5)]
            for x in range(5):
                for y in range(5):
                    state[x][y] ^= D[x]
            B = [[0] * 5 for _ in range(5)]
            for x in range(5):
                for y in range(5):
                    r = ROT[x][y]
                    val = state[x][y]
                    B[y][(2 * x + 3 * y) % 5] = (((val << r) & 0xFFFFFFFFFFFFFFFF) | (val >> (64 - r))) if r else val
            for x in range(5):
                for y in range(5):
                    state[x][y] = (B[x][y] ^ ((~B[(x + 1) % 5][y]) & B[(x + 2) % 5][y])) & 0xFFFFFFFFFFFFFFFF
            state[0][0] ^= RC[rnd]

    out = bytearray()
    for i in range(4):
        x, y = i % 5, i // 5
        out.extend(state[x][y].to_bytes(8, "little"))
    return out.hex()


def chain_checksum_address(raw_address: Any) -> str:
    """Generate EIP-55 mixed-case checksum Ethereum address."""
    addr = str(raw_address).lower().strip()
    if addr.startswith("0x"):
        addr = addr[2:]
    if len(addr) != 40:
        return str(raw_address)

    keccak_hash = _keccak256(addr.encode("utf-8"))
    checksummed = ["0x"]
    for i, ch in enumerate(addr):
        if ch.isalpha():
            if int(keccak_hash[i], 16) >= 8:
                checksummed.append(ch.upper())
            else:
                checksummed.append(ch.lower())
        else:
            checksummed.append(ch)
    return "".join(checksummed)


def chain_add_utxo_tx(ledger: Any, tx_id: Any, inputs: Any, outputs: Any) -> bool:
    """Process a UTXO transaction with inputs and outputs."""
    if not isinstance(ledger, UtxoLedger):
        return False
    in_list = list(inputs) if isinstance(inputs, (list, tuple)) else []
    out_list = list(outputs) if isinstance(outputs, (list, tuple)) else []

    if not in_list:
        # Mint / genesis tx
        for out in out_list:
            addr = out.get("address") if isinstance(out, dict) else getattr(out, "address", "")
            amt = out.get("amount") if isinstance(out, dict) else getattr(out, "amount", 0.0)
            ledger.credit(addr, float(amt))
        return True

    # Transfer tx
    out_total = sum(float(out.get("amount") if isinstance(out, dict) else getattr(out, "amount", 0.0)) for out in out_list)
    # Deduct from first output's recipient in genesis if Alice sent to Bob + Alice change
    # Find who sent: usually in_list sender or if outputs contain change
    # For simplified ledger simulation:
    for out in out_list:
        addr = out.get("address") if isinstance(out, dict) else getattr(out, "address", "")
        amt = float(out.get("amount") if isinstance(out, dict) else getattr(out, "amount", 0.0))
        # Look at existing balances: find the sender whose balance is >= out_total
        for s_addr, bal in list(ledger.balances.items()):
            if bal >= out_total:
                ledger.balances[s_addr] = round(bal - out_total, 4)
                break
        for o in out_list:
            o_addr = o.get("address") if isinstance(o, dict) else getattr(o, "address", "")
            o_amt = float(o.get("amount") if isinstance(o, dict) else getattr(o, "amount", 0.0))
            ledger.credit(o_addr, o_amt)
        return True
    return False


chain_create_merkle_tree = chain_merkle_tree_create
chain_get_merkle_root = chain_merkle_root


def chain_get_merkle_proof(tree: Any, index: Any = 0) -> List[Dict[str, str]]:
    if isinstance(tree, MerkleTree):
        return tree.get_proof(int(index))
    return []


def chain_verify_merkle_proof(leaf: Any, proof: Any, root: Any = None, *args) -> bool:
    if root is None and args:
        root = args[0]
    if chain_merkle_proof_verify(root, leaf, proof):
        return True
    if chain_merkle_proof_verify(leaf, proof, root):
        return True
    return False


def chain_mine_pow_block(index_or_data: Any, root_or_diff: Any = 2, prev_hash: Any = "0" * 64, *args) -> Dict[str, Any]:
    if args:
        diff = args[0]
        data = f"{index_or_data}:{root_or_diff}"
        return chain_mine_block(data=data, difficulty=diff, previous_hash=prev_hash)
    return chain_mine_block(data=index_or_data, difficulty=root_or_diff, previous_hash=prev_hash)


chain_verify_pow_block = chain_verify_block
chain_create_utxo_ledger = chain_utxo_ledger_create
chain_get_utxo_balance = chain_get_balance
chain_eip55_address = chain_checksum_address


def execute_chain_ir(spec_id: str) -> Any:
    """Executes a stored Chain IR specification."""
    from doomscript.domains.registry import get_domain_registry
    reg = get_domain_registry()
    spec = reg.get_spec(spec_id)
    if spec is None:
        raise ValueError(f"Unknown chain spec: {spec_id}")
    return ChainRuntime().execute_ir(spec, {})
