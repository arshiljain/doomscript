"""
Comprehensive Test Suite for DoomScript Natural English Units of Measurement System.
Tests physical, temporal, digital, temperature, and financial quantities,
dimensional analysis, conversions, arithmetic, comparisons, and ergonomic syntax.
"""

import io
import contextlib
import textwrap
import pytest
from doomscript.compiler.engine import execute
from doomscript.core.units import Quantity, make_quantity, convert_unit
from doomscript.exceptions import DoomTypeError, DoomValueError


def run_code(code: str) -> str:
    """Executes DoomScript code and captures standard output."""
    dedented = textwrap.dedent(code).strip()
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        execute(dedented)
    return f.getvalue().strip()


def test_units_core_creation():
    q1 = make_quantity(10, "kilometers")
    assert q1.value == 10.0
    assert q1.unit == "kilometers"
    assert q1.dimension == "length"

    q2 = make_quantity(60, "miles per hour")
    assert q2.value == 60.0
    assert q2.dimension == "speed"

    q3 = make_quantity(500, "megabytes")
    assert q3.value == 500.0
    assert q3.dimension == "data"


def test_units_unknown_unit_error():
    with pytest.raises(DoomValueError) as excinfo:
        make_quantity(10, "lightyears_unknown")
    assert "Unknown unit of measurement" in str(excinfo.value)


def test_units_addition_and_subtraction():
    out = run_code("""
    set dist1 to 5 kilometers
    set dist2 to 500 meters
    set total to dist1 + dist2
    set diff to dist1 - dist2
    say total
    say diff
    """)
    lines = out.splitlines()
    assert lines[0] == "5.5 kilometers"
    assert lines[1] == "4.5 kilometers"


def test_units_scalar_multiplication_division():
    out = run_code("""
    set speed to 30 miles per hour
    set double_speed to speed * 2
    set half_speed to speed / 2
    say double_speed
    say half_speed
    """)
    lines = out.splitlines()
    assert lines[0] == "60 miles per hour"
    assert lines[1] == "15 miles per hour"


def test_units_dimensional_analysis_speed_time_distance():
    out = run_code("""
    set speed to 60 miles per hour
    set travel_time to 2.5 hours
    set distance to speed * travel_time
    set calc_speed to distance / travel_time
    set calc_time to distance / speed
    say distance
    say calc_speed
    say calc_time
    """)
    lines = out.splitlines()
    assert lines[0] == "150 miles"
    assert lines[1] == "60 miles per hour"
    assert lines[2] == "2.5 hours"


def test_units_dimensionless_ratio():
    out = run_code("""
    set d1 to 100 meters
    set d2 to 20 meters
    set ratio to d1 / d2
    say ratio
    """)
    assert out == "5.0"


def test_units_temperature_affine_conversion():
    out = run_code("""
    set room_temp to 72 degrees fahrenheit
    convert room_temp to celsius into temp_c
    convert 0 celsius to fahrenheit into freeze_f
    convert 0 celsius to kelvin into freeze_k
    say temp_c
    say freeze_f
    say freeze_k
    """)
    lines = out.splitlines()
    assert "22.22" in lines[0]
    assert "32 fahrenheit" in lines[1]
    assert "273.15 kelvin" in lines[2]


def test_units_currency():
    out = run_code("""
    set price to $100
    set budget to 500 dollars
    set euro_price to €50
    set pound_price to £20
    say price
    say budget
    say euro_price
    say pound_price
    """)
    lines = out.splitlines()
    assert "100 dollars" in lines[0]
    assert "500 dollars" in lines[1]
    assert "50 euros" in lines[2]
    assert "20 pounds sterling" in lines[3]


def test_units_statement_conversion():
    out = run_code("""
    set distance to 10 kilometers
    convert distance to miles into dist_mi
    convert 500 megabytes to gigabytes into gb_val
    say dist_mi
    say gb_val
    """)
    lines = out.splitlines()
    assert "6.2137" in lines[0]
    assert "miles" in lines[0]
    assert "0.488" in lines[1] or "0.5" in lines[1]
    assert "gigabytes" in lines[1]


def test_units_expression_conversion():
    out = run_code("""
    set dist_km to 10 kilometers
    say dist_km in miles
    say 72 degrees fahrenheit in celsius
    """)
    lines = out.splitlines()
    assert "6.2137" in lines[0]
    assert "22.22" in lines[1]


def test_units_comparisons():
    out = run_code("""
    if 500 meters < 1 kilometer:
        say "500m is less than 1km"
    if 1000 milliseconds == 1 second:
        say "1000ms equals 1s"
    if 75 degrees fahrenheit > 20 degrees celsius:
        say "75F is warmer than 20C"
    """)
    lines = out.splitlines()
    assert "500m is less than 1km" in lines
    assert "1000ms equals 1s" in lines
    assert "75F is warmer than 20C" in lines


def test_units_relative_time_protection():
    out = run_code("""
    set future to 2 days from now
    set past to 3 hours ago
    say "Relative time parsed cleanly"
    """)
    assert "Relative time parsed cleanly" in out


def test_units_for_loop_protection():
    out = run_code("""
    set days to [1, 2, 3]
    set total to 0
    for day in days:
        total = total + day
    say total
    """)
    assert out == "6"


def test_units_incompatible_dimensions_error():
    with pytest.raises(DoomTypeError) as excinfo:
        execute("set bad to 10 meters + 5 seconds")
    assert "incompatible" in str(excinfo.value).lower()

    with pytest.raises(DoomTypeError) as excinfo:
        execute("convert 10 meters to seconds into bad")
    assert "dimensions must match" in str(excinfo.value).lower()


def test_units_properties_and_helpers():
    out = run_code("""
    set d to 10 kilometers
    say d.value
    say d.unit
    say d.dimension
    say to_number(d)
    """)
    lines = out.splitlines()
    assert "10" in lines[0]
    assert lines[1] == "kilometers"
    assert lines[2] == "length"
    assert "10" in lines[3]


def test_units_timing_sleep():
    out = run_code("""
    sleep 10 milliseconds
    wait 10 ms
    say "Timing passed"
    """)
    assert out == "Timing passed"
