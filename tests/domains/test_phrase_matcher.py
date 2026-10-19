"""Unit tests for EnglishPhraseMatcher and declarative VerbSpec architecture."""

import pytest
from doomscript.domains.matcher import (
    EnglishPhraseMatcher,
    VerbSpec,
    PhraseMatchResult,
    suggest_near_miss_verb,
)


def test_phrase_matcher_basic_and_synonyms():
    v = VerbSpec(
        pattern="[fetch] stock [prices] [for] {symbol:expr} [from {start:expr}] [to {end:expr}] into {target:ident}",
        emit="set {target} to fetch_stock_prices({symbol}, start_date={start|'2024-01-01'}, end_date={end|'2024-12-31'})",
        doc="Fetches stock prices",
    )
    matcher = EnglishPhraseMatcher([v])

    # Test full phrase
    res1 = matcher.match('fetch stock prices for "AAPL" from "2024-01-01" to "2024-12-31" into quotes')
    assert res1 is not None
    assert res1.emitted == 'set quotes to fetch_stock_prices("AAPL", start_date="2024-01-01", end_date="2024-12-31")'

    # Test optional tokens omitted
    res2 = matcher.match('fetch stock "AAPL" into q')
    assert res2 is not None
    assert res2.emitted == "set q to fetch_stock_prices(\"AAPL\", start_date='2024-01-01', end_date='2024-12-31')"


def test_phrase_matcher_alternatives_and_numbers():
    v = VerbSpec(
        pattern="[calculate] {window:int} day (moving average|sma|ema) [of] {series:expr} into {target:ident}",
        emit="set {target} to moving_average({series}, window={window}, kind='{_group1}')",
        doc="Calculates moving average",
    )
    matcher = EnglishPhraseMatcher([v])

    res = matcher.match("calculate 20 day sma of prices into trend")
    assert res is not None
    assert "window=20" in res.emitted
    assert "kind='sma'" in res.emitted
    assert "trend" in res.emitted


def test_near_miss_diagnostic():
    v = VerbSpec(
        pattern="orders where {condition:expr} into {target:ident}",
        emit="set {target} to filter_records(orders, {condition})",
        doc="Filters records",
    )
    suggestion = suggest_near_miss_verb('orders where status is "paid"', [v])
    assert suggestion is not None
    assert "into" in suggestion
