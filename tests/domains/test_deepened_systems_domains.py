"""Comprehensive verification test suite for Deepened Systems, Cloud, DB, Simulation, and Research Domains."""

import os
import math
import zipfile
import pytest

from doomscript.domains.opt import (
    opt_simulated_annealing,
    opt_genetic_algorithm,
    opt_particle_swarm,
    opt_nelder_mead,
)
from doomscript.domains.sim import (
    sim_queue_system,
    CellularAutomaton,
    SpatialAgentSimulation,
)
from doomscript.domains.geo import (
    geo_vincenty_distance,
    geo_point_in_polygon,
    geo_polygon_area_sq_km,
    geo_geohash_encode,
    geo_geohash_decode,
    SpatialRTree,
    point,
    polygon,
)
from doomscript.domains.cloud import (
    CloudBucket,
    CloudStorageManager,
    IAMPolicyEngine,
    CloudCostCalculator,
)
from doomscript.domains.db import (
    SQLQueryBuilder,
    InMemoryRelationalDB,
    MigrationManager,
    db_connect,
)
from doomscript.domains.net import (
    HTTP2FrameParser,
    PacketDissector,
    WebSocketCodec,
)
from doomscript.domains.agent import (
    ToolHarness,
    AgentMemoryBuffer,
    ReActAgent,
)
from doomscript.domains.web import (
    HTMLDOMSelector,
    web_extract_metadata,
    RobotsTxtParser,
)
from doomscript.domains.office import (
    PureXlsxWorkbook,
    PureDocxDocument,
    PurePptxPresentation,
)
from doomscript.domains.research import (
    BibTeXEngine,
    CitationNetwork,
    AcademicLiteratureSynthesizer,
)


# ==============================================================================
# 1. OPT DOMAIN DEEPENING TESTS
# ==============================================================================

def test_opt_simulated_annealing():
    # Sphere function with minimum at [3.0, -2.0]
    def sphere(x):
        return (x[0] - 3.0) ** 2 + (x[1] + 2.0) ** 2

    res = opt_simulated_annealing(
        sphere,
        initial_state=[0.0, 0.0],
        bounds=[(-10.0, 10.0), (-10.0, 10.0)],
        temp_max=50.0,
        cooling_rate=0.9,
        steps_per_temp=10,
        seed=42,
    )
    assert "best_state" in res
    assert "best_cost" in res
    # Should get reasonably close to minimum
    assert res["best_cost"] < 2.0
    assert abs(res["best_state"][0] - 3.0) < 1.5
    assert abs(res["best_state"][1] - (-2.0)) < 1.5


def test_opt_genetic_algorithm():
    def rosenbrock_slice(x):
        return 100 * (x[1] - x[0]**2)**2 + (1 - x[0])**2

    res = opt_genetic_algorithm(
        rosenbrock_slice,
        bounds=[(-2.0, 2.0), (-1.0, 3.0)],
        population_size=30,
        generations=25,
        seed=42,
    )
    assert "best_state" in res
    assert "history" in res
    # Cost should decrease over generations
    assert res["history"][-1] <= res["history"][0]


def test_opt_particle_swarm():
    def simple_loss(pos):
        return (pos[0] - 1.5)**2 + (pos[1] - 2.5)**2

    res = opt_particle_swarm(
        simple_loss,
        bounds=[(-5.0, 5.0), (-5.0, 5.0)],
        n_particles=25,
        iterations=30,
        seed=42,
    )
    assert "best_state" in res
    assert res["best_cost"] < 0.5
    assert abs(res["best_state"][0] - 1.5) < 0.5
    assert abs(res["best_state"][1] - 2.5) < 0.5


def test_opt_nelder_mead():
    def quad(x):
        return (x[0] - 4.0)**2 + (x[1] - 1.0)**2

    res = opt_nelder_mead(quad, initial_point=[0.0, 0.0], max_iter=80)
    assert "best_state" in res
    assert res["best_cost"] < 1e-3
    assert abs(res["best_state"][0] - 4.0) < 0.1
    assert abs(res["best_state"][1] - 1.0) < 0.1


# ==============================================================================
# 2. SIM DOMAIN DEEPENING TESTS
# ==============================================================================

def test_sim_queue_system():
    # M/M/2 queue
    q = sim_queue_system(arrival_rate=2.0, service_rate=1.5, servers=2, max_time=100.0, seed=42)
    assert q["servers"] == 2
    assert q["total_arrivals"] > 0
    assert q["served_count"] > 0
    assert q["server_utilization"] > 0.0
    assert "avg_wait_time" in q


def test_cellular_automaton_blinker():
    # Conway's Game of Life: Blinker oscillator (period 2)
    ca = CellularAutomaton(width=5, height=5, rule="B3/S23")
    # Horizontal line of 3 cells in middle row
    ca.set_cell(1, 2, 1)
    ca.set_cell(2, 2, 1)
    ca.set_cell(3, 2, 1)
    assert ca.population == 3

    # Step 1: should become vertical line
    ca.step()
    grid = ca.to_list()
    assert ca.population == 3
    assert grid[1][2] == 1
    assert grid[2][2] == 1
    assert grid[3][2] == 1
    assert grid[2][1] == 0
    assert grid[2][3] == 0

    # Step 2: should oscillate back to horizontal line
    ca.step()
    grid2 = ca.to_list()
    assert ca.population == 3
    assert grid2[2][1] == 1
    assert grid2[2][2] == 1
    assert grid2[2][3] == 1


def test_spatial_agent_simulation():
    sim = SpatialAgentSimulation(width=50.0, height=50.0, n_agents=15, seed=42)
    sim.run(steps=5, dt=0.5)
    positions = sim.positions()
    assert len(positions) == 15
    for x, y in positions:
        assert 0.0 <= x <= 50.0
        assert 0.0 <= y <= 50.0


# ==============================================================================
# 3. GEO DOMAIN DEEPENING TESTS
# ==============================================================================

def test_geo_vincenty_geodesic():
    # London (51.5074, -0.1278) to Paris (48.8566, 2.3522)
    london = (51.5074, -0.1278)
    paris = (48.8566, 2.3522)
    dist = geo_vincenty_distance(london, paris)
    # Geodesic distance between London and Paris is approx 343 km
    assert 340.0 <= dist <= 346.0


def test_geo_point_in_polygon():
    # Square polygon from (0,0) to (10,10)
    square = [
        [0.0, 0.0],
        [10.0, 0.0],
        [10.0, 10.0],
        [0.0, 10.0],
        [0.0, 0.0],
    ]
    assert geo_point_in_polygon((5.0, 5.0), square) is True
    assert geo_point_in_polygon((15.0, 5.0), square) is False
    assert geo_point_in_polygon((-1.0, 5.0), square) is False


def test_geo_polygon_area():
    # 1 degree x 1 degree rectangle near equator
    rect = [
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0],
        [0.0, 0.0],
    ]
    area = geo_polygon_area_sq_km(rect)
    # Approx 111 km * 111 km ≈ 12,321 sq km
    assert 12000.0 <= area <= 12600.0


def test_geo_geohash_encode_decode():
    lat, lon = 37.7749, -122.4194  # San Francisco
    h = geo_geohash_encode(lat, lon, precision=7)
    assert isinstance(h, str)
    assert len(h) == 7

    decoded = geo_geohash_decode(h)
    assert abs(decoded["lat"] - lat) < 0.01
    assert abs(decoded["lon"] - lon) < 0.01
    assert "bounds" in decoded


def test_spatial_rtree_queries():
    tree = SpatialRTree()
    tree.insert(0.0, 0.0, 5.0, 5.0, "box1")
    tree.insert(10.0, 10.0, 15.0, 15.0, "box2")
    tree.insert(4.0, 4.0, 8.0, 8.0, "box3")

    # Query covering box1 and box3
    res1 = tree.query(2.0, 2.0, 6.0, 6.0)
    assert "box1" in res1
    assert "box3" in res1
    assert "box2" not in res1

    # Query disjoint from all
    res2 = tree.query(50.0, 50.0, 60.0, 60.0)
    assert len(res2) == 0


# ==============================================================================
# 4. CLOUD DOMAIN DEEPENING TESTS
# ==============================================================================

def test_cloud_multipart_storage(tmp_path):
    bucket = CloudBucket("test-multi-bucket")
    mgr = CloudStorageManager(bucket)

    upload_id = mgr.initiate_multipart_upload("large_dataset.csv")
    assert upload_id is not None

    part1 = mgr.upload_part(upload_id, 1, "id,name,val\n1,alice,100\n")
    part2 = mgr.upload_part(upload_id, 2, "2,bob,200\n3,carol,300\n")

    assert part1["part_number"] == 1
    assert part2["part_number"] == 2

    completed = mgr.complete_multipart_upload(upload_id)
    assert completed["key"] == "large_dataset.csv"
    assert completed["total_parts"] == 2
    assert completed["total_bytes"] > 0
    assert "etag" in completed

    versions = mgr.list_versions("large_dataset.csv")
    assert len(versions) == 1
    assert versions[0]["version_id"] == "v1"


def test_iam_policy_engine():
    engine = IAMPolicyEngine()
    engine.add_policy({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": ["arn:aws:s3:::my-bucket/*"],
            },
            {
                "Effect": "Deny",
                "Action": ["s3:GetObject"],
                "Resource": ["arn:aws:s3:::my-bucket/secret/*"],
            },
        ],
    })

    # Public doc -> Allow
    eval1 = engine.evaluate("s3:GetObject", "arn:aws:s3:::my-bucket/public/readme.txt")
    assert eval1["allowed"] is True

    # Secret doc -> Deny
    eval2 = engine.evaluate("s3:GetObject", "arn:aws:s3:::my-bucket/secret/keys.pem")
    assert eval2["allowed"] is False
    assert eval2["decision"] == "Deny"

    # Unauthorized action -> ImplicitDeny
    eval3 = engine.evaluate("s3:DeleteObject", "arn:aws:s3:::my-bucket/public/readme.txt")
    assert eval3["allowed"] is False


def test_cloud_cost_calculator():
    calc = CloudCostCalculator()
    calc.add_instance("medium", count=2, hours_per_month=730.0)
    calc.add_storage(100.0, storage_class="STANDARD")
    calc.add_egress(50.0)

    est = calc.estimate_monthly()
    assert est["compute_cost"] > 0.0
    assert est["storage_cost"] > 0.0
    assert est["egress_cost"] > 0.0
    assert est["total_monthly_estimate"] > 50.0


# ==============================================================================
# 5. DB DOMAIN DEEPENING TESTS
# ==============================================================================

def test_sql_query_builder():
    builder = SQLQueryBuilder("users")
    sql, params = (
        builder
        .select("id", "name", "email")
        .join("orders", "users.id = orders.user_id")
        .where("users.status", "=", "active")
        .where("orders.amount", ">", 50.0)
        .order_by("users.name")
        .limit(10)
        .build()
    )
    assert "SELECT id, name, email FROM users" in sql
    assert "INNER JOIN orders ON users.id = orders.user_id" in sql
    assert "WHERE users.status = ? AND orders.amount > ?" in sql
    assert "ORDER BY users.name ASC LIMIT ?" in sql
    assert params == ["active", 50.0, 10]


def test_in_memory_relational_db():
    db = InMemoryRelationalDB()
    db.create_table("employees")
    db.insert("employees", {"id": 1, "name": "Alice", "dept": "Engineering", "salary": 120000})
    db.insert("employees", {"id": 2, "name": "Bob", "dept": "Marketing", "salary": 80000})
    db.insert("employees", {"id": 3, "name": "Carol", "dept": "Engineering", "salary": 140000})

    # Query with filter
    engs = db.query("employees", where_filter=lambda r: r["dept"] == "Engineering")
    assert len(engs) == 2

    # Aggregations
    sums = db.aggregate("employees", group_by_col="dept", agg_col="salary", agg_func="sum")
    assert sums["Engineering"] == 260000.0
    assert sums["Marketing"] == 80000.0


def test_schema_migration_manager():
    conn = db_connect(":memory:")
    mgr = MigrationManager(conn)
    assert mgr.current_version() == 0

    mgr.add_migration(1, "create_users", "CREATE TABLE users (id INT, name TEXT);", "DROP TABLE users;")
    mgr.add_migration(2, "add_email", "ALTER TABLE users ADD COLUMN email TEXT;", "")

    applied = mgr.migrate_up()
    assert applied == 2
    assert mgr.current_version() == 2

    # Check table exists and has column
    cur = conn.execute("PRAGMA table_info(users)")
    cols = [r[1] for r in cur.fetchall()]
    assert "id" in cols
    assert "email" in cols


# ==============================================================================
# 6. NET DOMAIN DEEPENING TESTS
# ==============================================================================

def test_http2_frame_parser():
    payload = b"PINGPAYLOAD"
    # Serialize PING frame (type 0x6, stream_id 0)
    frame_bytes = HTTP2FrameParser.serialize_frame("PING", flags=0x1, stream_id=0, payload=payload)
    assert len(frame_bytes) == 9 + len(payload)

    parsed = HTTP2FrameParser.parse_frame(frame_bytes)
    assert parsed["length"] == len(payload)
    assert parsed["type"] == "PING"
    assert parsed["flags"] == 0x1
    assert parsed["stream_id"] == 0
    assert parsed["payload"] == payload


def test_packet_dissector_ipv4():
    # Construct synthetic 20-byte IPv4 packet
    # Version=4, IHL=5 (0x45), TOS=0, Length=20, Ident=1, Flags=0, TTL=64, Proto=6 (TCP), Checksum=0
    # Src=192.168.1.10, Dst=10.0.0.1
    raw = bytearray([
        0x45, 0x00, 0x00, 0x14,
        0x00, 0x01, 0x00, 0x00,
        0x40, 0x06, 0x00, 0x00,
        192, 168, 1, 10,
        10, 0, 0, 1,
    ])
    checksum = PacketDissector.calculate_ip_checksum(bytes(raw))
    raw[10] = (checksum >> 8) & 0xFF
    raw[11] = checksum & 0xFF

    dissected = PacketDissector.dissect_ipv4_header(bytes(raw))
    assert dissected["version"] == 4
    assert dissected["ihl"] == 20
    assert dissected["ttl"] == 64
    assert dissected["protocol_name"] == "TCP"
    assert dissected["src_ip"] == "192.168.1.10"
    assert dissected["dst_ip"] == "10.0.0.1"


def test_websocket_codec_masking():
    msg = "Hello DoomScript WebSockets!"
    encoded = WebSocketCodec.encode_frame(msg, opcode="TEXT", masked=True, mask_key=b"\x12\x34\x56\x78")

    decoded = WebSocketCodec.decode_frame(encoded)
    assert decoded["fin"] is True
    assert decoded["opcode"] == "TEXT"
    assert decoded["masked"] is True
    assert decoded["text"] == msg


# ==============================================================================
# 7. AGENT DOMAIN DEEPENING TESTS
# ==============================================================================

def test_tool_harness():
    harness = ToolHarness()

    def add(a: int, b: int) -> int:
        return a + b

    harness.register("add", add, description="Add two integers", param_schema={"a": int, "b": int})
    res = harness.execute("add", a=10, b=25)
    assert res == 35

    defs = harness.get_tool_definitions()
    assert len(defs) == 1
    assert defs[0]["name"] == "add"


def test_agent_memory_buffer_compaction():
    mem = AgentMemoryBuffer(max_messages=6, max_chars=1000)
    for i in range(10):
        mem.add("user" if i % 2 == 0 else "assistant", f"Message number {i} discussing topic {i}")

    # Messages should have been compacted
    assert len(mem.messages) <= 6
    assert mem.compacted_summary != ""
    ctx = mem.get_context_for_prompt()
    assert "Previous Context Summary" in ctx


def test_react_agent_execution_loop():
    harness = ToolHarness()
    harness.register("calculator", lambda expr: 42, description="Evaluate math expression")

    agent = ReActAgent("MathSolver", harness=harness, max_iterations=3)

    def scripted_policy(goal, trajectory):
        if len(trajectory) == 0:
            return {"thought": "I need to calculate answer", "action": "calculator", "action_input": {"expr": "6*7"}}
        else:
            return {"thought": "I have the calculation result", "action": None, "final_answer": "42"}

    res = agent.solve("Calculate 6 times 7", reasoning_policy=scripted_policy)
    assert res["status"] == "success"
    assert res["final_answer"] == "42"
    assert len(res["trajectory"]) == 2


# ==============================================================================
# 8. WEB DOMAIN DEEPENING TESTS
# ==============================================================================

def test_html_dom_css_selectors():
    html = """
    <div id="container" class="main-wrap">
        <h1 class="header-title">Welcome</h1>
        <ul class="nav-list">
            <li class="item active"><a href="/home">Home</a></li>
            <li class="item"><a href="/about">About</a></li>
        </ul>
        <div data-role="panel">Secret Panel Content</div>
    </div>
    """
    dom = HTMLDOMSelector(html)

    # By ID
    container = dom.query("#container")
    assert container is not None
    assert container.tag == "div"

    # By class
    title = dom.query(".header-title")
    assert title is not None
    assert "Welcome" in title.inner_text

    # By descendant
    nav_links = dom.query_all("ul.nav-list a")
    assert len(nav_links) == 2
    assert nav_links[0].inner_text == "Home"

    # By attribute
    panel = dom.query("[data-role=panel]")
    assert panel is not None
    assert "Secret Panel Content" in panel.inner_text


def test_web_metadata_extraction():
    html = """
    <html>
      <head>
        <title>Article Title</title>
        <meta name="description" content="A comprehensive guide to DoomScript.">
        <meta property="og:title" content="OpenGraph Guide">
        <meta property="og:image" content="https://example.com/thumb.png">
        <script type="application/ld+json">
          {"@context": "https://schema.org", "@type": "Article", "headline": "DoomScript 101"}
        </script>
      </head>
      <body></body>
    </html>
    """
    meta = web_extract_metadata(html)
    assert meta["title"] == "Article Title"
    assert meta["description"] == "A comprehensive guide to DoomScript."
    assert meta["open_graph"]["title"] == "OpenGraph Guide"
    assert meta["open_graph"]["image"] == "https://example.com/thumb.png"
    assert len(meta["json_ld"]) == 1
    assert meta["json_ld"][0]["headline"] == "DoomScript 101"


def test_robots_txt_parser():
    robots = """
    User-agent: Googlebot
    Disallow: /admin/
    Allow: /admin/public/

    User-agent: *
    Disallow: /private/
    Disallow: /tmp/
    """
    parser = RobotsTxtParser(robots)
    assert parser.is_allowed("/public/page.html") is True
    assert parser.is_allowed("/private/data.json") is False
    assert parser.is_allowed("/tmp/file.txt") is False
    assert parser.is_allowed("/admin/public/index.html", user_agent="Googlebot") is True
    assert parser.is_allowed("/admin/secret", user_agent="Googlebot") is False


# ==============================================================================
# 9. OFFICE DOMAIN DEEPENING TESTS
# ==============================================================================

def test_pure_xlsx_workbook(tmp_path):
    wb = PureXlsxWorkbook()
    wb.append_row("Sheet1", ["Item", "Quantity", "Price", "Total"])
    wb.append_row("Sheet1", ["Widgets", 10, 5.5, "=B2*C2"])
    wb.append_row("Sheet1", ["Gadgets", 5, 20.0, "=B3*C3"])

    target_xlsx = str(tmp_path / "test_report.xlsx")
    saved = wb.save(target_xlsx)
    assert os.path.exists(saved)
    assert zipfile.is_zipfile(saved)

    with zipfile.ZipFile(saved, "r") as zf:
        namelist = zf.namelist()
        assert "xl/workbook.xml" in namelist
        assert "xl/worksheets/sheet1.xml" in namelist
        content = zf.read("xl/worksheets/sheet1.xml").decode("utf-8")
        assert "Widgets" in content
        assert "Total" in content
        assert "<f>B2*C2</f>" in content


def test_pure_docx_document(tmp_path):
    doc = PureDocxDocument()
    doc.add_heading("DoomScript Executive Report", level=1)
    doc.add_paragraph("This is an automated report generated with zero external dependencies.", bold=True)
    doc.add_paragraph("All algorithms executed in pure Python.", italic=True)

    target_docx = str(tmp_path / "report.docx")
    saved = doc.save(target_docx)
    assert os.path.exists(saved)
    assert zipfile.is_zipfile(saved)

    with zipfile.ZipFile(saved, "r") as zf:
        doc_xml = zf.read("word/document.xml").decode("utf-8")
        assert "DoomScript Executive Report" in doc_xml
        assert "<w:b/>" in doc_xml
        assert "<w:i/>" in doc_xml


def test_pure_pptx_presentation(tmp_path):
    pptx = PurePptxPresentation()
    pptx.add_slide("Introduction to DoomScript", "The Universal Spoken DSL")
    pptx.add_slide("Key Architecture", "Zero Dependencies & High Performance")

    target_pptx = str(tmp_path / "presentation.pptx")
    saved = pptx.save(target_pptx)
    assert os.path.exists(saved)
    assert zipfile.is_zipfile(saved)


# ==============================================================================
# 10. RESEARCH DOMAIN DEEPENING TESTS
# ==============================================================================

def test_bibtex_parser_and_formatter():
    bib = """
    @article{vaswani2017attention,
      author = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki},
      title = {Attention Is All You Need},
      journal = {Advances in Neural Information Processing Systems},
      volume = {30},
      year = {2017}
    }
    """
    entries = BibTeXEngine.parse(bib)
    assert len(entries) == 1
    e = entries[0]
    assert e["cite_key"] == "vaswani2017attention"
    assert e["title"] == "Attention Is All You Need"
    assert e["year"] == "2017"

    apa = BibTeXEngine.format_citation(e, style="apa")
    assert "Vaswani, Ashish and Shazeer, Noam and Parmar, Niki (2017)." in apa
    assert "Attention Is All You Need." in apa

    ieee = BibTeXEngine.format_citation(e, style="ieee")
    assert '"Attention Is All You Need,"' in ieee


def test_citation_network_h_index_and_pagerank():
    net = CitationNetwork()
    net.add_paper("p1", title="Foundations of AI", author="Turing", year=1950)
    net.add_paper("p2", title="Neural Nets", author="Hinton", year=1986)
    net.add_paper("p3", title="Deep Learning", author="Hinton", year=2012)
    net.add_paper("p4", title="Dropout", author="Hinton", year=2014)

    # Citations
    net.add_citation("p3", "p2")
    net.add_citation("p4", "p2")
    net.add_citation("p4", "p3")
    net.add_citation("p2", "p1")

    # Hinton has p2 (cited 2 times), p3 (cited 1 time), p4 (cited 0 times)
    # Sorted citations: [2, 1, 0] -> at rank 1, c=2>=1; at rank 2, c=1<2. h=1.
    h = net.calculate_h_index("Hinton")
    assert h >= 1

    pr = net.compute_pagerank()
    assert len(pr) == 4
    # p1 and p2 receive most citations
    assert pr["p1"] > 0.0
    assert pr["p2"] > 0.0


def test_academic_literature_synthesizer():
    syn = AcademicLiteratureSynthesizer()
    syn.add_document("doc1", "Quantum Teleportation", "Quantum entanglement enables information transfer across states.")
    syn.add_document("doc2", "Deep Residual Networks", "Residual learning framework eases the training of very deep networks.")
    syn.add_document("doc3", "Transformers in NLP", "Self-attention mechanism replaces recurrent layers in sequence modeling.")

    res = syn.search_by_relevance("quantum entanglement states")
    assert len(res) > 0
    assert res[0]["id"] == "doc1"
