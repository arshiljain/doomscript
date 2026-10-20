"""Metrics, Observability & Prometheus Telemetry Domain Pack for DoomScript.

Enables native spoken-English Counters, Gauges, Histograms, Quantiles, and Prometheus export
via 'use metrics'.
"""

from typing import List, Optional, Dict, Any
from doomscript.domains.base import (
    DomainContract,
    DomainRuntime,
    DomainIR,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.metrics.runtime import (
    Counter,
    Gauge,
    Histogram,
    QuantileReservoir,
    TraceSpan,
    MetricsRegistry,
    metrics_counter,
    metrics_gauge,
    metrics_histogram,
    metrics_calculate_percentile,
    metrics_export_prometheus,
    metrics_clear,
    OTLPTraceExporter,
    ExponentialDecayReservoir,
    EWMAAnomalyDetector,
    metrics_export_otlp_traces,
    metrics_create_ewma_detector,
)
from doomscript.domains.metrics.parser import MetricsDomainParser
from doomscript.domains.metrics.exporter import MetricsASTExporter


class MetricsRuntime(DomainRuntime):
    """Runtime coordinator for metrics routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


class MetricsDomain(DomainContract):
    """Domain contract for Metrics & Prometheus Telemetry."""

    name = "metrics"
    aliases = ["telemetry", "prometheus", "observability", "stats"]
    description = "Prometheus-compatible counters, gauges, histograms, quantiles, and OpenMetrics plaintext export"
    parser = MetricsDomainParser()
    runtime = MetricsRuntime()
    exporter = MetricsASTExporter()
    capabilities = ["counter", "gauge", "histogram", "percentile", "prometheus"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="create counter {name:expr} into {target:ident}",
            description="Creates or retrieves a monotonic counter",
        ),
        VerbSpec(
            pattern="create gauge {name:expr} into {target:ident}",
            description="Creates or retrieves a gauge metric",
        ),
        VerbSpec(
            pattern="export openmetrics into {target:ident}",
            description="Exports all registered metrics to OpenMetrics format",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("create counter ")
            or s.startswith("create gauge ")
            or s.startswith("export openmetrics ")
            or s.startswith("export domain metrics ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


METRICS_DOMAIN = MetricsDomain()
get_domain_registry().register(METRICS_DOMAIN)

__all__ = [
    "MetricsDomain",
    "METRICS_DOMAIN",
    "MetricsRuntime",
    "Counter",
    "Gauge",
    "Histogram",
    "QuantileReservoir",
    "TraceSpan",
    "MetricsRegistry",
    "metrics_counter",
    "metrics_gauge",
    "metrics_histogram",
    "metrics_calculate_percentile",
    "metrics_export_openmetrics",
    "metrics_export_prometheus",
    "metrics_clear",
    "OTLPTraceExporter",
    "ExponentialDecayReservoir",
    "EWMAAnomalyDetector",
    "metrics_export_otlp_traces",
    "metrics_create_ewma_detector",
]
