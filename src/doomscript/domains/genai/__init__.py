from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.genai.runtime import (
    genai_chunk_text, genai_cosine_similarity, genai_retrieve_top_k,
    genai_estimate_tokens, genai_apply_template, genai_bm25_score,
    genai_reciprocal_rank_fusion, genai_softmax_sample,
    genai_detect_prompt_injection, genai_rouge_l, genai_bleu_score
)
from doomscript.domains.genai.parser import GenaiDomainParser
from doomscript.domains.genai.exporter import GenaiASTExporter

class GenAIRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class GenAIDomain(DomainContract):
    name = "genai"
    aliases = ["generative_ai", "llm", "embeddings"]
    description = "GenAI, LLMs & RAG: Vector search, chunking, BM25, RRF, prompt safety, ROUGE/BLEU"
    parser = GenaiDomainParser()
    runtime = GenAIRuntime()
    exporter = GenaiASTExporter()
    capabilities = ["chunk_text", "cosine_similarity", "retrieve_top_k", "estimate_tokens", "prompt_template", "bm25", "rrf", "prompt_injection", "rouge", "bleu"]
    verbs = [
        VerbSpec(pattern="calculate cosine similarity between {v1:expr} and {v2:expr} into {target:ident}", description="Cosine similarity"),
        VerbSpec(pattern="fuse rankings for lists {lists:expr} into {target:ident}", description="RRF rank fusion"),
        VerbSpec(pattern="check prompt injection for text {text:expr} into {target:ident}", description="Prompt injection detection")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("chunk text ") or s.startswith("calculate cosine similarity ") or s.startswith("estimate token count ") or s.startswith("apply prompt template ") or s.startswith("fuse rankings ") or s.startswith("check prompt injection ") or s.startswith("calculate rouge score ") or s.startswith("calculate bleu score ")

GENAI_DOMAIN = GenAIDomain()
get_domain_registry().register(GENAI_DOMAIN)

__all__ = [
    "GenAIDomain", "GENAI_DOMAIN", "GenAIRuntime",
    "genai_chunk_text", "genai_cosine_similarity", "genai_retrieve_top_k",
    "genai_estimate_tokens", "genai_apply_template", "genai_bm25_score",
    "genai_reciprocal_rank_fusion", "genai_softmax_sample",
    "genai_detect_prompt_injection", "genai_rouge_l", "genai_bleu_score"
]
