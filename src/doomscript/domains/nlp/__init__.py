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
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.nlp.exporter import NLPASTExporter
from doomscript.domains.registry import get_domain_registry


class NLPDomain(DomainContract):
    """Natural Language Processing & Text Analytics domain pack."""

    name = "nlp"
    aliases = ["text", "text_analytics"]
    description = "Natural Language Processing, tokenization, sentiment analysis, TF-IDF, named entity recognition"
    parser = NLPDomainParser()
    runtime = NLPRuntime()
    exporter = NLPASTExporter()
    capabilities = ["tokenization", "sentiment", "tfidf", "entities", "cleaning"]
    optional_dependencies = ["nltk", "spacy"]

    verbs = [
        VerbSpec(
            name="clean_text",
            pattern="clean [text] {text_expr:expr} into {target:ident}",
            arg_schema={"text_expr": "expr", "target": "ident"},
            returns="str",
            description="Normalize case, remove punctuation, and strip whitespace",
        ),
        VerbSpec(
            name="tokenize",
            pattern="tokenize {text_expr:expr} into {target:ident}",
            arg_schema={"text_expr": "expr", "target": "ident"},
            returns="Collection",
            description="Tokenize string into list of word tokens",
        ),
        VerbSpec(
            name="ngrams",
            pattern="(bigrams|trigrams) of {text_expr:expr} into {target:ident}",
            arg_schema={"text_expr": "expr", "target": "ident"},
            returns="Collection",
            description="Extract consecutive N-gram word tuples",
        ),
        VerbSpec(
            name="sentiment",
            pattern="[analyze] sentiment of {text_expr:expr} into {target:ident}",
            arg_schema={"text_expr": "expr", "target": "ident"},
            returns="Record",
            description="Compute polarity score and sentiment label",
        ),
        VerbSpec(
            name="tfidf",
            pattern="[calculate] tfidf of {corpus_expr:expr} into {target:ident}",
            arg_schema={"corpus_expr": "expr", "target": "ident"},
            returns="Table",
            description="Compute Term Frequency - Inverse Document Frequency matrix",
        ),
        VerbSpec(
            name="entities",
            pattern="entities in {text_expr:expr} into {target:ident}",
            arg_schema={"text_expr": "expr", "target": "ident"},
            returns="Collection",
            description="Extract named entities (people, places, dates)",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("clean ")
            or s.startswith("clean text ")
            or s.startswith("tokenize ")
            or s.startswith("extract ")
            or s.startswith("analyze sentiment ")
            or s.startswith("sentiment of ")
            or s.startswith("words in ")
            or s.startswith("sentences in ")
            or s.startswith("bigrams of ")
            or s.startswith("trigrams of ")
            or s.startswith("entities in ")
            or s.startswith("calculate tfidf ")
            or s.startswith("tfidf of ")
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
