"""Digital Signal Processing, Wavelets & Filters Domain Pack for DoomScript.

Enables native spoken-English Discrete Wavelet Transforms (Haar/db4), FIR/IIR filtering,
Hilbert analytic signal extraction, and peak detection via 'use signals'.
"""

from typing import List, Optional, Dict, Any
from doomscript.domains.base import (
    DomainContract,
    DomainParser,
    DomainRuntime,
    DomainASTExporter,
    DomainIR,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.signals.runtime import (
    WaveletTransform,
    FilterDesign,
    SignalAnalytics,
    signals_haar_dwt,
    signals_haar_idwt,
    signals_db4_dwt,
    signals_fir_lowpass,
    signals_butterworth_filter,
    signals_hilbert,
    signals_find_peaks,
    STFTSpectrogram,
    SavitzkyGolayFilter,
    signals_stft,
    signals_savitzky_golay,
    CooleyTukeyFFT,
    HilbertTransform,
    CrossCorrelation,
    PeakDetector,
    LombScarglePeriodogram,
    signals_fft,
    signals_ifft,
    signals_cross_correlation,
    signals_detect_pitch,
    signals_lomb_scargle,
)
from doomscript.domains.signals.parser import SignalsDomainParser
from doomscript.domains.signals.exporter import SignalsASTExporter


class SignalsRuntime(DomainRuntime):
    """Runtime coordinator for signals routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


class SignalsDomain(DomainContract):
    """Domain contract for Digital Signal Processing & Wavelets."""

    name = "signals"
    aliases = ["dsp", "filtering", "wavelets"]
    description = "Discrete Wavelet Transform, FIR/IIR filters, Hilbert transform, and peak detection"
    parser = SignalsDomainParser()
    runtime = SignalsRuntime()
    exporter = SignalsASTExporter()
    capabilities = ["haar_dwt", "db4_dwt", "fir_filter", "iir_butterworth", "hilbert", "peak_detection"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="decompose signal {sig:expr} using haar wavelet into {target:ident}",
            description="Performs 1D Haar Discrete Wavelet Transform",
        ),
        VerbSpec(
            pattern="apply fir lowpass filter to {sig:expr} with cutoff {cut:expr} and rate {rate:expr} into {target:ident}",
            description="Applies windowed-sinc FIR lowpass filter to signal",
        ),
        VerbSpec(
            pattern="calculate analytic signal of {sig:expr} using hilbert into {target:ident}",
            description="Computes analytic signal and amplitude envelope via Hilbert transform",
        ),
        VerbSpec(
            pattern="find peaks in signal {sig:expr} into {target:ident}",
            description="Detects local maxima peaks in signal",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("decompose signal ")
            or s.startswith("apply fir lowpass filter to ")
            or s.startswith("calculate analytic signal of ")
            or s.startswith("find peaks in signal ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


SIGNALS_DOMAIN = SignalsDomain()
get_domain_registry().register(SIGNALS_DOMAIN)

__all__ = [
    "SignalsDomain",
    "SIGNALS_DOMAIN",
    "SignalsRuntime",
    "WaveletTransform",
    "FilterDesign",
    "SignalAnalytics",
    "signals_haar_dwt",
    "signals_haar_idwt",
    "signals_db4_dwt",
    "signals_fir_lowpass",
    "signals_butterworth_filter",
    "signals_hilbert",
    "signals_find_peaks",
    "STFTSpectrogram",
    "SavitzkyGolayFilter",
    "signals_stft",
    "signals_savitzky_golay",
]
