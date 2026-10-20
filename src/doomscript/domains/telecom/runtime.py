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
