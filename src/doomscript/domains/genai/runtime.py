"""GenAI Domain Runtime: RAG chunking, vector similarity, token estimation, and prompt templating."""
import math
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
    return dot / (norm1 * norm2)

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
    # Words + punctuation heuristic
    words = re.findall(r"\w+|[^\w\s]", str(text))
    return max(1, int(len(words) * 1.25))

def genai_apply_template(template: str, variables: Dict[str, Any]) -> str:
    """Fills a prompt template containing {variable} placeholders."""
    result = str(template)
    for k, v in variables.items():
        result = result.replace(f"{{{k}}}", str(v))
    return result
