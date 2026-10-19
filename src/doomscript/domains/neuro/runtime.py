"""Computational Neuroscience & Neuromorphic Spiking Neural Networks Domain for DoomScript.

Provides 100% pure Python implementations of:
- Leaky Integrate-and-Fire (LIF) neuron dynamics with refractory periods
- Izhikevich 2-variable dynamical neuron model (Regular Spiking, Fast Spiking, Bursting)
- Spike-Timing-Dependent Plasticity (STDP) Hebbian synaptic learning rule
- Homogeneous Poisson point-process spike train generation
- Inter-Spike Interval (ISI) analytics and coefficient of variation
Zero external dependencies.
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Optional, Tuple, Union


class LIFNeuron:
    """Leaky Integrate-and-Fire (LIF) biological neuron model."""

    def __init__(
        self,
        v_rest: float = -70.0,
        v_thresh: float = -55.0,
        v_reset: float = -75.0,
        tau_m: float = 20.0,
        resistance: float = 10.0,
        refractory_period: float = 2.0,
    ):
        self.v_rest = float(v_rest)
        self.v_thresh = float(v_thresh)
        self.v_reset = float(v_reset)
        self.tau_m = float(tau_m)
        self.resistance = float(resistance)
        self.refractory_period = float(refractory_period)

        self.v = self.v_rest
        self.refractory_time_left = 0.0

    def reset(self) -> None:
        self.v = self.v_rest
        self.refractory_time_left = 0.0

    def step(self, current_nA: float, dt_ms: float = 1.0) -> bool:
        """Advances neuron by dt_ms with injected input current. Returns True if spike occurred."""
        if self.refractory_time_left > 0.0:
            self.refractory_time_left -= dt_ms
            self.v = self.v_reset
            return False

        # Euler step: dv/dt = (-(v - v_rest) + R * I) / tau_m
        dv = (-(self.v - self.v_rest) + self.resistance * current_nA) * (dt_ms / self.tau_m)
        self.v += dv

        if self.v >= self.v_thresh:
            self.v = self.v_reset
            self.refractory_time_left = self.refractory_period
            return True

        return False


class IzhikevichNeuron:
    """Izhikevich 2-variable dynamical biological neuron model.
    dv/dt = 0.04*v^2 + 5*v + 140 - u + I
    du/dt = a*(b*v - u)
    if v >= 30 mV: v -> c, u -> u + d
    """

    PRESETS = {
        "RS": {"a": 0.02, "b": 0.2, "c": -65.0, "d": 8.0},    # Regular Spiking
        "IB": {"a": 0.02, "b": 0.2, "c": -55.0, "d": 4.0},    # Intrinsically Bursting
        "CH": {"a": 0.02, "b": 0.2, "c": -50.0, "d": 2.0},    # Chattering
        "FS": {"a": 0.1,  "b": 0.2, "c": -65.0, "d": 2.0},    # Fast Spiking
        "TC": {"a": 0.02, "b": 0.25, "c": -65.0, "d": 0.05},  # Thalamo-Cortical
    }

    def __init__(self, preset: str = "RS", a: float = 0.02, b: float = 0.2, c: float = -65.0, d: float = 8.0):
        if preset in self.PRESETS:
            p = self.PRESETS[preset]
            self.a, self.b, self.c, self.d = p["a"], p["b"], p["c"], p["d"]
        else:
            self.a, self.b, self.c, self.d = a, b, c, d

        self.v = self.c
        self.u = self.b * self.v

    def step(self, current: float, dt: float = 0.5) -> bool:
        """Performs two 0.5-step Euler integrations for numerical stability."""
        # Half step 1
        self.v += 0.5 * (0.04 * self.v * self.v + 5.0 * self.v + 140.0 - self.u + current) * dt
        self.v += 0.5 * (0.04 * self.v * self.v + 5.0 * self.v + 140.0 - self.u + current) * dt
        self.u += self.a * (self.b * self.v - self.u) * dt

        if self.v >= 30.0:
            self.v = self.c
            self.u += self.d
            return True
        return False


class STDP:
    """Spike-Timing-Dependent Plasticity learning rule."""

    @staticmethod
    def update_weight(
        w: float,
        dt_ms: float,
        a_pos: float = 0.01,
        a_neg: float = 0.012,
        tau_pos: float = 20.0,
        tau_neg: float = 20.0,
        w_min: float = 0.0,
        w_max: float = 1.0,
    ) -> float:
        """Updates synaptic weight w given dt = t_post - t_pre in milliseconds.
        dt > 0: Long-Term Potentiation (LTP)
        dt < 0: Long-Term Depression (LTD)
        """
        if dt_ms > 0:
            dw = a_pos * math.exp(-dt_ms / tau_pos)
        elif dt_ms < 0:
            dw = -a_neg * math.exp(dt_ms / tau_neg)
        else:
            dw = 0.0

        new_w = min(w_max, max(w_min, w + dw))
        return round(new_w, 6)


class PoissonSpikeGenerator:
    """Generates stochastic Poisson point-process spike trains."""

    @staticmethod
    def generate(rate_hz: float, duration_ms: float, dt_ms: float = 1.0, seed: Optional[int] = None) -> List[int]:
        if seed is not None:
            random.seed(seed)
        num_steps = int(duration_ms / dt_ms)
        p_spike = (rate_hz * dt_ms) / 1000.0
        spikes = [1 if random.random() < p_spike else 0 for _ in range(num_steps)]
        return spikes


class SpikeAnalytics:
    """Analyzes inter-spike intervals, firing rate, and regularity."""

    @staticmethod
    def inter_spike_intervals(spike_train: List[int], dt_ms: float = 1.0) -> List[float]:
        spike_times = [i * dt_ms for i, s in enumerate(spike_train) if s == 1]
        if len(spike_times) < 2:
            return []
        return [round(spike_times[i] - spike_times[i - 1], 4) for i in range(1, len(spike_times))]

    @staticmethod
    def coefficient_of_variation(spike_train: List[int], dt_ms: float = 1.0) -> float:
        """CV = std(ISI) / mean(ISI). CV=1 indicates Poisson process, CV=0 is periodic clock."""
        isis = SpikeAnalytics.inter_spike_intervals(spike_train, dt_ms)
        if len(isis) < 2:
            return 0.0
        mean_isi = sum(isis) / len(isis)
        var_isi = sum((x - mean_isi) ** 2 for x in isis) / len(isis)
        std_isi = math.sqrt(var_isi)
        return round(std_isi / mean_isi, 4) if mean_isi > 0 else 0.0


# --- High-Level Public Functions ---

def neuro_create_lif(
    v_rest: float = -70.0,
    v_thresh: float = -55.0,
    v_reset: float = -75.0,
    tau_m: float = 20.0,
    resistance: float = 10.0,
    refractory_period: float = 2.0,
) -> LIFNeuron:
    """Creates a Leaky Integrate-and-Fire biological neuron."""
    return LIFNeuron(v_rest, v_thresh, v_reset, tau_m, resistance, refractory_period)


def neuro_create_izhikevich(preset: str = "RS") -> IzhikevichNeuron:
    """Creates an Izhikevich dynamical neuron model."""
    return IzhikevichNeuron(preset=preset)


def neuro_stdp_update(
    w: float,
    dt_ms: float,
    a_pos: float = 0.01,
    a_neg: float = 0.012,
    tau_pos: float = 20.0,
    tau_neg: float = 20.0,
) -> float:
    """Applies Spike-Timing-Dependent Plasticity rule."""
    return STDP.update_weight(w, dt_ms, a_pos, a_neg, tau_pos, tau_neg)


def neuro_poisson_spikes(
    rate_hz: float, duration_ms: float, dt_ms: float = 1.0, seed: Optional[int] = None
) -> List[int]:
    """Generates stochastic Poisson spike train."""
    return PoissonSpikeGenerator.generate(rate_hz, duration_ms, dt_ms, seed)


def neuro_simulate_lif(neuron: LIFNeuron, current_trace: List[float], dt_ms: float = 1.0) -> Dict[str, Any]:
    """Simulates LIF neuron across input current time series."""
    neuron.reset()
    voltages: List[float] = []
    spikes: List[int] = []

    for I in current_trace:
        is_spike = neuron.step(I, dt_ms)
        voltages.append(round(neuron.v, 3))
        spikes.append(1 if is_spike else 0)

    total_spikes = sum(spikes)
    duration_sec = (len(current_trace) * dt_ms) / 1000.0
    mean_rate = total_spikes / duration_sec if duration_sec > 0 else 0.0

    return {
        "voltages": voltages,
        "spikes": spikes,
        "total_spikes": total_spikes,
        "firing_rate_hz": round(mean_rate, 2),
        "isi": SpikeAnalytics.inter_spike_intervals(spikes, dt_ms),
        "cv": SpikeAnalytics.coefficient_of_variation(spikes, dt_ms),
    }
