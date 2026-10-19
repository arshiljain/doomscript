"""End-to-End Cross-Domain Integration Tests.

Validates that multiple domain packs (net, data, db, ml, sim, dsa, viz) can seamlessly
interoperate within a single DoomScript program, passing data across domain boundaries
and compiling/exporting cleanly to native Python AST.
"""

import http.server
import json
import socketserver
import threading
import pytest
from doomscript.compiler.engine import execute, export_to_python


class MultiDomainAPIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/telemetry":
            data = [
                {"id": 1, "feature1": 10.0, "feature2": 2.0, "score": 25.0},
                {"id": 2, "feature1": 20.0, "feature2": 4.0, "score": 45.0},
                {"id": 3, "feature1": 30.0, "feature2": 6.0, "score": 65.0},
                {"id": 4, "feature1": 40.0, "feature2": 8.0, "score": 85.0},
                {"id": 5, "feature1": 50.0, "feature2": 10.0, "score": 105.0},
                {"id": 5, "feature1": 50.0, "feature2": 10.0, "score": 105.0},  # duplicate
            ]
            payload = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


@pytest.fixture(scope="module")
def api_server():
    server = socketserver.TCPServer(("127.0.0.1", 0), MultiDomainAPIHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


def test_cross_domain_pipeline_execution(api_server):
    """Executes a full cross-domain DoomScript program chaining 6 domains."""
    source = f"""
use net
use data
use db
use ml
use sim
use dsa

# 1. Fetch raw data via Web & API domain
request GET "{api_server}/telemetry" into net_resp
parse net_resp as JSON into raw_telemetry

# 2. Clean and deduplicate via Data Engineering domain
pipeline "clean_telemetry" from raw_telemetry into cleaned_data:
    remove duplicate rows
    filter where score is greater than 30

# 3. Query high-value records via Database & SQL domain
query cleaned_data into high_scores:
    select id, score
    where score is over 50
    order by score descending

# 4. Train predictive model via Machine Learning domain
model performance_model from cleaned_data:
    target: score
    features: feature1, feature2
    algorithm: linear_regression
    split: 80% training, 20% testing

train performance_model
evaluate performance_model into ml_eval

# 5. Run system queue simulation via Simulation domain
simulate customer_queue:
    arrivals: poisson with rate 10.0
    service: exponential with rate 15.0
    duration: 50 events
    servers: 1

# 6. Benchmark an algorithm via Testing & DSA domain
to dummy_sort with arr:
    set n to count of arr
    return n

benchmark dummy_sort:
    input_sizes: [10, 50, 100]
    repeat: 3
    measure: execution_time
"""
    env = execute(source)

    # 1. Net assertions
    assert "net_resp" in env
    assert env["net_resp"].status_code == 200
    assert len(env["raw_telemetry"]) == 6

    # 2. Data engineering assertions (deduplicated 6 -> 5, filtered score > 30 -> 4)
    assert "cleaned_data" in env
    assert len(env["cleaned_data"]) == 4

    # 3. DB assertions (score > 50 -> ids 3, 4, 5)
    assert "high_scores" in env
    assert len(env["high_scores"]) == 3
    assert env["high_scores"][0]["id"] == 5

    # 4. ML assertions
    assert "performance_model" in env
    assert "ml_eval" in env
    assert "r2_score" in env["ml_eval"]
    assert env["ml_eval"]["r2_score"] > 0.8

    # 5. Simulation assertions
    assert "customer_queue" in env
    assert "utilization" in env["customer_queue"]

    # 6. DSA benchmarking assertions
    assert "dummy_sort_benchmark" in env
    assert env["dummy_sort_benchmark"]["complexity_class"] in ("O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)")
    assert "timings" in env["dummy_sort_benchmark"]
    assert "confidence_r2" in env["dummy_sort_benchmark"]


def test_cross_domain_ast_export():
    """Verifies that a multi-domain program exports cleanly to native Python AST."""
    source = """
use data
use db
use ml
use sim

raw_items = [
    {"x": 1.0, "y": 2.0},
    {"x": 2.0, "y": 4.0},
    {"x": 3.0, "y": 6.0}
]

pipeline "clean_items" from raw_items into ready_items:
    remove duplicate rows

query ready_items into filtered_items:
    select x, y
    where y is over 3

model reg_model from ready_items:
    target: y
    features: x
    algorithm: linear_regression

simulate queue_sim:
    arrivals: poisson with rate 5.0
    service: exponential with rate 8.0
    duration: 100 events
"""
    exported_py = export_to_python(source)
    assert isinstance(exported_py, str)
    assert "pandas" in exported_py or "pd" in exported_py
    assert "sqlite3" in exported_py
    assert "SELECT" in exported_py or "filter" in exported_py


def test_cross_domain_web_agent_image(tmp_path):
    """Verifies seamless orchestration across web scraping, AI agents, and image manipulation."""
    import os
    banner_path = str(tmp_path / "article_banner.png").replace("\\", "/")
    source = f"""
use web
use agent
use image

# 1. Scrape web page
parse html "<html><title>Breakthrough AI</title><body><h1>Quantum Leap</h1><p>New quantum algorithms accelerate ML.</p></body></html>" into page
title of page into heading

# 2. Agent summarizes and devises a slogan
create agent CreativeDirector with role "Visual Slogan Creator" into director
ask agent director to "Generate a 2-word punchy headline" with context heading into slogan

# 3. Image domain creates branded visual banner
create blank image with width 600, height 200, color "navy" into banner
draw text slogan on banner at 20, 80 with color "white"
save image banner to "{banner_path}"
"""
    env = execute(source)
    assert env["heading"] == "Breakthrough AI"
    assert "slogan" in env
    assert env["banner"].size == (600, 200)
    assert os.path.exists(banner_path)


def test_cross_domain_finance_office_cloud(tmp_path):
    """Verifies end-to-end integration: quant finance -> spreadsheet creation -> cloud bucket sync."""
    import os
    sheet_file = str(tmp_path / "aapl_report.xlsx").replace("\\", "/")
    source = f"""
use finance
use office
use cloud

# 1. Fetch stock prices and compute indicators
fetch stock prices for "AAPL" from "2024-01-01" to "2024-01-31" into quotes
calculate 5 day moving average of quotes into sma5

# 2. Package into spreadsheet workbook
create spreadsheet into report_sheet
add row ["Date", "Symbol", "Close"] to report_sheet
for q in quotes:
    add row [q.date, q.symbol, q.close] to report_sheet
save spreadsheet report_sheet to "{sheet_file}"

# 3. Synchronize to cloud object storage
connect to bucket "financial-reports" into storage
upload file "{sheet_file}" to bucket storage as "2024/aapl_report.xlsx"
list all files in storage matching "*.xlsx" into cloud_sheets
generate signed url for "2024/aapl_report.xlsx" in storage into download_link
"""
    env = execute(source)
    assert os.path.exists(sheet_file)
    assert "2024/aapl_report.xlsx" in env["cloud_sheets"]
    assert env["download_link"].startswith("https://financial-reports.s3.amazonaws.com/")
    assert len(env["quotes"]) > 10
