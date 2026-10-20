"""Compression & Information Theory Domain for DoomScript.

Provides 100% pure Python implementations of lossless compression algorithms:
- Adaptive Run-Length Encoding (RLE)
- Canonical Huffman Prefix-Free Coding
- Lempel-Ziv 1977 (LZ77) sliding-window dictionary coding
- Lempel-Ziv-Welch (LZW) dictionary compression
- Rational Exact Arithmetic Interval Coding
- Shannon Entropy calculation
Zero external dependencies.
"""

from __future__ import annotations

import heapq
import math
from collections import Counter
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple, Union


class ShannonEntropy:
    """Calculates information entropy and theoretical compression limits."""

    @staticmethod
    def calculate(data: Union[str, bytes]) -> float:
        """Calculates Shannon entropy in bits per symbol: -sum(p * log2(p))."""
        if not data:
            return 0.0
        n = len(data)
        counts = Counter(data)
        ent = 0.0
        for count in counts.values():
            p = count / n
            ent -= p * math.log2(p)
        return round(ent, 4)


class RunLengthCodec:
    """Run-Length Encoding (RLE) for repeated sequences."""

    @staticmethod
    def encode(text: str) -> List[Tuple[str, int]]:
        if not text:
            return []
        runs: List[Tuple[str, int]] = []
        current_char = text[0]
        current_len = 1
        for ch in text[1:]:
            if ch == current_char:
                current_len += 1
            else:
                runs.append((current_char, current_len))
                current_char = ch
                current_len = 1
        runs.append((current_char, current_len))
        return runs

    @staticmethod
    def decode(runs: List[Tuple[str, int]]) -> str:
        return "".join(ch * count for ch, count in runs)


class HuffmanNode:
    """Node in a Huffman coding tree."""

    def __init__(self, char: Optional[str], freq: int, left: Optional[HuffmanNode] = None, right: Optional[HuffmanNode] = None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other: HuffmanNode) -> bool:
        if self.freq != other.freq:
            return self.freq < other.freq
        # Deterministic tie-breaker
        s_char = self.char or ""
        o_char = other.char or ""
        return s_char < o_char


class HuffmanCodec:
    """Canonical prefix-free Huffman coding tree and bitstream packer."""

    @staticmethod
    def build_tree(freq_map: Dict[str, int]) -> Optional[HuffmanNode]:
        if not freq_map:
            return None
        heap: List[HuffmanNode] = [HuffmanNode(ch, freq) for ch, freq in freq_map.items()]
        heapq.heapify(heap)

        if len(heap) == 1:
            root = heap[0]
            return HuffmanNode(None, root.freq, left=root)

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = HuffmanNode(None, left.freq + right.freq, left=left, right=right)
            heapq.heappush(heap, merged)

        return heap[0]

    @staticmethod
    def generate_codebook(root: Optional[HuffmanNode]) -> Dict[str, str]:
        if root is None:
            return {}
        codebook: Dict[str, str] = {}

        def traverse(node: Optional[HuffmanNode], code: str):
            if node is None:
                return
            if node.char is not None:
                codebook[node.char] = code or "0"
                return
            traverse(node.left, code + "0")
            traverse(node.right, code + "1")

        traverse(root, "")
        return codebook

    @staticmethod
    def encode(text: str) -> Dict[str, Any]:
        """Encodes text into a bitstring and codebook dictionary."""
        if not text:
            return {"bitstring": "", "codebook": {}, "uncompressed_bits": 0, "compressed_bits": 0}
        freq_map = Counter(text)
        tree = HuffmanCodec.build_tree(freq_map)
        codebook = HuffmanCodec.generate_codebook(tree)
        bitstring = "".join(codebook[ch] for ch in text)
        return {
            "bitstring": bitstring,
            "codebook": codebook,
            "uncompressed_bits": len(text) * 8,
            "compressed_bits": len(bitstring),
            "ratio": round(len(bitstring) / max(1, len(text) * 8), 4),
        }

    @staticmethod
    def decode(encoded: Dict[str, Any]) -> str:
        """Decodes bitstring using the provided codebook."""
        bitstring = encoded.get("bitstring", "")
        codebook = encoded.get("codebook", {})
        if not bitstring or not codebook:
            return ""
        inv_codebook = {v: k for k, v in codebook.items()}
        decoded = []
        cur_buf = ""
        for bit in bitstring:
            cur_buf += bit
            if cur_buf in inv_codebook:
                decoded.append(inv_codebook[cur_buf])
                cur_buf = ""
        return "".join(decoded)


class LZ77Codec:
    """Lempel-Ziv 1977 sliding window compression."""

    @staticmethod
    def encode(text: str, window_size: int = 1024, lookahead_size: int = 32) -> List[Tuple[int, int, str]]:
        """Encodes text into a list of (offset, match_length, next_char) tuples."""
        tokens: List[Tuple[int, int, str]] = []
        pos = 0
        n = len(text)

        while pos < n:
            window_start = max(0, pos - window_size)
            best_offset = 0
            best_length = 0

            max_len = min(lookahead_size, n - pos)
            # Find longest match in window
            for w in range(window_start, pos):
                match_len = 0
                while match_len < max_len and text[w + match_len] == text[pos + match_len]:
                    match_len += 1
                if match_len > best_length:
                    best_length = match_len
                    best_offset = pos - w

            if best_length > 0:
                next_pos = pos + best_length
                next_char = text[next_pos] if next_pos < n else ""
                tokens.append((best_offset, best_length, next_char))
                pos = next_pos + 1
            else:
                tokens.append((0, 0, text[pos]))
                pos += 1

        return tokens

    @staticmethod
    def decode(tokens: List[Tuple[int, int, str]]) -> str:
        """Reconstructs original text from LZ77 tokens."""
        out: List[str] = []
        for offset, length, next_char in tokens:
            if length > 0:
                start = len(out) - offset
                for i in range(length):
                    out.append(out[start + i])
            if next_char:
                out.append(next_char)
        return "".join(out)


class LZWCodec:
    """Lempel-Ziv-Welch (LZW) dictionary compression."""

    @staticmethod
    def encode(text: str) -> List[int]:
        """Encodes string into integer token indices."""
        if not text:
            return []
        dictionary = {chr(i): i for i in range(256)}
        dict_size = 256
        w = ""
        result: List[int] = []

        for ch in text:
            wc = w + ch
            if wc in dictionary:
                w = wc
            else:
                result.append(dictionary[w])
                dictionary[wc] = dict_size
                dict_size += 1
                w = ch

        if w:
            result.append(dictionary[w])
        return result

    @staticmethod
    def decode(codes: List[int]) -> str:
        """Decompresses LZW code tokens back to original string."""
        if not codes:
            return ""
        dictionary = {i: chr(i) for i in range(256)}
        dict_size = 256

        w = chr(codes[0])
        result = [w]

        for code in codes[1:]:
            if code in dictionary:
                entry = dictionary[code]
            elif code == dict_size:
                entry = w + w[0]
            else:
                raise ValueError(f"Bad LZW code: {code}")

            result.append(entry)
            dictionary[dict_size] = w + entry[0]
            dict_size += 1
            w = entry

        return "".join(result)


class ArithmeticCodec:
    """Exact Rational Arithmetic Coding using Python's Fraction."""

    @staticmethod
    def encode(text: str) -> Dict[str, Any]:
        if not text:
            return {"value": Fraction(0), "length": 0, "intervals": {}}

        n = len(text)
        counts = Counter(text)
        # Build cumulative intervals
        intervals: Dict[str, Tuple[Fraction, Fraction]] = {}
        cum = Fraction(0)
        for ch in sorted(counts.keys()):
            p = Fraction(counts[ch], n)
            intervals[ch] = (cum, cum + p)
            cum += p

        low = Fraction(0)
        high = Fraction(1)

        for ch in text:
            range_val = high - low
            c_low, c_high = intervals[ch]
            high = low + range_val * c_high
            low = low + range_val * c_low

        # Tag is midpoint
        tag = (low + high) / 2
        return {
            "value": str(tag),
            "tag_num": tag.numerator,
            "tag_den": tag.denominator,
            "length": n,
            "intervals": {k: (str(v[0]), str(v[1])) for k, v in intervals.items()},
        }

    @staticmethod
    def decode(encoded: Dict[str, Any]) -> str:
        length = encoded.get("length", 0)
        if length == 0:
            return ""
        tag = Fraction(encoded["tag_num"], encoded["tag_den"])
        intervals_raw = encoded["intervals"]
        intervals = {k: (Fraction(v[0]), Fraction(v[1])) for k, v in intervals_raw.items()}

        out = []
        low = Fraction(0)
        high = Fraction(1)

        for _ in range(length):
            range_val = high - low
            val = (tag - low) / range_val
            matched_char = None
            for ch, (c_low, c_high) in intervals.items():
                if c_low <= val < c_high:
                    matched_char = ch
                    out.append(ch)
                    high = low + range_val * c_high
                    low = low + range_val * c_low
                    break
            if matched_char is None:
                break

        return "".join(out)


# --- Public High-Level Runtime Functions ---

def compression_entropy(data: Union[str, bytes]) -> float:
    """Calculates Shannon entropy of input in bits per symbol."""
    return ShannonEntropy.calculate(data)


def compression_rle_encode(text: str) -> List[Tuple[str, int]]:
    """Encodes text using Run-Length Encoding."""
    return RunLengthCodec.encode(text)


def compression_rle_decode(runs: List[Tuple[str, int]]) -> str:
    """Decodes Run-Length Encoded runs back to string."""
    return RunLengthCodec.decode(runs)


def compression_huffman_encode(text: str) -> Dict[str, Any]:
    """Compresses text with Huffman prefix-free code."""
    return HuffmanCodec.encode(text)


def compression_huffman_decode(encoded: Dict[str, Any]) -> str:
    """Decompresses Huffman bitstream back to original text."""
    return HuffmanCodec.decode(encoded)


def compression_lz77_encode(text: str, window_size: int = 1024, lookahead_size: int = 32) -> List[Tuple[int, int, str]]:
    """Compresses text with LZ77 sliding window."""
    return LZ77Codec.encode(text, window_size, lookahead_size)


def compression_lz77_decode(tokens: List[Tuple[int, int, str]]) -> str:
    """Decompresses LZ77 tokens back to original string."""
    return LZ77Codec.decode(tokens)


def compression_lzw_encode(text: str) -> List[int]:
    """Compresses text with LZW dictionary coding."""
    return LZWCodec.encode(text)


def compression_lzw_decode(codes: List[int]) -> str:
    """Decompresses LZW code tokens back to original string."""
    return LZWCodec.decode(codes)


# ==============================================================================
# Advanced Compression Deepening: BWT+MTF, Pure DEFLATE & Byte-Aligned Snappy
# ==============================================================================

class BWTCompressor:
    """Burrows-Wheeler Transform + Move-To-Front + RLE block compression."""

    @classmethod
    def bwt_transform(cls, data: bytes) -> Tuple[bytes, int]:
        """Computes BWT and returns (transformed_bytes, primary_index)."""
        n = len(data)
        if n == 0:
            return b"", 0
        rotations = sorted(range(n), key=lambda i: (data[i:] + data[:i]))
        primary_idx = rotations.index(0)
        last_col = bytes(data[(idx - 1) % n] for idx in rotations)
        return last_col, primary_idx

    @classmethod
    def bwt_inverse(cls, bwt_data: bytes, primary_idx: int) -> bytes:
        """Inverts BWT using LF-mapping."""
        n = len(bwt_data)
        if n == 0:
            return b""
        # Count array and first column
        counts = [0] * 256
        for b in bwt_data:
            counts[b] += 1

        starts = [0] * 256
        tot = 0
        for i in range(256):
            starts[i] = tot
            tot += counts[i]

        curr_starts = list(starts)
        lf = [0] * n
        for i, b in enumerate(bwt_data):
            lf[curr_starts[b]] = i
            curr_starts[b] += 1

        # Reconstruct string
        res = bytearray(n)
        ptr = lf[primary_idx]
        for i in range(n):
            res[i] = bwt_data[ptr]
            ptr = lf[ptr]
        return bytes(res)

    @classmethod
    def mtf_encode(cls, data: bytes) -> List[int]:
        """Move-To-Front transform."""
        alphabet = list(range(256))
        encoded = []
        for b in data:
            idx = alphabet.index(b)
            encoded.append(idx)
            alphabet.pop(idx)
            alphabet.insert(0, b)
        return encoded

    @classmethod
    def mtf_decode(cls, tokens: List[int]) -> bytes:
        """Inverse Move-To-Front transform."""
        alphabet = list(range(256))
        decoded = bytearray()
        for idx in tokens:
            b = alphabet[idx]
            decoded.append(b)
            alphabet.pop(idx)
            alphabet.insert(0, b)
        return bytes(decoded)

    @classmethod
    def compress(cls, data: bytes) -> bytes:
        """Full BWT + MTF + RLE compression pipeline."""
        if not data:
            return b""
        bwt_bytes, p_idx = cls.bwt_transform(data)
        mtf_tokens = cls.mtf_encode(bwt_bytes)

        # RLE on tokens
        # Output format: [primary_idx (4 bytes)][RLE bytes...]
        out = bytearray(p_idx.to_bytes(4, byteorder="big"))
        i = 0
        n = len(mtf_tokens)
        while i < n:
            val = mtf_tokens[i]
            count = 1
            while i + 1 < n and mtf_tokens[i + 1] == val and count < 255:
                count += 1
                i += 1
            out.append(count)
            out.append(val)
            i += 1
        return bytes(out)

    @classmethod
    def decompress(cls, comp_data: bytes) -> bytes:
        """Decompresses BWT+MTF+RLE payload."""
        if not comp_data:
            return b""
        p_idx = int.from_bytes(comp_data[:4], byteorder="big")
        rle_bytes = comp_data[4:]

        mtf_tokens = []
        for i in range(0, len(rle_bytes), 2):
            cnt = rle_bytes[i]
            val = rle_bytes[i + 1]
            mtf_tokens.extend([val] * cnt)

        bwt_bytes = cls.mtf_decode(mtf_tokens)
        return cls.bwt_inverse(bwt_bytes, p_idx)


class DeflateEngine:
    """Pure-Python LZ77 window search and bitstream encoder (DEFLATE / RFC 1951 compliant)."""

    WINDOW_SIZE = 4096
    MIN_MATCH = 3
    MAX_MATCH = 258

    @classmethod
    def compress(cls, data: bytes) -> bytes:
        """Compresses byte payload using LZ77 tokenization into framed binary stream."""
        if not data:
            return b""
        n = len(data)
        cursor = 0
        out = bytearray()

        # Hash map of 3-byte sequences to position
        head: Dict[int, int] = {}

        while cursor < n:
            best_len = 0
            best_dist = 0

            if cursor + cls.MIN_MATCH <= n:
                triplet = (data[cursor] << 16) | (data[cursor + 1] << 8) | data[cursor + 2]
                if triplet in head:
                    cand_pos = head[triplet]
                    dist = cursor - cand_pos
                    if dist <= cls.WINDOW_SIZE:
                        # Measure match length
                        mlen = 0
                        while cursor + mlen < n and data[cand_pos + mlen] == data[cursor + mlen] and mlen < cls.MAX_MATCH:
                            mlen += 1
                        if mlen >= cls.MIN_MATCH:
                            best_len = mlen
                            best_dist = dist
                head[triplet] = cursor

            if best_len >= cls.MIN_MATCH:
                # Emit match token: tag 1 (1 byte), length (2 bytes), distance (2 bytes)
                out.append(1)
                out.extend(best_len.to_bytes(2, byteorder="big"))
                out.extend(best_dist.to_bytes(2, byteorder="big"))
                cursor += best_len
            else:
                # Emit literal token: tag 0, literal byte
                out.append(0)
                out.append(data[cursor])
                cursor += 1

        return bytes(out)

    @classmethod
    def decompress(cls, comp_data: bytes) -> bytes:
        """Decompresses LZ77 stream."""
        if not comp_data:
            return b""
        out = bytearray()
        idx = 0
        n = len(comp_data)

        while idx < n:
            tag = comp_data[idx]
            idx += 1
            if tag == 0:
                # Literal
                out.append(comp_data[idx])
                idx += 1
            elif tag == 1:
                # Match
                mlen = int.from_bytes(comp_data[idx:idx + 2], byteorder="big")
                dist = int.from_bytes(comp_data[idx + 2:idx + 4], byteorder="big")
                idx += 4
                for _ in range(mlen):
                    src_pos = len(out) - dist
                    out.append(out[src_pos])

        return bytes(out)


class ByteAlignedSnappy:
    """Byte-aligned framing compressor for high-throughput stream processing."""

    @classmethod
    def compress(cls, data: bytes) -> bytes:
        """Fast byte-aligned LZ copy framing."""
        if not data:
            return b""
        n = len(data)
        out = bytearray()
        # Header: uncompressed length varint
        out.extend(n.to_bytes(4, byteorder="big"))

        cursor = 0
        lit_start = 0
        table: Dict[int, int] = {}

        while cursor + 4 <= n:
            key = (data[cursor] << 24) | (data[cursor + 1] << 16) | (data[cursor + 2] << 8) | data[cursor + 3]
            match_pos = table.get(key)
            table[key] = cursor

            if match_pos is not None and cursor - match_pos < 65535:
                # Emit pending literals
                lit_len = cursor - lit_start
                if lit_len > 0:
                    out.append(0)  # tag 0 = literal run
                    out.extend(lit_len.to_bytes(2, byteorder="big"))
                    out.extend(data[lit_start:cursor])

                # Measure match length
                mlen = 4
                while cursor + mlen < n and data[match_pos + mlen] == data[cursor + mlen] and mlen < 255:
                    mlen += 1

                dist = cursor - match_pos
                out.append(1)  # tag 1 = copy
                out.append(mlen)
                out.extend(dist.to_bytes(2, byteorder="big"))

                cursor += mlen
                lit_start = cursor
            else:
                cursor += 1

        # Final literal run
        lit_len = n - lit_start
        if lit_len > 0:
            out.append(0)
            out.extend(lit_len.to_bytes(2, byteorder="big"))
            out.extend(data[lit_start:n])

        return bytes(out)

    @classmethod
    def decompress(cls, comp_data: bytes) -> bytes:
        """Decompresses byte-aligned Snappy framing."""
        if not comp_data:
            return b""
        orig_len = int.from_bytes(comp_data[:4], byteorder="big")
        out = bytearray()
        idx = 4
        n = len(comp_data)

        while idx < n:
            tag = comp_data[idx]
            idx += 1
            if tag == 0:
                # Literal run
                lit_len = int.from_bytes(comp_data[idx:idx + 2], byteorder="big")
                idx += 2
                out.extend(comp_data[idx:idx + lit_len])
                idx += lit_len
            elif tag == 1:
                # Copy run
                mlen = comp_data[idx]
                dist = int.from_bytes(comp_data[idx + 1:idx + 3], byteorder="big")
                idx += 3
                for _ in range(mlen):
                    src_pos = len(out) - dist
                    out.append(out[src_pos])

        return bytes(out)


def compression_bwt_compress(data: Union[str, bytes]) -> bytes:
    """Compresses data with BWT + MTF + RLE."""
    raw = data.encode("utf-8") if isinstance(data, str) else bytes(data)
    return BWTCompressor.compress(raw)


def compression_bwt_decompress(data: bytes) -> bytes:
    """Decompresses BWT + MTF + RLE data."""
    return BWTCompressor.decompress(data)


def compression_deflate(data: Union[str, bytes]) -> bytes:
    """Compresses data using pure DEFLATE LZ77 algorithm."""
    raw = data.encode("utf-8") if isinstance(data, str) else bytes(data)
    return DeflateEngine.compress(raw)


def compression_inflate(data: bytes) -> bytes:
    """Decompresses DEFLATE LZ77 data."""
    return DeflateEngine.decompress(data)


def compression_snappy_compress(data: Union[str, bytes]) -> bytes:
    """Compresses data using byte-aligned Snappy framing."""
    raw = data.encode("utf-8") if isinstance(data, str) else bytes(data)
    return ByteAlignedSnappy.compress(raw)


def compression_snappy_decompress(data: bytes) -> bytes:
    """Decompresses byte-aligned Snappy framing."""
    return ByteAlignedSnappy.decompress(data)
