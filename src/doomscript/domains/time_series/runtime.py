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
from doomscript.runtime import Record


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

