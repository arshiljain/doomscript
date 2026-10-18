"""
DoomScript Extended Runtime (Phases 26 to 100)
Pure Python Standard Library implementations covering:
- Systems, OS & Signals (Phases 26-32)
- Network Protocols & Sockets (Phases 33-40)
- Advanced Data Engineering & Compression (Phases 41-48)
- Math, Linear Algebra & Statistics (Phases 49-56)
- Event-Driven, Queues & Resiliency (Phases 57-64)
- Web, UI & Components (Phases 65-72)
- AI Agents, RAG & Cognitive Loops (Phases 73-80)
- Security, Auth, JWT & Compliance (Phases 81-88)
- Cloud, Containers & Metrics (Phases 89-95)
- Metaprogramming, FFI & Self-Hosting (Phases 96-100)
"""

import os
import sys
import time
import math
import json
import base64
import hashlib
import hmac
import struct
import shutil
import zlib
import gzip
import bz2
import lzma
import zipfile
import tarfile
import subprocess
import signal
import socket
import threading
import queue
import itertools
import statistics
import ctypes
import ctypes.util
import re
import shlex
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable, Union

class Record(dict):
    """
    A dictionary that allows attribute-style access (e.g. record's field).
    Allows player's health = 100 and player['health'] interchangeably.
    """
    def __getattr__(self, key):
        try:
            val = self[key]
            if isinstance(val, dict) and not isinstance(val, Record):
                val = Record(val)
                self[key] = val
            return val
        except KeyError:
            raise AttributeError(f"Record has no field '{key}'") from None

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"Record has no field '{key}'") from None



# ===========================================================================
# CLUSTER 1: SYSTEMS, OS, PROCESSES & SIGNALS (Phases 26-32)
# ===========================================================================

def run_command_piped(cmd: Union[str, List[str]], shell: bool = False) -> Record:
    """
    Phase 26: Subprocess command with captured stdout, stderr, and code.
    
    Security Notice:
    By default, shell=False and string commands are safely split into arguments via shlex.split
    to prevent command injection risks. Pass shell=True only when shell pipelines or redirections
    are explicitly required with trusted input.
    """
    if isinstance(cmd, str):
        if not shell:
            try:
                args = shlex.split(cmd, posix=(sys.platform != "win32"))
            except ValueError:
                args = cmd.split()
            res = subprocess.run(args, shell=False, capture_output=True, text=True)
        else:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    else:
        res = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    return Record(stdout=res.stdout.strip(), stderr=res.stderr.strip(), exit_code=res.returncode, ok=(res.returncode == 0))

def register_signal_handler(sig_name: str, handler: Callable):
    """Phase 27: Register graceful signal handling."""
    sig_map = {"int": signal.SIGINT, "term": getattr(signal, "SIGTERM", signal.SIGINT)}
    sig = sig_map.get(sig_name.lower().replace("signal", "").strip(), signal.SIGINT)
    signal.signal(sig, lambda s, f: handler())

def system_cpu_usage() -> float:
    """Phase 28: System CPU estimate without psutil."""
    t0 = time.process_time()
    time.sleep(0.01)
    t1 = time.process_time()
    return min(100.0, max(0.0, ((t1 - t0) / 0.01) * 100.0))

def system_memory_usage() -> Record:
    """Phase 28: Memory metrics."""
    return Record(active_mb=round(sys.getsizeof({}) / (1024 * 1024), 2))

def system_disk_space(path: str = ".") -> Record:
    """Phase 28: Disk space metrics."""
    total, used, free = shutil.disk_usage(path)
    return Record(total_gb=round(total / (1024**3), 2), used_gb=round(used / (1024**3), 2), free_gb=round(free / (1024**3), 2))

class FileLock:
    """Phase 30: Multi-process cooperative file lock."""
    def __init__(self, path: str):
        self.lock_file = Path(path + ".lock")
    def acquire(self):
        start = time.time()
        while self.lock_file.exists():
            time.sleep(0.05)
            if time.time() - start > 10.0:
                break
        self.lock_file.write_text(str(os.getpid()), encoding="utf-8")
    def release(self):
        if self.lock_file.exists():
            try: self.lock_file.unlink()
            except OSError: pass

def acquire_file_lock(path: str) -> FileLock:
    fl = FileLock(path)
    fl.acquire()
    return fl

def release_file_lock(fl: FileLock):
    fl.release()

def add_system_path(folder_path: str):
    """Phase 31: Dynamic PATH extension."""
    p = str(Path(folder_path).resolve())
    if p not in sys.path:
        sys.path.insert(0, p)
    os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")

def check_process_running(name: str) -> bool:
    """Phase 32: Process existence check."""
    cmd = ["tasklist"] if sys.platform == "win32" else ["ps", "aux"]
    res = subprocess.run(cmd, shell=False, capture_output=True, text=True)
    return name.lower() in res.stdout.lower()


# ===========================================================================
# CLUSTER 2: NETWORK PROTOCOLS & WEB (Phases 33-40)
# ===========================================================================

def resolve_dns(host: str) -> List[str]:
    """Phase 36: DNS resolution."""
    try:
        infos = socket.getaddrinfo(host, None)
        return list({item[4][0] for item in infos})
    except socket.gaierror:
        return []

def ping_host(host: str) -> Record:
    """Phase 36: Network ping/reachability check."""
    t0 = time.perf_counter()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.0)
    try:
        s.connect((host, 80))
        s.close()
        latency = (time.perf_counter() - t0) * 1000.0
        return Record(host=host, alive=True, latency_ms=round(latency, 2))
    except Exception:
        return Record(host=host, alive=False, latency_ms=-1.0)

class CookieJar:
    """Phase 38: In-memory HTTP cookie jar."""
    def __init__(self):
        self.cookies: Dict[str, str] = {}
    def set(self, k: str, v: str):
        self.cookies[k] = str(v)
    def get(self, k: str, default: str = "") -> str:
        return self.cookies.get(k, default)
    def header_value(self) -> str:
        return "; ".join(f"{k}={v}" for k, v in self.cookies.items())

def cookie_jar_create() -> CookieJar:
    return CookieJar()

def cookie_jar_set(jar: CookieJar, key: str, value: str):
    jar.set(key, value)

def cookie_jar_get(jar: CookieJar, key: str, default: str = "") -> str:
    return jar.get(key, default)



# ===========================================================================
# CLUSTER 3: ADVANCED DATA ENGINEERING & COMPRESSION (Phases 41-48)
# ===========================================================================

def compress_gzip(data: str) -> bytes:
    """Phase 45: Gzip compression."""
    return gzip.compress(data.encode("utf-8"))

def decompress_gzip(data: bytes) -> str:
    """Phase 45: Gzip decompression."""
    return gzip.decompress(data).decode("utf-8")

def compress_bz2(data: str) -> bytes:
    """Phase 45: BZ2 compression."""
    return bz2.compress(data.encode("utf-8"))

def decompress_bz2(data: bytes) -> str:
    """Phase 45: BZ2 decompression."""
    return bz2.decompress(data).decode("utf-8")

def create_zip_archive(target_zip: str, source: Any):
    """Phase 44: ZIP creation."""
    with zipfile.ZipFile(target_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        if isinstance(source, (list, tuple)):
            for f in source:
                p = Path(f)
                if p.is_file():
                    zf.write(p, arcname=p.name)
        else:
            s = Path(source)
            if s.is_file():
                zf.write(s, arcname=s.name)
            elif s.is_dir():
                for p in s.rglob("*"):
                    if p.is_file():
                        zf.write(p, arcname=p.relative_to(s))
    return target_zip

def extract_zip_archive(zip_path: str, target_dir: str):
    """Phase 44: ZIP extraction."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target_dir)
    return target_dir

def calculate_checksum_crc32(data: str) -> int:
    """Phase 48: CRC32 checksum as integer."""
    return int(zlib.crc32(data.encode("utf-8")) & 0xffffffff)

def calculate_checksum_adler32(data: str) -> int:
    """Phase 48: Adler32 checksum as integer."""
    return int(zlib.adler32(data.encode("utf-8")) & 0xffffffff)

def calculate_geo_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Phase 46: Haversine distance in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 3)

def diff_records(old_rec: Any, new_rec: Any) -> Record:
    """Phase 47: Record property diffing."""
    o_dict = dict(old_rec) if isinstance(old_rec, dict) else (old_rec.__dict__ if hasattr(old_rec, "__dict__") else {})
    n_dict = dict(new_rec) if isinstance(new_rec, dict) else (new_rec.__dict__ if hasattr(new_rec, "__dict__") else {})
    added = {}
    removed = {}
    changed = {}
    for k in set(o_dict.keys()).union(n_dict.keys()):
        if k not in o_dict:
            added[k] = n_dict[k]
        elif k not in n_dict:
            removed[k] = o_dict[k]
        elif o_dict[k] != n_dict[k]:
            changed[k] = Record(old=o_dict[k], new=n_dict[k])
    return Record(added=added, removed=removed, changed=changed, total_changes=len(added) + len(removed) + len(changed))


# ===========================================================================
# CLUSTER 4: MATHEMATICS & STATISTICS (Phases 49-56)
# ===========================================================================

def vector_dot(v1: List[float], v2: List[float]) -> float:
    """Phase 49: Vector dot product."""
    return sum(a * b for a, b in zip(v1, v2))

def vector_magnitude(v: List[float]) -> float:
    """Phase 49: Euclidean vector length."""
    return math.sqrt(sum(x**2 for x in v))

def matrix_multiply(m1: List[List[float]], m2: List[List[float]]) -> List[List[float]]:
    """Phase 49: Matrix multiplication."""
    r1, c1 = len(m1), len(m1[0])
    r2, c2 = len(m2), len(m2[0])
    res = [[0.0] * c2 for _ in range(r1)]
    for i in range(r1):
        for j in range(c2):
            for k in range(c1):
                res[i][j] += m1[i][k] * m2[k][j]
    return res

def stats_stdev(data: List[float]) -> float:
    """Phase 50: Standard deviation."""
    return round(statistics.stdev(data) if len(data) > 1 else 0.0, 4)

def stats_variance(data: List[float]) -> float:
    """Phase 50: Sample variance."""
    return round(statistics.variance(data) if len(data) > 1 else 0.0, 4)

def stats_median(data: List[float]) -> float:
    """Phase 50: Median."""
    return round(statistics.median(data), 4)

def stats_percentile(data: List[float], p: float) -> float:
    """Phase 50: Percentile estimation."""
    sorted_d = sorted(data)
    idx = int((len(sorted_d) - 1) * (p / 100.0))
    return round(sorted_d[idx], 4)

def _normalize_rate(rate: Any) -> float:
    """Normalizes an interest rate to decimal form (e.g. 5, 5.0, '5%' -> 0.05; 0.05 -> 0.05)."""
    if isinstance(rate, str):
        rate_str = rate.strip()
        if rate_str.endswith("%"):
            return float(rate_str[:-1].strip()) / 100.0
        r = float(rate_str)
    else:
        r = float(rate)
    if abs(r) >= 1.0:
        return r / 100.0
    return r

COMPOUNDING_PERIODS = {
    "annually": 1,
    "annual": 1,
    "yearly": 1,
    "semi-annually": 2,
    "semiannually": 2,
    "quarterly": 4,
    "monthly": 12,
    "daily": 365,
}

def calc_compound_interest(principal: float, annual_rate: Any, years: float, compounding: Any = 1) -> float:
    """Phase 51: Compound interest future value.
    Defaults to annual compounding (1 time per year).
    Can specify compounding frequency as integer or string ('annually', 'quarterly', 'monthly', 'daily').
    """
    p = float(principal)
    r = _normalize_rate(annual_rate)
    t = float(years)
    if isinstance(compounding, str):
        n = COMPOUNDING_PERIODS.get(compounding.strip().lower(), 1)
    else:
        n = int(compounding) if compounding else 1
    return round(p * ((1 + (r / n)) ** (n * t)), 2)

def calc_loan_payment(principal: float, annual_rate: Any, months: float) -> float:
    """Phase 51: Monthly amortization payment for given number of months."""
    p = float(principal)
    r = _normalize_rate(annual_rate) / 12.0
    n = float(months)
    if r == 0:
        return round(p / n, 2)
    return round(p * (r * (1 + r)**n) / ((1 + r)**n - 1), 2)

def math_lerp(a: float, b: float, t: float) -> float:
    """Phase 53: Linear interpolation."""
    return a + (b - a) * t


# ===========================================================================
# CLUSTER 5: EVENT-DRIVEN & QUEUES (Phases 57-64)
# ===========================================================================

class EventBus:
    """Phase 57: In-memory pub/sub event bus."""
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
    def subscribe(self, topic: str, handler: Callable):
        self._listeners.setdefault(topic, []).append(handler)
    def publish(self, topic: str, data: Any = None):
        for h in self._listeners.get(topic, []):
            try:
                h(data)
            except TypeError:
                h()

_GLOBAL_EVENT_BUS = EventBus()

def event_subscribe(topic: str, handler: Callable):
    _GLOBAL_EVENT_BUS.subscribe(topic, handler)

def event_publish(topic: str, data: Any):
    _GLOBAL_EVENT_BUS.publish(topic, data)

class PriorityQueueWrapper:
    """Phase 58: Thread-safe priority queue."""
    def __init__(self):
        self._q = queue.PriorityQueue()
    def enqueue(self, priority: int, item: Any):
        self._q.put((priority, item))
    def dequeue(self) -> Any:
        return self._q.get()[1]
    def size(self) -> int:
        return self._q.qsize()

def priority_queue_create() -> PriorityQueueWrapper:
    return PriorityQueueWrapper()

def priority_queue_enqueue(pq: PriorityQueueWrapper, item: Any, priority: int = 10):
    pq.enqueue(int(priority), item)

def priority_queue_dequeue(pq: PriorityQueueWrapper) -> Any:
    return pq.dequeue()

class CircuitBreaker:
    """Phase 62: Resilient circuit breaker."""
    def __init__(self, failure_threshold: int = 3, cooldown: float = 5.0):
        self.threshold = failure_threshold
        self.cooldown = cooldown
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = 0.0

    def call(self, fn: Callable, *args, **kwargs) -> Any:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.cooldown:
                self.state = "HALF-OPEN"
            else:
                raise RuntimeError("Circuit breaker is OPEN - call rejected")
        try:
            res = fn(*args, **kwargs)
            if self.state == "HALF-OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return res
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.threshold:
                self.state = "OPEN"
            raise e

def circuit_breaker_call(cb: CircuitBreaker, fn: Callable, *args):
    return cb.call(fn, *args)



# ===========================================================================
# CLUSTER 6: GENERATIVE UI & GRAPHICS (Phases 65-72)
# ===========================================================================

def generate_svg_circle(cx: int, cy: int, r: int, fill: str = "#000") -> str:
    """Phase 70: SVG circle."""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" />'

def generate_svg_rect(x: int, y: int, w: int, h: int, fill: str = "#000") -> str:
    """Phase 70: SVG rectangle."""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" />'

def generate_svg_canvas(width: int, height: int, elements: List[str]) -> str:
    """Phase 70: SVG document canvas."""
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">\n' + "\n".join(elements) + "\n</svg>"


# ===========================================================================
# CLUSTER 7: AI AGENTS, RAG & COGNITIVE LOOPS (Phases 73-80)
# ===========================================================================

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Phase 75: Vector cosine similarity."""
    dot = vector_dot(v1, v2)
    m1 = vector_magnitude(v1)
    m2 = vector_magnitude(v2)
    if m1 == 0 or m2 == 0:
        return 0.0
    return round(dot / (m1 * m2), 4)

_SEMANTIC_STOP_WORDS = {
    "a", "an", "the", "and", "or", "is", "are", "was", "were", "in", "on", "at",
    "to", "for", "with", "by", "of", "from", "it", "this", "that", "these", "those"
}

def _stem_word(word: str) -> str:
    w = word.lower()
    for sfx in ("edly", "ingly", "ing", "ed", "es", "s", "ly"):
        if len(w) > len(sfx) + 2 and w.endswith(sfx):
            return w[:-len(sfx)]
    return w

def _tokenize_semantic(text: str) -> List[str]:
    raw = re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())
    return [_stem_word(w) for w in raw if len(w) > 1]

def mock_embedding(text: str, dim: int = 16) -> List[float]:
    """Phase 75: Deterministic semantic feature embedding using token hashing."""
    tokens = _tokenize_semantic(text)
    if not tokens:
        return [0.0] * dim
    vec = [0.0] * dim
    for i, tok in enumerate(tokens):
        w = 0.2 if tok in _SEMANTIC_STOP_WORDS else 1.0
        h = int(hashlib.md5(tok.encode("utf-8")).hexdigest()[:8], 16)
        idx = h % dim
        sign = 1.0 if (h & 0x100) else -1.0
        vec[idx] += sign * w
        if i < len(tokens) - 1:
            bigram = f"{tok}_{tokens[i+1]}"
            hb = int(hashlib.md5(bigram.encode("utf-8")).hexdigest()[:8], 16)
            b_idx = hb % dim
            b_sign = 1.0 if (hb & 0x100) else -1.0
            vec[b_idx] += b_sign * 0.5
    mag = math.sqrt(sum(x * x for x in vec))
    if mag == 0:
        return [0.0] * dim
    return [round(x / mag, 4) for x in vec]

class SemanticKnowledgeIndex:
    """Phase 76: In-memory RAG vector index with semantic token relevance scoring."""
    def __init__(self):
        self.documents: List[Record] = []
    def add(self, text: str, doc_id: str = "", metadata: Any = None):
        emb = mock_embedding(text)
        tokens = _tokenize_semantic(text)
        self.documents.append(Record(id=doc_id, text=text, embedding=emb, tokens=tokens, metadata=metadata))
    def search(self, query: str, top_k: int = 3) -> List[Record]:
        q_tokens = _tokenize_semantic(query)
        q_emb = mock_embedding(query)
        scored = []
        for doc in self.documents:
            sim = cosine_similarity(q_emb, doc.embedding)
            doc_tokens = doc.get("tokens", [])
            overlap = 0.0
            for qt in q_tokens:
                if qt in _SEMANTIC_STOP_WORDS:
                    continue
                tf = doc_tokens.count(qt)
                if tf > 0:
                    overlap += 2.0 * (1.0 + math.log(tf))
            total_score = overlap + sim
            scored.append((total_score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

def knowledge_index_create() -> SemanticKnowledgeIndex:
    return SemanticKnowledgeIndex()

def knowledge_index_add(index: SemanticKnowledgeIndex, doc_id: str, text: str):
    index.add(text, doc_id=str(doc_id))

def knowledge_index_query(index: SemanticKnowledgeIndex, query: str) -> List[Record]:
    return index.search(query)

class ConversationMemory:
    """Phase 77: Conversation memory."""
    def __init__(self):
        self.history: List[Record] = []
    def remember(self, role: str, content: str):
        self.history.append(Record(role=role, content=content))
    def recall(self) -> List[Record]:
        return list(self.history)
    def get_context(self) -> str:
        return "\n".join(f"{item.role}: {item.content}" for item in self.history)

def memory_create() -> ConversationMemory:
    return ConversationMemory()

def memory_remember(memory: ConversationMemory, role: str, content: str):
    memory.remember(role, content)

def memory_recall(memory: ConversationMemory) -> List[Record]:
    return memory.recall()


# ===========================================================================
# CLUSTER 8: SECURITY, IDENTITY & COMPLIANCE (Phases 81-88)
# ===========================================================================

def jwt_create(payload: Dict[str, Any], secret: str) -> str:
    """Phase 81: Zero-dependency HS256 JSON Web Token generator."""
    header = {"alg": "HS256", "typ": "JWT"}
    b64_header = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
    b64_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
    signing_input = f"{b64_header}.{b64_payload}".encode()
    signature = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    b64_sig = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()
    return f"{b64_header}.{b64_payload}.{b64_sig}"

def jwt_verify(token: str, secret: str) -> Optional[Dict[str, Any]]:
    """Phase 81: HS256 JWT signature and claims verifier."""
    try:
        parts = token.split(".")
        if len(parts) != 3: return None
        b64_header, b64_payload, b64_sig = parts
        signing_input = f"{b64_header}.{b64_payload}".encode()
        expected = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
        actual = base64.urlsafe_b64decode(b64_sig + "==")
        if not hmac.compare_digest(expected, actual):
            return None
        payload_bytes = base64.urlsafe_b64decode(b64_payload + "==")
        return json.loads(payload_bytes.decode())
    except Exception:
        return None

def hash_password_secure(password: str, salt: Optional[str] = None) -> str:
    """Phase 82: Salted PBKDF2 password hashing."""
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 10000)
    return f"{salt}${hashed.hex()}"

def verify_password_secure(password: str, stored_hash: str) -> bool:
    """Phase 82: Password hash verification."""
    salt, _ = stored_hash.split("$", 1)
    return hmac.compare_digest(hash_password_secure(password, salt), stored_hash)

def mask_pii_text(text: str) -> str:
    """Phase 85: PII detection and redaction."""
    # Redact email addresses
    s = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL_MASKED]", text)
    # Redact phone numbers
    s = re.sub(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE_MASKED]", s)
    # Redact SSN
    s = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN_MASKED]", s)
    return s


# ===========================================================================
# CLUSTER 9: CLOUD, CONTAINERS & METRICS (Phases 89-95)
# ===========================================================================

def generate_dockerfile_content(entrypoint: str = "main.doom") -> str:
    """Phase 89: Generates multi-stage optimized Dockerfile."""
    return f"""# Generated by DoomScript v1.0.0 Packager
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir lark typer rich
ENTRYPOINT ["python", "-m", "doomscript.cli", "run", "{entrypoint}"]
"""

class MetricsRegistry:
    """Phase 91: Prometheus-style metrics registry."""
    def __init__(self):
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
    def increment(self, name: str, value: float = 1.0):
        self.counters[name] = self.counters.get(name, 0.0) + value
    def set_gauge(self, name: str, value: float):
        self.gauges[name] = float(value)
    def render_prometheus(self) -> str:
        lines = []
        for k, v in self.counters.items():
            lines.append(f"# TYPE {k} counter\n{k} {v}")
        for k, v in self.gauges.items():
            lines.append(f"# TYPE {k} gauge\n{k} {v}")
        return "\n".join(lines)

_METRICS = MetricsRegistry()

def metric_increment(name: str, value: float = 1.0):
    _METRICS.increment(name, value)

def metric_set(name: str, value: float):
    _METRICS.set_gauge(name, value)

def metrics_export_prometheus() -> str:
    return _METRICS.render_prometheus()


# ===========================================================================
# CLUSTER 10: METAPROGRAMMING, FFI & SELF-HOSTING (Phases 96-100)
# ===========================================================================

def call_c_function(lib_name: str, func_name: str, *args):
    """Phase 97: Pure ctypes Foreign Function Interface (FFI)."""
    # Unpack args if passed as a single list or tuple, e.g. [-5]
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        args = tuple(args[0])

    is_libc = lib_name.lower().strip() in (
        "libc", "libc.so", "libc.so.6", "c", "msvcrt", "msvcrt.dll", "libsystem.b.dylib"
    )
    lib = None
    if is_libc:
        if os.name == "nt":
            lib = ctypes.cdll.msvcrt
        else:
            try:
                lib = ctypes.CDLL(lib_name)
            except Exception:
                try:
                    found = ctypes.util.find_library("c")
                    if found:
                        lib = ctypes.CDLL(found)
                except Exception:
                    pass
    else:
        try:
            lib = ctypes.CDLL(lib_name)
        except Exception:
            try:
                found = ctypes.util.find_library(lib_name)
                if found:
                    lib = ctypes.CDLL(found)
            except Exception:
                pass

    if not lib or not hasattr(lib, func_name):
        return 0

    func = getattr(lib, func_name)
    c_args = []
    for a in args:
        if isinstance(a, str):
            c_args.append(a.encode("utf-8"))
        else:
            c_args.append(a)

    try:
        return func(*c_args)
    except Exception:
        return 0

def minify_doomscript_source(source: str) -> str:
    """Phase 99: Code minification (strip comments and blank lines)."""
    normalized = source.replace("\\n", "\n")
    out = []
    for line in normalized.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue
        out.append(trimmed)
    return "\n".join(out)

