"""
DoomScript Standard Runtime
Provides Record dictionaries, math utilities, file I/O, audio, graphics, networking, database, randomness, and relative time.
"""

import time
import json
import random
import sqlite3
import urllib.request
import urllib.parse
import shutil
import re
import threading
import csv
import os
import subprocess
import math
from html.parser import HTMLParser
from zoneinfo import ZoneInfo
import email.message
import smtplib
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta, date
from pathlib import Path
import sys
import statistics
from typing import Any, Dict, List, Optional, Tuple, Callable, Union

class Record(dict):
    """
    A dictionary that allows attribute-style access (e.g. record's field).
    Allows player's health = 100 and player['health'] interchangeably.
    """
    def __getattr__(self, key):
        try:
            val = self[key]
            if isinstance(val, dict) and not isinstance(val, Record):
                val = Record(val)
                self[key] = val
            return val
        except KeyError:
            raise AttributeError(f"Record has no field '{key}'") from None

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"Record has no field '{key}'") from None

from doomscript.taxonomy import (
    Table,
    RecordList,
    ValueKind,
    classify_value,
    to_table,
    to_records,
)
from doomscript.introspection import (
    explain,
    explain_domain,
    preview_of,
    summary_of,
)


def sleep(seconds):
    """Pause execution for a given number of seconds."""
    time.sleep(float(seconds))


def percent_of(pct, total):
    """Calculate percentage: e.g. 20% of 150 = 30.0"""
    return total * (pct / 100.0)


def write_file(filename, content):
    """Write text content into a file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(content))


def append_file(filename, content):
    """Append text content to the end of a file."""
    with open(filename, "a", encoding="utf-8") as f:
        f.write(str(content) + "\n")


def read_file(filename):
    """Read the entire text content of a file."""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def count_of(collection):
    """Return the length/count of a collection or string."""
    return len(collection)


# Randomness Primitives
def random_range(low, high):
    """Generate a random integer between low and high (inclusive)."""
    return random.randint(int(low), int(high))


def pick_random(collection):
    """Pick a random element from a list or collection."""
    if not collection:
        return None
    return random.choice(list(collection))


def shuffle_list(collection):
    """Shuffle a list in place."""
    if isinstance(collection, list):
        random.shuffle(collection)
    return collection


# Aggregate Functions
def agg_sum(items, *args, **kwargs):
    """Calculate sum of items."""
    return sum(items, *args, **kwargs)


def agg_avg(items):
    """Calculate average of items."""
    if not items:
        return 0.0
    return sum(items) / len(items)


def agg_field(op: str, field: str, collection):
    """Aggregate a specific field across a collection of records/dicts."""
    def _coerce_num(v):
        if isinstance(v, (int, float)):
            return v
        if isinstance(v, str):
            s = v.strip()
            try:
                return float(s) if "." in s else int(s)
            except (ValueError, TypeError):
                pass
        return v

    raw_vals = [item[field] if isinstance(item, dict) else getattr(item, field, item) for item in collection]
    vals = [_coerce_num(v) for v in raw_vals]
    if op in ("sum", "_var_sum"):
        return sum(vals)
    elif op in ("avg", "_var_avg"):
        return sum(vals) / len(vals) if vals else 0.0
    elif op in ("max", "_var_max"):
        return max(vals) if vals else 0
    elif op in ("min", "_var_min"):
        return min(vals) if vals else 0
    return vals


def agg_max(items):
    """Return highest item."""
    return max(items) if items else None


def agg_min(items):
    """Return lowest item."""
    return min(items) if items else None


def agg_first(items):
    """Return first item."""
    return items[0] if items else None


def agg_last(items):
    """Return last item."""
    return items[-1] if items else None


# Built-in SQLite Database Engine
def db_save(record, db_path, table_name):
    """Save a Record or dictionary into an SQLite database table, creating schema dynamically."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    table_name = str(table_name)
    keys = list(record.keys())
    if not keys:
        conn.close()
        return

    cols = ", ".join(f'"{k}" TEXT' for k in keys)
    cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({cols})')
    
    placeholders = ", ".join("?" for _ in keys)
    col_names = ", ".join(f'"{k}"' for k in keys)
    values = [str(record[k]) for k in keys]
    cursor.execute(f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders})', values)
    conn.commit()
    conn.close()


def db_load(db_path, table_name):
    """Load all records from an SQLite database table as a list of Records."""
    db_file = Path(str(db_path))
    if not db_file.exists():
        return []
    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(f'SELECT * FROM "{table_name}"')
        rows = cursor.fetchall()
        result = [Record(dict(row)) for row in rows]
    except Exception:
        result = []
    finally:
        conn.close()
    return result


# Audio Primitives (HolyC Style)
def beep(freq, duration_sec):
    """Emit a tone at a given frequency (Hz) for a duration in seconds."""
    freq = int(freq)
    ms = int(float(duration_sec) * 1000)
    try:
        import winsound
        winsound.Beep(max(37, min(32767, freq)), max(10, ms))
    except Exception:
        time.sleep(float(duration_sec))


def play_sound(filepath):
    """Play a sound file asynchronously."""
    try:
        import winsound
        winsound.PlaySound(str(filepath), winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass


# 2D Graphics Canvas (Tkinter powered)
class _DoomCanvasEngine:
    def __init__(self):
        self.root = None
        self.canvas = None

    def open(self, title, width, height):
        try:
            import tkinter as tk
            self.root = tk.Tk()
            self.root.title(str(title))
            self.root.geometry(f"{int(width)}x{int(height)}")
            self.canvas = tk.Canvas(self.root, width=int(width), height=int(height), bg="black")
            self.canvas.pack(fill=tk.BOTH, expand=True)
            self.root.update()
        except Exception:
            self.root = None
            self.canvas = None

    def circle(self, x, y, radius, color):
        if self.canvas and self.root:
            x, y, r = float(x), float(y), float(radius)
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline=color)
            self.root.update()

    def rectangle(self, x, y, width, height, color):
        if self.canvas and self.root:
            x, y, w, h = float(x), float(y), float(width), float(height)
            self.canvas.create_rectangle(x, y, x + w, y + h, fill=color, outline=color)
            self.root.update()

    def text(self, text_str, x, y, size, color):
        if self.canvas and self.root:
            self.canvas.create_text(float(x), float(y), text=str(text_str), font=("Arial", int(size), "bold"), fill=color)
            self.root.update()

    def clear(self):
        if self.canvas and self.root:
            self.canvas.delete("all")
            self.root.update()

    def refresh(self):
        if self.root:
            self.root.update()

_CANVAS = _DoomCanvasEngine()

def open_window(title, width, height):
    _CANVAS.open(title, width, height)

def draw_circle(x, y, radius, color):
    _CANVAS.circle(x, y, radius, color)

def draw_rectangle(x, y, width, height, color):
    _CANVAS.rectangle(x, y, width, height, color)

def draw_text(text_str, x, y, size, color):
    _CANVAS.text(text_str, x, y, size, color)

def clear_screen():
    _CANVAS.clear()

def refresh_screen():
    _CANVAS.refresh()


def _auto_cast_val(v: Any) -> Any:
    """Coerce string numerics (integers/floats) to numbers for seamless data manipulation."""
    if not isinstance(v, str):
        return v
    s = v.strip()
    if not s:
        return s
    if re.fullmatch(r"[-+]?\d+", s):
        try:
            return int(s)
        except ValueError:
            pass
    if re.fullmatch(r"[-+]?\d*\.\d+", s):
        try:
            return float(s)
        except ValueError:
            pass
    return v


def _convert_records_auto_cast(obj: Any) -> Any:
    """Recursively converts dicts into Records and auto-casts string numbers."""
    if isinstance(obj, dict):
        return Record({k.strip() if isinstance(k, str) else k: _convert_records_auto_cast(v) for k, v in obj.items() if k is not None})
    elif isinstance(obj, list):
        return [_convert_records_auto_cast(x) for x in obj]
    elif isinstance(obj, str):
        return _auto_cast_val(obj)
    return obj


# Networking (Fetch & Download)
def fetch_json(url):
    """Fetch and decode JSON from a remote URL with automatic numeric inference."""
    req = urllib.request.Request(str(url), headers={"User-Agent": "DoomScript/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return _convert_records_auto_cast(data)


def fetch_text(url):
    """Fetch raw text from a remote URL."""
    req = urllib.request.Request(str(url), headers={"User-Agent": "DoomScript/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode("utf-8")


def download_file(url, filepath):
    """Download a remote file into a local destination."""
    req = urllib.request.Request(str(url), headers={"User-Agent": "DoomScript/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp, open(filepath, "wb") as out_f:
        out_f.write(resp.read())


# Relative Time Primitives
def time_future(amount, unit_str):
    """Return a datetime timestamp in the future."""
    mult = {
        "second": 1, "seconds": 1,
        "minute": 60, "minutes": 60,
        "hour": 3600, "hours": 3600,
        "day": 86400, "days": 86400,
    }
    secs = float(amount) * mult.get(str(unit_str).lower(), 1)
    return datetime.now() + timedelta(seconds=secs)


def time_past(amount, unit_str):
    """Return a datetime timestamp in the past."""
    mult = {
        "second": 1, "seconds": 1,
        "minute": 60, "minutes": 60,
        "hour": 3600, "hours": 3600,
        "day": 86400, "days": 86400,
    }
    secs = float(amount) * mult.get(str(unit_str).lower(), 1)
    return datetime.now() - timedelta(seconds=secs)


# String Operations
def str_replace(source, needle, replacement):
    """Replace needle with replacement in source string."""
    return str(source).replace(str(needle), str(replacement))


def str_split(text, delimiter):
    """Split text by delimiter into a list."""
    return str(text).split(str(delimiter))


def str_join(items, delimiter):
    """Join a collection of items with delimiter."""
    return str(delimiter).join(str(i) for i in items)


def str_uppercase(text):
    """Convert text to uppercase."""
    return str(text).upper()


def str_lowercase(text):
    """Convert text to lowercase."""
    return str(text).lower()


def str_capitalize(text):
    """Capitalize first character of text."""
    return str(text).capitalize()


def str_trim(text):
    """Trim leading and trailing whitespace."""
    return str(text).strip()


def str_starts_with(text, prefix):
    """Check if text starts with prefix."""
    return str(text).startswith(str(prefix))


def str_ends_with(text, suffix):
    """Check if text ends with suffix."""
    return str(text).endswith(str(suffix))


def str_matches_pattern(text, pattern):
    """Check if text matches regular expression pattern."""
    return bool(re.search(str(pattern), str(text)))


# Filesystem Operations
def copy_file(src, dst):
    """Copy a file from src to dst."""
    shutil.copy2(str(src), str(dst))


def delete_file(filepath):
    """Delete a file if it exists."""
    p = Path(str(filepath))
    if p.exists() and p.is_file():
        p.unlink()


def create_dir(dirpath):
    """Create directory hierarchy."""
    Path(str(dirpath)).mkdir(parents=True, exist_ok=True)


def list_files(dirpath):
    """List filenames in a directory."""
    p = Path(str(dirpath))
    if not p.exists() or not p.is_dir():
        return []
    return [item.name for item in p.iterdir()]


def file_exists(filepath):
    """Check if a file exists on disk."""
    return Path(str(filepath)).exists()


# Concurrency Primitives
def spawn_thread(target_fn, *args):
    """Spawn a background daemon thread running target_fn with args."""
    t = threading.Thread(target=target_fn, args=args, daemon=True)
    t.start()
    return t


def wait_for_thread(thread_obj):
    """Wait for a thread or task to finish."""
    if hasattr(thread_obj, "join"):
        thread_obj.join()


# Built-in English Micro Web Server
_ROUTES = {}

def add_route(method, path, handler):
    """Register an HTTP route handler."""
    _ROUTES[(str(method).upper(), str(path))] = handler


class _DoomHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence console log noise during server execution
        pass

    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")

    def do_PUT(self):
        self._dispatch("PUT")

    def do_DELETE(self):
        self._dispatch("DELETE")

    def _dispatch(self, method):
        clean_path = self.path.split("?")[0]
        handler = _ROUTES.get((method, clean_path))
        if handler is None:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            return

        try:
            res = handler()
            if isinstance(res, (dict, list, Record)):
                payload = json.dumps(res).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            else:
                payload = str(res).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
        except Exception as exc:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(f"500 Internal Error: {exc}".encode("utf-8"))


def start_server(port, in_background=False):
    """Start the HTTP server on specified port."""
    server = HTTPServer(("0.0.0.0", int(port)), _DoomHTTPHandler)
    if in_background:
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        return server
    else:
        server.serve_forever()
        return server


def stop_server(server):
    """Stop running HTTP server."""
    if server:
        server.shutdown()
        server.server_close()


# Interactive CLI & Terminal Styling
_ANSI_COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "bold": "\033[1m",
}
_ANSI_RESET = "\033[0m"

def display_colored(text, color_name):
    """Display colored text to stdout using ANSI sequences."""
    color_code = _ANSI_COLORS.get(str(color_name).lower(), "")
    print(f"{color_code}{text}{_ANSI_RESET}")


def ask_input(prompt: str = "") -> str:
    """Reads input from user or piped stdin gracefully without EOFError."""
    try:
        if sys.stdin is None:
            return ""
        if hasattr(sys.stdin, "isatty") and sys.stdin.isatty():
            try:
                return input(prompt)
            except (EOFError, OSError):
                return ""
        else:
            # Piped / redirected input (stdin is pipe/file)
            if prompt and hasattr(sys.stdout, "write"):
                sys.stdout.write(prompt)
                if hasattr(sys.stdout, "flush"):
                    sys.stdout.flush()
            line = sys.stdin.readline()
            if not line:
                return ""
            return line.rstrip("\r\n")
    except (EOFError, OSError, ValueError):
        return ""


def pause_terminal():
    """Waits for user Enter key without raising EOFError on piped input."""
    ask_input("Press Enter to continue...")


def ask_choice(prompt: str, options: list):
    """Interactive prompt offering numbered choices from options, safe on piped input."""
    if not options:
        return ""
    if not (sys.stdin and hasattr(sys.stdin, "isatty") and sys.stdin.isatty()):
        raw = ask_input("").strip()
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx]
        for opt in options:
            if str(opt).lower() == raw.lower():
                return opt
        return options[0]

    print(prompt)
    for idx, opt in enumerate(options, 1):
        print(f"  [{idx}] {opt}")
    while True:
        try:
            sel = ask_input("Enter choice number: ").strip()
            if not sel:
                return options[0]
            sel_idx = int(sel) - 1
            if 0 <= sel_idx < len(options):
                return options[sel_idx]
        except Exception:
            pass
        print("Invalid choice, please enter a valid option number.")


# Math & Number Primitives
def math_round(value, decimals=None):
    """Round a number to specified decimal places."""
    if decimals is None or decimals == 0:
        return round(value)
    return round(value, int(decimals))


def math_clamp(value, min_val, max_val):
    """Clamp a number between minimum and maximum bounds."""
    return max(float(min_val), min(float(max_val), float(value)))


def math_mod(a, b):
    """Calculate modulo of two numbers: a mod b."""
    return a % b


def math_pow(base, exp):
    """Calculate base to the power of exp: base ** exp."""
    return base ** exp


def math_median(collection):
    """Calculate the median of a numeric collection."""
    if not collection:
        return 0
    return statistics.median(collection)


def ds_mean(xs):
    """Compute arithmetic mean of a sequence or collection."""
    if hasattr(xs, "mean") and callable(getattr(xs, "mean")):
        return float(xs.mean())
    items = list(xs)
    if not items:
        return 0.0
    return float(sum(items) / len(items))


def ds_median(xs):
    """Compute median of a sequence or collection."""
    if hasattr(xs, "median") and callable(getattr(xs, "median")):
        return xs.median()
    items = list(xs)
    if not items:
        return 0.0
    return statistics.median(items)


def ds_variance(xs):
    """Compute sample variance of a sequence or collection."""
    if hasattr(xs, "var") and callable(getattr(xs, "var")):
        return float(xs.var())
    items = list(xs)
    if len(items) <= 1:
        return 0.0
    return float(statistics.variance(items))


def ds_std_dev(xs):
    """Compute standard deviation of a sequence or collection."""
    if hasattr(xs, "std") and callable(getattr(xs, "std")):
        return float(xs.std())
    items = list(xs)
    if len(items) <= 1:
        return 0.0
    return float(statistics.stdev(items))


mean = ds_mean
median = ds_median
std_dev = ds_std_dev
stdev = ds_std_dev
stats_stdev = ds_std_dev
variance = ds_variance
stats_variance = ds_variance
stats_median = ds_median
PI = math.pi
E = math.e
INF = float("inf")



def get_field(obj, attr):
    """Safely access a field on a Record, dictionary, or object."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(str(attr))
    return getattr(obj, str(attr), None)


def to_text(val):
    """Convert any value to a string representation."""
    return str(val)


def to_number(val):
    """Convert a value or string to integer or float."""
    if isinstance(val, (int, float)):
        return val
    s = str(val).strip()
    try:
        return float(s) if "." in s else int(s)
    except (ValueError, TypeError):
        return 0


def str_title(text: str) -> str:
    """Capitalize the first letter of each word in text."""
    return str(text).title()


def date_yesterday() -> str:
    """Return yesterday's date formatted as YYYY-MM-DD."""
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def date_tomorrow() -> str:
    """Return tomorrow's date formatted as YYYY-MM-DD."""
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


def math_product(collection):
    """Calculate the product of all elements in a numeric collection."""
    if not collection:
        return 0
    res = 1
    for x in collection:
        res *= x
    return res


# ---------------------------------------------------------------------------
# Phase 2 English Standard Library Helpers
# ---------------------------------------------------------------------------

def ask_number(prompt: str = ""):
    """Prompts the user for numeric input (int or float) without EOFError."""
    raw = ask_input(prompt).strip()
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except (ValueError, TypeError):
        return 0


def ask_boolean(prompt: str = "") -> bool:
    """Prompts the user for yes/no confirmation without EOFError."""
    raw = ask_input(prompt).strip().lower()
    return raw in ("y", "yes", "true", "1")


def item_of(index, collection):
    """Access item in collection using natural 1-based indexing."""
    idx = int(index)
    if idx > 0:
        return collection[idx - 1]
    return collection[idx]


def set_item(index, collection, value):
    """Mutate item in collection using natural 1-based indexing."""
    idx = int(index)
    if idx > 0:
        collection[idx - 1] = value
    else:
        collection[idx] = value


def pop(collection):
    """Pop and return last item from collection."""
    return collection.pop()


def first_n_items(n, collection):
    """Returns the first N items of a list."""
    return collection[:int(n)]


def last_n_items(n, collection):
    """Returns the last N items of a list."""
    return collection[-int(n):]


def sorted_list(collection, *args, **kwargs):
    """Returns a newly sorted copy of the collection."""
    return sorted(collection, *args, **kwargs)


def reversed_list(collection):
    """Returns a reversed copy of the collection."""
    return list(reversed(collection))


def copy_value(val):
    """Returns a copy of the collection, record or object."""
    if hasattr(val, "copy"):
        return val.copy()
    import copy
    return copy.copy(val)


def unique_items(collection):
    """Returns items with duplicates removed while preserving order."""
    seen = []
    for item in collection:
        if item not in seen:
            seen.append(item)
    return seen


def insert_list(collection, index, item):
    """Inserts an item at 1-based index in collection."""
    idx = int(index)
    if idx > 0:
        idx -= 1
    collection.insert(idx, item)
    return collection


def range_inclusive(start, stop, step=1):
    """Inclusive range generator for English loops."""
    st = int(start)
    sp = int(stop)
    s = int(step) if step is not None else 1
    if s > 0:
        return range(st, sp + 1, s)
    else:
        return range(st, sp - 1, s)


def sort_records(collection, field: str, descending: bool = False):
    """Sorts a list of dicts/Records in-place by field."""
    def key_fn(item):
        val = item.get(field, 0) if isinstance(item, dict) else getattr(item, field, 0)
        if isinstance(val, (int, float)):
            return (0, val)
        if isinstance(val, str):
            s = val.strip()
            try:
                num = float(s) if "." in s else int(s)
                return (0, num)
            except (ValueError, TypeError):
                return (1, val)
        return (2, str(val))
    collection.sort(key=key_fn, reverse=descending)
    return collection


def group_by(collection, key_field: str):
    """Groups records by a key field into a Record of lists."""
    result = Record()
    for item in collection:
        if isinstance(item, dict):
            key = item.get(key_field, "unknown")
        else:
            key = getattr(item, key_field, "unknown")
        if key not in result:
            result[key] = []
        result[key].append(item)
    return result



def read_csv(filepath: str):
    """Reads a CSV file into a list of Record objects with automatic numeric inference."""
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = []
        for row in reader:
            parsed = {k.strip(): _auto_cast_val(v) for k, v in row.items() if k is not None}
            records.append(Record(parsed))
        return records


def write_csv(filepath: str, rows):
    """Writes a list of dicts/Records into a CSV file."""
    if not rows:
        with open(filepath, "w", encoding="utf-8") as f:
            pass
        return
    fieldnames = list(rows[0].keys())
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(r))


def append_csv(filepath: str, row):
    """Appends a single dict/Record into a CSV file."""
    p = Path(filepath)
    has_content = p.exists() and p.stat().st_size > 0
    fieldnames = list(row.keys())
    with open(filepath, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not has_content:
            writer.writeheader()
        writer.writerow(dict(row))


def parse_json(raw_text: str):
    """Parses JSON text into a Record or list of Records with automatic numeric inference."""
    data = json.loads(raw_text)
    return _convert_records_auto_cast(data)


def stringify_json(obj, indent: int = 2):
    """Converts a Python/Record object into formatted JSON string."""
    return json.dumps(obj, indent=indent, default=str)


def date_today():
    """Returns today's date formatted as YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")


def date_now():
    """Returns the current date and time formatted as YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def math_abs(value):
    """Absolute value."""
    return abs(value)


def math_sqrt(value):
    """Square root of value."""
    return math.sqrt(float(value))


def get_env_var(name: str, default: str = ""):
    """Gets an environment variable or returns default."""
    return os.environ.get(str(name), default)


def run_command(cmd: Union[str, List[str]], shell: bool = False):
    """
    Executes a system command and returns standard output.

    Security Notice:
    By default, shell=False and string commands are safely split into arguments via shlex.split
    to prevent command injection risks. Pass shell=True only when shell pipelines or redirections
    are explicitly required with trusted input.
    """
    import shlex
    if isinstance(cmd, str):
        if not shell:
            if sys.platform == "win32":
                try:
                    raw_args = shlex.split(cmd, posix=False)
                    args = [a[1:-1] if len(a) >= 2 and a[0] == a[-1] and a[0] in ('"', "'") else a for a in raw_args]
                except ValueError:
                    args = cmd.split()
            else:
                try:
                    args = shlex.split(cmd, posix=True)
                except ValueError:
                    args = cmd.split()
            res = subprocess.run(args, shell=False, capture_output=True, text=True)
        else:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    else:
        res = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    return res.stdout.strip()


def load_doom_file(filepath: str, custom_globals=None):
    """Executes another .doom file."""
    from doomscript.compiler.engine import execute
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    return execute(source, custom_globals=custom_globals)


# ---------------------------------------------------------------------------
# Phase 4 Automation & Data Batteries
# ---------------------------------------------------------------------------

class _HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self._ignore = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() in ("script", "style"):
            self._ignore = True

    def handle_endtag(self, tag):
        if tag.lower() in ("script", "style"):
            self._ignore = False
        elif tag.lower() in ("p", "br", "div", "h1", "h2", "h3", "li", "tr"):
            self.text_parts.append("\n")

    def handle_data(self, data):
        if not self._ignore:
            self.text_parts.append(data)

    def get_text(self) -> str:
        raw = "".join(self.text_parts)
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw.splitlines()]
        return "\n".join(l for l in lines if l).strip()


class _HTMLLinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            for k, v in attrs:
                if k.lower() == "href" and v:
                    self.links.append(v)


def extract_html_text(html_content: str) -> str:
    """Strips HTML tags and scripts, returning clean readable text."""
    parser = _HTMLTextExtractor()
    parser.feed(str(html_content))
    return parser.get_text()


def extract_html_links(html_content: str) -> list:
    """Extracts all href link URLs from an HTML string."""
    parser = _HTMLLinkExtractor()
    parser.feed(str(html_content))
    return parser.links


def fetch_url(url: str, method: str = "GET", headers: dict = None, json_body=None, data: str = None) -> Record:
    """
    Performs an HTTP request using urllib.request and returns a Record
    containing status, text, json, and headers.
    """
    req_headers = {"User-Agent": "DoomScript/0.6.0"}
    if headers:
        for k, v in headers.items():
            req_headers[str(k)] = str(v)

    body_bytes = None
    if json_body is not None:
        body_bytes = json.dumps(json_body).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    elif data is not None:
        body_bytes = str(data).encode("utf-8")

    req = urllib.request.Request(str(url), data=body_bytes, headers=req_headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status_code = resp.status
            content = resp.read().decode("utf-8", errors="replace")
            resp_headers = dict(resp.headers)
            parsed_json = None
            try:
                parsed_json = json.loads(content)
                if isinstance(parsed_json, dict):
                    parsed_json = Record(parsed_json)
                elif isinstance(parsed_json, list):
                    parsed_json = [Record(item) if isinstance(item, dict) else item for item in parsed_json]
            except Exception:
                pass
            return Record({
                "status": status_code,
                "text": content,
                "json": parsed_json,
                "headers": Record(resp_headers)
            })
    except urllib.error.HTTPError as e:
        err_content = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        return Record({
            "status": e.code,
            "text": err_content,
            "json": None,
            "headers": Record(dict(e.headers)) if hasattr(e, "headers") else Record()
        })
    except Exception as e:
        return Record({
            "status": 0,
            "text": str(e),
            "json": None,
            "headers": Record()
        })


def download_file_url(url: str, target_path: str) -> str:
    """Downloads a remote file to a local destination."""
    dst = Path(str(target_path))
    dst.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(str(url), headers={"User-Agent": "DoomScript/0.6.0"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(dst, "wb") as f:
        shutil.copyfileobj(resp, f)
    return str(dst)


def combine_tables(left: list, right: list, on_key: str, how: str = "inner") -> list:
    """
    Performs a relational join on two lists of dictionaries/Records.
    how options: 'inner', 'left', 'outer'.
    """
    key = str(on_key)
    style = str(how).lower()

    right_map = {}
    for r in right:
        k = r.get(key) if isinstance(r, dict) else getattr(r, key, None)
        if k is not None:
            right_map.setdefault(k, []).append(r)

    matched_right_keys = set()
    result = []

    for l in left:
        k = l.get(key) if isinstance(l, dict) else getattr(l, key, None)
        rights = right_map.get(k, [])
        if rights:
            matched_right_keys.add(k)
            for r in rights:
                merged = Record(dict(l))
                for rk, rv in (r.items() if isinstance(r, dict) else r.__dict__.items()):
                    if rk != key:
                        merged[rk] = rv
                result.append(merged)
        elif style in ("left", "outer"):
            result.append(Record(dict(l)))

    if style == "outer":
        for rk, rights in right_map.items():
            if rk not in matched_right_keys:
                for r in rights:
                    result.append(Record(dict(r)))

    return result


def send_email(to_addr: str, subject: str, body: str, from_addr: str = "doomscript@local") -> Record:
    """Sends an email or returns sent metadata."""
    host = os.environ.get("DOOM_SMTP_HOST")
    port = int(os.environ.get("DOOM_SMTP_PORT", 25))
    msg = email.message.EmailMessage()
    msg["To"] = str(to_addr)
    msg["From"] = str(from_addr)
    msg["Subject"] = str(subject)
    msg.set_content(str(body))

    if host:
        try:
            with smtplib.SMTP(host, port) as server:
                server.send_message(msg)
            return Record({"status": "SENT", "to": to_addr, "subject": subject})
        except Exception as e:
            return Record({"status": "FAILED", "error": str(e), "to": to_addr})
    else:
        return Record({"status": "SIMULATED", "to": str(to_addr), "subject": str(subject), "body": str(body)})


def date_now_in(tz_name: str) -> str:
    """Returns current date and time in a given timezone."""
    try:
        tz = ZoneInfo(str(tz_name))
        return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def next_business_day(from_date=None) -> str:
    """Calculates next business day (Monday-Friday) as YYYY-MM-DD."""
    if from_date is None:
        curr = date.today()
    elif isinstance(from_date, str):
        curr = datetime.strptime(from_date[:10], "%Y-%m-%d").date()
    else:
        curr = from_date

    curr = curr + timedelta(days=1)
    while curr.weekday() >= 5:
        curr = curr + timedelta(days=1)
    return curr.strftime("%Y-%m-%d")


def is_weekend(d=None) -> bool:
    """Checks whether date is a Saturday or Sunday."""
    if d is None:
        curr = date.today()
    elif isinstance(d, str):
        curr = datetime.strptime(d[:10], "%Y-%m-%d").date()
    else:
        curr = d
    return curr.weekday() >= 5


# ---------------------------------------------------------------------------
# PHASE 9: DESTRUCTURING & PATTERN MATCHING HELPERS
# ---------------------------------------------------------------------------

def unpack_values(keys: list, container: Any) -> list:
    """Unpacks values from a record or iterable based on requested keys/positions."""
    if isinstance(container, dict):
        return [container.get(k) for k in keys]
    elif hasattr(container, "__iter__") and not isinstance(container, (str, bytes)):
        items = list(container)
        return [items[i] if i < len(items) else None for i in range(len(keys))]
    return [None] * len(keys)


def head_of(container: Any) -> Any:
    """Returns the first item of a collection or None."""
    if hasattr(container, "__getitem__") and len(container) > 0:
        return container[0]
    return None


def tail_of(container: Any) -> list:
    """Returns the remaining items of a collection after the first item."""
    if hasattr(container, "__getitem__") and len(container) > 1:
        return list(container[1:])
    return []


# ---------------------------------------------------------------------------
# PHASE 11: DECLARATIVE CLI BUILDER HELPERS
# ---------------------------------------------------------------------------

class DoomCLI:
    def __init__(self, description=""):
        self.description = description
        self.options = []

    def set_description(self, desc):
        self.description = desc

    def add_option(self, name, default=None, opt_type=None, help_text=""):
        self.options.append({
            "name": name,
            "default": default,
            "type": opt_type,
            "help": help_text,
            "is_flag": False
        })

    def add_flag(self, name, help_text=""):
        self.options.append({
            "name": name,
            "default": False,
            "type": "boolean",
            "help": help_text,
            "is_flag": True
        })

    def parse(self, args=None):
        import argparse
        parser = argparse.ArgumentParser(description=self.description)
        for opt in self.options:
            name = opt["name"]
            flag_long = f"--{name.replace('_', '-')}"
            flag_short = f"-{name[0]}"
            if opt["is_flag"]:
                parser.add_argument(flag_short, flag_long, dest=name, action="store_true", help=opt["help"])
            else:
                kwargs = {"default": opt["default"], "help": opt["help"]}
                if opt["type"] == "number":
                    kwargs["type"] = float
                elif opt["type"] == "int":
                    kwargs["type"] = int
                parser.add_argument(flag_short, flag_long, dest=name, **kwargs)
        parsed, _ = parser.parse_known_args(args)
        return Record(**vars(parsed))

_CURRENT_CLI = DoomCLI()

def cli_set_description(desc):
    _CURRENT_CLI.set_description(desc)

def cli_add_option(name, default=None, opt_type=None, help_text=""):
    _CURRENT_CLI.add_option(name, default, opt_type, help_text)

def cli_add_flag(name, help_text=""):
    _CURRENT_CLI.add_flag(name, help_text)

def cli_parse_arguments(args=None):
    return _CURRENT_CLI.parse(args)


# ---------------------------------------------------------------------------
# PHASE 12: CONCURRENCY & BACKGROUND TASKS HELPERS
# ---------------------------------------------------------------------------

import concurrent.futures

_GLOBAL_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=16)

def spawn_background_task(fn, *args, **kwargs):
    """Spawns a callable into a background worker pool and returns a Future."""
    return _GLOBAL_POOL.submit(fn, *args, **kwargs)

def wait_background_task(task, timeout=None):
    """Waits for a background Future to complete and returns its result."""
    if hasattr(task, "result"):
        return task.result(timeout=timeout)
    return task

def wait_all_background_tasks(tasks, timeout=None):
    """Waits for multiple background tasks and returns a list of results."""
    results = []
    for t in tasks:
        if hasattr(t, "result"):
            results.append(t.result(timeout=timeout))
        else:
            results.append(t)
    return results

def timeout_call(timeout_seconds, fn, *args, **kwargs):
    """Executes a function with a timeout in seconds."""
    fut = _GLOBAL_POOL.submit(fn, *args, **kwargs)
    return fut.result(timeout=timeout_seconds)


# ---------------------------------------------------------------------------
# PHASE 14: ENGLISH AI & LLM PRIMITIVES
# ---------------------------------------------------------------------------

import urllib.request
import urllib.parse
import json as _json

def ask_ai(prompt: str, model: str = "default", system: Optional[str] = None, as_json: bool = False) -> Any:
    """
    Plain-English AI and LLM invocation using pure standard library HTTP.
    Supports Ollama, Gemini, OpenAI, or a deterministic fallback mock if no API key is set.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    # 1. Gemini REST API (if GEMINI_API_KEY configured)
    if gemini_key:
        api_model = "gemini-1.5-flash" if model in ("default", "gemini") else model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{api_model}:generateContent?key={gemini_key}"
        body = {
            "contents": [{"parts": [{"text": f"System: {system}\n\nUser: {prompt}" if system else prompt}]}]
        }
        req = urllib.request.Request(
            url,
            data=_json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = _json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return _json.loads(text) if as_json else text
        except Exception as e:
            pass

    # 2. OpenAI REST API (if OPENAI_API_KEY configured)
    if openai_key:
        api_model = "gpt-4o-mini" if model in ("default", "openai") else model
        url = "https://api.openai.com/v1/chat/completions"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        body = {"model": api_model, "messages": messages}
        req = urllib.request.Request(
            url,
            data=_json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {openai_key}"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = _json.loads(resp.read().decode("utf-8"))
                text = data["choices"][0]["message"]["content"]
                return _json.loads(text) if as_json else text
        except Exception as e:
            pass

    # 3. Deterministic / Offline Fallback Engine
    # For local test suites and zero-configuration development
    if as_json:
        return Record(response=f"AI Simulation: Processed '{prompt}'", model=model, status="ok")
    return f"AI response for: {prompt}"

def ask_ai_json(prompt: str) -> Any:
    return ask_ai(prompt, as_json=True)

def ask_ai_model(prompt: str, model: str) -> Any:
    return ask_ai(prompt, model=model)


# ---------------------------------------------------------------------------
# PHASE 15: DECLARATIVE ENGLISH DATABASE ORM & ENTITIES
# ---------------------------------------------------------------------------

import sqlite3

class _DoomORM:
    def __init__(self):
        self._schemas: Dict[str, Dict[str, str]] = {}
        self._entities: Dict[str, List[Record]] = {}
        self._next_ids: Dict[str, int] = {}

    def define(self, entity_name: str, schema: Dict[str, str]):
        self._schemas[entity_name.lower()] = schema
        if entity_name.lower() not in self._entities:
            self._entities[entity_name.lower()] = []
            self._next_ids[entity_name.lower()] = 1

    def save(self, entity_name: str, data: Dict[str, Any]) -> Record:
        ename = entity_name.lower()
        if ename not in self._entities:
            self._entities[ename] = []
            self._next_ids[ename] = 1

        rec_dict = dict(data)
        if "id" not in rec_dict or rec_dict["id"] is None:
            rec_dict["id"] = self._next_ids[ename]
            self._next_ids[ename] += 1

        rec = Record(**rec_dict)
        # Update if exists, else append
        existing_idx = None
        for i, existing in enumerate(self._entities[ename]):
            if getattr(existing, "id", None) == rec_dict["id"]:
                existing_idx = i
                break
        if existing_idx is not None:
            self._entities[ename][existing_idx] = rec
        else:
            self._entities[ename].append(rec)
        return rec

    def find_all(self, entity_name: str, filter_fn=None) -> List[Record]:
        ename = entity_name.lower()
        records = list(self._entities.get(ename, []))
        if filter_fn is not None:
            records = [r for r in records if filter_fn(r)]
        return records

    def find_first(self, entity_name: str, filter_fn=None) -> Optional[Record]:
        results = self.find_all(entity_name, filter_fn)
        return results[0] if results else None

    def delete(self, entity_name: str, filter_fn=None) -> int:
        ename = entity_name.lower()
        if ename not in self._entities:
            return 0
        original_count = len(self._entities[ename])
        if filter_fn is None:
            self._entities[ename] = []
            return original_count
        self._entities[ename] = [r for r in self._entities[ename] if not filter_fn(r)]
        return original_count - len(self._entities[ename])

_ORM = _DoomORM()

def orm_define(entity_name: str, **schema_types):
    _ORM.define(entity_name, schema_types)

def orm_save(entity_name: str, **fields):
    return _ORM.save(entity_name, fields)

def orm_find_all(entity_name: str, filter_fn=None):
    return _ORM.find_all(entity_name, filter_fn)

def orm_find_first(entity_name: str, filter_fn=None):
    return _ORM.find_first(entity_name, filter_fn)

def orm_delete(entity_name: str, filter_fn=None):
    return _ORM.delete(entity_name, filter_fn)


# ---------------------------------------------------------------------------
# PHASE 17: ENGLISH MARKDOWN & RICH DOCUMENT GENERATOR
# ---------------------------------------------------------------------------

class DoomDocument:
    def __init__(self):
        self.sections: List[Dict[str, Any]] = []

    def add_heading(self, text: str, level: int = 1):
        self.sections.append({"type": "heading", "text": str(text), "level": max(1, min(6, int(level)))})
        return self

    def add_paragraph(self, text: str):
        self.sections.append({"type": "paragraph", "text": str(text)})
        return self

    def add_bullet_list(self, items: List[Any]):
        self.sections.append({"type": "list", "items": [str(i) for i in items], "ordered": False})
        return self

    def add_table(self, headers: List[str], rows: List[List[Any]]):
        self.sections.append({"type": "table", "headers": [str(h) for h in headers], "rows": rows})
        return self

    def to_markdown(self) -> str:
        lines = []
        for s in self.sections:
            stype = s["type"]
            if stype == "heading":
                lines.append(f"{'#' * s['level']} {s['text']}\n")
            elif stype == "paragraph":
                lines.append(f"{s['text']}\n")
            elif stype == "list":
                for item in s["items"]:
                    lines.append(f"- {item}")
                lines.append("")
            elif stype == "table":
                headers = s["headers"]
                lines.append("| " + " | ".join(headers) + " |")
                lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                for row in s["rows"]:
                    lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
                lines.append("")
        return "\n".join(lines)

    def to_html(self) -> str:
        html = ["<!DOCTYPE html><html><head><meta charset='utf-8'>",
                "<style>body{font-family:system-ui,-apple-system,sans-serif;max-width:800px;margin:2rem auto;padding:0 1rem;line-height:1.6;color:#333;}",
                "table{border-collapse:collapse;width:100%;margin:1rem 0;}th,td{border:1px solid #ddd;padding:8px 12px;text-align:left;}th{background:#f4f4f4;}",
                "</style></head><body>"]
        for s in self.sections:
            stype = s["type"]
            if stype == "heading":
                html.append(f"<h{s['level']}>{s['text']}</h{s['level']}>")
            elif stype == "paragraph":
                html.append(f"<p>{s['text']}</p>")
            elif stype == "list":
                html.append("<ul>")
                for item in s["items"]:
                    html.append(f"<li>{item}</li>")
                html.append("</ul>")
            elif stype == "table":
                html.append("<table><thead><tr>")
                for h in s["headers"]:
                    html.append(f"<th>{h}</th>")
                html.append("</tr></thead><tbody>")
                for row in s["rows"]:
                    html.append("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>")
                html.append("</tbody></table>")
        html.append("</body></html>")
        return "\n".join(html)

    def save(self, file_path: str):
        content = self.to_markdown() if file_path.endswith((".md", ".txt")) else self.to_html()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

def doc_create() -> DoomDocument:
    return DoomDocument()

def doc_add_heading(doc: DoomDocument, text: str, level: int = 1):
    doc.add_heading(text, level)
    return doc

def doc_add_paragraph(doc: DoomDocument, text: str):
    doc.add_paragraph(text)
    return doc

def doc_add_table(doc: DoomDocument, headers: List[str], rows: List[List[Any]]):
    doc.add_table(headers, rows)
    return doc

def doc_add_list(doc: DoomDocument, items: List[Any]):
    doc.add_bullet_list(items)
    return doc

def doc_save(doc: DoomDocument, path: str):
    return doc.save(path)

def doc_render_markdown(doc: DoomDocument) -> str:
    return doc.to_markdown()

def doc_render_html(doc: DoomDocument) -> str:
    return doc.to_html()


# ---------------------------------------------------------------------------
# PHASE 19: ENGLISH CRON & EVENT SCHEDULING
# ---------------------------------------------------------------------------

import threading

class DoomScheduler:
    def __init__(self):
        self.tasks = []
        self._stop_event = threading.Event()
        self._threads = []

    def schedule_interval(self, seconds: float, fn, *args):
        self.tasks.append({"interval": float(seconds), "fn": fn, "args": args})

    def run_for(self, duration_seconds: float):
        start = time.time()
        last_runs = [0.0] * len(self.tasks)
        while time.time() - start < duration_seconds:
            now = time.time()
            for i, task in enumerate(self.tasks):
                if now - last_runs[i] >= task["interval"]:
                    task["fn"](*task["args"])
                    last_runs[i] = now
            time.sleep(0.01)

_SCHEDULER = DoomScheduler()

def schedule_every_seconds(seconds: float, fn, *args):
    _SCHEDULER.schedule_interval(seconds, fn, *args)

def run_scheduler_for(duration: float):
    _SCHEDULER.run_for(float(duration))


# ---------------------------------------------------------------------------
# PHASE 20: SECURE ENGLISH CRYPTOGRAPHY & SECRETS
# ---------------------------------------------------------------------------

import hashlib
import secrets
import base64
import hmac

def crypto_hash(text: str, algorithm: str = "sha256") -> str:
    """Hashes text using sha256, sha512, or md5."""
    algo = algorithm.lower().strip()
    data = str(text).encode("utf-8")
    if algo in ("sha256", "sha-256"):
        return hashlib.sha256(data).hexdigest()
    elif algo in ("sha512", "sha-512"):
        return hashlib.sha512(data).hexdigest()
    elif algo == "md5":
        return hashlib.md5(data).hexdigest()
    return hashlib.sha256(data).hexdigest()

def crypto_token(length: int = 32) -> str:
    """Generates a cryptographically secure random hexadecimal token."""
    return secrets.token_hex(int(length) // 2 or 16)

def crypto_base64_encode(text: str) -> str:
    """Encodes a string into Base64 format."""
    return base64.b64encode(str(text).encode("utf-8")).decode("utf-8")

def crypto_base64_decode(encoded: str) -> str:
    """Decodes a Base64 string back to plaintext."""
    return base64.b64decode(str(encoded).strip().encode("utf-8")).decode("utf-8")

def crypto_encrypt(text: str, secret_key: str) -> str:
    """Simple authenticated stream cipher using HMAC and XOR for stdlib encryption."""
    key = hashlib.sha256(str(secret_key).encode("utf-8")).digest()
    data = str(text).encode("utf-8")
    keystream = (key * (len(data) // len(key) + 1))[:len(data)]
    cipher_bytes = bytes([b ^ k for b, k in zip(data, keystream)])
    mac = hmac.new(key, cipher_bytes, hashlib.sha256).digest()[:8]
    return base64.b64encode(mac + cipher_bytes).decode("utf-8")

def crypto_decrypt(cipher_text: str, secret_key: str) -> str:
    """Decrypts ciphertext created with crypto_encrypt."""
    key = hashlib.sha256(str(secret_key).encode("utf-8")).digest()
    raw = base64.b64decode(str(cipher_text).encode("utf-8"))
    mac, cipher_bytes = raw[:8], raw[8:]
    expected_mac = hmac.new(key, cipher_bytes, hashlib.sha256).digest()[:8]
    if not hmac.compare_digest(mac, expected_mac):
        raise ValueError("Cryptographic verification failed: invalid key or tampered ciphertext.")
    keystream = (key * (len(cipher_bytes) // len(key) + 1))[:len(cipher_bytes)]
    decrypted_bytes = bytes([b ^ k for b, k in zip(cipher_bytes, keystream)])
    return decrypted_bytes.decode("utf-8")


# ---------------------------------------------------------------------------
# PHASE 21: STREAMING DATA & PIPELINE OPERATORS
# ---------------------------------------------------------------------------

import itertools

def pipe_pipeline(initial_val, *functions):
    """Feeds initial value through a chain of functions sequentially."""
    cur = initial_val
    for fn in functions:
        cur = fn(cur)
    return cur

def stream_file_lines(path: str):
    """Generator streaming file lines lazily."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\r\n")

def take_first_n(collection, n: int):
    """Takes first n items from a list or generator."""
    if isinstance(collection, (list, tuple)):
        return list(collection[:int(n)])
    return list(itertools.islice(collection, int(n)))

def drop_first_n(collection, n: int):
    """Drops first n items from a list or generator."""
    if isinstance(collection, (list, tuple)):
        return list(collection[int(n):])
    return list(itertools.islice(collection, int(n), None))

def batch_items(collection, batch_size: int):
    """Batches items into sublists of size batch_size."""
    bs = int(batch_size)
    items = list(collection)
    return [items[i:i + bs] for i in range(0, len(items), bs)]


# ---------------------------------------------------------------------------
# PHASE 22: BINARY & HEX DATA SERIALIZATION
# ---------------------------------------------------------------------------

import struct
import binascii

def num_to_hex(val: int) -> str:
    """Converts an integer to a hex string."""
    return hex(int(val))

def hex_to_num(hex_str: str) -> int:
    """Converts a hex string to an integer."""
    h = str(hex_str).strip()
    return int(h, 16)

def pack_numbers(numbers: List[int], fmt: str = "int32") -> bytes:
    """Packs integers into binary bytes."""
    type_code = {"int32": "i", "int16": "h", "int64": "q", "float": "f", "double": "d"}.get(fmt.lower(), "i")
    return struct.pack(f"<{len(numbers)}{type_code}", *numbers)

def unpack_numbers(buffer: bytes, fmt: str = "int32") -> List[Any]:
    """Unpacks binary bytes into a list of numbers."""
    type_code = {"int32": "i", "int16": "h", "int64": "q", "float": "f", "double": "d"}.get(fmt.lower(), "i")
    size = struct.calcsize(type_code)
    count = len(buffer) // size
    return list(struct.unpack(f"<{count}{type_code}", buffer[:count * size]))

def bytes_length(buffer: bytes) -> int:
    """Returns length of byte buffer in bytes."""
    return len(buffer)


# ---------------------------------------------------------------------------
# PHASE 23: ENGLISH CONFIGURATION MANAGER (INI, JSON, ENV)
# ---------------------------------------------------------------------------

import configparser

def config_load(file_path: str) -> Record:
    """Loads configuration from JSON or INI file into a Record."""
    p = Path(file_path)
    if not p.exists():
        return Record()
    if p.suffix in (".json", ".js"):
        with open(p, "r", encoding="utf-8") as f:
            return Record(**_json.load(f))
    elif p.suffix in (".ini", ".cfg", ".conf"):
        cp = configparser.ConfigParser()
        cp.read(p, encoding="utf-8")
        out = {}
        for section in cp.sections():
            out[section] = Record(**dict(cp.items(section)))
        return Record(**out)
    return Record()

def config_get(conf: Record, key: str, default: Any = None) -> Any:
    """Gets a nested or flat configuration property."""
    parts = key.split(".")
    cur = conf
    for part in parts:
        if isinstance(cur, Record):
            cur = getattr(cur, part, None)
        elif isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return default
        if cur is None:
            return default
    return cur

def config_set(conf: Record, key: str, value: Any):
    """Sets a configuration property."""
    setattr(conf, key, value)
    return conf

def config_save(conf: Record, file_path: str):
    """Saves a configuration record to disk."""
    p = Path(file_path)
    data = dict(conf.__dict__)
    with open(p, "w", encoding="utf-8") as f:
        _json.dump(data, f, indent=2)
    return file_path


# ---------------------------------------------------------------------------
# PHASE 24: VISUAL BENCHMARK & LATENCY PROFILER
# ---------------------------------------------------------------------------

def benchmark_block(name: str, iterations: int, fn, *args):
    """Runs a function N times and prints timing statistics."""
    latencies = []
    for _ in range(int(iterations)):
        t0 = time.perf_counter()
        fn(*args)
        t1 = time.perf_counter()
        latencies.append(t1 - t0)
    total_time = sum(latencies)
    avg_ms = (total_time / iterations) * 1000.0
    ops_per_sec = iterations / total_time if total_time > 0 else 0
    res = Record(
        name=name,
        iterations=iterations,
        total_seconds=total_time,
        average_ms=avg_ms,
        ops_per_second=ops_per_sec
    )
    print(f"[DoomBench] {name}: {iterations} ops in {total_time:.4f}s ({ops_per_sec:,.0f} ops/sec, avg {avg_ms:.3f} ms)")
    return res


# Import all Extended Runtime Features (Phases 26 through 100)
from doomscript.runtime_extended import *


# Phase 5: Data Science Verbs over pandas
def load_table(path):
    """Load a tabular file (CSV) into a pandas DataFrame."""
    import pandas as pd
    return pd.read_csv(path)


def save_table(table, path):
    """Save a table/DataFrame to a CSV file."""
    import pandas as pd
    if hasattr(table, "to_csv"):
        table.to_csv(path, index=False)
    else:
        pd.DataFrame(table).to_csv(path, index=False)


def filter_table(table, col, op, val):
    """Filter a table/DataFrame by a column condition."""
    is_list_input = isinstance(table, list)
    import pandas as pd
    if not isinstance(table, pd.DataFrame):
        table = pd.DataFrame(table)

    col = str(col).strip('"\'')
    op_str = str(op).strip().lower()
    if op_str in (">", "is greater than", "is over"):
        res = table[table[col] > val]
    elif op_str in (">=", "is at least", "is greater than or equal to"):
        res = table[table[col] >= val]
    elif op_str in ("<", "is less than", "is under"):
        res = table[table[col] < val]
    elif op_str in ("<=", "is at most", "is less than or equal to"):
        res = table[table[col] <= val]
    elif op_str in ("==", "equals", "is"):
        res = table[table[col] == val]
    elif op_str in ("!=", "is not", "isn't"):
        res = table[table[col] != val]
    else:
        res = table

    if is_list_input:
        return [Record(r) for r in res.to_dict("records")]
    return res


def sort_table(table, col, ascending=True):
    """Sort a table/DataFrame by a column."""
    is_list_input = isinstance(table, list)
    import pandas as pd
    if not isinstance(table, pd.DataFrame):
        table = pd.DataFrame(table)
    col = str(col).strip('"\'')
    res = table.sort_values(col, ascending=ascending)
    if is_list_input:
        return [Record(r) for r in res.to_dict("records")]
    return res


def group_and_agg_table(table, group_col, agg_col, func="mean"):
    """Group a table/DataFrame by a column and aggregate a metric."""
    import pandas as pd
    if not isinstance(table, pd.DataFrame):
        table = pd.DataFrame(table)
    if func in ("mean", "average", "avg"):
        return table.groupby(group_col, as_index=False)[agg_col].mean()
    elif func == "sum":
        return table.groupby(group_col, as_index=False)[agg_col].sum()
    elif func == "count":
        return table.groupby(group_col, as_index=False)[agg_col].count()
    elif func in ("min", "lowest"):
        return table.groupby(group_col, as_index=False)[agg_col].min()
    elif func in ("max", "highest"):
        return table.groupby(group_col, as_index=False)[agg_col].max()
    return table.groupby(group_col, as_index=False)[agg_col].agg(func)


def plot_table(table, x_col, y_col, kind="line", title=None):
    """Create a plot from a table/DataFrame and return the matplotlib Figure."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    if kind == "line":
        ax.plot(table[x_col], table[y_col])
    elif kind == "scatter":
        ax.scatter(table[x_col], table[y_col])
    elif kind == "bar":
        ax.bar(table[x_col], table[y_col])
    ax.set_xlabel(str(x_col))
    ax.set_ylabel(str(y_col))
    if title:
        ax.set_title(str(title))
    return fig


# ---------------------------------------------------------------------------
# Research Module Integration
# ---------------------------------------------------------------------------
from doomscript.research.backend import (
    ResearchRNG,
    ResearchSession,
    get_active_session,
    set_active_session,
)
from doomscript.research.distributions import (
    gammainc,
    gammaincc,
    betainc,
    betaincc,
    t_cdf,
    t_sf,
    f_cdf,
    f_sf,
    chi2_cdf,
    chi2_sf,
    inv_normal_cdf,
    inv_t_cdf,
    inv_chi2_cdf,
)
from doomscript.research.stats import (
    welch_t_test,
    student_t_test,
    mann_whitney_u_test,
    one_way_anova,
    chi_square_test,
    confidence_interval,
    wilson_score_interval,
    bca_bootstrap,
    adjust_p_values,
    metropolis_hastings,
    pearson_correlation,
    spearman_correlation,
    wilcoxon_signed_rank,
    fisher_exact_test,
    TestResult,
    MCMCResult,
)
from doomscript.research.graph import (
    ResearchGraph,
    dijkstra_shortest_path,
    bellman_ford,
    floyd_warshall,
    topological_sort,
    edmonds_karp_max_flow,
    NegativeEdgeWeightError,
    NegativeCycleError,
)
from doomscript.research.algorithms import (
    levenshtein_distance,
    longest_common_subsequence,
    knapsack_01,
)
from doomscript.research.autograd import Scalar, check_grad
from doomscript.research.tensor import Tensor
from doomscript.research.optim import Adam, SGDMomentum

# ---------------------------------------------------------------------------
# Grammar of Graphics Visualization Integration
# ---------------------------------------------------------------------------
from doomscript.viz import (
    PlotSpec,
    AestheticMapping,
    LayerSpec,
    FacetSpec,
    ThemeSpec,
    ScaleSpec,
    LabelSpec,
    PlotBuilder,
    explore_dataset,
    ExplorationReport,
)

def show_plot(obj):
    """Displays a plot or exploration report, or prints the object."""
    if hasattr(obj, "show"):
        return obj.show()
    print(obj)

def save_plot(obj, path, width=None, height=None, dpi=None):
    """Saves a plot or exploration report to HTML, PNG, SVG, or PDF."""
    if hasattr(obj, "save"):
        return obj.save(path, width=width, height=height, dpi=dpi)
    raise TypeError(f"Object of type {type(obj).__name__} does not support save().")


# ---------------------------------------------------------------------------
# Data Engineering Domain Integration
# ---------------------------------------------------------------------------
from doomscript.domains.data import (
    PipelineSpec,
    ValidationRule,
    DedupeStep,
    FilterStep,
    FillNaStep,
    DeriveStep,
    JoinStep,
    GroupByStep,
    SortStep,
    SinkStep,
    inspect_dataset,
    profile_dataset,
    clean_dataset,
    join_datasets,
)
from doomscript.domains.ml.runtime import (
    train_model,
    evaluate_model,
    predict_model,
    inspect_model,
    ModelContainer,
    MLModelRuntime,
    cross_validate_model,
    save_model,
    load_model,
    ml_split_data,
    ml_confusion_matrix,
    ml_classification_metrics,
    ml_roc_auc_score,
    ml_mean_squared_error,
    ml_r2_score,
    ml_one_hot_encode,
    ml_knn_classifier,
    ml_decision_stump,
    ml_gaussian_naive_bayes,
    ml_bernoulli_naive_bayes,
    ml_kmeans_clustering,
    ml_pca_transform,
    ml_log_loss,
    ml_brier_score,
    ml_f1_score,
    ml_precision_recall,
    ml_polynomial_features,
    ml_target_encode,
    ml_cosine_decay_lr,
    ml_train_val_test_split,
    ml_one_class_anomaly_score,
    ml_silhouette_score_sample,
    ml_hinge_loss,
    ml_learning_curve_points,
    ml_exponential_moving_average_weights,
    ml_gradient_clip_norm,
    MLPClassifier,
    MLPRegressor,
    CARTDecisionTree,
    GBDTModel,
    IsolationForestModel,
    ml_train_mlp,
    ml_train_cart,
    ml_train_gbdt,
    ml_train_isolation_forest,
)

def execute_data_ir(spec):
    import sys
    from doomscript.domains.data.runtime import DataPipelineRuntime
    from doomscript.domains.registry import get_domain_registry
    if isinstance(spec, str):
        spec = get_domain_registry().get_spec(spec)
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    res = DataPipelineRuntime().execute_pipeline(spec, scope)
    for k, v in scope.items():
        target_env[k] = v
    return res


def execute_ml_ir(spec):
    import sys
    from doomscript.domains.ml.runtime import MLModelRuntime
    from doomscript.domains.registry import get_domain_registry
    if isinstance(spec, str):
        spec = get_domain_registry().get_spec(spec)
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    res = MLModelRuntime().execute_ir(spec, scope)
    for k, v in scope.items():
        target_env[k] = v
    return res


from doomscript.domains.db.runtime import (
    execute_parameterized_query,
    inspect_table_schema,
    execute_raw_sql,
    get_db_runtime,
    db_transaction,
    db_connect,
    db_inspect_schema,
    db_upsert_record,
    db_optimize,
    db_backup,
    db_truncate_table,
    db_count_rows_where,
    db_create_index,
    WALCrashRecovery,
    CostBasedQueryOptimizer,
    SnapshotIsolationMVCC,
    db_wal_create,
    db_mvcc_create,
    db_drop_index,
    db_add_column,
    db_drop_column_sqlite,
    db_vacuum,
    db_analyze,
    db_list_tables,
    db_list_views,
    db_list_indices,
    db_table_exists,
    db_bulk_insert,
    db_export_table_to_csv,
    db_import_csv_to_table,
    db_get_foreign_keys,
    db_check_foreign_key_integrity,
    db_export_ddl,
    db_table_column_types,
    db_database_size_bytes,
    db_count_distinct_values,
    db_clone_table_schema,
)

def execute_db_ir(spec):
    import sys
    from doomscript.domains.db.runtime import get_db_runtime
    from doomscript.domains.registry import get_domain_registry
    if isinstance(spec, str):
        spec = get_domain_registry().get_spec(spec)
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    res = get_db_runtime().execute_query_spec(spec, scope)
    for k, v in scope.items():
        target_env[k] = v
    return res


def insert_rows(table_name, data):
    import sys
    caller_frame = sys._getframe(1)
    scope = dict(caller_frame.f_globals)
    scope.update(caller_frame.f_locals)
    return get_db_runtime().insert_rows(table_name, data, scope)


from doomscript.domains.net.runtime import (
    NetRuntime,
    HttpResponseContainer,
    execute_http_request,
    inspect_response,
    parse_response_content,
    save_response_content,
    set_mutating_requests_allowed,
    is_mutating_requests_allowed,
    net_ping_host,
    net_resolve_dns,
    net_check_port,
    net_create_basic_auth,
    net_create_bearer_auth,
    net_is_connected,
    net_cidr_to_netmask,
    net_ip_in_subnet,
    net_expand_cidr_range,
    net_is_valid_ipv4,
    net_is_valid_ipv6,
    net_format_mac_address,
    net_whois_domain,
    net_http_status_message,
    net_build_query_string,
    net_parse_url_components,
    net_exponential_backoff_delay,
    net_check_multiple_ports,
    net_reverse_dns_lookup,
    net_generate_multipart_boundary,
    net_encode_basic_auth_header,
    net_decode_basic_auth_header,
    net_parse_http_headers,
    net_format_http_headers,
    net_is_private_ip,
    net_download_file,
)

def execute_net_ir(spec):
    import sys
    from doomscript.domains.net.runtime import NetRuntime
    from doomscript.domains.registry import get_domain_registry
    if isinstance(spec, str):
        spec = get_domain_registry().get_spec(spec)
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    res = NetRuntime().execute_workflow(spec, scope)
    for k, v in scope.items():
        target_env[k] = v
    return res


from doomscript.domains.sim.runtime import (
    SimRuntime,
    summarize_metric,
    summarize_uncertainty,
    sample_distribution,
    DiscreteEventQueueEngine,
    NelderMeadOptimizer,
    run_trials as _sim_run_trials,
    sweep_parameter as _sim_sweep_parameter,
    sim_random_walk,
    sim_exponential,
    sim_poisson,
    sim_monte_carlo_pi,
    sim_roll_dice,
    sim_coin_tosses,
    sim_markov_chain_step,
    sim_markov_chain_walk,
    sim_sample_geometric,
    sim_sample_binomial,
    sim_sample_triangular,
    sim_bootstrap_mean_ci,
    sim_permutation_test,
    sim_mm1_queue,
    sim_wiener_process,
    sim_bernoulli_trial,
    sim_sample_lognormal,
    sim_monte_carlo_integral,
    sim_estimate_expected_value,
    sim_birthday_paradox_prob,
    sim_coupon_collector_estimate,
    sim_shuffle_deck,
    sim_draw_cards,
    sim_sample_weibull,
    sim_generate_synthetic_timeline,
    sim_survival_rate_kaplan_meier,
)
from doomscript.domains.sim.spec import OptimizationSpec, TrialsSpec, SweepSpec

def execute_sim_ir(spec):
    import sys
    from doomscript.domains.sim.runtime import SimRuntime
    from doomscript.domains.registry import get_domain_registry
    if isinstance(spec, str):
        spec = get_domain_registry().get_spec(spec)
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    res = SimRuntime().execute_ir(spec, scope)
    for k, v in scope.items():
        target_env[k] = v
    return res


def run_trials(sim_name, trials=100, seed=42):
    import sys
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    return _sim_run_trials(sim_name, trials=trials, seed=seed, scope=scope)


def sweep_parameter(sim_name, param, values, trials_per_value=5, seed=42):
    import sys
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    return _sim_sweep_parameter(
        sim_name, param, values, trials_per_value=trials_per_value, seed=seed, scope=scope
    )


def optimize_function(fn_name, initial_guess=None):
    import sys
    from doomscript.domains.sim.runtime import SimRuntime
    from doomscript.domains.sim.spec import OptimizationSpec
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    spec = OptimizationSpec(objective=fn_name, initial_guess=initial_guess or [0.0])
    return SimRuntime().execute_optimization(spec, scope)


from doomscript.domains.dsa.runtime import (
    DsaRuntime,
    run_benchmark,
    fit_complexity,
    profile_memory_of_function as _prof_mem,
)
from doomscript.domains.dsa.spec import BenchmarkSpec

def analyze_complexity(fn_name, input_sizes=None):
    import sys
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    spec = BenchmarkSpec(fn_name=fn_name, input_sizes=input_sizes or [100, 500, 1000, 2000])
    return run_benchmark(spec, scope)


def run_benchmark_with_sizes(fn_name, sizes):
    import sys
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    spec = BenchmarkSpec(fn_name=fn_name, input_sizes=sizes)
    return run_benchmark(spec, scope)


def profile_memory_of_function(fn_name, input_expr):
    import sys
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    return _prof_mem(fn_name, input_expr, scope)


def execute_dsa_ir(spec):
    import sys
    from doomscript.domains.dsa.runtime import DsaRuntime
    from doomscript.domains.registry import get_domain_registry
    if isinstance(spec, str):
        spec = get_domain_registry().get_spec(spec)
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    res = DsaRuntime().execute_ir(spec, scope)
    for k, v in scope.items():
        target_env[k] = v
    return res


def run_dsa_benchmark(fn_name, input_sizes, repeat=3, generator="sorted_integers", measure_memory=True):
    """Executes a DSA benchmark against the caller's scope and returns the ComplexityReport dict."""
    import sys
    from doomscript.domains.dsa.spec import BenchmarkSpec
    from doomscript.domains.dsa.runtime import run_benchmark
    spec = BenchmarkSpec(
        fn_name=fn_name,
        input_sizes=input_sizes,
        repeat=repeat,
        generator=generator,
        measure_memory=measure_memory,
    )
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    return run_benchmark(spec, scope)


from doomscript.domains.dsa.runtime import (
    ListNode,
    TreeNode,
    trace_recursion,
    DsaHeap,
    dsa_create_heap,
    dsa_create_deque,
    dsa_peek_min,
    dsa_peek_max,
    dsa_peek_left,
    dsa_pop_right,
    dsa_push_left,
    dsa_create_grid,
    dsa_is_inside_grid,
    dsa_connected_components_grid,
    dsa_count_connected_components_grid,
    DsaGraph,
    dsa_build_graph,
    dsa_graph_has_cycle,
    dsa_graph_topological_sort,
    dsa_graph_shortest_path,
    dsa_graph_connected_components,
    dsa_memoize,
    dsa_merge_intervals,
    dsa_intersect_intervals,
    dsa_frequency_map,
    dsa_sliding_window_max,
    DsaTrie,
    dsa_create_trie,
    dsa_trie_insert,
    dsa_trie_contains,
    dsa_trie_starts_with,
    dsa_trie_words_with_prefix,
    DsaDisjointSet,
    dsa_create_disjoint_set,
    dsa_dsu_union,
    dsa_dsu_find,
    dsa_dsu_connected,
    dsa_dsu_count,
    dsa_build_binary_tree,
    dsa_level_order,
    dsa_preorder,
    dsa_inorder,
    dsa_postorder,
    dsa_tree_max_depth,
    dsa_invert_binary_tree,
    dsa_binary_search,
    dsa_lower_bound,
    dsa_upper_bound,
    dsa_next_greater_elements,
    dsa_next_smaller_elements,
    dsa_previous_greater_elements,
    dsa_permutations,
    dsa_combinations,
    dsa_power_set,
    dsa_build_linked_list,
    dsa_reverse_linked_list,
    dsa_linked_list_has_cycle,
    dsa_linked_list_to_list,
    dsa_max_subarray_sum,
    dsa_max_subarray,
    dsa_prefix_sums,
    dsa_range_sum,
    dsa_prefix_sums_2d,
    dsa_query_range_sum_2d,
    dsa_find_pair_sum,
    dsa_find_triplets_sum,
    dsa_minimum_spanning_tree,
    dsa_minimum_spanning_tree_weight,
    dsa_solve_knapsack_01,
    dsa_min_coins,
    dsa_coin_change_ways,
    dsa_kmp_search,
    dsa_longest_palindromic_substring,
    dsa_is_palindrome,
    DsaSegmentTree,
    dsa_create_segment_tree,
    dsa_segment_tree_query,
    dsa_segment_tree_update,
    DsaFenwickTree,
    dsa_create_fenwick_tree,
    dsa_fenwick_prefix_sum,
    dsa_fenwick_update,
    dsa_reservoir_sample,
    dsa_lcs,
    dsa_correlation,
    dsa_linear_regression,
    dsa_moving_median,
    dsa_percentile,
    dsa_z_score_normalize,
    dsa_min_max_scale,
    dsa_empirical_cdf,
    dsa_trie_create,
    dsa_trie_insert,
    dsa_trie_search,
    dsa_trie_starts_with,
    dsa_dsu_create,
    dsa_dsu_find,
    dsa_dsu_union,
    dsa_lru_create,
    dsa_lru_get,
    dsa_lru_put,
    dsa_binary_search_left,
    dsa_binary_search_right,
    dsa_quickselect,
    dsa_kadane_2d,
    dsa_count_inversions,
    dsa_next_permutation,
    dsa_prev_permutation,
    dsa_rabin_karp_search,
    dsa_manacher,
    dsa_tarjan_bridges,
    AVLTree,
    AVLNode,
    dsa_avl_create,
    dsa_avl_insert,
    dsa_avl_delete,
    dsa_avl_contains,
    dsa_avl_inorder,
    dsa_avl_height,
    SuffixAutomaton,
    dsa_suffix_automaton_create,
    dsa_sam_contains_substring,
    dsa_sam_distinct_substrings,
    dsa_sam_longest_common_substring,
    AhoCorasick,
    dsa_aho_corasick_create,
    dsa_aho_corasick_search,
    Treap,
    TreapNode,
    dsa_treap_create,
    dsa_treap_insert,
    dsa_treap_contains,
    dsa_treap_to_list,
    DinicMaxFlow,
    dsa_dinic_max_flow,
)

from doomscript.domains.data.runtime import (
    data_pivot_table,
    data_melt_table,
    data_fill_missing,
    data_drop_duplicates,
    data_stratified_sample,
    data_rolling_mean,
    data_explode_column,
    data_merge_tables,
    data_rank_column,
    data_lag_column,
    data_lead_column,
    data_cumulative_sum,
    data_cumulative_max,
    data_cumulative_min,
    data_coalesce_columns,
    data_multi_sort,
    data_cross_join,
    data_validate_schema,
    data_rename_columns,
    data_clip_column,
    data_format_date_column,
    data_string_trim,
    data_string_upper,
    data_string_lower,
    data_fill_null_forward,
    data_fill_null_backward,
    data_extract_year,
    data_sample_fraction,
    ColumnarTable,
    data_to_columnar,
    columnar_to_records,
    data_fuzzy_join,
    data_pivot_advanced,
    data_unpivot_melt,
    data_json_explode,
    data_window_rolling,
    RollingAggregator,
    RelationalJoinEngine,
    PivotTableEngine,
    data_relational_join,
    data_rolling_aggregate,
)

from doomscript.domains.nlp.runtime import (
    clean_text,
    tokenize_text,
    extract_ngrams,
    analyze_sentiment,
    calculate_tfidf,
    extract_entities,
    NLPRuntime,
    nlp_extractive_summary,
    nlp_remove_stopwords,
    nlp_word_frequencies,
    nlp_text_similarity,
    nlp_jaccard_similarity,
    nlp_extract_keywords,
    nlp_extract_matches,
    nlp_bm25_score,
    nlp_levenshtein_distance,
    nlp_hamming_distance,
    nlp_stem_porter,
    nlp_soundex,
    nlp_metaphone,
    nlp_rouge_l,
    nlp_bleu_score,
    nlp_cosine_similarity_tf,
    nlp_expand_contractions,
    nlp_mask_sensitive_entities,
    nlp_readability_flesch,
    nlp_readability_gunning_fog,
    nlp_syllable_count,
    nlp_sentence_split,
    nlp_pos_tag_rule_based,
    nlp_sentiment_vader_heuristic,
    nlp_character_ngrams,
    nlp_collocations,
    nlp_word_wrap,
    BPETokenizer,
    HMMPOSTagger,
    Word2VecSimple,
    TextRankSummarizer,
)

def execute_nlp_ir(spec):
    import sys
    from doomscript.domains.nlp.runtime import NLPRuntime
    from doomscript.domains.registry import get_domain_registry
    if isinstance(spec, str):
        spec = get_domain_registry().get_spec(spec)
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    res = NLPRuntime().execute_ir(spec, scope)
    for k, v in scope.items():
        target_env[k] = v
    return res


from doomscript.domains.geo.runtime import (
    point,
    polygon,
    distance_between,
    is_point_in_polygon,
    bounding_box,
    spatial_join,
    to_geojson,
    GeoRuntime,
    geo_haversine_distance,
    geo_bounding_box_contains,
    geo_centroid,
    geo_polygon_area,
    geo_to_geojson_point,
    geo_nearest_coordinate,
    geo_encode_geohash,
    geo_decode_geohash,
    geo_initial_bearing,
    geo_final_bearing,
    geo_destination_point,
    geo_midpoint,
    geo_cross_track_distance,
    geo_bounding_box_intersection,
    geo_bounding_box_union,
    geo_convex_hull_graham,
    geo_point_to_line_distance,
    geo_simplify_douglas_peucker,
    geo_to_geojson_polygon,
    geo_to_geojson_feature_collection,
    geo_polygon_perimeter,
    geo_buffer_point_circle,
    geo_utm_zone_number,
    geo_rhumb_line_distance,
    geo_rhumb_line_bearing,
)

def execute_geo_ir(spec):
    import sys
    from doomscript.domains.geo.runtime import GeoRuntime
    from doomscript.domains.registry import get_domain_registry
    if isinstance(spec, str):
        spec = get_domain_registry().get_spec(spec)
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    res = GeoRuntime().execute_ir(spec, scope)
    for k, v in scope.items():
        target_env[k] = v
    return res


from doomscript.domains.opt.runtime import (
    solve_linear_program as _opt_solve_lp,
    SimplexSolver,
    parse_linear_expression,
    parse_constraint,
    OptRuntime,
    opt_minimize_1d,
    opt_grid_search,
    opt_fractional_knapsack,
    opt_activity_selection,
    opt_gradient_descent_step,
    opt_bisection_root,
    opt_simulated_annealing,
    opt_golden_section_search,
    opt_knapsack_01_dp,
    opt_longest_increasing_subsequence,
    opt_coin_change_minimum,
    opt_coin_change_combinations,
    opt_job_scheduling_deadline,
    opt_huffman_encoding,
    opt_matrix_chain_multiplication,
    opt_levenshtein_alignment,
    opt_subset_sum_exists,
    opt_subset_sum_find,
    opt_rod_cutting,
    opt_two_opt_tsp,
    opt_linear_interpolation,
    opt_weighted_interval_scheduling,
    opt_pareto_frontier,
    opt_hungarian_assignment,
    opt_binary_search_peak_1d,
)

def solve_linear_program(spec_or_name):
    import sys
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    return _opt_solve_lp(spec_or_name, scope=scope)

def execute_opt_ir(spec):
    import sys
    from doomscript.domains.opt.runtime import OptRuntime
    from doomscript.domains.registry import get_domain_registry
    if isinstance(spec, str):
        spec = get_domain_registry().get_spec(spec)
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    res = OptRuntime().execute_ir(spec, scope)
    for k, v in scope.items():
        target_env[k] = v
    return res


from doomscript.domains.agent.runtime import (
    Agent,
    AgentTeam,
    create_agent,
    create_team,
    ask_agent,
    tell_agent,
    clear_agent_memory,
    agent_memory,
    run_team,
    execute_agent_ir,
    agent_broadcast_message,
    agent_consensus_vote,
    agent_prioritize_tasks,
    agent_dispatch_task,
    agent_aggregate_responses,
    agent_filter_memory,
    agent_evaluate_response_quality,
    agent_format_chat_history,
    agent_summarize_memory,
    agent_route_task_by_keywords,
    agent_retry_with_backoff,
    agent_validate_json_output,
    agent_extract_action_calls,
    agent_chain_of_thought_step,
    agent_calculate_consensus_agreement,
    agent_debate_round,
    agent_plan_task_breakdown,
    agent_filter_memory_by_date,
    agent_merge_agent_memories,
    agent_register_dynamic_tool,
    agent_inspect_available_tools,
    agent_set_system_persona,
    agent_audit_conversation_safety,
    agent_count_conversation_turns,
    agent_export_chat_transcript,
    ReActAgent,
    TreeOfThoughts,
    ToTNode,
    MultiAgentDebate,
    agent_react_run,
    agent_tree_of_thoughts_search,
    agent_run_debate,
)

from doomscript.domains.image.runtime import (
    DoomImage,
    open_image,
    create_blank_image,
    image_dimensions,
    image_width,
    image_height,
    resize_image,
    crop_image,
    rotate_image,
    flip_image,
    filter_image,
    adjust_image,
    draw_on_image,
    save_image,
    execute_image_ir,
    image_to_grayscale,
    image_blur,
    image_resize,
    image_crop_box,
    image_rotate,
    image_adjust_brightness,
    image_histogram,
    image_sobel_edge_detection,
    image_threshold_binarize,
    image_sharpen,
    image_invert_colors,
    image_adjust_contrast,
    image_split_channels,
    image_merge_channels,
    image_apply_sepia,
    image_flip_horizontal,
    image_flip_vertical,
    image_color_vignette,
    image_pad_borders,
    image_compute_mean_color,
    image_crop_center,
    image_gamma_correction,
    image_emboss,
    image_posterize,
    image_mosaic_pixelate,
    image_blend_overlay,
    image_difference,
    image_canny_edge_detector,
    image_otsu_threshold,
    image_bilateral_filter,
    image_hough_lines,
    GeometricWarp,
    MorphologicalOps,
    ColorQuantizer,
    image_warp_affine,
    image_morphology,
    image_quantize_palette,
)

from doomscript.domains.web.runtime import (
    WebPage,
    open_webpage,
    parse_html,
    webpage_title,
    webpage_text,
    extract_web_links,
    extract_web_table,
    download_web_media,
    execute_web_ir,
    DOMElement,
    CSSSelectorEngine,
    RFC6265CookieJar,
    web_css_select,
    web_cookie_jar,
    web_select_all,
    web_extract_tables,
    web_parse_query_params,
    web_build_url,
    web_strip_tags,
    web_extract_meta_tags,
    web_response_is_successful,
    web_extract_images,
    web_extract_forms,
    web_encode_form_data,
    web_decode_form_data,
    web_parse_sitemap_xml,
    web_parse_robots_txt,
    web_canonicalize_url,
    web_extract_meta_description,
    web_extract_headings,
    web_check_ssl_expiry,
    web_parse_cookie_header,
    web_build_cookie_header,
    web_extract_json_ld,
    web_strip_query_params,
    web_count_element_tags,
    web_extract_text_by_class,
    web_extract_element_by_id,
    web_parse_content_type,
    web_is_valid_url,
    web_generate_curl_command,
)

from doomscript.domains.audio.runtime import (
    DoomAudio,
    load_audio,
    create_blank_audio,
    audio_duration,
    trim_audio,
    fade_audio,
    adjust_audio_volume,
    combine_audio,
    save_audio,
    execute_audio_ir,
    audio_generate_sine,
    audio_normalize,
    audio_fade_in,
    audio_reverse,
    audio_concatenate,
    audio_generate_square,
    audio_generate_sawtooth,
    audio_generate_triangle,
    audio_generate_white_noise,
    audio_adjust_gain_db,
    audio_trim_silence,
    audio_apply_fade_out,
    audio_mix_tracks,
    audio_pan_stereo,
    audio_low_pass_filter,
    audio_high_pass_filter,
    audio_peak_amplitude,
    audio_rms_energy,
    audio_zero_crossing_rate,
    audio_clip_samples,
    audio_loop_track,
    audio_delay_echo,
    audio_time_stretch_naive,
    audio_generate_silence,
    audio_fft,
    audio_ifft,
    audio_stft_spectrogram,
    audio_mel_spectrogram,
    audio_mfcc,
    audio_biquad_filter,
    PolyphonicSynth,
    YINPitchDetector,
    ParametricEQ,
    audio_poly_synth_render,
    audio_yin_pitch,
    audio_parametric_eq,
)

from doomscript.domains.finance.runtime import (
    fetch_stock_prices,
    moving_average,
    relative_strength_index,
    calculate_daily_returns,
    calculate_sharpe_ratio,
    backtest_strategy,
    execute_finance_ir,
    finance_analytical_greeks,
    finance_binomial_price,
    finance_bollinger_bands,
    finance_rsi,
    finance_macd,
    finance_sharpe_ratio,
    finance_maximum_drawdown,
    finance_value_at_risk,
    finance_cagr,
    fin_vwap,
    fin_stochastic_oscillator,
    fin_sortino_ratio,
    fin_treynor_ratio,
    fin_calmar_ratio,
    fin_beta,
    fin_alpha,
    fin_black_scholes_call,
    fin_black_scholes_put,
    fin_keltner_channels,
    fin_average_true_range,
    fin_williams_r,
    fin_money_flow_index,
    fin_portfolio_rebalance,
    fin_twap,
    fin_donchian_channels,
    fin_information_ratio,
    fin_drawdown_series,
    fin_implied_volatility_bisection,
    fin_var_historical,
    fin_black_litterman,
    fin_var_cvar_monte_carlo,
    fin_hull_white_trinomial,
    fin_ichimoku_cloud,
)

from doomscript.domains.graph.runtime import (
    DoomGraph,
    create_graph,
    add_graph_node,
    add_graph_edge,
    graph_shortest_path,
    graph_pagerank,
    graph_degrees,
    graph_communities,
    execute_graph_ir,
    graph_degree_centrality,
    graph_betweenness_centrality,
    graph_closeness_centrality,
    graph_is_bipartite,
    graph_find_eulerian_path,
    graph_strongly_connected_components,
    graph_diameter,
    graph_eigenvector_centrality,
    graph_dijkstra_shortest_path,
    graph_bellman_ford,
    graph_floyd_warshall,
    graph_kruskal_mst,
    graph_prim_mst,
    graph_articulation_points,
    graph_bipartite_check,
    graph_max_flow_edmonds_karp,
    graph_radius,
    graph_clustering_coefficient,
    graph_transitivity,
    graph_density,
    graph_degree_histogram,
    graph_jaccard_similarity,
    graph_find_articulation_points,
    graph_jaccard_coefficient,
    graph_average_clustering_coefficient,
    graph_find_bridges,
    graph_eccentricity,
    graph_center,
    graph_is_tree,
    graph_transitive_closure,
    graph_k_core,
    graph_laplacian_matrix,
    graph_bron_kerbosch_cliques,
    graph_louvain_communities,
    graph_tarjan_scc,
    graph_mst,
)

from doomscript.domains.office.runtime import (
    DoomSpreadsheet,
    DoomWordDocument,
    create_spreadsheet,
    add_spreadsheet_row,
    add_spreadsheet_rows,
    save_spreadsheet,
    create_word_document,
    add_document_heading,
    add_document_paragraph,
    save_word_document,
    execute_office_ir,
    office_count_worksheets,
    office_extract_text,
    office_add_worksheet,
    office_markdown_to_sections,
    office_merge_pdfs,
    office_count_pages,
    office_append_table_to_sheet,
    office_calculate_sheet_summary,
    office_detect_csv_delimiter,
    office_read_csv_header,
    office_create_table_in_document,
    office_add_bulleted_list,
    office_add_numbered_list,
    office_set_spreadsheet_cell,
    office_get_spreadsheet_cell,
    office_find_replace_in_document,
    office_list_worksheet_names,
    office_delete_worksheet,
    office_rename_worksheet,
    office_sort_spreadsheet_by_column,
    office_filter_spreadsheet_rows,
    office_export_sheet_to_json,
    office_import_json_to_sheet,
    office_count_words_in_document,
    office_count_characters_in_document,
    office_extract_document_metadata,
    SpreadsheetFormulaEngine,
    CSVDialectSniffer,
    office_eval_spreadsheet,
    office_sniff_csv,
)

from doomscript.domains.cloud.runtime import (
    CloudBucket,
    connect_to_bucket,
    upload_cloud_file,
    download_cloud_file,
    list_cloud_files,
    generate_cloud_signed_url,
    execute_cloud_ir,
    cloud_list_prefix,
    cloud_sync_directory,
    cloud_file_metadata,
    cloud_file_exists,
    cloud_delete_matching,
    cloud_bucket_size,
    cloud_copy_object,
    cloud_generate_presigned_put_url,
    cloud_verify_md5_checksum,
    cloud_verify_sha256_checksum,
    cloud_set_object_tags,
    cloud_get_object_tags,
    cloud_batch_delete_keys,
    cloud_filter_files_by_size,
    cloud_filter_files_by_date,
    cloud_create_directory_marker,
    cloud_move_object,
    cloud_mirror_buckets,
    cloud_archive_stale_files,
    cloud_export_bucket_manifest,
    cloud_diff_buckets,
    cloud_count_objects_by_extension,
    cloud_read_object_text,
    cloud_write_object_text,
    cloud_get_storage_class,
    cloud_set_storage_class,
    MultipartUploadManager,
    ContentAddressableStorage,
    BucketLifecycleEngine,
    cloud_multipart_initiate,
    cloud_cas_put,
    cloud_evaluate_lifecycle,
)

from doomscript.domains.research.runtime import (
    research_topological_sort,
    research_dijkstra_shortest_path,
    research_bellman_ford,
    research_floyd_warshall_all_pairs,
    research_edmonds_karp_max_flow,
    research_hopcroft_karp_bipartite_matching,
    research_tarjan_strongly_connected,
    research_kruskal_minimum_spanning_tree,
    research_prim_minimum_spanning_tree,
    research_graph_diameter,
    research_graph_radius,
    research_connected_components,
    research_pagerank,
    research_hits_algorithm,
    research_eulerian_circuit_hierholzer,
    research_graph_isomorphism_hash,
    research_transitive_reduction,
    research_find_negative_cycle,
    research_degree_distribution,
    SVDDecomposition,
    RungeKuttaFehlberg,
    LevenbergMarquardt,
    research_svd,
    research_rkf45_solve,
    research_levenberg_marquardt,
)

from doomscript.domains.bio.runtime import (
    bio_gc_content,
    bio_transcribe,
    bio_reverse_complement,
    bio_translate,
    bio_find_orfs,
    bio_kmer_counts,
    bio_find_motif,
    bio_molecular_weight,
    bio_needleman_wunsch,
    bio_smith_waterman,
    bio_parse_fasta,
    execute_bio_ir,
    SequenceAligner,
    FMIndexBWT,
    PhylogeneticTreeNJ,
    bio_affine_align,
    bio_fm_index_search,
    bio_neighbor_joining_tree,
)
bio_transcribe_dna = bio_transcribe
bio_translate_rna = bio_translate

from doomscript.domains.physics.runtime import (
    physics_projectile_trajectory,
    physics_projectile_range,
    physics_drag_trajectory,
    physics_check_aabb_collision,
    physics_check_sat_collision,
    physics_harmonic_oscillator,
    physics_orbital_velocity,
    physics_escape_velocity,
    physics_create_pid,
    physics_update_pid,
    physics_kinetic_energy,
    execute_physics_ir,
    BarnesHutNode,
    BarnesHutNBody,
    ImpulseCollision2D,
    VanDerWaalsGas,
    physics_barnes_hut_step,
    physics_resolve_collision,
    physics_van_der_waals_pressure,
)
physics_trajectory = physics_projectile_trajectory
physics_ballistic_range = physics_projectile_range
physics_pid_create = physics_create_pid
physics_pid_update = physics_update_pid
physics_aabb_collision = physics_check_aabb_collision
physics_sat_polygon_collision = physics_check_sat_collision

from doomscript.domains.sec.runtime import (
    sec_entropy,
    sec_audit_password,
    sec_caesar_cipher,
    sec_caesar_crack,
    sec_vigenere_cipher,
    sec_vigenere_encode,
    sec_vigenere_decode,
    sec_jwt_verify,
    sec_frequency_analysis,
    sec_xor_cipher,
    sec_decode_jwt,
    sec_verify_jwt,
    sec_hexdump,
    sec_cvss_score,
    sec_parse_banner,
    execute_sec_ir,
    ShamirSecretSharing,
    TOTPGenerator,
    Secp256k1Curve,
)
sec_password_entropy = sec_entropy
sec_password_audit = sec_audit_password

from doomscript.domains.game.runtime import (
    game_roll_dice,
    game_weighted_choice,
    game_create_tilemap,
    game_set_tile,
    game_get_tile,
    game_astar_grid,
    game_has_line_of_sight,
    game_resolve_turn,
    game_apply_status_effect,
    execute_game_ir,
    BehaviorTree,
    SequenceNode,
    SelectorNode,
    InverterNode,
    ActionNode,
    ConditionNode,
    SteeringBehaviors,
    TilemapPhysics,
    game_create_behavior_tree,
    game_steering_seek,
    game_tilemap_resolve,
)
game_tilemap_create = game_create_tilemap
game_tilemap_set = game_set_tile
game_tilemap_get = game_get_tile
game_grid_astar_path = game_astar_grid
game_line_of_sight = game_has_line_of_sight
game_loot_table_pick = game_weighted_choice
game_apply_buff = game_apply_status_effect

from doomscript.domains.quantum.runtime import (
    QuantumRegister,
    quantum_create_register,
    quantum_apply_h,
    quantum_apply_x,
    quantum_apply_y,
    quantum_apply_z,
    quantum_apply_phase,
    quantum_apply_cnot,
    quantum_measure,
    quantum_sample,
    quantum_bell_state,
    quantum_state_vector,
    execute_quantum_ir,
    QuantumErrorCorrection,
    GroverSearch,
    QuantumTeleportation,
    quantum_grover_search,
)
quantum_register_create = quantum_create_register
quantum_apply_hadamard = quantum_apply_h
quantum_apply_pauli_x = quantum_apply_x
quantum_apply_pauli_y = quantum_apply_y
quantum_apply_pauli_z = quantum_apply_z

from doomscript.domains.circuit.runtime import (
    circuit_ohms_law,
    circuit_ohm_voltage,
    circuit_ohm_current,
    circuit_ohm_resistance,
    circuit_resistor_bands,
    circuit_voltage_divider,
    circuit_555_timer,
    circuit_rc_time_constant,
    circuit_eval_logic,
    circuit_pwm_analog_value,
    circuit_create_gpio,
    circuit_set_pin,
    circuit_read_pin,
    execute_circuit_ir,
    ModifiedNodalAnalysis,
    BodePlotAnalyzer,
    OpAmpModel,
    circuit_mna_dc_solve,
    circuit_bode_plot,
    circuit_opamp_amplify,
)

from doomscript.domains.chain.runtime import (
    MerkleTree,
    chain_create_merkle_tree,
    chain_get_merkle_root,
    chain_get_merkle_proof,
    chain_verify_merkle_proof,
    chain_mine_pow_block,
    chain_verify_pow_block,
    chain_create_utxo_ledger,
    chain_add_utxo_tx,
    chain_get_utxo_balance,
    chain_eip55_address,
    execute_chain_ir,
    PatriciaMerkleTrie,
    SchnorrZKProtocol,
    RaftConsensusEngine,
    chain_schnorr_prove,
    chain_schnorr_verify,
    chain_schnorr_public_key,
)
chain_merkle_tree_create = chain_create_merkle_tree
chain_merkle_root = chain_get_merkle_root
chain_merkle_proof_verify = chain_verify_merkle_proof
chain_mine_block = chain_mine_pow_block

from doomscript.domains.math3d.runtime import (
    Vec3,
    Vec4,
    Mat4,
    Quat,
    Ray,
    math3d_ray_sphere_intersect,
    math3d_ray_triangle_intersect,
    math3d_sdf_sphere,
    math3d_sdf_box,
    math3d_sdf_torus,
    math3d_sdf_smooth_union,
    math3d_sdf_normal,
    math3d_raymarch,
    Raymarcher3D,
    DualQuaternion,
    Quickhull3D,
    math3d_raymarcher_render,
    math3d_dual_quaternion,
    math3d_quickhull,
)
math3d_create_vec3 = Vec3
from doomscript.domains.math3d import (
    math3d_cross_product,
    math3d_dot_product,
    math3d_normalize_vec,
    math3d_look_at,
    math3d_perspective,
    math3d_slerp,
)

from doomscript.domains.graphics.runtime import (
    graphics_create_framebuffer,
    graphics_create_depthbuffer,
    graphics_draw_line,
    graphics_draw_circle,
    graphics_draw_rect,
    graphics_draw_triangle,
)

from doomscript.domains.opt.runtime import opt_create_linear_program
from doomscript.domains.net.runtime import net_format_ip

from doomscript.domains.compiler.runtime import (
    Opcode,
    Instruction,
    BytecodeVM,
    Assembler,
    LexerGenerator,
    PrattParser,
    compiler_run_bytecode,
    compiler_assemble_string,
    compiler_parse_pratt,
    LALR1Parser,
    SSAFormBuilder,
    ChaitinRegisterAllocator,
    compiler_lalr1_parse,
    compiler_build_ssa,
    compiler_allocate_registers,
)

from doomscript.domains.robotics.runtime import (
    DHParameter,
    ForwardKinematicsChain,
    InverseKinematics2D,
    TrajectoryPlanner,
    ExtendedKalmanFilter2D,
    RRTNode,
    RRTPlanner2D,
    ArtificialPotentialField2D,
    DifferentialDriveKinematics,
    PurePursuitController,
    StewartPlatformIK,
    TrapezoidalVelocityProfile,
    robotics_forward_kinematics,
    robotics_inverse_kinematics_2link,
    robotics_cubic_trajectory,
    robotics_create_ekf,
    robotics_rrt_plan,
    robotics_rrt_star_plan,
    robotics_apf_forces,
    robotics_diff_drive_forward,
    robotics_diff_drive_odometry,
    robotics_pure_pursuit,
    robotics_stewart_platform_ik,
    robotics_trapezoidal_profile,
)

from doomscript.domains.signals.runtime import (
    WaveletTransform,
    FilterDesign,
    SignalAnalytics,
    signals_haar_dwt,
    signals_haar_idwt,
    signals_db4_dwt,
    signals_fir_lowpass,
    signals_butterworth_filter,
    signals_hilbert,
    signals_find_peaks,
    STFTSpectrogram,
    SavitzkyGolayFilter,
    signals_stft,
    signals_savitzky_golay,
    CooleyTukeyFFT,
    HilbertTransform,
    CrossCorrelation,
    PeakDetector,
    LombScarglePeriodogram,
    signals_fft,
    signals_ifft,
    signals_cross_correlation,
    signals_detect_pitch,
    signals_lomb_scargle,
)

from doomscript.domains.astronomy.runtime import (
    CelestialTime,
    KeplerianOrbit,
    CelestialCoordinates,
    Astrodynamics,
    astronomy_julian_date,
    astronomy_kepler_orbit,
    astronomy_eq_to_horiz,
    astronomy_hohmann_transfer,
    PlanetaryEphemeris,
    EclipsePredictor,
    AtmosphericRefraction,
    astronomy_planet_position,
    astronomy_planet_geocentric,
    astronomy_predict_eclipse,
    astronomy_atmospheric_refraction,
)

from doomscript.domains.chem.runtime import (
    PERIODIC_TABLE,
    FormulaParser,
    Atom,
    Bond,
    MoleculeGraph,
    SMILESParser,
    ReactionBalancer,
    chem_molecular_weight,
    chem_elemental_composition,
    chem_parse_smiles,
    chem_balance_reaction,
    MolecularGraphLayout,
    MorganFingerprint,
    ReactionKineticsSimulator,
    chem_generate_layout,
    chem_morgan_fingerprint,
    chem_tanimoto_similarity,
    chem_simulate_kinetics,
)

from doomscript.domains.compression.runtime import (
    ShannonEntropy,
    RunLengthCodec,
    HuffmanCodec,
    LZ77Codec,
    LZWCodec,
    ArithmeticCodec,
    compression_entropy,
    compression_rle_encode,
    compression_rle_decode,
    compression_huffman_encode,
    compression_huffman_decode,
    compression_lz77_encode,
    compression_lz77_decode,
    compression_lzw_encode,
    compression_lzw_decode,
    BWTCompressor,
    DeflateEngine,
    ByteAlignedSnappy,
    compression_bwt_compress,
    compression_bwt_decompress,
    compression_deflate,
    compression_inflate,
    compression_snappy_compress,
    compression_snappy_decompress,
)

from doomscript.domains.time_series.runtime import (
    TimeSeriesDifferencer,
    AutocorrelationAnalyzer,
    TimeSeriesDecomposer,
    ExponentialSmoothing,
    time_series_decompose,
    time_series_acf,
    time_series_pacf,
    time_series_holt_winters,
    time_series_difference,
    ARIMASimulator,
    DynamicTimeWarping,
    CUSUMDetector,
)

from doomscript.domains.symbolic.runtime import (
    Expr,
    Constant,
    Symbol,
    Add,
    Mul,
    Pow,
    Sin,
    Cos,
    Ln,
    Exp,
    ExpressionParser,
    PolyOps,
    symbolic_parse,
    symbolic_diff,
    symbolic_simplify,
    symbolic_eval,
    symbolic_poly_gcd,
    SymbolicIntegrator,
    TaylorSeries,
    ExactRationalLinearSolver,
    symbolic_integrate,
    symbolic_taylor_series,
    symbolic_solve_rational_linear,
)

from doomscript.domains.graphics.runtime import (
    FrameBuffer,
    DepthBuffer,
    Rasterizer2D,
    Rasterizer3D,
    graphics_create_framebuffer,
    graphics_create_depthbuffer,
    graphics_draw_line,
    graphics_draw_circle,
    graphics_draw_rect,
    graphics_draw_triangle,
    BlinnPhongShader,
    BilinearTextureMapper,
    SuperSampledFrameBuffer,
    graphics_blinn_phong,
    graphics_sample_bilinear,
    graphics_supersampled_framebuffer,
)

from doomscript.domains.telecom.runtime import (
    Hamming74,
    CRC,
    GF256,
    ReedSolomon,
    telecom_hamming74_encode,
    telecom_hamming74_decode,
    telecom_crc8,
    telecom_crc16,
    telecom_crc32,
    telecom_reed_solomon_encode,
    telecom_reed_solomon_decode,
    ViterbiDecoder,
    QAMModem,
    OFDMFramer,
    telecom_viterbi_encode,
    telecom_viterbi_decode,
    telecom_qam_modulate,
    telecom_qam_demodulate,
    telecom_ofdm_frame,
)

from doomscript.domains.neuro.runtime import (
    LIFNeuron,
    IzhikevichNeuron,
    STDP,
    PoissonSpikeGenerator,
    SpikeAnalytics,
    neuro_create_lif,
    neuro_create_izhikevich,
    neuro_stdp_update,
    neuro_poisson_spikes,
    neuro_simulate_lif,
    TsodyksMarkramSynapse,
    FitzHughNagumoNeuron,
    WinnerTakeAllNetwork,
)

from doomscript.domains.automata.runtime import (
    DFA,
    NFA,
    ThompsonRegex,
    TuringMachine,
    automata_create_dfa,
    automata_dfa_accepts,
    automata_minimize_dfa,
    automata_regex_to_dfa,
    automata_run_turing_machine,
    PushdownAutomaton,
    MooreMealyFSM,
    BuchiAutomaton,
    automata_create_pda,
    automata_pda_accepts,
    automata_create_moore_fsm,
    automata_create_mealy_fsm,
    automata_run_fsm,
    automata_create_buchi,
    automata_buchi_accepts_cycle,
)

from doomscript.domains.metrics.runtime import (
    Counter,
    Gauge,
    Histogram,
    QuantileReservoir,
    TraceSpan,
    metrics_counter,
    metrics_gauge,
    metrics_histogram,
    metrics_calculate_percentile,
    metrics_export_openmetrics,
    metrics_clear,
    OTLPTraceExporter,
    ExponentialDecayReservoir,
    EWMAAnomalyDetector,
    metrics_export_otlp_traces,
    metrics_create_ewma_detector,
)

from doomscript.domains.spatial_audio.runtime import (
    BinauralPanner,
    AmbisonicsBFormat,
    DopplerEffect,
    SchroederReverberator,
    spatial_audio_binaural,
    spatial_audio_ambisonics_encode,
    spatial_audio_ambisonics_decode_stereo,
    spatial_audio_doppler,
    spatial_audio_schroeder_reverb,
    HigherOrderAmbisonics,
    AcousticRaytracer,
    HRTFConvolution,
    VectorBaseAmplitudePanning,
    AtmosphericAttenuation,
    spatial_audio_hoa_encode,
    spatial_audio_room_impulse_response,
    spatial_audio_hrtf_binaural,
    spatial_audio_vbap_2d,
    spatial_audio_distance_attenuate,
)

from doomscript.domains.dsa.runtime import (
    RedBlackTree,
    RBNode,
    SkipList,
    SkipListNode,
    dsa_red_black_tree,
    dsa_skip_list,
    BTree,
    BTreeNode,
    PrefixTrie,
    TrieNode,
    dsa_btree,
    dsa_prefix_trie,
    FibonacciHeap,
    FibonacciHeapNode,
    DisjointSetUnion,
    FenwickTree,
    FenwickTree2D,
    BloomFilter,
    CountingBloomFilter,
    dsa_fibonacci_heap,
    dsa_dsu,
    dsa_fenwick_tree,
    dsa_fenwick_tree_2d,
    dsa_bloom_filter,
    dsa_counting_bloom_filter,
)

from doomscript.domains.ml.runtime import (
    RandomForestModel,
    ml_train_random_forest,
    LinearSVM,
    KMeansPlusPlus,
    TinyConvNet,
    GradientBoostedTreesExact,
    ml_svm_train,
    ml_kmeans_plus_plus,
    ml_tiny_convnet,
    ml_xgboost_exact,
)

from doomscript.domains.finance.runtime import (
    fin_monte_carlo_var,
    AnalyticalGreeks,
    BinomialCoxRossRubinstein,
    MarkowitzOptimizer,
)

from doomscript.domains.graph.runtime import (
    graph_johnson_apsp,
    graph_tarjan_scc,
    graph_hopcroft_karp,
    graph_eulerian_path,
    graph_boruvka_mst,
)

from doomscript.domains.net.runtime import (
    DNSWireProtocol,
    net_dns_build_query,
    net_dns_parse_packet,
    TLS13ClientHelloParser,
    SOCKS5Protocol,
    CIDRPrefixTrie,
    net_parse_tls_client_hello,
    net_build_socks5_response,
    net_create_cidr_trie,
)

from doomscript.domains.sim.runtime import (
    SimResource,
    DiscreteEventSimulation,
    sim_create_discrete_event_sim,
    AgentBasedModel2D,
    Agent2D,
    MCMCSampler,
    JacksonQueuingNetwork,
    sim_create_abm_2d,
    sim_mcmc_sample,
    sim_jackson_network,
)

from doomscript.domains.geo.runtime import (
    QuadTree,
    QuadTreeNode,
    geo_quadtree,
    DelaunayTriangulator,
    WebMercatorProjection,
    IsochroneContour,
)

from doomscript.domains.nlp.runtime import (
    KneserNeyLanguageModel,
    nlp_kneser_ney,
    BytePairEncoder,
    Word2VecCBOW,
    nlp_bpe_train,
    nlp_hmm_pos_tagger,
    nlp_cbow_word2vec,
)

from doomscript.domains.opt.runtime import (
    opt_hungarian_algorithm,
    PrimalDualInteriorPoint,
    BranchAndBoundMILP,
    AdaptiveSimulatedAnnealing,
    opt_solve_interior_point,
    opt_branch_and_bound_milp,
    opt_adaptive_simulated_annealing,
)



# ---------------------------------------------------------------------------
# English-First Ergonomics & Domain Shortcuts
# ---------------------------------------------------------------------------

def words_of(val: Any) -> list:
    """Extract words from text as a list of strings."""
    if val is None:
        return []
    return str(val).split()


def lines_of(val: Any) -> list:
    """Extract lines from text as a list of strings."""
    if val is None:
        return []
    res = []
    for part in str(val).splitlines():
        res.extend(part.split("\\n"))
    return res


def dict_keys(val: Any) -> list:
    """Return keys of a record or dictionary."""
    if hasattr(val, "keys"):
        return list(val.keys())
    return []


def dict_values(val: Any) -> list:
    """Return values of a record or dictionary."""
    if hasattr(val, "values"):
        return list(val.values())
    return []


def accuracy_score_fn(preds: Any, actuals: Any) -> float:
    """Calculates accuracy score between predicted and actual values."""
    if not preds or not actuals:
        return 0.0
    p_list = list(preds)
    a_list = list(actuals)
    if len(p_list) != len(a_list):
        return 0.0
    correct = sum(1 for p, a in zip(p_list, a_list) if p == a)
    return round(correct / len(p_list), 4)


def dsa_push(container: Any, item: Any) -> Any:
    """Push an item into a heap, list, or deque."""
    from collections import deque
    if hasattr(container, "push") and callable(container.push):
        container.push(item)
    elif isinstance(container, deque):
        container.append(item)
    elif isinstance(container, list):
        container.append(item)
    return container


def dsa_heap_push(heap_list: Any, item: Any) -> Any:
    """Push an item into a min/max heap or list."""
    if hasattr(heap_list, "push") and callable(heap_list.push):
        heap_list.push(item)
        return heap_list
    import heapq
    heapq.heappush(heap_list, item)
    return heap_list


def dsa_heap_pop_min(heap_list: Any) -> Any:
    """Pop the minimum item from a min-heap or list."""
    from doomscript.domains.dsa.runtime import DsaHeap
    if isinstance(heap_list, DsaHeap):
        return heap_list.pop()
    import heapq
    if not heap_list:
        return None
    return heapq.heappop(heap_list)


def dsa_heap_pop_max(heap_list: Any) -> Any:
    """Remove and return the maximum item from a max-heap or collection."""
    from doomscript.domains.dsa.runtime import DsaHeap
    if isinstance(heap_list, DsaHeap) and getattr(heap_list, "kind", "") == "max":
        return heap_list.pop()
    if not heap_list:
        return None
    mx = max(heap_list)
    heap_list.remove(mx)
    return mx


def dsa_deque_pop_left(q: Any) -> Any:
    """Pop the first/left element from a deque or list."""
    from collections import deque
    if isinstance(q, deque):
        return q.popleft() if q else None
    if isinstance(q, list):
        return q.pop(0) if q else None
    return None


def db_find_rows(table_name: str, where_sql: Optional[str] = None) -> list:
    """Query rows from an SQLite table in the active db session."""
    from doomscript.domains.db.runtime import get_db_runtime
    db_rt = get_db_runtime()
    q = f'SELECT * FROM "{table_name}"'
    if where_sql:
        q += f" WHERE {where_sql}"
    cur = db_rt.get_connection().cursor()
    cur.execute(q)
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = cur.fetchall()
    return [Record(dict(zip(cols, r))) for r in rows]


def db_count_rows(table_name: str) -> int:
    """Count rows in an SQLite table in the active db session."""
    from doomscript.domains.db.runtime import get_db_runtime
    db_rt = get_db_runtime()
    cur = db_rt.get_connection().cursor()
    cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    row = cur.fetchone()
    return row[0] if row else 0


def sim_sample_normal(mean: float, std: float, count: int = 1000) -> list:
    """Generate samples from a Normal (Gaussian) distribution."""
    import random
    return [random.gauss(float(mean), float(std)) for _ in range(int(count))]


def sim_sample_uniform(low: float, high: float, count: int = 1000) -> list:
    """Generate samples from a Uniform distribution."""
    import random
    return [random.uniform(float(low), float(high)) for _ in range(int(count))]


def filter_dataset(data: Any, condition: str) -> list:
    """Filter records in a dataset using safe AST expression evaluation."""
    from doomscript.domains.data.runtime import _to_record_list
    from doomscript.domains.data.expr_eval import SafeASTEvaluator
    rows = _to_record_list(data)
    evaluator = SafeASTEvaluator()
    return [Record(r) for r in rows if evaluator.evaluate(condition, r)]


def sort_dataset(data: Any, by_col: str, descending: bool = False) -> list:
    """Sort records in a dataset by a given column."""
    from doomscript.domains.data.runtime import _to_record_list
    rows = _to_record_list(data)
    return [
        Record(r)
        for r in sorted(
            rows,
            key=lambda r: (r.get(by_col) is None, r.get(by_col)),
            reverse=descending,
        )
    ]


def group_dataset(data: Any, by_col: str, agg_func: str, agg_col: str) -> list:
    """Group dataset by column and compute aggregate."""
    from doomscript.domains.data.runtime import _to_record_list
    rows = _to_record_list(data)
    grouped: Dict[Any, List[Any]] = {}
    for r in rows:
        key = r.get(by_col)
        grouped.setdefault(key, []).append(r.get(agg_col))
    out = []
    fn = agg_func.lower()
    for k, vals in grouped.items():
        clean_vals = [v for v in vals if isinstance(v, (int, float))]
        if fn in ("sum", "total"):
            res = sum(clean_vals) if clean_vals else 0
        elif fn in ("avg", "mean", "average"):
            res = (sum(clean_vals) / len(clean_vals)) if clean_vals else 0
        elif fn in ("min", "lowest", "minimum"):
            res = min(clean_vals) if clean_vals else 0
        elif fn in ("max", "highest", "maximum"):
            res = max(clean_vals) if clean_vals else 0
        elif fn in ("count",):
            res = len(vals)
        else:
            res = len(vals)
        out.append(Record({by_col: k, f"{fn}_{agg_col}": res}))
    return out


def train_direct_model(
    algo: str,
    data_val: Any,
    target_col: str,
    feature_cols: Optional[List[str]] = None,
    scope: Optional[Dict[str, Any]] = None,
):
    """Direct one-liner model trainer."""
    from doomscript.domains.data.runtime import _to_record_list
    from doomscript.domains.ml.spec import ModelSpec
    from doomscript.domains.ml.runtime import ModelContainer, train_model
    rows = _to_record_list(data_val)
    if not feature_cols and rows:
        feature_cols = [k for k in rows[0].keys() if k != target_col]
    spec = ModelSpec(
        name=f"{algo}_model",
        dataset="__direct_dataset__",
        target=target_col,
        features=feature_cols or [],
        algorithm=algo,
    )
    container = ModelContainer(spec)
    if scope is None:
        import sys
        caller_frame = sys._getframe(1)
        scope = dict(caller_frame.f_globals)
        if caller_frame.f_locals:
            scope.update(caller_frame.f_locals)
    scope["__direct_dataset__"] = data_val
    return train_model(container, scope=scope)














# --- Cluster G: Finance, Time Series, Blockchain, Quantum & Cybersecurity Wrappers ---

def finance_analytical_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> Any:
    """Calculates Black-Scholes price and exact analytical Greeks (Delta, Gamma, Vega, Theta, Rho)."""
    return Record(AnalyticalGreeks.all_greeks(S, K, T, r, sigma, option_type=option_type))


def finance_binomial_price(
    S0: float, K: float, T: float, r: float, sigma: float, steps: int = 100, option_type: str = "call", is_american: bool = False
) -> Any:
    """Prices European or American option using Cox-Ross-Rubinstein binomial lattice."""
    return Record(BinomialCoxRossRubinstein.price(S0, K, T, r, sigma, steps=steps, option_type=option_type, is_american=is_american))


def finance_optimize_markowitz(
    returns: List[float], cov_matrix: List[List[float]], risk_free_rate: float = 0.02
) -> Dict[str, Any]:
    """Computes tangency maximum Sharpe ratio portfolio weights under Markowitz modern portfolio theory."""
    return MarkowitzOptimizer.maximum_sharpe_portfolio(returns, cov_matrix, risk_free_rate=risk_free_rate)


def time_series_arima_simulate(
    n: int,
    ar_params: Optional[List[float]] = None,
    d: int = 0,
    ma_params: Optional[List[float]] = None,
    constant: float = 0.0,
    sigma: float = 1.0,
    seed: int = 42,
) -> List[float]:
    """Simulates ARIMA(p, d, q) process data."""
    return ARIMASimulator.simulate(n, ar_params=ar_params, d=d, ma_params=ma_params, constant=constant, sigma=sigma, seed=seed)


def time_series_dtw(series1: List[float], series2: List[float], window: Optional[int] = None) -> Dict[str, Any]:
    """Calculates Dynamic Time Warping alignment distance and optimal path between two sequences."""
    return DynamicTimeWarping.align(series1, series2, window=window)


def time_series_cusum(series: List[float], threshold_h: float = 4.0) -> Dict[str, Any]:
    """Performs CUSUM change point anomaly detection on time series."""
    return CUSUMDetector.detect(series, threshold_h=threshold_h)


def chain_patricia_trie() -> PatriciaMerkleTrie:
    """Instantiates a new Modified Merkle Patricia Trie."""
    return PatriciaMerkleTrie()


def chain_schnorr_prove(
    secret_x: int, public_y: int, g: Optional[int] = None, p: Optional[int] = None, q: Optional[int] = None
) -> Dict[str, Any]:
    """Generates non-interactive Schnorr zero-knowledge proof of discrete logarithm."""
    return SchnorrZKProtocol.prove(secret_x, public_y, g=g, p=p, q=q)


def chain_schnorr_verify(
    public_y: int, proof: Dict[str, Any], g: Optional[int] = None, p: Optional[int] = None, q: Optional[int] = None
) -> bool:
    """Verifies Schnorr zero-knowledge proof."""
    return SchnorrZKProtocol.verify(public_y, proof, g=g, p=p, q=q)


def quantum_grover_search(num_qubits: int, target: int) -> Any:
    """Executes Grover search algorithm to amplify target state with quadratic speedup."""
    grover = GroverSearch(num_qubits=num_qubits, target_state=target)
    return Record(grover.run_optimal())


def quantum_teleport(alpha: complex, beta: complex) -> Dict[str, Any]:
    """Simulates quantum state teleportation over an entangled EPR channel."""
    return QuantumTeleportation.teleport(alpha, beta)


def sec_shamir_split(secret_int: int, n: int, k: int) -> List[Tuple[int, int]]:
    """Splits integer secret into n shares with threshold k."""
    return ShamirSecretSharing.split_secret(secret_int, n=n, k=k)


def sec_shamir_recover(shares: List[Tuple[int, int]]) -> int:
    """Reconstructs secret from k shares using Lagrange polynomial interpolation."""
    return ShamirSecretSharing.recover_secret(shares)


def sec_generate_totp(secret: Union[str, bytes], digits: int = 6) -> str:
    """Generates RFC 6238 time-based one-time password."""
    return TOTPGenerator.generate_totp(secret, digits=digits)


def sec_verify_totp(secret: Union[str, bytes], token: str, tolerance: int = 1) -> bool:
    """Verifies RFC 6238 time-based one-time password with clock drift window."""
    return TOTPGenerator.verify_totp(secret, token, tolerance=tolerance)


def sec_secp256k1_public_key(priv_key: int) -> Tuple[int, int]:
    """Derives elliptic curve public key (x, y) point on secp256k1."""
    return Secp256k1Curve.public_key(priv_key)


def sec_secp256k1_ecdh(priv_key: int, peer_pub_key: Tuple[int, int]) -> str:
    """Derives SHA-256 Elliptic Curve Diffie-Hellman (ECDH) shared secret."""
    return Secp256k1Curve.ecdh_shared_secret(priv_key, peer_pub_key)


# --- Cluster H: Web, Database, Neuroscience & Geospatial Wrappers ---

def web_css_select(html: str, selector: str) -> List[DOMElement]:
    """Parses HTML into DOM and executes CSS selector query."""
    root = CSSSelectorEngine.parse_html(html)
    return CSSSelectorEngine.select(root, selector)


def web_cookie_jar() -> RFC6265CookieJar:
    """Instantiates a new RFC 6265 compliant HTTP cookie jar."""
    return RFC6265CookieJar()


def db_wal_create() -> WALCrashRecovery:
    """Instantiates an ARIES write-ahead logger with recovery support."""
    return WALCrashRecovery()


def db_query_optimizer() -> CostBasedQueryOptimizer:
    """Instantiates a cost-based query optimizer for table scan planning."""
    return CostBasedQueryOptimizer()


def db_mvcc_create() -> SnapshotIsolationMVCC:
    """Instantiates a Snapshot Isolation Multi-Version Concurrency Control engine."""
    return SnapshotIsolationMVCC()


def neuro_tsodyks_markram(
    U: float = 0.2, tau_rec: float = 800.0, tau_fac: float = 50.0, A: float = 1.0
) -> TsodyksMarkramSynapse:
    """Instantiates a Tsodyks-Markram short-term depressing and facilitating synapse."""
    return TsodyksMarkramSynapse(U=U, tau_rec=tau_rec, tau_fac=tau_fac, A=A)


def neuro_fitzhugh_nagumo(a: float = 0.7, b: float = 0.8, tau: float = 12.5) -> FitzHughNagumoNeuron:
    """Instantiates a FitzHugh-Nagumo biological excitable membrane model."""
    return FitzHughNagumoNeuron(a=a, b=b, tau=tau)


def neuro_wta_network(
    num_neurons: int, beta: float = 0.5, tau: float = 10.0, threshold: float = 0.0
) -> WinnerTakeAllNetwork:
    """Instantiates a competitive lateral inhibitory Winner-Take-All neural circuit."""
    return WinnerTakeAllNetwork(num_neurons=num_neurons, beta=beta, tau=tau, threshold=threshold)


def geo_delaunay_triangulate(
    points: List[Tuple[float, float]]
) -> List[Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]]:
    """Computes 2D Delaunay Triangulation using Bowyer-Watson incremental algorithm."""
    return DelaunayTriangulator.triangulate(points)


def geo_voronoi_diagram(points: List[Tuple[float, float]]) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
    """Computes 2D Voronoi diagram dual edges."""
    return DelaunayTriangulator.voronoi_diagram(points)


def geo_web_mercator_forward(lat: float, lon: float) -> Tuple[float, float]:
    """Transforms WGS84 (lat, lon) in degrees to EPSG:3857 (meters x, y)."""
    return WebMercatorProjection.lat_lon_to_xy(lat, lon)


def geo_web_mercator_inverse(x: float, y: float) -> Tuple[float, float]:
    """Transforms EPSG:3857 (meters x, y) back to WGS84 (lat, lon) in degrees."""
    return WebMercatorProjection.xy_to_lat_lon(x, y)


def geo_compute_isochrone(
    origin_node: str,
    nodes: Dict[str, Tuple[float, float]],
    edges: List[Dict[str, Any]],
    max_time_minutes: float,
) -> Dict[str, Any]:
    """Computes reachable road nodes and convex hull isochrone polygon."""
    return IsochroneContour.compute_isochrone(origin_node, nodes, edges, max_time_minutes)
