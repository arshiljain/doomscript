"""Comprehensive test suite for Cluster XIII deepened engines (Audio, Image, NLP, Cloud, DB).

Validates pure Python runtime engines and end-to-end spoken English .doom scripts.
"""

import math
import pytest
from doomscript.compiler.engine import execute

# Import runtime classes & functions
from doomscript.domains.audio.runtime import (
    HighOrderAmbisonics3D,
    DynamicRangeCompressorLimiter,
    audio_hoa_3d_encode,
    audio_hoa_binaural_decode,
    audio_dynamic_compressor,
)
from doomscript.domains.image.runtime import (
    FASTCornerAndHarrisDetector,
    HoughTransformLineDetector,
    image_detect_fast_corners,
    image_hough_lines,
)
from doomscript.domains.nlp.runtime import (
    TextRankSummarizer,
    LevenshteinAutomatonFuzzyMatcher,
    nlp_textrank_summarize,
    nlp_fuzzy_match,
    nlp_fuzzy_search_text,
)
from doomscript.domains.cloud.runtime import (
    DistributedConsistentHashRing,
    LeakyBucketTrafficShaper,
    cloud_hash_ring_create,
    cloud_hash_ring_get,
    cloud_hash_ring_preference_list,
    cloud_leaky_bucket_create,
    cloud_leaky_bucket_enqueue,
    cloud_leaky_bucket_drain,
)
from doomscript.domains.db.runtime import (
    BitmapIndexCompressor,
    LSMTreeCompactionEngine,
    db_bitmap_compress,
    db_bitmap_decompress,
    db_bitmap_and,
    db_bitmap_or,
    db_bitmap_not,
    db_bitmap_query_indices,
    db_lsm_create,
    db_lsm_put,
    db_lsm_get,
    db_lsm_delete,
    db_lsm_flush,
    db_lsm_compact,
)


# ==============================================================================
# AUDIO DOMAIN TESTS
# ==============================================================================

def test_audio_hoa_3d_ambisonics():
    signal = [1.0, 0.5, -0.5, 0.0]
    enc = HighOrderAmbisonics3D.encode_signal(signal, azimuth_deg=0.0, elevation_deg=0.0, order=1)
    assert len(enc["channels"]) == 4
    # Channel W = 1.0 * signal
    assert enc["channels"][0][0] == pytest.approx(1.0)
    # Channel X = cos(0)*cos(0)*sqrt(3)*signal
    assert enc["channels"][3][0] == pytest.approx(math.sqrt(3.0) * 1.0, abs=1e-3)

    # Decode binaural
    dec = HighOrderAmbisonics3D.decode_binaural(enc["channels"])
    assert len(dec["left"]) == 4
    assert len(dec["right"]) == 4


def test_audio_dynamic_range_compressor():
    samples = [0.1, 0.2, 0.8, 0.9, 0.85, 0.2, 0.1]
    res = DynamicRangeCompressorLimiter.process(
        samples, threshold_db=-12.0, ratio=4.0, attack_ms=1.0, release_ms=10.0, sample_rate=1000
    )
    assert len(res["output_samples"]) == len(samples)
    assert res["output_samples"][3] < 0.9
    assert res["max_gain_reduction_db"] <= 0.0


def test_audio_spoken_english():
    code = """use audio
set sig to [0.2, 0.8, 0.4, 0.1]
encode hoa 3d sig with azimuth 45.0 and elevation 0.0 into hoa_res
compress dynamic range sig with threshold -10.0 and ratio 3.0 into comp_res
"""
    env = execute(code)
    assert env["hoa_res"].order == 1
    assert len(env["hoa_res"].channels) == 4
    assert env["comp_res"].samples_count == 4


# ==============================================================================
# IMAGE DOMAIN TESTS
# ==============================================================================

def test_image_fast_corner_harris():
    mat = [[10.0] * 10 for _ in range(10)]
    mat[5][5] = 200.0
    res = FASTCornerAndHarrisDetector.detect(mat, threshold=30.0, min_contiguous=9)
    assert "num_corners" in res
    assert res["image_width"] == 10
    assert res["image_height"] == 10


def test_image_hough_lines():
    mat = [[0.0] * 20 for _ in range(20)]
    for c in range(20):
        mat[10][c] = 1.0
    res = HoughTransformLineDetector.detect(mat, threshold=10, num_rho=40, num_theta=30)
    assert res["lines_count"] > 0
    assert res["max_votes"] >= 10


def test_image_spoken_english():
    code = """use image
set edge_grid to [[0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
detect hough lines in image edge_grid with threshold 5 into hough_res
"""
    env = execute(code)
    assert env["hough_res"].lines_count >= 1


# ==============================================================================
# NLP DOMAIN TESTS
# ==============================================================================

def test_nlp_textrank_summarization():
    doc = (
        "Artificial intelligence is transforming software engineering. "
        "Compilers and languages are evolving to support automated agents. "
        "DoomScript provides native spoken English syntax for complex algorithms. "
        "Software engineering workflows benefit from clear declarative semantics. "
        "Natural language interfaces bridge human thought and program execution."
    )
    res = TextRankSummarizer.summarize(doc, num_sentences=2)
    assert res["num_sentences"] == 2
    assert res["total_sentences"] == 5
    assert len(res["summary"]) > 0
    assert len(res["ranked_sentences"]) == 5


def test_nlp_fuzzy_matching():
    vocab = ["algorithm", "algorithmic", "algebra", "logarithm", "rhythm"]
    res = LevenshteinAutomatonFuzzyMatcher.match("algoritm", vocab, max_distance=2)
    assert res["matches_count"] >= 1
    top_word = res["matches"][0].word
    assert top_word == "algorithm"
    assert res["matches"][0].distance == 1


def test_nlp_spoken_english():
    code = """use nlp
set text_doc to "Alpha is the beginning. Beta follows alpha closely. Gamma tests the system after beta. Delta finalizes deployment."
summarize text text_doc with 2 sentences into summary_res
set dict_words to ["database", "dataset", "datagram", "network"]
fuzzy match "databse" in dictionary dict_words with max distance 1 into fuzzy_res
"""
    env = execute(code)
    assert env["summary_res"].num_sentences == 2
    assert env["fuzzy_res"].matches_count == 1
    assert env["fuzzy_res"].matches[0].word == "database"


# ==============================================================================
# CLOUD DOMAIN TESTS
# ==============================================================================

def test_cloud_consistent_hash_ring():
    ring = DistributedConsistentHashRing(default_vnodes=30)
    ring.add_node("node-east-1")
    ring.add_node("node-west-1")
    ring.add_node("node-central-1")

    node1 = ring.get_node("user:10492")
    node2 = ring.get_node("user:10492")
    assert node1 == node2
    assert node1 in {"node-east-1", "node-west-1", "node-central-1"}

    prefs = ring.get_preference_list("user:10492", count=2)
    assert len(prefs) == 2
    assert prefs[0] != prefs[1]


def test_cloud_leaky_bucket():
    bucket = LeakyBucketTrafficShaper(capacity=3, leak_rate=1.0)
    t0 = 1000.0
    r1 = bucket.enqueue("pkt1", current_time=t0)
    r2 = bucket.enqueue("pkt2", current_time=t0)
    r3 = bucket.enqueue("pkt3", current_time=t0)
    r4 = bucket.enqueue("pkt4", current_time=t0)
    assert r1["accepted"] is True
    assert r2["accepted"] is True
    assert r3["accepted"] is True
    assert r4["accepted"] is False
    assert r4["dropped"] is True

    # 2 seconds later, 2 packets leak out
    drained = bucket.drain(current_time=t0 + 2.0)
    assert len(drained) == 2
    assert drained == ["pkt1", "pkt2"]


def test_cloud_spoken_english():
    code = """use cloud
set nodes_list to ["alpha-node", "beta-node", "gamma-node"]
create hash ring with nodes nodes_list and vnodes 25 into my_ring
lookup node for key "session-token-9981" in hash ring my_ring into target_node
create leaky bucket with capacity 5 and leak rate 10 into my_bucket
enqueue packet "req-001" into leaky bucket my_bucket into enq_res
"""
    env = execute(code)
    assert env["my_ring"].nodes_count == 3
    assert env["target_node"] in ["alpha-node", "beta-node", "gamma-node"]
    assert env["enq_res"].accepted is True


# ==============================================================================
# DB DOMAIN TESTS
# ==============================================================================

def test_db_bitmap_compressor():
    bits1 = [1, 1, 1, 0, 0, 1, 0, 1, 1]
    bits2 = [1, 0, 1, 0, 1, 1, 0, 0, 1]
    c1 = BitmapIndexCompressor.compress(bits1)
    c2 = BitmapIndexCompressor.compress(bits2)
    assert BitmapIndexCompressor.decompress(c1) == bits1

    and_c = BitmapIndexCompressor.bitwise_and(c1, c2)
    and_bits = BitmapIndexCompressor.decompress(and_c)
    expected_and = [b1 & b2 for b1, b2 in zip(bits1, bits2)]
    assert and_bits == expected_and

    indices = BitmapIndexCompressor.query_indices(and_c)
    assert indices == [0, 2, 5, 8]


def test_db_lsm_tree():
    lsm = LSMTreeCompactionEngine(memtable_threshold=3)
    lsm.put("user:1", "Alice")
    lsm.put("user:2", "Bob")
    lsm.put("user:3", "Charlie")
    assert len(lsm.level0) == 1
    assert len(lsm.memtable) == 0

    assert lsm.get("user:2") == "Bob"

    lsm.put("user:4", "David")
    lsm.put("user:2", "Bob Updated")
    lsm.delete("user:1")
    assert len(lsm.level0) == 2

    assert lsm.get("user:2") == "Bob Updated"
    assert lsm.get("user:1") is None

    comp = lsm.compact_level0_to_level1()
    assert comp["compacted_tables"] == 2
    assert len(lsm.level0) == 0
    assert lsm.get("user:2") == "Bob Updated"
    assert lsm.get("user:1") is None


def test_db_spoken_english():
    code = """use db
set raw_bits to [1, 1, 0, 0, 1, 1, 1, 0]
compress bitmap raw_bits into bmp_res
query bitmap indices in bmp_res into idx_res

create lsm tree with threshold 2 into lsm_store
lsm put "config:mode" with value "production" into lsm_store
lsm put "config:port" with value 8080 into lsm_store
lsm get "config:mode" from lsm_store into mode_val
lsm compact lsm_store into cmp_res
"""
    env = execute(code)
    assert env["idx_res"] == [0, 1, 4, 5, 6]
    assert env["mode_val"] == "production"
    assert env["cmp_res"].compacted_tables == 1
