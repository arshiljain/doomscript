"""Cache Domain Runtime: LRU, LFU, TTL caches, Bloom Filters, and Consistent Hashing Rings."""
import hashlib
import time
from collections import OrderedDict, defaultdict
from typing import Any, Dict, List, Optional

class LRUCache:
    def __init__(self, capacity: int = 128):
        self.capacity = max(1, int(capacity))
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    def get(self, key: Any) -> Optional[Any]:
        if key in self.cache:
            self.hits += 1
            self.cache.move_to_end(key)
            return self.cache[key]
        self.misses += 1
        return None
    def set(self, key: Any, value: Any) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
                self.evictions += 1
        self.cache[key] = value

class LFUCache:
    def __init__(self, capacity: int = 128):
        self.capacity = max(1, int(capacity))
        self.vals = {}
        self.counts = {}
        self.count_lists = defaultdict(OrderedDict)
        self.min_count = 0
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    def get(self, key: Any) -> Optional[Any]:
        if key not in self.vals:
            self.misses += 1
            return None
        self.hits += 1
        c = self.counts[key]
        self.counts[key] = c + 1
        del self.count_lists[c][key]
        if not self.count_lists[c] and c == self.min_count:
            self.min_count += 1
        self.count_lists[c + 1][key] = True
        return self.vals[key]
    def set(self, key: Any, value: Any) -> None:
        if key in self.vals:
            self.vals[key] = value
            self.get(key)
            return
        if len(self.vals) >= self.capacity:
            evict_key, _ = self.count_lists[self.min_count].popitem(last=False)
            del self.vals[evict_key]
            del self.counts[evict_key]
            self.evictions += 1
        self.vals[key] = value
        self.counts[key] = 1
        self.count_lists[1][key] = True
        self.min_count = 1

class BloomFilter:
    def __init__(self, size: int = 1000, num_hashes: int = 3):
        self.size = max(10, int(size))
        self.num_hashes = max(1, int(num_hashes))
        self.bits = [False] * self.size
    def _hashes(self, item: Any) -> List[int]:
        s = str(item).encode("utf-8")
        h1 = int(hashlib.md5(s).hexdigest(), 16)
        h2 = int(hashlib.sha256(s).hexdigest(), 16)
        return [(h1 + i * h2) % self.size for i in range(self.num_hashes)]
    def add(self, item: Any) -> None:
        for idx in self._hashes(item):
            self.bits[idx] = True
    def check(self, item: Any) -> bool:
        return all(self.bits[idx] for idx in self._hashes(item))

class ConsistentHashRing:
    def __init__(self, replicas: int = 3):
        self.replicas = max(1, int(replicas))
        self.ring = {}
        self.sorted_keys = []
    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
    def add_node(self, node: str) -> None:
        for i in range(self.replicas):
            k = self._hash(f"{node}:{i}")
            self.ring[k] = node
            self.sorted_keys.append(k)
        self.sorted_keys.sort()
    def get_node(self, key: str) -> Optional[str]:
        if not self.ring:
            return None
        h = self._hash(str(key))
        for k in self.sorted_keys:
            if h <= k:
                return self.ring[k]
        return self.ring[self.sorted_keys[0]]

def cache_create_lru(capacity: int = 128) -> LRUCache:
    return LRUCache(capacity)

def cache_create_lfu(capacity: int = 128) -> LFUCache:
    return LFUCache(capacity)

def cache_store(c: Any, key: Any, value: Any) -> None:
    if hasattr(c, "set"):
        c.set(key, value)
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
    return bf.check(item)

def cache_ring_create(replicas: int = 3) -> ConsistentHashRing:
    return ConsistentHashRing(replicas)

def cache_ring_add_node(ring: ConsistentHashRing, node: str) -> None:
    ring.add_node(str(node))

def cache_ring_get_node(ring: ConsistentHashRing, key: str) -> Optional[str]:
    return ring.get_node(str(key))

def cache_stats(cache_obj: Any) -> Dict[str, Any]:
    hits = getattr(cache_obj, "hits", 0)
    misses = getattr(cache_obj, "misses", 0)
    evictions = getattr(cache_obj, "evictions", 0)
    total = hits + misses
    ratio = hits / total if total > 0 else 0.0
    return {"hits": hits, "misses": misses, "evictions": evictions, "hit_ratio": round(ratio, 4)}
