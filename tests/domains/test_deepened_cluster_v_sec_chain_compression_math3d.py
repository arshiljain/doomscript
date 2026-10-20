"""Integration and verification test suite for Deepened Cluster V:
Security, Blockchain, Compression, and Math3D domains in DoomScript.

Validates pure Python algorithms and native spoken-English .doom code execution.
"""

import pytest
from doomscript.compiler.engine import execute


# ==============================================================================
# SECURITY (SEC) TESTS
# ==============================================================================

def test_sec_pbkdf2_key_derivation():
    """Validates PBKDF2 HMAC-SHA256 key derivation."""
    code = """
use sec
derive pbkdf2 key for "SuperSecretPassword123" with salt "SaltValue987" with iterations 1000 into key_res
assert key_res's key_hex is not empty
assert key_res's key_length equals 32
assert key_res's iterations equals 1000
"""
    env = execute(code)
    res = env["key_res"]
    assert res.key_length == 32
    assert len(res.key_hex) == 64


def test_sec_totp_authentication():
    """Validates RFC 6238 TOTP token generation and time-step verification."""
    code = """
use sec
generate totp token for secret "JBSWY3DPEHPK3PXP" into token_val
verify totp token token_val for secret "JBSWY3DPEHPK3PXP" into is_valid
assert is_valid is true
"""
    env = execute(code)
    assert len(env["token_val"]) == 6
    assert env["is_valid"] is True


def test_sec_shamir_secret_sharing():
    """Validates Shamir's (3, 5) threshold secret sharing and reconstruction."""
    code = """
use sec
split secret 424242 with threshold 3 total 5 into split_res
set my_shares to split_res's shares
set recovery_subset to [my_shares[0], my_shares[2], my_shares[4]]
combine secret shares recovery_subset into recovered_secret
assert recovered_secret equals 424242
"""
    env = execute(code)
    assert env["recovered_secret"] == 424242


# ==============================================================================
# BLOCKCHAIN (CHAIN) TESTS
# ==============================================================================

def test_chain_merkle_patricia_trie():
    """Validates Merkle Patricia Trie construction and state root calculation."""
    code = """
use chain
create merkle patricia trie into mpt
get mpt root of mpt into root_hex
assert root_hex is not empty
"""
    env = execute(code)
    assert len(env["root_hex"]) == 64


def test_chain_proof_of_stake_consensus():
    """Validates PoS proposer election and 2/3 supermajority finalization."""
    code = """
use chain
set vals to [{"address": "val_1", "stake": 100}, {"address": "val_2", "stake": 200}, {"address": "val_3", "stake": 300}]
create pos validator pool with validators vals into engine
select pos proposer for slot 42 in engine into proposer
assert proposer is not empty

finalize pos block "0xabcdef1234567890" with voters ["val_1", "val_2", "val_3"] in engine into fin_res
assert fin_res's finalized is true
assert fin_res's vote_percentage is over 0.66
"""
    env = execute(code)
    assert env["proposer"] in ["val_1", "val_2", "val_3"]
    fin = env["fin_res"]
    assert fin.finalized is True
    assert fin.vote_percentage > 0.66


# ==============================================================================
# COMPRESSION TESTS
# ==============================================================================

def test_compression_delta_bit_packing():
    """Validates columnar integer delta differencing and bit packing roundtrip."""
    code = """
use compression
set timestamps to [1000, 1005, 1012, 1018, 1025, 1030, 1031]
compress integers timestamps with delta bit packing into packed_res
assert packed_res's num_elements equals 7
assert packed_res's bit_width is over 0
assert packed_res's compression_ratio is over 0.0

decompress delta bit packing packed_res into unpacked_seq
assert unpacked_seq equals timestamps
"""
    env = execute(code)
    packed = env["packed_res"]
    unpacked = env["unpacked_seq"]
    assert packed.num_elements == 7
    assert unpacked == [1000, 1005, 1012, 1018, 1025, 1030, 1031]


# ==============================================================================
# MATH3D TESTS
# ==============================================================================

def test_math3d_obb_sat_collision():
    """Validates 3D Oriented Bounding Box 15-axis SAT collision and separation."""
    code = """
use math3d
create obb at [0, 0, 0] with extents [1, 1, 1] into box_a
create obb at [1.5, 0, 0] with extents [1, 1, 1] into box_b_overlap
create obb at [5, 0, 0] with extents [1, 1, 1] into box_c_disjoint

test obb collision between box_a and box_b_overlap into hit_res
assert hit_res's colliding is true
assert hit_res's penetration_depth is over 0.0

test obb collision between box_a and box_c_disjoint into miss_res
assert miss_res's colliding is false
assert miss_res's distance is over 0.0
"""
    env = execute(code)
    hit = env["hit_res"]
    miss = env["miss_res"]
    assert hit.colliding is True
    assert hit.penetration_depth > 0.0
    assert miss.colliding is False
    assert miss.distance > 0.0


def test_math3d_frustum_sphere_culling():
    """Validates 6-plane camera frustum sphere culling."""
    code = """
use math3d
create frustum with fov 60 and aspect 1.333 and near 0.1 and far 100 into cam_frustum
cull sphere at [0, 0, -10] with radius 1 against frustum cam_frustum into in_res
cull sphere at [0, 50, -10] with radius 1 against frustum cam_frustum into out_res

assert in_res's visible is true
assert out_res's visible is false
assert out_res's status equals "OUTSIDE"
"""
    env = execute(code)
    in_sphere = env["in_res"]
    out_sphere = env["out_res"]
    assert in_sphere.visible is True
    assert out_sphere.visible is False
    assert out_sphere.status == "OUTSIDE"


def test_math3d_bvh_spatial_raycast():
    """Validates BVH spatial acceleration tree building and ray intersection."""
    code = """
use math3d
set tri1 to [[-1, -1, -5], [1, -1, -5], [0, 1, -5]]
set tri2 to [[10, 10, -5], [12, 10, -5], [11, 12, -5]]
build bvh tree from triangles [tri1, tri2] into bvh_tree
assert bvh_tree's num_triangles equals 2

trace ray [0, 0, 0] with direction [0, 0, -1] in bvh bvh_tree into ray_hit
assert ray_hit's hit is true
assert ray_hit's triangle_index equals 0
assert ray_hit's t equals 5.0
"""
    env = execute(code)
    hit = env["ray_hit"]
    assert hit.hit is True
    assert hit.triangle_index == 0
    assert abs(hit.t - 5.0) < 1e-4
