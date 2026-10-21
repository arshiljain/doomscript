"""Unit tests for Tranche 1 Domain Expansions (sec, graph, audio)."""

import math
import pytest
from doomscript.domains.sec.runtime import (
    ChaCha20Cipher,
    Poly1305Authenticator,
    sec_chacha20_encrypt,
    sec_chacha20_decrypt,
    sec_poly1305_mac,
    sec_poly1305_verify,
)
from doomscript.domains.graph.runtime import (
    EdmondsKarpMaxFlow,
    DinicMaxFlow,
    graph_edmonds_karp,
    graph_dinic_max_flow,
)
from doomscript.domains.audio.runtime import (
    CooleyTukeyFFT,
    STFTProcessor,
    audio_fft,
    audio_ifft,
    audio_stft,
)


def test_chacha20_encryption_decryption_roundtrip():
    """Verify ChaCha20 encrypt and decrypt restores original plaintext."""
    key = b"0123456789abcdef0123456789abcdef"  # 32 bytes
    nonce = b"0123456789ab"                    # 12 bytes
    message = b"DoomScript high-performance cryptography standard library 2026."

    ciphertext = sec_chacha20_encrypt(key, nonce, message, counter=1)
    assert ciphertext != message
    assert len(ciphertext) == len(message)

    decrypted = sec_chacha20_decrypt(key, nonce, ciphertext, counter=1)
    assert decrypted == message


def test_poly1305_authenticator():
    """Verify Poly1305 MAC tag generation and constant-time verification."""
    key = b"0123456789abcdef0123456789abcdef"  # 32 bytes
    msg = b"Secure authenticated message payload."

    tag = sec_poly1305_mac(key, msg)
    assert len(tag) == 16
    assert sec_poly1305_verify(key, msg, tag) is True

    # Tampered message must fail
    assert sec_poly1305_verify(key, b"Tampered payload.", tag) is False


def test_edmonds_karp_and_dinic_max_flow():
    """Verify network flow calculation parity between Edmonds-Karp and Dinic."""
    nodes = ["s", "a", "b", "c", "d", "t"]
    edges = [
        {"source": "s", "target": "a", "capacity": 10.0},
        {"source": "s", "target": "c", "capacity": 10.0},
        {"source": "a", "target": "b", "capacity": 4.0},
        {"source": "a", "target": "c", "capacity": 2.0},
        {"source": "a", "target": "d", "capacity": 8.0},
        {"source": "c", "target": "d", "capacity": 9.0},
        {"source": "b", "target": "t", "capacity": 10.0},
        {"source": "d", "target": "t", "capacity": 10.0},
    ]

    ek_res = graph_edmonds_karp(nodes, edges, "s", "t")
    dinic_res = graph_dinic_max_flow(nodes, edges, "s", "t")

    assert ek_res.max_flow == pytest.approx(14.0)
    assert dinic_res.max_flow == pytest.approx(14.0)


def test_cooley_tukey_fft_and_ifft():
    """Verify FFT and Inverse FFT round-trip on pure sine wave."""
    n = 64
    freq = 4.0
    # Generate pure sinusoidal signal
    signal = [math.sin(2.0 * math.pi * freq * i / n) for i in range(n)]

    spectrum = audio_fft(signal)
    assert len(spectrum) == 64

    # Peak must be at frequency index 4 and 60 (symmetric)
    mags = [abs(x) for x in spectrum]
    assert mags[4] == max(mags[:32])

    reconstructed = audio_ifft(spectrum)
    assert len(reconstructed) == 64
    for orig, rec in zip(signal, reconstructed):
        assert rec == pytest.approx(orig, abs=1e-7)


def test_audio_stft_processing():
    """Verify Short-Time Fourier Transform frame decomposition."""
    samples = [math.sin(0.1 * i) for i in range(1024)]
    stft_res = audio_stft(samples, frame_size=256, hop_size=128)

    assert stft_res.num_frames > 0
    assert len(stft_res.magnitudes) == stft_res.num_frames
    assert len(stft_res.magnitudes[0]) == 256 // 2 + 1
