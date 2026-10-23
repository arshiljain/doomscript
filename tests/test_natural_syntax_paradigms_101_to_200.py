"""
Regression Suite for Paradigms 101 to 200 (Clusters 11 to 15) in DoomScript.
Verifies File System, Network/HTTP, Tabular CSV, System/OS, and Unit Conversions.
"""

import os
import tempfile
import pytest
from doomscript.compiler.engine import execute


def test_cluster11_file_system_and_file_io(tmp_path):
    test_file = str(tmp_path / "sample.txt").replace("\\", "/")
    test_copy = str(tmp_path / "sample_copy.txt").replace("\\", "/")
    test_subfolder = str(tmp_path / "sub").replace("\\", "/")

    code = f"""
# 103: write <content> to file <path>
write "Line 1\\nLine 2\\nLine 3" to file "{test_file}"

# 105: if file <path> exists:
file_found = False
if file "{test_file}" exists:
    file_found = True
assert file_found == True

# 101: read lines of file <path> into <target>
read lines of file "{test_file}" into file_lines
assert count of file_lines == 3
assert file_lines[0] == "Line 1"

# 102: read entire file <path> into <target>
read entire file "{test_file}" into full_text
assert "Line 2" in full_text

# 104: append <content> to file <path>
append "\\nLine 4" to file "{test_file}"
read lines of file "{test_file}" into updated_lines
assert count of updated_lines == 4

# 109: copy file <src> to <dst>
copy file "{test_file}" to "{test_copy}"
assert file "{test_copy}" exists

# 111: ensure folder <path> exists
ensure folder "{test_subfolder}" exists

# 106: if folder <path> exists:
folder_found = False
if folder "{test_subfolder}" exists:
    folder_found = True
assert folder_found == True

# 118: file extension of <path>
ext = file extension of "{test_file}"
assert ext == ".txt"

# 119: filename of <path>
fname = filename of "{test_file}"
assert fname == "sample.txt"

# 120: parent folder of <path>
pdir = parent folder of "{test_file}"
assert len(pdir) > 0

# 112: list all files in folder <path> into <target>
list all files in folder "{str(tmp_path).replace('\\\\', '/')}" into file_list
assert "sample.txt" in file_list

# 115: file size of <path> in bytes
sz = file size of "{test_file}" in bytes
assert sz > 0

# 107: delete file <path>
delete file "{test_copy}"
assert not (file "{test_copy}" exists)
"""
    execute(code)


def test_cluster12_network_web_and_http():
    code = """
# 128: url encode <text> into <target>
url encode "hello world & doom" into encoded_url
assert encoded_url == "hello%20world%20%26%20doom"

# 129: url decode <text> into <target>
url decode "hello%20world%20%26%20doom" into decoded_url
assert decoded_url == "hello world & doom"

# 130: parse url <url> into <target>
parse url "https://api.example.com:8080/v1/users?page=1&limit=10" into url_info
assert url_info["scheme"] == "https"
assert url_info["host"] == "api.example.com"
assert url_info["port"] == 8080
assert url_info["path"] == "/v1/users"

# 131: url domain of <url>
domain = url domain of "https://example.org/path"
assert domain == "example.org"

# 132: url path of <url>
path_part = url path of "https://example.org/my/page.html"
assert path_part == "/my/page.html"

# 133: url query parameters of <url>
qparams = url query parameters of "https://example.org?user=alice&role=admin"
assert qparams["user"] == "alice"
assert qparams["role"] == "admin"

# 134: url protocol of <url>
proto = url protocol of "wss://socket.example.org"
assert proto == "wss"

# 135: if http status is 200 / ok
resp_ok = {"status": 200, "headers": {"Content-Type": "application/json"}, "body": '{"ok": true}'}
is_success = False
if http status of resp_ok is 200:
    is_success = True
assert is_success == True

# 136: if http status is 404 / not found
resp_404 = {"status": 404, "headers": {}, "body": "Not Found"}
is_missing = False
if http status of resp_404 is 404:
    is_missing = True
assert is_missing == True

# 137: if http status is error
is_err = False
if http status of resp_404 is error:
    is_err = True
assert is_err == True

# 139: http headers of <response>
hdrs = http headers of resp_ok
assert hdrs["Content-Type"] == "application/json"

# 140: http status code of <response>
code_val = http status code of resp_ok
assert code_val == 200

# 138: build url <base> with query <params> into <target>
build url "https://example.com/search" with query {"q": "doomscript", "page": 2} into built_url
assert "q=doomscript" in built_url
"""
    execute(code)


def test_cluster13_tabular_data_and_csv_operations(tmp_path):
    csv_file = str(tmp_path / "data.csv").replace("\\", "/")
    code = f"""
raw_csv = "name,age,salary\\nAlice,30,70000\\nBob,25,50000\\nCharlie,35,90000"

# 142: load csv text <text> into <target>
load csv text raw_csv into tbl
assert count of tbl == 3
assert tbl[0]["name"] == "Alice"

# 143: export <records> to csv <path>
export tbl to csv "{csv_file}"
assert file "{csv_file}" exists

# 141: load csv from <path> into <target>
load csv from "{csv_file}" into loaded_tbl
assert count of loaded_tbl == 3

# 144: convert <records> to csv text into <target>
convert loaded_tbl to csv text into csv_output
assert "Alice" in csv_output

# 145: column names of <table>
cols = column names of tbl
assert "name" in cols
assert "salary" in cols

# 146: row count of <table>
rc = row count of tbl
assert rc == 3

# 147: column <col> of <table> into <target>
column "name" of tbl into names_list
assert names_list == ["Alice", "Bob", "Charlie"]

# 148: add column <col> as <expr> to <table>
# 151: rename column <old> to <new> in <table>
rename column "salary" to "comp" in tbl
assert "comp" in tbl[0]

# 149: drop column <col> from <table>
drop column "comp" from tbl
assert "comp" not in tbl[0]

# 152: sort table <table> by <col> ascending
sort table tbl by "age" ascending
assert tbl[0]["name"] == "Bob"

# 153: sort table <table> by <col> descending
sort table tbl by "age" descending
assert tbl[0]["name"] == "Charlie"

# 155: group table <table> by <col> into <target>
group table tbl by "age" into age_groups
assert 35 in age_groups or "35" in age_groups

# 159: first <n> rows of <table> into <target>
first 2 rows of tbl into top2
assert count of top2 == 2

# 160: last <n> rows of <table> into <target>
last 1 rows of tbl into bot1
assert count of bot1 == 1
"""
    execute(code)


def test_cluster14_system_os_and_process_interaction():
    code = """
# 167: current working directory
cwd = current working directory
assert len(cwd) > 0

# 169: operating system name
os_name = operating system name
assert len(os_name) > 0

# 170: machine hostname
hname = machine hostname
assert len(hname) > 0

# 171: cpu core count
cores = cpu core count
assert cores >= 1

# 172: current process id
pid = current process id
assert pid > 0

# 176: user home directory
home = user home directory
assert len(home) > 0

# 177: temporary directory
tmp = temporary directory
assert len(tmp) > 0

# 178: path separator
sep = path separator
assert count of sep == 1

# 165: set environment variable <name> to <val>
set environment variable "DOOM_TEST_VAR" to "Active123"

# 163: get environment variable <name> into <target>
get environment variable "DOOM_TEST_VAR" into env_val
assert env_val == "Active123"

# 164: get environment variable <name> with default <val> into <target>
get environment variable "DOOM_NON_EXISTENT_VAR" with default "fallback_val" into fallback_res
assert fallback_res == "fallback_val"

# 179: if environment variable <name> exists:
has_env = False
if environment variable "DOOM_TEST_VAR" exists:
    has_env = True
assert has_env == True

# 161: run command <cmd> into <target>
run command "echo hello doom" into cmd_out
assert "hello doom" in cmd_out

# 162: run command <cmd> capturing exit code into <target>
run command "echo test" capturing exit code into code_out
assert code_out == 0

# 175: sleep for <n> milliseconds
sleep for 5 milliseconds
"""
    execute(code)


def test_cluster15_unit_conversions_and_dimensional_quantities():
    code = """
# 181: convert <x> miles to kilometers
km = convert 10 miles to kilometers
assert abs(km - 16.09344) < 1e-4

# 182: convert <x> kilometers to miles
miles = convert 16.09344 kilometers to miles
assert abs(miles - 10.0) < 1e-4

# 183: convert <x> meters to feet
ft = convert 10 meters to feet
assert abs(ft - 32.8084) < 1e-3

# 184: convert <x> feet to meters
m = convert 32.8084 feet to meters
assert abs(m - 10.0) < 1e-3

# 185: convert <x> inches to centimeters
cm = convert 5 inches to centimeters
assert abs(cm - 12.7) < 1e-4

# 186: convert <x> centimeters to inches
inches = convert 12.7 centimeters to inches
assert abs(inches - 5.0) < 1e-4

# 187: convert <x> fahrenheit to celsius
c = convert 212 fahrenheit to celsius
assert abs(c - 100.0) < 1e-4

# 188: convert <x> celsius to fahrenheit
f = convert 100 celsius to fahrenheit
assert abs(f - 212.0) < 1e-4

# 189: convert <x> celsius to kelvin
k = convert 0 celsius to kelvin
assert abs(k - 273.15) < 1e-4

# 190: convert <x> kelvin to celsius
c2 = convert 273.15 kelvin to celsius
assert abs(c2 - 0.0) < 1e-4

# 191: convert <x> pounds to kilograms
kg = convert 100 pounds to kilograms
assert abs(kg - 45.359237) < 1e-4

# 192: convert <x> kilograms to pounds
lbs = convert 45.359237 kilograms to pounds
assert abs(lbs - 100.0) < 1e-4

# 193: convert <x> ounces to grams
g = convert 10 ounces to grams
assert abs(g - 283.4952) < 1e-2

# 194: convert <x> grams to ounces
oz = convert 283.4952 grams to ounces
assert abs(oz - 10.0) < 1e-2

# 195: convert <x> bytes to kilobytes
kb = convert 2048 bytes to kilobytes
assert kb == 2.0

# 196: convert <x> kilobytes to megabytes
mb = convert 2048 kilobytes to megabytes
assert mb == 2.0

# 197: convert <x> megabytes to gigabytes
gb = convert 2048 megabytes to gigabytes
assert gb == 2.0

# 198: convert <x> gigabytes to terabytes
tb = convert 2048 gigabytes to terabytes
assert tb == 2.0

# 199: convert <x> degrees to radians
rad = convert 180 degrees to radians
assert abs(rad - 3.14159265) < 1e-4

# 200: convert <x> radians to degrees
deg = convert 3.141592653589793 radians to degrees
assert abs(deg - 180.0) < 1e-4
"""
    execute(code)
