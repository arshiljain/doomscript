"""Testing & Algorithm Analysis Domain Specification and Intermediate Representation (IR)."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from doomscript.domains.base import DomainIR


@dataclass
class BenchmarkSpec(DomainIR):
    """Specification for algorithm benchmarking and empirical complexity analysis."""

    fn_name: str
    input_sizes: List[int] = field(default_factory=lambda: [100, 500, 1000, 5000])
    repeat: int = 5
    measure_memory: bool = True
    generator: str = "sorted_integers"  # "sorted_integers", "random_integers", "reversed_integers"
    target_var: str = "benchmark_results"

    def validate(self) -> List[str]:
        errors = []
        if not self.fn_name:
            errors.append("Benchmark function name cannot be empty")
        if not self.input_sizes:
            errors.append("Benchmark requires at least one input size")
        if any(s <= 0 for s in self.input_sizes):
            errors.append("All input sizes must be positive integers")
        if self.repeat <= 0:
            errors.append(f"Repeat count must be >= 1, got {self.repeat}")
        return errors


@dataclass
class ComplexityReport:
    """Empirical complexity analysis report."""

    fn_name: str
    best_fit: str  # "O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)"
    confidence_r2: float
    timings: Dict[int, float] = field(default_factory=dict)
    peak_memory_bytes: int = 0
    fits: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fn_name": self.fn_name,
            "best_fit": self.best_fit,
            "complexity_class": self.best_fit,
            "confidence_r2": round(self.confidence_r2, 4),
            "timings": {s: round(t, 6) for s, t in self.timings.items()},
            "peak_memory_bytes": self.peak_memory_bytes,
            "all_fits": {k: round(v, 4) for k, v in self.fits.items()},
        }
