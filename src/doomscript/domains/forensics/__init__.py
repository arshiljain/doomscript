from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.forensics.runtime import (
    forensics_magic_bytes, forensics_shannon_entropy, forensics_deobfuscate_base64
)
from doomscript.domains.forensics.parser import ForensicsDomainParser
from doomscript.domains.forensics.exporter import ForensicsASTExporter

class ForensicsRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class ForensicsDomain(DomainContract):
    name = "forensics"
    aliases = ["dfir", "digital_forensics", "file_carving"]
    description = "File signature identification, entropy calculations, and string deobfuscation"
    parser = ForensicsDomainParser()
    runtime = ForensicsRuntime()
    exporter = ForensicsASTExporter()
    capabilities = ["magic_bytes", "shannon_entropy", "deobfuscate_base64"]
    verbs = [
        VerbSpec(pattern="identify file type by magic bytes {header:expr} into {target:ident}", description="File signature match"),
        VerbSpec(pattern="calculate shannon entropy for data {data:expr} into {target:ident}", description="Entropy measurement")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("identify file type ") or s.startswith("calculate shannon entropy ") or s.startswith("deobfuscate nested base64 ")

FORENSICS_DOMAIN = ForensicsDomain()
get_domain_registry().register(FORENSICS_DOMAIN)

__all__ = [
    "ForensicsDomain", "FORENSICS_DOMAIN", "ForensicsRuntime",
    "forensics_magic_bytes", "forensics_shannon_entropy", "forensics_deobfuscate_base64"
]
