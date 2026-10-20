"""Time Series Analysis, Forecasting & Decomposition Domain Pack for DoomScript.

Enables native spoken-English STL seasonal decomposition, autocorrelation (ACF/PACF),
and Holt-Winters exponential smoothing via 'use time_series'.
"""

from typing import List, Optional, Dict, Any
from doomscript.domains.base import (
    DomainContract,
    DomainRuntime,
    DomainIR,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.time_series.runtime import (
    TimeSeriesDifferencer,
    AutocorrelationAnalyzer,
    TimeSeriesDecomposer,
    ExponentialSmoothing,
    time_series_decompose,
    time_series_acf,
    time_series_pacf,
    time_series_holt_winters,
    time_series_difference,
    ARIMASimulator,
    DynamicTimeWarping,
    CUSUMDetector,
    HoltWintersSmoothing,
    AutoregressiveModelAR,
    timeseries_holt_winters,
    timeseries_ar_forecast,
    DynamicTimeWarpingSakoeChiba,
    SpectralDensityPeriodogram,
    timeseries_dtw_sakoe_chiba,
    timeseries_spectral_periodogram,
    MultivariateVectorAutoregressionVAR,
    KalmanFilterStateSpace,
    timeseries_fit_var_model,
    timeseries_kalman_filter_smooth,
    NaturalCubicSpline,
    SeasonalARIMASARIMA,
    EmpiricalModeDecompositionEMD,
    timeseries_sarima_forecast,
    timeseries_emd_decompose,
)
from doomscript.domains.time_series.parser import TimeSeriesDomainParser
from doomscript.domains.time_series.exporter import TimeSeriesASTExporter


class TimeSeriesRuntime(DomainRuntime):
    """Runtime coordinator for time series routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


class TimeSeriesDomain(DomainContract):
    """Domain contract for Time Series Analysis & Forecasting."""

    name = "time_series"
    aliases = ["timeseries", "forecasting", "trend", "seasonality"]
    description = "Classical seasonal decomposition, ACF, PACF, Holt-Winters forecasting, and differencing"
    parser = TimeSeriesDomainParser()
    runtime = TimeSeriesRuntime()
    exporter = TimeSeriesASTExporter()
    capabilities = ["decompose", "acf", "pacf", "holt_winters", "difference"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="decompose time series {series:expr} with period {period:expr} into {target:ident}",
            description="Decomposes series into trend, seasonal, and residual components",
        ),
        VerbSpec(
            pattern="calculate acf of {series:expr} with lags {lags:expr} into {target:ident}",
            description="Calculates sample autocorrelation function up to specified lags",
        ),
        VerbSpec(
            pattern="calculate pacf of {series:expr} with lags {lags:expr} into {target:ident}",
            description="Calculates sample partial autocorrelation function via Durbin-Levinson",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("decompose time series ")
            or s.startswith("calculate acf of ")
            or s.startswith("calculate pacf of ")
            or s.startswith("forecast holt winters on ")
            or s.startswith("forecast ar model on ")
            or s.startswith("calculate sakoe chiba dtw ")
            or s.startswith("calculate spectral periodogram ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


TIME_SERIES_DOMAIN = TimeSeriesDomain()
get_domain_registry().register(TIME_SERIES_DOMAIN)

__all__ = [
    "TimeSeriesDomain",
    "TIME_SERIES_DOMAIN",
    "TimeSeriesRuntime",
    "TimeSeriesDifferencer",
    "AutocorrelationAnalyzer",
    "TimeSeriesDecomposer",
    "ExponentialSmoothing",
    "time_series_decompose",
    "time_series_acf",
    "time_series_pacf",
    "time_series_holt_winters",
    "time_series_difference",
    "ARIMASimulator",
    "DynamicTimeWarping",
    "CUSUMDetector",
    "HoltWintersSmoothing",
    "AutoregressiveModelAR",
    "timeseries_holt_winters",
    "timeseries_ar_forecast",
    "DynamicTimeWarpingSakoeChiba",
    "SpectralDensityPeriodogram",
    "timeseries_dtw_sakoe_chiba",
    "timeseries_spectral_periodogram",
    "MultivariateVectorAutoregressionVAR",
    "KalmanFilterStateSpace",
    "timeseries_fit_var_model",
    "timeseries_kalman_filter_smooth",
    "NaturalCubicSpline",
    "SeasonalARIMASARIMA",
    "EmpiricalModeDecompositionEMD",
    "timeseries_sarima_forecast",
    "timeseries_emd_decompose",
]
