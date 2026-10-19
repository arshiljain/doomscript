"""Time Series Analysis, Forecasting & Decomposition Domain for DoomScript.

Provides 100% pure Python implementations of:
- Classical Additive & Multiplicative Seasonal Decomposition (Trend, Seasonal, Residual)
- Sample Autocorrelation Function (ACF)
- Partial Autocorrelation Function (PACF) via Durbin-Levinson recursion
- Holt-Winters Triple Exponential Smoothing (additive and multiplicative)
- Series Differencing and Lag Operations
Zero external dependencies.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple, Union


class TimeSeriesDifferencer:
    """Computes ordinary and seasonal differences for stationarity."""

    @staticmethod
    def difference(series: List[float], order: int = 1, seasonal_lag: int = 1) -> List[float]:
        """Applies lag-d differencing iteratively."""
        cur = list(series)
        for _ in range(order):
            if len(cur) <= seasonal_lag:
                return []
            cur = [cur[i] - cur[i - seasonal_lag] for i in range(seasonal_lag, len(cur))]
        return cur

    @staticmethod
    def invert_difference(diffed: List[float], initial_values: List[float], seasonal_lag: int = 1) -> List[float]:
        """Inverts differencing back to the original scale."""
        restored = list(initial_values)
        for d in diffed:
            val = d + restored[-seasonal_lag]
            restored.append(val)
        return restored


class AutocorrelationAnalyzer:
    """Calculates Sample Autocorrelation (ACF) and Partial Autocorrelation (PACF)."""

    @staticmethod
    def acf(series: List[float], nlags: int = 10) -> List[float]:
        """Computes sample autocorrelation function up to nlags."""
        n = len(series)
        if n == 0:
            return []
        mean_val = sum(series) / n
        var_val = sum((x - mean_val) ** 2 for x in series)
        if var_val == 0:
            return [1.0] + [0.0] * min(nlags, n - 1)

        result: List[float] = [1.0]
        max_lag = min(nlags, n - 1)
        for k in range(1, max_lag + 1):
            cov = sum((series[t] - mean_val) * (series[t + k] - mean_val) for t in range(n - k))
            result.append(round(cov / var_val, 4))
        return result

    @staticmethod
    def pacf(series: List[float], nlags: int = 10) -> List[float]:
        """Computes partial autocorrelation function up to nlags using Durbin-Levinson recursion."""
        r = AutocorrelationAnalyzer.acf(series, nlags)
        if not r:
            return []
        k_max = len(r) - 1
        if k_max == 0:
            return [1.0]

        phi: Dict[Tuple[int, int], float] = {}
        pacf_vals = [1.0]

        # k = 1
        phi[(1, 1)] = r[1]
        pacf_vals.append(round(phi[(1, 1)], 4))

        for k in range(2, k_max + 1):
            num = r[k] - sum(phi[(k - 1, j)] * r[k - j] for j in range(1, k))
            den = 1.0 - sum(phi[(k - 1, j)] * r[j] for j in range(1, k))
            if abs(den) < 1e-12:
                phi_kk = 0.0
            else:
                phi_kk = num / den
            phi[(k, k)] = phi_kk
            pacf_vals.append(round(phi_kk, 4))

            for j in range(1, k):
                phi[(k, j)] = phi[(k - 1, j)] - phi_kk * phi[(k - 1, k - j)]

        return pacf_vals


class TimeSeriesDecomposer:
    """Classical Additive and Multiplicative STL Seasonal Decomposition."""

    @staticmethod
    def decompose(
        series: List[float], period: int = 12, model: str = "additive"
    ) -> Dict[str, List[Optional[float]]]:
        """Decomposes series into trend, seasonal, and residual components."""
        n = len(series)
        if n < 2 * period:
            raise ValueError(f"Series length {n} is too short for period {period} (requires at least {2*period})")

        model_type = model.lower()
        if model_type not in ("additive", "multiplicative"):
            raise ValueError(f"Invalid model '{model}', must be 'additive' or 'multiplicative'")

        # 1. Estimate Trend via Moving Average
        trend: List[Optional[float]] = [None] * n
        half = period // 2

        if period % 2 == 1:
            # Odd period: simple symmetric moving average
            for i in range(half, n - half):
                trend[i] = sum(series[i - half : i + half + 1]) / period
        else:
            # Even period: 2xM centered moving average
            for i in range(half, n - half):
                s1 = sum(series[i - half : i + half])
                s2 = sum(series[i - half + 1 : i + half + 1])
                trend[i] = (s1 + s2) / (2.0 * period)

        # 2. Detrend series
        detrended: List[Optional[float]] = [None] * n
        for i in range(n):
            if trend[i] is not None:
                if model_type == "additive":
                    detrended[i] = series[i] - trend[i]
                else:
                    detrended[i] = series[i] / trend[i] if abs(trend[i]) > 1e-12 else 1.0

        # 3. Calculate Seasonal Component (average per cyclic phase)
        seasonal_averages: List[float] = [0.0] * period
        seasonal_counts: List[int] = [0] * period

        for i in range(n):
            if detrended[i] is not None:
                p_idx = i % period
                seasonal_averages[p_idx] += detrended[i]
                seasonal_counts[p_idx] += 1

        for p_idx in range(period):
            if seasonal_counts[p_idx] > 0:
                seasonal_averages[p_idx] /= seasonal_counts[p_idx]

        # Normalize seasonal averages
        if model_type == "additive":
            mean_season = sum(seasonal_averages) / period
            seasonal_averages = [s - mean_season for s in seasonal_averages]
        else:
            mean_season = sum(seasonal_averages) / period
            if mean_season > 0:
                seasonal_averages = [s / mean_season for s in seasonal_averages]

        seasonal: List[float] = [seasonal_averages[i % period] for i in range(n)]

        # 4. Residual Component
        residual: List[Optional[float]] = [None] * n
        for i in range(n):
            if trend[i] is not None:
                if model_type == "additive":
                    residual[i] = series[i] - trend[i] - seasonal[i]
                else:
                    denom = trend[i] * seasonal[i]
                    residual[i] = series[i] / denom if abs(denom) > 1e-12 else 1.0

        return {
            "trend": [round(x, 4) if x is not None else None for x in trend],
            "seasonal": [round(x, 4) for x in seasonal],
            "residual": [round(x, 4) if x is not None else None for x in residual],
        }


class ExponentialSmoothing:
    """Holt-Winters Triple Exponential Smoothing for Trend and Seasonality."""

    @staticmethod
    def forecast(
        series: List[float],
        period: int,
        alpha: float = 0.2,
        beta: float = 0.1,
        gamma: float = 0.3,
        n_preds: int = 5,
        model: str = "additive",
    ) -> List[float]:
        """Performs Holt-Winters smoothing and forecasts n_preds steps ahead."""
        n = len(series)
        if n < 2 * period:
            raise ValueError("Series length must be at least 2 seasonal periods")

        # Initial level and trend
        level = sum(series[:period]) / period
        trend = (sum(series[period : 2 * period]) - sum(series[:period])) / (period * period)

        # Initial seasonals
        seasonals: List[float] = [0.0] * period
        for i in range(period):
            if model == "additive":
                seasonals[i] = series[i] - level
            else:
                seasonals[i] = series[i] / level if level != 0 else 1.0

        # Run filter
        for i in range(n):
            val = series[i]
            s_idx = i % period
            last_level = level
            last_trend = trend

            if model == "additive":
                level = alpha * (val - seasonals[s_idx]) + (1 - alpha) * (last_level + last_trend)
                trend = beta * (level - last_level) + (1 - beta) * last_trend
                seasonals[s_idx] = gamma * (val - level) + (1 - gamma) * seasonals[s_idx]
            else:
                s_factor = seasonals[s_idx] if seasonals[s_idx] != 0 else 1.0
                level = alpha * (val / s_factor) + (1 - alpha) * (last_level + last_trend)
                trend = beta * (level - last_level) + (1 - beta) * last_trend
                seasonals[s_idx] = gamma * (val / level) + (1 - gamma) * seasonals[s_idx]

        # Forecast future points
        forecasts: List[float] = []
        for m in range(1, n_preds + 1):
            s_idx = (n + m - 1) % period
            if model == "additive":
                pred = level + m * trend + seasonals[s_idx]
            else:
                pred = (level + m * trend) * seasonals[s_idx]
            forecasts.append(round(pred, 4))

        return forecasts


# --- Public High-Level Runtime Functions ---

def time_series_decompose(
    series: List[float], period: int = 12, model: str = "additive"
) -> Dict[str, List[Optional[float]]]:
    """Decomposes a time series into trend, seasonal, and residual components."""
    return TimeSeriesDecomposer.decompose(series, period, model)


def time_series_acf(series: List[float], nlags: int = 10) -> List[float]:
    """Computes sample autocorrelation function up to nlags."""
    return AutocorrelationAnalyzer.acf(series, nlags)


def time_series_pacf(series: List[float], nlags: int = 10) -> List[float]:
    """Computes sample partial autocorrelation function up to nlags."""
    return AutocorrelationAnalyzer.pacf(series, nlags)


def time_series_holt_winters(
    series: List[float],
    period: int,
    alpha: float = 0.2,
    beta: float = 0.1,
    gamma: float = 0.3,
    n_preds: int = 5,
    model: str = "additive",
) -> List[float]:
    """Forecasts time series using Holt-Winters exponential smoothing."""
    return ExponentialSmoothing.forecast(series, period, alpha, beta, gamma, n_preds, model)


def time_series_difference(series: List[float], order: int = 1, seasonal_lag: int = 1) -> List[float]:
    """Applies lag-d differencing to remove trend or seasonality."""
    return TimeSeriesDifferencer.difference(series, order, seasonal_lag)
