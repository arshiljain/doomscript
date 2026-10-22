"""GenAI Domain Runtime: RAG chunking, vector similarity, token estimation, BM25, RRF, Softmax, ROUGE, and BLEU."""
import math
import random
import re
from typing import List, Dict, Any, Optional

def genai_chunk_text(text: str, size: int = 500, overlap: int = 50) -> List[str]:
    """Splits text into chunks of specified character size with overlap."""
    size = int(size)
    overlap = int(overlap)
    if size <= overlap:
        overlap = max(0, size // 4)
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + size, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start += (size - overlap)
    return chunks

def genai_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates cosine similarity between two numeric embedding vectors."""
    if len(v1) != len(v2) or not v1:
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return round(dot / (norm1 * norm2), 4)

def genai_retrieve_top_k(chunks: List[Any], query_vec: List[float], chunk_vectors: List[List[float]], k: int = 3) -> List[Dict[str, Any]]:
    """Retrieves the top k most similar chunks based on cosine similarity."""
    k = int(k)
    scored = []
    for i, (chunk, vec) in enumerate(zip(chunks, chunk_vectors)):
        sim = genai_cosine_similarity(query_vec, vec)
        scored.append({"index": i, "chunk": chunk, "score": sim})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:k]

def genai_estimate_tokens(text: str) -> int:
    """Heuristic token count estimation (~4 characters per token)."""
    if not text:
        return 0
    words = re.findall(r"\w+|[^\w\s]", str(text))
    return max(1, int(len(words) * 1.25))

def genai_apply_template(template: str, variables: Dict[str, Any]) -> str:
    """Fills a prompt template string with variable values."""
    res = str(template)
    for k, v in variables.items():
        res = res.replace("{" + str(k) + "}", str(v))
    return res

def genai_bm25_score(query_tokens: List[str], doc_tokens: List[str], doc_freq: Dict[str, int], total_docs: int, avg_doc_len: float, k1: float = 1.5, b: float = 0.75) -> float:
    """Calculates Okapi BM25 score for a document given query tokens and corpus statistics."""
    doc_len = len(doc_tokens)
    if doc_len == 0 or total_docs == 0:
        return 0.0
    tf_dict = {}
    for t in doc_tokens:
        tf_dict[t] = tf_dict.get(t, 0) + 1
    score = 0.0
    for q in query_tokens:
        if q in tf_dict:
            tf = tf_dict[q]
            df = doc_freq.get(q, 1)
            idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1.0)
            denom = tf + k1 * (1.0 - b + b * (doc_len / avg_doc_len)) if avg_doc_len > 0 else tf + k1
            score += idf * (tf * (k1 + 1.0)) / denom
    return round(score, 4)

def genai_reciprocal_rank_fusion(ranked_lists: List[List[Any]], k: int = 60) -> List[Dict[str, Any]]:
    """Combines multiple ranked lists (e.g. dense + sparse search) using Reciprocal Rank Fusion (RRF)."""
    scores = {}
    for r_list in ranked_lists:
        for rank, item in enumerate(r_list):
            item_key = str(item)
            scores[item_key] = scores.get(item_key, 0.0) + 1.0 / (k + rank + 1)
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [{"item": item, "score": round(score, 6)} for item, score in sorted_items]

def genai_softmax_sample(logits: List[float], temperature: float = 1.0) -> List[float]:
    """Applies temperature scaling and softmax to a list of unnormalized logits."""
    if not logits:
        return []
    temp = max(1e-5, float(temperature))
    scaled = [l / temp for l in logits]
    max_val = max(scaled)
    exp_vals = [math.exp(v - max_val) for v in scaled]
    sum_exp = sum(exp_vals)
    return [round(v / sum_exp, 4) for v in exp_vals]

def genai_detect_prompt_injection(text: str) -> Dict[str, Any]:
    """Heuristic rule-based detection for prompt injection and jailbreak attempts."""
    t = str(text).lower()
    patterns = [
        (r"ignore\s+(?:all\s+)?previous\s+instructions", "Instruction override"),
        (r"system\s*:\s*you\s+are\s+now", "System role spoofing"),
        (r"dan\s+mode|jailbreak|unrestricted\s+mode", "Jailbreak persona"),
        (r"disregard\s+(?:the\s+)?above", "Above disregard"),
        (r"reveal\s+(?:the\s+)?secret\s+key|api\s*key", "Secret extraction")
    ]
    matches = []
    for pat, desc in patterns:
        if re.search(pat, t):
            matches.append(desc)
    is_suspicious = len(matches) > 0
    risk_score = min(1.0, len(matches) * 0.35)
    return {"suspicious": is_suspicious, "risk_score": round(risk_score, 2), "flags": matches}

def genai_rouge_l(candidate: str, reference: str) -> Dict[str, float]:
    """Calculates ROUGE-L (Longest Common Subsequence) precision, recall, and F1."""
    c_words = str(candidate).lower().split()
    r_words = str(reference).lower().split()
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
    lcs = dp[m][n]
    prec = lcs / m
    rec = lcs / n
    f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
    return {"precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}

def genai_bleu_score(candidate: str, reference: str, max_n: int = 4) -> float:
    """Calculates simple sentence BLEU score with brevity penalty."""
    c_words = str(candidate).lower().split()
    r_words = str(reference).lower().split()
    if not c_words or not r_words:
        return 0.0
    precisions = []
    for n in range(1, max_n + 1):
        c_ngrams = [tuple(c_words[i:i+n]) for i in range(len(c_words) - n + 1)]
        r_ngrams = [tuple(r_words[i:i+n]) for i in range(len(r_words) - n + 1)]
        if not c_ngrams:
            break
        r_counts = {}
        for g in r_ngrams:
            r_counts[g] = r_counts.get(g, 0) + 1
        matches = 0
        for g in c_ngrams:
            if r_counts.get(g, 0) > 0:
                matches += 1
                r_counts[g] -= 1
        precisions.append(matches / len(c_ngrams) if c_ngrams else 0.0)
    if not precisions or min(precisions) == 0.0:
        return 0.0
    log_sum = sum(math.log(p) for p in precisions) / len(precisions)
    geo_mean = math.exp(log_sum)
    # Brevity penalty
    c_len = len(c_words)
    r_len = len(r_words)
    bp = 1.0 if c_len > r_len else math.exp(1.0 - (r_len / c_len))
    return round(bp * geo_mean, 4)
