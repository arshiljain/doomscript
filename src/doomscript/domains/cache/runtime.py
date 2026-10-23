"""Cache Domain Runtime: High performance caching algorithms, eviction policies, Bloom filters, and cache stampede protection."""
import time
import math
import heapq
import random
import hashlib
from typing import Dict, Any, Optional, List, Tuple, Set
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. CLASSIC LRU & LFU CACHES
# ============================================================================

class LRUCache:
    """Least Recently Used (LRU) Cache implemented with linked tracking."""
    def __init__(self, capacity: int = 128):
        self.capacity = max(1, int(capacity))
        self.cache: Dict[str, Any] = {}
        self.order: List[str] = []
        self.hits = 0
        self.misses = 0

    def get(self, key: Any, default: Any = None) -> Any:
        k = str(key)
        if k in self.cache:
            self.hits += 1
            self.order.remove(k)
            self.order.append(k)
            return self.cache[k]
        self.misses += 1
        return default

    def put(self, key: Any, value: Any) -> None:
        k = str(key)
        if k in self.cache:
            self.order.remove(k)
        elif len(self.cache) >= self.capacity:
            oldest = self.order.pop(0)
            del self.cache[oldest]
        self.cache[k] = value
        self.order.append(k)

    def stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        ratio = self.hits / total if total > 0 else 0.0
        return {"hits": self.hits, "misses": self.misses, "hit_ratio": round(ratio, 4), "size": len(self.cache), "capacity": self.capacity}

class LFUCache:
    """Least Frequently Used (LFU) Cache with frequency tracking."""
    def __init__(self, capacity: int = 128):
        self.capacity = max(1, int(capacity))
        self.cache: Dict[str, Any] = {}
        self.freqs: Dict[str, int] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: Any, default: Any = None) -> Any:
        k = str(key)
        if k in self.cache:
            self.hits += 1
            self.freqs[k] = self.freqs.get(k, 0) + 1
            return self.cache[k]
        self.misses += 1
        return default

    def put(self, key: Any, value: Any) -> None:
        k = str(key)
        if k in self.cache:
            self.cache[k] = value
            self.freqs[k] = self.freqs.get(k, 0) + 1
            return
        if len(self.cache) >= self.capacity:
            min_k = min(self.freqs.items(), key=lambda x: x[1])[0]
            del self.cache[min_k]
            del self.freqs[min_k]
        self.cache[k] = value
        self.freqs[k] = 1

    def stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        ratio = self.hits / total if total > 0 else 0.0
        return {"hits": self.hits, "misses": self.misses, "hit_ratio": round(ratio, 4), "size": len(self.cache), "capacity": self.capacity}

# ============================================================================
# 2. ADAPTIVE REPLACEMENT CACHE (ARC) & 2Q
# ============================================================================

class ARCCache:
    """Adaptive Replacement Cache (ARC) self-tuning between recency (T1) and frequency (T2)."""
    def __init__(self, capacity: int = 128):
        self.c = max(1, int(capacity))
        self.p = 0
        self.t1: List[str] = []
        self.b1: List[str] = []
        self.t2: List[str] = []
        self.b2: List[str] = []
        self.cache: Dict[str, Any] = {}
        self.hits = 0
        self.misses = 0

    def _replace(self, k: str) -> None:
        if self.t1 and ((len(self.t1) > self.p) or (k in self.b2 and len(self.t1) == self.p)):
            del_key = self.t1.pop(0)
            self.b1.append(del_key)
            if del_key in self.cache:
                del self.cache[del_key]
        else:
            if self.t2:
                del_key = self.t2.pop(0)
                self.b2.append(del_key)
                if del_key in self.cache:
                    del self.cache[del_key]

    def get(self, key: Any, default: Any = None) -> Any:
        k = str(key)
        if k in self.cache:
            self.hits += 1
            if k in self.t1:
                self.t1.remove(k)
                self.t2.append(k)
            elif k in self.t2:
                self.t2.remove(k)
                self.t2.append(k)
            return self.cache[k]
        self.misses += 1
        return default

    def put(self, key: Any, value: Any) -> None:
        k = str(key)
        if k in self.cache:
            self.cache[k] = value
            if k in self.t1:
                self.t1.remove(k)
                self.t2.append(k)
            return
        if k in self.b1:
            delta = max(1, len(self.b2) // max(1, len(self.b1)))
            self.p = min(self.c, self.p + delta)
            self._replace(k)
            self.b1.remove(k)
            self.t2.append(k)
            self.cache[k] = value
            return
        if k in self.b2:
            delta = max(1, len(self.b1) // max(1, len(self.b2)))
            self.p = max(0, self.p - delta)
            self._replace(k)
            self.b2.remove(k)
            self.t2.append(k)
            self.cache[k] = value
            return
        if len(self.t1) + len(self.b1) == self.c:
            if len(self.t1) < self.c:
                self.b1.pop(0)
                self._replace(k)
            else:
                del_k = self.t1.pop(0)
                if del_k in self.cache:
                    del self.cache[del_k]
        elif len(self.t1) + len(self.t2) + len(self.b1) + len(self.b2) >= self.c:
            if len(self.t1) + len(self.t2) + len(self.b1) + len(self.b2) == 2 * self.c:
                if self.b2:
                    self.b2.pop(0)
            self._replace(k)
        self.t1.append(k)
        self.cache[k] = value

    def stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        ratio = self.hits / total if total > 0 else 0.0
        return {"hits": self.hits, "misses": self.misses, "hit_ratio": round(ratio, 4), "p_target": self.p, "size": len(self.cache)}

class TwoQueueCache:
    """Two-Queue (2Q) algorithm separating one-time scans from frequent accesses."""
    def __init__(self, capacity: int = 128, kin_ratio: float = 0.25):
        self.capacity = max(1, int(capacity))
        self.kin_cap = max(1, int(self.capacity * kin_ratio))
        self.a1in: List[str] = []
        self.a1out: List[str] = []
        self.am: List[str] = []
        self.cache: Dict[str, Any] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: Any, default: Any = None) -> Any:
        k = str(key)
        if k in self.cache:
            self.hits += 1
            if k in self.am:
                self.am.remove(k)
                self.am.append(k)
            return self.cache[k]
        self.misses += 1
        return default

    def put(self, key: Any, value: Any) -> None:
        k = str(key)
        if k in self.cache:
            self.cache[k] = value
            if k in self.am:
                self.am.remove(k)
                self.am.append(k)
            return
        if k in self.a1out:
            self.a1out.remove(k)
            if len(self.am) >= self.capacity - self.kin_cap and self.am:
                del_k = self.am.pop(0)
                if del_k in self.cache:
                    del self.cache[del_k]
            self.am.append(k)
            self.cache[k] = value
            return
        if len(self.a1in) >= self.kin_cap and self.a1in:
            oldest = self.a1in.pop(0)
            if oldest in self.cache:
                del self.cache[oldest]
            self.a1out.append(oldest)
            if len(self.a1out) > self.capacity:
                self.a1out.pop(0)
        self.a1in.append(k)
        self.cache[k] = value

# ============================================================================
# 3. SECOND-CHANCE / CLOCK & SEGMENTED LRU
# ============================================================================

class ClockCache:
    """Clock (Second-Chance) circular replacement algorithm."""
    def __init__(self, capacity: int = 128):
        self.capacity = max(1, int(capacity))
        self.keys: List[Optional[str]] = [None] * self.capacity
        self.ref_bits: List[int] = [0] * self.capacity
        self.cache: Dict[str, Any] = {}
        self.hand = 0
        self.hits = 0
        self.misses = 0

    def get(self, key: Any, default: Any = None) -> Any:
        k = str(key)
        if k in self.cache:
            self.hits += 1
            idx = self.keys.index(k)
            self.ref_bits[idx] = 1
            return self.cache[k]
        self.misses += 1
        return default

    def put(self, key: Any, value: Any) -> None:
        k = str(key)
        if k in self.cache:
            self.cache[k] = value
            idx = self.keys.index(k)
            self.ref_bits[idx] = 1
            return
        while True:
            curr_k = self.keys[self.hand]
            if curr_k is None:
                self.keys[self.hand] = k
                self.ref_bits[self.hand] = 1
                self.cache[k] = value
                self.hand = (self.hand + 1) % self.capacity
                break
            if self.ref_bits[self.hand] == 1:
                self.ref_bits[self.hand] = 0
                self.hand = (self.hand + 1) % self.capacity
            else:
                del self.cache[curr_k]
                self.keys[self.hand] = k
                self.ref_bits[self.hand] = 1
                self.cache[k] = value
                self.hand = (self.hand + 1) % self.capacity
                break

class SegmentedLRUCache:
    """Segmented LRU with probationary and protected segments."""
    def __init__(self, capacity: int = 128, protected_ratio: float = 0.8):
        self.capacity = max(2, int(capacity))
        self.protected_cap = max(1, int(self.capacity * protected_ratio))
        self.probationary_cap = self.capacity - self.protected_cap
        self.probationary: List[str] = []
        self.protected: List[str] = []
        self.cache: Dict[str, Any] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: Any, default: Any = None) -> Any:
        k = str(key)
        if k in self.cache:
            self.hits += 1
            if k in self.protected:
                self.protected.remove(k)
                self.protected.append(k)
            elif k in self.probationary:
                self.probationary.remove(k)
                if len(self.protected) >= self.protected_cap:
                    demoted = self.protected.pop(0)
                    self.probationary.append(demoted)
                self.protected.append(k)
            return self.cache[k]
        self.misses += 1
        return default

    def put(self, key: Any, value: Any) -> None:
        k = str(key)
        if k in self.cache:
            self.cache[k] = value
            self.get(k)
            return
        if len(self.probationary) >= self.probationary_cap:
            evicted = self.probationary.pop(0)
            if evicted in self.cache:
                del self.cache[evicted]
        self.probationary.append(k)
        self.cache[k] = value

# ============================================================================
# 4. TTL CACHE & PROBABILISTIC EARLY EXPIRATION (XFETCH)
# ============================================================================

class TTLCache:
    """Time-To-Live (TTL) Cache with explicit expiration times."""
    def __init__(self, default_ttl_sec: float = 60.0):
        self.default_ttl = float(default_ttl_sec)
        self.cache: Dict[str, Tuple[Any, float]] = {}

    def get(self, key: Any, default: Any = None) -> Any:
        k = str(key)
        now = time.time()
        if k in self.cache:
            val, exp = self.cache[k]
            if now < exp:
                return val
            del self.cache[k]
        return default

    def put(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        k = str(key)
        duration = float(ttl) if ttl is not None else self.default_ttl
        self.cache[k] = (value, time.time() + duration)

    def cleanup(self) -> int:
        now = time.time()
        expired = [k for k, (_, exp) in self.cache.items() if now >= exp]
        for k in expired:
            del self.cache[k]
        return len(expired)

def cache_xfetch_should_recompute(delta_computation_time: float, beta: float, expiry_timestamp: float, now: Optional[float] = None) -> bool:
    """XFetch probabilistic early cache expiration to prevent cache stampedes."""
    current = now if now is not None else time.time()
    r = random.random()
    if r <= 0.0:
        return True
    threshold = -delta_computation_time * beta * math.log(r)
    return (current - threshold) >= expiry_timestamp

# ============================================================================
# 5. BLOOM FILTER & CONSISTENT HASH RING
# ============================================================================

class BloomFilter:
    """Space-efficient probabilistic data structure for set membership testing."""
    def __init__(self, size: int = 1000, num_hashes: int = 3):
        self.size = max(10, int(size))
        self.num_hashes = max(1, int(num_hashes))
        self.bits = [0] * self.size
        self.count = 0

    def add(self, item: Any) -> None:
        s = str(item)
        for i in range(self.num_hashes):
            idx = int(hashlib.md5(f"{s}:{i}".encode()).hexdigest(), 16) % self.size
            self.bits[idx] = 1
        self.count += 1

    def contains(self, item: Any) -> bool:
        s = str(item)
        for i in range(self.num_hashes):
            idx = int(hashlib.md5(f"{s}:{i}".encode()).hexdigest(), 16) % self.size
            if not self.bits[idx]:
                return False
        return True

    def false_positive_rate(self) -> float:
        m = self.size
        k = self.num_hashes
        n = self.count
        return round((1.0 - math.exp(-k * n / m)) ** k, 4)

class ConsistentHashRing:
    """Consistent hashing ring with virtual node replication for distributed sharding."""
    def __init__(self, replicas: int = 3):
        self.replicas = max(1, int(replicas))
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []

    def add_node(self, node: str) -> None:
        for i in range(self.replicas):
            key = int(hashlib.sha256(f"{node}:{i}".encode()).hexdigest()[:8], 16)
            self.ring[key] = node
            if key not in self.sorted_keys:
                self.sorted_keys.append(key)
        self.sorted_keys.sort()

    def remove_node(self, node: str) -> None:
        to_del = [k for k, v in self.ring.items() if v == node]
        for k in to_del:
            del self.ring[k]
            self.sorted_keys.remove(k)

    def get_node(self, key: str) -> Optional[str]:
        if not self.ring:
            return None
        h = int(hashlib.sha256(str(key).encode()).hexdigest()[:8], 16)
        for node_key in self.sorted_keys:
            if h <= node_key:
                return self.ring[node_key]
        return self.ring[self.sorted_keys[0]]

# ============================================================================
# 6. STANDALONE HELPER FUNCTIONS
# ============================================================================

def cache_create_lru(capacity: int = 128) -> LRUCache:
    return LRUCache(capacity)

def cache_create_lfu(capacity: int = 128) -> LFUCache:
    return LFUCache(capacity)

def cache_create_arc(capacity: int = 128) -> ARCCache:
    return ARCCache(capacity)

def cache_create_2q(capacity: int = 128) -> TwoQueueCache:
    return TwoQueueCache(capacity)

def cache_create_clock(capacity: int = 128) -> ClockCache:
    return ClockCache(capacity)

def cache_create_slru(capacity: int = 128) -> SegmentedLRUCache:
    return SegmentedLRUCache(capacity)

def cache_create_ttl(default_ttl: float = 60.0) -> TTLCache:
    return TTLCache(default_ttl)

def cache_store(c: Any, key: Any, value: Any) -> None:
    if hasattr(c, "put"):
        c.put(key, value)
    elif isinstance(c, dict):
        c[key] = value

def cache_fetch(c: Any, key: Any) -> Any:
    if hasattr(c, "get"):
        return c.get(key)
    elif isinstance(c, dict):
        return c.get(key)
    return None

def cache_create_bloom(size: int = 1000, num_hashes: int = 3) -> BloomFilter:
    return BloomFilter(size, num_hashes)

def cache_bloom_add(bf: BloomFilter, item: Any) -> None:
    bf.add(item)

def cache_bloom_check(bf: BloomFilter, item: Any) -> bool:
    return bf.contains(item)

def cache_ring_create(replicas: int = 3) -> ConsistentHashRing:
    return ConsistentHashRing(replicas)

def cache_ring_add_node(ring: ConsistentHashRing, node: str) -> None:
    ring.add_node(node)

def cache_ring_get_node(ring: ConsistentHashRing, key: str) -> Optional[str]:
    return ring.get_node(key)

def cache_stats(cache_obj: Any) -> Dict[str, Any]:
    if hasattr(cache_obj, "stats"):
        return cache_obj.stats()
    elif isinstance(cache_obj, dict):
        return {"size": len(cache_obj)}
    return {}

# ============================================================================
# 7. DOMAIN RUNTIME
# ============================================================================

class CacheRuntime(DomainRuntime):
    """Unified runtime bridge for the Cache computational domain."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def new_lru(self, capacity: int = 128) -> LRUCache:
        return LRUCache(capacity)
    def new_lfu(self, capacity: int = 128) -> LFUCache:
        return LFUCache(capacity)
    def new_arc(self, capacity: int = 128) -> ARCCache:
        return ARCCache(capacity)
    def new_2q(self, capacity: int = 128) -> TwoQueueCache:
        return TwoQueueCache(capacity)
    def new_clock(self, capacity: int = 128) -> ClockCache:
        return ClockCache(capacity)
    def new_slru(self, capacity: int = 128) -> SegmentedLRUCache:
        return SegmentedLRUCache(capacity)
    def new_ttl(self, ttl: float = 60.0) -> TTLCache:
        return TTLCache(ttl)
    def new_bloom(self, size: int = 1000, hashes: int = 3) -> BloomFilter:
        return BloomFilter(size, hashes)
    def new_ring(self, replicas: int = 3) -> ConsistentHashRing:
        return ConsistentHashRing(replicas)
    def should_recompute(self, delta: float, beta: float, expiry: float) -> bool:
        return cache_xfetch_should_recompute(delta, beta, expiry)
