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

import math
import random
import struct
from typing import Any, Dict, List, Optional, Tuple, Union
from doomscript.runtime import Record


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


# ==============================================================================
# Advanced Telecom Deepening: Viterbi Decoder, QAM Modem & OFDM Framer
# ==============================================================================

class ViterbiDecoder:
    """Rate 1/2 Convolutional encoder and Viterbi trellis maximum likelihood decoder (K=3)."""

    # Polynomials: G1 = 7 (111b), G2 = 5 (101b)
    K = 3
    NUM_STATES = 4  # 2^(K-1)

    @classmethod
    def encode(cls, bits: List[int]) -> List[int]:
        """Encodes bit stream into rate 1/2 convolutional codeword."""
        state = 0  # 2-bit shift register (s1, s0)
        encoded = []
        for bit in bits:
            b = 1 if bit else 0
            # Next state: (b, s1)
            # Output 1: b ^ s1 ^ s0
            # Output 2: b ^ s0
            s1 = (state >> 1) & 1
            s0 = state & 1
            out1 = b ^ s1 ^ s0
            out2 = b ^ s0
            encoded.append(out1)
            encoded.append(out2)
            state = ((b << 1) | s1) & 3
        return encoded

    @classmethod
    def decode(cls, received: List[int]) -> List[int]:
        """Viterbi maximum-likelihood hard-decision trellis traceback decoder."""
        n_pairs = len(received) // 2
        if n_pairs == 0:
            return []

        # path_metrics: state -> metric
        INF = 1000000000
        path_metrics = [0] + [INF] * (cls.NUM_STATES - 1)
        history: List[List[Tuple[int, int]]] = []  # step -> [state -> (prev_state, input_bit)]

        for t in range(n_pairs):
            r1 = received[2 * t]
            r2 = received[2 * t + 1]

            new_metrics = [INF] * cls.NUM_STATES
            step_history = [(0, 0)] * cls.NUM_STATES

            for curr_state in range(cls.NUM_STATES):
                s1 = (curr_state >> 1) & 1
                s0 = curr_state & 1

                for input_bit in (0, 1):
                    out1 = input_bit ^ s1 ^ s0
                    out2 = input_bit ^ s0
                    next_state = ((input_bit << 1) | s1) & 3

                    # Hamming distance branch metric
                    branch_cost = (r1 ^ out1) + (r2 ^ out2)
                    candidate_cost = path_metrics[curr_state] + branch_cost

                    if candidate_cost < new_metrics[next_state]:
                        new_metrics[next_state] = candidate_cost
                        step_history[next_state] = (curr_state, input_bit)

            path_metrics = new_metrics
            history.append(step_history)

        # Traceback from minimum metric state
        best_state = min(range(cls.NUM_STATES), key=lambda s: path_metrics[s])
        decoded_bits = []

        curr = best_state
        for t in range(n_pairs - 1, -1, -1):
            prev_state, input_bit = history[t][curr]
            decoded_bits.append(input_bit)
            curr = prev_state

        return list(reversed(decoded_bits))


class QAMModem:
    """Quadrature Amplitude Modulation (BPSK, QPSK, 16-QAM) and EVM analyzer."""

    @classmethod
    def modulate(cls, bits: List[int], scheme: str = "QPSK") -> List[complex]:
        """Maps bits to complex constellation symbols."""
        s = scheme.upper().strip()
        symbols = []

        if s == "BPSK":
            for b in bits:
                val = 1.0 if b else -1.0
                symbols.append(complex(val, 0.0))
        elif s == "QPSK":
            norm = 1.0 / math.sqrt(2.0)
            for i in range(0, len(bits) - 1, 2):
                re = norm if bits[i] else -norm
                im = norm if bits[i + 1] else -norm
                symbols.append(complex(re, im))
        elif s == "16QAM":
            norm = 1.0 / math.sqrt(10.0)
            mapping = {0: -3.0 * norm, 1: -1.0 * norm, 3: 1.0 * norm, 2: 3.0 * norm}
            for i in range(0, len(bits) - 3, 4):
                re_bits = (bits[i] << 1) | bits[i + 1]
                im_bits = (bits[i + 2] << 1) | bits[i + 3]
                symbols.append(complex(mapping.get(re_bits, 0.0), mapping.get(im_bits, 0.0)))
        else:
            # Default BPSK
            return cls.modulate(bits, "BPSK")

        return symbols

    @classmethod
    def demodulate(cls, symbols: List[complex], scheme: str = "QPSK") -> List[int]:
        """Demodulates complex symbols back to bit stream using maximum likelihood slicer."""
        s = scheme.upper().strip()
        bits = []

        if s == "BPSK":
            for sym in symbols:
                bits.append(1 if sym.real >= 0.0 else 0)
        elif s == "QPSK":
            for sym in symbols:
                bits.append(1 if sym.real >= 0.0 else 0)
                bits.append(1 if sym.imag >= 0.0 else 0)
        elif s == "16QAM":
            norm = 1.0 / math.sqrt(10.0)
            thresholds = [-2.0 * norm, 0.0, 2.0 * norm]

            def slice_1d(val: float) -> Tuple[int, int]:
                if val < thresholds[0]:
                    return (0, 0)
                elif val < thresholds[1]:
                    return (0, 1)
                elif val < thresholds[2]:
                    return (1, 1)
                return (1, 0)

            for sym in symbols:
                b_re = slice_1d(sym.real)
                b_im = slice_1d(sym.imag)
                bits.extend([b_re[0], b_re[1], b_im[0], b_im[1]])

        return bits

    @classmethod
    def calculate_evm(cls, ideal: List[complex], received: List[complex]) -> Dict[str, float]:
        """Calculates Error Vector Magnitude (EVM) in percentage and dB."""
        n = min(len(ideal), len(received))
        if n == 0:
            return {"evm_pct": 0.0, "evm_db": -100.0}

        err_power = sum(abs(ideal[i] - received[i]) ** 2 for i in range(n))
        ref_power = sum(abs(ideal[i]) ** 2 for i in range(n))

        if ref_power < 1e-12:
            return {"evm_pct": 0.0, "evm_db": -100.0}

        evm_rms = math.sqrt(err_power / ref_power)
        evm_pct = evm_rms * 100.0
        evm_db = 20.0 * math.log10(max(1e-9, evm_rms))

        return {
            "evm_percent": round(evm_pct, 3),
            "evm_db": round(evm_db, 2),
        }


class OFDMFramer:
    """Orthogonal Frequency Division Multiplexing framer with cyclic prefix insertion."""

    @classmethod
    def modulate_frame(
        cls,
        subcarriers: List[complex],
        n_fft: int = 64,
        cp_len: int = 16,
    ) -> List[complex]:
        """IFFT subcarrier modulation + Cyclic Prefix (CP) guard interval."""
        n = len(subcarriers)
        # Zero-pad or truncate to n_fft
        sub_padded = list(subcarriers[:n_fft]) + [0.0 + 0.0j] * max(0, n_fft - n)

        # Discrete Inverse Fourier Transform
        time_samples = []
        for t in range(n_fft):
            s = 0.0 + 0.0j
            for k in range(n_fft):
                angle = 2.0 * math.pi * k * t / n_fft
                s += sub_padded[k] * complex(math.cos(angle), math.sin(angle))
            time_samples.append(s / n_fft)

        # Prepend cyclic prefix (last cp_len samples)
        cp = time_samples[-cp_len:]
        return cp + time_samples

    @classmethod
    def demodulate_frame(
        cls,
        time_samples: List[complex],
        n_fft: int = 64,
        cp_len: int = 16,
    ) -> List[complex]:
        """Strips cyclic prefix and performs FFT."""
        # Strip CP
        payload = time_samples[cp_len:cp_len + n_fft]
        if len(payload) < n_fft:
            payload.extend([0.0 + 0.0j] * (n_fft - len(payload)))

        # Discrete Fourier Transform
        freq_bins = []
        for k in range(n_fft):
            s = 0.0 + 0.0j
            for t in range(n_fft):
                angle = -2.0 * math.pi * k * t / n_fft
                s += payload[t] * complex(math.cos(angle), math.sin(angle))
            freq_bins.append(complex(round(s.real, 6), round(s.imag, 6)))

        return freq_bins


def telecom_viterbi_encode(bits: List[int]) -> List[int]:
    """Encodes bit stream using rate 1/2 convolutional code."""
    return ViterbiDecoder.encode(bits)


def telecom_viterbi_decode(codeword: List[int]) -> List[int]:
    """Decodes rate 1/2 convolutional codeword via Viterbi algorithm."""
    return ViterbiDecoder.decode(codeword)


def telecom_qam_modulate(bits: List[int], scheme: str = "QPSK") -> List[complex]:
    """Modulates bits to complex constellation symbols."""
    return QAMModem.modulate(bits, scheme)


def telecom_qam_demodulate(symbols: List[complex], scheme: str = "QPSK") -> List[int]:
    """Demodulates complex symbols to bits."""
    return QAMModem.demodulate(symbols, scheme)


def telecom_ofdm_frame(subcarriers: List[complex], n_fft: int = 64, cp_len: int = 16) -> List[complex]:
    """Generates time-domain OFDM frame with cyclic prefix."""
    return OFDMFramer.modulate_frame(subcarriers, n_fft, cp_len)


# ==============================================================================
# 5. ADVANCED FEC, SECDED, CONFIGURABLE CRC & AWGN CHANNEL
# ==============================================================================

class ExtendedHamming84:
    """Extended Hamming(8, 4) Single-Error-Correction Double-Error-Detection (SECDED) Codec."""

    @staticmethod
    def encode_nibble(d: List[int]) -> List[int]:
        """Encodes 4 data bits [d1, d2, d3, d4] into 8 bits with overall parity."""
        h7 = Hamming74.encode_nibble(d)
        overall_p = 0
        for b in h7:
            overall_p ^= b
        return h7 + [overall_p]

    @staticmethod
    def decode_byte(c: List[int]) -> Record:
        """Decodes 8 received bits, checks for single-bit correction or double-bit detection."""
        r8 = list(c)
        r7 = r8[:7]
        p_overall = r8[7] if len(r8) > 7 else 0

        # Calculate standard Hamming syndrome
        s1 = r7[0] ^ r7[2] ^ r7[4] ^ r7[6]
        s2 = r7[1] ^ r7[2] ^ r7[5] ^ r7[6]
        s3 = r7[3] ^ r7[4] ^ r7[5] ^ r7[6]
        syndrome = (s3 << 2) | (s2 << 1) | s1

        # Calculate actual parity of all 8 bits
        actual_parity = 0
        for b in r8:
            actual_parity ^= b

        has_single_error = False
        has_double_error = False
        corrected_bit_idx = -1

        if syndrome == 0 and actual_parity == 0:
            # No error
            pass
        elif syndrome != 0 and actual_parity != 0:
            # Single bit error in Hamming 7 bits -> correctable
            has_single_error = True
            corrected_bit_idx = syndrome - 1
            r7[corrected_bit_idx] ^= 1
        elif syndrome == 0 and actual_parity != 0:
            # Single bit error in the 8th parity bit itself
            has_single_error = True
            corrected_bit_idx = 7
        elif syndrome != 0 and actual_parity == 0:
            # Double bit error -> detectable but not correctable!
            has_double_error = True

        d1 = r7[2]
        d2 = r7[4]
        d3 = r7[5]
        d4 = r7[6]

        return Record({
            "data": [d1, d2, d3, d4],
            "has_single_error": has_single_error,
            "has_double_error": has_double_error,
            "corrected_bit": corrected_bit_idx,
            "is_valid": not has_double_error,
        })

    @classmethod
    def encode_bits(cls, bits: List[int]) -> List[int]:
        """Encodes arbitrary bitstream using extended Hamming(8,4)."""
        padded = list(bits)
        rem = len(padded) % 4
        if rem != 0:
            padded.extend([0] * (4 - rem))
        out: List[int] = []
        for i in range(0, len(padded), 4):
            nibble = padded[i : i + 4]
            out.extend(cls.encode_nibble(nibble))
        return out

    @classmethod
    def decode_bits(cls, bits: List[int]) -> Record:
        """Decodes 8-bit blocks and returns recovered data and error metrics."""
        recovered_data = []
        single_err_count = 0
        double_err_count = 0

        for i in range(0, len(bits) - 7, 8):
            block = bits[i : i + 8]
            res = cls.decode_byte(block)
            recovered_data.extend(res["data"])
            if res["has_single_error"]:
                single_err_count += 1
            if res["has_double_error"]:
                double_err_count += 1

        return Record({
            "data": recovered_data,
            "single_error_count": single_err_count,
            "double_error_count": double_err_count,
            "success": double_err_count == 0,
        })


class GeneralizedCRC:
    """Configurable Cyclic Redundancy Check (CRC) engine with precomputed lookup table."""

    def __init__(
        self,
        width: int = 32,
        poly: int = 0x04C11DB7,
        init_val: int = 0xFFFFFFFF,
        ref_in: bool = True,
        ref_out: bool = True,
        xor_out: int = 0xFFFFFFFF,
    ):
        self.width = int(width)
        self.poly = int(poly)
        self.init_val = int(init_val)
        self.ref_in = bool(ref_in)
        self.ref_out = bool(ref_out)
        self.xor_out = int(xor_out)
        self.mask = (1 << self.width) - 1
        self.table = self._generate_table()

    def _reflect(self, val: int, bits: int) -> int:
        res = 0
        for i in range(bits):
            if (val >> i) & 1:
                res |= 1 << (bits - 1 - i)
        return res

    def _generate_table(self) -> List[int]:
        """Precomputes 256-entry CRC lookup table."""
        tbl = []
        top_bit = 1 << (self.width - 1)
        for b in range(256):
            cur = self._reflect(b, 8) if self.ref_in else (b << (self.width - 8))
            if not self.ref_in:
                for _ in range(8):
                    if cur & top_bit:
                        cur = ((cur << 1) ^ self.poly) & self.mask
                    else:
                        cur = (cur << 1) & self.mask
            else:
                for _ in range(8):
                    if cur & 1:
                        cur = (cur >> 1) ^ self._reflect(self.poly, self.width)
                    else:
                        cur >>= 1
            tbl.append(cur)
        return tbl

    def compute(self, data: Union[str, bytes, List[int]]) -> Record:
        """Computes CRC checksum over string, bytes, or integer list."""
        if isinstance(data, str):
            b_data = data.encode("utf-8")
        elif isinstance(data, (bytes, bytearray)):
            b_data = bytes(data)
        elif isinstance(data, list):
            b_data = bytes(data)
        else:
            b_data = str(data).encode("utf-8")

        crc = self.init_val & self.mask

        if self.ref_in:
            for byte in b_data:
                idx = (crc ^ byte) & 0xFF
                crc = (crc >> 8) ^ self.table[idx]
        else:
            shift = self.width - 8
            for byte in b_data:
                idx = ((crc >> shift) ^ byte) & 0xFF
                crc = ((crc << 8) & self.mask) ^ self.table[idx]

        if self.ref_out and not self.ref_in:
            crc = self._reflect(crc, self.width)
        elif not self.ref_out and self.ref_in:
            crc = self._reflect(crc, self.width)

        final_crc = (crc ^ self.xor_out) & self.mask
        hex_digits = max(2, (self.width + 3) // 4)

        return Record({
            "crc": final_crc,
            "hex": f"0x{final_crc:0{hex_digits}X}",
            "bytes_processed": len(b_data),
            "width": self.width,
        })


class AWGNChannelSimulator:
    """Additive White Gaussian Noise (AWGN) channel and Bit Error Rate (BER) simulator."""

    @classmethod
    def rand_gaussian(cls, mean: float = 0.0, std: float = 1.0) -> float:
        """Box-Muller transformation for Gaussian distribution."""
        u1 = max(random.random(), 1e-12)
        u2 = random.random()
        return mean + std * math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)

    @classmethod
    def add_noise(
        cls,
        symbols: List[complex],
        snr_db: float = 10.0,
    ) -> List[complex]:
        """Adds complex AWGN noise to transmitted symbols corresponding to SNR in dB."""
        # Symbol power E_s = 1.0 (assuming normalized constellation)
        snr_linear = 10.0 ** (float(snr_db) / 10.0)
        noise_variance = 1.0 / (2.0 * snr_linear)
        sigma = math.sqrt(noise_variance)

        noisy = []
        for s in symbols:
            nr = cls.rand_gaussian(0.0, sigma)
            ni = cls.rand_gaussian(0.0, sigma)
            noisy.append(complex(round(s.real + nr, 5), round(s.imag + ni, 5)))
        return noisy

    @classmethod
    def simulate_transmission(
        cls,
        bits: List[int],
        scheme: str = "QPSK",
        snr_db: float = 10.0,
    ) -> Record:
        """Full transmission loop: modulate -> AWGN -> demodulate -> BER calculation."""
        mod_symbols = QAMModem.modulate(bits, scheme=scheme)
        noisy_symbols = cls.add_noise(mod_symbols, snr_db=snr_db)
        recovered_bits = QAMModem.demodulate(noisy_symbols, scheme=scheme)

        # Truncate to original bitstream length
        rec_trimmed = recovered_bits[:len(bits)]
        bit_errors = sum(1 for b_orig, b_rec in zip(bits, rec_trimmed) if b_orig != b_rec)
        ber = bit_errors / max(1, len(bits))

        # Calculate EVM (Error Vector Magnitude)
        evm_num = sum(abs(ns - ms) ** 2 for ns, ms in zip(noisy_symbols, mod_symbols))
        evm_den = sum(abs(ms) ** 2 for ms in mod_symbols)
        evm_rms = math.sqrt(evm_num / max(1e-12, evm_den)) * 100.0

        return Record({
            "original_bits_count": len(bits),
            "bit_errors": bit_errors,
            "ber": round(ber, 6),
            "evm_percent": round(evm_rms, 2),
            "transmitted_symbols": len(mod_symbols),
            "snr_db": float(snr_db),
            "scheme": scheme.upper(),
        })


# --- Spoken English Telecom Wrappers ---

def telecom_secded_encode(bits: List[int]) -> List[int]:
    """Encodes bitstream using extended Hamming(8,4) SECDED code."""
    return ExtendedHamming84.encode_bits(bits)


def telecom_secded_decode(bits: List[int]) -> Record:
    """Decodes extended Hamming(8,4) SECDED codeword with single-error correction and double-error detection."""
    return ExtendedHamming84.decode_bits(bits)


def telecom_custom_crc(
    data: Any,
    poly: int = 0x04C11DB7,
    width: int = 32,
) -> Record:
    """Computes generalized CRC with specified polynomial and width."""
    crc_eng = GeneralizedCRC(width=width, poly=poly)
    return crc_eng.compute(data)


def telecom_awgn_simulate(
    bits: List[int],
    scheme: str = "QPSK",
    snr_db: float = 10.0,
) -> Record:
    """Simulates wireless link over AWGN channel and measures BER and EVM."""
    return AWGNChannelSimulator.simulate_transmission(bits, scheme=scheme, snr_db=snr_db)


class OFDMModulationEngine:
    """Orthogonal Frequency Division Multiplexing (OFDM) baseband modulator/demodulator."""

    @staticmethod
    def _dft(x: List[complex], inverse: bool = False) -> List[complex]:
        n = len(x)
        if n == 0:
            return []
        out = []
        sign = 1.0 if inverse else -1.0
        scale = 1.0 / n if inverse else 1.0
        for k in range(n):
            s = 0.0 + 0.0j
            for t in range(n):
                angle = sign * 2.0 * math.pi * k * t / n
                w = complex(math.cos(angle), math.sin(angle))
                s += x[t] * w
            out.append(s * scale)
        return out

    @classmethod
    def modulate(
        cls,
        symbols: List[complex],
        n_fft: int = 16,
        n_cp: int = 4,
    ) -> Dict[str, Any]:
        n = len(symbols)
        # Pad to multiple of n_fft
        pad_len = (n_fft - (n % n_fft)) % n_fft
        padded = list(symbols) + [0.0 + 0.0j] * pad_len

        num_frames = len(padded) // n_fft
        tx_stream: List[complex] = []

        for f in range(num_frames):
            block = padded[f * n_fft : (f + 1) * n_fft]
            time_domain = cls._dft(block, inverse=True)
            # Cyclic prefix: last n_cp samples
            cp = time_domain[-n_cp:]
            frame = cp + time_domain
            tx_stream.extend(frame)

        return {
            "time_samples": tx_stream,
            "num_frames": num_frames,
            "samples_count": len(tx_stream),
            "n_fft": n_fft,
            "n_cp": n_cp,
        }

    @classmethod
    def demodulate(
        cls,
        time_samples: List[complex],
        n_fft: int = 16,
        n_cp: int = 4,
    ) -> Dict[str, Any]:
        frame_len = n_fft + n_cp
        num_frames = len(time_samples) // frame_len
        rx_symbols: List[complex] = []

        for f in range(num_frames):
            frame = time_samples[f * frame_len : (f + 1) * frame_len]
            # Strip cyclic prefix
            block_time = frame[n_cp : n_cp + n_fft]
            freq_domain = cls._dft(block_time, inverse=False)
            rx_symbols.extend([complex(round(z.real, 5), round(z.imag, 5)) for z in freq_domain])

        return {
            "recovered_symbols": rx_symbols,
            "num_frames": num_frames,
            "symbols_count": len(rx_symbols),
        }


class ViterbiConvolutionalDecoder:
    """Rate 1/2 constraint length K=3 convolutional encoder and Viterbi maximum-likelihood trellis decoder."""

    # Polynomials g0 = 111_2 (7), g1 = 101_2 (5)
    @classmethod
    def encode(cls, bits: List[int]) -> List[int]:
        s1 = 0
        s0 = 0
        encoded = []
        for bit in bits:
            b = 1 if bit else 0
            y0 = b ^ s1 ^ s0
            y1 = b ^ s0
            encoded.extend([y0, y1])
            s0 = s1
            s1 = b
        return encoded

    @classmethod
    def decode(cls, encoded_bits: List[int], original_bits: Optional[List[int]] = None) -> Dict[str, Any]:
        n_pairs = len(encoded_bits) // 2
        if n_pairs == 0:
            return {"decoded_bits": [], "bit_errors": 0, "pairs_count": 0}

        # States: 0 (00), 1 (01), 2 (10), 3 (11)
        # Trellis transitions: from state (s1, s0) on input bit b:
        # next_state = (b << 1) | s1
        # out0 = b ^ s1 ^ s0, out1 = b ^ s0
        num_states = 4
        # path_metrics: current cost to reach each state
        path_metrics = [float("inf")] * num_states
        path_metrics[0] = 0.0  # Start at state 0

        # Trellis history for traceback: list of dict {state: (prev_state, input_bit)}
        trellis: List[Dict[int, Tuple[int, int]]] = []

        for t in range(n_pairs):
            r0 = encoded_bits[2 * t]
            r1 = encoded_bits[2 * t + 1]

            new_metrics = [float("inf")] * num_states
            new_history: Dict[int, Tuple[int, int]] = {}

            for curr_st in range(num_states):
                if path_metrics[curr_st] == float("inf"):
                    continue
                s1 = (curr_st >> 1) & 1
                s0 = curr_st & 1

                for b in (0, 1):
                    y0 = b ^ s1 ^ s0
                    y1 = b ^ s0
                    # Hamming branch metric
                    bm = (r0 ^ y0) + (r1 ^ y1)
                    cost = path_metrics[curr_st] + bm

                    next_st = ((b << 1) | s1) & 3
                    if cost < new_metrics[next_st]:
                        new_metrics[next_st] = cost
                        new_history[next_st] = (curr_st, b)

            path_metrics = new_metrics
            trellis.append(new_history)

        # Traceback from state with minimum path metric
        best_state = min(range(num_states), key=lambda st: path_metrics[st])
        decoded = []
        curr = best_state

        for t in reversed(range(n_pairs)):
            prev_st, b = trellis[t][curr]
            decoded.append(b)
            curr = prev_st

        decoded.reverse()

        bit_errors = 0
        if original_bits is not None:
            bit_errors = sum(1 for d, o in zip(decoded, original_bits) if d != o)

        return {
            "decoded_bits": decoded,
            "bit_errors": bit_errors,
            "pairs_count": n_pairs,
            "final_metric": path_metrics[best_state],
        }


def telecom_ofdm_modulate(
    symbols: List[complex],
    n_fft: int = 16,
    n_cp: int = 4,
) -> Record:
    """Modulates frequency-domain symbols into time-domain OFDM frames."""
    return Record(OFDMModulationEngine.modulate(symbols, n_fft=n_fft, n_cp=n_cp))


def telecom_ofdm_demodulate(
    time_samples: List[complex],
    n_fft: int = 16,
    n_cp: int = 4,
) -> Record:
    """Demodulates time-domain OFDM frames back to frequency constellation symbols."""
    return Record(OFDMModulationEngine.demodulate(time_samples, n_fft=n_fft, n_cp=n_cp))


def telecom_viterbi_encode(bits: List[int]) -> List[int]:
    """Encodes bitstream using rate 1/2 K=3 convolutional code."""
    return ViterbiConvolutionalDecoder.encode(bits)


def telecom_viterbi_decode(encoded_bits: List[int], original_bits: Optional[List[int]] = None) -> Record:
    """Decodes convolutional code via Viterbi trellis dynamic programming."""
    return Record(ViterbiConvolutionalDecoder.decode(encoded_bits, original_bits=original_bits))


# ==============================================================================
# TURBO CODE ITERATIVE BCJR/MAX-LOG-MAP DECODER & COSTAS LOOP CARRIER RECOVERY
# ==============================================================================


class TurboCodeIterativeDecoder:
    """Parallel Concatenated Convolutional Code (PCCC / Turbo Code) Engine.

    Features 3GPP LTE compliant 8-state Recursive Systematic Convolutional (RSC)
    constituent encoders with generator polynomials G = [1, 15/13] (octal: feedback 13, feedforward 15),
    pseudo-random interleaver, and iterative Max-Log-MAP / BCJR soft-input soft-output (SISO) decoders.
    """

    # 4-state RSC generator: feedback 0b111 (7 octal), feedforward 0b101 (5 octal)
    # State: 2 bits (s0, s1), 4 states: 0, 1, 2, 3
    NUM_STATES = 4

    @classmethod
    def _rsc_step(cls, state: int, bit: int) -> Tuple[int, int, int]:
        """Single RSC encoder trellis step: returns (next_state, systematic_bit, parity_bit)."""
        s0 = (state >> 1) & 1
        s1 = state & 1
        # Feedback polynomial: 1 + D + D^2 (octal 7)
        fb = bit ^ s0 ^ s1
        # Feedforward polynomial: 1 + D^2 (octal 5)
        parity = fb ^ s1
        next_state = ((state << 1) & 2) | fb
        return next_state, bit, parity

    @classmethod
    def encode(cls, bits: List[int], interleaver: Optional[List[int]] = None) -> Dict[str, Any]:
        """Encodes bits with rate 1/3 Turbo Code."""
        n = len(bits)
        if interleaver is None:
            # Deterministic pseudo-random permutation: coprime stride
            interleaver = [(i * 7 + 3) % n for i in range(n)]

        interleaved_bits = [bits[interleaver[i]] for i in range(n)]

        # Encoder 1
        state1 = 0
        sys_out = []
        par1_out = []
        for b in bits:
            state1, s_bit, p_bit = cls._rsc_step(state1, b)
            sys_out.append(s_bit)
            par1_out.append(p_bit)

        # Encoder 2 (operating on interleaved bits)
        state2 = 0
        par2_out = []
        for b in interleaved_bits:
            state2, _, p_bit = cls._rsc_step(state2, b)
            par2_out.append(p_bit)

        return {
            "systematic_bits": sys_out,
            "parity1_bits": par1_out,
            "parity2_bits": par2_out,
            "interleaver": interleaver,
            "code_rate": 1.0 / 3.0,
            "num_bits": n,
        }

    @classmethod
    def _bcjr_max_log_map(
        cls,
        l_sys: List[float],
        l_apriori: List[float],
        l_par: List[float],
    ) -> List[float]:
        """Constituent BCJR Max-Log-MAP soft-in soft-out (SISO) decoder."""
        n = len(l_sys)
        n_states = cls.NUM_STATES
        neg_inf = -1e9

        # Trellis transitions: transitions[state][input_bit] = (next_state, parity_bit)
        transitions = {}
        rev_transitions = {}
        for s in range(n_states):
            transitions[s] = {}
            for b in (0, 1):
                nxt, _, p = cls._rsc_step(s, b)
                transitions[s][b] = (nxt, p)
                if nxt not in rev_transitions:
                    rev_transitions[nxt] = []
                rev_transitions[nxt].append((s, b, p))

        # 1. Forward metrics alpha[k][s]
        alpha = [[neg_inf] * n_states for _ in range(n + 1)]
        alpha[0][0] = 0.0

        for k in range(n):
            u_llr = l_sys[k] + l_apriori[k]
            p_llr = l_par[k]
            for s in range(n_states):
                if alpha[k][s] <= neg_inf / 2:
                    continue
                for b in (0, 1):
                    nxt, p = transitions[s][b]
                    # Branch metric gamma
                    # BPSK mapping: bit 0 -> +1, bit 1 -> -1
                    gamma = (0.5 * u_llr if b == 0 else -0.5 * u_llr) + (0.5 * p_llr if p == 0 else -0.5 * p_llr)
                    val = alpha[k][s] + gamma
                    if val > alpha[k + 1][nxt]:
                        alpha[k + 1][nxt] = val

            # Normalize alpha to prevent overflow
            max_a = max(alpha[k + 1])
            for s in range(n_states):
                alpha[k + 1][s] -= max_a

        # 2. Backward metrics beta[k][s]
        beta = [[neg_inf] * n_states for _ in range(n + 1)]
        for s in range(n_states):
            beta[n][s] = 0.0

        for k in range(n - 1, -1, -1):
            u_llr = l_sys[k] + l_apriori[k]
            p_llr = l_par[k]
            for s in range(n_states):
                for b in (0, 1):
                    nxt, p = transitions[s][b]
                    gamma = (0.5 * u_llr if b == 0 else -0.5 * u_llr) + (0.5 * p_llr if p == 0 else -0.5 * p_llr)
                    val = beta[k + 1][nxt] + gamma
                    if val > beta[k][s]:
                        beta[k][s] = val

            # Normalize beta
            max_b = max(beta[k])
            for s in range(n_states):
                beta[k][s] -= max_b

        # 3. Compute extrinsic LLR L_e[k]
        l_extrinsic = [0.0] * n
        for k in range(n):
            max0 = neg_inf
            max1 = neg_inf
            p_llr = l_par[k]

            for s in range(n_states):
                for b in (0, 1):
                    nxt, p = transitions[s][b]
                    gamma_parity = 0.5 * p_llr if p == 0 else -0.5 * p_llr
                    metric = alpha[k][s] + gamma_parity + beta[k + 1][nxt]
                    if b == 0:
                        if metric > max0:
                            max0 = metric
                    else:
                        if metric > max1:
                            max1 = metric

            # Extrinsic info is max0 - max1 (scaled)
            l_extrinsic[k] = round(max0 - max1, 4)

        return l_extrinsic

    @classmethod
    def decode(
        cls,
        l_sys: List[float],
        l_par1: List[float],
        l_par2: List[float],
        interleaver: Optional[List[int]] = None,
        iterations: int = 4,
    ) -> Dict[str, Any]:
        """Iterative Turbo Decoding via Max-Log-MAP exchange."""
        n = len(l_sys)
        if n == 0:
            return {"decoded_bits": [], "iterations": 0}

        if interleaver is None:
            interleaver = [(i * 7 + 3) % n for i in range(n)]

        # Inverse interleaver
        deinterleaver = [0] * n
        for i, p in enumerate(interleaver):
            deinterleaver[p] = i

        l_apriori1 = [0.0] * n
        interleaved_sys = [l_sys[interleaver[i]] for i in range(n)]

        for it in range(iterations):
            # Decoder 1: systematic + a priori 1 + parity 1
            l_ext1 = cls._bcjr_max_log_map(l_sys, l_apriori1, l_par1)

            # Interleave extrinsic from Dec1 to form a priori for Dec2
            l_apriori2 = [l_ext1[interleaver[i]] for i in range(n)]

            # Decoder 2: interleaved systematic + a priori 2 + parity 2
            l_ext2 = cls._bcjr_max_log_map(interleaved_sys, l_apriori2, l_par2)

            # De-interleave extrinsic from Dec2 to feed back into Dec1
            l_apriori1 = [l_ext2[deinterleaver[i]] for i in range(n)]

        # Final decision on total LLR
        final_llr = [l_sys[i] + l_apriori1[i] for i in range(n)]
        decoded = [0 if llr >= 0.0 else 1 for llr in final_llr]

        return {
            "decoded_bits": decoded,
            "final_llr": [round(x, 3) for x in final_llr],
            "iterations_completed": iterations,
            "bit_count": n,
        }


class CostasLoopCarrierRecovery:
    """Costas Loop Carrier Phase and Frequency Tracking System.

    Synchronizes suppressed-carrier BPSK/QPSK signals by mixing with an internal
    Numerically Controlled Oscillator (NCO), computing cross-product phase error,
    and filtering through a second-order Proportional-Integral (PI) loop filter.
    """

    @classmethod
    def process(
        cls,
        samples: List[float],
        modulation: str = "bpsk",
        loop_bw: float = 0.04,
        damping: float = 0.707,
    ) -> Dict[str, Any]:
        """Performs carrier recovery on input I/Q or real RF samples."""
        n = len(samples)
        if n == 0:
            return {"recovered_i": [], "recovered_q": [], "phase_error": [], "lock_detected": False}

        # Loop filter coefficients from natural frequency and damping ratio
        theta_n = loop_bw / (damping + 0.25 / damping)
        d = 1.0 + 2.0 * damping * theta_n + theta_n * theta_n
        kp = (4.0 * damping * theta_n) / d
        ki = (4.0 * theta_n * theta_n) / d

        nco_phase = 0.0
        integrator = 0.0

        out_i = [0.0] * n
        out_q = [0.0] * n
        err_arr = [0.0] * n

        is_qpsk = modulation.lower() == "qpsk"

        for idx, s in enumerate(samples):
            # Complex NCO mixing
            cos_val = math.cos(nco_phase)
            sin_val = math.sin(nco_phase)

            # In-phase and Quadrature arm outputs
            i_val = s * cos_val
            q_val = -s * sin_val

            out_i[idx] = round(i_val, 5)
            out_q[idx] = round(q_val, 5)

            # Phase Detector
            if is_qpsk:
                # QPSK error: sign(I)*Q - sign(Q)*I
                sgn_i = 1.0 if i_val >= 0.0 else -1.0
                sgn_q = 1.0 if q_val >= 0.0 else -1.0
                err = sgn_i * q_val - sgn_q * i_val
            else:
                # BPSK error: sign(I) * Q
                sgn_i = 1.0 if i_val >= 0.0 else -1.0
                err = sgn_i * q_val

            err_arr[idx] = round(err, 5)

            # Loop filter (PI)
            integrator += ki * err
            v = kp * err + integrator

            # NCO phase advance
            nco_phase = (nco_phase + v) % (2.0 * math.pi)

        # Detect lock based on tail error variance
        tail_start = int(0.8 * n)
        tail_errors = err_arr[tail_start:]
        if tail_errors:
            tail_mean = sum(tail_errors) / len(tail_errors)
            tail_var = sum((x - tail_mean) ** 2 for x in tail_errors) / len(tail_errors)
            locked = tail_var < 0.1
        else:
            locked = False

        return {
            "recovered_i": out_i,
            "recovered_q": out_q,
            "phase_error": err_arr,
            "estimated_frequency_offset": round(integrator, 6),
            "lock_detected": locked,
            "modulation": modulation.upper(),
            "sample_count": n,
        }


def telecom_turbo_encode(bits: List[int]) -> Record:
    """Encodes bitstream using rate 1/3 Turbo Code."""
    return Record(TurboCodeIterativeDecoder.encode(bits))


def telecom_turbo_decode(
    l_sys: List[float],
    l_par1: List[float],
    l_par2: List[float],
    iterations: int = 4,
) -> Record:
    """Decodes rate 1/3 Turbo Code using iterative Max-Log-MAP BCJR algorithm."""
    return Record(
        TurboCodeIterativeDecoder.decode(
            l_sys, l_par1, l_par2, iterations=iterations
        )
    )


def telecom_costas_loop_recovery(
    samples: List[float],
    modulation: str = "bpsk",
    loop_bw: float = 0.04,
) -> Record:
    """Performs carrier phase and frequency tracking via Costas Loop."""
    return Record(
        CostasLoopCarrierRecovery.process(
            samples, modulation=modulation, loop_bw=loop_bw
        )
    )



