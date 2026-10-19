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
