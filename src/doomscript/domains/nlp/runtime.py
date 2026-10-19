"""Runtime execution engine for NLP & Text Analytics domain."""

import math
import re
from typing import Any, Dict, List, Optional, Tuple, Set
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.nlp.spec import (
    NLPCleanSpec,
    NLPTokenizeSpec,
    NLPNgramSpec,
    NLPSentimentSpec,
    NLPTfidfSpec,
    NLPEntitiesSpec,
)

ENGLISH_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
    "by", "can", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for",
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just",
    "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once",
    "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she",
    "should", "so", "some", "such", "t", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which",
    "while", "who", "whom", "why", "will", "with", "you", "your", "yours", "yourself",
}

POSITIVE_WORDS: Set[str] = {
    "good", "great", "excellent", "amazing", "wonderful", "fantastic", "positive",
    "awesome", "superb", "brilliant", "love", "loved", "loving", "best", "happy",
    "pleased", "helpful", "fast", "efficient", "clean", "reliable", "beautiful",
    "smooth", "perfect", "enjoy", "enjoyed", "superior", "success", "successful",
    "impressive", "intuitive", "delight", "delightful", "terrific", "outstanding",
    "elegant",
}

NEGATIVE_WORDS: Set[str] = {
    "bad", "terrible", "horrible", "worst", "awful", "negative", "hate", "hated",
    "poor", "sad", "fail", "failed", "failing", "failure", "broken", "useless",
    "difficult", "error", "errors", "bug", "bugs", "slow", "ugly", "nasty",
    "unpleasant", "wrong", "flaw", "flawed", "crash", "crashed", "inferior",
    "frustrating", "annoying", "disaster", "disappointing",
}

NEGATION_WORDS: Set[str] = {
    "not", "never", "no", "hardly", "barely", "scarcely", "isn't", "aren't",
    "wasn't", "weren't", "don't", "doesn't", "didn't", "won't", "wouldn't",
    "can't", "cannot", "without",
}


def clean_text(text: str, remove_stopwords: bool = False) -> str:
    """Normalizes text by lowercasing, stripping punctuation, and optionally removing stop words."""
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    # Lowercase
    t = text.lower()
    # Replace non-alphanumeric (except spaces) with space
    t = re.sub(r"[^\w\s]", " ", t)
    # Collapse multiple whitespaces
    tokens = t.strip().split()
    if remove_stopwords:
        tokens = [tok for tok in tokens if tok not in ENGLISH_STOPWORDS]
    return " ".join(tokens)


def tokenize_text(text: str, mode: str = "word") -> List[str]:
    """Tokenizes text into a list of words or sentences."""
    if not isinstance(text, str):
        text = str(text) if text is not None else ""

    if mode == "sentence":
        # Split on sentence ending punctuation followed by space or end of string
        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        return [p.strip() for p in parts if p.strip()]

    # Default: word tokens preserving word boundaries
    return re.findall(r"\b\w+\b", text)


def extract_ngrams(text_or_tokens: Any, n: int = 2) -> List[str]:
    """Extracts contiguous sequences of n tokens from text or a token list."""
    if isinstance(text_or_tokens, str):
        tokens = tokenize_text(text_or_tokens)
    elif isinstance(text_or_tokens, list):
        tokens = [str(t) for t in text_or_tokens]
    else:
        tokens = tokenize_text(str(text_or_tokens))

    if len(tokens) < n or n <= 0:
        return []

    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Computes polarity score, compound score, and label based on lexicon with negation handling."""
    tokens = tokenize_text(text.lower())
    pos_count = 0
    neg_count = 0
    score = 0.0

    negated = False
    negation_window = 0

    for tok in tokens:
        if tok in NEGATION_WORDS:
            negated = True
            negation_window = 3
            continue

        is_pos = tok in POSITIVE_WORDS
        is_neg = tok in NEGATIVE_WORDS

        if is_pos:
            if negated:
                neg_count += 1
                score -= 1.0
            else:
                pos_count += 1
                score += 1.0
        elif is_neg:
            if negated:
                pos_count += 1
                score += 0.5
            else:
                neg_count += 1
                score -= 1.0

        if negation_window > 0:
            negation_window -= 1
            if negation_window == 0:
                negated = False

    total_sentiment_words = pos_count + neg_count
    if total_sentiment_words > 0:
        polarity = round(score / total_sentiment_words, 4)
    else:
        polarity = 0.0

    compound = round(score / (math.sqrt(score * score + 15)), 4) if score != 0 else 0.0

    if polarity > 0.05:
        label = "positive"
    elif polarity < -0.05:
        label = "negative"
    else:
        label = "neutral"

    return {
        "polarity": polarity,
        "compound": compound,
        "label": label,
        "positive_count": pos_count,
        "negative_count": neg_count,
    }


def calculate_tfidf(documents: List[str], max_features: Optional[int] = None) -> Dict[str, Any]:
    """Calculates TF-IDF vector matrix and vocabulary for a list of text documents."""
    if not isinstance(documents, list) or not documents:
        return {"vocabulary": [], "matrix": [], "feature_names": []}

    tokenized_docs = [tokenize_text(doc.lower()) for doc in documents]
    n_docs = len(tokenized_docs)

    # Document frequency
    doc_freq: Dict[str, int] = {}
    for doc in tokenized_docs:
        seen = set(doc)
        for term in seen:
            doc_freq[term] = doc_freq.get(term, 0) + 1

    # Sort terms by document frequency and term name
    sorted_terms = sorted(doc_freq.keys(), key=lambda t: (-doc_freq[t], t))
    if max_features and max_features > 0:
        sorted_terms = sorted_terms[:max_features]

    vocab = {term: idx for idx, term in enumerate(sorted(sorted_terms))}
    feature_names = sorted(vocab.keys())

    # Smooth IDF: ln((1 + N) / (1 + df)) + 1
    idf = {term: math.log((1.0 + n_docs) / (1.0 + doc_freq[term])) + 1.0 for term in feature_names}

    matrix: List[List[float]] = []
    for doc in tokenized_docs:
        doc_len = max(len(doc), 1)
        term_counts: Dict[str, int] = {}
        for t in doc:
            if t in vocab:
                term_counts[t] = term_counts.get(t, 0) + 1

        row = []
        for term in feature_names:
            tf = term_counts.get(term, 0) / doc_len
            tfidf_val = tf * idf[term]
            row.append(tfidf_val)

        # L2 normalize
        norm = math.sqrt(sum(v * v for v in row))
        if norm > 0:
            row = [round(v / norm, 4) for v in row]
        else:
            row = [0.0 for _ in row]
        matrix.append(row)

    return {
        "vocabulary": feature_names,
        "matrix": matrix,
        "feature_names": feature_names,
    }


def extract_entities(text: str) -> List[Dict[str, str]]:
    """Extracts structured entities (emails, URLs, dates, numbers, capitalized names) via regex."""
    if not isinstance(text, str):
        text = str(text) if text is not None else ""

    entities: List[Dict[str, str]] = []

    # Emails
    for m in re.finditer(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text):
        entities.append({"entity": m.group(0), "label": "EMAIL", "start": m.start(), "end": m.end()})

    # URLs
    for m in re.finditer(r"https?://[^\s/$.?#].[^\s]*", text):
        entities.append({"entity": m.group(0), "label": "URL", "start": m.start(), "end": m.end()})

    # Dates (YYYY-MM-DD, MM/DD/YYYY, DD-MM-YYYY)
    for m in re.finditer(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b", text):
        entities.append({"entity": m.group(0), "label": "DATE", "start": m.start(), "end": m.end()})

    # Numbers
    for m in re.finditer(r"\b\d+(?:\.\d+)?\b", text):
        # Don't duplicate if part of date
        span = (m.start(), m.end())
        if not any(e["label"] == "DATE" and e["start"] <= span[0] and span[1] <= e["end"] for e in entities):
            entities.append({"entity": m.group(0), "label": "NUMBER", "start": m.start(), "end": m.end()})

    # Proper nouns / Capitalized terms (2+ words capitalized or single proper nouns)
    for m in re.finditer(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text):
        val = m.group(0)
        # Avoid overriding email/url parts
        span = (m.start(), m.end())
        if not any(e["start"] <= span[0] and span[1] <= e["end"] for e in entities):
            entities.append({"entity": val, "label": "PROPER_NOUN", "start": m.start(), "end": m.end()})

    return entities


class NLPRuntime(DomainRuntime):
    """Runtime engine for NLP & Text Analytics domain."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        if isinstance(ir, NLPCleanSpec):
            text_val = scope.get(ir.text_expr, ir.text_expr)
            res = clean_text(str(text_val), remove_stopwords=ir.remove_stopwords)
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        elif isinstance(ir, NLPTokenizeSpec):
            text_val = scope.get(ir.text_expr, ir.text_expr)
            res = tokenize_text(str(text_val), mode=ir.mode)
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        elif isinstance(ir, NLPNgramSpec):
            text_val = scope.get(ir.text_expr, ir.text_expr)
            res = extract_ngrams(text_val, n=ir.n)
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        elif isinstance(ir, NLPSentimentSpec):
            text_val = scope.get(ir.text_expr, ir.text_expr)
            res = analyze_sentiment(str(text_val))
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        elif isinstance(ir, NLPTfidfSpec):
            corpus_val = scope.get(ir.corpus_var, ir.corpus_var)
            if not isinstance(corpus_val, list):
                corpus_val = [str(corpus_val)]
            res = calculate_tfidf(corpus_val, max_features=ir.max_features)
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        elif isinstance(ir, NLPEntitiesSpec):
            text_val = scope.get(ir.text_expr, ir.text_expr)
            res = extract_entities(str(text_val))
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        raise TypeError(f"Unknown NLP IR: {type(ir).__name__}")
