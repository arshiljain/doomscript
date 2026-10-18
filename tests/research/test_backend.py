# tests/research/test_backend.py
import pytest
from doomscript.research.backend import (
    ResearchRNG,
    ResearchSession,
    get_active_session,
    set_active_session,
    UnsupportedBackendOperationError,
)

def test_prng_reproducibility():
    rng1 = ResearchRNG(seed=12345)
    rng2 = ResearchRNG(seed=12345)
    seq1 = [rng1.random() for _ in range(100)]
    seq2 = [rng2.random() for _ in range(100)]
    assert seq1 == seq2
    assert 0.0 <= seq1[0] <= 1.0

def test_prng_distributions():
    rng = ResearchRNG(seed=42)
    uniforms = [rng.uniform(-5.0, 5.0) for _ in range(100)]
    assert all(-5.0 <= u <= 5.0 for u in uniforms)
    
    normals = [rng.normal(0.0, 1.0) for _ in range(100)]
    mean_val = sum(normals) / len(normals)
    assert abs(mean_val) < 0.5  # Rough sample mean check

    sample = rng.sample([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], k=4)
    assert len(sample) == 4
    assert len(set(sample)) == 4

def test_provenance_log_separation():
    session = ResearchSession(backend="pure", seed=42)
    log = session.get_provenance()
    assert "deterministic" in log
    assert "volatile" in log
    assert log["deterministic"]["backend"] == "pure"
    assert log["deterministic"]["seed"] == 42
    assert "timestamp_utc" in log["volatile"]
    assert "execution_seconds" in log["volatile"]

def test_unsupported_backend_operation():
    session = ResearchSession(backend="pure", seed=42)
    with pytest.raises(UnsupportedBackendOperationError, match="not supported"):
        session.assert_supported("nonexistent_cuda_op")
