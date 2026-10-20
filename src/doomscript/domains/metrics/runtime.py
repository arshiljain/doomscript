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
from doomscript.core.record import Record


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
    res = _REGISTRY.export_prometheus()
    if not res or not res.strip():
        try:
            from doomscript.runtime_extended import _METRICS
            return _METRICS.render_prometheus()
        except Exception:
            pass
    return res


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


# ==============================================================================
# NON-PARAMETRIC STATISTICAL TESTS & KERNEL DENSITY ESTIMATION
# ==============================================================================

class NonParametricMannWhitneyU:
    """Two-sample Mann-Whitney U test (Wilcoxon rank-sum) with tie correction and continuity."""

    @classmethod
    def test(cls, sample1: List[float], sample2: List[float]) -> Dict[str, Any]:
        n1 = len(sample1)
        n2 = len(sample2)
        if n1 == 0 or n2 == 0:
            return {
                "u_statistic": 0.0,
                "u1": 0.0,
                "u2": 0.0,
                "z_score": 0.0,
                "p_value": 1.0,
                "significant_05": False,
                "n1": n1,
                "n2": n2,
            }

        # Combine and sort with group tagging
        combined = [(float(x), 1) for x in sample1] + [(float(y), 2) for y in sample2]
        combined.sort(key=lambda item: item[0])

        # Assign average ranks for ties
        n_total = n1 + n2
        ranks = [0.0] * n_total
        i = 0
        tie_sum = 0

        while i < n_total:
            j = i
            while j < n_total - 1 and combined[j][0] == combined[j + 1][0]:
                j += 1
            tie_len = j - i + 1
            if tie_len > 1:
                tie_sum += (tie_len ** 3) - tie_len
            avg_rank = (i + 1 + j + 1) / 2.0
            for k in range(i, j + 1):
                ranks[k] = avg_rank
            i = j + 1

        # Sum of ranks for sample 1
        r1 = sum(ranks[k] for k in range(n_total) if combined[k][1] == 1)
        r2 = sum(ranks[k] for k in range(n_total) if combined[k][1] == 2)

        u1 = r1 - (n1 * (n1 + 1)) / 2.0
        u2 = (n1 * n2) - u1
        u_stat = min(u1, u2)

        # Asymptotic normal approximation with tie correction
        mean_u = (n1 * n2) / 2.0
        tie_term = (n1 * n2 * tie_sum) / (12.0 * n_total * (n_total - 1)) if n_total > 1 else 0.0
        var_u = (n1 * n2 * (n_total + 1)) / 12.0 - tie_term
        std_u = math.sqrt(max(1e-9, var_u))

        # Continuity correction
        diff = u_stat - mean_u
        correction = 0.5 if diff < 0 else (-0.5 if diff > 0 else 0.0)
        z_score = (diff + correction) / std_u

        # Two-tailed p-value via complementary error function
        p_val = math.erfc(abs(z_score) / math.sqrt(2.0))
        p_val = min(1.0, max(0.0, p_val))

        return {
            "u_statistic": round(u_stat, 4),
            "u1": round(u1, 4),
            "u2": round(u2, 4),
            "z_score": round(z_score, 4),
            "p_value": round(p_val, 6),
            "significant_05": bool(p_val < 0.05),
            "n1": n1,
            "n2": n2,
        }


class KolmogorovSmirnovTwoSample:
    """Two-sample Kolmogorov-Smirnov test for continuous distribution equality."""

    @classmethod
    def test(cls, sample1: List[float], sample2: List[float]) -> Dict[str, Any]:
        n1 = len(sample1)
        n2 = len(sample2)
        if n1 == 0 or n2 == 0:
            return {
                "d_statistic": 0.0,
                "p_value": 1.0,
                "significant_05": False,
                "n1": n1,
                "n2": n2,
            }

        s1 = sorted([float(x) for x in sample1])
        s2 = sorted([float(y) for y in sample2])

        # Step through unified sorted values
        i1 = 0
        i2 = 0
        d_max = 0.0

        all_vals = sorted(list(set(s1 + s2)))
        for val in all_vals:
            while i1 < n1 and s1[i1] <= val:
                i1 += 1
            while i2 < n2 and s2[i2] <= val:
                i2 += 1
            cdf1 = i1 / n1
            cdf2 = i2 / n2
            diff = abs(cdf1 - cdf2)
            if diff > d_max:
                d_max = diff

        # Asymptotic p-value approximation
        ne = (n1 * n2) / (n1 + n2)
        lam = (math.sqrt(ne) + 0.12 + 0.11 / math.sqrt(ne)) * d_max

        # Kolmogorov distribution sum
        p_val = 0.0
        for j in range(1, 101):
            term = 2.0 * ((-1) ** (j - 1)) * math.exp(-2.0 * (j ** 2) * (lam ** 2))
            p_val += term
            if abs(term) < 1e-12:
                break
        p_val = min(1.0, max(0.0, p_val))

        return {
            "d_statistic": round(d_max, 6),
            "p_value": round(p_val, 6),
            "significant_05": bool(p_val < 0.05),
            "n1": n1,
            "n2": n2,
        }


class KernelDensityEstimator1D:
    """1D Non-parametric Kernel Density Estimation (KDE) with Gaussian & Epanechnikov kernels."""

    def __init__(
        self,
        data: List[float],
        bandwidth: Optional[float] = None,
        kernel: str = "gaussian",
    ):
        self.data = sorted([float(x) for x in data])
        self.n = len(self.data)
        self.kernel = kernel.lower()

        if bandwidth is not None and bandwidth > 0:
            self.h = float(bandwidth)
        else:
            # Silverman's rule of thumb
            if self.n > 1:
                mean_val = sum(self.data) / self.n
                variance = sum((x - mean_val) ** 2 for x in self.data) / (self.n - 1)
                std_dev = math.sqrt(max(1e-6, variance))
                self.h = 1.06 * std_dev * (self.n ** (-0.2))
            else:
                self.h = 1.0

    def _kernel_eval(self, u: float) -> float:
        if self.kernel == "epanechnikov":
            if abs(u) <= 1.0:
                return 0.75 * (1.0 - u * u)
            return 0.0
        # Default Gaussian
        return (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * u * u)

    def evaluate_point(self, x: float) -> float:
        """Evaluates probability density at single point x."""
        if self.n == 0:
            return 0.0
        s = sum(self._kernel_eval((x - xi) / self.h) for xi in self.data)
        return s / (self.n * self.h)

    def evaluate_grid(self, points: List[float]) -> List[float]:
        """Evaluates probability density over an array of points."""
        return [round(self.evaluate_point(pt), 6) for pt in points]

    def find_peaks(self, num_grid_pts: int = 100) -> List[float]:
        """Finds modal peak coordinates along the empirical range."""
        if self.n == 0:
            return []
        min_x = self.data[0] - 2 * self.h
        max_x = self.data[-1] + 2 * self.h
        step = (max_x - min_x) / max(1, num_grid_pts - 1)

        grid_x = [min_x + i * step for i in range(num_grid_pts)]
        densities = [self.evaluate_point(x) for x in grid_x]

        peaks = []
        for i in range(1, num_grid_pts - 1):
            if densities[i] > densities[i - 1] and densities[i] > densities[i + 1]:
                peaks.append(round(grid_x[i], 4))
        return peaks


def metrics_mann_whitney_u(sample1: List[float], sample2: List[float]) -> Any:
    """Computes Mann-Whitney U rank-sum test between two independent samples."""
    return Record(NonParametricMannWhitneyU.test(sample1, sample2))


def metrics_kolmogorov_smirnov_2samp(sample1: List[float], sample2: List[float]) -> Any:
    """Computes two-sample Kolmogorov-Smirnov test."""
    return Record(KolmogorovSmirnovTwoSample.test(sample1, sample2))


def metrics_kde_create(
    data: List[float],
    bandwidth: Optional[float] = None,
    kernel: str = "gaussian",
) -> Any:
    """Constructs a 1D Kernel Density Estimator record."""
    kde = KernelDensityEstimator1D(data, bandwidth=bandwidth, kernel=kernel)
    return Record({
        "bandwidth": round(kde.h, 6),
        "kernel": kde.kernel,
        "n_samples": kde.n,
        "instance": kde,
    })


def metrics_kde_evaluate(kde: Any, points: List[float]) -> List[float]:
    """Evaluates KDE probability density at query points."""
    inst = kde.instance if hasattr(kde, "instance") else kde
    return inst.evaluate_grid(points)


class WassersteinDistance1D:
    """Computes first Wasserstein distance (Earth Mover's Distance) between 1D empirical distributions."""

    @classmethod
    def compute(
        cls,
        u_samples: List[float],
        v_samples: List[float],
        u_weights: Optional[List[float]] = None,
        v_weights: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        u = [float(x) for x in u_samples]
        v = [float(x) for x in v_samples]
        n_u = len(u)
        n_v = len(v)
        if n_u == 0 or n_v == 0:
            return {"wasserstein_distance": 0.0, "samples_u_count": n_u, "samples_v_count": n_v}

        u_sorted = sorted(u)
        v_sorted = sorted(v)

        if n_u == n_v and (u_weights is None and v_weights is None):
            dist = sum(abs(u_sorted[i] - v_sorted[i]) for i in range(n_u)) / n_u
        else:
            all_vals = sorted(list(set(u + v)))
            w_u = [1.0 / n_u] * n_u if u_weights is None else [float(w) / sum(u_weights) for w in u_weights]
            w_v = [1.0 / n_v] * n_v if v_weights is None else [float(w) / sum(v_weights) for w in v_weights]

            u_pairs = sorted(zip(u, w_u), key=lambda item: item[0])
            v_pairs = sorted(zip(v, w_v), key=lambda item: item[0])

            dist = 0.0
            idx_u = 0
            idx_v = 0
            cum_u = 0.0
            cum_v = 0.0

            for i in range(len(all_vals) - 1):
                x_curr = all_vals[i]
                x_next = all_vals[i + 1]
                dx = x_next - x_curr

                while idx_u < n_u and u_pairs[idx_u][0] <= x_curr:
                    cum_u += u_pairs[idx_u][1]
                    idx_u += 1
                while idx_v < n_v and v_pairs[idx_v][0] <= x_curr:
                    cum_v += v_pairs[idx_v][1]
                    idx_v += 1

                dist += abs(cum_u - cum_v) * dx

        return {
            "wasserstein_distance": round(dist, 6),
            "samples_u_count": n_u,
            "samples_v_count": n_v,
        }


class MulticlassROCAUCIntegrator:
    """Computes One-vs-Rest ROC curves, trapezoidal AUC integration, and macro/micro averages."""

    @classmethod
    def compute(
        cls,
        y_true: List[int],
        y_prob_matrix: List[List[float]],
        num_classes: int,
    ) -> Dict[str, Any]:
        k = int(num_classes)
        n = len(y_true)
        if n == 0 or k <= 1:
            return {"macro_auc": 0.0, "micro_auc": 0.0, "classes_count": k, "per_class_auc": []}

        y_t = [int(y) for y in y_true]
        probs = [[float(p) for p in row] for row in y_prob_matrix]

        def binary_roc_auc(binary_labels: List[int], scores: List[float]) -> Tuple[float, List[Dict[str, float]]]:
            paired = sorted(zip(scores, binary_labels), key=lambda item: item[0], reverse=True)
            pos_count = sum(binary_labels)
            neg_count = len(binary_labels) - pos_count
            if pos_count == 0 or neg_count == 0:
                return 0.5, []

            tp = 0
            fp = 0
            roc_points = [{"fpr": 0.0, "tpr": 0.0}]
            auc = 0.0
            prev_fpr = 0.0
            prev_tpr = 0.0

            for s, label in paired:
                if label == 1:
                    tp += 1
                else:
                    fp += 1
                fpr = fp / neg_count
                tpr = tp / pos_count
                auc += (fpr - prev_fpr) * (tpr + prev_tpr) / 2.0
                prev_fpr = fpr
                prev_tpr = tpr
                roc_points.append({"fpr": round(fpr, 4), "tpr": round(tpr, 4)})

            return max(0.0, min(1.0, auc)), roc_points

        per_class_results = []
        class_aucs = []

        for c in range(k):
            bin_labels = [1 if y == c else 0 for y in y_t]
            c_scores = [probs[i][c] if c < len(probs[i]) else 0.0 for i in range(n)]
            c_auc, pts = binary_roc_auc(bin_labels, c_scores)
            class_aucs.append(c_auc)
            per_class_results.append({
                "class_index": c,
                "auc": round(c_auc, 4),
                "num_positive": sum(bin_labels),
            })

        macro_auc = sum(class_aucs) / k if k > 0 else 0.0

        all_labels = []
        all_scores = []
        for c in range(k):
            for i in range(n):
                all_labels.append(1 if y_t[i] == c else 0)
                all_scores.append(probs[i][c] if c < len(probs[i]) else 0.0)

        micro_auc, _ = binary_roc_auc(all_labels, all_scores)

        return {
            "classes_count": k,
            "samples_count": n,
            "macro_auc": round(macro_auc, 4),
            "micro_auc": round(micro_auc, 4),
            "per_class_auc": [Record(r) for r in per_class_results],
        }


def metrics_wasserstein_distance_1d(
    u_samples: List[float],
    v_samples: List[float],
    u_weights: Optional[List[float]] = None,
    v_weights: Optional[List[float]] = None,
) -> Any:
    """Computes first Wasserstein distance (Earth Mover's Distance) between 1D distributions."""
    return Record(WassersteinDistance1D.compute(u_samples, v_samples, u_weights=u_weights, v_weights=v_weights))


def metrics_multiclass_roc_auc(
    y_true: List[int],
    y_prob_matrix: List[List[float]],
    num_classes: int,
) -> Any:
    """Computes multi-class One-vs-Rest ROC curve and macro/micro AUC scores."""
    return Record(MulticlassROCAUCIntegrator.compute(y_true, y_prob_matrix, num_classes))


# ==============================================================================
# MULTICLASS CONFUSION METRICS & PRECISION-RECALL AVERAGE PRECISION (AP)
# ==============================================================================


class ConfusionMatrixMultiClassMetrics:
    """Computes full multi-class classification metrics: macro/micro/weighted F1,
    Cohen's Kappa, and Gorodkin's multi-class Matthews Correlation Coefficient (MCC).
    """

    @classmethod
    def compute(
        cls,
        y_true: List[Any],
        y_pred: List[Any],
        labels: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        if len(y_true) != len(y_pred):
            raise ValueError(f"Lengths differ: len(y_true)={len(y_true)} vs len(y_pred)={len(y_pred)}")

        n = len(y_true)
        if n == 0:
            return {"sample_count": 0, "accuracy": 0.0, "mcc": 0.0, "cohen_kappa": 0.0}

        if labels is None:
            unique_labels = sorted(list(set(y_true) | set(y_pred)))
        else:
            unique_labels = list(labels)

        k = len(unique_labels)
        lbl_to_idx = {lbl: i for i, lbl in enumerate(unique_labels)}

        matrix = [[0] * k for _ in range(k)]
        for yt, yp in zip(y_true, y_pred):
            if yt in lbl_to_idx and yp in lbl_to_idx:
                matrix[lbl_to_idx[yt]][lbl_to_idx[yp]] += 1

        # Diagonal and sums
        diag = sum(matrix[i][i] for i in range(k))
        row_sums = [sum(matrix[i]) for i in range(k)]
        col_sums = [sum(matrix[i][j] for i in range(k)) for j in range(k)]

        accuracy = diag / n

        # Per-class precision, recall, f1, specificity
        per_class = []
        precisions, recalls, f1s = [], [], []
        supports = []

        for i, lbl in enumerate(unique_labels):
            tp = matrix[i][i]
            fp = col_sums[i] - tp
            fn = row_sums[i] - tp
            tn = n - (tp + fp + fn)

            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2.0 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
            spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
            supp = row_sums[i]

            precisions.append(prec)
            recalls.append(rec)
            f1s.append(f1)
            supports.append(supp)

            per_class.append({
                "label": lbl,
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "specificity": round(spec, 4),
                "support": supp,
            })

        # Macro averages
        macro_prec = sum(precisions) / k if k > 0 else 0.0
        macro_rec = sum(recalls) / k if k > 0 else 0.0
        macro_f1 = sum(f1s) / k if k > 0 else 0.0

        # Weighted averages
        total_supp = sum(supports)
        weighted_prec = (
            sum(p * s for p, s in zip(precisions, supports)) / total_supp if total_supp > 0 else 0.0
        )
        weighted_rec = (
            sum(r * s for r, s in zip(recalls, supports)) / total_supp if total_supp > 0 else 0.0
        )
        weighted_f1 = (
            sum(f * s for f, s in zip(f1s, supports)) / total_supp if total_supp > 0 else 0.0
        )

        # Cohen's Kappa
        p_o = accuracy
        p_e = sum(row_sums[i] * col_sums[i] for i in range(k)) / (n * n) if n > 0 else 0.0
        kappa = (p_o - p_e) / (1.0 - p_e) if (1.0 - p_e) > 0 else 0.0

        # Gorodkin's Multiclass MCC
        c = diag
        s = n
        p_rc = sum(row_sums[i] * col_sums[i] for i in range(k))
        p_row2 = sum(r * r for r in row_sums)
        p_col2 = sum(c * c for c in col_sums)
        num_mcc = c * s - p_rc
        den_mcc = math.sqrt(max(0.0, s * s - p_row2)) * math.sqrt(max(0.0, s * s - p_col2))
        mcc = num_mcc / den_mcc if den_mcc > 0 else 0.0

        return {
            "sample_count": n,
            "classes_count": k,
            "labels": unique_labels,
            "confusion_matrix": matrix,
            "accuracy": round(accuracy, 4),
            "macro_precision": round(macro_prec, 4),
            "macro_recall": round(macro_rec, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "cohen_kappa": round(kappa, 4),
            "matthews_corrcoef": round(mcc, 4),
            "per_class": [Record(r) for r in per_class],
        }


class PrecisionRecallCurveAP:
    """Computes binary Precision-Recall curve, Average Precision (AP), and optimal F-score threshold."""

    @classmethod
    def compute(
        cls,
        y_true: List[int],
        scores: List[float],
        pos_label: int = 1,
    ) -> Dict[str, Any]:
        if len(y_true) != len(scores):
            raise ValueError("y_true and scores must have same length")

        paired = sorted(zip(scores, y_true), key=lambda x: x[0], reverse=True)
        total_pos = sum(1 for _, y in paired if y == pos_label)
        n = len(paired)

        if total_pos == 0 or n == 0:
            return {
                "average_precision": 0.0,
                "optimal_threshold": 0.0,
                "max_f1": 0.0,
                "curve_points_count": 0,
            }

        tp = 0
        fp = 0
        precisions = [1.0]
        recalls = [0.0]
        thresholds = []
        best_f1 = -1.0
        best_thresh = 0.5

        for score, y in paired:
            if y == pos_label:
                tp += 1
            else:
                fp += 1

            p = tp / (tp + fp)
            r = tp / total_pos
            f1 = 2.0 * p * r / (p + r) if (p + r) > 0 else 0.0

            precisions.append(p)
            recalls.append(r)
            thresholds.append(score)

            if f1 > best_f1:
                best_f1 = f1
                best_thresh = score

        # Average Precision (AP) via trapezoidal integration of P(R)
        ap = 0.0
        for i in range(1, len(recalls)):
            dr = recalls[i] - recalls[i - 1]
            ap += dr * precisions[i]

        return {
            "average_precision": round(ap, 4),
            "optimal_threshold": round(best_thresh, 4),
            "max_f1": round(best_f1, 4),
            "curve_points_count": len(recalls),
            "total_positive_samples": total_pos,
        }


def metrics_confusion_matrix_multiclass(
    y_true: List[Any],
    y_pred: List[Any],
    labels: Optional[List[Any]] = None,
) -> Any:
    """Computes multiclass confusion matrix and comprehensive macro/micro/MCC statistics."""
    return Record(ConfusionMatrixMultiClassMetrics.compute(y_true, y_pred, labels=labels))


def metrics_precision_recall_ap(
    y_true: List[int],
    scores: List[float],
    pos_label: int = 1,
) -> Any:
    """Computes Precision-Recall curve, Average Precision (AP), and optimal decision threshold."""
    return Record(PrecisionRecallCurveAP.compute(y_true, scores, pos_label=pos_label))


