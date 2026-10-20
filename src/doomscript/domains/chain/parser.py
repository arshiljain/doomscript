"""Blockchain Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class ChainDomainParser(DomainParser):
    """Parses spoken-English blockchain, Merkle tree, and cryptoeconomic statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # create merkle tree from <leaves> into <target>
        m_mt = re.match(
            r"^create\s+merkle\s+tree\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mt:
            leaves = m_mt.group(1).strip()
            target = m_mt.group(2).strip()
            return f"set {target} to chain_merkle_tree_create({leaves})"

        # get merkle root of <tree> into <target>
        m_root = re.match(
            r"^get\s+merkle\s+root\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_root:
            tree = m_root.group(1).strip()
            target = m_root.group(2).strip()
            return f"set {target} to chain_merkle_root({tree})"

        # verify merkle proof for item <leaf> with root <root> and proof <proof> into <target>
        m_pf = re.match(
            r"^verify\s+merkle\s+proof\s+for\s+(?:item\s+)?(.+?)\s+with\s+root\s+(.+?)\s+and\s+proof\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pf:
            leaf = m_pf.group(1).strip()
            root = m_pf.group(2).strip()
            proof = m_pf.group(3).strip()
            target = m_pf.group(4).strip()
            return f"set {target} to chain_merkle_proof_verify({root}, {leaf}, {proof})"

        # mine block with data <data> and difficulty <diff> into <target>
        m_mine = re.match(
            r"^mine\s+block\s+with\s+data\s+(.+?)\s+and\s+difficulty\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mine:
            data = m_mine.group(1).strip()
            diff = m_mine.group(2).strip()
            target = m_mine.group(3).strip()
            return f"set {target} to chain_mine_block({data}, {diff})"

        # verify block hash <block> with difficulty <diff> into <target>
        m_vblk = re.match(
            r"^verify\s+block\s+hash\s+(.+?)\s+with\s+difficulty\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vblk:
            blk = m_vblk.group(1).strip()
            diff = m_vblk.group(2).strip()
            target = m_vblk.group(3).strip()
            return f"set {target} to chain_verify_block({blk}, {diff})"

        # create utxo ledger into <target>
        m_utxo = re.match(
            r"^create\s+utxo\s+ledger\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_utxo:
            target = m_utxo.group(1).strip()
            return f"set {target} to chain_utxo_ledger_create()"

        # process transaction <tx> in <ledger> into <target>
        m_tx = re.match(
            r"^process\s+transaction\s+(.+?)\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tx:
            tx = m_tx.group(1).strip()
            led = m_tx.group(2).strip()
            target = m_tx.group(3).strip()
            return f"set {target} to chain_process_tx({led}, {tx})"

        # get balance for address <addr> in <ledger> into <target>
        m_bal = re.match(
            r"^get\s+balance\s+for\s+address\s+(.+?)\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bal:
            addr = m_bal.group(1).strip()
            led = m_bal.group(2).strip()
            target = m_bal.group(3).strip()
            return f"set {target} to chain_get_balance({led}, {addr})"

        # generate checksum address from <addr> into <target>
        m_chk = re.match(
            r"^generate\s+checksum\s+address\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_chk:
            addr = m_chk.group(1).strip()
            target = m_chk.group(2).strip()
            return f"set {target} to chain_checksum_address({addr})"

        # prove knowledge of secret <secret> for public <public> into <target>
        m_schnorr_prove = re.match(
            r"^prove\s+(?:knowledge\s+of\s+secret|schnorr\s+secret)\s+(.+?)\s+for\s+public\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_schnorr_prove:
            sec_x, pub_y, target = m_schnorr_prove.group(1).strip(), m_schnorr_prove.group(2).strip(), m_schnorr_prove.group(3).strip()
            return f"set {target} to chain_schnorr_prove({sec_x}, {pub_y})"

        # verify schnorr proof <proof> for public <public> into <target>
        m_schnorr_ver = re.match(
            r"^verify\s+(?:schnorr\s+)?proof\s+(.+?)\s+for\s+public\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_schnorr_ver:
            proof, pub_y, target = m_schnorr_ver.group(1).strip(), m_schnorr_ver.group(2).strip(), m_schnorr_ver.group(3).strip()
            return f"set {target} to chain_schnorr_verify({pub_y}, {proof})"

        # create merkle patricia trie into <target>
        m_mpt = re.match(
            r"^create\s+merkle\s+patricia\s+trie\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mpt:
            target = m_mpt.group(1).strip()
            return f"set {target} to chain_mpt_create()"

        # get mpt root of <mpt> into <target>
        m_mpt_root = re.match(
            r"^get\s+mpt\s+root\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mpt_root:
            mpt, target = m_mpt_root.group(1).strip(), m_mpt_root.group(2).strip()
            return f"set {target} to chain_mpt_root({mpt})"

        # create pos validator pool with validators <vals> into <target>
        m_pos = re.match(
            r"^create\s+pos\s+validator\s+pool\s+with\s+validators\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pos:
            vals, target = m_pos.group(1).strip(), m_pos.group(2).strip()
            return f"set {target} to chain_pos_create({vals})"

        # select pos proposer for slot <slot> in <pos> into <target>
        m_pos_prop = re.match(
            r"^select\s+pos\s+proposer\s+for\s+slot\s+(\d+)\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pos_prop:
            slot, pos, target = m_pos_prop.group(1).strip(), m_pos_prop.group(2).strip(), m_pos_prop.group(3).strip()
            return f"set {target} to chain_pos_proposer({pos}, {slot})"

        # finalize pos block <hash> with voters <voters> in <pos> into <target>
        m_pos_vote = re.match(
            r"^finalize\s+pos\s+block\s+(.+?)\s+with\s+voters\s+(.+?)\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pos_vote:
            b_hash, voters, pos, target = m_pos_vote.group(1).strip(), m_pos_vote.group(2).strip(), m_pos_vote.group(3).strip(), m_pos_vote.group(4).strip()
            return f"set {target} to chain_pos_vote({pos}, {b_hash}, {voters})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Chain domain does not define declarative blocks")
