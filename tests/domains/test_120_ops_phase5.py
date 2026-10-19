import pytest
import os
from doomscript.compiler.engine import execute

def test_batch16_agent():
    code = """
use agent

create agent dev_lead with role "lead" into lead_agent
create agent dev_eng with role "developer" into eng_agent
create team engineering with agents [lead_agent, eng_agent] into team_eng

broadcast message "prepare for release" to team team_eng into bcast_res
tally consensus votes from ["approve", "approve", "reject"] with threshold 0.6 into vote_res
prioritize agent tasks [{"task": "doc typo", "urgency": "low"}, {"task": "fix crash", "urgency": "critical"}, {"task": "add button", "urgency": "medium"}] into prio_tasks
dispatch task {"task": "implement feature", "role": "developer"} to team team_eng into dispatch_res
aggregate agent responses ["Review 1 looks good", "Review 2 approves"] into summary_res
filter memory of agent lead_agent by "user" into filtered_mem
"""
    result = execute(code)
    assert result["bcast_res"]["delivered"] is True
    assert result["bcast_res"]["count"] == 2
    
    assert result["vote_res"]["winner"] == "approve"
    assert result["vote_res"]["confidence"] == round(2 / 3, 4)
    assert result["vote_res"]["consensus"] is True
    
    assert result["prio_tasks"][0]["urgency"] == "critical"
    assert result["prio_tasks"][-1]["urgency"] == "low"
    
    assert result["dispatch_res"]["assigned_to"] == "dev_eng"
    assert result["dispatch_res"]["status"] == "dispatched"
    
    assert result["summary_res"]["count"] == 2
    assert "Review 1" in result["summary_res"]["combined_text"]
    
    assert isinstance(result["filtered_mem"], list)
    assert len(result["filtered_mem"]) >= 1
    assert result["filtered_mem"][0]["content"] == "prepare for release"

def test_batch17_cloud(tmp_path):
    temp_file = str(tmp_path / "temp_test.txt")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write("SAMPLE CONTENT FOR CLOUD TESTS")

    code = f"""
use cloud

connect to bucket "test_bucket_batch17" into bkt
upload file "{temp_file.replace(chr(92), '/')}" to bucket bkt as "logs/2026/run1.txt"
upload file "{temp_file.replace(chr(92), '/')}" to bucket bkt as "logs/2026/run2.txt"
upload file "{temp_file.replace(chr(92), '/')}" to bucket bkt as "data/input.csv"

list files in bucket bkt with prefix "logs/2026" into log_files
get metadata of file "data/input.csv" in bucket bkt into file_meta
check if file "data/input.csv" exists in bucket bkt into exists_res
calculate total size of bucket bkt into bucket_stats
copy object "data/input.csv" to "archive/input.csv" in bucket bkt into copy_res
delete files matching "*.txt" in bucket bkt into deleted_cnt
"""
    result = execute(code)
    assert len(result["log_files"]) == 2
    assert "logs/2026/run1.txt" in result["log_files"]
    
    assert result["file_meta"]["exists"] is True
    assert result["file_meta"]["size_bytes"] > 0
    assert result["exists_res"] is True
    
    assert result["bucket_stats"]["file_count"] >= 3
    assert result["bucket_stats"]["total_bytes"] > 0
    
    assert "archive/input.csv" in result["copy_res"]
    assert result["deleted_cnt"] == 2

def test_batch18_office():
    code = """
use office

create spreadsheet into sheet
add worksheet "Q4 Report" to spreadsheet sheet into sheet_with_tab
append table [{"item": "Widget A", "sales": 100}, {"item": "Widget B", "sales": 250}] to worksheet "Q4 Report" in spreadsheet sheet into updated_sheet
count worksheets in spreadsheet sheet into sheet_count

create word document into doc
add heading "Executive Summary" to document doc
add paragraph "This is the primary report body." to document doc
extract text from document doc into doc_text
count pages in document doc into doc_pages

set md_sample to "# Title\\n\\nIntroduction paragraph\\n- First point\\n- Second point"
convert markdown md_sample to document sections into parsed_sections
merge pdf files ["p1.pdf", "p2.pdf"] into merged_result
"""
    result = execute(code)
    assert result["sheet_count"] == 2
    assert "Q4 Report" in result["updated_sheet"].worksheets
    assert len(result["updated_sheet"].worksheets["Q4 Report"]) >= 2
    
    assert "Executive Summary" in result["doc_text"]
    assert "primary report body" in result["doc_text"]
    assert result["doc_pages"] >= 1
    
    assert len(result["parsed_sections"]) >= 3
    assert result["parsed_sections"][0]["type"] == "heading"
    assert result["parsed_sections"][0]["text"] == "Title"
    
    assert result["merged_result"]["merged_count"] == 2
    assert result["merged_result"]["success"] is True
