import pytest
import sqlite3
import os
from doomscript.compiler.engine import execute

def test_batch8_image_processing():
    # Tests image processing operations using PureImage fallback
    code = """
use image

create blank image with width 100 height 100 color [100, 150, 200] into img
convert image img to grayscale into gray_img
apply blur with radius 2 to image img into blurred
resize image img to width 50 height 50 into thumb
crop box [10, 10, 40, 40] from image img into cropped
rotate image img by 90 degrees into rotated
adjust brightness of image img by factor 1.2 into bright
calculate histogram of image img into hist
"""
    result = execute(code)
    assert "img" in result
    assert "gray_img" in result
    assert "blurred" in result
    assert "thumb" in result
    assert "cropped" in result
    assert "rotated" in result
    assert "bright" in result
    assert "hist" in result

    assert result["thumb"].width == 50
    assert result["thumb"].height == 50
    assert result["cropped"].width == 30
    assert result["cropped"].height == 30
    assert isinstance(result["hist"], (list, dict))
    assert len(result["hist"]) > 0

def test_batch9_web_scraping():
    code = """
use web

set html_doc to "<html><head><meta name='author' content='DoomAuthor'><title>Test</title></head><body><p class='intro'>First</p><p>Second</p><table><tr><th>Name</th><th>Age</th></tr><tr><td>Alice</td><td>30</td></tr></table></body></html>"

select all "p" elements from html_doc into paragraphs
extract all tables from html_doc into tables
parse query params from "https://example.com/search?q=doomscript&page=2" into params
build url "https://example.com/api" with params params into full_url
strip html tags from "<p>Hello <b>World</b>!</p>" into clean_text
extract meta tags from html_doc into meta_info
check if response {"status_code": 200} is successful into is_ok
"""
    result = execute(code)
    assert len(result["paragraphs"]) == 2
    assert "First" in result["paragraphs"][0]
    assert len(result["tables"]) == 1
    assert result["tables"][0]["Name"] == "Alice"
    assert result["tables"][0]["Age"] == "30"
    assert result["params"] == {"q": "doomscript", "page": "2"}
    assert "https://example.com/api?" in result["full_url"]
    assert "q=doomscript" in result["full_url"]
    assert result["clean_text"] == "Hello World!"
    assert result["meta_info"].get("author") == "DoomAuthor"
    assert result["is_ok"] is True

def test_batch10_audio_synthesis():
    code = """
use audio

generate sine tone at 440 hz for 0.1 seconds into tone
normalize audio track tone into norm_audio
get duration of audio track tone into duration_sec
apply fade in of 0.02 seconds to audio track tone into faded
reverse audio track tone into reversed_audio
concatenate audio track tone with norm_audio into joined_audio
"""
    result = execute(code)
    tone = result["tone"]
    assert tone.sample_rate == 44100
    assert len(tone.samples) == int(44100 * 0.1)
    assert abs(result["duration_sec"] - 0.1) < 0.01
    assert len(result["joined_audio"].samples) == len(tone.samples) * 2
    assert len(result["faded"].samples) == len(tone.samples)
    assert len(result["reversed_audio"].samples) == len(tone.samples)

def test_batch11_database_operations(tmp_path):
    db_file = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_file)
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    conn.execute("INSERT INTO users VALUES (1, 'Alice', 25)")
    conn.execute("INSERT INTO users VALUES (2, 'Bob', 35)")
    conn.execute("CREATE TABLE temp_data (val TEXT)")
    conn.execute("INSERT INTO temp_data VALUES ('temp1')")
    conn.commit()
    conn.close()

    code = f"""
use db

connect to sqlite "{db_file.replace(chr(92), '/')}" into db_conn
inspect database schema of db_conn into schema_info
upsert record {{"id": 3, "name": "Charlie", "age": 40}} into table "users" with key "id" using db_conn into upsert_res
count rows in table "users" where "age > 30" using db_conn into count_res
truncate table "temp_data" using db_conn into trunc_res
optimize database using db_conn into opt_res
backup database db_conn to "{(str(tmp_path / 'backup.db')).replace(chr(92), '/')}" into backup_res
"""
    result = execute(code)
    assert "users" in result["schema_info"]
    assert result["count_res"] == 2  # Bob (35) and Charlie (40)
    assert result["trunc_res"] is True
    assert result["opt_res"] is True
    assert os.path.exists(str(tmp_path / "backup.db"))
