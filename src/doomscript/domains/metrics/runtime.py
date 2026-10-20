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


# ==============================================================================
# Advanced Metrics Deepening: OTLP Exporter, Exponential Decay & EWMA Anomaly
# ==============================================================================

class OTLPTraceExporter:
    """OpenTelemetry (OTLP/JSON) standard trace and span serializer."""

    @staticmethod
    def _val_to_anyvalue(val: Any) -> Dict[str, Any]:
        if isinstance(val, bool):
            return {"boolValue": val}
        elif isinstance(val, int):
            return {"intValue": str(val)}
        elif isinstance(val, float):
            return {"doubleValue": val}
        return {"stringValue": str(val)}

    @classmethod
    def export_spans(
        cls,
        spans: List[TraceSpan],
        service_name: str = "doomscript-service",
        service_version: str = "1.0.0",
    ) -> Dict[str, Any]:
        """Converts internal TraceSpan objects to OTLP JSON protocol structure."""
        otlp_spans = []

        for s in spans:
            start_nano = int(s.start_time * 1e9)
            end_time = s.end_time if s.end_time is not None else s.start_time + 0.001
            end_nano = int(end_time * 1e9)

            attrs = []
            for k, v in s.tags.items():
                attrs.append({
                    "key": str(k),
                    "value": cls._val_to_anyvalue(v),
                })

            events = []
            for ev_time, msg in s.events:
                events.append({
                    "timeUnixNano": str(int(ev_time * 1e9)),
                    "name": msg,
                    "attributes": [],
                })

            # Format 32-char hex trace_id and 16-char hex span_id
            t_id = (s.trace_id.replace("-", "") * 4)[:32].ljust(32, "0")
            sp_id = (s.span_id.replace("-", "") * 4)[:16].ljust(16, "0")
            parent_sp_id = ((s.parent_id or "").replace("-", "") * 4)[:16].ljust(16, "0") if s.parent_id else ""

            otlp_spans.append({
                "traceId": t_id,
                "spanId": sp_id,
                "parentSpanId": parent_sp_id,
                "name": s.name,
                "kind": 1,  # SPAN_KIND_INTERNAL
                "startTimeUnixNano": str(start_nano),
                "endTimeUnixNano": str(end_nano),
                "attributes": attrs,
                "events": events,
                "status": {"code": 1},  # STATUS_CODE_OK
            })

        return {
            "resourceSpans": [
                {
                    "resource": {
                        "attributes": [
                            {"key": "service.name", "value": {"stringValue": service_name}},
                            {"key": "service.version", "value": {"stringValue": service_version}},
                        ]
                    },
                    "scopeSpans": [
                        {
                            "scope": {"name": "doomscript.tracer", "version": "1.0.0"},
                            "spans": otlp_spans,
                        }
                    ],
                }
            ]
        }


class ExponentialDecayReservoir:
    """Forward-decaying reservoir sampling for streaming percentiles (Cormode et al.)."""

    def __init__(self, size: int = 1028, alpha: float = 0.015):
        self.size = size
        self.alpha = float(alpha)
        self.start_time = time.time()
        # Min-heap of (priority, timestamp, value)
        self.values: List[Tuple[float, float, float]] = []

    def update(self, val: float, timestamp: Optional[float] = None) -> None:
        """Inserts an observation with forward-decay priority."""
        t = timestamp if timestamp is not None else time.time()
        rel_time = t - self.start_time
        # Priority weight = exp(alpha * rel_time) / random_uniform
        import random
        r = max(1e-9, random.random())
        weight = math.exp(self.alpha * rel_time) / r

        item = (weight, rel_time, float(val))
        if len(self.values) < self.size:
            self.values.append(item)
            if len(self.values) == self.size:
                self.values.sort(key=lambda x: x[0])
        else:
            if weight > self.values[0][0]:
                self.values[0] = item
                self.values.sort(key=lambda x: x[0])

    def get_percentile(self, p: float) -> float:
        """Calculates percentile (0 <= p <= 100) taking exponential decay into account."""
        if not self.values:
            return 0.0
        # Sort values by data value
        data = sorted([item[2] for item in self.values])
        k = (len(data) - 1) * (max(0.0, min(100.0, float(p))) / 100.0)
        f = int(math.floor(k))
        c = int(math.ceil(k))
        if f == c:
            return data[f]
        return round(data[f] * (c - k) + data[c] * (k - f), 4)


class EWMAAnomalyDetector:
    """Exponentially Weighted Moving Average and standard deviation anomaly detector."""

    def __init__(self, alpha: float = 0.2, threshold_z: float = 3.0):
        self.alpha = float(alpha)
        self.threshold_z = float(threshold_z)
        self.mean: Optional[float] = None
        self.variance: float = 0.0

    def update(self, val: float) -> Dict[str, Any]:
        """Observes a value and flags statistical anomalies based on z-score."""
        x = float(val)

        if self.mean is None:
            self.mean = x
            self.variance = 0.0
            return {
                "value": x,
                "mean": x,
                "std": 0.0,
                "z_score": 0.0,
                "is_anomaly": False,
            }

        prev_mean = self.mean
        prev_std = math.sqrt(max(1e-9, self.variance))
        z = (x - prev_mean) / prev_std
        is_anomaly = abs(z) >= self.threshold_z

        # Update mean
        self.mean = self.alpha * x + (1.0 - self.alpha) * prev_mean

        # Update variance
        delta = x - prev_mean
        self.variance = (1.0 - self.alpha) * (self.variance + self.alpha * (delta ** 2))
        std = math.sqrt(max(1e-9, self.variance))

        return {
            "value": x,
            "mean": round(self.mean, 4),
            "std": round(std, 4),
            "z_score": round(z, 3),
            "is_anomaly": is_anomaly,
        }


def metrics_export_otlp_traces(spans: List[TraceSpan], service_name: str = "doomscript-app") -> Dict[str, Any]:
    """Serializes spans into OpenTelemetry trace dictionary."""
    return OTLPTraceExporter.export_spans(spans, service_name=service_name)


def metrics_create_ewma_detector(alpha: float = 0.2, threshold_z: float = 3.0) -> EWMAAnomalyDetector:
    """Creates a new streaming EWMA anomaly detector."""
    return EWMAAnomalyDetector(alpha, threshold_z)
