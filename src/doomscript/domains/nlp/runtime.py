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


# --- Batch 5 Spoken English NLP Verbs ---

def nlp_extractive_summary(text: Any, num_sentences: Any = 2) -> str:
    """Extractive sentence scoring summary preserving chronological order."""
    t = str(text).strip()
    n = int(num_sentences)
    sentences = tokenize_text(t, mode="sentence")
    if len(sentences) <= n:
        return t

    # Compute word frequencies across document
    words = [w.lower() for w in tokenize_text(t, mode="word") if w.lower() not in ENGLISH_STOPWORDS]
    freqs: Dict[str, int] = {}
    for w in words:
        freqs[w] = freqs.get(w, 0) + 1

    # Score each sentence
    scored = []
    for i, s in enumerate(sentences):
        s_words = [w.lower() for w in tokenize_text(s, mode="word") if w.lower() not in ENGLISH_STOPWORDS]
        score = sum(freqs.get(w, 0) for w in s_words)
        scored.append((score, i, s))

    # Pick top n by score, then sort back by original index
    top = sorted(sorted(scored, key=lambda x: x[0], reverse=True)[:n], key=lambda x: x[1])
    return " ".join(item[2] for item in top)


def nlp_remove_stopwords(text: Any) -> str:
    """Strip standard English stopwords from text."""
    return clean_text(str(text), remove_stopwords=True)


def nlp_word_frequencies(text: Any) -> Dict[str, int]:
    """Calculate token frequency distribution sorted descending."""
    words = [w.lower() for w in tokenize_text(str(text), mode="word")]
    freqs: Dict[str, int] = {}
    for w in words:
        freqs[w] = freqs.get(w, 0) + 1
    return dict(sorted(freqs.items(), key=lambda kv: kv[1], reverse=True))


def nlp_text_similarity(s1: Any, s2: Any) -> float:
    """Cosine similarity of bag-of-words vectors between two texts."""
    v1_words = [w.lower() for w in tokenize_text(str(s1), mode="word")]
    v2_words = [w.lower() for w in tokenize_text(str(s2), mode="word")]
    if not v1_words or not v2_words:
        return 0.0

    all_vocab = list(set(v1_words + v2_words))
    f1 = {w: v1_words.count(w) for w in all_vocab}
    f2 = {w: v2_words.count(w) for w in all_vocab}

    dot = sum(f1[w] * f2[w] for w in all_vocab)
    norm1 = math.sqrt(sum(f1[w] ** 2 for w in all_vocab))
    norm2 = math.sqrt(sum(f2[w] ** 2 for w in all_vocab))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return round(dot / (norm1 * norm2), 4)


def nlp_jaccard_similarity(s1: Any, s2: Any) -> float:
    """Jaccard set similarity between two texts."""
    set1 = set(w.lower() for w in tokenize_text(str(s1), mode="word"))
    set2 = set(w.lower() for w in tokenize_text(str(s2), mode="word"))
    if not set1 and not set2:
        return 1.0
    union = set1 | set2
    if not union:
        return 0.0
    return round(len(set1 & set2) / len(union), 4)


def nlp_extract_keywords(text: Any, k: Any = 5) -> List[str]:
    """Extract top k salient non-stopword tokens by frequency."""
    k_int = int(k)
    words = [w.lower() for w in tokenize_text(str(text), mode="word") if w.lower() not in ENGLISH_STOPWORDS and len(w) > 2]
    freqs: Dict[str, int] = {}
    for w in words:
        freqs[w] = freqs.get(w, 0) + 1
    sorted_words = [w for w, _ in sorted(freqs.items(), key=lambda kv: kv[1], reverse=True)]
    return sorted_words[:k_int]


def nlp_extract_matches(text: Any, pattern: Any) -> List[str]:
    """Find all regex pattern matches in text."""
    pat_str = str(pattern).strip("'\"")
    return re.findall(pat_str, str(text))


# 350-Expansion NLP Operations

def nlp_bm25_score(corpus: Any, query: Any, k1: Any = 1.5, b: Any = 0.75) -> List[Dict[str, Any]]:
    """Rank corpus documents against query using BM25 scoring."""
    docs = [str(d) for d in corpus] if isinstance(corpus, (list, tuple)) else [str(corpus)]
    q_words = [w.lower() for w in tokenize_text(str(query), mode="word")]
    n_docs = len(docs)
    if n_docs == 0:
        return []
    doc_words = [[w.lower() for w in tokenize_text(d, mode="word")] for d in docs]
    avgdl = sum(len(dw) for dw in doc_words) / n_docs or 1.0
    k1_val = float(k1)
    b_val = float(b)
    idf: Dict[str, float] = {}
    for q in q_words:
        n_q = sum(1 for dw in doc_words if q in dw)
        idf[q] = math.log(((n_docs - n_q + 0.5) / (n_q + 0.5)) + 1.0)
    scores = []
    for idx, dw in enumerate(doc_words):
        dl = len(dw)
        score = 0.0
        counts: Dict[str, int] = {}
        for w in dw:
            counts[w] = counts.get(w, 0) + 1
        for q in q_words:
            f = counts.get(q, 0)
            if f > 0:
                num = f * (k1_val + 1.0)
                denom = f + k1_val * (1.0 - b_val + b_val * (dl / avgdl))
                score += idf[q] * (num / denom)
        scores.append({"index": idx, "doc": docs[idx], "score": round(score, 4)})
    return sorted(scores, key=lambda x: x["score"], reverse=True)


def nlp_levenshtein_distance(s1: Any, s2: Any) -> int:
    """Calculate minimum Levenshtein edit distance."""
    str1, str2 = str(s1), str(s2)
    m, n = len(str1), len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]


def nlp_hamming_distance(s1: Any, s2: Any) -> int:
    """Calculate Hamming distance between two strings."""
    str1, str2 = str(s1), str(s2)
    dist = sum(1 for c1, c2 in zip(str1, str2) if c1 != c2)
    dist += abs(len(str1) - len(str2))
    return dist


def nlp_stem_porter(word: Any) -> str:
    """Lightweight rule-based word stemmer."""
    w = str(word).lower().strip()
    if len(w) <= 3:
        return w
    for suffix in ("sses", "ies", "ss", "s"):
        if w.endswith(suffix):
            w = w[:-len(suffix)] + ("ss" if suffix == "sses" else "i" if suffix == "ies" else "ss" if suffix == "ss" else "")
            break
    for suffix in ("eed", "ing", "ed"):
        if w.endswith(suffix):
            base = w[:-len(suffix)]
            if any(c in "aeiouy" for c in base):
                w = base
                if w.endswith(("at", "bl", "iz")):
                    w += "e"
                elif len(w) >= 2 and w[-1] == w[-2] and w[-1] not in ("l", "s", "z"):
                    w = w[:-1]
            break
    for suffix in ("fully", "ness", "ment", "ly"):
        if w.endswith(suffix):
            w = w[:-len(suffix)]
            break
    return w


def nlp_soundex(word: Any) -> str:
    """Compute American Soundex phonetic algorithm code."""
    w = re.sub(r"[^A-Za-z]", "", str(word)).upper()
    if not w:
        return "0000"
    mapping = {
        "B": "1", "F": "1", "P": "1", "V": "1",
        "C": "2", "G": "2", "J": "2", "K": "2", "Q": "2", "S": "2", "X": "2", "Z": "2",
        "D": "3", "T": "3",
        "L": "4",
        "M": "5", "N": "5",
        "R": "6",
    }
    first_letter = w[0]
    encoded = [first_letter]
    last_code = mapping.get(first_letter, "")
    for char in w[1:]:
        code = mapping.get(char, "")
        if code and code != last_code:
            encoded.append(code)
            last_code = code
        elif char not in ("H", "W"):
            last_code = ""
    res = "".join(encoded).replace("0", "")
    return (res + "0000")[:4]


def nlp_metaphone(word: Any) -> str:
    """Simplified Metaphone phonetic representation."""
    w = re.sub(r"[^A-Za-z]", "", str(word)).upper()
    if not w:
        return ""
    if w.startswith(("KN", "GN", "PN", "WR")):
        w = w[1:]
    elif w.startswith("WH"):
        w = "W" + w[2:]
    elif w.startswith("X"):
        w = "S" + w[1:]
    w = re.sub(r"PH", "F", w)
    w = re.sub(r"CK", "K", w)
    w = re.sub(r"SH", "X", w)
    w = re.sub(r"CH", "X", w)
    w = re.sub(r"TH", "0", w)
    w = re.sub(r"C(?=[EIY])", "S", w)
    w = re.sub(r"C", "K", w)
    w = re.sub(r"Q", "K", w)
    w = re.sub(r"(.)\1+", r"\1", w)
    first = w[0]
    rest = re.sub(r"[AEIOUY]", "", w[1:])
    return (first if first in "AEIOU" else "") + (first if first not in "AEIOU" else "") + rest


def nlp_rouge_l(candidate: Any, reference: Any) -> Dict[str, float]:
    """Compute ROUGE-L Longest Common Subsequence metrics."""
    c_words = [w.lower() for w in tokenize_text(str(candidate), mode="word")]
    r_words = [w.lower() for w in tokenize_text(str(reference), mode="word")]
    m, n = len(c_words), len(r_words)
    if m == 0 or n == 0:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if c_words[i - 1] == r_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    lcs_len = dp[m][n]
    p = lcs_len / m
    r = lcs_len / n
    f1 = (2.0 * p * r) / (p + r) if (p + r) > 0 else 0.0
    return {"precision": round(p, 4), "recall": round(r, 4), "f1": round(f1, 4)}


def nlp_bleu_score(candidate: Any, reference: Any, max_n: Any = 4) -> float:
    """Compute sentence BLEU score."""
    c_words = [w.lower() for w in tokenize_text(str(candidate), mode="word")]
    r_words = [w.lower() for w in tokenize_text(str(reference), mode="word")]
    c_len, r_len = len(c_words), len(r_words)
    if c_len == 0 or r_len == 0:
        return 0.0
    bp = 1.0 if c_len > r_len else math.exp(1.0 - float(r_len) / c_len)
    precisions = []
    n_limit = min(int(max_n), c_len)
    for n in range(1, n_limit + 1):
        c_ngrams = [tuple(c_words[i:i + n]) for i in range(c_len - n + 1)]
        r_ngrams = [tuple(r_words[i:i + n]) for i in range(r_len - n + 1)]
        r_counts: Dict[Tuple, int] = {}
        for g in r_ngrams:
            r_counts[g] = r_counts.get(g, 0) + 1
        matches = 0
        for g in c_ngrams:
            if r_counts.get(g, 0) > 0:
                matches += 1
                r_counts[g] -= 1
        p = matches / len(c_ngrams) if c_ngrams else 0.0
        precisions.append(max(p, 1e-6))
    geom_mean = math.exp(sum(math.log(p) for p in precisions) / len(precisions))
    return round(bp * geom_mean, 4)


def nlp_cosine_similarity_tf(text1: Any, text2: Any) -> float:
    """Cosine similarity of Term Frequency vectors."""
    return nlp_text_similarity(text1, text2)


def nlp_expand_contractions(text: Any) -> str:
    """Expand common English contractions."""
    t = str(text)
    contractions = {
        r"\bcan't\b": "cannot",
        r"\bwon't\b": "will not",
        r"\bdon't\b": "do not",
        r"\bdoesn't\b": "does not",
        r"\bdidn't\b": "did not",
        r"\bisn't\b": "is not",
        r"\baren't\b": "are not",
        r"\bwasn't\b": "was not",
        r"\bweren't\b": "were not",
        r"\bhaven't\b": "have not",
        r"\bhasn't\b": "has not",
        r"\bhadn't\b": "had not",
        r"\bit's\b": "it is",
        r"\bi'm\b": "i am",
        r"\byou're\b": "you are",
        r"\bthey're\b": "they are",
        r"\bwe're\b": "we are",
        r"\bthat's\b": "that is",
        r"\bwhat's\b": "what is",
    }
    for pat, rep in contractions.items():
        t = re.sub(pat, rep, t, flags=re.IGNORECASE)
    return t


def nlp_mask_sensitive_entities(text: Any, entity_types: Any = None) -> str:
    """Mask PII entities (email, phone, ssn)."""
    t = str(text)
    t = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[EMAIL]", t)
    t = re.sub(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE]", t)
    t = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]", t)
    return t


def nlp_syllable_count(word: Any) -> int:
    """Estimate syllable count in a single word."""
    w = str(word).lower().strip()
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]|ed|es|e)$", "", w)
    w = re.sub(r"^y", "", w)
    matches = re.findall(r"[aeiouy]{1,2}", w)
    return max(1, len(matches))


def nlp_readability_flesch(text: Any) -> float:
    """Compute Flesch Reading Ease score."""
    t = str(text)
    words = tokenize_text(t, mode="word")
    sents = tokenize_text(t, mode="sentence")
    if not words or not sents:
        return 100.0
    n_words = len(words)
    n_sents = len(sents)
    n_syllables = sum(nlp_syllable_count(w) for w in words)
    score = 206.835 - 1.015 * (n_words / n_sents) - 84.6 * (n_syllables / n_words)
    return round(score, 2)


def nlp_readability_gunning_fog(text: Any) -> float:
    """Compute Gunning Fog index."""
    t = str(text)
    words = tokenize_text(t, mode="word")
    sents = tokenize_text(t, mode="sentence")
    if not words or not sents:
        return 0.0
    n_words = len(words)
    n_sents = len(sents)
    complex_words = sum(1 for w in words if nlp_syllable_count(w) >= 3)
    fog = 0.4 * ((n_words / n_sents) + 100.0 * (complex_words / n_words))
    return round(fog, 2)


def nlp_sentence_split(text: Any) -> List[str]:
    """Split text into sentences."""
    return tokenize_text(str(text), mode="sentence")


def nlp_pos_tag_rule_based(tokens: Any) -> List[Tuple[str, str]]:
    """Heuristic rule-based POS tagger."""
    words = list(tokens) if isinstance(tokens, (list, tuple)) else tokenize_text(str(tokens), mode="word")
    tagged = []
    for w in words:
        wl = str(w).lower()
        if wl in ENGLISH_STOPWORDS:
            tag = "DET" if wl in ("the", "a", "an", "this", "that") else "PRON" if wl in ("he", "she", "it", "they", "i", "we") else "ADP" if wl in ("in", "on", "at", "by", "for", "with") else "CONJ"
        elif re.match(r"^\d+(?:\.\d+)?$", wl):
            tag = "NUM"
        elif wl.endswith(("ing", "ed", "ize", "ate")):
            tag = "VERB"
        elif wl.endswith(("ly",)):
            tag = "ADV"
        elif wl.endswith(("able", "ible", "ous", "ful", "ive", "al")):
            tag = "ADJ"
        else:
            tag = "NOUN"
        tagged.append((str(w), tag))
    return tagged


def nlp_sentiment_vader_heuristic(text: Any) -> Dict[str, float]:
    """Heuristic polarity analyzer with compound score."""
    return analyze_sentiment(str(text))


def nlp_character_ngrams(text: Any, n: Any = 3) -> List[str]:
    """Generate character-level n-grams from text."""
    s = str(text)
    n_val = int(n)
    if len(s) < n_val:
        return []
    return [s[i:i + n_val] for i in range(len(s) - n_val + 1)]


def nlp_collocations(tokens: Any, min_freq: Any = 2) -> List[Tuple[str, str]]:
    """Extract frequent bigram collocations."""
    words = list(tokens) if isinstance(tokens, (list, tuple)) else tokenize_text(str(tokens), mode="word")
    m_freq = int(min_freq)
    counts: Dict[Tuple[str, str], int] = {}
    for i in range(len(words) - 1):
        bg = (words[i].lower(), words[i + 1].lower())
        counts[bg] = counts.get(bg, 0) + 1
    return [bg for bg, c in sorted(counts.items(), key=lambda kv: kv[1], reverse=True) if c >= m_freq]


def nlp_word_wrap(text: Any, width: Any = 80) -> str:
    """Wrap text lines at whitespace boundary."""
    words = str(text).split()
    w_limit = int(width)
    lines, cur_line = [], []
    cur_len = 0
    for w in words:
        if cur_len + len(w) + (1 if cur_line else 0) <= w_limit:
            cur_line.append(w)
            cur_len += len(w) + (1 if cur_len > 0 else 0)
        else:
            if cur_line:
                lines.append(" ".join(cur_line))
            cur_line = [w]
            cur_len = len(w)
    if cur_line:
        lines.append(" ".join(cur_line))
    return "\n".join(lines)


# =========================================================================
# Deepened NLP Models: BPE Tokenizer, HMM Viterbi POS Tagger, Word2Vec, TextRank
# =========================================================================

class BPETokenizer:
    """Byte-Pair Encoding (BPE) subword tokenizer."""

    def __init__(self, vocab_size: int = 100):
        self.target_vocab_size = vocab_size
        self.merges: List[Tuple[str, str]] = []
        self.vocab: Set[str] = set()

    def train(self, corpus: List[str]) -> "BPETokenizer":
        # Form initial word frequencies with characters + '</w>'
        word_freqs: Dict[Tuple[str, ...], int] = {}
        for doc in corpus:
            words = re.findall(r"\b\w+\b", str(doc).lower())
            for w in words:
                chars = tuple(list(w) + ["</w>"])
                word_freqs[chars] = word_freqs.get(chars, 0) + 1

        self.vocab = set()
        for w_tuple in word_freqs:
            for ch in w_tuple:
                self.vocab.add(ch)

        self.merges = []

        while len(self.vocab) < self.target_vocab_size:
            # Count adjacent pairs
            pair_counts: Dict[Tuple[str, str], int] = {}
            for w_tuple, freq in word_freqs.items():
                for i in range(len(w_tuple) - 1):
                    pair = (w_tuple[i], w_tuple[i + 1])
                    pair_counts[pair] = pair_counts.get(pair, 0) + freq

            if not pair_counts:
                break

            best_pair = max(pair_counts.items(), key=lambda kv: kv[1])[0]
            if pair_counts[best_pair] < 1:
                break

            self.merges.append(best_pair)
            merged_token = best_pair[0] + best_pair[1]
            self.vocab.add(merged_token)

            # Apply merge across all words
            new_word_freqs = {}
            for w_tuple, freq in word_freqs.items():
                new_w = []
                i = 0
                while i < len(w_tuple):
                    if i < len(w_tuple) - 1 and (w_tuple[i], w_tuple[i + 1]) == best_pair:
                        new_w.append(merged_token)
                        i += 2
                    else:
                        new_w.append(w_tuple[i])
                        i += 1
                new_word_freqs[tuple(new_w)] = freq
            word_freqs = new_word_freqs

        return self

    def encode(self, text: str) -> List[str]:
        words = re.findall(r"\b\w+\b", str(text).lower())
        tokens = []
        for w in words:
            word_tokens = list(w) + ["</w>"]
            for pair in self.merges:
                merged = pair[0] + pair[1]
                new_tokens = []
                i = 0
                while i < len(word_tokens):
                    if i < len(word_tokens) - 1 and word_tokens[i] == pair[0] and word_tokens[i + 1] == pair[1]:
                        new_tokens.append(merged)
                        i += 2
                    else:
                        new_tokens.append(word_tokens[i])
                        i += 1
                word_tokens = new_tokens
            tokens.extend(word_tokens)
        return tokens

    def decode(self, tokens: List[str]) -> str:
        s = "".join(tokens)
        return s.replace("</w>", " ").strip()


class HMMPOSTagger:
    """Hidden Markov Model Part-of-Speech Tagger using Viterbi Trellis Decoding."""

    def __init__(self):
        self.tags: Set[str] = {"NOUN", "VERB", "ADJ", "ADV", "DET", "PRON", "PREP", "PUNCT"}
        self.transitions: Dict[str, Dict[str, float]] = {t: {t2: 1.0 for t2 in self.tags} for t in self.tags}
        self.emissions: Dict[str, Dict[str, float]] = {t: {} for t in self.tags}
        self.start_probs: Dict[str, float] = {
            "DET": 15.0,
            "PRON": 12.0,
            "NOUN": 10.0,
            "ADJ": 5.0,
            "VERB": 2.0,
            "ADV": 2.0,
            "PREP": 2.0,
            "PUNCT": 0.01,
        }
        self._init_defaults()

    def _init_defaults(self):
        # Seed realistic English linguistic heuristics
        heuristics = [
            ("DET", ["the", "a", "an", "this", "that", "these", "those", "every", "all"]),
            ("PRON", ["i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them"]),
            ("VERB", ["is", "are", "was", "were", "be", "have", "has", "had", "do", "does", "did", "say", "go", "make", "take", "run", "runs", "ran", "jump", "jumps", "jumped", "eats", "ate"]),
            ("NOUN", ["cat", "dog", "man", "woman", "person", "time", "year", "day", "way", "fox", "fence", "quick", "lazy", "food", "data", "model", "graph"]),
            ("ADJ", ["quick", "brown", "lazy", "good", "great", "fast", "slow", "smart", "big", "small", "happy", "new", "first", "last"]),
            ("ADV", ["quickly", "slowly", "very", "never", "always", "often", "well", "almost", "now", "then"]),
            ("PREP", ["in", "on", "at", "to", "for", "with", "from", "by", "about", "over", "under"]),
            ("PUNCT", [".", ",", "!", "?", ";", ":", "-", "(", ")", "\"", "'"]),
        ]
        for tag, words in heuristics:
            for w in words:
                self.emissions[tag][w] = 10.0

        # Seed realistic transition weights
        self.transitions["DET"]["NOUN"] = 10.0
        self.transitions["DET"]["ADJ"] = 8.0
        self.transitions["ADJ"]["NOUN"] = 10.0
        self.transitions["NOUN"]["VERB"] = 10.0
        self.transitions["PRON"]["VERB"] = 10.0
        self.transitions["VERB"]["NOUN"] = 8.0
        self.transitions["VERB"]["PREP"] = 8.0
        self.transitions["PREP"]["DET"] = 10.0
        self.transitions["PREP"]["NOUN"] = 8.0

    def train(self, tagged_sentences: List[List[Tuple[str, str]]]) -> "HMMPOSTagger":
        for sent in tagged_sentences:
            if not sent:
                continue
            prev_t = None
            for idx, (word, tag) in enumerate(sent):
                w = word.lower()
                self.tags.add(tag)
                if tag not in self.transitions:
                    self.transitions[tag] = {}
                if tag not in self.emissions:
                    self.emissions[tag] = {}

                self.emissions[tag][w] = self.emissions[tag].get(w, 0.0) + 1.0

                if idx == 0:
                    self.start_probs[tag] = self.start_probs.get(tag, 0.0) + 1.0
                if prev_t is not None:
                    if prev_t not in self.transitions:
                        self.transitions[prev_t] = {}
                    self.transitions[prev_t][tag] = self.transitions[prev_t].get(tag, 0.0) + 1.0
                prev_t = tag
        return self

    def tag(self, words: List[str]) -> List[Tuple[str, str]]:
        if not words:
            return []
        tokens = [str(w).lower() for w in words]
        n_words = len(tokens)
        tags_list = sorted(list(self.tags))

        all_vocab = {w for t in self.tags for w in self.emissions.get(t, {})}
        vocab_size = max(50, len(all_vocab))

        def get_emit_p(t: str, word: str) -> float:
            tag_em = self.emissions.get(t, {})
            tot = sum(tag_em.values()) + vocab_size
            c = tag_em.get(word, 1e-4)
            return math.log(c / tot)

        # Viterbi tables
        viterbi = [{t: -float("inf") for t in tags_list} for _ in range(n_words)]
        backpointer = [{t: None for t in tags_list} for _ in range(n_words)]

        total_starts = sum(self.start_probs.values()) or 1.0
        w0 = tokens[0]

        for t in tags_list:
            p_start = math.log((self.start_probs.get(t, 1.0)) / total_starts)
            viterbi[0][t] = p_start + get_emit_p(t, w0)

        # Forward trellis
        for i in range(1, n_words):
            wi = tokens[i]
            for t in tags_list:
                p_emit = get_emit_p(t, wi)
                best_prob = -float("inf")
                best_prev = None

                for prev_t in tags_list:
                    tot_trans = sum(self.transitions.get(prev_t, {}).values()) + len(tags_list)
                    t_count = self.transitions.get(prev_t, {}).get(t, 1.0)
                    p_trans = math.log(t_count / tot_trans)

                    candidate = viterbi[i - 1][prev_t] + p_trans + p_emit
                    if candidate > best_prob:
                        best_prob = candidate
                        best_prev = prev_t

                viterbi[i][t] = best_prob
                backpointer[i][t] = best_prev

        # Find best terminal tag
        best_last_tag = max(tags_list, key=lambda t: viterbi[-1][t])
        best_path = [best_last_tag]

        for i in range(n_words - 1, 0, -1):
            best_last_tag = backpointer[i][best_last_tag]
            best_path.append(best_last_tag)

        best_path.reverse()
        return list(zip(words, best_path))


class Word2VecSimple:
    """Pure-Python Skip-Gram Word Embeddings with Negative Sampling."""

    def __init__(self, embedding_dim: int = 16, lr: float = 0.05, epochs: int = 5):
        self.dim = embedding_dim
        self.lr = lr
        self.epochs = epochs
        self.word2id: Dict[str, int] = {}
        self.id2word: Dict[int, str] = {}
        self.W_in: List[List[float]] = []
        self.W_out: List[List[float]] = []

    def fit(self, corpus: List[str], window: int = 2, n_negatives: int = 3, seed: int = 42) -> "Word2VecSimple":
        import random
        rng = random.Random(seed)

        # Build vocabulary
        freqs: Dict[str, int] = {}
        tokenized_docs = []
        for doc in corpus:
            tokens = re.findall(r"\b\w+\b", str(doc).lower())
            tokenized_docs.append(tokens)
            for tok in tokens:
                freqs[tok] = freqs.get(tok, 0) + 1

        self.word2id = {w: i for i, w in enumerate(sorted(freqs.keys()))}
        self.id2word = {i: w for w, i in self.word2id.items()}
        vocab_size = len(self.word2id)
        if vocab_size == 0:
            return self

        # Initialize weights
        limit = 1.0 / math.sqrt(self.dim)
        self.W_in = [[rng.uniform(-limit, limit) for _ in range(self.dim)] for _ in range(vocab_size)]
        self.W_out = [[0.0 for _ in range(self.dim)] for _ in range(vocab_size)]

        # Training loop
        all_ids = list(range(vocab_size))
        for _ in range(self.epochs):
            for doc in tokenized_docs:
                for idx, word in enumerate(doc):
                    center_id = self.word2id[word]
                    start = max(0, idx - window)
                    end = min(len(doc), idx + window + 1)
                    context_words = [doc[j] for j in range(start, end) if j != idx]

                    for ctx_w in context_words:
                        ctx_id = self.word2id[ctx_w]
                        # Target pair: (center_id, ctx_id) label = 1
                        self._update_pair(center_id, ctx_id, 1.0)

                        # Negative samples
                        for _ in range(n_negatives):
                            neg_id = rng.choice(all_ids)
                            if neg_id != ctx_id:
                                self._update_pair(center_id, neg_id, 0.0)

        return self

    def _update_pair(self, center_id: int, target_id: int, label: float) -> None:
        v_c = self.W_in[center_id]
        v_t = self.W_out[target_id]

        # Dot product
        dot = sum(v_c[d] * v_t[d] for d in range(self.dim))
        sig = 1.0 / (1.0 + math.exp(-max(-20.0, min(20.0, dot))))
        err = sig - label

        # Gradients
        for d in range(self.dim):
            g_c = err * v_t[d]
            g_t = err * v_c[d]
            self.W_in[center_id][d] -= self.lr * g_c
            self.W_out[target_id][d] -= self.lr * g_t

    def get_vector(self, word: str) -> Optional[List[float]]:
        wid = self.word2id.get(str(word).lower())
        if wid is not None:
            return self.W_in[wid]
        return None

    def cosine_similarity(self, word1: str, word2: str) -> float:
        v1 = self.get_vector(word1)
        v2 = self.get_vector(word2)
        if not v1 or not v2:
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1)) or 1.0
        norm2 = math.sqrt(sum(b * b for b in v2)) or 1.0
        return round(dot / (norm1 * norm2), 4)

    def most_similar(self, word: str, top_n: int = 5) -> List[Tuple[str, float]]:
        w = str(word).lower()
        if w not in self.word2id:
            return []
        sims = []
        for other_w in self.word2id:
            if other_w != w:
                sims.append((other_w, self.cosine_similarity(w, other_w)))
        sims.sort(key=lambda item: item[1], reverse=True)
        return sims[:top_n]


class TextRankSummarizer:
    """Graph-based TextRank keyword and sentence extraction."""

    @staticmethod
    def extract_keywords(text: str, top_n: int = 5, window_size: int = 3, max_iter: int = 30) -> List[str]:
        words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", str(text)) if w.lower() not in ENGLISH_STOPWORDS]
        if not words:
            return []

        vocab = sorted(list(set(words)))
        word_idx = {w: i for i, w in enumerate(vocab)}
        n = len(vocab)
        if n == 1:
            return vocab

        # Co-occurrence graph
        adj = [[0.0] * n for _ in range(n)]
        for i in range(len(words)):
            w1 = words[i]
            idx1 = word_idx[w1]
            for j in range(i + 1, min(len(words), i + window_size)):
                w2 = words[j]
                idx2 = word_idx[w2]
                if idx1 != idx2:
                    adj[idx1][idx2] += 1.0
                    adj[idx2][idx1] += 1.0

        # PageRank power iteration
        d = 0.85
        scores = [1.0 / n] * n
        deg = [sum(adj[i]) for i in range(n)]

        for _ in range(max_iter):
            new_scores = [(1.0 - d) / n] * n
            for i in range(n):
                for j in range(n):
                    if adj[j][i] > 0 and deg[j] > 0:
                        new_scores[i] += d * (scores[j] * adj[j][i] / deg[j])
            scores = new_scores

        ranked = sorted(zip(vocab, scores), key=lambda it: it[1], reverse=True)
        return [w for w, _ in ranked[:top_n]]

    @staticmethod
    def summarize(text: str, top_n_sentences: int = 2, max_iter: int = 30) -> str:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", str(text)) if s.strip()]
        if len(sentences) <= top_n_sentences:
            return " ".join(sentences)

        n = len(sentences)
        # Sentence word sets
        sent_words = [set(w.lower() for w in re.findall(r"\b\w+\b", s) if w.lower() not in ENGLISH_STOPWORDS) for s in sentences]

        # Similarity matrix based on token overlap
        sim_mat = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                inter = len(sent_words[i] & sent_words[j])
                len1 = len(sent_words[i])
                len2 = len(sent_words[j])
                if inter > 0 and len1 > 0 and len2 > 0:
                    denom = math.log(len1 + 1) + math.log(len2 + 1)
                    score = inter / denom if denom > 0 else 0.0
                    sim_mat[i][j] = score
                    sim_mat[j][i] = score

        d = 0.85
        scores = [1.0 / n] * n
        deg = [sum(sim_mat[i]) for i in range(n)]

        for _ in range(max_iter):
            new_scores = [(1.0 - d) / n] * n
            for i in range(n):
                for j in range(n):
                    if sim_mat[j][i] > 0 and deg[j] > 0:
                        new_scores[i] += d * (scores[j] * sim_mat[j][i] / deg[j])
            scores = new_scores

        ranked_indices = sorted(range(n), key=lambda i: scores[i], reverse=True)[:top_n_sentences]
        # Keep original sequence order
        ranked_indices.sort()
        return " ".join(sentences[i] for i in ranked_indices)


class KneserNeyLanguageModel:
    """N-gram language model with interpolated Kneser-Ney smoothing."""

    def __init__(self, order: int = 3, discount: float = 0.75):
        if order < 2:
            raise ValueError("Kneser-Ney model order must be >= 2")
        self.order = order
        self.discount = float(discount)
        self.ngram_counts: Dict[int, Dict[Tuple[str, ...], int]] = {i: {} for i in range(1, order + 1)}
        self.context_counts: Dict[Tuple[str, ...], int] = {}
        self.continuations_out: Dict[Tuple[str, ...], set] = {}
        self.continuations_in: Dict[str, set] = {}
        self.vocab: set = set()
        self.total_unique_bigrams = 0

    def fit(self, corpus: List[str]) -> "KneserNeyLanguageModel":
        tokenized_sentences = []
        for line in corpus:
            tokens = re.findall(r"\b\w+\b", str(line).lower())
            if tokens:
                tokenized_sentences.append(["<s>"] * (self.order - 1) + tokens + ["</s>"])
                self.vocab.update(tokens)

        self.vocab.add("<s>")
        self.vocab.add("</s>")

        # Count n-grams for lengths 1 .. order
        for sent in tokenized_sentences:
            for k in range(1, self.order + 1):
                for i in range(len(sent) - k + 1):
                    ng = tuple(sent[i : i + k])
                    self.ngram_counts[k][ng] = self.ngram_counts[k].get(ng, 0) + 1
                    if k > 1:
                        ctx = ng[:-1]
                        target_w = ng[-1]
                        self.context_counts[ctx] = self.context_counts.get(ctx, 0) + 1
                        if ctx not in self.continuations_out:
                            self.continuations_out[ctx] = set()
                        self.continuations_out[ctx].add(target_w)
                        if target_w not in self.continuations_in:
                            self.continuations_in[target_w] = set()
                        self.continuations_in[target_w].add(ctx[-1])

        self.total_unique_bigrams = sum(len(s) for s in self.continuations_in.values())
        return self

    def _p_continuation(self, word: str) -> float:
        if self.total_unique_bigrams == 0:
            return 1.0 / max(len(self.vocab), 1)
        num = len(self.continuations_in.get(word, set()))
        return max(num, 1e-6) / self.total_unique_bigrams

    def prob(self, word: str, context: Tuple[str, ...]) -> float:
        """Computes Kneser-Ney smoothed P(word | context)."""
        ctx = tuple(context[-(self.order - 1):])
        k = len(ctx) + 1

        if k == 1:
            return self._p_continuation(word)

        ctx_count = self.context_counts.get(ctx, 0)
        ng = ctx + (word,)
        ng_count = self.ngram_counts[k].get(ng, 0)

        lower_prob = self.prob(word, ctx[1:])

        if ctx_count == 0:
            return lower_prob

        # Discounted count
        direct_prob = max(ng_count - self.discount, 0.0) / ctx_count
        num_continuations = len(self.continuations_out.get(ctx, set()))
        alpha = (self.discount * num_continuations) / ctx_count

        return direct_prob + alpha * lower_prob

    def score_sentence(self, sentence: str) -> float:
        """Calculates log2 probability of a sentence under the model."""
        tokens = re.findall(r"\b\w+\b", str(sentence).lower())
        if not tokens:
            return 0.0
        padded = ["<s>"] * (self.order - 1) + tokens + ["</s>"]
        total_log_prob = 0.0
        for i in range(self.order - 1, len(padded)):
            w = padded[i]
            ctx = tuple(padded[i - self.order + 1 : i])
            p = max(self.prob(w, ctx), 1e-12)
            total_log_prob += math.log2(p)
        return round(total_log_prob, 4)

    def predict_next(self, context_tokens: List[str], top_n: int = 5) -> List[Tuple[str, float]]:
        """Predicts top candidate next words given context."""
        ctx = tuple(str(tok).lower() for tok in context_tokens)
        candidates = []
        for w in self.vocab:
            if w in ("<s>", "</s>"):
                continue
            p = self.prob(w, ctx)
            candidates.append((w, round(p, 6)))
        candidates.sort(key=lambda t: t[1], reverse=True)
        return candidates[:top_n]


def nlp_kneser_ney(order: int = 3, discount: float = 0.75) -> KneserNeyLanguageModel:
    """Creates a Kneser-Ney smoothed n-gram language model."""
    return KneserNeyLanguageModel(order=order, discount=discount)



