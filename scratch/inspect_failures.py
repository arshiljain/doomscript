import json

with open("scratch/audit_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total tests: {len(data)}")
failed = [d for d in data if d["status"] != "SUCCESS"]
print(f"Total non-success: {len(failed)}")

for d in failed:
    print(f"\n[{d['id']}] {d['status']} - {d['name']}")
    print(f"  Code: {d['code']}")
    print(f"  Norm: {d['normalized_code']}")
    print(f"  Error Type: {d['error_type']}")
    print(f"  Error Message: {d['error_message']}")
    if d.get("suggestion"):
        print(f"  Suggestion: {d['suggestion']}")
    if d.get("python_leakage"):
        print(f"  Python Leakage: {d['python_leakage']}")
