"""Cybersecurity, Cryptanalysis & Security Forensics Domain Pack for DoomScript.

Enables native spoken-English password entropy analysis, Caesar/Vigenere/XOR cryptanalysis,
JWT parsing & verification, hexdumps, and CVSS scores via 'use sec'.
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
from doomscript.domains.sec.runtime import (
    SecRuntime,
    sec_password_entropy,
    sec_password_audit,
    sec_caesar_crack,
    sec_vigenere_encode,
    sec_vigenere_decode,
    sec_frequency_analysis,
    sec_xor_cipher,
    sec_jwt_decode,
    sec_jwt_verify,
    sec_hexdump,
    sec_cvss_score,
    sec_parse_banner,
    ShamirSecretSharing,
    TOTPGenerator,
    Secp256k1Curve,
    PBKDF2KeyDeriver,
    TOTPAuthenticator,
    sec_derive_pbkdf2,
    sec_totp_generate,
    sec_totp_verify,
    sec_shamir_split,
    sec_shamir_combine,
)
from doomscript.domains.sec.parser import SecDomainParser
from doomscript.domains.sec.exporter import SecASTExporter


class SecDomain(DomainContract):
    """Domain contract for Cybersecurity & Cryptanalysis."""

    name = "sec"
    aliases = ["security", "crypto"]
    description = "Cybersecurity, password entropy, cryptanalysis, JWT, and vulnerability metrics"
    parser = SecDomainParser()
    runtime = SecRuntime()
    exporter = SecASTExporter()
    capabilities = ["entropy", "jwt", "caesar_crack", "vigenere", "cvss", "hexdump"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="calculate password entropy for {pass:expr} into {target:ident}",
            description="Calculates Shannon password entropy in bits",
        ),
        VerbSpec(
            pattern="audit password strength for {pass:expr} into {target:ident}",
            description="Audits password strength score and resistance to cracking",
        ),
        VerbSpec(
            pattern="crack caesar cipher {ctx:expr} into {target:ident}",
            description="Breaks Caesar cipher using letter frequency analysis",
        ),
        VerbSpec(
            pattern="encode text {txt:expr} with vigenere key {key:expr} into {target:ident}",
            description="Encrypts text using polyalphabetic Vigenere cipher",
        ),
        VerbSpec(
            pattern="decode vigenere {ctx:expr} with key {key:expr} into {target:ident}",
            description="Decrypts text using Vigenere cipher",
        ),
        VerbSpec(
            pattern="verify jwt token {tok:expr} with secret {sec:expr} into {target:ident}",
            description="Verifies HMAC-SHA256 signature of a JWT token",
        ),
        VerbSpec(
            pattern="generate hexdump of {data:expr} into {target:ident}",
            description="Formats binary data into canonical hexdump view",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("calculate password entropy ")
            or s.startswith("audit password strength ")
            or s.startswith("crack caesar cipher ")
            or s.startswith("encode text ") and " with vigenere key " in s
            or s.startswith("decode vigenere ")
            or s.startswith("frequency analysis of ")
            or s.startswith("xor encrypt ")
            or s.startswith("decode jwt token ")
            or s.startswith("verify jwt token ")
            or s.startswith("generate hexdump of ")
            or s.startswith("calculate cvss score ")
            or s.startswith("parse port banner ")
            or s.startswith("derive pbkdf2 key ")
            or s.startswith("generate totp token ")
            or s.startswith("verify totp token ")
            or s.startswith("split secret ")
            or s.startswith("combine secret shares ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


SEC_DOMAIN = SecDomain()
get_domain_registry().register(SEC_DOMAIN)

__all__ = [
    "SecDomain",
    "SEC_DOMAIN",
    "SecRuntime",
    "SecDomainParser",
    "SecASTExporter",
    "sec_password_entropy",
    "sec_password_audit",
    "sec_caesar_crack",
    "sec_vigenere_encode",
    "sec_vigenere_decode",
    "sec_frequency_analysis",
    "sec_xor_cipher",
    "sec_jwt_decode",
    "sec_jwt_verify",
    "sec_hexdump",
    "sec_cvss_score",
    "sec_parse_banner",
    "ShamirSecretSharing",
    "TOTPGenerator",
    "Secp256k1Curve",
    "PBKDF2KeyDeriver",
    "TOTPAuthenticator",
    "sec_derive_pbkdf2",
    "sec_totp_generate",
    "sec_totp_verify",
    "sec_shamir_split",
    "sec_shamir_combine",
]
