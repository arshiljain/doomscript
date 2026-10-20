"""Unit and integration tests for Deepened Cluster F (Data, Storage & Telecommunications).

Tests the enhanced capabilities of:
- data: RollingAggregator, RelationalJoinEngine, PivotTableEngine
- office: SpreadsheetFormulaEngine, CSVDialectSniffer
- cloud: MultipartUploadManager, ContentAddressableStorage, BucketLifecycleEngine
- compression: BWTCompressor, DeflateEngine, ByteAlignedSnappy
- telecom: ViterbiDecoder, QAMModem, OFDMFramer
"""

import math
import pytest

from doomscript.domains.data.runtime import (
    RollingAggregator,
    RelationalJoinEngine,
    PivotTableEngine,
    data_relational_join,
    data_pivot_table,
    data_rolling_aggregate,
)
from doomscript.domains.office.runtime import (
    SpreadsheetFormulaEngine,
    CSVDialectSniffer,
    office_eval_spreadsheet,
    office_sniff_csv,
)
from doomscript.domains.cloud.runtime import (
    MultipartUploadManager,
    ContentAddressableStorage,
    BucketLifecycleEngine,
    cloud_multipart_initiate,
    cloud_cas_put,
    cloud_evaluate_lifecycle,
)
from doomscript.domains.compression.runtime import (
    BWTCompressor,
    DeflateEngine,
    ByteAlignedSnappy,
    compression_bwt_compress,
    compression_bwt_decompress,
    compression_deflate,
    compression_inflate,
    compression_snappy_compress,
    compression_snappy_decompress,
)
from doomscript.domains.telecom.runtime import (
    ViterbiDecoder,
    QAMModem,
    OFDMFramer,
    telecom_viterbi_encode,
    telecom_viterbi_decode,
    telecom_qam_modulate,
    telecom_qam_demodulate,
    telecom_ofdm_frame,
)


# ==============================================================================
# Data Tests
# ==============================================================================

def test_rolling_aggregator():
    data = [1.0, 2.0, 3.0, 4.0, 5.0]

    # Rolling Mean with window=3
    means = RollingAggregator.rolling_series(data, window=3, stat="mean")
    assert means[:2] == [None, None]
    assert abs(means[2] - 2.0) < 1e-4  # (1+2+3)/3 = 2
    assert abs(means[3] - 3.0) < 1e-4  # (2+3+4)/3 = 3
    assert abs(means[4] - 4.0) < 1e-4  # (3+4+5)/3 = 4

    # Rolling Sum with window=3
    sums = RollingAggregator.rolling_series(data, window=3, stat="sum")
    assert sums[2] == 6.0
    assert sums[3] == 9.0
    assert sums[4] == 12.0


def test_relational_join_engine():
    left = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"},
    ]
    right = [
        {"id": 1, "score": 95},
        {"id": 2, "score": 80},
        {"id": 4, "score": 70},
    ]

    # Inner Join
    inner = RelationalJoinEngine.join(left, right, on="id", how="inner")
    assert len(inner) == 2
    assert {r["name"] for r in inner} == {"Alice", "Bob"}
    assert inner[0]["score"] == 95

    # Left Join
    left_res = RelationalJoinEngine.join(left, right, on="id", how="left")
    assert len(left_res) == 3
    charlie = next(r for r in left_res if r["name"] == "Charlie")
    assert charlie["score"] is None

    # Cross Join
    cross = RelationalJoinEngine.join(left, right, on="id", how="cross")
    assert len(cross) == 9


def test_pivot_table_engine():
    records = [
        {"region": "North", "prod": "A", "sales": 100},
        {"region": "North", "prod": "B", "sales": 150},
        {"region": "North", "prod": "A", "sales": 50},
        {"region": "South", "prod": "A", "sales": 200},
        {"region": "South", "prod": "B", "sales": 300},
    ]

    pt = PivotTableEngine.pivot(records, index="region", columns="prod", values="sales", aggfunc="sum")
    assert pt["North"]["A"] == 150.0  # 100 + 50
    assert pt["North"]["B"] == 150.0
    assert pt["South"]["A"] == 200.0
    assert pt["South"]["B"] == 300.0


# ==============================================================================
# Office Tests
# ==============================================================================

def test_spreadsheet_formula_engine():
    grid = {
        "A1": 10.0,
        "A2": 20.0,
        "A3": "=SUM(A1:A2)",
        "A4": "=AVERAGE(A1:A2)",
        "B1": "=A3 * 2",
    }

    evaluated = SpreadsheetFormulaEngine.evaluate_grid(grid)
    assert evaluated["A3"] == 30.0
    assert evaluated["A4"] == 15.0
    assert evaluated["B1"] == 60.0

    # Test circular dependency raises ValueError
    cycle_grid = {
        "C1": "=C2 + 1",
        "C2": "=C1 + 1",
    }
    with pytest.raises(ValueError, match="Circular dependency"):
        SpreadsheetFormulaEngine.evaluate_grid(cycle_grid)


def test_csv_dialect_sniffer():
    csv_sample = """user_id;username;balance;active
101;alice;1500.50;true
102;bob;250.00;false
103;charlie;0.00;true
"""
    info = CSVDialectSniffer.sniff(csv_sample)
    assert info["delimiter"] == ";"
    assert info["has_header"] is True
    assert info["column_names"] == ["user_id", "username", "balance", "active"]
    assert info["column_types"] == ["integer", "string", "float", "boolean"]


# ==============================================================================
# Cloud Tests
# ==============================================================================

def test_multipart_upload_manager():
    mgr = MultipartUploadManager()
    upload_id = mgr.initiate_upload("my-bucket", "large_file.bin")
    assert upload_id.startswith("upload-")

    chunk1 = b"Part 1 data block: " * 10
    chunk2 = b"Part 2 data block: " * 10
    chunk3 = b"Part 3 final data."

    etag1 = mgr.upload_part(upload_id, 1, chunk1)
    etag2 = mgr.upload_part(upload_id, 2, chunk2)
    etag3 = mgr.upload_part(upload_id, 3, chunk3)

    parts = [
        {"part_number": 1, "etag": etag1},
        {"part_number": 2, "etag": etag2},
        {"part_number": 3, "etag": etag3},
    ]

    res = mgr.complete_upload(upload_id, parts)
    assert res["total_bytes"] == len(chunk1) + len(chunk2) + len(chunk3)
    assert res["parts_count"] == 3
    assert res["data"] == chunk1 + chunk2 + chunk3


def test_content_addressable_storage():
    cas = ContentAddressableStorage()
    data1 = b"Hello DoomScript CAS storage"
    data2 = b"Second distinct blob"

    h1 = cas.put(data1)
    h2 = cas.put(data2)
    h1_dup = cas.put(data1)

    assert h1 == h1_dup
    assert len(cas.blobs) == 2  # Deduplicated

    assert cas.get(h1) == data1
    assert cas.has(h2) is True

    # Garbage collection
    gc_res = cas.gc(active_hashes={h1})
    assert gc_res["deleted_count"] == 1
    assert not cas.has(h2)
    assert cas.has(h1)


def test_bucket_lifecycle_engine():
    now = 1700000000.0
    day = 86400.0

    objects = [
        {"key": "logs/app.log", "last_modified_epoch": now - 40 * day, "storage_class": "STANDARD"},
        {"key": "logs/recent.log", "last_modified_epoch": now - 5 * day, "storage_class": "STANDARD"},
        {"key": "backups/2023.tar", "last_modified_epoch": now - 100 * day, "storage_class": "STANDARD"},
    ]

    rules = [
        {"prefix": "logs/", "expire_days": 30},
        {"prefix": "backups/", "transition_days": 90, "target_tier": "GLACIER"},
    ]

    res = BucketLifecycleEngine.evaluate(objects, rules, current_time_epoch=now)
    assert len(res["expired"]) == 1
    assert res["expired"][0]["key"] == "logs/app.log"

    assert len(res["transitioned"]) == 1
    assert res["transitioned"][0]["key"] == "backups/2023.tar"
    assert res["transitioned"][0]["new_storage_class"] == "GLACIER"


# ==============================================================================
# Compression Tests
# ==============================================================================

def test_bwt_compressor():
    data = b"SIX.MIXED.PIXIES.SIFT.SIXTY.PIXIE.PIXES."
    bwt_text, p_idx = BWTCompressor.bwt_transform(data)
    recovered = BWTCompressor.bwt_inverse(bwt_text, p_idx)
    assert recovered == data

    # Full pipeline
    comp = BWTCompressor.compress(data)
    decomp = BWTCompressor.decompress(comp)
    assert decomp == data


def test_deflate_engine():
    data = b"The quick brown fox jumps over the lazy dog. The quick brown fox jumps again and again and again."
    compressed = DeflateEngine.compress(data)
    decompressed = DeflateEngine.decompress(compressed)
    assert decompressed == data


def test_byte_aligned_snappy():
    data = b"ABCDEF123456" * 20
    comp = ByteAlignedSnappy.compress(data)
    decomp = ByteAlignedSnappy.decompress(comp)
    assert decomp == data
    # Repeated pattern should compress
    assert len(comp) < len(data)


# ==============================================================================
# Telecom Tests
# ==============================================================================

def test_viterbi_decoder_error_correction():
    original_bits = [1, 0, 1, 1, 0, 0, 1, 0, 0, 0]  # with trailing flush zeros
    codeword = ViterbiDecoder.encode(original_bits)
    assert len(codeword) == len(original_bits) * 2

    # Inject single-bit error
    corrupted = list(codeword)
    corrupted[3] ^= 1  # Flip bit at index 3

    # Viterbi decoder should correct single bit error
    decoded = ViterbiDecoder.decode(corrupted)
    assert decoded[:len(original_bits)] == original_bits


def test_qam_modem():
    bits = [1, 0, 0, 1, 1, 1, 0, 0]

    # QPSK modulate & demodulate
    qpsk_symbols = QAMModem.modulate(bits, "QPSK")
    assert len(qpsk_symbols) == len(bits) // 2
    recovered_qpsk = QAMModem.demodulate(qpsk_symbols, "QPSK")
    assert recovered_qpsk == bits

    # 16-QAM modulate & demodulate
    qam16_symbols = QAMModem.modulate(bits, "16QAM")
    assert len(qam16_symbols) == len(bits) // 4
    recovered_16qam = QAMModem.demodulate(qam16_symbols, "16QAM")
    assert recovered_16qam == bits

    # EVM calculation
    evm = QAMModem.calculate_evm(qpsk_symbols, qpsk_symbols)
    assert evm["evm_percent"] == 0.0


def test_ofdm_framer():
    # 16 subcarriers QPSK
    bits = [1, 0] * 16
    subcarriers = QAMModem.modulate(bits, "QPSK")
    assert len(subcarriers) == 16

    # Modulate to time frame with CP=4
    time_frame = OFDMFramer.modulate_frame(subcarriers, n_fft=16, cp_len=4)
    assert len(time_frame) == 20  # 16 + 4

    # Demodulate back to frequency subcarriers
    recovered_sub = OFDMFramer.demodulate_frame(time_frame, n_fft=16, cp_len=4)
    assert len(recovered_sub) == 16

    # Check that demodulated subcarriers match original within numerical precision
    for orig, rec in zip(subcarriers, recovered_sub):
        assert abs(orig - rec) < 1e-4
