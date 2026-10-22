"""Queue Domain Runtime: FIFO/LIFO queues, Priority queues, and PubSub message brokers."""
import heapq
from collections import deque
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
        # Min-heap by default; negate priority for max-heap
        heapq.heappush(self.heap, (-int(priority), self._counter, msg))
        self._counter += 1
    def dequeue(self) -> Optional[Any]:
        if not self.heap:
            return None
        _, _, msg = heapq.heappop(self.heap)
        return msg
    def size(self) -> int:
        return len(self.heap)

class PubSubBroker:
    def __init__(self):
        self.topics = {}
    def subscribe(self, topic: str, subscriber_id: str) -> None:
        if topic not in self.topics:
            self.topics[topic] = set()
        self.topics[topic].add(subscriber_id)
    def publish(self, topic: str, msg: Any) -> int:
        subs = self.topics.get(topic, set())
        return len(subs)

def queue_create(capacity: int = 1000) -> MessageQueue:
    return MessageQueue(capacity)

def queue_publish(q: Any, msg: Any, priority: Optional[int] = None) -> Any:
    if priority is not None and hasattr(q, "enqueue"):
        return q.enqueue(msg, priority)
    if hasattr(q, "enqueue"):
        return q.enqueue(msg)
    if isinstance(q, list):
        q.append(msg)
        return True
    return False

def queue_consume(q: Any) -> Any:
    if hasattr(q, "dequeue"):
        return q.dequeue()
    if isinstance(q, list) and q:
        return q.pop(0)
    return None

def queue_create_priority() -> PriorityMessageQueue:
    return PriorityMessageQueue()

def queue_create_broker() -> PubSubBroker:
    return PubSubBroker()
