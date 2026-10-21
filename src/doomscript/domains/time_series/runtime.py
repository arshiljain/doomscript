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
from doomscript.core.record import Record


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


# --- Deepened Time Series: ARIMA, Dynamic Time Warping & CUSUM ---

class ARIMASimulator:
    """Simulation, parameter estimation, and multi-step forecasting for ARIMA(p, d, q) processes."""

    @classmethod
    def simulate(
        cls,
        n: int,
        ar_params: Optional[List[float]] = None,
        d: int = 0,
        ma_params: Optional[List[float]] = None,
        constant: float = 0.0,
        sigma: float = 1.0,
        seed: int = 42,
    ) -> List[float]:
        """Simulates an ARIMA(p, d, q) time series with Gaussian white noise."""
        import random
        rng = random.Random(seed)
        p = len(ar_params) if ar_params else 0
        q = len(ma_params) if ma_params else 0
        ar = ar_params or []
        ma = ma_params or []

        burn_in = 50
        total_len = n + burn_in
        noise = [rng.gauss(0.0, sigma) for _ in range(total_len)]
        arma_series = [0.0] * total_len

        for t in range(total_len):
            val = constant + noise[t]
            for i in range(p):
                if t - 1 - i >= 0:
                    val += ar[i] * arma_series[t - 1 - i]
            for j in range(q):
                if t - 1 - j >= 0:
                    val += ma[j] * noise[t - 1 - j]
            arma_series[t] = val

        # Discard burn-in
        series = arma_series[burn_in:]

        # Apply cumulative sum d times if d > 0
        cur = series
        for _ in range(d):
            integrated = [cur[0]]
            for val in cur[1:]:
                integrated.append(integrated[-1] + val)
            cur = integrated

        return [round(x, 6) for x in cur]

    @classmethod
    def fit_ar(cls, series: List[float], p: int = 1) -> List[float]:
        """Estimates autoregressive AR(p) coefficients using least squares."""
        if len(series) <= p + 1:
            return [0.0] * p

        # Construct design matrix X and response y
        # y_t = phi_1 * y_{t-1} + ... + phi_p * y_{t-p}
        N = len(series) - p
        X: List[List[float]] = []
        y: List[float] = []

        for t in range(p, len(series)):
            row = [series[t - 1 - i] for i in range(p)]
            X.append(row)
            y.append(series[t])

        # Solve (X^T X) beta = X^T y via Gaussian elimination
        # Normal equations: M * beta = b
        M = [[0.0] * p for _ in range(p)]
        b = [0.0] * p
        for row, target in zip(X, y):
            for i in range(p):
                b[i] += row[i] * target
                for j in range(p):
                    M[i][j] += row[i] * row[j]

        # Regularize diagonal for numerical stability
        for i in range(p):
            M[i][i] += 1e-6

        # Forward Gaussian elimination
        for i in range(p):
            pivot = M[i][i]
            if abs(pivot) < 1e-12:
                continue
            for k in range(i + 1, p):
                factor = M[k][i] / pivot
                for j in range(i, p):
                    M[k][j] -= factor * M[i][j]
                b[k] -= factor * b[i]

        # Back-substitution
        coeffs = [0.0] * p
        for i in range(p - 1, -1, -1):
            if abs(M[i][i]) > 1e-12:
                coeffs[i] = (b[i] - sum(M[i][j] * coeffs[j] for j in range(i + 1, p))) / M[i][i]

        return [round(c, 6) for c in coeffs]

    @classmethod
    def forecast(
        cls,
        series: List[float],
        p: int = 1,
        d: int = 0,
        steps: int = 5,
        ar_params: Optional[List[float]] = None,
    ) -> List[float]:
        """Forecasts future points by differencing, applying AR model, and inverting difference."""
        from doomscript.domains.time_series.runtime import TimeSeriesDifferencer

        diffed = series
        diff_histories = []
        for _ in range(d):
            diff_histories.append(diffed[-1])
            diffed = TimeSeriesDifferencer.difference(diffed, order=1)
            if not diffed:
                return [series[-1]] * steps

        # Fit AR params if not provided
        coeffs = ar_params if ar_params is not None else cls.fit_ar(diffed, p=p)

        # Forecast in differenced domain
        history = list(diffed)
        forecasts = []
        for _ in range(steps):
            next_val = sum(coeffs[i] * history[-1 - i] for i in range(min(len(coeffs), len(history))))
            forecasts.append(next_val)
            history.append(next_val)

        # Invert differencing if d > 0
        cur_forecasts = forecasts
        for last_val in reversed(diff_histories):
            restored = []
            cum = last_val
            for f in cur_forecasts:
                cum += f
                restored.append(cum)
            cur_forecasts = restored

        return [round(x, 4) for x in cur_forecasts]


class DynamicTimeWarping:
    """Non-linear Dynamic Time Warping (DTW) distance and optimal alignment path."""

    @classmethod
    def align(
        cls,
        series1: List[float],
        series2: List[float],
        window: Optional[int] = None,
        dist_metric: str = "euclidean",
    ) -> Dict[str, Any]:
        """Computes DTW cost matrix, total alignment distance, and warping path."""
        n = len(series1)
        m = len(series2)
        if n == 0 or m == 0:
            return {"distance": 0.0, "normalized_distance": 0.0, "path": []}

        # Initialize cost matrix with infinity
        inf = float("inf")
        D = [[inf] * (m + 1) for _ in range(n + 1)]
        D[0][0] = 0.0

        w = max(window, abs(n - m)) if window is not None else max(n, m)

        for i in range(1, n + 1):
            low = max(1, i - w)
            high = min(m, i + w)
            for j in range(low, high + 1):
                if dist_metric == "manhattan":
                    d = abs(series1[i - 1] - series2[j - 1])
                else:
                    d = (series1[i - 1] - series2[j - 1]) ** 2

                min_prev = min(D[i - 1][j], D[i][j - 1], D[i - 1][j - 1])
                D[i][j] = d + min_prev

        total_cost = D[n][m]
        if dist_metric != "manhattan":
            total_dist = math.sqrt(total_cost) if total_cost != inf else inf
        else:
            total_dist = total_cost

        # Backtrack optimal warping path
        path = []
        i, j = n, m
        while i > 0 or j > 0:
            path.append((i - 1, j - 1))
            if i == 0:
                j -= 1
            elif j == 0:
                i -= 1
            else:
                prev_steps = [
                    (D[i - 1][j - 1], i - 1, j - 1),
                    (D[i - 1][j], i - 1, j),
                    (D[i][j - 1], i, j - 1),
                ]
                prev_steps.sort(key=lambda x: x[0])
                _, i, j = prev_steps[0]

        path.reverse()
        normalized = total_dist / max(1, len(path))

        return {
            "distance": round(total_dist, 6),
            "normalized_distance": round(normalized, 6),
            "path_length": len(path),
            "path": path,
        }


class CUSUMDetector:
    """Cumulative Sum (CUSUM) statistical control chart for mean-shift change point detection."""

    @classmethod
    def detect(
        cls,
        series: List[float],
        baseline_mean: Optional[float] = None,
        std_dev: Optional[float] = None,
        drift_k: Optional[float] = None,
        threshold_h: float = 4.0,
        reset_on_change: bool = True,
    ) -> Dict[str, Any]:
        """Detects upward and downward structural shifts in time series data."""
        if not series:
            return {"change_points": [], "pos_cusum": [], "neg_cusum": []}

        # Estimate parameters if not specified
        mu = baseline_mean if baseline_mean is not None else (sum(series) / len(series))
        if std_dev is None:
            var = sum((x - mu) ** 2 for x in series) / max(1, len(series) - 1)
            sigma = math.sqrt(var) if var > 1e-12 else 1.0
        else:
            sigma = max(1e-12, std_dev)

        k = drift_k if drift_k is not None else (0.5 * sigma)
        h = threshold_h * sigma

        pos_sum = 0.0
        neg_sum = 0.0
        pos_cusum: List[float] = []
        neg_cusum: List[float] = []
        change_points: List[Dict[str, Any]] = []

        for idx, val in enumerate(series):
            # Pos shift: accumulation of deviations above (mu + k)
            pos_sum = max(0.0, pos_sum + (val - mu - k))
            # Neg shift: accumulation of deviations below (mu - k)
            neg_sum = max(0.0, neg_sum - (val - mu + k))

            pos_cusum.append(round(pos_sum, 4))
            neg_cusum.append(round(neg_sum, 4))

            if pos_sum > h:
                change_points.append({
                    "index": idx,
                    "direction": "upward",
                    "value": val,
                    "cusum_score": round(pos_sum, 4),
                })
                if reset_on_change:
                    pos_sum = 0.0

            if neg_sum > h:
                change_points.append({
                    "index": idx,
                    "direction": "downward",
                    "value": val,
                    "cusum_score": round(neg_sum, 4),
                })
                if reset_on_change:
                    neg_sum = 0.0

        return {
            "baseline_mean": round(mu, 4),
            "std_dev": round(sigma, 4),
            "threshold_h": round(h, 4),
            "change_points": change_points,
            "pos_cusum": pos_cusum,
            "neg_cusum": neg_cusum,
        }


# ==============================================================================
# HOLT-WINTERS TRIPLE EXPONENTIAL SMOOTHING FORECASTER
# ==============================================================================

class HoltWintersSmoothing:
    """Holt-Winters triple exponential smoothing with level, trend, and seasonal components."""

    @classmethod
    def fit_forecast(
        cls,
        series: List[float],
        season_period: int = 4,
        alpha: float = 0.2,
        beta: float = 0.1,
        gamma: float = 0.3,
        forecast_steps: int = 4,
        multiplicative: bool = False,
    ) -> Dict[str, Any]:
        y = [float(v) for v in series]
        n = len(y)
        m = max(2, int(season_period))
        if n < 2 * m:
            raise ValueError(f"Series length {n} is too short for seasonal period {m} (needs at least 2*m)")

        # Initial level and trend from first 2 seasons
        l_prev = sum(y[:m]) / m
        b_prev = sum((y[m + i] - y[i]) / m for i in range(m)) / m

        # Initial seasonal indices
        if not multiplicative:
            s = [y[i] - l_prev for i in range(m)]
        else:
            s = [y[i] / max(1e-6, l_prev) for i in range(m)]

        fitted = []
        residuals = []

        for t in range(n):
            yt = y[t]
            s_idx = t % m
            s_val = s[s_idx]

            if not multiplicative:
                y_hat = l_prev + b_prev + s_val
                l_new = alpha * (yt - s_val) + (1.0 - alpha) * (l_prev + b_prev)
                b_new = beta * (l_new - l_prev) + (1.0 - beta) * b_prev
                s[s_idx] = gamma * (yt - l_new) + (1.0 - gamma) * s_val
            else:
                y_hat = (l_prev + b_prev) * s_val
                l_new = alpha * (yt / max(1e-6, s_val)) + (1.0 - alpha) * (l_prev + b_prev)
                b_new = beta * (l_new - l_prev) + (1.0 - beta) * b_prev
                s[s_idx] = gamma * (yt / max(1e-6, l_new)) + (1.0 - gamma) * s_val

            fitted.append(round(y_hat, 4))
            residuals.append(round(yt - y_hat, 4))
            l_prev = l_new
            b_prev = b_new

        # Compute multi-step out-of-sample forecast
        forecasts = []
        for h in range(1, forecast_steps + 1):
            s_idx = (n + h - 1) % m
            if not multiplicative:
                fh = l_prev + h * b_prev + s[s_idx]
            else:
                fh = (l_prev + h * b_prev) * s[s_idx]
            forecasts.append(round(fh, 4))

        # Metrics
        rmse = math.sqrt(sum(r * r for r in residuals) / n)
        mae = sum(abs(r) for r in residuals) / n

        return {
            "series_length": n,
            "season_period": m,
            "final_level": round(l_prev, 4),
            "final_trend": round(b_prev, 4),
            "forecasts": forecasts,
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            "multiplicative": multiplicative,
        }


# ==============================================================================
# AUTOREGRESSIVE MODEL AR(P) VIA YULE-WALKER
# ==============================================================================

class AutoregressiveModelAR:
    """Autoregressive AR(p) model fitting using Yule-Walker and Levinson-Durbin recursion."""

    @classmethod
    def fit_and_forecast(cls, series: List[float], order_p: int = 2, forecast_steps: int = 3) -> Dict[str, Any]:
        y = [float(v) for v in series]
        n = len(y)
        p = max(1, min(n - 2, int(order_p)))

        mean_y = sum(y) / n
        yc = [v - mean_y for v in y]

        # Sample autocovariance gamma_k for k = 0..p
        gamma = [0.0] * (p + 1)
        for k in range(p + 1):
            gamma[k] = sum(yc[t] * yc[t - k] for t in range(k, n)) / n

        if gamma[0] < 1e-12:
            return {"ar_coefficients": [0.0] * p, "forecasts": [round(mean_y, 4)] * forecast_steps}

        # Levinson-Durbin algorithm to solve Toeplitz system R * phi = r
        phi = [[0.0] * (p + 1) for _ in range(p + 1)]
        v = gamma[0]

        for k in range(1, p + 1):
            acc = sum(phi[k - 1][j] * gamma[k - j] for j in range(1, k))
            lambda_k = (gamma[k] - acc) / v
            phi[k][k] = lambda_k
            for j in range(1, k):
                phi[k][j] = phi[k - 1][j] - lambda_k * phi[k - 1][k - j]
            v = v * (1.0 - lambda_k * lambda_k)

        ar_coeffs = [round(phi[p][j], 4) for j in range(1, p + 1)]
        sigma_sq = max(1e-12, v)

        # AIC and BIC
        aic = round(n * math.log(sigma_sq) + 2.0 * p, 3)
        bic = round(n * math.log(sigma_sq) + p * math.log(n), 3)

        # Multi-step forecasting
        hist = list(yc)
        forecasts = []
        for _ in range(forecast_steps):
            pred_c = 0.0
            for j in range(p):
                pred_c += ar_coeffs[j] * hist[-1 - j]
            hist.append(pred_c)
            forecasts.append(round(pred_c + mean_y, 4))

        return {
            "order_p": p,
            "mean": round(mean_y, 4),
            "ar_coefficients": ar_coeffs,
            "noise_variance": round(sigma_sq, 6),
            "aic": aic,
            "bic": bic,
            "forecasts": forecasts,
        }


def timeseries_holt_winters(
    series: List[float],
    season_period: int = 4,
    forecast_steps: int = 4,
    multiplicative: bool = False,
) -> Any:
    """Fits Holt-Winters exponential smoothing and generates forecasts."""
    return Record(HoltWintersSmoothing.fit_forecast(series, season_period=season_period, forecast_steps=forecast_steps, multiplicative=multiplicative))


def timeseries_ar_forecast(
    series: List[float],
    order_p: int = 2,
    forecast_steps: int = 3,
) -> Any:
    """Fits AR(p) autoregressive model via Yule-Walker and forecasts future steps."""
    return Record(AutoregressiveModelAR.fit_and_forecast(series, order_p=order_p, forecast_steps=forecast_steps))


class DynamicTimeWarpingSakoeChiba:
    """Constrained Dynamic Time Warping using Sakoe-Chiba band window."""

    @classmethod
    def align(
        cls,
        series_a: List[float],
        series_b: List[float],
        band_window: int = 5,
    ) -> Dict[str, Any]:
        n = len(series_a)
        m = len(series_b)
        if n == 0 or m == 0:
            return {
                "alignment_cost": 0.0,
                "normalized_distance": 0.0,
                "path_length": 0,
                "warping_path": [],
            }

        w = max(int(band_window), abs(n - m))
        INF = float("inf")
        dp = [[INF] * (m + 1) for _ in range(n + 1)]
        dp[0][0] = 0.0

        for i in range(1, n + 1):
            j_start = max(1, i - w)
            j_end = min(m, i + w)
            for j in range(j_start, j_end + 1):
                cost = abs(float(series_a[i - 1]) - float(series_b[j - 1]))
                dp[i][j] = cost + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

        path = []
        i, j = n, m
        while i > 0 or j > 0:
            path.append([i - 1, j - 1])
            if i == 0:
                j -= 1
            elif j == 0:
                i -= 1
            else:
                prev_min = min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1])
                if prev_min == dp[i - 1][j - 1]:
                    i -= 1
                    j -= 1
                elif prev_min == dp[i - 1][j]:
                    i -= 1
                else:
                    j -= 1

        path.reverse()
        total_cost = dp[n][m] if dp[n][m] != INF else 0.0
        norm_dist = total_cost / max(len(path), 1)

        return {
            "alignment_cost": round(total_cost, 4),
            "normalized_distance": round(norm_dist, 4),
            "path_length": len(path),
            "warping_path": path,
        }


class SpectralDensityPeriodogram:
    """Discrete spectral power density periodogram estimation and peak detection."""

    @classmethod
    def analyze(
        cls,
        series: List[float],
        sampling_rate: float = 1.0,
        window_type: str = "hann",
        top_k_peaks: int = 3,
    ) -> Dict[str, Any]:
        data = [float(x) for x in series]
        n = len(data)
        if n == 0:
            return {
                "sampling_rate": sampling_rate,
                "frequencies_count": 0,
                "peak_frequencies": [],
                "spectral_entropy": 0.0,
                "total_power": 0.0,
            }

        mean_val = sum(data) / n
        centered = [x - mean_val for x in data]

        w_type = window_type.lower().strip()
        win = [1.0] * n
        if w_type == "hann" and n > 1:
            win = [0.5 * (1.0 - math.cos(2.0 * math.pi * i / (n - 1))) for i in range(n)]
        elif w_type == "hamming" and n > 1:
            win = [0.54 - 0.46 * math.cos(2.0 * math.pi * i / (n - 1)) for i in range(n)]
        elif w_type == "blackman" and n > 1:
            win = [0.42 - 0.5 * math.cos(2.0 * math.pi * i / (n - 1)) + 0.08 * math.cos(4.0 * math.pi * i / (n - 1)) for i in range(n)]

        win_sum_sq = sum(w * w for w in win) or 1.0
        tapered = [centered[i] * win[i] for i in range(n)]

        n_freqs = n // 2 + 1
        freqs = [k * sampling_rate / n for k in range(n_freqs)]
        psd = []

        for k in range(n_freqs):
            w = 2.0 * math.pi * k / n
            re_part = sum(tapered[t] * math.cos(w * t) for t in range(n))
            im_part = -sum(tapered[t] * math.sin(w * t) for t in range(n))
            mag_sq = re_part * re_part + im_part * im_part
            factor = 2.0 if 0 < k < (n / 2.0) else 1.0
            power = (factor * mag_sq) / (sampling_rate * win_sum_sq)
            psd.append(power)

        total_power = sum(psd)

        entropy = 0.0
        if total_power > 1e-12:
            for p in psd:
                p_norm = p / total_power
                if p_norm > 1e-12:
                    entropy -= p_norm * math.log2(p_norm)

        indexed_peaks = []
        for k in range(1, n_freqs):
            indexed_peaks.append((psd[k], freqs[k]))
        indexed_peaks.sort(key=lambda item: item[0], reverse=True)
        top_peaks = [
            {"frequency_hz": round(f, 4), "power": round(p, 4)}
            for p, f in indexed_peaks[:max(1, top_k_peaks)]
        ]

        return {
            "sampling_rate": sampling_rate,
            "window_applied": w_type,
            "frequencies_count": n_freqs,
            "total_power": round(total_power, 4),
            "spectral_entropy": round(entropy, 4),
            "peak_frequencies": [Record(pk) for pk in top_peaks],
        }


def timeseries_dtw_sakoe_chiba(
    series_a: List[float],
    series_b: List[float],
    band_window: int = 5,
) -> Any:
    """Calculates Sakoe-Chiba band constrained Dynamic Time Warping distance and path."""
    return Record(DynamicTimeWarpingSakoeChiba.align(series_a, series_b, band_window=band_window))


def timeseries_spectral_periodogram(
    series: List[float],
    sampling_rate: float = 1.0,
    window_type: str = "hann",
    top_k_peaks: int = 3,
) -> Any:
    """Estimates spectral power density periodogram and identifies peak frequencies."""
    return Record(SpectralDensityPeriodogram.analyze(
        series, sampling_rate=sampling_rate, window_type=window_type, top_k_peaks=top_k_peaks
    ))


# ==============================================================================
# MULTIVARIATE VECTOR AUTOREGRESSION (VAR(p)) & GRANGER CAUSALITY
# ==============================================================================

class MultivariateVectorAutoregressionVAR:
    """Vector Autoregressive VAR(p) model with multivariate OLS and Granger causality."""

    @staticmethod
    def _invert_matrix(A: List[List[float]]) -> List[List[float]]:
        """Inverts a square matrix using Gauss-Jordan elimination with partial pivoting."""
        n = len(A)
        # Augment with identity
        aug = [list(A[i]) + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

        for c in range(n):
            # Pivot
            pivot = max(range(c, n), key=lambda r: abs(aug[r][c]))
            if abs(aug[pivot][c]) < 1e-12:
                raise ValueError("Matrix is singular or near-singular")
            aug[c], aug[pivot] = aug[pivot], aug[c]

            pv = aug[c][c]
            for j in range(2 * n):
                aug[c][j] /= pv

            for r in range(n):
                if r != c:
                    factor = aug[r][c]
                    for j in range(2 * n):
                        aug[r][j] -= factor * aug[c][j]

        return [row[n:] for row in aug]

    @staticmethod
    def _mat_mul(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        n, m = len(A), len(B[0])
        p = len(B)
        res = [[0.0] * m for _ in range(n)]
        for i in range(n):
            for k in range(p):
                aik = A[i][k]
                for j in range(m):
                    res[i][j] += aik * B[k][j]
        return res

    @staticmethod
    def _mat_transpose(A: List[List[float]]) -> List[List[float]]:
        return [[A[r][c] for r in range(len(A))] for c in range(len(A[0]))]

    @classmethod
    def fit_and_forecast(
        cls,
        data: List[List[float]],
        lags: int = 1,
        forecast_steps: int = 3,
        variable_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Fits VAR(p) on multivariate time series (data is T x K) and computes h-step forecasts."""
        t_total = len(data)
        k_vars = len(data[0])
        p = max(1, int(lags))
        h = max(1, int(forecast_steps))

        if t_total <= p + k_vars * p + 1:
            raise ValueError(f"Insufficient observations T={t_total} for VAR({p}) with {k_vars} variables")

        vnames = variable_names or [f"var_{i}" for i in range(k_vars)]

        # Construct Design Matrix Z and Target Matrix Y
        # For t = p, ..., T-1:
        # y_t = [c, y_{t-1}, y_{t-2}, ..., y_{t-p}] * B + eps
        n_obs = t_total - p
        y_mat = []
        z_mat = []

        for t in range(p, t_total):
            y_mat.append(list(data[t]))
            row = [1.0]  # Intercept
            for lag in range(1, p + 1):
                row.extend(data[t - lag])
            z_mat.append(row)

        # OLS: B = (Z^T Z)^(-1) Z^T Y
        zt = cls._mat_transpose(z_mat)
        zt_z = cls._mat_mul(zt, z_mat)
        # Ridge regularization if needed for stability
        for i in range(len(zt_z)):
            zt_z[i][i] += 1e-9
        inv_zt_z = cls._invert_matrix(zt_z)
        zt_y = cls._mat_mul(zt, y_mat)
        b_coeff = cls._mat_mul(inv_zt_z, zt_y)  # (1 + K*p) x K

        # Residuals and Sigma
        y_pred = cls._mat_mul(z_mat, b_coeff)
        residuals = [[y_mat[r][c] - y_pred[r][c] for c in range(k_vars)] for r in range(n_obs)]

        dof = max(1, n_obs - (1 + k_vars * p))
        sigma = [[0.0] * k_vars for _ in range(k_vars)]
        for r in range(n_obs):
            for i in range(k_vars):
                for j in range(k_vars):
                    sigma[i][j] += residuals[r][i] * residuals[r][j] / dof

        # Granger causality F-tests (for each pair (cause, effect))
        granger_tests = []
        for cause_idx in range(k_vars):
            for effect_idx in range(k_vars):
                if cause_idx == effect_idx:
                    continue
                # Unrestricted RSS
                rss_u = sum(residuals[r][effect_idx] ** 2 for r in range(n_obs))

                # Restricted model without lags of cause_idx
                # Form restricted Z
                z_res = []
                for t in range(p, t_total):
                    row = [1.0]
                    for lag in range(1, p + 1):
                        for var_j in range(k_vars):
                            if var_j != cause_idx:
                                row.append(data[t - lag][var_j])
                    z_res.append(row)

                zt_r = cls._mat_transpose(z_res)
                ztr_zr = cls._mat_mul(zt_r, z_res)
                for ii in range(len(ztr_zr)):
                    ztr_zr[ii][ii] += 1e-9
                inv_zr = cls._invert_matrix(ztr_zr)
                y_eff = [[y_mat[r][effect_idx]] for r in range(n_obs)]
                zr_y = cls._mat_mul(zt_r, y_eff)
                b_res = cls._mat_mul(inv_zr, zr_y)
                y_pred_res = cls._mat_mul(z_res, b_res)
                rss_r = sum((y_eff[r][0] - y_pred_res[r][0]) ** 2 for r in range(n_obs))

                # F-statistic: ((RSS_R - RSS_U) / p) / (RSS_U / dof)
                num = max(0.0, (rss_r - rss_u) / p)
                den = max(1e-12, rss_u / dof)
                f_stat = num / den

                granger_tests.append({
                    "cause": vnames[cause_idx],
                    "effect": vnames[effect_idx],
                    "f_statistic": round(f_stat, 4),
                    "is_causal": f_stat > 3.0,
                })

        # Recursive h-step forecasting
        history = [list(row) for row in data]
        forecasts = []

        for _ in range(h):
            t_curr = len(history)
            row = [1.0]
            for lag in range(1, p + 1):
                row.extend(history[t_curr - lag])

            # Next state: row * B
            next_vals = [0.0] * k_vars
            for j in range(k_vars):
                next_vals[j] = sum(row[k] * b_coeff[k][j] for k in range(len(row)))

            forecasts.append({vnames[j]: round(next_vals[j], 4) for j in range(k_vars)})
            history.append(next_vals)

        return {
            "num_variables": k_vars,
            "variable_names": vnames,
            "lags": p,
            "forecast_steps": h,
            "residual_covariance": [[round(x, 6) for x in row] for row in sigma],
            "forecasts": [Record(fc) for fc in forecasts],
            "granger_causality": [Record(gt) for gt in granger_tests],
        }


# ==============================================================================
# STATE-SPACE KALMAN FILTER & RTS BACKWARD SMOOTHER
# ==============================================================================

class KalmanFilterStateSpace:
    """Linear Dynamic State-Space Model with forward Kalman filter and Rauch-Tung-Striebel smoother."""

    @staticmethod
    def _inv_2x2(M: List[List[float]]) -> List[List[float]]:
        det = M[0][0] * M[1][1] - M[0][1] * M[1][0]
        if abs(det) < 1e-12:
            return [[1.0, 0.0], [0.0, 1.0]]
        inv_det = 1.0 / det
        return [
            [M[1][1] * inv_det, -M[0][1] * inv_det],
            [-M[1][0] * inv_det, M[0][0] * inv_det],
        ]

    @classmethod
    def filter_and_smooth_1d(
        cls,
        measurements: List[float],
        process_variance_q: float = 1e-4,
        measurement_variance_r: float = 1e-2,
        initial_state: float = 0.0,
        initial_covariance: float = 1.0,
        drift_f: float = 1.0,
    ) -> Dict[str, Any]:
        """Runs 1D Kalman filter and RTS smoother on a series of observations."""
        q = float(process_variance_q)
        r = float(measurement_variance_r)
        f = float(drift_f)

        x_hat = float(initial_state)
        p = float(initial_covariance)

        filtered_x = []
        filtered_p = []
        predicted_x = []
        predicted_p = []
        innovations = []

        for z in measurements:
            # 1. Predict
            x_pred = f * x_hat
            p_pred = (f * p * f) + q
            predicted_x.append(x_pred)
            predicted_p.append(p_pred)

            # 2. Update
            y = z - x_pred  # Innovation
            s = p_pred + r  # Innovation variance
            k = p_pred / max(1e-12, s)  # Kalman gain

            x_hat = x_pred + k * y
            p = (1.0 - k) * p_pred

            filtered_x.append(x_hat)
            filtered_p.append(p)
            innovations.append(round(y, 4))

        # Rauch-Tung-Striebel backward smoother
        n = len(measurements)
        smoothed_x = list(filtered_x)
        smoothed_p = list(filtered_p)

        for t in range(n - 2, -1, -1):
            c_t = (filtered_p[t] * f) / max(1e-12, predicted_p[t + 1])
            smoothed_x[t] = filtered_x[t] + c_t * (smoothed_x[t + 1] - predicted_x[t + 1])
            smoothed_p[t] = filtered_p[t] + (c_t ** 2) * (smoothed_p[t + 1] - predicted_p[t + 1])

        return {
            "observations_count": n,
            "filtered_states": [round(v, 4) for v in filtered_x],
            "filtered_variances": [round(v, 6) for v in filtered_p],
            "smoothed_states": [round(v, 4) for v in smoothed_x],
            "smoothed_variances": [round(v, 6) for v in smoothed_p],
            "innovations": innovations,
            "final_gain": round(k, 4),
        }


def timeseries_fit_var_model(
    data: List[List[float]],
    lags: int = 1,
    forecast_steps: int = 3,
    variable_names: Optional[List[str]] = None,
) -> Record:
    """Fits multivariate Vector Autoregression VAR(p) with Granger causality and forecasts."""
    return Record(MultivariateVectorAutoregressionVAR.fit_and_forecast(
        data, lags=lags, forecast_steps=forecast_steps, variable_names=variable_names
    ))


def timeseries_kalman_filter_smooth(
    measurements: List[float],
    process_variance_q: float = 1e-4,
    measurement_variance_r: float = 1e-2,
    initial_state: float = 0.0,
    initial_covariance: float = 1.0,
) -> Record:
    """Applies 1D forward Kalman filter and RTS backward smoother to noisy measurements."""
    return Record(KalmanFilterStateSpace.filter_and_smooth_1d(
        measurements,
        process_variance_q=process_variance_q,
        measurement_variance_r=measurement_variance_r,
        initial_state=initial_state,
        initial_covariance=initial_covariance,
    ))


class NaturalCubicSpline:
    """Natural cubic spline interpolation for time-series envelope estimation."""

    def __init__(self, x: List[float], y: List[float]) -> None:
        n = len(x)
        self.x = list(x)
        self.y = list(y)
        if n < 2:
            return

        h = [x[i + 1] - x[i] for i in range(n - 1)]
        alpha = [0.0] * n
        for i in range(1, n - 1):
            alpha[i] = (3.0 / h[i]) * (y[i + 1] - y[i]) - (3.0 / h[i - 1]) * (y[i] - y[i - 1])

        l = [1.0] * n
        mu = [0.0] * n
        z = [0.0] * n
        for i in range(1, n - 1):
            l[i] = 2.0 * (x[i + 1] - x[i - 1]) - h[i - 1] * mu[i - 1]
            mu[i] = h[i] / l[i]
            z[i] = (alpha[i] - h[i - 1] * z[i - 1]) / l[i]

        self.c = [0.0] * n
        self.b = [0.0] * (n - 1)
        self.d = [0.0] * (n - 1)
        self.a = [y[i] for i in range(n - 1)]

        for j in range(n - 2, -1, -1):
            self.c[j] = z[j] - mu[j] * self.c[j + 1]
            self.b[j] = (y[j + 1] - y[j]) / h[j] - h[j] * (self.c[j + 1] + 2.0 * self.c[j]) / 3.0
            self.d[j] = (self.c[j + 1] - self.c[j]) / (3.0 * h[j])

    def eval(self, xi: float) -> float:
        n = len(self.x)
        if n == 0:
            return 0.0
        if n == 1:
            return self.y[0]
        if xi <= self.x[0]:
            return self.y[0]
        if xi >= self.x[-1]:
            return self.y[-1]

        low, high = 0, n - 2
        while low <= high:
            mid = (low + high) // 2
            if self.x[mid] <= xi <= self.x[mid + 1]:
                dx = xi - self.x[mid]
                return self.a[mid] + self.b[mid] * dx + self.c[mid] * (dx ** 2) + self.d[mid] * (dx ** 3)
            elif xi < self.x[mid]:
                high = mid - 1
            else:
                low = mid + 1
        return self.y[-1]


class SeasonalARIMASARIMA:
    """Seasonal AutoRegressive Integrated Moving Average SARIMA(p,d,q)x(P,D,Q)_s Engine."""

    @staticmethod
    def _difference(series: List[float], d: int, s: int, D: int) -> Tuple[List[float], List[List[float]], List[List[float]]]:
        curr = list(series)
        diff_d_history = []
        for _ in range(d):
            diff_d_history.append(list(curr))
            curr = [curr[i] - curr[i - 1] for i in range(1, len(curr))]

        diff_D_history = []
        for _ in range(D):
            diff_D_history.append(list(curr))
            curr = [curr[i] - curr[i - s] for i in range(s, len(curr))]
        return curr, diff_d_history, diff_D_history

    @staticmethod
    def _integrate(forecasts: List[float], orig_series: List[float], d: int, s: int, D: int) -> List[float]:
        res = list(forecasts)
        for _ in range(D):
            extended = list(orig_series)
            out = []
            for f in res:
                prev_s = extended[-s] if len(extended) >= s else 0.0
                val = f + prev_s
                extended.append(val)
                out.append(val)
            res = out

        for _ in range(d):
            last_val = orig_series[-1] if orig_series else 0.0
            out = []
            for f in res:
                last_val = last_val + f
                out.append(last_val)
            res = out
        return res

    @classmethod
    def fit_and_forecast(
        cls,
        series: List[float],
        p: int = 1,
        d: int = 1,
        q: int = 0,
        P: int = 0,
        D: int = 0,
        Q: int = 0,
        s: int = 4,
        forecast_steps: int = 4,
    ) -> Dict[str, Any]:
        """Fits SARIMA model and generates out-of-sample forecasts."""
        diff_series, _, _ = cls._difference(series, d, s, D)
        n = len(diff_series)
        if n < 4:
            last = series[-1] if series else 0.0
            return {
                "order": f"SARIMA({p},{d},{q})x({P},{D},{Q})_{s}",
                "coefficients": [0.0],
                "forecast": [round(last, 4)] * forecast_steps,
                "forecast_steps": forecast_steps,
            }

        X = []
        Y = []
        max_lag = max(p, 1)
        for t in range(max_lag, n):
            row = [diff_series[t - lag] for lag in range(1, p + 1)] if p > 0 else []
            X.append(row)
            Y.append(diff_series[t])

        if X and X[0]:
            k = len(X[0])
            XTX = [[sum(X[r][i] * X[r][j] for r in range(len(X))) for j in range(k)] for i in range(k)]
            for i in range(k):
                XTX[i][i] += 1e-4  # Ridge regularization
            XTY = [sum(X[r][i] * Y[r] for r in range(len(X))) for i in range(k)]

            if k == 1:
                beta = [XTY[0] / XTX[0][0]]
            else:
                det = XTX[0][0] * XTX[1][1] - XTX[0][1] * XTX[1][0]
                if abs(det) > 1e-12:
                    beta = [
                        (XTX[1][1] * XTY[0] - XTX[0][1] * XTY[1]) / det,
                        (-XTX[1][0] * XTY[0] + XTX[0][0] * XTY[1]) / det,
                    ]
                else:
                    beta = [0.0] * k
        else:
            beta = [0.0]

        diff_hist = list(diff_series)
        diff_preds = []
        for _ in range(forecast_steps):
            pred = 0.0
            for lag in range(1, p + 1):
                if lag <= len(diff_hist):
                    pred += beta[lag - 1] * diff_hist[-lag]
            diff_preds.append(pred)
            diff_hist.append(pred)

        integrated_preds = cls._integrate(diff_preds, series, d, s, D)

        return {
            "order": f"SARIMA({p},{d},{q})x({P},{D},{Q})_{s}",
            "coefficients": [round(b, 4) for b in beta],
            "forecast": [round(v, 4) for v in integrated_preds],
            "forecast_steps": forecast_steps,
        }


class IMF(list):
    """Intrinsic Mode Function list with energy property."""
    @property
    def energy(self) -> float:
        return round(sum(v * v for v in self), 4)

    @property
    def values(self) -> list:
        return list(self)


class EmpiricalModeDecompositionEMD:
    """Empirical Mode Decomposition (EMD) & Hilbert-Huang Transform."""

    @classmethod
    def decompose(cls, signal: List[float], max_imfs: int = 3, max_sifts: int = 5) -> Dict[str, Any]:
        """Decomposes nonlinear non-stationary signals into Intrinsic Mode Functions (IMFs)."""
        n = len(signal)
        t = [float(i) for i in range(n)]
        r = list(signal)
        imfs = []

        for _ in range(max_imfs):
            h = list(r)
            for _ in range(max_sifts):
                max_idx = [i for i in range(1, n - 1) if h[i] > h[i - 1] and h[i] >= h[i + 1]]
                min_idx = [i for i in range(1, n - 1) if h[i] < h[i - 1] and h[i] <= h[i + 1]]
                if len(max_idx) < 2 or len(min_idx) < 2:
                    break

                max_x = [0.0] + [t[i] for i in max_idx] + [float(n - 1)]
                max_y = [h[max_idx[0]]] + [h[i] for i in max_idx] + [h[max_idx[-1]]]
                min_x = [0.0] + [t[i] for i in min_idx] + [float(n - 1)]
                min_y = [h[min_idx[0]]] + [h[i] for i in min_idx] + [h[min_idx[-1]]]

                upper_sp = NaturalCubicSpline(max_x, max_y)
                lower_sp = NaturalCubicSpline(min_x, min_y)

                m = [(upper_sp.eval(ti) + lower_sp.eval(ti)) / 2.0 for ti in t]
                h = [h[i] - m[i] for i in range(n)]

            max_cnt = sum(1 for i in range(1, n - 1) if h[i] > h[i - 1] and h[i] >= h[i + 1])
            min_cnt = sum(1 for i in range(1, n - 1) if h[i] < h[i - 1] and h[i] <= h[i + 1])
            if max_cnt < 2 and min_cnt < 2:
                break

            imfs.append(IMF([round(v, 4) for v in h]))
            r = [r[i] - h[i] for i in range(n)]

        return {
            "imfs": imfs,
            "residual": [round(v, 4) for v in r],
            "total_imfs": len(imfs),
        }


def timeseries_sarima_forecast(
    series: List[float],
    p: int = 1,
    d: int = 1,
    q: int = 0,
    P: int = 0,
    D: int = 0,
    Q: int = 0,
    s: int = 4,
    forecast_steps: int = 4,
) -> Record:
    """Fits SARIMA model and computes multi-step out-of-sample forecasts."""
    return Record(SeasonalARIMASARIMA.fit_and_forecast(
        series, p=p, d=d, q=q, P=P, D=D, Q=Q, s=s, forecast_steps=forecast_steps
    ))


def timeseries_emd_decompose(
    signal: List[float],
    max_imfs: int = 3,
    max_sifts: int = 5,
) -> Record:
    """Decomposes signal into Intrinsic Mode Functions using Empirical Mode Decomposition."""
    return Record(EmpiricalModeDecompositionEMD.decompose(
        signal, max_imfs=max_imfs, max_sifts=max_sifts
    ))



