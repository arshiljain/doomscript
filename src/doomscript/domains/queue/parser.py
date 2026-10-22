import re
from typing import Optional
from doomscript.domains.base import DomainParser

class QueueDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_mq = re.match(r"^create\s+message\s+queue\s+with\s+capacity\s+(\d+|[A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mq:
            return f"set {m_mq.group(2)} to queue_create({m_mq.group(1)})"

        m_pq = re.match(r"^create\s+priority\s+queue\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_pq:
            return f"set {m_pq.group(1)} to queue_create_priority()"

        m_rb = re.match(r"^create\s+ring\s+buffer\s+with\s+size\s+(\d+|[A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rb:
            return f"set {m_rb.group(2)} to queue_ring_create({m_rb.group(1)})"

        m_tb = re.match(r"^create\s+token\s+bucket\s+rate\s+(.+?)\s+capacity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tb:
            return f"set {m_tb.group(3)} to queue_token_bucket_create({m_tb.group(1)}, {m_tb.group(2)})"

        m_dlq = re.match(r"^create\s+dead\s+letter\s+queue\s+retries\s+(\d+|[A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dlq:
            return f"set {m_dlq.group(2)} to queue_dlq_create({m_dlq.group(1)})"

        m_pub = re.match(r"^publish\s+message\s+(.+?)\s+to\s+queue\s+(.+?)(?:\s+with\s+priority\s+(.+?))?$", s, re.IGNORECASE)
        if m_pub:
            prio = m_pub.group(3) if m_pub.group(3) else "None"
            return f"queue_publish({m_pub.group(2)}, {m_pub.group(1)}, {prio})"

        m_cons = re.match(r"^consume\s+from\s+queue\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cons:
            return f"set {m_cons.group(2)} to queue_consume({m_cons.group(1)})"

        m_backoff = re.match(r"^calculate\s+backoff\s+for\s+attempt\s+(.+?)\s+base\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_backoff:
            return f"set {m_backoff.group(3)} to queue_exponential_backoff({m_backoff.group(1)}, {m_backoff.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Queue domain does not define declarative blocks")
