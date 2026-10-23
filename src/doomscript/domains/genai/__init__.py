from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.genai.runtime import (
    GenAIRuntime, GenAISemanticCache, PagedKVCacheManager,
    genai_chunk_text, genai_recursive_chunk, genai_cosine_similarity,
    genai_euclidean_distance, genai_dot_product, genai_l2_normalize,
    genai_retrieve_top_k, genai_estimate_tokens, genai_apply_template,
    genai_bm25_score, genai_reciprocal_rank_fusion, genai_softmax,
    genai_softmax_sample, genai_multi_head_attention, genai_grouped_query_attention,
    genai_apply_rope, genai_alibi_bias, genai_train_bpe, genai_encode_bpe,
    genai_decode_bpe, genai_sample_logits, genai_beam_search,
    genai_speculative_verification, genai_calculate_kv_cache_memory,
    genai_lora_forward, genai_quantize_int4, genai_detect_prompt_injection,
    genai_redact_pii, genai_rouge_l, genai_bleu_score, genai_perplexity
)
from doomscript.domains.genai.parser import GenaiDomainParser
from doomscript.domains.genai.exporter import GenaiASTExporter

class GenAIDomain(DomainContract):
    name = "genai"
    aliases = ["generative_ai", "llm", "embeddings"]
    description = "GenAI, LLMs & RAG: Vector search, chunking, BM25, RRF, prompt safety, ROUGE/BLEU, Attention, RoPE, BPE"
    parser = GenaiDomainParser()
    runtime = GenAIRuntime()
    exporter = GenaiASTExporter()
    capabilities = [
        "chunk_text", "recursive_chunk", "cosine_similarity", "retrieve_top_k",
        "estimate_tokens", "prompt_template", "bm25", "rrf", "prompt_injection",
        "rouge", "bleu", "multi_head_attention", "grouped_query_attention",
        "rope", "bpe", "speculative_decoding", "kv_cache", "lora", "semantic_cache"
    ]
    verbs = [
        VerbSpec(pattern="calculate cosine similarity between {v1:expr} and {v2:expr} into {target:ident}", description="Cosine similarity"),
        VerbSpec(pattern="fuse rankings for lists {lists:expr} into {target:ident}", description="RRF rank fusion"),
        VerbSpec(pattern="check prompt injection for text {text:expr} into {target:ident}", description="Prompt injection detection"),
        VerbSpec(pattern="redact pii in text {text:expr} into {target:ident}", description="PII redaction"),
        VerbSpec(pattern="calculate kv memory for layers {l:expr} heads {h:expr} dim {d:expr} seq {seq:expr} into {target:ident}", description="KV cache memory calculation"),
        VerbSpec(pattern="sample logits {logits:expr} with temperature {temp:expr} into {target:ident}", description="Logits sampling"),
        VerbSpec(pattern="retrieve top {k:expr} chunks from {chunks:expr} for query {query:expr} into {target:ident}", description="Vector retrieval"),
        VerbSpec(pattern="train bpe for corpus {corpus:expr} merges {n:expr} into {target:ident}", description="BPE training")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("chunk text ") or
            s.startswith("calculate cosine similarity ") or
            s.startswith("estimate token count ") or
            s.startswith("apply prompt template ") or
            s.startswith("fuse rankings ") or
            s.startswith("check prompt injection ") or
            s.startswith("calculate rouge score ") or
            s.startswith("calculate bleu score ") or
            s.startswith("redact pii ") or
            s.startswith("calculate kv memory ") or
            s.startswith("sample logits ") or
            s.startswith("retrieve top ") or
            s.startswith("train bpe ")
        )

GENAI_DOMAIN = GenAIDomain()
get_domain_registry().register(GENAI_DOMAIN)

__all__ = [
    "GenAIDomain", "GENAI_DOMAIN", "GenAIRuntime", "GenAISemanticCache", "PagedKVCacheManager",
    "genai_chunk_text", "genai_recursive_chunk", "genai_cosine_similarity",
    "genai_euclidean_distance", "genai_dot_product", "genai_l2_normalize",
    "genai_retrieve_top_k", "genai_estimate_tokens", "genai_apply_template",
    "genai_bm25_score", "genai_reciprocal_rank_fusion", "genai_softmax",
    "genai_softmax_sample", "genai_multi_head_attention", "genai_grouped_query_attention",
    "genai_apply_rope", "genai_alibi_bias", "genai_train_bpe", "genai_encode_bpe",
    "genai_decode_bpe", "genai_sample_logits", "genai_beam_search",
    "genai_speculative_verification", "genai_calculate_kv_cache_memory",
    "genai_lora_forward", "genai_quantize_int4", "genai_detect_prompt_injection",
    "genai_redact_pii", "genai_rouge_l", "genai_bleu_score", "genai_perplexity"
]
