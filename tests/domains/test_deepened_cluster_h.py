"""Comprehensive tests for Deepened Cluster H domains:
- web: CSSSelectorEngine, RFC6265CookieJar
- db: WALCrashRecovery, CostBasedQueryOptimizer, SnapshotIsolationMVCC
- neuro: TsodyksMarkramSynapse, FitzHughNagumoNeuron, WinnerTakeAllNetwork
- geo: DelaunayTriangulator, WebMercatorProjection, IsochroneContour
"""

import math
from doomscript.domains.web.runtime import (
    DOMElement,
    CSSSelectorEngine,
    RFC6265CookieJar,
)
from doomscript.domains.db.runtime import (
    WALCrashRecovery,
    CostBasedQueryOptimizer,
    SnapshotIsolationMVCC,
)
from doomscript.domains.neuro.runtime import (
    TsodyksMarkramSynapse,
    FitzHughNagumoNeuron,
    WinnerTakeAllNetwork,
)
from doomscript.domains.geo.runtime import (
    DelaunayTriangulator,
    WebMercatorProjection,
    IsochroneContour,
)
from doomscript.runtime import (
    web_css_select,
    web_cookie_jar,
    db_wal_create,
    db_query_optimizer,
    db_mvcc_create,
    neuro_tsodyks_markram,
    neuro_fitzhugh_nagumo,
    neuro_wta_network,
    geo_delaunay_triangulate,
    geo_voronoi_diagram,
    geo_web_mercator_forward,
    geo_web_mercator_inverse,
    geo_compute_isochrone,
)


# --- 1. Web Scraping & CSS Selector Tests ---

def test_css_selector_engine():
    html = """
    <div id="main" class="container content">
        <h1 class="title">DoomScript Documentation</h1>
        <div class="section" data-role="chapter">
            <p class="lead">Introduction text.</p>
            <p>Second paragraph with <a href="/docs" class="link">link</a>.</p>
            <ul id="items">
                <li class="item active">Item 1</li>
                <li class="item">Item 2</li>
            </ul>
        </div>
        <div class="footer">
            <input type="text" name="query" value="search">
        </div>
    </div>
    """
    root = CSSSelectorEngine.parse_html(html)

    # Tag selector
    p_tags = CSSSelectorEngine.select(root, "p")
    assert len(p_tags) == 2
    assert "Introduction text." in p_tags[0].text

    # ID selector
    main_div = CSSSelectorEngine.select(root, "#main")
    assert len(main_div) == 1
    assert main_div[0].attrs["id"] == "main"

    # Class selector
    lead = CSSSelectorEngine.select(root, ".lead")
    assert len(lead) == 1
    assert "Introduction text." in lead[0].text

    # Child combinator
    items = CSSSelectorEngine.select(root, "ul#items > li")
    assert len(items) == 2

    # Descendant combinator
    links = CSSSelectorEngine.select(root, "#main a.link")
    assert len(links) == 1
    assert links[0].attrs.get("href") == "/docs"

    # Attribute selector
    inputs = CSSSelectorEngine.select(root, "input[type=text]")
    assert len(inputs) == 1
    assert inputs[0].attrs.get("name") == "query"


def test_rfc6265_cookie_jar():
    jar = RFC6265CookieJar()

    # Set session cookie
    jar.set_cookie("session_id=xyz123; Path=/; Domain=example.com; HttpOnly", "https://example.com/login")
    # Set secure cookie
    jar.set_cookie("auth_token=secret789; Path=/api; Domain=api.example.com; Secure", "https://api.example.com/api/v1")
    # Set expired cookie (Max-Age=0)
    jar.set_cookie("stale=old; Path=/; Max-Age=0", "https://example.com", current_time=1000.0)

    # Query for example.com/home (non-secure)
    header1 = jar.get_cookie_header("http://example.com/home", is_secure=False, current_time=1000.0)
    assert "session_id=xyz123" in header1
    assert "stale" not in header1
    assert "auth_token" not in header1

    # Query for api.example.com/api/data (secure)
    header2 = jar.get_cookie_header("https://api.example.com/api/data", is_secure=True, current_time=1000.0)
    assert "auth_token=secret789" in header2
    assert "session_id=xyz123" in header2  # Subdomain matches parent domain cookie


# --- 2. Database & Systems Tests ---

def test_wal_crash_recovery():
    wal = WALCrashRecovery()

    # Tx 1 commits
    wal.begin_tx(1)
    wal.write_update(1, page_id=10, old_val="init_10", new_val="val_tx1")
    wal.commit_tx(1)

    # Flush page 10 to disk
    wal.flush_page_to_disk(10)

    # Tx 2 writes update but crashes before commit
    wal.begin_tx(2)
    wal.write_update(2, page_id=10, old_val="val_tx1", new_val="corrupt_val")
    wal.write_update(2, page_id=20, old_val="init_20", new_val="uncommitted_20")

    # Simulate sudden crash
    wal.simulate_crash()
    # At crash: page 10 has disk state 'val_tx1', page 20 is not on disk

    # Run ARIES recovery
    rec = wal.recover()
    assert 2 in rec["uncommitted_txs"]
    assert 1 not in rec["uncommitted_txs"]
    assert rec["redone_operations"] >= 1
    assert rec["undone_operations"] >= 1

    # Page 10 must be restored to committed value 'val_tx1'
    assert rec["recovered_pages"][10] == "val_tx1"


def test_cost_based_query_optimizer():
    cbo = CostBasedQueryOptimizer()
    cbo.register_table(
        "customers",
        num_rows=100_000,
        num_pages=2_000,
        indexes={
            "customer_id": {"distinct_vals": 100_000, "idx_pages": 10},
            "status": {"distinct_vals": 4, "idx_pages": 4},
        },
    )

    # Highly selective predicate on indexed column -> INDEX_SCAN
    plan_eq = cbo.optimize_scan("customers", "customer_id", "=", 42)
    assert plan_eq["chosen_plan"] == "INDEX_SCAN"
    assert plan_eq["estimated_cost"] < plan_eq["seq_scan_cost"]

    # Low selectivity predicate on non-selective index (1/4 of table = 25,000 rows) -> SEQ_SCAN
    plan_status = cbo.optimize_scan("customers", "status", "=", "ACTIVE")
    assert plan_status["chosen_plan"] == "SEQ_SCAN"


def test_snapshot_isolation_mvcc():
    mvcc = SnapshotIsolationMVCC()

    # Initial state
    tx0 = mvcc.begin()
    mvcc.write(tx0, "acc_alice", 100)
    mvcc.commit(tx0)

    # Concurrent transactions Tx1 and Tx2
    tx1 = mvcc.begin()
    tx2 = mvcc.begin()

    # Both observe Alice balance = 100
    assert mvcc.read(tx1, "acc_alice") == 100
    assert mvcc.read(tx2, "acc_alice") == 100

    # Tx2 updates Alice and commits
    mvcc.write(tx2, "acc_alice", 150)
    ok2 = mvcc.commit(tx2)
    assert ok2 is True

    # Tx1 still reads its original snapshot value (repeatable read)
    assert mvcc.read(tx1, "acc_alice") == 100

    # Tx1 attempts to write Alice and commit -> should abort on write-write conflict!
    mvcc.write(tx1, "acc_alice", 110)
    ok1 = mvcc.commit(tx1)
    assert ok1 is False  # Aborted


# --- 3. Computational Neuroscience Tests ---

def test_tsodyks_markram_synapse():
    # Depressing synapse (high U, long recovery)
    syn = TsodyksMarkramSynapse(U=0.5, tau_rec=500.0, tau_fac=10.0, A=2.0)
    train = [1, 0, 0, 1, 0, 0, 1]  # 3 pulses spaced by 2ms

    res = syn.simulate_train(train, dt_ms=1.0)
    assert len(res["psc_trace"]) == 7
    # First pulse should have highest response due to depression
    spikes_psc = [res["psc_trace"][0], res["psc_trace"][3], res["psc_trace"][6]]
    assert spikes_psc[0] > spikes_psc[1] > spikes_psc[2]
    assert res["peak_psc"] > 0


def test_fitzhugh_nagumo_neuron():
    neuron = FitzHughNagumoNeuron(a=0.7, b=0.8, tau=12.5)

    # Subthreshold current vs supra-threshold current
    trace = [0.5] * 200  # sustained depolarizing current
    res = neuron.simulate(trace, dt=0.2)
    assert res["total_spikes"] > 0
    assert len(res["voltages"]) == 200


def test_winner_take_all_network():
    # 4 neurons with inputs, neuron 1 receives strongest stimulus
    wta = WinnerTakeAllNetwork(num_neurons=4, beta=0.8, tau=5.0)
    inputs = [1.0, 6.0, 2.0, 0.5]

    res = wta.run_until_convergence(inputs, max_steps=50)
    assert res["winner_index"] == 1
    # Winner unit has dominant activity
    assert res["winner_activity"] > max(
        res["final_activities"][0],
        res["final_activities"][2],
        res["final_activities"][3],
    )


# --- 4. Geospatial Systems Tests ---

def test_delaunay_triangulator():
    points = [
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0),
    ]

    triangles = DelaunayTriangulator.triangulate(points)
    # A 4-point unit square triangulates into 2 triangles
    assert len(triangles) == 2

    # Voronoi dual edges
    edges = DelaunayTriangulator.voronoi_diagram(points)
    assert len(edges) >= 1


def test_web_mercator_projection():
    # San Francisco lat/lon
    lat, lon = 37.7749, -122.4194
    x, y = WebMercatorProjection.lat_lon_to_xy(lat, lon)
    assert -14_000_000 < x < -13_000_000
    assert 4_000_000 < y < 5_000_000

    # Invert back
    recovered_lat, recovered_lon = WebMercatorProjection.xy_to_lat_lon(x, y)
    assert abs(recovered_lat - lat) < 1e-4
    assert abs(recovered_lon - lon) < 1e-4

    # Tile coordinate at zoom 10
    tx, ty = WebMercatorProjection.lat_lon_to_tile(lat, lon, zoom=10)
    bbox = WebMercatorProjection.tile_to_bbox(tx, ty, zoom=10)
    assert bbox["min_lat"] <= lat <= bbox["max_lat"]
    assert bbox["min_lon"] <= lon <= bbox["max_lon"]

    # Quadkey
    qk = WebMercatorProjection.tile_to_quadkey(tx, ty, zoom=10)
    assert len(qk) == 10
    assert all(c in "0123" for c in qk)


def test_isochrone_contour():
    nodes = {
        "A": (37.77, -122.41),  # Origin
        "B": (37.78, -122.41),  # 1 km north
        "C": (37.77, -122.40),  # 1 km east
        "D": (37.85, -122.41),  # 10 km north
    }
    edges = [
        {"u": "A", "v": "B", "distance_km": 1.0, "speed_kmh": 60.0},  # 1 min
        {"u": "A", "v": "C", "distance_km": 1.0, "speed_kmh": 30.0},  # 2 min
        {"u": "B", "v": "D", "distance_km": 10.0, "speed_kmh": 60.0}, # 10 min
    ]

    # Reachable within 3 minutes -> A, B, C (not D which needs 11 min)
    iso3 = IsochroneContour.compute_isochrone("A", nodes, edges, max_time_minutes=3.0)
    assert iso3["reachable_nodes_count"] == 3
    assert "A" in iso3["reachable_nodes"]
    assert "B" in iso3["reachable_nodes"]
    assert "C" in iso3["reachable_nodes"]
    assert "D" not in iso3["reachable_nodes"]
    assert len(iso3["contour_polygon"]) >= 3

    # Reachable within 15 minutes -> all 4 nodes
    iso15 = IsochroneContour.compute_isochrone("A", nodes, edges, max_time_minutes=15.0)
    assert iso15["reachable_nodes_count"] == 4
    assert "D" in iso15["reachable_nodes"]
