"""Queue Domain Natural Language Parser."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class QueueDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # create message queue with capacity <cap> into <target>
        m_q = re.match(r"^create\s+message\s+queue\s+with\s+capacity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_q:
            return f"set {m_q.group(2)} to queue_create({m_q.group(1)})"

        # create priority queue into <target>
        m_pq = re.match(r"^create\s+priority\s+queue\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_pq:
            return f"set {m_pq.group(1)} to queue_create_priority()"

        # create ring buffer with size <sz> into <target>
        m_rb = re.match(r"^create\s+ring\s+buffer\s+with\s+size\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rb:
            return f"set {m_rb.group(2)} to queue_ring_create({m_rb.group(1)})"

        # create token bucket with rate <r> capacity <c> into <target>
        m_tb = re.match(r"^create\s+token\s+bucket\s+with\s+rate\s+(.+?)\s+capacity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tb:
            return f"set {m_tb.group(3)} to queue_token_bucket_create({m_tb.group(1)}, {m_tb.group(2)})"

        # create dead letter queue with retries <n> into <target>
        m_dlq = re.match(r"^create\s+dead\s+letter\s+queue\s+with\s+retries\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dlq:
            return f"set {m_dlq.group(2)} to queue_dlq_create({m_dlq.group(1)})"

        # publish message <msg> to <q>
        m_pub = re.match(r"^publish\s+message\s+(.+?)\s+to\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_pub:
            return f"queue_publish({m_pub.group(2)}, {m_pub.group(1)})"

        # consume from queue <q> into <target>
        m_con = re.match(r"^consume\s+from\s+queue\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_con:
            return f"set {m_con.group(2)} to queue_consume({m_con.group(1)})"

        m_bo_alt = re.match(r"^calculate\s+backoff\s+for\s+attempt\s+(.+?)\s+base\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bo_alt:
            return f"set {m_bo_alt.group(3)} to queue_exponential_backoff({m_bo_alt.group(1)}, {m_bo_alt.group(2)})"

        # calculate backoff for attempt <att> into <target>
        m_bo = re.match(r"^calculate\s+backoff\s+for\s+attempt\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bo:
            return f"set {m_bo.group(2)} to queue_exponential_backoff({m_bo.group(1)})"

        
        m_pub = re.match(r"^publish\s+message\s+(.+?)\s+to\s+(?:queue\s+)?([A-Za-z_]\w*)(?:\s+with\s+priority\s+(.+?))?$", s, re.IGNORECASE)
        if m_pub:
            msg = m_pub.group(1)
            q_var = m_pub.group(2)
            prio = m_pub.group(3)
            if prio:
                return f"queue_priority_push({q_var}, {msg}, {prio})"
            return f"queue_fifo_push({q_var}, {msg})"

        m_tb_alt = re.match(r"^create\s+token\s+bucket\s+rate\s+(.+?)\s+capacity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tb_alt:
            return f"set {m_tb_alt.group(3)} to queue_token_bucket_create({m_tb_alt.group(1)}, {m_tb_alt.group(2)})"

        m_dlq_alt = re.match(r"^create\s+dead\s+letter\s+queue\s+retries\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dlq_alt:
            return f"set {m_dlq_alt.group(2)} to queue_dead_letter_create({m_dlq_alt.group(1)})"

        m_bo_alt = re.match(r"^calculate\s+backoff\s+for\s+attempt\s+(.+?)\s+base\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bo_alt:
            return f"set {m_bo_alt.group(3)} to queue_exponential_backoff({m_bo_alt.group(1)}, {m_bo_alt.group(2)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Queue domain does not define declarative blocks")
