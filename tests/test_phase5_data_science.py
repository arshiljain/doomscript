"""
Phase 5 Tests: Data Science Verbs over pandas
Verifies high-level data science verbs and raw pandas interop.
"""

import os
import tempfile
import pytest
import pandas as pd
from doomscript.compiler.engine import execute


def test_load_and_save_table():
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "employees.csv").replace("\\", "/")
        out_path = os.path.join(tmpdir, "saved_employees.csv").replace("\\", "/")
        
        df = pd.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "dept": ["Eng", "Sales", "Eng"],
            "salary": [100000, 80000, 120000]
        })
        df.to_csv(csv_path, index=False)
        
        code = f"""
load table "{csv_path}" into employees
save table employees into "{out_path}"
"""
        env = execute(code)
        assert os.path.exists(out_path)
        loaded_df = pd.read_csv(out_path)
        assert len(loaded_df) == 3
        assert list(loaded_df["name"]) == ["Alice", "Bob", "Charlie"]


def test_filter_table():
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "scores.csv").replace("\\", "/")
        df = pd.DataFrame({
            "student": ["Sam", "Alex", "Jordan", "Taylor"],
            "score": [85, 92, 78, 95]
        })
        df.to_csv(csv_path, index=False)
        
        code = f"""
load table "{csv_path}" into grades
filter grades where score >= 90 into top_students
"""
        env = execute(code)
        top = env["top_students"]
        assert len(top) == 2
        assert set(top["student"]) == {"Alex", "Taylor"}


def test_sort_table_descending():
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "products.csv").replace("\\", "/")
        df = pd.DataFrame({
            "product": ["Pen", "Notebook", "Backpack"],
            "price": [2.5, 5.0, 45.0]
        })
        df.to_csv(csv_path, index=False)
        
        code = f"""
load table "{csv_path}" into items
sort items by price descending into ranked
"""
        env = execute(code)
        ranked = env["ranked"]
        assert list(ranked["product"]) == ["Backpack", "Notebook", "Pen"]


def test_group_by_and_average_and_sum():
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "sales.csv").replace("\\", "/")
        df = pd.DataFrame({
            "rep": ["Alice", "Bob", "Alice", "Bob", "Alice"],
            "revenue": [200, 150, 300, 250, 100]
        })
        df.to_csv(csv_path, index=False)
        
        code = f"""
load table "{csv_path}" into sales
group sales by rep and average revenue into avg_rev
group sales by rep and sum revenue into total_rev
"""
        env = execute(code)
        avg_df = env["avg_rev"]
        tot_df = env["total_rev"]
        
        alice_avg = avg_df[avg_df["rep"] == "Alice"]["revenue"].iloc[0]
        bob_avg = avg_df[avg_df["rep"] == "Bob"]["revenue"].iloc[0]
        assert alice_avg == 200.0
        assert bob_avg == 200.0
        
        alice_tot = tot_df[tot_df["rep"] == "Alice"]["revenue"].iloc[0]
        bob_tot = tot_df[tot_df["rep"] == "Bob"]["revenue"].iloc[0]
        assert alice_tot == 600
        assert bob_tot == 400


def test_raw_pandas_interop():
    code = """
use python module pandas as pd
data = {"dept": ["HR", "Eng", "Eng", "HR"], "salary": [50000, 110000, 120000, 60000]}
df = pd.DataFrame(data)
dept_means = df.groupby("dept")["salary"].mean()
say dept_means["Eng"]
"""
    env = execute(code)
    assert env["dept_means"]["Eng"] == 115000.0


def test_end_to_end_data_pipeline(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        input_csv = os.path.join(tmpdir, "raw_data.csv").replace("\\", "/")
        summary_csv = os.path.join(tmpdir, "dept_summary.csv").replace("\\", "/")
        
        raw_df = pd.DataFrame({
            "dept": ["Support", "Eng", "Eng", "Sales", "Support", "Eng", "Sales"],
            "active": [1, 1, 1, 1, 0, 1, 1],
            "tenure": [2, 5, 3, 1, 4, 8, 3]
        })
        raw_df.to_csv(input_csv, index=False)
        
        code = f"""
load table "{input_csv}" into full_data
filter full_data where active == 1 into active_data
group active_data by dept and average tenure into summary
sort summary by tenure descending into final_report
save table final_report into "{summary_csv}"
say final_report["dept"].iloc[0]
"""
        execute(code)
        captured = capsys.readouterr()
        assert captured.out.strip() == "Eng"
        
        saved = pd.read_csv(summary_csv)
        assert len(saved) == 3
        assert saved.iloc[0]["dept"] == "Eng"
        assert saved.iloc[0]["tenure"] == (5 + 3 + 8) / 3.0


def test_plot_verb():
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "timeseries.csv").replace("\\", "/")
        df = pd.DataFrame({
            "time": [1, 2, 3, 4],
            "val": [10, 20, 15, 30]
        })
        df.to_csv(csv_path, index=False)
        
        code = f"""
load table "{csv_path}" into ts
fig = plot val against time from ts
"""
        env = execute(code)
        assert env["fig"] is not None
