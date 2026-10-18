"""
DoomScript Documentation Generator (Phase 16)
Inspects .doom files and generates static, interactive HTML documentation.
"""

import os
import re
from pathlib import Path
from typing import Optional, List, Dict, Any

def extract_file_docs(file_path: Path) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    doc = {
        "filename": file_path.name,
        "path": str(file_path),
        "description": "",
        "functions": [],
        "entities": [],
        "cli_options": [],
        "routes": [],
        "tests": []
    }

    # Extract leading comment as description
    leading_comments = []
    for line in lines:
        if line.strip().startswith("#"):
            leading_comments.append(line.strip().lstrip("#").strip())
        elif not line.strip():
            continue
        else:
            break
    doc["description"] = " ".join(leading_comments)

    for idx, line in enumerate(lines, start=1):
        s = line.strip()
        # Functions: to name with ...
        fn_m = re.match(r"^to\s+([A-Za-z_]\w*)(?:\s+with\s+(.+?))?:?$", s)
        if fn_m:
            doc["functions"].append({
                "name": fn_m.group(1),
                "params": fn_m.group(2) or "",
                "line": idx
            })
        # Entities: define entity Name with ...
        ent_m = re.match(r"^define\s+entity\s+([A-Za-z_]\w*)\s+with\s+(.+)$", s, re.IGNORECASE)
        if ent_m:
            doc["entities"].append({
                "name": ent_m.group(1),
                "fields": ent_m.group(2),
                "line": idx
            })
        # CLI Options
        opt_m = re.match(r"^option\s+([A-Za-z_]\w*)(.*)$", s, re.IGNORECASE)
        if opt_m:
            doc["cli_options"].append({"name": opt_m.group(1), "details": opt_m.group(2).strip(), "line": idx})
        # Routes: on get|post ...
        route_m = re.match(r"^on\s+(get|post|put|delete)\s+(.+?):?$", s, re.IGNORECASE)
        if route_m:
            doc["routes"].append({"method": route_m.group(1).upper(), "path": route_m.group(2), "line": idx})
        # Tests: test "..."
        test_m = re.match(r"^test\s+(.+?):?$", s, re.IGNORECASE)
        if test_m:
            doc["tests"].append({"name": test_m.group(1).strip().strip('"\''), "line": idx})

    return doc

def generate_html_docs(docs: List[Dict[str, Any]], title: str = "DoomScript Documentation") -> str:
    html = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'><title>" + title + "</title>",
        "<style>",
        "body{font-family:system-ui,-apple-system,sans-serif;max-width:1000px;margin:2rem auto;padding:0 1.5rem;line-height:1.6;color:#1e293b;background:#f8fafc;}",
        "h1{color:#0f172a;border-bottom:2px solid #e2e8f0;padding-bottom:0.5rem;}",
        "h2{color:#1e293b;margin-top:2rem;}",
        ".card{background:white;border-radius:8px;padding:1.5rem;margin:1rem 0;box-shadow:0 1px 3px rgba(0,0,0,0.1);}",
        ".badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:0.8rem;font-weight:600;margin-right:0.5rem;}",
        ".badge-fn{background:#dbeafe;color:#1d4ed8;}",
        ".badge-route{background:#dcfce7;color:#15803d;}",
        ".badge-ent{background:#fef3c7;color:#b45309;}",
        "code{background:#f1f5f9;padding:2px 6px;border-radius:4px;font-family:monospace;}",
        "</style></head><body>",
        f"<h1>{title}</h1>",
        f"<p>Generated documentation for <strong>{len(docs)}</strong> DoomScript source file(s).</p>"
    ]

    for d in docs:
        html.append(f"<div class='card'>")
        html.append(f"<h2>{d['filename']}</h2>")
        if d['description']:
            html.append(f"<p><em>{d['description']}</em></p>")

        if d["functions"]:
            html.append("<h3>Functions</h3><ul>")
            for f in d["functions"]:
                params_str = f" with {f['params']}" if f['params'] else ""
                html.append(f"<li><span class='badge badge-fn'>Function</span><code>to {f['name']}{params_str}</code> (line {f['line']})</li>")
            html.append("</ul>")

        if d["entities"]:
            html.append("<h3>Entities / Data Models</h3><ul>")
            for e in d["entities"]:
                html.append(f"<li><span class='badge badge-ent'>Entity</span><code>{e['name']}</code>: {e['fields']} (line {e['line']})</li>")
            html.append("</ul>")

        if d["routes"]:
            html.append("<h3>Web Endpoints</h3><ul>")
            for r in d["routes"]:
                html.append(f"<li><span class='badge badge-route'>{r['method']}</span><code>{r['path']}</code> (line {r['line']})</li>")
            html.append("</ul>")

        if d["tests"]:
            html.append(f"<p><strong>Tests:</strong> {len(d['tests'])} test case(s) defined.</p>")

        html.append("</div>")

    html.append("</body></html>")
    return "\n".join(html)

def build_docs(target_dir: Path, output_file: Path) -> Path:
    doom_files = list(target_dir.rglob("*.doom"))
    docs = [extract_file_docs(p) for p in doom_files]
    html_content = generate_html_docs(docs)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    return output_file
