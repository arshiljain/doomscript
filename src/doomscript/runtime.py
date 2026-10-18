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
def agg_sum(items):
    """Calculate sum of items."""
    return sum(items)


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
def math_round(value, decimals=0):
    """Round a number to specified decimal places."""
    if decimals == 0:
        return round(float(value))
    return round(float(value), int(decimals))


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
variance = ds_variance
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


def sorted_list(collection):
    """Returns a newly sorted copy of the collection."""
    return sorted(collection)


def reversed_list(collection):
    """Returns a reversed copy of the collection."""
    return list(reversed(collection))


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
    import pandas as pd
    if not isinstance(table, pd.DataFrame):
        table = pd.DataFrame(table)

    op_str = str(op).strip().lower()
    if op_str in (">", "is greater than", "is over"):
        return table[table[col] > val]
    elif op_str in (">=", "is at least", "is greater than or equal to"):
        return table[table[col] >= val]
    elif op_str in ("<", "is less than", "is under"):
        return table[table[col] < val]
    elif op_str in ("<=", "is at most", "is less than or equal to"):
        return table[table[col] <= val]
    elif op_str in ("==", "equals", "is"):
        return table[table[col] == val]
    elif op_str in ("!=", "is not", "isn't"):
        return table[table[col] != val]
    return table


def sort_table(table, col, ascending=True):
    """Sort a table/DataFrame by a column."""
    import pandas as pd
    if not isinstance(table, pd.DataFrame):
        table = pd.DataFrame(table)
    return table.sort_values(col, ascending=ascending)


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






