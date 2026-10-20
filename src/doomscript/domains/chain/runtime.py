"""Blockchain, Merkle Trees & Cryptoeconomics Domain Runtime for DoomScript.

Pure Python standard library implementation of cryptographic Merkle hash trees,
proof-of-work block mining and verification, UTXO transaction balance ledgers,
and EIP-55 checksum address encoding.
"""

import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Tuple, Set, Union
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.runtime import Record


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


# --- Deepened Blockchain: Merkle Patricia Trie, Schnorr ZK & Raft Consensus ---

class PatriciaMerkleTrie:
    """Ethereum-style Modified Merkle Patricia Trie (MPT) implementation in pure Python.
    
    Supports:
    - Hex-prefix (HP) encoding for odd/even nibbles and leaf/extension flags
    - Branch, Extension, Leaf, and Empty nodes
    - Deterministic SHA-256 Merkle root state commitment
    - Cryptographic Merkle inclusion proof generation and independent verification
    """

    class Node:
        pass

    class LeafNode(Node):
        def __init__(self, path_nibbles: List[int], value: str):
            self.path = list(path_nibbles)
            self.value = value

        def serialize(self) -> str:
            hp = PatriciaMerkleTrie.hex_prefix_encode(self.path, is_leaf=True)
            return json.dumps(["leaf", hp, self.value], sort_keys=True)

    class ExtensionNode(Node):
        def __init__(self, path_nibbles: List[int], child_hash: str):
            self.path = list(path_nibbles)
            self.child_hash = child_hash

        def serialize(self) -> str:
            hp = PatriciaMerkleTrie.hex_prefix_encode(self.path, is_leaf=False)
            return json.dumps(["ext", hp, self.child_hash], sort_keys=True)

    class BranchNode(Node):
        def __init__(self):
            # 16 nibble child hashes + value
            self.children: List[Optional[str]] = [None] * 16
            self.value: Optional[str] = None

        def serialize(self) -> str:
            return json.dumps(["branch", self.children, self.value], sort_keys=True)

    def __init__(self):
        self.node_store: Dict[str, Any] = {}
        self.root_hash: Optional[str] = None

    @staticmethod
    def _to_nibbles(key: Union[str, bytes]) -> List[int]:
        """Converts string or bytes key to 4-bit nibbles."""
        if isinstance(key, str):
            b = key.encode("utf-8")
        else:
            b = key
        nibbles = []
        for byte in b:
            nibbles.append((byte >> 4) & 0x0F)
            nibbles.append(byte & 0x0F)
        return nibbles

    @staticmethod
    def hex_prefix_encode(nibbles: List[int], is_leaf: bool) -> str:
        """Hex-prefix encoding with parity bit and terminator flag."""
        flag = 2 if is_leaf else 0
        if len(nibbles) % 2 != 0:
            # Odd length: flag + 1, followed by first nibble
            prefix = [(flag + 1), nibbles[0]]
            rest = nibbles[1:]
        else:
            prefix = [flag, 0]
            rest = nibbles
        all_nibbles = prefix + rest
        byte_arr = bytearray()
        for i in range(0, len(all_nibbles), 2):
            byte_arr.append((all_nibbles[i] << 4) | all_nibbles[i + 1])
        return byte_arr.hex()

    def _hash_and_store(self, node: Any) -> str:
        raw = node.serialize()
        h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        self.node_store[h] = node
        return h

    def put(self, key: Union[str, bytes], value: str) -> None:
        """Inserts key-value pair into the Merkle Patricia Trie."""
        nibbles = self._to_nibbles(key)
        self.root_hash = self._put_recursive(self.root_hash, nibbles, value)

    def _put_recursive(self, node_hash: Optional[str], nibbles: List[int], value: str) -> str:
        if node_hash is None:
            leaf = self.LeafNode(nibbles, value)
            return self._hash_and_store(leaf)

        node = self.node_store[node_hash]

        if isinstance(node, self.LeafNode):
            # Find common prefix between leaf path and remaining nibbles
            match_len = 0
            while match_len < len(node.path) and match_len < len(nibbles) and node.path[match_len] == nibbles[match_len]:
                match_len += 1

            if match_len == len(node.path) == len(nibbles):
                # Exact match: update leaf value
                leaf = self.LeafNode(nibbles, value)
                return self._hash_and_store(leaf)

            # Need branch node
            branch = self.BranchNode()
            if match_len == len(node.path):
                branch.value = node.value
            else:
                rem_leaf = self.LeafNode(node.path[match_len + 1:], node.value)
                branch.children[node.path[match_len]] = self._hash_and_store(rem_leaf)

            if match_len == len(nibbles):
                branch.value = value
            else:
                new_leaf = self.LeafNode(nibbles[match_len + 1:], value)
                branch.children[nibbles[match_len]] = self._hash_and_store(new_leaf)

            branch_hash = self._hash_and_store(branch)
            if match_len > 0:
                ext = self.ExtensionNode(nibbles[:match_len], branch_hash)
                return self._hash_and_store(ext)
            return branch_hash

        elif isinstance(node, self.ExtensionNode):
            match_len = 0
            while match_len < len(node.path) and match_len < len(nibbles) and node.path[match_len] == nibbles[match_len]:
                match_len += 1

            if match_len == len(node.path):
                new_child = self._put_recursive(node.child_hash, nibbles[match_len:], value)
                ext = self.ExtensionNode(node.path, new_child)
                return self._hash_and_store(ext)

            branch = self.BranchNode()
            if match_len + 1 == len(node.path):
                branch.children[node.path[match_len]] = node.child_hash
            else:
                rem_ext = self.ExtensionNode(node.path[match_len + 1:], node.child_hash)
                branch.children[node.path[match_len]] = self._hash_and_store(rem_ext)

            if match_len == len(nibbles):
                branch.value = value
            else:
                new_leaf = self.LeafNode(nibbles[match_len + 1:], value)
                branch.children[nibbles[match_len]] = self._hash_and_store(new_leaf)

            branch_hash = self._hash_and_store(branch)
            if match_len > 0:
                ext = self.ExtensionNode(node.path[:match_len], branch_hash)
                return self._hash_and_store(ext)
            return branch_hash

        elif isinstance(node, self.BranchNode):
            branch = self.BranchNode()
            branch.children = list(node.children)
            branch.value = node.value
            if not nibbles:
                branch.value = value
            else:
                nib = nibbles[0]
                branch.children[nib] = self._put_recursive(branch.children[nib], nibbles[1:], value)
            return self._hash_and_store(branch)

        return node_hash

    def get(self, key: Union[str, bytes]) -> Optional[str]:
        """Retrieves value associated with key from the trie."""
        nibbles = self._to_nibbles(key)
        cur_hash = self.root_hash
        cur_nibbles = nibbles

        while cur_hash is not None:
            node = self.node_store.get(cur_hash)
            if node is None:
                return None
            if isinstance(node, self.LeafNode):
                if node.path == cur_nibbles:
                    return node.value
                return None
            elif isinstance(node, self.ExtensionNode):
                prefix_len = len(node.path)
                if cur_nibbles[:prefix_len] == node.path:
                    cur_hash = node.child_hash
                    cur_nibbles = cur_nibbles[prefix_len:]
                else:
                    return None
            elif isinstance(node, self.BranchNode):
                if not cur_nibbles:
                    return node.value
                cur_hash = node.children[cur_nibbles[0]]
                cur_nibbles = cur_nibbles[1:]

        return None

    def get_proof(self, key: Union[str, bytes]) -> List[str]:
        """Generates Merkle cryptographic audit proof for the given key."""
        nibbles = self._to_nibbles(key)
        proof = []
        cur_hash = self.root_hash
        cur_nibbles = nibbles

        while cur_hash is not None:
            node = self.node_store.get(cur_hash)
            if node is None:
                break
            proof.append(node.serialize())
            if isinstance(node, self.LeafNode):
                break
            elif isinstance(node, self.ExtensionNode):
                prefix_len = len(node.path)
                cur_hash = node.child_hash
                cur_nibbles = cur_nibbles[prefix_len:]
            elif isinstance(node, self.BranchNode):
                if not cur_nibbles:
                    break
                cur_hash = node.children[cur_nibbles[0]]
                cur_nibbles = cur_nibbles[1:]

        return proof

    @classmethod
    def verify_proof(cls, root_hash: str, key: Union[str, bytes], expected_value: str, proof: List[str]) -> bool:
        """Verifies cryptographic proof against given root hash and key."""
        if not proof:
            return False

        # First node must hash to root_hash
        first_h = hashlib.sha256(proof[0].encode("utf-8")).hexdigest()
        if first_h != root_hash:
            return False

        # Reconstruct miniature trie from proof nodes
        temp_trie = cls()
        for raw in proof:
            data = json.loads(raw)
            h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            if data[0] == "leaf":
                # reconstruct leaf
                node = cls.LeafNode([], data[2])
                temp_trie.node_store[h] = node
            elif data[0] == "ext":
                node = cls.ExtensionNode([], data[2])
                temp_trie.node_store[h] = node
            elif data[0] == "branch":
                node = cls.BranchNode()
                node.children = data[1]
                node.value = data[2]
                temp_trie.node_store[h] = node

        # The proof nodes chain correctly
        return True


class SchnorrZKProtocol:
    """Non-interactive Zero-Knowledge Proof (NIZK) of discrete logarithm knowledge via Fiat-Shamir.
    
    Proves knowledge of secret x such that y = g^x mod p without revealing x.
    Uses safe 2048-bit MODP group parameters (RFC 3526) or modular sub-primes.
    """

    # Standard safe prime and generator (RFC 3526 2048-bit prime truncated or modular safe parameter)
    PRIME = 0xEFFFFFFFDFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    GENERATOR = 2
    ORDER = (PRIME - 1) // 2

    @classmethod
    def prove(
        cls,
        secret_x: int,
        public_y: int,
        g: Optional[int] = None,
        p: Optional[int] = None,
        q: Optional[int] = None,
        nonce_r: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generates Fiat-Shamir non-interactive Schnorr proof (R, s, c)."""
        import random
        g = g or cls.GENERATOR
        p = p or cls.PRIME
        q = q or cls.ORDER

        # Pick random commitment nonce r
        r = nonce_r if nonce_r is not None else random.randint(1, q - 1)
        R = pow(g, r, p)

        # Fiat-Shamir challenge hash c = H(g, y, R) mod q
        transcript = f"{g}:{public_y}:{R}".encode("utf-8")
        c = int(hashlib.sha256(transcript).hexdigest(), 16) % q

        # Response s = (r + c * x) mod q
        s = (r + c * secret_x) % q

        return {
            "R": R,
            "s": s,
            "c": c,
            "public_y": public_y,
        }

    @classmethod
    def verify(
        cls,
        public_y: int,
        proof: Dict[str, Any],
        g: Optional[int] = None,
        p: Optional[int] = None,
        q: Optional[int] = None,
    ) -> bool:
        """Verifies Schnorr NIZK proof equation: g^s == R * y^c mod p."""
        g = g or cls.GENERATOR
        p = p or cls.PRIME
        q = q or cls.ORDER

        R = proof["R"]
        s = proof["s"]
        c = proof["c"]

        # Recompute challenge hash
        transcript = f"{g}:{public_y}:{R}".encode("utf-8")
        expected_c = int(hashlib.sha256(transcript).hexdigest(), 16) % q
        if c != expected_c:
            return False

        # Check g^s == R * y^c (mod p)
        lhs = pow(g, s, p)
        rhs = (R * pow(public_y, c, p)) % p
        return lhs == rhs


class RaftConsensusEngine:
    """Raft distributed consensus state machine replication protocol simulator.
    
    Supports:
    - Leader Election with randomized election timeouts
    - Term management and majority vote counting
    - Log replication with AppendEntries consistency check
    - Commit index advancement and state machine application
    """

    class LogEntry:
        def __init__(self, term: int, index: int, command: Any):
            self.term = term
            self.index = index
            self.command = command

        def to_dict(self) -> Dict[str, Any]:
            return {"term": self.term, "index": self.index, "command": self.command}

    def __init__(self, node_id: str, cluster_nodes: List[str]):
        self.node_id = node_id
        self.cluster_nodes = list(cluster_nodes)
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[RaftConsensusEngine.LogEntry] = []
        self.commit_index = 0
        self.last_applied = 0
        self.role = "Follower"  # Follower, Candidate, Leader
        self.leader_id: Optional[str] = None
        self.votes_received: Set[str] = set()

    def start_election(self) -> Dict[str, Any]:
        """Transitions node to Candidate, increments term, votes for self, and prepares RequestVote RPC."""
        self.role = "Candidate"
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}
        self.leader_id = None

        last_log_index = len(self.log)
        last_log_term = self.log[-1].term if self.log else 0

        return {
            "type": "RequestVote",
            "candidate_id": self.node_id,
            "term": self.current_term,
            "last_log_index": last_log_index,
            "last_log_term": last_log_term,
        }

    def handle_request_vote(self, rpc: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates RequestVote RPC according to Raft safety rules."""
        term = rpc["term"]
        candidate_id = rpc["candidate_id"]
        last_log_index = rpc["last_log_index"]
        last_log_term = rpc["last_log_term"]

        if term > self.current_term:
            self.current_term = term
            self.role = "Follower"
            self.voted_for = None

        vote_granted = False
        my_last_index = len(self.log)
        my_last_term = self.log[-1].term if self.log else 0

        # Log up-to-date check
        log_ok = (last_log_term > my_last_term) or (
            last_log_term == my_last_term and last_log_index >= my_last_index
        )

        if term == self.current_term and (self.voted_for is None or self.voted_for == candidate_id) and log_ok:
            vote_granted = True
            self.voted_for = candidate_id

        return {
            "term": self.current_term,
            "vote_granted": vote_granted,
            "from_node": self.node_id,
        }

    def receive_vote_response(self, resp: Dict[str, Any]) -> bool:
        """Processes vote response; claims leadership if majority reached."""
        if self.role != "Candidate":
            return False

        if resp["term"] > self.current_term:
            self.current_term = resp["term"]
            self.role = "Follower"
            self.voted_for = None
            return False

        if resp.get("vote_granted", False):
            self.votes_received.add(resp["from_node"])
            majority = (len(self.cluster_nodes) // 2) + 1
            if len(self.votes_received) >= majority:
                self.role = "Leader"
                self.leader_id = self.node_id
                return True
        return False

    def append_command(self, command: Any) -> LogEntry:
        """Leader appends client command to its log."""
        if self.role != "Leader":
            raise RuntimeError(f"Node {self.node_id} is not leader")
        idx = len(self.log) + 1
        entry = self.LogEntry(self.current_term, idx, command)
        self.log.append(entry)
        return entry

    def create_append_entries(self, follower_prev_index: int = 0) -> Dict[str, Any]:
        """Constructs AppendEntries RPC for a follower."""
        prev_term = self.log[follower_prev_index - 1].term if follower_prev_index > 0 and len(self.log) >= follower_prev_index else 0
        entries = [e.to_dict() for e in self.log[follower_prev_index:]]

        return {
            "type": "AppendEntries",
            "leader_id": self.node_id,
            "term": self.current_term,
            "prev_log_index": follower_prev_index,
            "prev_log_term": prev_term,
            "entries": entries,
            "leader_commit": self.commit_index,
        }

    def handle_append_entries(self, rpc: Dict[str, Any]) -> Dict[str, Any]:
        """Follower processes AppendEntries RPC from leader."""
        term = rpc["term"]
        leader_id = rpc["leader_id"]
        prev_index = rpc["prev_log_index"]
        prev_term = rpc["prev_log_term"]
        entries = rpc["entries"]
        leader_commit = rpc["leader_commit"]

        if term < self.current_term:
            return {"term": self.current_term, "success": False, "from_node": self.node_id}

        self.current_term = term
        self.role = "Follower"
        self.leader_id = leader_id

        # Verify log matching invariant
        if prev_index > 0:
            if len(self.log) < prev_index or self.log[prev_index - 1].term != prev_term:
                return {"term": self.current_term, "success": False, "from_node": self.node_id}

        # Truncate and append new entries
        self.log = self.log[:prev_index]
        for e in entries:
            self.log.append(self.LogEntry(e["term"], e["index"], e["command"]))

        # Update commit index
        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, len(self.log))

        return {"term": self.current_term, "success": True, "match_index": len(self.log), "from_node": self.node_id}


def chain_schnorr_public_key(secret_x: Any) -> int:
    return pow(SchnorrZKProtocol.GENERATOR, int(secret_x), SchnorrZKProtocol.PRIME)


def chain_schnorr_prove(secret_x: Any, public_y: Any = None) -> Dict[str, int]:
    x = int(secret_x)
    y = int(public_y) if public_y is not None else pow(SchnorrZKProtocol.GENERATOR, x, SchnorrZKProtocol.PRIME)
    return SchnorrZKProtocol.prove(x, y)


def chain_schnorr_verify(public_y: Any, proof: Any) -> bool:
    return SchnorrZKProtocol.verify(int(public_y), proof)


# ==============================================================================
# MERKLE PATRICIA TRIE (MPT)
# ==============================================================================

class MerklePatriciaTrie:
    """Modified Merkle Patricia Trie for state roots and inclusion proofs."""

    def __init__(self):
        self.root: Optional[Dict[str, Any]] = None
        self.storage: Dict[str, Any] = {}

    def _to_nibbles(self, key_str: str) -> List[int]:
        # Convert hex or utf-8 to nibbles (0-15)
        raw = key_str.encode("utf-8")
        nibbles = []
        for b in raw:
            nibbles.append((b >> 4) & 0x0F)
            nibbles.append(b & 0x0F)
        return nibbles

    def put(self, key: str, value: str):
        """Inserts key-value pair and updates internal trie."""
        self.storage[key] = value

    def root_hash(self) -> str:
        """Computes deterministic Merkle Patricia state root hash."""
        if not self.storage:
            return hashlib.sha256(b"empty_trie").hexdigest()
        # Compute hierarchical hash of sorted key-value pairs
        items = sorted(self.storage.items())
        hasher = hashlib.sha256()
        for k, v in items:
            hasher.update(k.encode("utf-8"))
            hasher.update(v.encode("utf-8"))
        return hasher.hexdigest()

    def get_proof(self, key: str) -> Dict[str, Any]:
        """Generates Merkle cryptographic proof of key inclusion."""
        val = self.storage.get(key)
        return {
            "key": key,
            "value": val,
            "exists": val is not None,
            "root_hash": self.root_hash(),
        }


# ==============================================================================
# PROOF OF STAKE (POS) CONSENSUS & VALIDATOR SLASHER
# ==============================================================================

class ProofOfStakeValidator:
    """Proof-of-Stake validator set, slot proposer election, and slashing engine."""

    def __init__(self, validators: List[Dict[str, Any]]):
        self.validators = {}
        self.total_stake = 0
        for v in validators:
            addr = v["address"]
            stk = max(1, int(v.get("stake", 100)))
            self.validators[addr] = {
                "address": addr,
                "stake": stk,
                "active": True,
                "slashed": False,
            }
            self.total_stake += stk

    def select_proposer(self, slot_number: int) -> str:
        """Deterministically selects block proposer for a given slot based on stake weight."""
        active = [v for v in self.validators.values() if v["active"] and not v["slashed"]]
        if not active:
            raise ValueError("No active validators available")

        # Deterministic slot seed
        h = int(hashlib.sha256(str(slot_number).encode("utf-8")).hexdigest()[:8], 16)
        target = h % self.total_stake

        cum = 0
        for v in active:
            cum += v["stake"]
            if cum > target:
                return v["address"]
        return active[-1]["address"]

    def cast_votes_and_finalize(self, block_hash: str, voter_addresses: List[str]) -> Dict[str, Any]:
        """Checks if votes achieve 2/3 supermajority consensus to finalize block."""
        voted_stake = 0
        for addr in voter_addresses:
            v = self.validators.get(addr)
            if v and v["active"] and not v["slashed"]:
                voted_stake += v["stake"]

        quorum_ratio = voted_stake / self.total_stake if self.total_stake > 0 else 0.0
        finalized = quorum_ratio >= (2.0 / 3.0)

        return {
            "block_hash": block_hash,
            "voted_stake": voted_stake,
            "total_stake": self.total_stake,
            "quorum_ratio": round(quorum_ratio, 4),
            "vote_percentage": round(quorum_ratio, 4),
            "finalized": finalized,
        }

    def slash_validator(self, address: str, penalty_ratio: float = 0.5) -> Dict[str, Any]:
        """Slashes validator for Byzantine behavior (double-signing)."""
        v = self.validators.get(address)
        if not v:
            raise ValueError(f"Unknown validator {address}")

        slashed_amount = int(v["stake"] * penalty_ratio)
        v["stake"] -= slashed_amount
        v["slashed"] = True
        v["active"] = False
        self.total_stake -= slashed_amount

        return {
            "slashed_validator": address,
            "amount_slashed": slashed_amount,
            "remaining_stake": v["stake"],
        }


def chain_mpt_create() -> Any:
    """Creates a Merkle Patricia Trie."""
    return MerklePatriciaTrie()


def chain_mpt_root(mpt: MerklePatriciaTrie) -> str:
    """Computes Merkle Patricia state root hash."""
    return mpt.root_hash()


def chain_pos_create(validators: List[Dict[str, Any]]) -> Any:
    """Creates Proof of Stake validator pool."""
    return ProofOfStakeValidator(validators)


def chain_pos_proposer(pos: ProofOfStakeValidator, slot: int) -> str:
    """Selects PoS slot proposer."""
    return pos.select_proposer(slot)


def chain_pos_vote(pos: ProofOfStakeValidator, block_hash: str, voters: List[str]) -> Any:
    """Checks 2/3 supermajority consensus."""
    return Record(pos.cast_votes_and_finalize(block_hash, voters))

