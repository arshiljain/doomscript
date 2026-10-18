"""
Tests for DoomScript Phases 26 through 100:
10 Unified Thematic Clusters:
- Cluster 1: Systems, OS, Processes & Signals (Phases 26-32)
- Cluster 2: Network Protocols & Web (Phases 33-40)
- Cluster 3: Data Engineering, Compression & Geolocation (Phases 41-48)
- Cluster 4: Mathematics, Linear Algebra, Statistics & Finance (Phases 49-56)
- Cluster 5: Reactive EventBus, Priority Queues, Circuit Breaker (Phases 57-64)
- Cluster 6: Modern Web, UI & Components, SVG Canvas (Phases 65-72)
- Cluster 7: AI Agents, RAG & Cognitive Loops (Phases 73-80)
- Cluster 8: Security, Identity, Auth & Compliance (Phases 81-88)
- Cluster 9: Cloud, Containers & Metrics (Phases 89-95)
- Cluster 10: Metaprogramming, FFI & Self-Hosting (Phases 96-100)
"""

import sys
import os
import textwrap
import pytest
from doomscript.compiler.engine import compile_to_ast, execute
from doomscript.grammar.phrases import normalize


def run(source: str, custom_globals: dict = None) -> dict:
    env = custom_globals if custom_globals is not None else {}
    norm = normalize(textwrap.dedent(source).strip())
    tree = compile_to_ast(norm)
    return execute(tree, custom_globals=env)


# ===========================================================================
# CLUSTER 1: SYSTEMS, OS, PROCESSES & SIGNALS (Phases 26-32)
# ===========================================================================

def test_cluster1_systems_and_processes(tmp_path):
    lock_file = str(tmp_path / "app").replace("\\", "/")
    
    code = f"""
    run command "python -c print(12345)" piped into res
    check if process "python" is running into is_py
    get system disk space into disk
    acquire file lock "{lock_file}" into lk
    release file lock lk
    """
    ns = run(code)
    assert "12345" in ns["res"].stdout
    assert ns["res"].exit_code == 0
    assert ns["res"].ok is True
    assert ns["is_py"] is True
    assert ns["disk"].total_gb > 0


# ===========================================================================
# CLUSTER 2: NETWORK PROTOCOLS & WEB (Phases 33-40)
# ===========================================================================

def test_cluster2_network_and_cookies():
    code = """
    resolve dns of "localhost" into ips
    ping host "localhost" into ping_res
    create cookie jar into jar
    set cookie "session" to "xyz987" in jar
    get cookie "session" from jar into sess
    get cookie "missing" with default "default_val" from jar into non_exist
    """
    ns = run(code)
    assert isinstance(ns["ips"], list)
    assert ns["sess"] == "xyz987"
    assert ns["non_exist"] == "default_val"


# ===========================================================================
# CLUSTER 3: DATA ENGINEERING & COMPRESSION (Phases 41-48)
# ===========================================================================

def test_cluster3_compression_checksums_and_geo(tmp_path):
    archive_path = str(tmp_path / "test_bundle.zip").replace("\\", "/")
    extract_dir = str(tmp_path / "extracted").replace("\\", "/")
    sample_file = tmp_path / "hello.txt"
    sample_file.write_text("DoomScript Archival Content", encoding="utf-8")
    sample_file_str = str(sample_file).replace("\\", "/")

    code = f"""
    compress text "English Programming Paradigm" with gzip into gz_data
    decompress gzip gz_data into gz_text
    
    compress text "High Density Stream" with bz2 into bz_data
    decompress bz2 bz_data into bz_text

    calculate crc32 of "DoomCitadel" into crc_val
    calculate adler32 of "DoomCitadel" into adler_val

    # Distance between London (51.5074, -0.1278) and Paris (48.8566, 2.3522)
    calculate geo distance between 51.5074, -0.1278 and 48.8566, 2.3522 into dist_km

    create zip archive "{archive_path}" from files ["{sample_file_str}"]
    extract zip archive "{archive_path}" into folder "{extract_dir}"
    """
    ns = run(code)
    assert ns["gz_text"] == "English Programming Paradigm"
    assert ns["bz_text"] == "High Density Stream"
    assert isinstance(ns["crc_val"], int)
    assert isinstance(ns["adler_val"], int)
    assert 300 < ns["dist_km"] < 400
    assert os.path.exists(os.path.join(extract_dir, "hello.txt"))


# ===========================================================================
# CLUSTER 4: MATHEMATICS, LINEAR ALGEBRA, STATISTICS & FINANCE (Phases 49-56)
# ===========================================================================

def test_cluster4_math_linear_algebra_and_finance():
    code = """
    # Linear Algebra
    vector [1, 2, 3] dot vector [4, 5, 6] into dot_res
    vector magnitude of [3, 4] into mag_res
    matrix [[1, 2], [3, 4]] multiply matrix [[2, 0], [1, 2]] into mat_res

    # Statistics
    set data to [2, 4, 4, 4, 5, 5, 7, 9]
    standard deviation of data into sd_val
    variance of data into var_val
    median of data into med_val

    # Financial
    compound interest on 1000 at 5% for 3 years into fv
    loan payment for principal 10000 rate 5% months 12 into pmt
    """
    ns = run(code)
    assert ns["dot_res"] == 32
    assert ns["mag_res"] == 5.0
    assert ns["mat_res"] == [[4, 4], [10, 8]]
    assert round(ns["med_val"], 1) == 4.5
    assert ns["fv"] > 1150
    assert 850 < ns["pmt"] < 860


# ===========================================================================
# CLUSTER 5: REACTIVE EVENTBUS, PRIORITY QUEUES, CIRCUIT BREAKER (Phases 57-64)
# ===========================================================================

def test_cluster5_events_queues_and_resiliency():
    code = """
    create event bus into bus
    set received to []
    to on_alert
        add "system_alarm" to received
    
    event_subscribe("alert", on_alert)
    publish event "alert" with data "critical"

    # Priority Queue
    create priority queue into pq
    enqueue task "low_task" with priority 10 into pq
    enqueue task "urgent_task" with priority 1 into pq
    dequeue next task from pq into first_task
    dequeue next task from pq into second_task

    # Circuit Breaker
    create circuit breaker named "api_service" into cb
    to failing_func
        return 1 / 0
    to success_func
        return 42
    
    call circuit breaker cb with success_func into cb_ok
    """
    ns = run(code)
    assert "system_alarm" in ns["received"]
    assert ns["first_task"] == "urgent_task"
    assert ns["second_task"] == "low_task"
    assert ns["cb_ok"] == 42
    assert ns["cb"].state == "CLOSED"


# ===========================================================================
# CLUSTER 6: MODERN WEB, UI & COMPONENTS, SVG CANVAS (Phases 65-72)
# ===========================================================================

def test_cluster6_svg_and_ui_diffing():
    code = """
    create svg circle at 50, 50 radius 25 fill "crimson" into c1
    create svg rect at 10, 10 width 80 height 20 fill "navy" into r1
    create svg canvas width 200 height 200 with elements [c1, r1] into canvas_xml

    set old_cfg to {"theme": "dark", "version": 1}
    set new_cfg to {"theme": "light", "version": 1, "fullscreen": true}
    diff records old_cfg and new_cfg into diff_res
    """
    ns = run(code)
    assert "<svg" in ns["canvas_xml"]
    assert "<circle" in ns["canvas_xml"]
    assert "<rect" in ns["canvas_xml"]
    diff_res = ns["diff_res"]
    assert diff_res
    assert "theme" in diff_res.changed
    assert "fullscreen" in diff_res.added


# ===========================================================================
# CLUSTER 7: AI AGENTS, RAG & COGNITIVE LOOPS (Phases 73-80)
# ===========================================================================

def test_cluster7_ai_agents_rag_and_memory():
    code = """
    create knowledge index into kb
    index document "doc1" text "DoomScript is an English-first language for everyday scripting" into kb
    index document "doc2" text "Python AST compiles directly to byte code and native executables" into kb
    search knowledge index kb for "English language" into matches

    cosine similarity of [1.0, 0.0] and [1.0, 0.0] into identical_sim
    cosine similarity of [1.0, 0.0] and [0.0, 1.0] into orthogonal_sim

    create conversation memory into mem
    remember in memory mem role "user" content "What is DoomScript?"
    remember in memory mem role "assistant" content "It is English-first code."
    get recall history from mem into chat_history
    """
    ns = run(code)
    assert len(ns["matches"]) > 0
    assert ns["matches"][0].id == "doc1"
    assert ns["identical_sim"] == 1.0
    assert ns["orthogonal_sim"] == 0.0
    assert len(ns["chat_history"]) == 2
    assert ns["chat_history"][0].role == "user"


# ===========================================================================
# CLUSTER 8: SECURITY, IDENTITY, AUTH & COMPLIANCE (Phases 81-88)
# ===========================================================================

def test_cluster8_security_auth_and_pii():
    code = """
    # JWT creation and validation
    set user_data to {"user_id": 42, "role": "admin"}
    create jwt with payload user_data and secret "my_citadel_key" into token
    verify jwt token with secret "my_citadel_key" into decoded

    # Password hashing (PBKDF2)
    secure hash password "DoomGuySlayer99!" into pwd_hash
    verify password "DoomGuySlayer99!" matches pwd_hash into is_valid
    verify password "wrong_password" matches pwd_hash into is_invalid

    # PII Masking
    set raw_text to "Contact agent at john.doe@cyber.org or call 555-123-4567 regarding SSN 000-12-3456"
    mask pii in text raw_text into sanitized
    """
    ns = run(code)
    assert ns["decoded"]["user_id"] == 42
    assert ns["decoded"]["role"] == "admin"
    assert ns["is_valid"] is True
    assert ns["is_invalid"] is False
    assert "[EMAIL_MASKED]" in ns["sanitized"]
    assert "[PHONE_MASKED]" in ns["sanitized"]
    assert "[SSN_MASKED]" in ns["sanitized"]


# ===========================================================================
# CLUSTER 9: CLOUD, CONTAINERS & METRICS (Phases 89-95)
# ===========================================================================

def test_cluster9_cloud_and_prometheus_metrics():
    code = """
    generate dockerfile for entrypoint "main.doom" into df
    
    increment metric "http_requests_total"
    increment metric "http_requests_total"
    set metric "system_health_ratio" to 99.8
    export prometheus metrics into prom_text
    """
    ns = run(code)
    assert "FROM python:3.11-slim" in ns["df"]
    assert "ENTRYPOINT" in ns["df"]
    assert "http_requests_total 2" in ns["prom_text"]
    assert "system_health_ratio 99.8" in ns["prom_text"]


# ===========================================================================
# CLUSTER 10: METAPROGRAMMING, FFI & SELF-HOSTING (Phases 96-100)
# ===========================================================================

def test_cluster10_metaprogramming_and_ffi():
    code = """
    set raw_source to "# Comment\\nset x to 10\\n# Another\\nsay x"
    minify doomscript raw_source into minified_src
    """
    ns = run(code)
    assert "#" not in ns["minified_src"]
    assert "set x to 10" in ns["minified_src"]
