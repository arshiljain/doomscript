"""NLP & Text Analytics Domain Specification and Intermediate Representation (IR)."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainIR


@dataclass
class NLPCleanSpec(DomainIR):
    """Specification for text cleaning and normalization."""

    text_expr: str
    remove_stopwords: bool = False
    target_var: str = "clean_text"

    def validate(self) -> List[str]:
        errors = []
        if not self.text_expr:
            errors.append("Text expression cannot be empty")
        return errors


@dataclass
class NLPTokenizeSpec(DomainIR):
    """Specification for tokenizing text by words or sentences."""

    text_expr: str
    mode: str = "word"  # "word" or "sentence"
    target_var: str = "tokens"

    def validate(self) -> List[str]:
        errors = []
        if not self.text_expr:
            errors.append("Text expression cannot be empty")
        if self.mode not in ("word", "sentence"):
            errors.append(f"Invalid tokenize mode '{self.mode}', must be 'word' or 'sentence'")
        return errors


@dataclass
class NLPNgramSpec(DomainIR):
    """Specification for n-gram extraction from text or token sequences."""

    text_expr: str
    n: int = 2
    target_var: str = "ngrams"

    def validate(self) -> List[str]:
        errors = []
        if not self.text_expr:
            errors.append("Text expression cannot be empty")
        if self.n <= 0:
            errors.append(f"N-gram degree must be > 0, got {self.n}")
        return errors


@dataclass
class NLPSentimentSpec(DomainIR):
    """Specification for lexicon-driven sentiment analysis."""

    text_expr: str
    target_var: str = "sentiment"

    def validate(self) -> List[str]:
        errors = []
        if not self.text_expr:
            errors.append("Text expression cannot be empty")
        return errors


@dataclass
class NLPTfidfSpec(DomainIR):
    """Specification for TF-IDF matrix generation across a corpus of documents."""

    corpus_var: str
    max_features: Optional[int] = None
    ngram_range: Tuple[int, int] = (1, 1)
    target_var: str = "tfidf_matrix"

    def validate(self) -> List[str]:
        errors = []
        if not self.corpus_var:
            errors.append("Corpus variable cannot be empty")
        if self.max_features is not None and self.max_features <= 0:
            errors.append(f"max_features must be > 0, got {self.max_features}")
        return errors


@dataclass
class NLPEntitiesSpec(DomainIR):
    """Specification for Named Entity and structured token extraction."""

    text_expr: str
    target_var: str = "entities"

    def validate(self) -> List[str]:
        errors = []
        if not self.text_expr:
            errors.append("Text expression cannot be empty")
        return errors
