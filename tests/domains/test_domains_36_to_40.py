"""Comprehensive test suite for Phase 3 new domains:
- telecom (Domain 36)
- neuro (Domain 37)
- automata (Domain 38)
- metrics (Domain 39)
- spatial_audio (Domain 40)
"""

import pytest
import math
from doomscript.compiler.engine import execute


def test_telecom_domain():
    code = """
use telecom
# Hamming(7, 4) encoding & error correction
data_bits = [1, 0, 1, 1]
encoded = telecom_hamming74_encode(data_bits)

# Introduce single bit error at index 3
corrupted = list(encoded)
corrupted[3] = corrupted[3] ^ 1

decoded_res = telecom_hamming74_decode(corrupted)

# CRC checksums
c8 = telecom_crc8("Hello Telecom")
c16 = telecom_crc16("Hello Telecom")
c32 = telecom_crc32("Hello Telecom")

# Reed-Solomon over GF(256)
rs_msg = [ord(c) for c in "DOOM"]
rs_encoded = telecom_reed_solomon_encode(rs_msg, 4)
# Corrupt 1 symbol
rs_corrupted = list(rs_encoded)
rs_corrupted[1] = 0
rs_decoded, rs_ok = telecom_reed_solomon_decode(rs_corrupted, 4)
rs_text = "".join([chr(c) for c in rs_decoded])
"""
    env = execute(code)
    # Hamming single bit correction
    dec_bits, err_count = env["decoded_res"]
    assert dec_bits[:4] == [1, 0, 1, 1]
    assert err_count == 1
    # CRC checks
    assert env["c32"] != 0
    assert env["c16"] != 0
    assert env["c8"] != 0
    # Reed-Solomon correction
    assert env["rs_ok"] is True
    assert env["rs_text"] == "DOOM"


def test_neuro_domain():
    code = """
use neuro
lif = neuro_create_lif(v_rest=-70.0, v_thresh=-55.0, v_reset=-75.0, tau_m=20.0, resistance=10.0)

# Simulate LIF with steady 2.0 nA current (20 mV step exceeds threshold)
current_trace = [2.0] * 100
sim_res = neuro_simulate_lif(lif, current_trace, dt_ms=1.0)

# STDP: pre before post (dt = +10 ms -> LTP)
w_initial = 0.5
w_potentiated = neuro_stdp_update(w_initial, dt_ms=10.0)
w_depressed = neuro_stdp_update(w_initial, dt_ms=-10.0)

# Poisson spike generator
spikes = neuro_poisson_spikes(rate_hz=50.0, duration_ms=1000.0, dt_ms=1.0, seed=42)
num_spikes = sum(spikes)
"""
    env = execute(code)
    assert env["sim_res"]["total_spikes"] > 0
    assert env["w_potentiated"] > 0.5
    assert env["w_depressed"] < 0.5
    # 50 Hz for 1 sec should yield roughly 35-65 spikes
    assert 30 <= env["num_spikes"] <= 70


def test_automata_domain():
    code = """
use automata
# Compile simple regex (a|b)*c into DFA
dfa = automata_regex_to_dfa("(a|b)*c")
acc1 = automata_dfa_accepts(dfa, "c")
acc2 = automata_dfa_accepts(dfa, "ababc")
acc3 = automata_dfa_accepts(dfa, "abab")

# Turing machine: simple unary incrementer (111 -> 1111)
tm_transitions = {
    ("q0", "1"): ("q0", "1", "R"),
    ("q0", "_"): ("q_accept", "1", "N"),
}
tm_res = automata_run_turing_machine(tm_transitions, tape="111", start_state="q0", accept_states=["q_accept"])
"""
    env = execute(code)
    assert env["acc1"] is True
    assert env["acc2"] is True
    assert env["acc3"] is False
    assert env["tm_res"]["accepted"] is True
    assert env["tm_res"]["tape"] == "1111"


def test_metrics_domain():
    code = """
use metrics
metrics_clear()
c = metrics_counter("http_requests_total", "Total HTTP requests", {"method": "GET", "status": "200"})
c.inc(10)

g = metrics_gauge("memory_usage_bytes", "Memory consumption")
g.set(1048576)
g.inc(1024)

h = metrics_histogram("request_duration_seconds", "HTTP latency", buckets=[0.1, 0.5, 1.0])
h.observe(0.05)
h.observe(0.25)
h.observe(0.8)

p95 = metrics_calculate_percentile([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], 95.0)

prom_text = metrics_export_openmetrics()
"""
    env = execute(code)
    assert env["p95"] == 95.5 or abs(env["p95"] - 95.5) < 1.0
    assert "# HELP http_requests_total" in env["prom_text"]
    assert 'http_requests_total{method="GET",status="200"} 10.0' in env["prom_text"]
    assert "# TYPE memory_usage_bytes gauge" in env["prom_text"]
    assert "memory_usage_bytes 1049600.0" in env["prom_text"]
    assert "request_duration_seconds_count 3" in env["prom_text"]


def test_spatial_audio_domain():
    code = """
use spatial_audio
# Generate short test signal (sine wave)
sample_rate = 44100
signal = [math.sin(2.0 * math.pi * 440.0 * i / sample_rate) for i in range(200)]

# Binaural pan at 45 degrees azimuth (sound from right side)
l_ch, r_ch = spatial_audio_binaural(signal, azimuth_deg=45.0, sample_rate=sample_rate)

# Ambisonics B-format encode & decode to stereo
b_fmt = spatial_audio_ambisonics_encode(signal, azimuth_deg=90.0, elevation_deg=0.0)
st_l, st_r = spatial_audio_ambisonics_decode_stereo(b_fmt)

# Doppler shift (fast moving emitter toward listener)
doppler_sig = spatial_audio_doppler(signal, source_speed=100.0, listener_speed=0.0, sample_rate=sample_rate)

# Schroeder reverberation
reverb_sig = spatial_audio_schroeder_reverb(signal, rt60=1.0, sample_rate=sample_rate)
"""
    env = execute(code)
    assert len(env["l_ch"]) == 200
    assert len(env["r_ch"]) == 200
    # Right channel should have higher amplitude because azimuth is +45 deg (on the right)
    max_r = max(abs(x) for x in env["r_ch"])
    max_l = max(abs(x) for x in env["l_ch"])
    assert max_r > max_l
    assert len(env["b_fmt"]["W"]) == 200
    assert len(env["st_l"]) == 200
    # Doppler compressed signal length
    assert len(env["doppler_sig"]) < 200
    assert len(env["reverb_sig"]) == 200
