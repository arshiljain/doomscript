from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.cache.runtime import (
    LRUCache, LFUCache, BloomFilter, ConsistentHashRing,
    cache_create_lru, cache_create_lfu, cache_store, cache_fetch,
    cache_create_bloom, cache_bloom_add, cache_bloom_check,
    cache_ring_create, cache_ring_add_node, cache_ring_get_node, cache_stats
)
from doomscript.domains.cache.parser import CacheDomainParser
from doomscript.domains.cache.exporter import CacheASTExporter

class CacheRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class CacheDomain(DomainContract):
    name = "cache"
    aliases = ["caching", "lru", "ttl"]
    description = "Advanced caching: LRU, LFU, Bloom filters, and consistent hashing rings"
    parser = CacheDomainParser()
    runtime = CacheRuntime()
    exporter = CacheASTExporter()
    capabilities = ["lru", "lfu", "bloom_filter", "consistent_hash_ring", "cache_stats"]
    verbs = [
        VerbSpec(pattern="create lru cache with capacity {cap:expr} into {target:ident}", description="Create LRU cache"),
        VerbSpec(pattern="create lfu cache with capacity {cap:expr} into {target:ident}", description="Create LFU cache"),
        VerbSpec(pattern="create hash ring with replicas {rep:expr} into {target:ident}", description="Consistent hash ring")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("create lru cache ") or s.startswith("create lfu cache ") or s.startswith("store in cache ") or s.startswith("fetch from cache ") or s.startswith("create bloom filter ") or s.startswith("check bloom filter ") or s.startswith("create hash ring ") or s.startswith("get node from hash ring ") or s.startswith("get stats for cache ")

CACHE_DOMAIN = CacheDomain()
get_domain_registry().register(CACHE_DOMAIN)

__all__ = [
    "CacheDomain", "CACHE_DOMAIN", "CacheRuntime",
    "LRUCache", "LFUCache", "BloomFilter", "ConsistentHashRing",
    "cache_create_lru", "cache_create_lfu", "cache_store", "cache_fetch",
    "cache_create_bloom", "cache_bloom_add", "cache_bloom_check",
    "cache_ring_create", "cache_ring_add_node", "cache_ring_get_node", "cache_stats"
]
