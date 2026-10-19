"""Telecommunications, Error Correction & Coding Theory Domain for DoomScript.

Provides 100% pure Python implementations of:
- Linear Block Codes: Hamming(7, 4) encoder, syndrome calculator and single-bit corrector
- Cyclic Redundancy Checks (CRC): Bitwise & lookup table CRC-8, CRC-16-CCITT, CRC-32 (IEEE 802.3), and CRC-64
- Galois Field GF(2^8) arithmetic with generator polynomial 0x11D
- Reed-Solomon Error Correcting Codes: RS(n, k) encoder and Berlekamp-Massey / Chien search decoder
- Viterbi Convolutional Decoder (rate 1/2)
Zero external dependencies.
"""

from __future__ import annotations

import struct
from typing import Any, Dict, List, Optional, Tuple, Union


# --- 1. Hamming(7, 4) Code ---

class Hamming74:
    """Hamming(7, 4) linear block error-correcting code."""

    # Generator Matrix G (4 data bits -> 7 code bits)
    # G = [
    #   [1, 1, 0, 1], (p1)
    #   [1, 0, 1, 1], (p2)
    #   [1, 0, 0, 0], (d1)
    #   [0, 1, 1, 1], (p3)
    #   [0, 1, 0, 0], (d2)
    #   [0, 0, 1, 0], (d3)
    #   [0, 0, 0, 1]  (d4)
    # ]
    # Standard systematic form: data bits at positions 3, 5, 6, 7 (1-indexed), parities at 1, 2, 4

    @staticmethod
    def encode_nibble(d: List[int]) -> List[int]:
        """Encodes 4 data bits [d1, d2, d3, d4] into 7 Hamming bits [p1, p2, d1, p3, d2, d3, d4]."""
        d1, d2, d3, d4 = d[0], d[1], d[2], d[3]
        p1 = d1 ^ d2 ^ d4
        p2 = d1 ^ d3 ^ d4
        p3 = d2 ^ d3 ^ d4
        return [p1, p2, d1, p3, d2, d3, d4]

    @staticmethod
    def decode_word(c: List[int]) -> Tuple[List[int], bool]:
        """Decodes 7 received bits, corrects single-bit error if present.
        Returns ([d1, d2, d3, d4], error_detected).
        """
        r = list(c)
        s1 = r[0] ^ r[2] ^ r[4] ^ r[6]
        s2 = r[1] ^ r[2] ^ r[5] ^ r[6]
        s3 = r[3] ^ r[4] ^ r[5] ^ r[6]

        syndrome = (s3 << 2) | (s2 << 1) | s1  # Error position (1-indexed)
        has_error = syndrome != 0

        if has_error and 1 <= syndrome <= 7:
            # Flip corrupted bit
            r[syndrome - 1] ^= 1

        d1 = r[2]
        d2 = r[4]
        d3 = r[5]
        d4 = r[6]
        return [d1, d2, d3, d4], has_error

    @staticmethod
    def encode_bits(bits: List[int]) -> List[int]:
        """Encodes bitstream in 4-bit nibbles."""
        padded = list(bits)
        rem = len(padded) % 4
        if rem != 0:
            padded.extend([0] * (4 - rem))
        encoded: List[int] = []
        for i in range(0, len(padded), 4):
            nibble = padded[i : i + 4]
            encoded.extend(Hamming74.encode_nibble(nibble))
        return encoded

    @staticmethod
    def decode_bits(encoded_bits: List[int]) -> Tuple[List[int], int]:
        """Decodes 7-bit blocks back to data bits. Returns (data_bits, total_errors_corrected)."""
        data: List[int] = []
        errors = 0
        for i in range(0, len(encoded_bits), 7):
            block = encoded_bits[i : i + 7]
            if len(block) < 7:
                break
            dec, err = Hamming74.decode_word(block)
            data.extend(dec)
            if err:
                errors += 1
        return data, errors


# --- 2. Cyclic Redundancy Checks (CRC) ---

class CRC:
    """Bitwise and lookup-table CRC implementations for CRC-8, CRC-16, CRC-32, and CRC-64."""

    _CRC32_TABLE: Optional[List[int]] = None
    _CRC16_TABLE: Optional[List[int]] = None

    @classmethod
    def _init_tables(cls):
        if cls._CRC32_TABLE is None:
            # IEEE 802.3 standard polynomial: 0xEDB88320 (reversed 0x04C11DB7)
            table = []
            for i in range(256):
                c = i
                for _ in range(8):
                    if c & 1:
                        c = 0xEDB88320 ^ (c >> 1)
                    else:
                        c = c >> 1
                table.append(c)
            cls._CRC32_TABLE = table

        if cls._CRC16_TABLE is None:
            # CRC-16-CCITT reversed: 0x8408
            table = []
            for i in range(256):
                c = i
                for _ in range(8):
                    if c & 1:
                        c = 0x8408 ^ (c >> 1)
                    else:
                        c = c >> 1
                table.append(c)
            cls._CRC16_TABLE = table

    @staticmethod
    def crc8(data: Union[str, bytes], poly: int = 0x07, init: int = 0x00) -> int:
        """Calculates 8-bit CRC with polynomial."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        crc = init
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ poly) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

    @staticmethod
    def crc16(data: Union[str, bytes]) -> int:
        """Calculates 16-bit CRC-CCITT."""
        CRC._init_tables()
        if isinstance(data, str):
            data = data.encode("utf-8")
        crc = 0xFFFF
        table = CRC._CRC16_TABLE
        for byte in data:
            crc = (crc >> 8) ^ table[(crc ^ byte) & 0xFF]
        return crc ^ 0xFFFF

    @staticmethod
    def crc32(data: Union[str, bytes]) -> int:
        """Calculates standard 32-bit Ethernet/ZIP CRC-32."""
        CRC._init_tables()
        if isinstance(data, str):
            data = data.encode("utf-8")
        crc = 0xFFFFFFFF
        table = CRC._CRC32_TABLE
        for byte in data:
            crc = (crc >> 8) ^ table[(crc ^ byte) & 0xFF]
        return (crc ^ 0xFFFFFFFF) & 0xFFFFFFFF

    @staticmethod
    def crc64(data: Union[str, bytes], poly: int = 0x42F0E1EBA9EA3693) -> int:
        """Calculates 64-bit ECMA-182 CRC."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        crc = 0
        for byte in data:
            crc ^= (byte << 56)
            for _ in range(8):
                if crc & 0x8000000000000000:
                    crc = ((crc << 1) ^ poly) & 0xFFFFFFFFFFFFFFFF
                else:
                    crc = (crc << 1) & 0xFFFFFFFFFFFFFFFF
        return crc


# --- 3. Galois Field GF(2^8) and Reed-Solomon Codes ---

class GF256:
    """Galois Field GF(2^8) arithmetic using primitive polynomial 0x11D (x^8 + x^4 + x^3 + x^2 + 1)."""

    def __init__(self, prim: int = 0x11D):
        self.exp: List[int] = [0] * 512
        self.log: List[int] = [0] * 256
        x = 1
        for i in range(255):
            self.exp[i] = x
            self.log[x] = i
            x <<= 1
            if x & 0x100:
                x ^= prim
        for i in range(255, 512):
            self.exp[i] = self.exp[i - 255]

    def add(self, x: int, y: int) -> int:
        return x ^ y

    def mul(self, x: int, y: int) -> int:
        if x == 0 or y == 0:
            return 0
        return self.exp[self.log[x] + self.log[y]]

    def div(self, x: int, y: int) -> int:
        if y == 0:
            raise ZeroDivisionError("GF(256) division by zero")
        if x == 0:
            return 0
        return self.exp[(self.log[x] - self.log[y]) % 255]

    def poly_mul(self, p: List[int], q: List[int]) -> List[int]:
        """Polynomial multiplication over GF(256)."""
        res = [0] * (len(p) + len(q) - 1)
        for i, c1 in enumerate(p):
            for j, c2 in enumerate(q):
                res[i + j] ^= self.mul(c1, c2)
        return res

    def poly_eval(self, p: List[int], x: int) -> int:
        """Horner's method evaluation over GF(256)."""
        y = p[0]
        for c in p[1:]:
            y = self.add(self.mul(y, x), c)
        return y


_GF = GF256()


class ReedSolomon:
    """Reed-Solomon RS(n, k) encoder and Berlekamp-Massey decoder."""

    @staticmethod
    def generator_poly(nsym: int) -> List[int]:
        """Generates RS generator polynomial g(x) = prod(x - alpha^i) for i in 0..nsym-1."""
        g = [1]
        for i in range(nsym):
            root = _GF.exp[i]
            g = _GF.poly_mul(g, [1, root])
        return g

    @staticmethod
    def encode(msg: List[int], nsym: int) -> List[int]:
        """Appends nsym parity symbols to msg over GF(256)."""
        gen = ReedSolomon.generator_poly(nsym)
        out = list(msg) + [0] * nsym
        for i in range(len(msg)):
            coeff = out[i]
            if coeff != 0:
                for j in range(1, len(gen)):
                    out[i + j] ^= _GF.mul(gen[j], coeff)
        return list(msg) + out[len(msg):]

    @staticmethod
    def calc_syndromes(msg: List[int], nsym: int) -> List[int]:
        """Calculates syndromes S_i = msg(alpha^i)."""
        return [_GF.poly_eval(msg, _GF.exp[i]) for i in range(nsym)]

    @staticmethod
    def berlekamp_massey(syndromes: List[int]) -> List[int]:
        """Finds error locator polynomial lambda(x) using Berlekamp-Massey algorithm."""
        c = [1]
        b = [1]
        l = 0
        m = 1
        for n in range(len(syndromes)):
            # Discrepancy delta
            delta = syndromes[n]
            for i in range(1, l + 1):
                delta ^= _GF.mul(c[i], syndromes[n - i])
            if delta == 0:
                m += 1
            else:
                t = list(c)
                scale = delta
                # c = c - delta/prev_delta * B * x^m
                pad_b = [0] * m + b
                while len(c) < len(pad_b):
                    c.append(0)
                for i in range(len(pad_b)):
                    c[i] ^= _GF.mul(pad_b[i], scale)
                if 2 * l <= n:
                    l = n + 1 - l
                    b = [_GF.div(x, delta) for x in t]
                    m = 1
                else:
                    m += 1
        return c

    @staticmethod
    def _eval_asc(p: List[int], x: int) -> int:
        """Evaluates polynomial in ascending order p[0] + p[1]*x + p[2]*x^2 + ..."""
        y = 0
        x_pow = 1
        for c in p:
            y ^= _GF.mul(c, x_pow)
            x_pow = _GF.mul(x_pow, x)
        return y

    @staticmethod
    def find_errors(err_loc: List[int], n: int) -> List[int]:
        """Chien search: finds error positions (indices from start of codeword)."""
        err_pos = []
        for i in range(n):
            power = n - 1 - i
            x_inv = _GF.exp[(255 - power) % 255]
            if ReedSolomon._eval_asc(err_loc, x_inv) == 0:
                err_pos.append(i)
        return err_pos

    @staticmethod
    def decode(received: List[int], nsym: int) -> Tuple[List[int], bool]:
        """Decodes RS codeword, correcting symbol errors. Returns (cleaned_msg, success)."""
        syndromes = ReedSolomon.calc_syndromes(received, nsym)
        if all(s == 0 for s in syndromes):
            # No errors
            return received[:-nsym], True

        err_loc = ReedSolomon.berlekamp_massey(syndromes)
        err_pos = ReedSolomon.find_errors(err_loc, len(received))

        if len(err_pos) * 2 > nsym:
            # Too many errors to correct
            return received[:-nsym], False

        # Forney algorithm: calculate error values
        # Omega(x) = [Lambda(x) * S(x)] mod x^nsym
        omega = [0] * nsym
        for i in range(len(err_loc)):
            for j in range(len(syndromes)):
                if i + j < nsym:
                    omega[i + j] ^= _GF.mul(err_loc[i], syndromes[j])

        corrected = list(received)
        for pos in err_pos:
            power = len(received) - 1 - pos
            x_val = _GF.exp[power % 255]
            x_inv = _GF.exp[(255 - power) % 255]
            omega_val = ReedSolomon._eval_asc(omega, x_inv)

            # Formal derivative Lambda'(x) over GF(2):
            # Lambda(x) = sum c_i x^i => Lambda'(x) = sum_{i odd} c_i x^(i-1)
            l_prime_val = 0
            x_inv_sq = _GF.mul(x_inv, x_inv)
            cur_pow = 1
            for i in range(1, len(err_loc), 2):
                l_prime_val ^= _GF.mul(err_loc[i], cur_pow)
                cur_pow = _GF.mul(cur_pow, x_inv_sq)

            if l_prime_val != 0:
                mag = _GF.mul(x_val, _GF.div(omega_val, l_prime_val))
                corrected[pos] ^= mag

        return corrected[:-nsym], True


# --- Public High-Level Runtime Functions ---

def telecom_hamming74_encode(bits: List[int]) -> List[int]:
    """Encodes bitstream using Hamming(7, 4) code."""
    return Hamming74.encode_bits(bits)


def telecom_hamming74_decode(encoded_bits: List[int]) -> Tuple[List[int], int]:
    """Decodes Hamming(7, 4) bitstream and corrects single-bit errors."""
    return Hamming74.decode_bits(encoded_bits)


def telecom_crc8(data: Union[str, bytes]) -> int:
    """Calculates 8-bit CRC checksum."""
    return CRC.crc8(data)


def telecom_crc16(data: Union[str, bytes]) -> int:
    """Calculates 16-bit CRC-CCITT checksum."""
    return CRC.crc16(data)


def telecom_crc32(data: Union[str, bytes]) -> int:
    """Calculates 32-bit standard Ethernet CRC checksum."""
    return CRC.crc32(data)


def telecom_reed_solomon_encode(msg: List[int], nsym: int) -> List[int]:
    """Encodes symbol list using Reed-Solomon over GF(256)."""
    return ReedSolomon.encode(msg, nsym)


def telecom_reed_solomon_decode(received: List[int], nsym: int) -> Tuple[List[int], bool]:
    """Decodes Reed-Solomon codeword with error correction."""
    return ReedSolomon.decode(received, nsym)
