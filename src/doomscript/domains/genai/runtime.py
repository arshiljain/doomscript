"""GenAI Domain Runtime: Industrial-grade LLM architectures, attention mechanisms, sampling, tokenization, vector search, and evaluation."""
import math
import random
import re
from typing import List, Dict, Any, Optional, Tuple, Set, Union
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. TEXT CHUNKING & PRE-PROCESSING
# ============================================================================

def genai_chunk_text(text: str, size: int = 500, overlap: int = 50) -> List[str]:
    """Splits text into chunks of specified character size with overlap.
    
    Args:
        text: The source string to be chunked.
        size: Target chunk character size.
        overlap: Character overlap between consecutive chunks.
        
    Returns:
        List of text chunks.
    """
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

def genai_recursive_chunk(text: str, max_chunk_size: int = 500, separators: Optional[List[str]] = None) -> List[str]:
    """Recursively splits text on natural boundaries (paragraphs, sentences, words)."""
    if separators is None:
        separators = ["\n\n", "\n", ". ", "? ", "! ", " ", ""]
    if len(text) <= max_chunk_size:
        return [text] if text else []
    sep = separators[0]
    sub_seps = separators[1:]
    if not sep:
        return [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    splits = text.split(sep)
    results = []
    current_chunk = ""
    for s in splits:
        piece = s if not current_chunk else sep + s
        if len(current_chunk) + len(piece) <= max_chunk_size:
            current_chunk += piece
        else:
            if current_chunk:
                results.append(current_chunk)
            if len(s) > max_chunk_size and sub_seps:
                results.extend(genai_recursive_chunk(s, max_chunk_size, sub_seps))
                current_chunk = ""
            else:
                current_chunk = s
    if current_chunk:
        results.append(current_chunk)
    return [c.strip() for c in results if c.strip()]

def genai_estimate_tokens(text: str) -> int:
    """Heuristic token estimator (~4 chars per token for English)."""
    if not text:
        return 0
    words = len(text.split())
    chars = len(text)
    return max(words, int(chars / 4.0))

def genai_apply_template(template: str, variables: Dict[str, Any]) -> str:
    """Fills a prompt template with variable substitution."""
    res = template
    for k, v in variables.items():
        res = res.replace("{" + str(k) + "}", str(v))
        res = res.replace("{{" + str(k) + "}}", str(v))
    return res

# ============================================================================
# 2. VECTOR SIMILARITY & EMBEDDING ALGORITHMS
# ============================================================================

def genai_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates cosine similarity between two numeric vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return max(-1.0, min(1.0, dot / (norm1 * norm2)))

def genai_euclidean_distance(v1: List[float], v2: List[float]) -> float:
    """Calculates Euclidean (L2) distance between two vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return float("inf")
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

def genai_dot_product(v1: List[float], v2: List[float]) -> float:
    """Calculates dot product between two vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    return sum(a * b for a, b in zip(v1, v2))

def genai_l2_normalize(vector: List[float]) -> List[float]:
    """Normalizes vector to unit L2 length."""
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0.0:
        return list(vector)
    return [round(x / norm, 6) for x in vector]

def genai_retrieve_top_k(chunks: List[Any], query_vec: List[float], chunk_vectors: Optional[Any] = None, k: int = 3) -> List[Dict[str, Any]]:
    """Retrieves top k chunks closest to query_vec by cosine similarity.
    Supports both (chunks, query_vec, k) and (chunks, query_vec, chunk_vectors, k).
    """
    if isinstance(chunk_vectors, (int, float)):
        k = int(chunk_vectors)
        chunk_vectors = None
    results = []
    if chunk_vectors is not None and isinstance(chunk_vectors, list) and len(chunk_vectors) == len(chunks):
        for c, vec in zip(chunks, chunk_vectors):
            sim = genai_cosine_similarity(query_vec, vec)
            results.append({"chunk": c, "score": round(sim, 4)})
    else:
        for c in chunks:
            if isinstance(c, dict) and "embedding" in c:
                sim = genai_cosine_similarity(query_vec, c["embedding"])
                results.append({"chunk": c.get("text", c), "score": round(sim, 4), "item": c})
            elif isinstance(c, (list, tuple)) and len(c) == 2 and isinstance(c[1], list):
                sim = genai_cosine_similarity(query_vec, c[1])
                results.append({"chunk": c[0], "score": round(sim, 4)})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:int(k)]

# ============================================================================
# 3. LEXICAL SEARCH & INFORMATION RETRIEVAL (BM25 & RRF)
# ============================================================================

def genai_bm25_score(query_tokens: List[str], doc_tokens: List[str], doc_freq: Optional[Dict[str, int]] = None, total_docs: int = 1, avg_doc_len: float = 100.0, k1: float = 1.5, b: float = 0.75) -> float:
    """Calculates BM25 lexical relevance score for a document against query tokens."""
    if not query_tokens or not doc_tokens:
        return 0.0
    doc_len = len(doc_tokens)
    score = 0.0
    for q in query_tokens:
        tf = doc_tokens.count(q)
        if tf > 0:
            numerator = tf * (k1 + 1.0)
            denominator = tf + k1 * (1.0 - b + b * (doc_len / max(1.0, avg_doc_len)))
            idf = 1.0
            if doc_freq and q in doc_freq:
                df = doc_freq[q]
                idf = math.log(max(1.0, (total_docs - df + 0.5) / (df + 0.5) + 1.0))
            score += idf * (numerator / denominator)
    return round(score, 4)

def genai_reciprocal_rank_fusion(ranked_lists: List[List[Any]], k: int = 60) -> List[Dict[str, Any]]:
    """Merges multiple search result rankings using Reciprocal Rank Fusion (RRF)."""
    scores: Dict[str, float] = {}
    items: Dict[str, Any] = {}
    for rlist in ranked_lists:
        for rank, item in enumerate(rlist):
            key = str(item)
            items[key] = item
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank + 1)
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [{"item": items[k], "rrf_score": round(s, 6)} for k, s in sorted_items]

# ============================================================================
# 4. ATTENTION MECHANISMS & POSITIONAL ENCODINGS
# ============================================================================

def genai_softmax(logits: List[float], temperature: float = 1.0) -> List[float]:
    """Applies temperature scaling and softmax normalization to logit vector."""
    if not logits:
        return []
    temp = max(1e-5, float(temperature))
    scaled = [l / temp for l in logits]
    max_l = max(scaled)
    exp_l = [math.exp(l - max_l) for l in scaled]
    sum_exp = sum(exp_l)
    return [round(e / sum_exp, 6) for e in exp_l]

def genai_softmax_sample(logits: List[float], temperature: float = 1.0) -> List[float]:
    """Backward-compatible alias for genai_softmax."""
    return genai_softmax(logits, temperature)

def genai_multi_head_attention(Q: List[List[float]], K: List[List[float]], V: List[List[float]], heads: int = 2) -> List[List[float]]:
    """Computes Multi-Head Scaled Dot-Product Attention simulation."""
    seq_len = len(Q)
    if seq_len == 0:
        return []
    d_model = len(Q[0])
    d_k = max(1, d_model // heads)
    output = [[0.0] * d_model for _ in range(seq_len)]
    for h in range(heads):
        start_col = h * d_k
        end_col = (h + 1) * d_k
        scores = [[0.0] * seq_len for _ in range(seq_len)]
        scale = math.sqrt(d_k)
        for i in range(seq_len):
            for j in range(seq_len):
                dot = sum(Q[i][c] * K[j][c] for c in range(start_col, end_col))
                scores[i][j] = dot / scale
        weights = [genai_softmax(row, temperature=1.0) for row in scores]
        for i in range(seq_len):
            for c in range(start_col, end_col):
                val = sum(weights[i][j] * V[j][c] for j in range(seq_len))
                output[i][c] = round(val, 4)
    return output

def genai_grouped_query_attention(Q: List[List[float]], K: List[List[float]], V: List[List[float]], num_q_heads: int = 8, num_kv_heads: int = 2) -> List[List[float]]:
    """Simulates Grouped-Query Attention (GQA) where multiple Q heads share a KV head."""
    seq_len = len(Q)
    if seq_len == 0:
        return []
    d_model = len(Q[0])
    head_dim = max(1, d_model // num_q_heads)
    group_size = num_q_heads // num_kv_heads
    output = [[0.0] * d_model for _ in range(seq_len)]
    scale = math.sqrt(head_dim)
    for q_h in range(num_q_heads):
        kv_h = q_h // group_size
        q_start = q_h * head_dim
        kv_start = (kv_h % len(K[0])) * head_dim
        scores = [[0.0] * seq_len for _ in range(seq_len)]
        for i in range(seq_len):
            for j in range(seq_len):
                dot = sum(Q[i][q_start + c] * K[j][min(kv_start + c, len(K[0])-1)] for c in range(head_dim))
                scores[i][j] = dot / scale
        weights = [genai_softmax(row, temperature=1.0) for row in scores]
        for i in range(seq_len):
            for c in range(head_dim):
                val = sum(weights[i][j] * V[j][min(kv_start + c, len(V[0])-1)] for j in range(seq_len))
                output[i][q_start + c] = round(val, 4)
    return output

def genai_apply_rope(vectors: List[List[float]], base: float = 10000.0) -> List[List[float]]:
    """Applies Rotary Position Embedding (RoPE) rotation to vectors by token position."""
    res = []
    for pos, vec in enumerate(vectors):
        new_vec = list(vec)
        d = len(vec)
        for i in range(0, d - 1, 2):
            theta = 1.0 / (base ** (i / d))
            m_theta = pos * theta
            cos_m = math.cos(m_theta)
            sin_m = math.sin(m_theta)
            v0 = vec[i]
            v1 = vec[i + 1]
            new_vec[i] = round(v0 * cos_m - v1 * sin_m, 6)
            new_vec[i + 1] = round(v0 * sin_m + v1 * cos_m, 6)
        res.append(new_vec)
    return res

def genai_alibi_bias(seq_len: int, num_heads: int = 8) -> List[List[List[float]]]:
    """Generates ALiBi (Attention with Linear Biases) geometric slope bias matrices."""
    m_slopes = [2.0 ** (-8.0 * (i + 1) / num_heads) for i in range(num_heads)]
    biases = []
    for m in m_slopes:
        mat = [[0.0] * seq_len for _ in range(seq_len)]
        for i in range(seq_len):
            for j in range(seq_len):
                mat[i][j] = round(-m * abs(i - j), 4)
        biases.append(mat)
    return biases

# ============================================================================
# 5. TOKENIZATION (BPE, WORDPIECE, UNIGRAM)
# ============================================================================

def genai_train_bpe(corpus: List[str], num_merges: int = 10) -> Dict[str, Any]:
    """Trains a simple Byte-Pair Encoding (BPE) vocabulary from text corpus."""
    vocab: Dict[str, int] = {}
    for word in corpus:
        chars = " ".join(list(word)) + " </w>"
        vocab[chars] = vocab.get(chars, 0) + 1
    merges: List[Tuple[str, str]] = []
    for _ in range(int(num_merges)):
        pairs: Dict[Tuple[str, str], int] = {}
        for word_str, freq in vocab.items():
            symbols = word_str.split()
            for i in range(len(symbols) - 1):
                p = (symbols[i], symbols[i + 1])
                pairs[p] = pairs.get(p, 0) + freq
        if not pairs:
            break
        best_pair = max(pairs.items(), key=lambda x: x[1])[0]
        merges.append(best_pair)
        bigram = " ".join(best_pair)
        replacement = "".join(best_pair)
        new_vocab = {}
        for word_str, freq in vocab.items():
            new_word_str = word_str.replace(bigram, replacement)
            new_vocab[new_word_str] = freq
        vocab = new_vocab
    return {"merges": merges, "vocabulary": vocab}

def genai_encode_bpe(text: str, merges: List[Tuple[str, str]]) -> List[str]:
    """Encodes text into subword tokens using learned BPE merge rules."""
    words = text.split()
    tokens = []
    for w in words:
        chars = list(w) + ["</w>"]
        for p1, p2 in merges:
            i = 0
            new_chars = []
            while i < len(chars):
                if i < len(chars) - 1 and chars[i] == p1 and chars[i + 1] == p2:
                    new_chars.append(p1 + p2)
                    i += 2
                else:
                    new_chars.append(chars[i])
                    i += 1
            chars = new_chars
        tokens.extend(chars)
    return tokens

def genai_decode_bpe(tokens: List[str]) -> str:
    """Decodes BPE tokens back into coherent text."""
    joined = "".join(tokens)
    return joined.replace("</w>", " ").strip()

# ============================================================================
# 6. SAMPLING & GENERATION STRATEGIES
# ============================================================================

def genai_sample_logits(logits: List[float], temperature: float = 1.0, top_k: int = 0, top_p: float = 1.0, min_p: float = 0.0) -> int:
    """Samples next token index using temperature scaling, top-k, nucleus top-p, and min-p."""
    if not logits:
        return 0
    probs = genai_softmax(logits, temperature=temperature)
    indexed = sorted(list(enumerate(probs)), key=lambda x: x[1], reverse=True)
    if top_k > 0:
        indexed = indexed[:top_k]
    if min_p > 0.0 and indexed:
        top_prob = indexed[0][1]
        threshold = top_prob * min_p
        indexed = [(idx, p) for idx, p in indexed if p >= threshold]
    if top_p < 1.0 and indexed:
        cum = 0.0
        filtered = []
        for idx, p in indexed:
            filtered.append((idx, p))
            cum += p
            if cum >= top_p:
                break
        indexed = filtered
    tot = sum(p for _, p in indexed)
    if tot <= 0.0:
        return indexed[0][0]
    norm = [(idx, p / tot) for idx, p in indexed]
    r = random.random()
    acc = 0.0
    for idx, p in norm:
        acc += p
        if r <= acc:
            return idx
    return indexed[0][0]

def genai_beam_search(initial_state: str, expand_fn: Any, beam_width: int = 3, max_steps: int = 5, length_penalty: float = 0.6) -> List[Dict[str, Any]]:
    """Beam search decoder with length-normalized cumulative log-probabilities."""
    beams = [(initial_state, 0.0)]
    for step in range(int(max_steps)):
        all_candidates = []
        for state, score in beams:
            expansions = expand_fn(state) if callable(expand_fn) else [(state + f" w{idx}", -0.5 * (idx + 1)) for idx in range(beam_width)]
            for next_state, log_p in expansions:
                all_candidates.append((next_state, score + log_p))
        all_candidates.sort(key=lambda x: x[1] / (len(x[0].split()) ** length_penalty), reverse=True)
        beams = all_candidates[:int(beam_width)]
    return [{"sequence": seq, "log_prob": round(score, 4), "normalized_score": round(score / (len(seq.split()) ** length_penalty), 4)} for seq, score in beams]

def genai_speculative_verification(draft_tokens: List[int], draft_probs: List[float], target_probs: List[float]) -> Dict[str, Any]:
    """Simulates speculative decoding token verification with rejection sampling."""
    accepted = []
    n = min(len(draft_tokens), len(draft_probs), len(target_probs))
    for i in range(n):
        q = draft_probs[i]
        p = target_probs[i]
        if q <= 0.0:
            accepted.append(draft_tokens[i])
            continue
        r = random.random()
        if r < min(1.0, p / q):
            accepted.append(draft_tokens[i])
        else:
            break
    speedup = (len(accepted) + 1) / max(1, len(draft_tokens))
    return {
        "accepted_tokens": accepted,
        "num_accepted": len(accepted),
        "acceptance_rate": round(len(accepted) / max(1, n), 4),
        "effective_speedup": round(speedup, 2)
    }

# ============================================================================
# 7. KV CACHE & GPU MEMORY PROFILING
# ============================================================================

def genai_calculate_kv_cache_memory(num_layers: int, num_heads: int, head_dim: int, seq_len: int, batch_size: int = 1, precision_bytes: int = 2) -> Dict[str, Any]:
    """Calculates KV Cache GPU memory requirements in MB and GB."""
    elements_per_token = 2 * int(num_layers) * int(num_heads) * int(head_dim)
    bytes_per_token = elements_per_token * int(precision_bytes)
    total_bytes = bytes_per_token * int(seq_len) * int(batch_size)
    mb = total_bytes / (1024 * 1024)
    gb = mb / 1024
    return {
        "bytes_per_token": bytes_per_token,
        "total_megabytes": round(mb, 2),
        "total_gigabytes": round(gb, 4),
        "parameters": {
            "num_layers": num_layers, "num_heads": num_heads,
            "head_dim": head_dim, "seq_len": seq_len, "batch_size": batch_size
        }
    }

class PagedKVCacheManager:
    """Simulates PagedAttention non-contiguous block memory allocation for KV cache."""
    def __init__(self, block_size: int = 16, num_blocks: int = 128):
        self.block_size = int(block_size)
        self.num_blocks = int(num_blocks)
        self.free_blocks = list(range(num_blocks))
        self.block_tables: Dict[str, List[int]] = {}

    def allocate(self, req_id: str, seq_len: int) -> bool:
        needed_blocks = math.ceil(seq_len / self.block_size)
        if len(self.free_blocks) < needed_blocks:
            return False
        allocated = [self.free_blocks.pop(0) for _ in range(needed_blocks)]
        self.block_tables[req_id] = allocated
        return True

    def free(self, req_id: str) -> None:
        if req_id in self.block_tables:
            self.free_blocks.extend(self.block_tables[req_id])
            del self.block_tables[req_id]

    def utilization(self) -> float:
        used = self.num_blocks - len(self.free_blocks)
        return round(used / self.num_blocks, 4)

# ============================================================================
# 8. ADAPTERS & FINE-TUNING (LORA & QLORA)
# ============================================================================

def genai_lora_forward(x: List[float], W: List[List[float]], A: List[List[float]], B: List[List[float]], alpha: float = 16.0, r: int = 4) -> List[float]:
    """Simulates Low-Rank Adaptation (LoRA) linear forward pass: y = x * W + (alpha/r) * (x * A) * B."""
    out_dim = len(W[0])
    in_dim = len(x)
    base_out = [0.0] * out_dim
    for j in range(out_dim):
        base_out[j] = sum(x[i] * W[i][j] for i in range(in_dim))
    r_dim = len(A[0])
    a_out = [0.0] * r_dim
    for k in range(r_dim):
        a_out[k] = sum(x[i] * A[i][k] for i in range(in_dim))
    lora_out = [0.0] * out_dim
    for j in range(out_dim):
        lora_out[j] = sum(a_out[k] * B[k][j] for k in range(r_dim))
    scale = float(alpha) / max(1, int(r))
    final_out = [round(base_out[j] + scale * lora_out[j], 4) for j in range(out_dim)]
    return final_out

def genai_quantize_int4(weights: List[float]) -> Dict[str, Any]:
    """Simulates symmetric 4-bit integer weight quantization."""
    if not weights:
        return {"scale": 1.0, "quantized": []}
    max_val = max(abs(w) for w in weights) or 1.0
    scale = max_val / 7.0
    quantized = [max(-8, min(7, round(w / scale))) for w in weights]
    return {"scale": round(scale, 6), "quantized": quantized}

# ============================================================================
# 9. GUARDRAILS, PII REDACTION & PROMPT SAFETY
# ============================================================================

def genai_detect_prompt_injection(text: str) -> Dict[str, Any]:
    """Scans text for common prompt injection and system prompt extraction patterns."""
    patterns = [
        r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"system\s*:\s*",
        r"you\s+are\s+now\s+(an?\s+)?unrestricted",
        r"reveal\s+your\s+(initial|system)\s+prompt",
        r"print\s+(the\s+)?system\s+prompt",
        r"disregard\s+all\s+rules",
        r"bypass\s+filters",
        r"do\s+anything\s+now",
        r"DAN\s+mode"
    ]
    flags = []
    t_lower = text.lower()
    for p in patterns:
        if re.search(p, t_lower):
            flags.append(p)
    return {
        "is_suspicious": len(flags) > 0,
        "suspicious": len(flags) > 0,
        "matched_rules": flags,
        "risk_level": "high" if len(flags) >= 2 else ("medium" if len(flags) == 1 else "clean")
    }

def genai_redact_pii(text: str, mask: str = "[REDACTED]") -> Dict[str, Any]:
    """Scans and redacts emails, phone numbers, SSNs, and IP addresses."""
    email_pat = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pat = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    ssn_pat = r"\b\d{3}-\d{2}-\d{4}\b"
    ip_pat = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    redacted = text
    matches = []
    for pat, label in [(email_pat, "EMAIL"), (phone_pat, "PHONE"), (ssn_pat, "SSN"), (ip_pat, "IP")]:
        for m in re.finditer(pat, text):
            matches.append({"type": label, "value": m.group(0), "span": m.span()})
        redacted = re.sub(pat, mask, redacted)
    return {"clean_text": redacted, "redactions": matches, "count": len(matches)}

# ============================================================================
# 10. EVALUATION METRICS (ROUGE, BLEU, PERPLEXITY)
# ============================================================================

def genai_rouge_l(candidate: str, reference: str) -> Dict[str, float]:
    """Calculates ROUGE-L (Longest Common Subsequence) precision, recall, and F1."""
    c_words = candidate.lower().split()
    r_words = reference.lower().split()
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
    prec = lcs_len / m
    rec = lcs_len / n
    f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
    return {"precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}

def genai_bleu_score(candidate: str, reference: str, max_n: int = 4) -> float:
    """Calculates sentence-level BLEU score up to max_n n-grams with brevity penalty."""
    c_words = candidate.lower().split()
    r_words = reference.lower().split()
    c_len = len(c_words)
    r_len = len(r_words)
    if c_len == 0 or r_len == 0:
        return 0.0
    bp = 1.0 if c_len > r_len else math.exp(1.0 - r_len / c_len)
    precisions = []
    for n in range(1, max_n + 1):
        c_ngrams = [tuple(c_words[i:i+n]) for i in range(len(c_words) - n + 1)]
        r_ngrams = [tuple(r_words[i:i+n]) for i in range(len(r_words) - n + 1)]
        if not c_ngrams:
            precisions.append(1e-5)
            continue
        c_counts: Dict[Tuple[str, ...], int] = {}
        for ng in c_ngrams:
            c_counts[ng] = c_counts.get(ng, 0) + 1
        r_counts: Dict[Tuple[str, ...], int] = {}
        for ng in r_ngrams:
            r_counts[ng] = r_counts.get(ng, 0) + 1
        clipped = sum(min(count, r_counts.get(ng, 0)) for ng, count in c_counts.items())
        precisions.append(max(1e-5, clipped / len(c_ngrams)))
    geo_mean = math.exp(sum(math.log(p) for p in precisions) / max_n)
    return round(bp * geo_mean, 4)

def genai_perplexity(cross_entropy_losses: List[float]) -> float:
    """Computes perplexity from a list of token cross-entropy loss values."""
    if not cross_entropy_losses:
        return 1.0
    avg_loss = sum(cross_entropy_losses) / len(cross_entropy_losses)
    return round(math.exp(avg_loss), 4)

# ============================================================================
# 11. SEMANTIC VECTOR CACHE
# ============================================================================

class GenAISemanticCache:
    """In-memory semantic vector cache with similarity threshold matching."""
    def __init__(self, threshold: float = 0.85):
        self.threshold = float(threshold)
        self.entries: List[Dict[str, Any]] = []

    def lookup(self, query_vec: List[float]) -> Optional[Dict[str, Any]]:
        best_match = None
        best_sim = -1.0
        for entry in self.entries:
            sim = genai_cosine_similarity(query_vec, entry["embedding"])
            if sim > best_sim:
                best_sim = sim
                best_match = entry
        if best_sim >= self.threshold and best_match is not None:
            return {"hit": True, "similarity": round(best_sim, 4), "response": best_match["response"]}
        return {"hit": False, "best_similarity": round(max(0.0, best_sim), 4)}

    def insert(self, query: str, query_vec: List[float], response: str) -> None:
        self.entries.append({"query": query, "embedding": query_vec, "response": response})

    def count(self) -> int:
        return len(self.entries)

# ============================================================================
# 12. DOMAIN RUNTIME WRAPPER
# ============================================================================

class GenAIRuntime(DomainRuntime):
    """Unified runtime bridge for the GenAI computational domain."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def chunk(self, text: str, size: int = 500, overlap: int = 50) -> List[str]:
        return genai_chunk_text(text, size, overlap)
    def recursive_chunk(self, text: str, max_chunk_size: int = 500) -> List[str]:
        return genai_recursive_chunk(text, max_chunk_size)
    def similarity(self, v1: List[float], v2: List[float]) -> float:
        return genai_cosine_similarity(v1, v2)
    def euclidean(self, v1: List[float], v2: List[float]) -> float:
        return genai_euclidean_distance(v1, v2)
    def normalize(self, v: List[float]) -> List[float]:
        return genai_l2_normalize(v)
    def retrieve(self, chunks: List[Any], query_vec: List[float], k: int = 3) -> List[Dict[str, Any]]:
        return genai_retrieve_top_k(chunks, query_vec, k=k)
    def estimate_tokens(self, text: str) -> int:
        return genai_estimate_tokens(text)
    def prompt(self, template: str, variables: Dict[str, Any]) -> str:
        return genai_apply_template(template, variables)
    def bm25(self, query_tokens: List[str], doc_tokens: List[str]) -> float:
        return genai_bm25_score(query_tokens, doc_tokens)
    def rrf(self, ranked_lists: List[List[Any]]) -> List[Dict[str, Any]]:
        return genai_reciprocal_rank_fusion(ranked_lists)
    def softmax(self, logits: List[float], temp: float = 1.0) -> List[float]:
        return genai_softmax(logits, temp)
    def sample(self, logits: List[float], temp: float = 1.0, k: int = 0, p: float = 1.0, min_p: float = 0.0) -> int:
        return genai_sample_logits(logits, temp, k, p, min_p)
    def guard(self, text: str) -> Dict[str, Any]:
        return genai_detect_prompt_injection(text)
    def rouge(self, candidate: str, reference: str) -> Dict[str, float]:
        return genai_rouge_l(candidate, reference)
    def bleu(self, candidate: str, reference: str) -> float:
        return genai_bleu_score(candidate, reference)
    def attention(self, Q: List[List[float]], K: List[List[float]], V: List[List[float]], heads: int = 2) -> List[List[float]]:
        return genai_multi_head_attention(Q, K, V, heads)
    def gqa(self, Q: List[List[float]], K: List[List[float]], V: List[List[float]], q_heads: int = 8, kv_heads: int = 2) -> List[List[float]]:
        return genai_grouped_query_attention(Q, K, V, q_heads, kv_heads)
    def rope(self, vectors: List[List[float]]) -> List[List[float]]:
        return genai_apply_rope(vectors)
    def alibi(self, seq_len: int, num_heads: int = 8) -> List[List[List[float]]]:
        return genai_alibi_bias(seq_len, num_heads)
    def bpe_train(self, corpus: List[str], merges: int = 10) -> Dict[str, Any]:
        return genai_train_bpe(corpus, merges)
    def bpe_encode(self, text: str, merges: List[Tuple[str, str]]) -> List[str]:
        return genai_encode_bpe(text, merges)
    def bpe_decode(self, tokens: List[str]) -> str:
        return genai_decode_bpe(tokens)
    def redact(self, text: str) -> Dict[str, Any]:
        return genai_redact_pii(text)
    def kv_memory(self, layers: int, heads: int, dim: int, seq: int) -> Dict[str, Any]:
        return genai_calculate_kv_cache_memory(layers, heads, dim, seq)
    def speculative(self, draft: List[int], d_probs: List[float], t_probs: List[float]) -> Dict[str, Any]:
        return genai_speculative_verification(draft, d_probs, t_probs)
    def lora(self, x: List[float], W: List[List[float]], A: List[List[float]], B: List[List[float]]) -> List[float]:
        return genai_lora_forward(x, W, A, B)
    def quantize_int4(self, weights: List[float]) -> Dict[str, Any]:
        return genai_quantize_int4(weights)
    def beam_search(self, start: str, expand: Any, width: int = 3) -> List[Dict[str, Any]]:
        return genai_beam_search(start, expand, width)
    def perplexity(self, losses: List[float]) -> float:
        return genai_perplexity(losses)
    def new_cache(self, threshold: float = 0.85) -> GenAISemanticCache:
        return GenAISemanticCache(threshold)
    def new_paged_kv(self, block_size: int = 16, num_blocks: int = 128) -> PagedKVCacheManager:
        return PagedKVCacheManager(block_size, num_blocks)
