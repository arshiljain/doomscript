import pytest
from doomscript.taxonomy import Table, to_table, to_records, ValueKind, classify_value
from doomscript.runtime import Record

def test_table_recordlist_conversion():
    records = [
        Record(name="Alice", score=95, active=True),
        Record(name="Bob", score=82, active=False),
    ]
    tbl = to_table(records)
    assert tbl.row_count == 2
    assert tbl.columns == ["name", "score", "active"]
    assert tbl.schema["score"] in ("int", "number")

    # Roundtrip conversion
    restored = to_records(tbl)
    assert len(restored) == 2
    assert restored[0]["name"] == "Alice"
    assert restored[0].score == 95

    # Markdown & HTML representation
    md = tbl.to_markdown()
    assert "| name | score | active |" in md
    html = tbl.to_html()
    assert "<table>" in html

def test_table_from_dict_of_columns():
    col_data = {
        "ticker": ["AAPL", "MSFT", "GOOGL"],
        "price": [150.5, 300.2, 140.8],
        "volume": [1000, 2500, 1800],
    }
    tbl = to_table(col_data)
    assert tbl.row_count == 3
    assert tbl.columns == ["ticker", "price", "volume"]
    assert tbl.schema["price"] in ("float", "number")
    assert tbl.schema["volume"] in ("int", "number")

    records = to_records(tbl)
    assert len(records) == 3
    assert records[1].ticker == "MSFT"
    assert records[1].price == 300.2

def test_value_taxonomy_classification():
    assert classify_value(42) == ValueKind.SCALAR
    assert classify_value("hello") == ValueKind.SCALAR
    assert classify_value([1, 2, 3]) == ValueKind.COLLECTION
    assert classify_value(Record(a=1)) == ValueKind.RECORD
    assert classify_value([Record(a=1), Record(a=2)]) == ValueKind.RECORD_LIST
    
    tbl = Table(columns=["a"], rows=[[1]])
    assert classify_value(tbl) == ValueKind.TABLE
