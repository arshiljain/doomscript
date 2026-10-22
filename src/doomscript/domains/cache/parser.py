import re
from typing import Optional
from doomscript.domains.base import DomainParser

class CacheDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_lru = re.match(r"^create\s+lru\s+cache\s+with\s+capacity\s+(\d+|[A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_lru:
            return f"set {m_lru.group(2)} to cache_create_lru({m_lru.group(1)})"

        m_lfu = re.match(r"^create\s+lfu\s+cache\s+with\s+capacity\s+(\d+|[A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_lfu:
            return f"set {m_lfu.group(2)} to cache_create_lfu({m_lfu.group(1)})"

        m_store = re.match(r"^store\s+in\s+cache\s+(.+?)\s+key\s+(.+?)\s+value\s+(.+)$", s, re.IGNORECASE)
        if m_store:
            return f"cache_store({m_store.group(1)}, {m_store.group(2)}, {m_store.group(3)})"

        m_fetch = re.match(r"^fetch\s+from\s+cache\s+(.+?)\s+key\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_fetch:
            return f"set {m_fetch.group(3)} to cache_fetch({m_fetch.group(1)}, {m_fetch.group(2)})"

        m_bloom = re.match(r"^create\s+bloom\s+filter\s+with\s+size\s+(\d+|[A-Za-z_]\w*)\s+hashes\s+(\d+|[A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bloom:
            return f"set {m_bloom.group(3)} to cache_create_bloom({m_bloom.group(1)}, {m_bloom.group(2)})"

        m_check = re.match(r"^check\s+bloom\s+filter\s+(.+?)\s+for\s+item\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_check:
            return f"set {m_check.group(3)} to cache_bloom_check({m_check.group(1)}, {m_check.group(2)})"

        m_ring = re.match(r"^create\s+hash\s+ring\s+with\s+replicas\s+(\d+|[A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ring:
            return f"set {m_ring.group(2)} to cache_ring_create({m_ring.group(1)})"

        m_ring_node = re.match(r"^get\s+node\s+from\s+hash\s+ring\s+(.+?)\s+for\s+key\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ring_node:
            return f"set {m_ring_node.group(3)} to cache_ring_get_node({m_ring_node.group(1)}, {m_ring_node.group(2)})"

        m_stats = re.match(r"^get\s+stats\s+for\s+cache\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_stats:
            return f"set {m_stats.group(2)} to cache_stats({m_stats.group(1)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Cache domain does not define declarative blocks")
