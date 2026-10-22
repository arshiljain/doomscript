from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.genai.runtime import (
    genai_chunk_text, genai_cosine_similarity, genai_retrieve_top_k,
    genai_estimate_tokens, genai_apply_template
)
from doomscript.domains.genai.parser import GenaiDomainParser
from doomscript.domains.genai.exporter import GenaiASTExporter

class GenaiRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class GenaiDomain(DomainContract):
    name = "genai"
    aliases = ["llm", "rag", "prompts"]
    description = "Generative AI, LLM prompting, RAG chunking, and vector retrieval"
    parser = GenaiDomainParser()
    runtime = GenaiRuntime()
    exporter = GenaiASTExporter()
    capabilities = ["chunk_text", "cosine_similarity", "estimate_tokens", "apply_template"]
    verbs = [
        VerbSpec(pattern="chunk text {t:expr} with size {s:expr} overlap {o:expr} into {target:ident}", description="Split text into overlapping chunks"),
        VerbSpec(pattern="calculate cosine similarity between {v1:expr} and {v2:expr} into {target:ident}", description="Compute cosine similarity between two vectors")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("chunk text ") or s.startswith("calculate cosine similarity ") or s.startswith("estimate token count ") or s.startswith("apply prompt template ")

GENAI_DOMAIN = GenaiDomain()
get_domain_registry().register(GENAI_DOMAIN)

__all__ = [
    "GenaiDomain", "GENAI_DOMAIN", "GenaiRuntime",
    "genai_chunk_text", "genai_cosine_similarity", "genai_retrieve_top_k",
    "genai_estimate_tokens", "genai_apply_template"
]
