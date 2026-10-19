"""Comprehensive test suite for Phase 2 new domains:
- chem (Domain 31)
- compression (Domain 32)
- time_series (Domain 33)
- symbolic (Domain 34)
- graphics (Domain 35)
"""

import pytest
import math
from doomscript.compiler.engine import execute


def test_chem_domain():
    code = """
use chem
mw_water = chem_molecular_weight("H2O")
mw_glucose = chem_molecular_weight("C6H12O6")
mw_hydrate = chem_molecular_weight("CuSO4*5H2O")
comp_water = chem_elemental_composition("H2O")

# Reaction balancing: C6H12O6 + O2 -> CO2 + H2O
balanced = chem_balance_reaction(["C6H12O6", "O2"], ["CO2", "H2O"])

# Parse SMILES: Benzene c1ccccc1
benzene = chem_parse_smiles("c1ccccc1")
"""
    env = execute(code)
    # H2O: 2 * 1.008 + 15.999 = 18.015
    assert abs(env["mw_water"] - 18.015) < 0.05
    # Glucose: 6*12.011 + 12*1.008 + 6*15.999 = 180.156
    assert abs(env["mw_glucose"] - 180.16) < 0.1
    # CuSO4*5H2O: Cu: 63.546 + S: 32.06 + 4*O: 63.996 + 5*18.015 = 249.677
    assert abs(env["mw_hydrate"] - 249.68) < 0.2
    assert env["comp_water"]["O"] > 88.0
    # Balanced combustion: 1 C6H12O6 + 6 O2 -> 6 CO2 + 6 H2O
    assert env["balanced"]["reactants"]["C6H12O6"] == 1
    assert env["balanced"]["reactants"]["O2"] == 6
    assert env["balanced"]["products"]["CO2"] == 6
    assert env["balanced"]["products"]["H2O"] == 6
    # Benzene aromaticity
    assert env["benzene"]["num_atoms"] == 6
    assert len(env["benzene"]["rings"]) == 1
    assert env["benzene"]["rings"][0]["is_aromatic"] is True


def test_compression_domain():
    code = """
use compression
msg = "ABRACADABRA_ABRACADABRA"
ent = compression_entropy(msg)

rle_runs = compression_rle_encode("WWWWWWAAAAAABBBB")
rle_dec = compression_rle_decode(rle_runs)

huff = compression_huffman_encode(msg)
huff_dec = compression_huffman_decode(huff)

lzw_codes = compression_lzw_encode(msg)
lzw_dec = compression_lzw_decode(lzw_codes)

lz77_tokens = compression_lz77_encode(msg)
lz77_dec = compression_lz77_decode(lz77_tokens)
"""
    env = execute(code)
    assert env["ent"] > 0.0
    assert env["rle_dec"] == "WWWWWWAAAAAABBBB"
    assert env["huff_dec"] == "ABRACADABRA_ABRACADABRA"
    assert env["huff"]["compressed_bits"] < env["huff"]["uncompressed_bits"]
    assert env["lzw_dec"] == "ABRACADABRA_ABRACADABRA"
    assert len(env["lzw_codes"]) < len("ABRACADABRA_ABRACADABRA")
    assert env["lz77_dec"] == "ABRACADABRA_ABRACADABRA"


def test_time_series_domain():
    code = """
use time_series
# Synthetic seasonal series with period 4
raw_series = [
    10.0, 20.0, 15.0, 5.0,
    12.0, 22.0, 17.0, 7.0,
    14.0, 24.0, 19.0, 9.0,
    16.0, 26.0, 21.0, 11.0
]
decomp = time_series_decompose(raw_series, period=4, model="additive")
acf_vals = time_series_acf(raw_series, nlags=5)
pacf_vals = time_series_pacf(raw_series, nlags=5)
diff_vals = time_series_difference(raw_series, order=1)
forecasts = time_series_holt_winters(raw_series, period=4, alpha=0.3, beta=0.1, gamma=0.3, n_preds=4)
"""
    env = execute(code)
    assert len(env["decomp"]["seasonal"]) == 16
    assert env["acf_vals"][0] == 1.0
    assert len(env["pacf_vals"]) == 6
    assert len(env["diff_vals"]) == 15
    assert len(env["forecasts"]) == 4
    # Future forecasts should follow the upward trend
    assert env["forecasts"][0] > 10.0


def test_symbolic_domain():
    code = """
use symbolic
# Polynomial derivative: d/dx (x^3 + 2*x^2 - 5*x + 7)
d1 = symbolic_diff("x^3 + 2*x^2 - 5*x + 7", var="x")
val1 = symbolic_eval(d1, {"x": 2.0})

# Trigonometric and chain rule: d/dx sin(x^2)
d2 = symbolic_diff("sin(x^2)", var="x")

# Simplification: (x + 0) * 1 + x * 0
s1 = symbolic_simplify("x + 0")

# Polynomial GCD of (x - 1)(x - 2) = x^2 - 3x + 2 and (x - 2)(x - 3) = x^2 - 5x + 6
# GCD should be (x - 2), i.e. coefficients [1.0, -2.0]
gcd_poly = symbolic_poly_gcd([1.0, -3.0, 2.0], [1.0, -5.0, 6.0])
"""
    env = execute(code)
    # d/dx at x=2: 3*(2^2) + 4*(2) - 5 = 12 + 8 - 5 = 15
    assert abs(env["val1"] - 15.0) < 1e-4
    assert str(env["s1"]) == "x"
    assert env["gcd_poly"] == [1.0, -2.0]


def test_graphics_domain():
    code = """
use graphics
fb = graphics_create_framebuffer(64, 64, (0, 0, 0, 255))
zb = graphics_create_depthbuffer(64, 64)

# Draw 2D lines and circle
graphics_draw_line(fb, 0, 0, 63, 63, (255, 0, 0, 255))
graphics_draw_circle(fb, 32, 32, 10, (0, 255, 0, 255), fill=True)
graphics_draw_rect(fb, 5, 5, 20, 20, (0, 0, 255, 255), fill=False)

# Draw 3D Gouraud-shaded triangle
v0 = (10.0, 10.0, 1.0)
v1 = (50.0, 10.0, 2.0)
v2 = (30.0, 50.0, 1.5)
c0 = (255, 0, 0)
c1 = (0, 255, 0)
c2 = (0, 0, 255)
graphics_draw_triangle(fb, zb, v0, v1, v2, c0, c1, c2)

# Export formats
ppm_str = fb.to_ppm()
bmp_bytes = fb.to_bmp()
"""
    env = execute(code)
    assert env["fb"].width == 64
    assert env["fb"].height == 64
    assert env["ppm_str"].startswith("P3")
    assert env["bmp_bytes"].startswith(b"BM")
    assert len(env["bmp_bytes"]) > 54
