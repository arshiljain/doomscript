"""NLP & Text Analytics Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.nlp.spec import (
    NLPCleanSpec,
    NLPTokenizeSpec,
    NLPNgramSpec,
    NLPSentimentSpec,
    NLPTfidfSpec,
    NLPEntitiesSpec,
)
from doomscript.domains.nlp.parser import NLPDomainParser
from doomscript.domains.nlp.runtime import (
    NLPRuntime,
    clean_text,
    tokenize_text,
    extract_ngrams,
    analyze_sentiment,
    calculate_tfidf,
    extract_entities,
)
from doomscript.domains.nlp.exporter import NLPASTExporter
from doomscript.domains.registry import get_domain_registry


class NLPDomain(DomainContract):
    """Natural Language Processing & Text Analytics domain pack."""

    name = "nlp"
    aliases = ["text", "text_analytics"]
    parser = NLPDomainParser()
    runtime = NLPRuntime()
    exporter = NLPASTExporter()

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("clean ")
            or s.startswith("clean text ")
            or s.startswith("tokenize ")
            or s.startswith("extract ")
            or s.startswith("analyze sentiment ")
            or s.startswith("calculate tfidf ")
        )

    def can_handle_block(self, header: str) -> bool:
        s = header.strip().lower()
        return s.startswith("tfidf ") and (":" in s)


# Register with central registry
NLP_DOMAIN = NLPDomain()
get_domain_registry().register(NLP_DOMAIN)

__all__ = [
    "NLPDomain",
    "NLP_DOMAIN",
    "NLPCleanSpec",
    "NLPTokenizeSpec",
    "NLPNgramSpec",
    "NLPSentimentSpec",
    "NLPTfidfSpec",
    "NLPEntitiesSpec",
    "NLPDomainParser",
    "NLPRuntime",
    "NLPASTExporter",
    "clean_text",
    "tokenize_text",
    "extract_ngrams",
    "analyze_sentiment",
    "calculate_tfidf",
    "extract_entities",
]
