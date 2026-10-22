from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.queue.runtime import (
    MessageQueue, PriorityMessageQueue, PubSubBroker, queue_create,
    queue_publish, queue_consume, queue_create_priority, queue_create_broker
)
from doomscript.domains.queue.parser import QueueDomainParser
from doomscript.domains.queue.exporter import QueueASTExporter

class QueueRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class QueueDomain(DomainContract):
    name = "queue"
    aliases = ["messaging", "pubsub", "streaming_queue"]
    description = "Message queues, priority heaps, and pub/sub broker architecture"
    parser = QueueDomainParser()
    runtime = QueueRuntime()
    exporter = QueueASTExporter()
    capabilities = ["message_queue", "priority_queue", "pubsub"]
    verbs = [
        VerbSpec(pattern="create message queue with capacity {cap:expr} into {target:ident}", description="Create message queue"),
        VerbSpec(pattern="consume from queue {q:expr} into {target:ident}", description="Dequeue message")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("create message queue ") or s.startswith("create priority queue ") or s.startswith("publish message ") or s.startswith("consume from queue ") or s.startswith("create pubsub broker ")

QUEUE_DOMAIN = QueueDomain()
get_domain_registry().register(QUEUE_DOMAIN)

__all__ = [
    "QueueDomain", "QUEUE_DOMAIN", "QueueRuntime",
    "MessageQueue", "PriorityMessageQueue", "PubSubBroker", "queue_create",
    "queue_publish", "queue_consume", "queue_create_priority", "queue_create_broker"
]
