from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.forensics.runtime import (
    ForensicsRuntime, forensics_magic_bytes, forensics_shannon_entropy,
    forensics_deobfuscate_base64, forensics_dga_score,
    forensics_detect_shellcode_nop_sled, forensics_detect_timestomping,
    forensics_lsb_steganography_check
)
from doomscript.domains.forensics.parser import ForensicsDomainParser
from doomscript.domains.forensics.exporter import ForensicsASTExporter

class ForensicsDomain(DomainContract):
    name = "forensics"
    aliases = ["digital_forensics", "dfir", "artifact_analysis"]
    description = "Digital forensics & malware triage: Magic byte identification, Shannon entropy, Base64 deobfuscation, DGA detection, and timestomping"
    parser = ForensicsDomainParser()
    runtime = ForensicsRuntime()
    exporter = ForensicsASTExporter()
    capabilities = ["magic_bytes", "shannon_entropy", "deobfuscate_base64", "dga_score", "nop_sled", "timestomping", "lsb_stego"]
    verbs = [
        VerbSpec(pattern="identify file type by magic bytes {header:expr} into {target:ident}", description="Magic bytes"),
        VerbSpec(pattern="calculate shannon entropy for data {data:expr} into {target:ident}", description="Entropy"),
        VerbSpec(pattern="check dga domain {d:expr} into {target:ident}", description="DGA detection"),
        VerbSpec(pattern="deobfuscate nested base64 {data:expr} into {target:ident}", description="Base64 deobfuscation")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("identify file type ") or
            s.startswith("calculate shannon entropy ") or
            s.startswith("deobfuscate nested base64 ") or
            s.startswith("check dga domain ") or
            s.startswith("check nop sled ")
        )

FORENSICS_DOMAIN = ForensicsDomain()
get_domain_registry().register(FORENSICS_DOMAIN)

__all__ = [
    "ForensicsDomain", "FORENSICS_DOMAIN", "ForensicsRuntime",
    "forensics_magic_bytes", "forensics_shannon_entropy",
    "forensics_deobfuscate_base64", "forensics_dga_score",
    "forensics_detect_shellcode_nop_sled", "forensics_detect_timestomping",
    "forensics_lsb_steganography_check"
]
