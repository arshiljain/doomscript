"""Unit tests for Track 1: Conversational Domain Vocabularies ("Talking to the Tools")."""

import http.server
import json
import socketserver
import threading
import pytest
from doomscript.compiler.engine import execute
from doomscript.core.record import Record


class ConversationalMockHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/data":
            payload = json.dumps({
                "status": "success",
                "data": {
                    "items": [
                        {"id": 101, "name": "Widget A", "price": 25.5},
                        {"id": 102, "name": "Widget B", "price": 40.0},
                    ],
                    "total": 2
                }
            }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/submit":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            received_data = json.loads(body) if body else {}
            payload = json.dumps({
                "status": "ok",
                "received": received_data,
                "message": "Created successfully"
            }).encode("utf-8")
            self.send_response(201)
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
def mock_server():
    server = socketserver.TCPServer(("127.0.0.1", 0), ConversationalMockHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


# ---------------------------------------------------------------------------
# Task 1: Web & APIs Conversational Tests
# ---------------------------------------------------------------------------

def test_web_conversational_get_request(mock_server):
    code = f"""
send a get request to "{mock_server}/data" and wait for response into res
extract json field "data.items" from res into items
extract json field "status" from res into st
"""
    env = execute(code)
    assert "res" in env
    assert env["res"]["status"] == 200
    assert "items" in env
    assert len(env["items"]) == 2
    assert env["items"][0]["name"] == "Widget A"
    assert env["st"] == "success"


def test_web_conversational_post_request(mock_server):
    code = f"""
payload = {{"item": "DoomBook", "qty": 3}}
send a post request to "{mock_server}/submit" with payload into res
extract json field "received.item" from res into item_name
"""
    env = execute(code)
    assert "res" in env
    assert env["res"]["status"] == 201
    assert env["item_name"] == "DoomBook"


def test_web_conversational_post_shorthand(mock_server):
    code = f"""
payload = {{"code": "XYZ"}}
post payload to "{mock_server}/submit" into res
extract json field "received.code" from res into code_val
"""
    env = execute(code)
    assert "res" in env
    assert env["res"]["status"] == 201
    assert env["code_val"] == "XYZ"


def test_extract_json_field_from_dict_and_string():
    code = """
raw = '{"user": {"profile": {"name": "Alice", "score": 98}}}'
extract json field "user.profile.name" from raw into user_name
extract field "user.profile.score" from raw into user_score
"""
    env = execute(code)
    assert env["user_name"] == "Alice"
    assert env["user_score"] == 98


# ---------------------------------------------------------------------------
# Task 2: Data & Analytics Conversational Tests
# ---------------------------------------------------------------------------

def test_conversational_load_csv_and_json(tmp_path):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text("region,revenue,units\nNorth,500,10\nSouth,300,5\nNorth,700,15\nSouth,400,8\n", encoding="utf-8")
    json_file = tmp_path / "config.json"
    json_file.write_text('{"app": "DoomScript", "version": "0.6.0"}', encoding="utf-8")

    csv_path_str = str(csv_file).replace("\\", "/")
    json_path_str = str(json_file).replace("\\", "/")

    code = f"""
load csv from "{csv_path_str}" into sales_table
load json from "{json_path_str}" into app_config
"""
    env = execute(code)
    assert "sales_table" in env
    assert len(env["sales_table"]) == 4
    assert env["app_config"]["version"] == "0.6.0"


def test_conversational_summarize_data(tmp_path):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text("region,revenue,units\nNorth,500,10\nSouth,300,5\nNorth,700,15\nSouth,400,8\n", encoding="utf-8")
    csv_path_str = str(csv_file).replace("\\", "/")

    code = f"""
load csv from "{csv_path_str}" into sales_table
summarize column "revenue" by "region" in sales_table into regional_sales
summarize sales_table by "region" calculating average of "revenue" into avg_sales
"""
    env = execute(code)
    assert "regional_sales" in env
    rs = env["regional_sales"]
    # Check that North sum is 1200 and South sum is 700
    by_region = {r["region"]: r["revenue"] for r in rs}
    assert by_region["North"] == 1200
    assert by_region["South"] == 700

    avg_rs = env["avg_sales"]
    avg_by_region = {r["region"]: r["revenue"] for r in avg_rs}
    assert avg_by_region["North"] == 600.0
    assert avg_by_region["South"] == 350.0


def test_conversational_plot_chart(tmp_path):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text("region,revenue\nNorth,1200\nSouth,700\n", encoding="utf-8")
    csv_path_str = str(csv_file).replace("\\", "/")

    code = f"""
load csv from "{csv_path_str}" into regional_sales
plot regional_sales as a bar chart titled "Q4 Regional Sales" into my_chart
"""
    env = execute(code)
    assert "my_chart" in env
    chart = env["my_chart"]
    assert chart._labels.title == "Q4 Regional Sales"


# ---------------------------------------------------------------------------
# Task 3: Finance & Simulation Conversational Tests
# ---------------------------------------------------------------------------

def test_conversational_compound_interest():
    code = """
calculate compound interest on principal 1000 at rate 5% over 10 years into total
calculate compound interest on principal 2000 at rate 0.08 over 3 years into total2
"""
    env = execute(code)
    assert "total" in env
    assert env["total"] == 1628.89
    assert "total2" in env
    assert env["total2"] == 2519.42


def test_conversational_portfolio_simulation_percentages():
    code = """
simulate portfolio with 50% BTC and 50% ETH into sim_result
"""
    env = execute(code)
    assert "sim_result" in env
    res = env["sim_result"]
    assert res["allocations"]["BTC"] == 0.5
    assert res["allocations"]["ETH"] == 0.5
    assert res["initial_value"] == 10000.0
    assert res["projected_value"] > 0
    assert "sharpe_ratio" in res


def test_conversational_portfolio_simulation_dict():
    code = """
weights = {"AAPL": 0.6, "MSFT": 0.4}
simulate portfolio with weights into sim_result
"""
    env = execute(code)
    assert "sim_result" in env
    res = env["sim_result"]
    assert res["allocations"]["AAPL"] == 0.6
    assert res["allocations"]["MSFT"] == 0.4
    assert res["projected_value"] > 0


# ---------------------------------------------------------------------------
# Task 4: AI & Agent Conversational Tests
# ---------------------------------------------------------------------------

def test_conversational_ask_assistant():
    code = """
ask the assistant "Summarize this report" into summary
ask assistant "Generate title" into title_res
"""
    env = execute(code)
    assert "summary" in env
    assert "report" in env["summary"].lower() or "ai" in env["summary"].lower()
    assert "title_res" in env


def test_conversational_ask_model_with_context():
    code = """
report = "Quarterly profits rose 15%."
ask the model "Classify sentiment" for report into sentiment
ask model "Summarize" for report into brief
"""
    env = execute(code)
    assert "sentiment" in env
    assert len(env["sentiment"]) > 0
    assert "brief" in env
    assert len(env["brief"]) > 0


def test_conversational_agent_article_tolerance():
    code = """
use agent
create agent "Researcher" into my_agent
ask the agent my_agent "Find papers" into findings
tell the agent my_agent "Good job"
"""
    env = execute(code)
    assert "findings" in env
    assert len(env["findings"]) > 0



