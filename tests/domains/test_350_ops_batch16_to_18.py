"""Verification test suite for Batch 16 to 18 of the 350 Spoken-English Operations:
- Batch 16: Cloud Domain (19 operations)
- Batch 17: Office Domain (19 operations)
- Batch 18: Research Domain (19 operations)
"""

import os
import shutil
import tempfile
import pytest
from doomscript.compiler.engine import execute


def test_batch_16_cloud_domain_operations():
    tmp_dir = tempfile.mkdtemp(prefix="doom_cloud_test_")
    try:
        script = f"""
use cloud
connect to bucket "test-store" into b1
connect to bucket "mirror-store" into b2

# 1. Direct text write
write text "Hello Cloud Storage" to object "notes/test.txt" in b1

# 2. Direct text read
read text from object "notes/test.txt" in b1 into content
say "Read content:", content

# 3. Presigned PUT url
generate presigned put url for "uploads/data.bin" in b1 with expiry 1800 into put_url
say "Presigned PUT URL:", put_url

# 4. Checksums
verify sha256 checksum of "notes/test.txt" in b1 against "ignored" into sha_match
verify md5 checksum of "notes/test.txt" in b1 against "ignored" into md5_match

# 5. Object tags
tags = a new record
tags["env"] = "staging"
tags["owner"] = "analyst"
set object tags for "notes/test.txt" in b1 to tags
get object tags for "notes/test.txt" in b1 into retrieved_tags

# 6. Storage class
set storage class for "notes/test.txt" in b1 to "COLDLINE"
get storage class for "notes/test.txt" in b1 into tier

# 7. Directory marker
create directory marker "logs/2026/" in b1 into dir_marker

# 8. Create additional files for filtering and diff
write text "Small log" to object "logs/app.log" in b1
write text "A bigger log with lots of info" to object "logs/audit.log" in b1
write text '{{"version": 1}}' to object "config/settings.json" in b1

# 9. Filter files by size
filter files in b1 by size between 1 and 20 into small_files
say "Small files count:", count of small_files

# 10. Filter files by date
filter files in b1 modified after "2020-01-01T00:00:00" into recent_files
say "Recent files count:", count of recent_files

# 11. Count objects by extension
count objects by extension in b1 into ext_counts
say "Log count:", ext_counts["log"]

# 12. Move object
move object "notes/test.txt" to "notes/renamed.txt" in b1

# 13. Mirror buckets
mirror bucket b1 to b2 into mirror_result

# 14. Diff buckets
write text "Unique to b1" to object "unique.txt" in b1
diff bucket b1 with bucket b2 into bucket_diff
say "Only in first:", count of bucket_diff["only_in_first"]

# 15. Export manifest
manifest_path = "{tmp_dir.replace('\\', '/')}/manifest.json"
export bucket manifest for b1 to manifest_path into exported_manifest

# 16. Archive stale files
archive stale files in b1 older than 365 days into archive_count

# 17. Batch delete keys
keys_to_delete = a list of "logs/app.log", "logs/audit.log"
batch delete keys keys_to_delete from b1 into deleted_count
say "Deleted keys count:", deleted_count
"""
        env = execute(script)
        assert env["content"] == "Hello Cloud Storage"
        assert "http" in env["put_url"]
        assert env["sha_match"] is False  # dummy hash doesn't match real sha256
        assert env["retrieved_tags"]["env"] == "staging"
        assert env["tier"] == "COLDLINE"
        assert env["dir_marker"] == "logs/2026/"
        assert len(env["small_files"]) >= 1
        assert len(env["recent_files"]) >= 3
        assert env["ext_counts"]["log"] == 2
        assert env["deleted_count"] == 2
        assert os.path.exists(env["exported_manifest"])
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_batch_17_office_domain_operations():
    tmp_dir = tempfile.mkdtemp(prefix="doom_office_test_")
    try:
        # Create a sample CSV file for delimiter detection and header reading
        csv_file = os.path.join(tmp_dir, "sample.csv").replace("\\", "/")
        with open(csv_file, "w", encoding="utf-8") as f:
            f.write("Department,Employees,Budget\nEngineering,50,500000\nMarketing,20,200000\nSales,30,300000\n")

        script = f"""
use office

# 1. Detect CSV delimiter
detect csv delimiter in "{csv_file}" into delim
say "Delimiter:", delim

# 2. Read CSV header
read csv header from "{csv_file}" into headers
say "Headers:", headers

# 3. Create spreadsheet and populate
create spreadsheet into sheet
row1 = a list of "Product", "Price", "Quantity"
add row row1 to sheet
row2 = a list of "Widget", 10.0, 5
add row row2 to sheet
row3 = a list of "Gadget", 25.0, 2
add row row3 to sheet
row4 = a list of "Doohickey", 15.0, 4
add row row4 to sheet

# 4. Sheet summary
calculate sheet summary of column 1 in sheet "Sheet1" of sheet into price_summary
say "Avg price:", price_summary["avg"]

# 5. Cell get and set
set cell at row 1 col 1 in sheet "Sheet1" of sheet to 12.5
get cell at row 1 col 1 in sheet "Sheet1" of sheet into updated_cell
say "Updated cell:", updated_cell

# 6. Worksheet management: add, list, rename, delete
add worksheet "Sheet2" to sheet into ws2
list worksheets in sheet into sheet_names
rename worksheet "Sheet2" to "Archive" in sheet
delete worksheet "Archive" from sheet
list worksheets in sheet into final_sheet_names

# 7. Sort sheet by column
sort sheet "Sheet1" in sheet by column 1 descending into sorted_rows

# 8. Filter sheet rows
filter sheet "Sheet1" in sheet where column 2 matches 5 into filtered_rows

# 9. Export sheet to JSON
export_json_path = "{tmp_dir.replace('\\', '/')}/sheet.json"
export sheet "Sheet1" in sheet to json export_json_path

# 10. Import JSON into new sheet
import json export_json_path into sheet "Imported" of sheet into imported_count

# 11. Word document operations
create word document into doc
add heading "Quarterly Operations Report" at level 1 to doc
add paragraph "This document outlines performance metrics across departments." to doc

# 12. Add lists and tables
items = a list of "First milestone achieved", "Budget approved", "Audit passed"
add bulleted list items to doc
add numbered list items to doc

tbl_headers = a list of "ID", "Metric", "Status"
row_a = a list of 1, "Uptime", "99.9%"
row_b = a list of 2, "Latency", "42ms"
tbl_rows = a list of row_a, row_b
add table with headers tbl_headers and rows tbl_rows to doc

# 13. Find and replace in document
find and replace "Audit" with "Security Audit" in doc into replace_count

# 14. Document word & character count
count words in doc into word_cnt
count characters in doc into char_cnt

# 15. Extract document metadata
extract document metadata from doc into doc_meta
"""
        env = execute(script)
        assert env["delim"] == ","
        assert env["headers"] == ["Department", "Employees", "Budget"]
        assert env["price_summary"]["count"] == 3
        assert env["updated_cell"] == 12.5
        assert "Sheet2" in env["sheet_names"]
        assert "Archive" not in env["final_sheet_names"]
        assert env["sorted_rows"][1][1] == 25.0  # highest price descending after header
        assert len(env["filtered_rows"]) == 2  # header + 1 matching row
        assert env["imported_count"] == 3
        assert env["replace_count"] >= 2  # replaced in bullet and numbered lists
        assert env["word_cnt"] > 10
        assert env["char_cnt"] > 50
        assert env["doc_meta"]["headings"] == 1
        assert env["doc_meta"]["tables"] == 1
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_batch_18_research_domain_operations():
    script = """
use research

create a research graph into g

# Construct a graph for testing shortest paths, components, trees, and flows
add edge from "A" to "B" with weight 4.0 to g
add edge from "A" to "C" with weight 2.0 to g
add edge from "C" to "B" with weight 1.0 to g
add edge from "B" to "D" with weight 5.0 to g
add edge from "C" to "D" with weight 8.0 to g

# 1. Dijkstra shortest path
find shortest path from "A" to "D" in g using dijkstra into dijk_res
dijk_dist = item 1 of dijk_res
dijk_path = item 2 of dijk_res
say "Dijkstra dist:", dijk_dist

# 2. Bellman-Ford
find shortest paths from "A" in g using bellman ford into bf_res
bf_dist = item 1 of bf_res
say "BF dist to D:", bf_dist["D"]

# 3. Floyd-Warshall
find all pairs shortest paths in g using floyd warshall into fw_matrix
say "FW A to D:", fw_matrix["A"]["D"]

# 4. Edmonds-Karp max flow
maximum flow from "A" to "D" in g using edmonds karp into max_flow
say "Max flow:", max_flow

# 5. Connected components
find connected components in g into components
say "Component count:", count of components

# 6. Graph diameter & radius
calculate diameter of g into diam
calculate radius of g into rad
say "Diameter:", diam
say "Radius:", rad

# 7. PageRank
calculate pagerank of g with damping 0.85 into pr_ranks
val_a = pr_ranks["A"]
val_b = pr_ranks["B"]
val_c = pr_ranks["C"]
val_d = pr_ranks["D"]
rank_list = a list of val_a, val_b, val_c, val_d
say "PageRank sum:", sum of rank_list

# 8. HITS (Hubs and Authorities)
calculate hits scores of g into hits_res
hubs = item 1 of hits_res
auths = item 2 of hits_res
say "HITS A hub:", hubs["A"] > 0

# 9. Minimum Spanning Trees (Kruskal & Prim)
find minimum spanning tree in g using kruskal into mst_kruskal
find minimum spanning tree in g using prim into mst_prim
say "Kruskal edge count:", count of mst_kruskal
say "Prim edge count:", count of mst_prim

# 10. Degree distribution
calculate degree distribution of g into deg_dist
say "Out-degree distribution:", deg_dist["out_degrees"]

# 11. Graph isomorphism hash
calculate isomorphism hash of g into iso_hash
say "Isomorphism hash:", iso_hash

# 12. DAG topological sort & transitive reduction
create a research graph into dag
add edge from "1" to "2" with weight 1.0 to dag
add edge from "2" to "3" with weight 1.0 to dag
add edge from "1" to "3" with weight 1.0 to dag
topological sort of dag into topo_order
calculate transitive reduction of dag into reduced_edges

# 13. Bipartite matching (Hopcroft-Karp)
create a research graph into bg
add edge from "u1" to "v1" with weight 1.0 to bg
add edge from "u1" to "v2" with weight 1.0 to bg
add edge from "u2" to "v1" with weight 1.0 to bg
u_nodes = a list of "u1", "u2"
v_nodes = a list of "v1", "v2"
find bipartite matching in bg between u_nodes and v_nodes into match_res
match_size = item 1 of match_res

# 14. Strongly Connected Components (Tarjan)
create a research graph into scc_g
add edge from "X" to "Y" with weight 1.0 to scc_g
add edge from "Y" to "Z" with weight 1.0 to scc_g
add edge from "Z" to "X" with weight 1.0 to scc_g
add edge from "Z" to "W" with weight 1.0 to scc_g
find strongly connected components in scc_g into sccs

# 15. Eulerian circuit (Hierholzer)
create a research graph into eul_g
add edge from "p1" to "p2" with weight 1.0 to eul_g
add edge from "p2" to "p3" with weight 1.0 to eul_g
add edge from "p3" to "p1" with weight 1.0 to eul_g
find eulerian circuit in eul_g into eul_circuit

# 16. Negative cycle detection
create a research graph into neg_g
add edge from "n1" to "n2" with weight 1.0 to neg_g
add edge from "n2" to "n3" with weight -5.0 to neg_g
add edge from "n3" to "n1" with weight 2.0 to neg_g
find negative cycle in neg_g into neg_cycle
"""
    env = execute(script)
    assert env["dijk_dist"] == 8.0
    assert env["dijk_path"] == ["A", "C", "B", "D"]
    assert env["bf_dist"]["D"] == 8.0
    assert env["fw_matrix"]["A"]["D"] == 8.0
    assert env["max_flow"] == 6.0
    assert len(env["components"]) == 1
    assert env["diam"] >= 8.0
    assert env["rad"] >= 0.0
    assert 0.99 <= sum(env["pr_ranks"].values()) <= 1.01
    assert env["hubs"]["A"] > 0.0
    assert len(env["mst_kruskal"]) == 3  # 4 nodes -> 3 edges in spanning tree
    assert len(env["mst_prim"]) == 3
    assert len(env["iso_hash"]) > 0
    assert env["topo_order"] == ["1", "2", "3"]
    assert len(env["reduced_edges"]) == 2  # (1, 3) bypassed through 2
    assert env["match_size"] == 2
    assert len(env["sccs"]) == 2  # [X, Y, Z] and [W]
    assert len(env["eul_circuit"]) == 4  # p1 -> p2 -> p3 -> p1
    assert len(env["neg_cycle"]) >= 3
