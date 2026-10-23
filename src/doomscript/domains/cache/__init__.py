from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.cache.runtime import (
    CacheRuntime, LRUCache, LFUCache, ARCCache, TwoQueueCache,
    ClockCache, SegmentedLRUCache, TTLCache, BloomFilter, ConsistentHashRing,
    cache_create_lru, cache_create_lfu, cache_create_arc, cache_create_2q,
    cache_create_clock, cache_create_slru, cache_create_ttl,
    cache_store, cache_fetch, cache_create_bloom, cache_bloom_add,
    cache_bloom_check, cache_ring_create, cache_ring_add_node,
    cache_ring_get_node, cache_stats, cache_xfetch_should_recompute
)
from doomscript.domains.cache.parser import CacheDomainParser
from doomscript.domains.cache.exporter import CacheASTExporter

class CacheDomain(DomainContract):
    name = "cache"
    aliases = ["caching", "lru", "ttl", "arc"]
    description = "Advanced caching: LRU, LFU, ARC, 2Q, Clock, Bloom filters, consistent hashing, and XFetch"
    parser = CacheDomainParser()
    runtime = CacheRuntime()
    exporter = CacheASTExporter()
    capabilities = ["lru", "lfu", "arc", "2q", "clock", "slru", "ttl", "bloom_filter", "consistent_hash_ring", "cache_stats", "xfetch"]
    verbs = [
        VerbSpec(pattern="create lru cache with capacity {cap:expr} into {target:ident}", description="Create LRU cache"),
        VerbSpec(pattern="create lfu cache with capacity {cap:expr} into {target:ident}", description="Create LFU cache"),
        VerbSpec(pattern="create arc cache with capacity {cap:expr} into {target:ident}", description="Create ARC cache"),
        VerbSpec(pattern="create hash ring with replicas {rep:expr} into {target:ident}", description="Consistent hash ring"),
        VerbSpec(pattern="store in cache {cache:expr} key {key:expr} value {val:expr}", description="Store cache value"),
        VerbSpec(pattern="fetch from cache {cache:expr} key {key:expr} into {target:ident}", description="Fetch cache value")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("create lru cache ") or
            s.startswith("create lfu cache ") or
            s.startswith("create arc cache ") or
            s.startswith("store in cache ") or
            s.startswith("fetch from cache ") or
            s.startswith("create bloom filter ") or
            s.startswith("check bloom filter ") or
            s.startswith("create hash ring ") or
            s.startswith("get node from hash ring ") or
            s.startswith("get stats for cache ")
        )

CACHE_DOMAIN = CacheDomain()
get_domain_registry().register(CACHE_DOMAIN)

__all__ = [
    "CacheDomain", "CACHE_DOMAIN", "CacheRuntime",
    "LRUCache", "LFUCache", "ARCCache", "TwoQueueCache",
    "ClockCache", "SegmentedLRUCache", "TTLCache", "BloomFilter", "ConsistentHashRing",
    "cache_create_lru", "cache_create_lfu", "cache_create_arc", "cache_create_2q",
    "cache_create_clock", "cache_create_slru", "cache_create_ttl",
    "cache_store", "cache_fetch", "cache_create_bloom", "cache_bloom_add",
    "cache_bloom_check", "cache_ring_create", "cache_ring_add_node",
    "cache_ring_get_node", "cache_stats", "cache_xfetch_should_recompute"
]
