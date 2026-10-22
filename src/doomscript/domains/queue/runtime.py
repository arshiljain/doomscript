"""Queue Domain Runtime: FIFO, Priority, Ring Buffer, Token Bucket, and Dead Letter Queues."""
import heapq
import random
import time
from collections import deque, defaultdict
from typing import Any, Dict, List, Optional

class MessageQueue:
    def __init__(self, capacity: int = 1000):
        self.capacity = int(capacity)
        self.q = deque()
    def enqueue(self, msg: Any) -> bool:
        if len(self.q) >= self.capacity:
            return False
        self.q.append(msg)
        return True
    def dequeue(self) -> Optional[Any]:
        return self.q.popleft() if self.q else None
    def size(self) -> int:
        return len(self.q)

class PriorityMessageQueue:
    def __init__(self):
        self.heap = []
        self._counter = 0
    def enqueue(self, msg: Any, priority: int = 0) -> None:
        heapq.heappush(self.heap, (-int(priority), self._counter, msg))
        self._counter += 1
    def dequeue(self) -> Optional[Any]:
        if not self.heap:
            return None
        _, _, msg = heapq.heappop(self.heap)
        return msg
    def size(self) -> int:
        return len(self.heap)

class RingBuffer:
    """Fixed-size circular buffer that automatically overwrites oldest items on overflow."""
    def __init__(self, size: int = 100):
        self.size = max(1, int(size))
        self.buffer = [None] * self.size
        self.head = 0
        self.tail = 0
        self.count = 0
    def push(self, item: Any) -> None:
        self.buffer[self.tail] = item
        self.tail = (self.tail + 1) % self.size
        if self.count < self.size:
            self.count += 1
        else:
            self.head = (self.head + 1) % self.size
    def pop(self) -> Optional[Any]:
        if self.count == 0:
            return None
        item = self.buffer[self.head]
        self.head = (self.head + 1) % self.size
        self.count -= 1
        return item
    def to_list(self) -> List[Any]:
        res = []
        for i in range(self.count):
            res.append(self.buffer[(self.head + i) % self.size])
        return res

class TokenBucket:
    """Rate limiter implementing the Token Bucket algorithm."""
    def __init__(self, refill_rate_per_sec: float = 10.0, capacity: float = 20.0):
        self.rate = float(refill_rate_per_sec)
        self.capacity = float(capacity)
        self.tokens = float(capacity)
        self.last_refill = time.time()
    def consume(self, tokens: float = 1.0) -> bool:
        now = time.time()
        elapsed = now - self.last_refill
        self.last_refill = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

class DeadLetterQueue:
    """Dead letter queue with retry threshold and error payload tracking."""
    def __init__(self, max_retries: int = 3):
        self.max_retries = int(max_retries)
        self.dlq = []
        self.retries = defaultdict(int)
    def handle_failure(self, msg: Any, error: str) -> Dict[str, Any]:
        msg_id = str(msg)
        self.retries[msg_id] += 1
        if self.retries[msg_id] >= self.max_retries:
            entry = {"message": msg, "error": str(error), "retries": self.retries[msg_id], "status": "dead_letter"}
            self.dlq.append(entry)
            return entry
        return {"message": msg, "retries": self.retries[msg_id], "status": "retry"}

def queue_create(capacity: int = 1000) -> MessageQueue:
    return MessageQueue(capacity)

def queue_publish(q: Any, msg: Any, priority: Optional[int] = None) -> Any:
    if hasattr(q, "enqueue"):
        if priority is not None:
            return q.enqueue(msg, priority)
        return q.enqueue(msg)
    return False

def queue_consume(q: Any) -> Optional[Any]:
    if hasattr(q, "dequeue"):
        return q.dequeue()
    return None

def queue_create_priority() -> PriorityMessageQueue:
    return PriorityMessageQueue()

def queue_ring_create(size: int = 100) -> RingBuffer:
    return RingBuffer(size)

def queue_token_bucket_create(rate: float = 10.0, capacity: float = 20.0) -> TokenBucket:
    return TokenBucket(rate, capacity)

def queue_dlq_create(max_retries: int = 3) -> DeadLetterQueue:
    return DeadLetterQueue(max_retries)

def queue_exponential_backoff(attempt: int, base_ms: float = 100.0, max_ms: float = 10000.0, jitter: bool = True) -> float:
    """Calculates exponential backoff with full jitter (AWS standard architecture)."""
    backoff = min(float(max_ms), float(base_ms) * (2.0 ** int(attempt)))
    if jitter:
        backoff = random.uniform(0.0, backoff)
    return round(backoff, 2)
