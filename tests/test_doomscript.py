"""
Comprehensive test suite for DoomScript compiler and runtime.
"""

import pytest
from doomscript.compiler.engine import compile_to_ast, transpile, execute
from doomscript.runtime import Record


def run_code_and_capture_globals(source: str):
    """Helper to execute DoomScript and return resulting local/global state."""
    env = {}
    execute(source, custom_globals=env)
    return env


def test_basic_assignment_and_math():
    code = """
x = 10
y = 20
total = x + y
diff = y - x
mult = x * 2
div = y / 2
"""
    env = run_code_and_capture_globals(code)
    assert env["total"] == 30
    assert env["diff"] == 10
    assert env["mult"] == 20
    assert env["div"] == 10.0


def test_percentage_math():
    code = """
price = 200
discount = 15% of price
final_price = price - discount
"""
    env = run_code_and_capture_globals(code)
    assert env["discount"] == 30.0
    assert env["final_price"] == 170.0


def test_english_comparisons():
    code = """
a = 10
b = 20

res_gte = a is at least 10
res_lte = a is at most 10
res_gt = b is greater than a
res_over = b is over a
res_lt = a is less than b
res_under = a is under b
res_eq = a equals 10
res_neq = a is not b
"""
    env = run_code_and_capture_globals(code)
    assert env["res_gte"] is True
    assert env["res_lte"] is True
    assert env["res_gt"] is True
    assert env["res_over"] is True
    assert env["res_lt"] is True
    assert env["res_under"] is True
    assert env["res_eq"] is True
    assert env["res_neq"] is True


def test_if_else_without_colons():
    code = """
health = 15
status = "OK"

if health is under 20
    status = "CRITICAL"
else
    status = "FINE"
"""
    env = run_code_and_capture_globals(code)
    assert env["status"] == "CRITICAL"


def test_if_with_colons():
    code = """
score = 100
result = "LOSE"

if score is at least 100:
    result = "WIN"
"""
    env = run_code_and_capture_globals(code)
    assert env["result"] == "WIN"


def test_repeat_loop():
    code = """
counter = 0
repeat 5 times
    counter = counter + 1
"""
    env = run_code_and_capture_globals(code)
    assert env["counter"] == 5


def test_for_each_loop():
    code = """
items = [1, 2, 3, 4]
total = 0
for each n in items
    total = total + n
"""
    env = run_code_and_capture_globals(code)
    assert env["total"] == 10


def test_list_add_and_remove():
    code = """
bag = ["potion"]
add "elixir" to bag
add "gem" to bag
remove "potion" from bag
"""
    env = run_code_and_capture_globals(code)
    assert env["bag"] == ["elixir", "gem"]


def test_records_and_possessives():
    code = """
hero = {name: "Slayer", hp: 100}
hero's hp = 85
current_hp = hero's hp
hero_name = hero's name
"""
    env = run_code_and_capture_globals(code)
    assert env["hero"]["hp"] == 85
    assert env["current_hp"] == 85
    assert env["hero_name"] == "Slayer"


def test_functions_with_english_syntax():
    code = """
to damage target with val
    target's hp = target's hp - val

boss = {hp: 300}
damage(boss, 100)
"""
    env = run_code_and_capture_globals(code)
    assert env["boss"]["hp"] == 200


def test_to_without_parameters():
    code = """
state = {flag: false}
to activate
    state's flag = true

activate()
"""
    env = run_code_and_capture_globals(code)
    assert env["state"]["flag"] is True


def test_set_increase_decrease():
    code = """
score = 100
increase score by 50
decrease score by 30

player = {hp: 80}
set player's hp to 100
decrease player's hp by 15
increase player's hp by 5
"""
    env = run_code_and_capture_globals(code)
    assert env["score"] == 120
    assert env["player"]["hp"] == 90


def test_contains_and_emptiness():
    code = """
inventory = ["shotgun", "plasma gun"]
has_shotgun = inventory contains "shotgun"
has_bfg = inventory contains "bfg9000"

empty_chest = []
full_chest = ["gold"]

chest_empty = empty_chest is empty
chest_not_empty = full_chest is not empty
"""
    env = run_code_and_capture_globals(code)
    assert env["has_shotgun"] is True
    assert env["has_bfg"] is False
    assert env["chest_empty"] is True
    assert env["chest_not_empty"] is True


def test_count_of():
    code = """
weapons = ["shotgun", "rocket launcher", "bfg"]
num_weapons = count of weapons
"""
    env = run_code_and_capture_globals(code)
    assert env["num_weapons"] == 3


def test_file_io(tmp_path):
    log_file = str(tmp_path / "test_log.txt").replace("\\", "/")
    code = f"""
write "First entry" into file "{log_file}"
append "Second entry" to file "{log_file}"
read file "{log_file}" into file_content
"""
    env = run_code_and_capture_globals(code)
    assert "First entry" in env["file_content"]
    assert "Second entry" in env["file_content"]


def test_string_interpolation(capsys):
    code = """
hero = {name: "Slayer", hp: 100}
say "Hero: {hero's name}, HP: {hero's hp}"
"""
    execute(code)
    captured = capsys.readouterr()
    assert "Hero: Slayer, HP: 100" in captured.out


def test_post_condition_if():
    code = """
health = 15
status = "OK"
status = "CRITICAL" if health is under 20
status = "DEAD" if health is 0
"""
    env = run_code_and_capture_globals(code)
    assert env["status"] == "CRITICAL"


def test_repeat_while_and_until():
    code = """
x = 0
repeat while x is under 5
    x = x + 1

y = 0
repeat until y is 5
    y = y + 1
"""
    env = run_code_and_capture_globals(code)
    assert env["x"] == 5
    assert env["y"] == 5


def test_natural_call_statements():
    code = """
to strike target with amount
    target's hp = target's hp - amount

boss = {hp: 200}
call strike with boss, 50
call strike boss with 50
"""
    env = run_code_and_capture_globals(code)
    assert env["boss"]["hp"] == 100


def test_relative_time():
    code = """
deadline = 2 days from now
past = 3 hours ago
"""
    env = run_code_and_capture_globals(code)
    assert env["deadline"].day != env["past"].day


def test_graphics_and_audio():
    code = """
beep 440 hz for 0.01 seconds
play sound "shotgun.wav"

open window "Test" with width 200, height 200
draw circle at 50, 50 with radius 10, color "red"
draw rectangle at 10, 10 with width 20, height 20, color "blue"
draw text "Hi" at 30, 30 with size 12, color "white"
refresh screen
clear screen
"""
    env = run_code_and_capture_globals(code)
    # Verifies that graphics and audio commands execute with zero errors
    assert env is not None


def test_random_and_pick():
    code = """
roll between 1 and 20 into d20
pick random from ["shotgun", "plasma gun"] into loot
deck = [1, 2, 3, 4, 5]
shuffle deck
"""
    env = run_code_and_capture_globals(code)
    assert 1 <= env["d20"] <= 20
    assert env["loot"] in ["shotgun", "plasma gun"]
    assert len(env["deck"]) == 5


def test_aggregates():
    code = """
scores = [10, 20, 30, 40]
total = sum of scores
avg = average of scores
top = highest in scores
bottom = lowest in scores
first_val = first item of scores
last_val = last item of scores
"""
    env = run_code_and_capture_globals(code)
    assert env["total"] == 100
    assert env["avg"] == 25.0
    assert env["top"] == 40
    assert env["bottom"] == 10
    assert env["first_val"] == 10
    assert env["last_val"] == 40


def test_database_sqlite(tmp_path):
    db_file = str(tmp_path / "game.db").replace("\\", "/")
    code = f"""
hero = {{name: "Slayer", score: 999}}
save record hero into database "{db_file}" table "leaderboard"
load records from database "{db_file}" table "leaderboard" into records
"""
    env = run_code_and_capture_globals(code)
    records = env["records"]
    assert len(records) == 1
    assert records[0]["name"] == "Slayer"
    assert records[0]["score"] == "999"


def test_attempt_and_fail_recovery():
    code = """
status = "initial"
attempt
    bad = 10 / 0
if it fails
    status = "recovered_gracefully"
"""
    env = run_code_and_capture_globals(code)
    assert env["status"] == "recovered_gracefully"


def test_string_operations():
    code = """
text = "The Cyberdemon strikes at dawn"
replace "Cyberdemon" with "Archvile" in text into new_text
split "mars,phobos,deimos" by "," into moons
join moons with " - " into joined
convert "doom" to uppercase into shout
convert "HELL" to lowercase into whisper
capitalize "slayer" into capped
trim "   spaced out   " into clean

has_the = text starts with "The"
has_dawn = text ends with "dawn"
has_dusk = text ends with "dusk"
matches = shout matches pattern "^[A-Z]+$"
"""
    env = run_code_and_capture_globals(code)
    assert env["new_text"] == "The Archvile strikes at dawn"
    assert env["moons"] == ["mars", "phobos", "deimos"]
    assert env["joined"] == "mars - phobos - deimos"
    assert env["shout"] == "DOOM"
    assert env["whisper"] == "hell"
    assert env["capped"] == "Slayer"
    assert env["clean"] == "spaced out"
    assert env["has_the"] is True
    assert env["has_dawn"] is True
    assert env["has_dusk"] is False
    assert env["matches"] is True


def test_filesystem_verbs(tmp_path):
    d = str(tmp_path / "subfolder").replace("\\", "/")
    src = str(tmp_path / "origin.txt").replace("\\", "/")
    dst = str(tmp_path / "subfolder" / "copied.txt").replace("\\", "/")
    
    code = f"""
create directory "{d}"
write "Secret Transmission" into file "{src}"
copy file "{src}" to "{dst}"
check if file "{dst}" exists into exists_after_copy
list files in "{d}" into files_list
delete file "{src}"
check if file "{src}" exists into src_still_there
if file "{dst}" exists
    verified = true
"""
    env = run_code_and_capture_globals(code)
    assert env["exists_after_copy"] is True
    assert env["files_list"] == ["copied.txt"]
    assert env["src_still_there"] is False
    assert env["verified"] is True


def test_math_round_and_clamp():
    code = """
round 3.14159265 to 2 decimals into pi_2
round 99.876 to 0 decimals into int_rounded
clamp 150 between 0 and 100 into hp_upper
clamp -20 between 0 and 100 into hp_lower
clamp 42 between 0 and 100 into hp_mid
"""
    env = run_code_and_capture_globals(code)
    assert env["pi_2"] == 3.14
    assert env["int_rounded"] == 100.0
    assert env["hp_upper"] == 100.0
    assert env["hp_lower"] == 0.0
    assert env["hp_mid"] == 42.0


def test_concurrency_spawn():
    code = """
result = []

to worker with item
    add item to result

spawn worker with "async_packet" into task_thread
wait for task_thread
"""
    env = run_code_and_capture_globals(code)
    assert env["result"] == ["async_packet"]


def test_english_web_server():
    import urllib.request
    import json
    
    code = """
to handle_index
    return "<h1>Doom Citadel Online</h1>"

to handle_api
    return {status: "operational", engine: "DoomScript"}

route GET "/" to handle_index
route GET "/api" to handle_api
start server on port 9876 in background into srv
"""
    env = run_code_and_capture_globals(code)
    srv = env["srv"]
    try:
        # Fetch root
        with urllib.request.urlopen("http://localhost:9876/") as resp:
            body = resp.read().decode("utf-8")
            assert "Doom Citadel Online" in body
            
        # Fetch json api
        with urllib.request.urlopen("http://localhost:9876/api") as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["status"] == "operational"
            assert data["engine"] == "DoomScript"
    finally:
        # Stop server
        stop_code = """
stop server srv
"""
        execute(stop_code, custom_globals=env)


def test_verification_assertions():
    code = """
passed = false
verify that 10 is greater than 5 otherwise "Math failed"
passed = true

failed_caught = false
attempt
    verify that 2 is greater than 100 otherwise "Expect fail"
if it fails
    failed_caught = true
"""
    env = run_code_and_capture_globals(code)
    assert env["passed"] is True
    assert env["failed_caught"] is True

