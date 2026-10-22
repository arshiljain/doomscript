"""Cache Domain Runtime: LRU, LFU, TTL expiration, and Bloom filter."""
import time
from collections import OrderedDict
from typing import Any, Dict, Optional, List

class LRUCache:
    def __init__(self, capacity: int = 100):
        self.capacity = int(capacity)
        self.cache = OrderedDict()
    def get(self, key: Any) -> Optional[Any]:
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]
    def put(self, key: Any, val: Any) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = val
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
    def size(self) -> int:
        return len(self.cache)

class BloomFilter:
    def __init__(self, size: int = 1024, hash_count: int = 3):
        self.size = int(size)
        self.hash_count = int(hash_count)
        self.bit_array = [0] * self.size
    def add(self, item: str) -> None:
        for i in range(self.hash_count):
            idx = (hash(str(item) + str(i))) % self.size
            self.bit_array[idx] = 1
    def contains(self, item: str) -> bool:
        for i in range(self.hash_count):
            idx = (hash(str(item) + str(i))) % self.size
            if not self.bit_array[idx]:
                return False
        return True

def cache_create_lru(capacity: int = 100) -> LRUCache:
    return LRUCache(capacity)

def cache_store(cache: LRUCache, key: Any, val: Any) -> None:
    if hasattr(cache, "put"):
        cache.put(key, val)
    elif isinstance(cache, dict):
        cache[key] = val

def cache_fetch(cache: LRUCache, key: Any) -> Any:
    if hasattr(cache, "get"):
        return cache.get(key)
    elif isinstance(cache, dict):
        return cache.get(key)
    return None

def cache_create_bloom(size: int = 1024, hash_count: int = 3) -> BloomFilter:
    return BloomFilter(size, hash_count)

def cache_bloom_check(bf: BloomFilter, item: Any) -> bool:
    if hasattr(bf, "contains"):
        return bf.contains(str(item))
    return False
