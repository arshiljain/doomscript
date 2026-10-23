"""Queue Domain Runtime: FIFO message queues, priority heaps, ring buffers, rate limiters, and queuing theory solvers."""
import heapq
import time
import math
import random
from typing import List, Dict, Any, Tuple, Optional
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED CORE QUEUES
# ============================================================================

class MessageQueue:
    """FIFO Message Queue with capacity tracking."""
    def __init__(self, capacity: int = 1000):
        self.capacity = max(1, int(capacity))
        self.items: List[Any] = []

    def publish(self, msg: Any) -> bool:
        if len(self.items) >= self.capacity:
            return False
        self.items.append(msg)
        return True

    def consume(self) -> Optional[Any]:
        return self.items.pop(0) if self.items else None

    def size(self) -> int:
        return len(self.items)

    def is_empty(self) -> bool:
        return len(self.items) == 0

class PriorityMessageQueue:
    """Priority message queue implemented via min-heap."""
    def __init__(self):
        self.heap: List[Tuple[int, int, Any]] = []
        self.counter = 0

    def publish(self, msg: Any, priority: int = 0) -> None:
        self.counter += 1
        heapq.heappush(self.heap, (-float(priority), self.counter, msg))

    def consume(self) -> Optional[Any]:
        if self.heap:
            return heapq.heappop(self.heap)[2]
        return None

    def size(self) -> int:
        return len(self.heap)

class RingBuffer:
    """Fixed-size circular ring buffer for bounded queue operations."""
    def __init__(self, size: int = 100):
        self.capacity = max(1, int(size))
        self.buffer: List[Any] = [None] * self.capacity
        self.head = 0
        self.tail = 0
        self.count = 0

    def push(self, item: Any) -> bool:
        if self.count >= self.capacity:
            return False
        self.buffer[self.tail] = item
        self.tail = (self.tail + 1) % self.capacity
        self.count += 1
        return True

    def pop(self) -> Optional[Any]:
        if self.count == 0:
            return None
        item = self.buffer[self.head]
        self.buffer[self.head] = None
        self.head = (self.head + 1) % self.capacity
        self.count -= 1
        return item

    def is_full(self) -> bool:
        return self.count >= self.capacity

    def is_empty(self) -> bool:
        return self.count == 0

class TokenBucket:
    """Token Bucket rate limiter algorithm."""
    def __init__(self, rate: float = 10.0, capacity: float = 20.0):
        self.rate = float(rate)
        self.capacity = float(capacity)
        self.tokens = float(capacity)
        self.last_update = time.time()

    def acquire(self, tokens_needed: float = 1.0) -> bool:
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_update = now
        if self.tokens >= tokens_needed:
            self.tokens -= tokens_needed
            return True
        return False

class DeadLetterQueue:
    """Dead-Letter Queue with max retry management and backoff."""
    def __init__(self, max_retries: int = 3):
        self.max_retries = int(max_retries)
        self.dead_letters: List[Dict[str, Any]] = []

    def record_failure(self, msg: Any, attempt: int, error: str) -> bool:
        if attempt >= self.max_retries:
            self.dead_letters.append({"message": msg, "attempts": attempt, "error": error, "timestamp": time.time()})
            return True
        return False

    def count(self) -> int:
        return len(self.dead_letters)

# ============================================================================
# 2. STANDALONE PRESERVED FACTORIES & HELPERS
# ============================================================================

def queue_create(capacity: int = 1000) -> MessageQueue:
    return MessageQueue(capacity)

def queue_publish(q: Any, msg: Any, priority: Optional[int] = None) -> Any:
    if hasattr(q, "publish"):
        if priority is not None and isinstance(q, PriorityMessageQueue):
            q.publish(msg, priority)
        else:
            q.publish(msg)
    elif hasattr(q, "push"):
        q.push(msg)

def queue_consume(q: Any) -> Optional[Any]:
    if hasattr(q, "consume"):
        return q.consume()
    elif hasattr(q, "pop"):
        return q.pop()
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
    delay = min(float(max_ms), float(base_ms) * (2 ** int(attempt)))
    if jitter:
        return round(random.uniform(0.0, delay), 2)
    return round(delay, 2)

# ============================================================================
# 3. ADVANCED QUEUING THEORY (ERLANG-C & LITTLE'S LAW)
# ============================================================================

def queue_erlang_c(arrival_rate_lambda: float, service_rate_mu: float, servers_c: int) -> Dict[str, Any]:
    """Calculates Erlang-C waiting probability, avg queue length, and waiting time in M/M/c queue."""
    c = int(servers_c)
    a = arrival_rate_lambda / service_rate_mu # Traffic intensity (Erlangs)
    rho = a / c # Server utilization
    if rho >= 1.0:
        return {"stable": False, "traffic_intensity": round(a, 4), "utilization": round(rho, 4)}
    sum_terms = sum((a ** k) / math.factorial(k) for k in range(c))
    last_term = ((a ** c) / (math.factorial(c) * (1.0 - rho)))
    p0 = 1.0 / (sum_terms + last_term)
    pw = last_term * p0
    lq = pw * (rho / (1.0 - rho))
    wq = lq / arrival_rate_lambda if arrival_rate_lambda > 0 else 0.0
    return {
        "stable": True,
        "traffic_intensity": round(a, 4),
        "utilization": round(rho, 4),
        "prob_wait": round(pw, 4),
        "expected_queue_length": round(lq, 4),
        "expected_wait_time": round(wq, 4)
    }

def queue_littles_law(arrival_rate: float, avg_wait_time: float) -> float:
    """Calculates average number of customers in system: L = lambda * W."""
    return round(float(arrival_rate) * float(avg_wait_time), 4)

# ============================================================================
# 4. ADVANCED SCHEDULERS (WFQ & DRR)
# ============================================================================

class WeightedFairQueue:
    """Weighted Fair Queuing (WFQ) scheduler with virtual finish times."""
    def __init__(self, flow_weights: Dict[str, float]):
        self.weights = {f: max(0.01, float(w)) for f, w in flow_weights.items()}
        self.queues: Dict[str, List[Dict[str, Any]]] = {f: [] for f in self.weights}
        self.virtual_time = 0.0
        self.last_finish_times: Dict[str, float] = {f: 0.0 for f in self.weights}

    def enqueue(self, flow: str, packet: Any, length: float) -> None:
        if flow not in self.weights:
            self.weights[flow] = 1.0
            self.queues[flow] = []
            self.last_finish_times[flow] = self.virtual_time
        start_time = max(self.virtual_time, self.last_finish_times[flow])
        finish_time = start_time + float(length) / self.weights[flow]
        self.last_finish_times[flow] = finish_time
        self.queues[flow].append({"packet": packet, "length": length, "finish_time": finish_time})

    def dequeue(self) -> Optional[Any]:
        best_flow = None
        min_finish = float("inf")
        for f, q in self.queues.items():
            if q and q[0]["finish_time"] < min_finish:
                min_finish = q[0]["finish_time"]
                best_flow = f
        if best_flow is not None:
            pkt = self.queues[best_flow].pop(0)
            self.virtual_time = pkt["finish_time"]
            return pkt["packet"]
        return None

class DeficitRoundRobin:
    """Deficit Round Robin (DRR) packet scheduler with quantum replenishment."""
    def __init__(self, quantum: int = 512):
        self.quantum = int(quantum)
        self.queues: Dict[str, List[Tuple[Any, int]]] = {}
        self.deficits: Dict[str, int] = {}
        self.flow_list: List[str] = []
        self.current_idx = 0

    def add_flow(self, flow_id: str) -> None:
        if flow_id not in self.queues:
            self.queues[flow_id] = []
            self.deficits[flow_id] = 0
            self.flow_list.append(flow_id)

    def enqueue(self, flow_id: str, packet: Any, size_bytes: int) -> None:
        self.add_flow(flow_id)
        self.queues[flow_id].append((packet, int(size_bytes)))

    def dequeue(self) -> Optional[Any]:
        if not self.flow_list:
            return None
        checked = 0
        while checked < len(self.flow_list):
            flow = self.flow_list[self.current_idx]
            q = self.queues[flow]
            if q:
                if self.deficits[flow] == 0:
                    self.deficits[flow] += self.quantum
                pkt, size = q[0]
                if size <= self.deficits[flow]:
                    self.deficits[flow] -= size
                    q.pop(0)
                    return pkt
            else:
                self.deficits[flow] = 0
            self.current_idx = (self.current_idx + 1) % len(self.flow_list)
            checked += 1
        return None

# ============================================================================
# 5. DOMAIN RUNTIME
# ============================================================================

class QueueRuntime(DomainRuntime):
    """Unified runtime bridge for the Queue computational domain."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def new_queue(self, capacity: int = 1000) -> MessageQueue:
        return MessageQueue(capacity)
    def new_priority_queue(self) -> PriorityMessageQueue:
        return PriorityMessageQueue()
    def new_ring_buffer(self, size: int = 100) -> RingBuffer:
        return RingBuffer(size)
    def new_token_bucket(self, rate: float = 10.0, cap: float = 20.0) -> TokenBucket:
        return TokenBucket(rate, cap)
    def new_dlq(self, retries: int = 3) -> DeadLetterQueue:
        return DeadLetterQueue(retries)
    def new_wfq(self, weights: Dict[str, float]) -> WeightedFairQueue:
        return WeightedFairQueue(weights)
    def new_drr(self, quantum: int = 512) -> DeficitRoundRobin:
        return DeficitRoundRobin(quantum)
    def erlang_c(self, lam: float, mu: float, c: int) -> Dict[str, Any]:
        return queue_erlang_c(lam, mu, c)
    def littles_law(self, lam: float, w: float) -> float:
        return queue_littles_law(lam, w)
    def backoff(self, attempt: int, base_ms: float = 100.0, max_ms: float = 10000.0) -> float:
        return queue_exponential_backoff(attempt, base_ms, max_ms)

queue_fifo_push = queue_publish
queue_priority_push = queue_publish
queue_dead_letter_create = queue_dlq_create
