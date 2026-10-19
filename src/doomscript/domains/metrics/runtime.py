"""Metrics, Observability & Prometheus Telemetry Domain for DoomScript.

Provides 100% pure Python implementations of:
- Monotonic Counters with dimensional label sets
- Bidirectional Gauges
- Cumulative Histograms with logarithmic/exponential bucket distributions
- Streaming quantile estimation (p50, p90, p95, p99)
- Distributed Trace Span instrumentation
- OpenMetrics / Prometheus plaintext exposition format exporter
Zero external dependencies.
"""

from __future__ import annotations

import math
import time
from typing import Any, Dict, List, Optional, Tuple, Union


class Counter:
    """Monotonically increasing Prometheus-compatible counter."""

    def __init__(self, name: str, help_text: str = "", labels: Optional[Dict[str, str]] = None):
        self.name = name
        self.help_text = help_text or f"Counter metric {name}"
        self.labels = dict(labels or {})
        self.value: float = 0.0

    def inc(self, amount: float = 1.0) -> None:
        if amount < 0:
            raise ValueError("Counter increments must be non-negative")
        self.value += float(amount)


class Gauge:
    """Value metric that can arbitrarily increase or decrease."""

    def __init__(self, name: str, help_text: str = "", labels: Optional[Dict[str, str]] = None):
        self.name = name
        self.help_text = help_text or f"Gauge metric {name}"
        self.labels = dict(labels or {})
        self.value: float = 0.0

    def set(self, val: float) -> None:
        self.value = float(val)

    def inc(self, amount: float = 1.0) -> None:
        self.value += float(amount)

    def dec(self, amount: float = 1.0) -> None:
        self.value -= float(amount)


class Histogram:
    """Cumulative bucket histogram for latencies and sizes."""

    DEFAULT_BUCKETS = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float("inf")]

    def __init__(
        self,
        name: str,
        help_text: str = "",
        labels: Optional[Dict[str, str]] = None,
        buckets: Optional[List[float]] = None,
    ):
        self.name = name
        self.help_text = help_text or f"Histogram metric {name}"
        self.labels = dict(labels or {})
        raw_b = list(buckets) if buckets else list(self.DEFAULT_BUCKETS)
        if float("inf") not in raw_b:
            raw_b.append(float("inf"))
        self.buckets = sorted(raw_b)

        self.bucket_counts = {b: 0 for b in self.buckets}
        self.count = 0
        self.total_sum = 0.0

    def observe(self, val: float) -> None:
        v = float(val)
        self.count += 1
        self.total_sum += v
        for b in self.buckets:
            if v <= b:
                self.bucket_counts[b] += 1


class QuantileReservoir:
    """Sliding-window / reservoir percentile calculation."""

    @staticmethod
    def calculate_percentile(values: List[float], p: float) -> float:
        """Calculates p-th percentile (0 <= p <= 100) using linear interpolation."""
        if not values:
            return 0.0
        s = sorted(values)
        if len(s) == 1:
            return float(s[0])
        p = max(0.0, min(100.0, float(p)))
        k = (len(s) - 1) * (p / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return float(s[int(k)])
        d0 = s[int(f)] * (c - k)
        d1 = s[int(c)] * (k - f)
        return round(d0 + d1, 4)


class TraceSpan:
    """Distributed tracing span."""

    def __init__(self, name: str, trace_id: str = "trace-001", parent_id: Optional[str] = None):
        self.name = name
        self.trace_id = trace_id
        self.span_id = f"span-{int(time.time() * 1000) % 1000000}"
        self.parent_id = parent_id
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.tags: Dict[str, Any] = {}
        self.events: List[Tuple[float, str]] = []

    def tag(self, key: str, value: Any) -> TraceSpan:
        self.tags[key] = value
        return self

    def log_event(self, message: str) -> None:
        self.events.append((time.time(), message))

    def finish(self) -> float:
        self.end_time = time.time()
        return self.duration_ms()

    def duration_ms(self) -> float:
        end = self.end_time or time.time()
        return round((end - self.start_time) * 1000.0, 3)


class MetricsRegistry:
    """Central registry of Prometheus metrics."""

    def __init__(self):
        self.counters: Dict[str, Counter] = {}
        self.gauges: Dict[str, Gauge] = {}
        self.histograms: Dict[str, Histogram] = {}

    def clear(self) -> None:
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()

    def counter(self, name: str, help_text: str = "", labels: Optional[Dict[str, str]] = None) -> Counter:
        key = f"{name}_{sorted(labels.items()) if labels else ''}"
        if key not in self.counters:
            self.counters[key] = Counter(name, help_text, labels)
        return self.counters[key]

    def gauge(self, name: str, help_text: str = "", labels: Optional[Dict[str, str]] = None) -> Gauge:
        key = f"{name}_{sorted(labels.items()) if labels else ''}"
        if key not in self.gauges:
            self.gauges[key] = Gauge(name, help_text, labels)
        return self.gauges[key]

    def histogram(
        self,
        name: str,
        help_text: str = "",
        labels: Optional[Dict[str, str]] = None,
        buckets: Optional[List[float]] = None,
    ) -> Histogram:
        key = f"{name}_{sorted(labels.items()) if labels else ''}"
        if key not in self.histograms:
            self.histograms[key] = Histogram(name, help_text, labels, buckets)
        return self.histograms[key]

    def export_prometheus(self) -> str:
        """Serializes all registered metrics to OpenMetrics / Prometheus plaintext exposition format."""
        lines = []

        # Export Counters
        for c in self.counters.values():
            lines.append(f"# HELP {c.name} {c.help_text}")
            lines.append(f"# TYPE {c.name} counter")
            lbl_str = self._format_labels(c.labels)
            lines.append(f"{c.name}{lbl_str} {c.value}")

        # Export Gauges
        for g in self.gauges.values():
            lines.append(f"# HELP {g.name} {g.help_text}")
            lines.append(f"# TYPE {g.name} gauge")
            lbl_str = self._format_labels(g.labels)
            lines.append(f"{g.name}{lbl_str} {g.value}")

        # Export Histograms
        for h in self.histograms.values():
            lines.append(f"# HELP {h.name} {h.help_text}")
            lines.append(f"# TYPE {h.name} histogram")
            for b in h.buckets:
                b_str = "+Inf" if b == float("inf") else str(b)
                b_labels = dict(h.labels)
                b_labels["le"] = b_str
                lines.append(f"{h.name}_bucket{self._format_labels(b_labels)} {h.bucket_counts[b]}")
            lines.append(f"{h.name}_sum{self._format_labels(h.labels)} {h.total_sum}")
            lines.append(f"{h.name}_count{self._format_labels(h.labels)} {h.count}")

        return "\n".join(lines) + "\n"

    def _format_labels(self, labels: Dict[str, str]) -> str:
        if not labels:
            return ""
        items = [f'{k}="{v}"' for k, v in sorted(labels.items())]
        return "{" + ",".join(items) + "}"


_REGISTRY = MetricsRegistry()


# --- Public High-Level Runtime Functions ---

def metrics_counter(name: str, help_text: str = "", labels: Optional[Dict[str, str]] = None) -> Counter:
    """Returns or creates a Prometheus counter."""
    return _REGISTRY.counter(name, help_text, labels)


def metrics_gauge(name: str, help_text: str = "", labels: Optional[Dict[str, str]] = None) -> Gauge:
    """Returns or creates a Prometheus gauge."""
    return _REGISTRY.gauge(name, help_text, labels)


def metrics_histogram(
    name: str,
    help_text: str = "",
    labels: Optional[Dict[str, str]] = None,
    buckets: Optional[List[float]] = None,
) -> Histogram:
    """Returns or creates a Prometheus histogram."""
    return _REGISTRY.histogram(name, help_text, labels, buckets)


def metrics_calculate_percentile(values: List[float], p: float) -> float:
    """Calculates percentile (e.g. 50.0 for p50, 99.0 for p99) from data values."""
    return QuantileReservoir.calculate_percentile(values, p)


def metrics_export_openmetrics() -> str:
    """Exports all registered domain metrics to OpenMetrics plaintext format."""
    return _REGISTRY.export_prometheus()


def metrics_export_prometheus() -> str:
    """Exports all registered metrics to Prometheus exposition text."""
    return _REGISTRY.export_prometheus()


def metrics_clear() -> None:
    """Clears all registered metrics."""
    _REGISTRY.clear()
