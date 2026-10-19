"""
Comprehensive test suite verifying DoomScript English-first syntax ergonomics
and shorter-than-Python idioms across core general programming and all domain packs.
"""

import math
import os
import tempfile
from collections import deque
from doomscript.compiler.engine import execute, compile_to_ast, transpile, export_to_python
from doomscript.runtime import Record


def test_core_english_file_io():
    with tempfile.TemporaryDirectory() as tmp_dir:
        text_path = os.path.join(tmp_dir, "notes.txt").replace("\\", "/")
        csv_path = os.path.join(tmp_dir, "data.csv").replace("\\", "/")

        source = f"""
content = "Hello English DoomScript!"
write content to "{text_path}"
read "{text_path}" into loaded_text
check if "{text_path}" exists into file_found

append "\\nLine two" to "{text_path}"
read "{text_path}" into updated_text

csv_rows = [{{"item": "apple", "qty": 10}}, {{"item": "banana", "qty": 20}}]
save csv_rows to "{csv_path}"
read "{csv_path}" into loaded_csv
"""
        env = execute(source)
        assert env["loaded_text"] == "Hello English DoomScript!"
        assert env["file_found"] is True
        assert "Line two" in env["updated_text"]
        assert len(env["loaded_csv"]) == 2
        assert env["loaded_csv"][0]["item"] == "apple"
        assert int(env["loaded_csv"][1]["qty"]) == 20


def test_core_english_math_and_stats():
    source = """
scores = [80, 90, 100, 70, 60]

average of scores into avg
median of scores into med
total of scores into total_score
maximum of scores into top_score
minimum of scores into low_score
standard deviation of scores into std_val
variance of scores into var_val
count of scores into n
"""
    env = execute(source)
    assert env["avg"] == 80.0
    assert env["med"] == 80.0
    assert env["total_score"] == 400
    assert env["top_score"] == 100
    assert env["low_score"] == 60
    assert env["n"] == 5
    assert math.isclose(env["std_val"], 15.811, abs_tol=0.01)
    assert math.isclose(env["var_val"], 250.0, abs_tol=0.01)


def test_core_english_string_and_collections():
    source = """
sentence = "DoomScript reads completely like natural English prose"
words in sentence into word_list
lines in "line 1\\nline 2" into line_list

user_info = Record({"name": "Arthur", "role": "admin", "level": 42})
keys of user_info into user_keys
values of user_info into user_vals

nums = [1, 2, 3, 4, 5]
reverse nums into rev_nums
shuffle nums into shuffled_nums

greeting = "hello world"
uppercase greeting into shouting
lowercase shouting into quiet
"""
    env = execute(source)
    assert env["word_list"] == ["DoomScript", "reads", "completely", "like", "natural", "English", "prose"]
    assert env["line_list"] == ["line 1", "line 2"]
    assert "name" in env["user_keys"]
    assert "Arthur" in env["user_vals"]
    assert env["rev_nums"] == [5, 4, 3, 2, 1]
    assert len(env["shuffled_nums"]) == 5
    assert env["shouting"] == "HELLO WORLD"
    assert env["quiet"] == "hello world"


def test_core_english_timing_and_wait():
    source = """
start_val = 10
sleep 0.01 seconds
delay 10 ms
pause 0.01 second
end_val = start_val + 5
"""
    env = execute(source)
    assert env["end_val"] == 15


def test_data_domain_english_one_liners():
    source = """use data

sales = [
    {"id": 1, "region": "North", "rep": "Alice", "revenue": 500},
    {"id": 2, "region": "South", "rep": "Bob", "revenue": 150},
    {"id": 3, "region": "North", "rep": "Charlie", "revenue": 300},
    {"id": 1, "region": "North", "rep": "Alice", "revenue": 500},
    {"id": 4, "region": "South", "rep": None, "revenue": 200}
]

remove duplicates from sales by "id" into unique_sales
remove nulls from unique_sales in "rep" into clean_sales
filter clean_sales where revenue > 200 into high_sales
sort high_sales by "revenue" descending into ranked_sales
group clean_sales by "region" calculating sum "revenue" into regional_revenue
"""
    env = execute(source)
    assert len(env["unique_sales"]) == 4
    assert len(env["clean_sales"]) == 3
    assert len(env["high_sales"]) == 2
    assert env["ranked_sales"][0]["revenue"] == 500
    assert env["ranked_sales"][1]["revenue"] == 300
    
    reg_rev = {r["region"]: r["sum_revenue"] for r in env["regional_revenue"]}
    assert reg_rev["North"] == 800
    assert reg_rev["South"] == 150


def test_data_domain_english_joins():
    source = """use data

customers = [
    {"cust_id": 101, "name": "Acme Corp"},
    {"cust_id": 102, "name": "Global Tech"}
]

orders = [
    {"order_id": 1, "cust_id": 101, "total": 1200},
    {"order_id": 2, "cust_id": 102, "total": 4500}
]

join customers with orders on "cust_id" as inner into matched_orders
"""
    env = execute(source)
    assert len(env["matched_orders"]) == 2
    assert env["matched_orders"][0]["name"] == "Acme Corp"
    assert env["matched_orders"][0]["total"] == 1200


def test_ml_domain_english_one_liners():
    source = """use ml

customers = [
    {"age": 25, "usage": 10, "churn": 0},
    {"age": 45, "usage": 5, "churn": 1},
    {"age": 22, "usage": 15, "churn": 0},
    {"age": 60, "usage": 2, "churn": 1},
    {"age": 30, "usage": 12, "churn": 0},
    {"age": 55, "usage": 3, "churn": 1}
]

train decision_tree on customers predicting churn into churn_model

test_samples = [
    {"age": 24, "usage": 11},
    {"age": 50, "usage": 4}
]

predict churn_model on test_samples into predictions
actual_labels = [0, 1]
accuracy of predictions against actual_labels into model_accuracy
"""
    env = execute(source)
    assert "churn_model" in env
    assert env["churn_model"].is_trained
    assert len(env["predictions"]) == 2
    assert env["predictions"] == [0, 1]
    assert env["model_accuracy"] == 1.0


def test_db_domain_english_one_liners():
    source = """use db

execute sql "DROP TABLE IF EXISTS employees"
execute sql "CREATE TABLE employees (id INT, name TEXT, salary INT, dept TEXT)"
execute sql "INSERT INTO employees VALUES (1, 'Alice', 110000, 'Engineering')"
execute sql "INSERT INTO employees VALUES (2, 'Bob', 85000, 'Design')"
execute sql "INSERT INTO employees VALUES (3, 'Charlie', 130000, 'Engineering')"

find rows in employees where salary > 100000 into top_earners
find all rows in employees into all_staff
count rows in employees into total_count
"""
    env = execute(source)
    assert len(env["top_earners"]) == 2
    assert env["top_earners"][0]["name"] == "Alice"
    assert env["top_earners"][1]["name"] == "Charlie"
    assert len(env["all_staff"]) == 3
    assert env["total_count"] == 3


def test_nlp_domain_english_one_liners():
    source = """use nlp

review = "DoomScript provides an outstanding and lovely developer experience! We really enjoyed using it."

sentiment of review into sentiment_info
words in review into word_tokens
sentences in review into sentence_tokens
bigrams of review into bigram_list
trigrams of review into trigram_list

corpus = ["good code", "great code", "python language", "doomscript language"]
tfidf of corpus into tfidf_matrix
"""
    env = execute(source)
    assert env["sentiment_info"]["polarity"] > 0
    assert len(env["word_tokens"]) > 5
    assert len(env["sentence_tokens"]) == 2
    assert len(env["bigram_list"]) > 0
    assert len(env["trigram_list"]) > 0
    assert len(env["tfidf_matrix"]["matrix"]) == 4


def test_geo_domain_english_one_liners():
    source = """use geo

point 37.7749, -122.4194 into sf
point 40.7128, -74.0060 into nyc

distance from sf to nyc in km into coast_to_coast_dist

zone = [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [0.0, 0.0]]
polygon from zone into delivery_area

point 5.0, 5.0 into inside_point
point 15.0, 15.0 into outside_point

is inside_point inside delivery_area into inside_res
is outside_point inside delivery_area into outside_res
"""
    env = execute(source)
    assert env["coast_to_coast_dist"] > 4000
    assert env["inside_res"] is True
    assert env["outside_res"] is False


def test_opt_domain_english_direct_block():
    source = """use opt

maximize 40 * chairs + 30 * tables into production_plan where:
    chairs + tables <= 16
    chairs + 2 * tables <= 20
"""
    env = execute(source)
    assert "production_plan" in env
    plan = env["production_plan"]
    assert plan["status"].lower() == "optimal"
    assert plan["objective_value"] > 500


def test_sim_domain_english_one_liners():
    source = """use sim

sample normal with mean 100 and std 15 count 500 into test_scores
average of test_scores into mean_score
standard deviation of test_scores into std_score

sample uniform between 10 and 20 count 500 into delay_times
average of delay_times into mean_delay
"""
    env = execute(source)
    assert 95 <= env["mean_score"] <= 105
    assert 12 <= env["std_score"] <= 18
    assert 13 <= env["mean_delay"] <= 17


def test_dsa_domain_english_one_liners():
    source = """use dsa

to linear_scan with arr:
    total = 0
    for each x in arr:
        total = total + x
    return total

benchmark linear_scan on sizes [10, 50, 100] into bench_result

heap_items = []
push 42 into heap heap_items
push 15 into heap heap_items
push 88 into heap heap_items

pop min from heap_items into min_val
pop max from heap_items into max_val
"""
    env = execute(source)
    assert "bench_result" in env
    assert len(env["bench_result"]["timings"]) == 3
    assert env["min_val"] == 15
    assert env["max_val"] == 88


def test_viz_domain_english_chart_forms():
    source = """use viz

sales_data = [
    {"quarter": "Q1", "revenue": 100},
    {"quarter": "Q2", "revenue": 150},
    {"quarter": "Q3", "revenue": 200}
]

bar chart of sales_data with x="quarter", y="revenue" into p_bar
line chart of sales_data with x="quarter", y="revenue" into p_line
scatter plot of sales_data with x="quarter", y="revenue" into p_scatter
"""
    env = execute(source)
    assert "p_bar" in env
    assert "p_line" in env
    assert "p_scatter" in env
    assert env["p_bar"].spec().layers[0].geom == "bar"
    assert env["p_line"].spec().layers[0].geom == "line"
    assert env["p_scatter"].spec().layers[0].geom == "point"
