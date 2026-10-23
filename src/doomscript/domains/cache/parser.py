"""Cache Domain Natural Language Parser."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class CacheDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # create lru cache with capacity <cap> into <target>
        m_lru = re.match(r"^create\s+lru\s+cache\s+with\s+capacity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_lru:
            return f"set {m_lru.group(2)} to cache_create_lru({m_lru.group(1)})"

        # create lfu cache with capacity <cap> into <target>
        m_lfu = re.match(r"^create\s+lfu\s+cache\s+with\s+capacity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_lfu:
            return f"set {m_lfu.group(2)} to cache_create_lfu({m_lfu.group(1)})"

        # create arc cache with capacity <cap> into <target>
        m_arc = re.match(r"^create\s+arc\s+cache\s+with\s+capacity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_arc:
            return f"set {m_arc.group(2)} to cache_create_arc({m_arc.group(1)})"

        # store in cache <cache> key <key> value <val>
        m_store = re.match(r"^store\s+in\s+cache\s+(.+?)\s+key\s+(.+?)\s+value\s+(.+?)$", s, re.IGNORECASE)
        if m_store:
            return f"cache_store({m_store.group(1)}, {m_store.group(2)}, {m_store.group(3)})"

        # fetch from cache <cache> key <key> into <target>
        m_fetch = re.match(r"^fetch\s+from\s+cache\s+(.+?)\s+key\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_fetch:
            return f"set {m_fetch.group(3)} to cache_fetch({m_fetch.group(1)}, {m_fetch.group(2)})"

        # create bloom filter with size <size> hashes <h> into <target>
        m_bloom = re.match(r"^create\s+bloom\s+filter\s+with\s+size\s+(.+?)\s+hashes\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bloom:
            return f"set {m_bloom.group(3)} to cache_create_bloom({m_bloom.group(1)}, {m_bloom.group(2)})"

        # check bloom filter <bf> for item <item> into <target>
        m_bcheck = re.match(r"^check\s+bloom\s+filter\s+(.+?)\s+for\s+item\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bcheck:
            return f"set {m_bcheck.group(3)} to cache_bloom_check({m_bcheck.group(1)}, {m_bcheck.group(2)})"

        # create hash ring with replicas <rep> into <target>
        m_ring = re.match(r"^create\s+hash\s+ring\s+with\s+replicas\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ring:
            return f"set {m_ring.group(2)} to cache_ring_create({m_ring.group(1)})"

        # get node from hash ring <ring> for key <key> into <target>
        m_node = re.match(r"^get\s+node\s+from\s+hash\s+ring\s+(.+?)\s+for\s+key\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_node:
            return f"set {m_node.group(3)} to cache_ring_get_node({m_node.group(1)}, {m_node.group(2)})"

        # get stats for cache <c> into <target>
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
