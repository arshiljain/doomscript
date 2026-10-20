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
from doomscript.runtime import Record


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


# --- Deepened Computational Neuroscience: Tsodyks-Markram Synapse, FitzHugh-Nagumo & WTA Network ---

class TsodyksMarkramSynapse:
    """Dynamic short-term synaptic plasticity model exhibiting depression (STD) and facilitation (STF)."""

    def __init__(
        self,
        U: float = 0.2,
        tau_rec: float = 800.0,
        tau_fac: float = 50.0,
        A: float = 1.0,
    ):
        self.U = float(U)              # baseline release probability
        self.tau_rec = float(tau_rec)  # recovery from depression (ms)
        self.tau_fac = float(tau_fac)  # decay of facilitation (ms)
        self.A = float(A)              # absolute synaptic weight

        # Initial resting state
        self.R = 1.0                   # fraction of available neurotransmitter resources
        self.u = self.U                # initial utilization

    def reset(self) -> None:
        self.R = 1.0
        self.u = self.U

    def step(self, is_spike: bool, dt_ms: float = 1.0) -> float:
        """Advances synapse by dt_ms and returns postsynaptic current (PSC)."""
        # Continuous relaxation between spikes
        if self.tau_fac > 0:
            self.u += - (self.u - self.U) * (dt_ms / self.tau_fac)
        if self.tau_rec > 0:
            self.R += (1.0 - self.R) * (dt_ms / self.tau_rec)

        psc = 0.0
        if is_spike:
            # Facilitation update: u increases toward 1.0
            u_plus = self.u + self.U * (1.0 - self.u)
            # Postsynaptic response
            psc = self.A * u_plus * self.R
            # Depression update: resources depleted by release
            self.R = max(0.0, self.R - u_plus * self.R)
            self.u = min(1.0, u_plus)

        return psc

    def simulate_train(self, spike_train: List[int], dt_ms: float = 1.0) -> Dict[str, Any]:
        """Simulates response across binary spike train."""
        self.reset()
        psc_trace: List[float] = []
        r_trace: List[float] = []
        u_trace: List[float] = []

        for spike in spike_train:
            psc = self.step(bool(spike), dt_ms=dt_ms)
            psc_trace.append(round(psc, 4))
            r_trace.append(round(self.R, 4))
            u_trace.append(round(self.u, 4))

        return {
            "psc_trace": psc_trace,
            "resource_r": r_trace,
            "utilization_u": u_trace,
            "total_charge": round(sum(psc_trace) * dt_ms, 4),
            "peak_psc": round(max(psc_trace) if psc_trace else 0.0, 4),
        }


class FitzHughNagumoNeuron:
    """Two-variable phase-plane biological excitable membrane model (v: membrane potential, w: recovery variable)."""

    def __init__(self, a: float = 0.7, b: float = 0.8, tau: float = 12.5):
        self.a = float(a)
        self.b = float(b)
        self.tau = float(tau)

        self.v = -1.2  # resting voltage
        self.w = -0.6  # resting recovery
        self._prev_v = self.v

    def reset(self) -> None:
        self.v = -1.2
        self.w = -0.6
        self._prev_v = self.v

    def step(self, I: float, dt: float = 0.1) -> Tuple[float, float, bool]:
        """Advances ODE using Runge-Kutta 2nd order (Midpoint method)."""
        def dv(v_val: float, w_val: float, current: float) -> float:
            return v_val - (v_val ** 3) / 3.0 - w_val + current

        def dw(v_val: float, w_val: float) -> float:
            return (v_val + self.a - self.b * w_val) / self.tau

        # Midpoint step
        k1_v = dv(self.v, self.w, I)
        k1_w = dw(self.v, self.w)

        mid_v = self.v + 0.5 * dt * k1_v
        mid_w = self.w + 0.5 * dt * k1_w

        k2_v = dv(mid_v, mid_w, I)
        k2_w = dw(mid_v, mid_w)

        old_v = self.v
        self.v += dt * k2_v
        self.w += dt * k2_w

        # Spike detection: upward zero crossing with high voltage
        spike = (old_v < 1.0 <= self.v)
        self._prev_v = self.v
        return self.v, self.w, spike

    def simulate(self, current_trace: List[float], dt: float = 0.1) -> Dict[str, Any]:
        self.reset()
        voltages: List[float] = []
        recoveries: List[float] = []
        spikes: List[int] = []

        for I in current_trace:
            v, w, is_spike = self.step(I, dt=dt)
            voltages.append(round(v, 4))
            recoveries.append(round(w, 4))
            spikes.append(1 if is_spike else 0)

        return {
            "voltages": voltages,
            "recoveries": recoveries,
            "spikes": spikes,
            "total_spikes": sum(spikes),
        }


class WinnerTakeAllNetwork:
    """Competitive lateral inhibitory neuronal population model."""

    def __init__(self, num_neurons: int, beta: float = 0.5, tau: float = 10.0, threshold: float = 0.0):
        self.N = max(2, int(num_neurons))
        self.beta = float(beta)        # lateral inhibition coefficient
        self.tau = float(tau)          # membrane integration time constant
        self.threshold = float(threshold)
        self.activities: List[float] = [0.0] * self.N

    def reset(self) -> None:
        self.activities = [0.0] * self.N

    def step(self, inputs: List[float], dt: float = 0.5) -> List[float]:
        """Performs one integration step under mutual recurrent inhibition."""
        if len(inputs) != self.N:
            raise ValueError(f"Expected {self.N} inputs, got {len(inputs)}")

        total_activity = sum(self.activities)
        new_acts = [0.0] * self.N

        for i in range(self.N):
            # Mutual inhibition is sum of other units: (total - self)
            inhibition = self.beta * (total_activity - self.activities[i])
            net_drive = max(0.0, inputs[i] - inhibition - self.threshold)
            # Leaky integration: dy/dt = (-y + net_drive) / tau
            dy = (-self.activities[i] + net_drive) / self.tau
            new_acts[i] = max(0.0, self.activities[i] + dt * dy)

        self.activities = new_acts
        return [round(x, 4) for x in self.activities]

    def run_until_convergence(
        self, inputs: List[float], max_steps: int = 100, tol: float = 1e-4, dt: float = 0.5
    ) -> Dict[str, Any]:
        """Runs dynamics until steady state is reached."""
        self.reset()
        for step_idx in range(max_steps):
            prev = list(self.activities)
            curr = self.step(inputs, dt=dt)
            diff = max(abs(c - p) for c, p in zip(curr, prev))
            if diff < tol:
                break

        winner_idx = max(range(self.N), key=lambda i: self.activities[i])
        return {
            "winner_index": winner_idx,
            "winner_activity": round(self.activities[winner_idx], 4),
            "final_activities": [round(x, 4) for x in self.activities],
            "converged": True,
            "steps_taken": step_idx + 1,
        }


# ==============================================================================
# HODGKIN-HUXLEY 4-VARIABLE CONDUCTANCE BIOPHYSICAL NEURON MODEL
# ==============================================================================

class HodgkinHuxleyNeuron:
    """Biophysical Hodgkin-Huxley model of squid giant axon action potentials.

    Variables:
    - V: Membrane potential (mV)
    - m: Sodium channel activation gate [0, 1]
    - h: Sodium channel inactivation gate [0, 1]
    - n: Potassium channel activation gate [0, 1]
    """

    def __init__(
        self,
        c_m: float = 1.0,         # Membrane capacitance (uF/cm^2)
        g_na: float = 120.0,      # Max Sodium conductance (mS/cm^2)
        g_k: float = 36.0,        # Max Potassium conductance (mS/cm^2)
        g_l: float = 0.3,         # Leak conductance (mS/cm^2)
        e_na: float = 50.0,       # Sodium reversal potential (mV)
        e_k: float = -77.0,       # Potassium reversal potential (mV)
        e_l: float = -54.387,     # Leak reversal potential (mV)
        v_init: float = -65.0,    # Initial membrane potential (mV)
    ):
        self.C_m = float(c_m)
        self.g_Na = float(g_na)
        self.g_K = float(g_k)
        self.g_L = float(g_l)
        self.E_Na = float(e_na)
        self.E_K = float(e_k)
        self.E_L = float(e_l)

        self.V = float(v_init)
        self.m = self._alpha_m(self.V) / (self._alpha_m(self.V) + self._beta_m(self.V))
        self.h = self._alpha_h(self.V) / (self._alpha_h(self.V) + self._beta_h(self.V))
        self.n = self._alpha_n(self.V) / (self._alpha_n(self.V) + self._beta_n(self.V))

    @staticmethod
    def _alpha_m(V: float) -> float:
        v = V + 40.0
        return 0.1 * v / (1.0 - math.exp(-v / 10.0)) if abs(v) > 1e-6 else 1.0

    @staticmethod
    def _beta_m(V: float) -> float:
        return 4.0 * math.exp(-(V + 65.0) / 18.0)

    @staticmethod
    def _alpha_h(V: float) -> float:
        return 0.07 * math.exp(-(V + 65.0) / 20.0)

    @staticmethod
    def _beta_h(V: float) -> float:
        return 1.0 / (1.0 + math.exp(-(V + 35.0) / 10.0))

    @staticmethod
    def _alpha_n(V: float) -> float:
        v = V + 55.0
        return 0.01 * v / (1.0 - math.exp(-v / 10.0)) if abs(v) > 1e-6 else 0.1

    @staticmethod
    def _beta_n(V: float) -> float:
        return 0.125 * math.exp(-(V + 65.0) / 80.0)

    def step(self, i_inj: float, dt_ms: float = 0.02) -> Dict[str, float]:
        """Integrates one time step dt using 4th-order Runge-Kutta / Euler."""
        # Ionic currents
        i_na = self.g_Na * (self.m ** 3) * self.h * (self.V - self.E_Na)
        i_k = self.g_K * (self.n ** 4) * (self.V - self.E_K)
        i_l = self.g_L * (self.V - self.E_L)

        dv = (i_inj - i_na - i_k - i_l) / self.C_m
        dm = self._alpha_m(self.V) * (1.0 - self.m) - self._beta_m(self.V) * self.m
        dh = self._alpha_h(self.V) * (1.0 - self.h) - self._beta_h(self.V) * self.h
        dn = self._alpha_n(self.V) * (1.0 - self.n) - self._beta_n(self.V) * self.n

        self.V += dt_ms * dv
        self.m += dt_ms * dm
        self.h += dt_ms * dh
        self.n += dt_ms * dn

        return {
            "v": round(self.V, 3),
            "m": round(self.m, 4),
            "h": round(self.h, 4),
            "n": round(self.n, 4),
            "i_na": round(i_na, 3),
            "i_k": round(i_k, 3),
        }

    def simulate(self, current_pulse_uA: float, duration_ms: float = 50.0, dt_ms: float = 0.02) -> Dict[str, Any]:
        """Runs continuous simulation under constant injected current."""
        steps = int(duration_ms / dt_ms)
        voltages = []
        spike_count = 0
        in_spike = False

        for _ in range(steps):
            res = self.step(current_pulse_uA, dt_ms=dt_ms)
            v = res["v"]
            voltages.append(v)
            if v >= 0.0 and not in_spike:
                spike_count += 1
                in_spike = True
            elif v < -20.0 and in_spike:
                in_spike = False

        return {
            "duration_ms": duration_ms,
            "voltages": voltages,
            "spike_count": spike_count,
            "firing_rate_hz": round((spike_count / (duration_ms / 1000.0)), 2),
            "v_max": round(max(voltages), 2) if voltages else round(self.V, 2),
            "v_min": round(min(voltages), 2) if voltages else round(self.V, 2),
            "final_v": round(self.V, 3),
        }


# ==============================================================================
# WILSON-COWAN EXCITATORY-INHIBITORY NEURAL POPULATION MODEL
# ==============================================================================

class WilsonCowanNetwork:
    """Nonlinear coupled excitatory (E) and inhibitory (I) neural population dynamics."""

    def __init__(
        self,
        c_ee: float = 16.0,
        c_ie: float = 12.0,
        c_ei: float = 15.0,
        c_ii: float = 3.0,
        tau_e: float = 8.0,
        tau_i: float = 8.0,
        theta_e: float = 4.0,
        theta_i: float = 3.7,
        a_e: float = 1.3,
        a_i: float = 2.0,
    ):
        self.c_ee = float(c_ee)
        self.c_ie = float(c_ie)
        self.c_ei = float(c_ei)
        self.c_ii = float(c_ii)
        self.tau_e = float(tau_e)
        self.tau_i = float(tau_i)
        self.theta_e = float(theta_e)
        self.theta_i = float(theta_i)
        self.a_e = float(a_e)
        self.a_i = float(a_i)

        self.E = 0.1
        self.I = 0.1

    def _sigmoid(self, x: float, a: float, theta: float) -> float:
        arg = -a * (x - theta)
        arg = max(-50.0, min(50.0, arg))
        return 1.0 / (1.0 + math.exp(arg))

    def step(self, p_ext: float = 1.0, q_ext: float = 0.0, dt: float = 0.1) -> Tuple[float, float]:
        s_e = self._sigmoid(self.c_ee * self.E - self.c_ie * self.I + p_ext, self.a_e, self.theta_e)
        s_i = self._sigmoid(self.c_ei * self.E - self.c_ii * self.I + q_ext, self.a_i, self.theta_i)

        de = (-self.E + s_e) / self.tau_e
        di = (-self.I + s_i) / self.tau_i

        self.E = max(0.0, min(1.0, self.E + dt * de))
        self.I = max(0.0, min(1.0, self.I + dt * di))

        return round(self.E, 4), round(self.I, 4)

    def simulate(self, p_ext: float = 1.25, q_ext: float = 0.0, duration: float = 100.0, dt: float = 0.1) -> Dict[str, Any]:
        steps = int(duration / dt)
        e_history = []
        i_history = []
        for _ in range(steps):
            e_val, i_val = self.step(p_ext, q_ext, dt=dt)
            e_history.append(e_val)
            i_history.append(i_val)

        return {
            "steps": steps,
            "duration": duration,
            "e_history": e_history,
            "i_history": i_history,
            "final_e": e_history[-1] if e_history else 0.0,
            "final_i": i_history[-1] if i_history else 0.0,
            "amplitude_e": round(max(e_history) - min(e_history), 4) if e_history else 0.0,
        }


# ==============================================================================
# EEG SPECTRAL BANDPOWER ANALYSIS
# ==============================================================================

class EEGBandpowerAnalyzer:
    """Clinical EEG frequency band decomposition and cognitive workload indices."""

    BANDS = {
        "delta": (0.5, 4.0),
        "theta": (4.0, 8.0),
        "alpha": (8.0, 13.0),
        "beta": (13.0, 30.0),
        "gamma": (30.0, 80.0),
    }

    @classmethod
    def analyze(cls, eeg_signal: List[float], sample_rate: int = 250) -> Dict[str, float]:
        """Calculates absolute bandpower, relative power, and alpha/theta workload ratio."""
        n = len(eeg_signal)
        if n < 4:
            return {b: 0.0 for b in cls.BANDS}

        # Demean
        mean_v = sum(eeg_signal) / n
        s_norm = [v - mean_v for v in eeg_signal]

        # Power spectrum via DFT
        freq_res = sample_rate / n
        powers = {}
        total_power = 0.0

        for band_name, (f_low, f_high) in cls.BANDS.items():
            k_low = int(math.floor(f_low / freq_res))
            k_high = min(int(math.ceil(f_high / freq_res)), n // 2)
            band_sum = 0.0

            for k in range(k_low, k_high + 1):
                # Calculate DFT coefficient for bin k
                re_sum = 0.0
                im_sum = 0.0
                for t, x in enumerate(s_norm):
                    ang = -2.0 * math.pi * k * t / n
                    re_sum += x * math.cos(ang)
                    im_sum += x * math.sin(ang)
                p = (re_sum * re_sum + im_sum * im_sum) / (n * n)
                band_sum += p

            powers[band_name] = round(band_sum, 6)
            total_power += band_sum

        results = {}
        for b, p in powers.items():
            results[f"{b}_power"] = p
            results[f"{b}_relative"] = round(p / total_power, 4) if total_power > 1e-12 else 0.0

        # Cognitive index: Alpha / Theta ratio
        theta_p = powers.get("theta", 1e-6)
        alpha_p = powers.get("alpha", 0.0)
        results["alpha_theta_ratio"] = round(alpha_p / theta_p, 4) if theta_p > 1e-12 else 0.0
        results["total_power"] = round(total_power, 6)

        return results


# ==============================================================================
# PERISTIMULUS TIME HISTOGRAM (PSTH) & SPIKE RASTER ANALYTICS
# ==============================================================================

class PSTHAnalyzer:
    """Computes trial-averaged Peristimulus Time Histogram and time-varying firing rate."""

    @staticmethod
    def compute(
        trials_spike_times_ms: List[List[float]],
        duration_ms: float,
        bin_width_ms: float = 10.0,
    ) -> Dict[str, Any]:
        num_trials = len(trials_spike_times_ms)
        if num_trials == 0 or duration_ms <= 0:
            return {"bins": [], "counts": [], "firing_rates_hz": [], "mean_rate_hz": 0.0}

        num_bins = max(1, int(math.ceil(duration_ms / bin_width_ms)))
        counts = [0] * num_bins
        bin_edges = [round(i * bin_width_ms, 2) for i in range(num_bins)]

        total_spikes = 0
        for trial in trials_spike_times_ms:
            for t in trial:
                if 0.0 <= t < duration_ms:
                    b = int(t // bin_width_ms)
                    if b < num_bins:
                        counts[b] += 1
                        total_spikes += 1

        # Rate in Hz = (count / num_trials) / (bin_width_sec)
        bin_sec = bin_width_ms / 1000.0
        rates_hz = [round((c / num_trials) / bin_sec, 2) for c in counts]
        mean_rate = round(total_spikes / (num_trials * (duration_ms / 1000.0)), 2)

        return {
            "bin_edges_ms": bin_edges,
            "counts": counts,
            "firing_rates_hz": rates_hz,
            "mean_rate_hz": mean_rate,
            "total_spikes": total_spikes,
        }


# High-level domain entrypoints
def neuro_simulate_hodgkin_huxley(current_uA: float, duration_ms: float = 50.0) -> Any:
    hh = HodgkinHuxleyNeuron()
    return Record(hh.simulate(current_uA, duration_ms=duration_ms))


def neuro_simulate_wilson_cowan(p_ext: float = 1.25, duration: float = 50.0) -> Any:
    wc = WilsonCowanNetwork()
    return Record(wc.simulate(p_ext=p_ext, duration=duration))


def neuro_analyze_eeg_bands(signal: List[float], sample_rate: int = 250) -> Any:
    return Record(EEGBandpowerAnalyzer.analyze(signal, sample_rate=sample_rate))


def neuro_compute_psth(trials: List[List[float]], duration_ms: float, bin_width_ms: float = 10.0) -> Any:
    return Record(PSTHAnalyzer.compute(trials, duration_ms, bin_width_ms))

