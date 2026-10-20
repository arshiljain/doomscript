"""Telecommunications, Error Correction & Coding Theory Domain Pack for DoomScript.

Enables native spoken-English Hamming(7,4), CRC-8/16/32/64, and Reed-Solomon error correction
via 'use telecom'.
"""

from typing import List, Optional, Dict, Any
from doomscript.domains.base import (
    DomainContract,
    DomainRuntime,
    DomainIR,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.telecom.runtime import (
    Hamming74,
    CRC,
    GF256,
    ReedSolomon,
    telecom_hamming74_encode,
    telecom_hamming74_decode,
    telecom_crc8,
    telecom_crc16,
    telecom_crc32,
    telecom_reed_solomon_encode,
    telecom_reed_solomon_decode,
    ViterbiDecoder,
    QAMModem,
    OFDMFramer,
    telecom_viterbi_encode,
    telecom_viterbi_decode,
    telecom_qam_modulate,
    telecom_qam_demodulate,
    telecom_ofdm_frame,
)
from doomscript.domains.telecom.parser import TelecomDomainParser
from doomscript.domains.telecom.exporter import TelecomASTExporter


class TelecomRuntime(DomainRuntime):
    """Runtime coordinator for telecommunications routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


class TelecomDomain(DomainContract):
    """Domain contract for Telecommunications & Error Correction."""

    name = "telecom"
    aliases = ["telecommunications", "fec", "ecc", "crc"]
    description = "Forward error correction, Hamming(7,4), CRC-32/16/8, Galois field arithmetic, and Reed-Solomon coding"
    parser = TelecomDomainParser()
    runtime = TelecomRuntime()
    exporter = TelecomASTExporter()
    capabilities = ["hamming74", "crc32", "crc16", "crc8", "reed_solomon"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="encode bits {bits:expr} with hamming74 into {target:ident}",
            description="Encodes bitstream using Hamming(7,4) linear block code",
        ),
        VerbSpec(
            pattern="decode bits {bits:expr} with hamming74 into {target:ident}",
            description="Decodes Hamming(7,4) code bits and corrects single-bit errors",
        ),
        VerbSpec(
            pattern="calculate crc32 of {data:expr} into {target:ident}",
            description="Calculates 32-bit Ethernet CRC checksum",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("encode bits ")
            or s.startswith("decode bits ")
            or s.startswith("calculate crc32 of ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


TELECOM_DOMAIN = TelecomDomain()
get_domain_registry().register(TELECOM_DOMAIN)

__all__ = [
    "TelecomDomain",
    "TELECOM_DOMAIN",
    "TelecomRuntime",
    "Hamming74",
    "CRC",
    "GF256",
    "ReedSolomon",
    "telecom_hamming74_encode",
    "telecom_hamming74_decode",
    "telecom_crc8",
    "telecom_crc16",
    "telecom_crc32",
    "telecom_reed_solomon_encode",
    "telecom_reed_solomon_decode",
    "ViterbiDecoder",
    "QAMModem",
    "OFDMFramer",
    "telecom_viterbi_encode",
    "telecom_viterbi_decode",
    "telecom_qam_modulate",
    "telecom_qam_demodulate",
    "telecom_ofdm_frame",
]
