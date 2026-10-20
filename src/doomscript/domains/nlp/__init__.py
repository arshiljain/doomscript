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
    BPETokenizer,
    HMMPOSTagger,
    Word2VecSimple,
    TextRankSummarizer,
    BytePairEncoder,
    Word2VecCBOW,
    nlp_bpe_train,
    nlp_hmm_pos_tagger,
    nlp_cbow_word2vec,
    LevenshteinAutomatonFuzzyMatcher,
    nlp_textrank_summarize,
    nlp_fuzzy_match,
    nlp_fuzzy_search_text,
    BM25OkapiInformationRetrieval,
    CYKProbabilisticContextFreeGrammarPCFG,
    nlp_bm25_search,
    nlp_pcfg_parse,
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
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
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
            or s.startswith("extractive summary of ")
            or s.startswith("remove stopwords from ")
            or s.startswith("word frequencies of ")
            or s.startswith("text similarity between ")
            or s.startswith("jaccard similarity of ")
            or s.startswith("extract all matches of pattern ")
            or s.startswith("rank corpus ")
            or s.startswith("bm25 score for ")
            or s.startswith("levenshtein distance between ")
            or s.startswith("hamming distance between ")
            or s.startswith("porter stem of ")
            or s.startswith("soundex ")
            or s.startswith("metaphone ")
            or s.startswith("rouge-l score between ")
            or s.startswith("rouge l score between ")
            or s.startswith("bleu score between ")
            or s.startswith("term frequency cosine similarity between ")
            or s.startswith("tf cosine similarity between ")
            or s.startswith("expand contractions in ")
            or s.startswith("mask sensitive entities in ")
            or s.startswith("flesch reading ease of ")
            or s.startswith("gunning fog index of ")
            or s.startswith("count syllables in ")
            or (s.startswith("split ") and " into sentences" in s)
            or s.startswith("tag parts of speech in ")
            or s.startswith("pos tag ")
            or s.startswith("heuristic sentiment score for ")
            or s.startswith("vader sentiment of ")
            or (s.startswith("extract ") and "-character ngrams from " in s)
            or s.startswith("character ngrams from ")
            or s.startswith("find collocations in ")
            or s.startswith("collocations in ")
            or s.startswith("wrap text ")
            or s.startswith("word wrap ")
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
    "nlp_bm25_score",
    "nlp_levenshtein_distance",
    "nlp_hamming_distance",
    "nlp_stem_porter",
    "nlp_soundex",
    "nlp_metaphone",
    "nlp_rouge_l",
    "nlp_bleu_score",
    "nlp_cosine_similarity_tf",
    "nlp_expand_contractions",
    "nlp_mask_sensitive_entities",
    "nlp_readability_flesch",
    "nlp_readability_gunning_fog",
    "nlp_syllable_count",
    "nlp_sentence_split",
    "nlp_pos_tag_rule_based",
    "nlp_sentiment_vader_heuristic",
    "nlp_character_ngrams",
    "nlp_collocations",
    "nlp_word_wrap",
    "BPETokenizer",
    "HMMPOSTagger",
    "Word2VecSimple",
    "TextRankSummarizer",
    "KneserNeyLanguageModel",
    "nlp_kneser_ney",
    "BytePairEncoder",
    "Word2VecCBOW",
    "nlp_bpe_train",
    "nlp_hmm_pos_tagger",
    "nlp_cbow_word2vec",
    "LevenshteinAutomatonFuzzyMatcher",
    "nlp_textrank_summarize",
    "nlp_fuzzy_match",
    "nlp_fuzzy_search_text",
    "BM25OkapiInformationRetrieval",
    "CYKProbabilisticContextFreeGrammarPCFG",
    "nlp_bm25_search",
    "nlp_pcfg_parse",
]

