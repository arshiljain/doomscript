import re
from typing import Optional
from doomscript.domains.base import DomainParser

class CacheDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_lru = re.match(r"^create\s+lru\s+cache\s+with\s+capacity\s+(\d+|[A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_lru:
            return f"set {m_lru.group(2)} to cache_create_lru({m_lru.group(1)})"

        m_store = re.match(r"^store\s+in\s+cache\s+(.+?)\s+key\s+(.+?)\s+value\s+(.+)$", s, re.IGNORECASE)
        if m_store:
            return f"cache_store({m_store.group(1)}, {m_store.group(2)}, {m_store.group(3)})"

        m_fetch = re.match(r"^fetch\s+from\s+cache\s+(.+?)\s+key\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_fetch:
            return f"set {m_fetch.group(3)} to cache_fetch({m_fetch.group(1)}, {m_fetch.group(2)})"

        m_bf = re.match(r"^create\s+bloom\s+filter\s+with\s+size\s+(\d+|[A-Za-z_]\w*)\s+hashes\s+(\d+|[A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bf:
            return f"set {m_bf.group(3)} to cache_create_bloom({m_bf.group(1)}, {m_bf.group(2)})"

        m_check = re.match(r"^check\s+bloom\s+filter\s+(.+?)\s+for\s+item\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_check:
            return f"set {m_check.group(3)} to cache_bloom_check({m_check.group(1)}, {m_check.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Cache domain does not define declarative blocks")
