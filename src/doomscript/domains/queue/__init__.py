from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.queue.runtime import (
    MessageQueue, PriorityMessageQueue, RingBuffer, TokenBucket, DeadLetterQueue,
    queue_create, queue_publish, queue_consume, queue_create_priority,
    queue_ring_create, queue_token_bucket_create, queue_dlq_create, queue_exponential_backoff
)
from doomscript.domains.queue.parser import QueueDomainParser
from doomscript.domains.queue.exporter import QueueASTExporter

class QueueRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class QueueDomain(DomainContract):
    name = "queue"
    aliases = ["queues", "priority_queue", "fifo"]
    description = "Queueing & messaging: FIFO, priority queues, ring buffers, token buckets, and DLQs"
    parser = QueueDomainParser()
    runtime = QueueRuntime()
    exporter = QueueASTExporter()
    capabilities = ["fifo_queue", "priority_queue", "ring_buffer", "token_bucket", "dead_letter_queue", "backoff"]
    verbs = [
        VerbSpec(pattern="create message queue with capacity {cap:expr} into {target:ident}", description="FIFO queue"),
        VerbSpec(pattern="create priority queue into {target:ident}", description="Priority queue"),
        VerbSpec(pattern="create ring buffer with size {sz:expr} into {target:ident}", description="Ring buffer")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("create message queue ") or s.startswith("create priority queue ") or s.startswith("create ring buffer ") or s.startswith("create token bucket ") or s.startswith("create dead letter queue ") or s.startswith("publish message ") or s.startswith("consume from queue ") or s.startswith("calculate backoff ")

QUEUE_DOMAIN = QueueDomain()
get_domain_registry().register(QUEUE_DOMAIN)

__all__ = [
    "QueueDomain", "QUEUE_DOMAIN", "QueueRuntime",
    "MessageQueue", "PriorityMessageQueue", "RingBuffer", "TokenBucket", "DeadLetterQueue",
    "queue_create", "queue_publish", "queue_consume", "queue_create_priority",
    "queue_ring_create", "queue_token_bucket_create", "queue_dlq_create", "queue_exponential_backoff"
]
