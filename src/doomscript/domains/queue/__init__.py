from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.queue.runtime import (
    QueueRuntime, MessageQueue, PriorityMessageQueue, RingBuffer, TokenBucket,
    DeadLetterQueue, WeightedFairQueue, DeficitRoundRobin, queue_create,
    queue_publish, queue_consume, queue_create_priority, queue_ring_create,
    queue_token_bucket_create, queue_dlq_create, queue_exponential_backoff, queue_fifo_push, queue_priority_push, queue_dead_letter_create,
    queue_erlang_c, queue_littles_law
)
from doomscript.domains.queue.parser import QueueDomainParser
from doomscript.domains.queue.exporter import QueueASTExporter

class QueueDomain(DomainContract):
    name = "queue"
    aliases = ["queues", "priority_queue", "fifo"]
    description = "Queueing & messaging: FIFO, priority queues, ring buffers, token buckets, DLQs, WFQ, and Erlang-C"
    parser = QueueDomainParser()
    runtime = QueueRuntime()
    exporter = QueueASTExporter()
    capabilities = ["fifo_queue", "priority_queue", "ring_buffer", "token_bucket", "dead_letter_queue", "backoff", "wfq", "drr", "erlang_c"]
    verbs = [
        VerbSpec(pattern="create message queue with capacity {cap:expr} into {target:ident}", description="FIFO queue"),
        VerbSpec(pattern="create priority queue into {target:ident}", description="Priority queue"),
        VerbSpec(pattern="create ring buffer with size {sz:expr} into {target:ident}", description="Ring buffer"),
        VerbSpec(pattern="publish message {msg:expr} to {q:ident}", description="Publish message"),
        VerbSpec(pattern="consume from queue {q:expr} into {target:ident}", description="Consume message")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("create message queue ") or
            s.startswith("create priority queue ") or
            s.startswith("create ring buffer ") or
            s.startswith("create token bucket ") or
            s.startswith("create dead letter queue ") or
            s.startswith("publish message ") or
            s.startswith("consume from queue ") or
            s.startswith("calculate backoff ")
        )

QUEUE_DOMAIN = QueueDomain()
get_domain_registry().register(QUEUE_DOMAIN)

__all__ = [
    "QueueDomain", "QUEUE_DOMAIN", "QueueRuntime",
    "MessageQueue", "PriorityMessageQueue", "RingBuffer", "TokenBucket",
    "DeadLetterQueue", "WeightedFairQueue", "DeficitRoundRobin",
    "queue_create", "queue_publish", "queue_consume", "queue_create_priority",
    "queue_ring_create", "queue_token_bucket_create", "queue_dlq_create",
    "queue_exponential_backoff", "queue_fifo_push", "queue_priority_push", "queue_dead_letter_create", "queue_erlang_c", "queue_littles_law"
]
