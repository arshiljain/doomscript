"""
Tests for DoomScript Phases 14 to 25:
AI, ORM, DocGen, Markdown/HTML, Watcher, Scheduler, Crypto, Streaming, Binary/Hex, Config, Benchmarking, Packager.
"""

import os
import time
from pathlib import Path
import pytest
from typer.testing import CliRunner

from doomscript.cli import app
from doomscript.compiler.engine import execute, compile_to_ast, transpile
from doomscript.docgen import build_docs
from doomscript.bench import benchmark_script
from doomscript.pack import pack_script
from doomscript.watcher import get_file_mtimes

runner = CliRunner()


def test_phase14_ai_primitives():
    code = """
set query to "Summarize the quarterly earnings report"
ask ai query into ai_summary
ask ai query as json into ai_record
"""
    ns = execute(code)
    assert "ai_summary" in ns
    assert "AI response for:" in ns["ai_summary"]
    assert "ai_record" in ns
    assert ns["ai_record"].status == "ok"


def test_phase15_database_orm():
    code = """
define entity Product with name as text, price as number, in_stock as boolean

save new Product with name "Cyber Blade", price 450, in_stock true into p1
save new Product with name "Plasma Grenade", price 120, in_stock false into p2

find all Products into catalog
find first Product into first_item
"""
    ns = execute(code)
    assert ns["p1"].id == 1
    assert ns["p1"].name == "Cyber Blade"
    assert ns["p2"].id == 2
    assert len(ns["catalog"]) == 2
    assert ns["first_item"].name == "Cyber Blade"


def test_phase16_docgen_cli(tmp_path):
    demo_file = tmp_path / "service.doom"
    demo_file.write_text("""# Payment and billing service
to process_charge with card_id, amount:
    return true

define entity Account with owner as text, balance as number

on post "/api/v1/charge":
    reply with json {"success": true}
""", encoding="utf-8")

    out_html = tmp_path / "docs" / "index.html"
    build_docs(tmp_path, out_html)
    assert out_html.exists()
    content = out_html.read_text(encoding="utf-8")
    assert "process_charge" in content
    assert "Account" in content
    assert "/api/v1/charge" in content


def test_phase17_document_generator(tmp_path):
    code = f"""
create markdown document into doc
add heading "Quarterly Performance" at level 1 to doc
add paragraph "The division exceeded targets across all metrics." to doc
add table with headers ["Dept", "Revenue"] and rows [["R&D", 50000], ["Sales", 120000]] to doc
add bullet list ["Completed migration", "Zero downtime"] to doc

render document doc as markdown into md_text
render document doc as html into html_text
save document doc to file "{tmp_path.as_posix()}/report.md"
"""
    ns = execute(code)
    assert "# Quarterly Performance" in ns["md_text"]
    assert "| Dept | Revenue |" in ns["md_text"]
    assert "<h1>Quarterly Performance</h1>" in ns["html_text"]
    assert (tmp_path / "report.md").exists()


def test_phase18_watcher_mtimes(tmp_path):
    test_f = tmp_path / "sample.doom"
    test_f.write_text("say 1", encoding="utf-8")
    mtimes = get_file_mtimes(tmp_path)
    assert test_f in mtimes


def test_phase19_scheduler():
    code = """
set tracker to {"count": 0}
to increment_counter:
    increase tracker.count by 1

schedule every 0.01 seconds increment_counter
run scheduler for 0.1 seconds
"""
    ns = execute(code)
    assert ns["tracker"].count >= 1


def test_phase20_cryptography():
    code = """
set secret_msg to "TopSecretPayload"
hash text secret_msg with algorithm "sha256" into h256
hash text secret_msg with algorithm "md5" into hmd5
generate secure token of length 16 into token

encode text secret_msg as base64 into b64
decode base64 b64 into decoded

encrypt text secret_msg with secret "masterkey123" into cipher
decrypt text cipher with secret "masterkey123" into decrypted
"""
    ns = execute(code)
    assert len(ns["h256"]) == 64
    assert len(ns["hmd5"]) == 32
    assert len(ns["token"]) == 16
    assert ns["decoded"] == "TopSecretPayload"
    assert ns["decrypted"] == "TopSecretPayload"


def test_phase21_streaming_pipelines():
    code = """
to add_ten with x:
    return x + 10

to double_val with x:
    return x * 2

pipe 5 into add_ten, double_val into piped_result

set original_items to [1, 2, 3, 4, 5, 6, 7, 8]
take first 3 items from original_items into first_three
drop first 5 items from original_items into last_three
batch original_items by 3 into batched
"""
    ns = execute(code)
    assert ns["piped_result"] == 30
    assert ns["first_three"] == [1, 2, 3]
    assert ns["last_three"] == [6, 7, 8]
    assert ns["batched"] == [[1, 2, 3], [4, 5, 6], [7, 8]]


def test_phase22_binary_and_hex():
    code = """
convert number 255 to hex into hex_val
convert hex hex_val to number into num_val

pack numbers [100, 200, 300] as "int32" into bin_buffer
size of buffer bin_buffer in bytes into buf_len
unpack binary "int32" from buffer bin_buffer into unpacked_nums
"""
    ns = execute(code)
    assert ns["hex_val"] == "0xff"
    assert ns["num_val"] == 255
    assert ns["buf_len"] == 12  # 3 * 4 bytes
    assert ns["unpacked_nums"] == [100, 200, 300]


def test_phase23_config_manager(tmp_path):
    ini_path = tmp_path / "settings.ini"
    ini_path.write_text("""[database]
host = db.local
port = 5432
""", encoding="utf-8")

    code = f"""
load config from "{ini_path.as_posix()}" into app_cfg
get config "database.host" from app_cfg into host
get config "database.timeout" with default 30 from app_cfg into timeout

set config "api_key" to "secret_abc" in app_cfg
save config app_cfg to file "{tmp_path.as_posix()}/backup.json"
"""
    ns = execute(code)
    assert ns["host"] == "db.local"
    assert ns["timeout"] == 30
    assert (tmp_path / "backup.json").exists()


def test_phase24_benchmarking_and_profiler(tmp_path):
    sample = tmp_path / "bench_target.doom"
    sample.write_text("""
set x to 100
set y to 200
set z to x + y
""", encoding="utf-8")

    res = benchmark_script(sample, iterations=5)
    assert res["iterations"] == 5
    assert res["ops_per_sec"] > 0


def test_phase25_standalone_packager(tmp_path):
    sample = tmp_path / "app.doom"
    sample.write_text("""
set a to 10
set b to 20
say "Sum is:", a + b
""", encoding="utf-8")

    out_pyz = tmp_path / "app.pyz"
    packed = pack_script(sample, out_pyz)
    assert packed.exists()
    assert packed.stat().st_size > 0
