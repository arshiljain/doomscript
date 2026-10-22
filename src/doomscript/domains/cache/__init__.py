from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.cache.runtime import (
    LRUCache, BloomFilter, cache_create_lru, cache_store, cache_fetch,
    cache_create_bloom, cache_bloom_check
)
from doomscript.domains.cache.parser import CacheDomainParser
from doomscript.domains.cache.exporter import CacheASTExporter

class CacheRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class CacheDomain(DomainContract):
    name = "cache"
    aliases = ["caching", "lru", "memo"]
    description = "In-memory caching algorithms: LRU, TTL, and Bloom filter"
    parser = CacheDomainParser()
    runtime = CacheRuntime()
    exporter = CacheASTExporter()
    capabilities = ["lru_cache", "bloom_filter", "cache_store", "cache_fetch"]
    verbs = [
        VerbSpec(pattern="create lru cache with capacity {cap:expr} into {target:ident}", description="Create LRU cache"),
        VerbSpec(pattern="fetch from cache {c:expr} key {k:expr} into {target:ident}", description="Retrieve value from cache")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("create lru cache ") or s.startswith("store in cache ") or s.startswith("fetch from cache ") or s.startswith("create bloom filter ") or s.startswith("check bloom filter ")

CACHE_DOMAIN = CacheDomain()
get_domain_registry().register(CACHE_DOMAIN)

__all__ = [
    "CacheDomain", "CACHE_DOMAIN", "CacheRuntime",
    "LRUCache", "BloomFilter", "cache_create_lru", "cache_store", "cache_fetch",
    "cache_create_bloom", "cache_bloom_check"
]
