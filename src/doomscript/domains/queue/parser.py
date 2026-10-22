import re
from typing import Optional
from doomscript.domains.base import DomainParser

class QueueDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_q = re.match(r"^create\s+message\s+queue\s+with\s+capacity\s+(\d+|[A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_q:
            return f"set {m_q.group(2)} to queue_create({m_q.group(1)})"

        m_pq = re.match(r"^create\s+priority\s+queue\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_pq:
            return f"set {m_pq.group(1)} to queue_create_priority()"

        m_pub = re.match(r"^publish\s+message\s+(.+?)\s+to\s+queue\s+(.+?)(?:\s+with\s+priority\s+(.+?))?$", s, re.IGNORECASE)
        if m_pub:
            msg, q, p = m_pub.group(1).strip(), m_pub.group(2).strip(), m_pub.group(3)
            return f"queue_publish({q}, {msg}, {p.strip() if p else 'None'})"

        m_con = re.match(r"^consume\s+from\s+queue\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_con:
            return f"set {m_con.group(2)} to queue_consume({m_con.group(1)})"

        m_brk = re.match(r"^create\s+pubsub\s+broker\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_brk:
            return f"set {m_brk.group(1)} to queue_create_broker()"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Queue domain does not define declarative blocks")
