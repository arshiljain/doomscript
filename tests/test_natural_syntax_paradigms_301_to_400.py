"""
Regression Suite for Paradigms 301 to 400 (Clusters 21 to 25) in DoomScript.
Verifies Stream Processing, Date/Time Recurrence, Human Formatting, Concurrency, and Error Recovery.
"""

import pytest
from doomscript.compiler.engine import execute


def test_cluster21_stream_processing_batching_and_windowing():
    code = """
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 301: chunk <list> by <size> into <target>
chunk nums by 3 into chunked
assert count of chunked == 3
assert chunked[0] == [1, 2, 3]

# 302: partition <list> into <n> chunks into <target>
partition nums into 3 chunks into part3
assert count of part3 == 3

# 303: sliding window of <size> over <list> into <target>
sliding window of 3 over [1, 2, 3, 4, 5] into win3
assert count of win3 == 3
assert win3[0] == [1, 2, 3]

# 304: sliding window of <size> with step <step> over <list> into <target>
sliding window of 2 with step 2 over [1, 2, 3, 4, 5, 6] into stepped_win
assert count of stepped_win == 3
assert stepped_win[0] == [1, 2]

# 305: interleave <l1> and <l2> into <target>
interleave [1, 3, 5] and [2, 4, 6] into mixed
assert mixed == [1, 2, 3, 4, 5, 6]

# 306: zip <l1> and <l2> into pairs into <target>
zip [1, 2] and ["a", "b"] into pairs into paired
assert count of paired == 2
p0 = paired[0]
assert p0[0] == 1
assert p0[1] == "a"

# 308: unzip <pairs> into <l1> and <l2>
unzip [[10, "x"], [20, "y"]] into nums_out and chars_out
assert nums_out == [10, 20]
assert chars_out == ["x", "y"]

# 309: flatten list <nested> into <target>
flatten list [[1, [2, 3]], [4, 5]] into flat_all
assert flat_all == [1, 2, 3, 4, 5]

# 310: flatten list <nested> by <depth> levels into <target>
flatten list [[1, [2, 3]], [4, 5]] by 1 levels into flat_one
assert count of flat_one == 4

# 311: compact <list> into <target>
compact [1, None, 2, "", 3, None] into compacted
assert compacted == [1, 2, 3]

# 312: frequency count of <list> into <target>
frequency count of ["a", "b", "a", "c", "a", "b"] into freq
assert freq["a"] == 3
assert freq["b"] == 2
assert freq["c"] == 1

# 313: cumulative sum of <list> into <target>
cumulative sum of [1, 2, 3, 4] into c_sum
assert c_sum == [1, 3, 6, 10]

# 314: cumulative product of <list> into <target>
cumulative product of [1, 2, 3, 4] into c_prod
assert c_prod == [1, 2, 6, 24]

# 315: differences between adjacent items in <list> into <target>
differences between adjacent items in [10, 15, 12, 20] into diffs
assert diffs == [5, -3, 8]

# 316: cycle <list> <n> times into <target>
cycle [1, 2] 3 times into cycled
assert cycled == [1, 2, 1, 2, 1, 2]

# 317: repeat <item> <n> times into <target>
repeat "hi" 4 times into repeated
assert repeated == ["hi", "hi", "hi", "hi"]

# 318: pad list <list> to length <n> with <val> into <target>
pad list [1, 2] to length 5 with 0 into padded
assert padded == [1, 2, 0, 0, 0]

# 319: split list <list> at index <i> into <l1> and <l2>
split list [1, 2, 3, 4, 5] at index 2 into left_part and right_part
assert left_part == [1, 2]
assert right_part == [3, 4, 5]
"""
    execute(code)


def test_cluster22_advanced_datetime_durations_recurrence():
    code = """
# 321: start of current day
s_day = start of current day
assert s_day.hour == 0
assert s_day.minute == 0

# 322: end of current day
e_day = end of current day
assert e_day.hour == 23
assert e_day.minute == 59

# 323: start of current week
s_wk = start of current week
assert s_wk.hour == 0

# 324: end of current week
e_wk = end of current week
assert e_wk.hour == 23

# 325: start of current month
s_mo = start of current month
assert s_mo.day == 1

# 327: start of current year
s_yr = start of current year
assert s_yr.month == 1
assert s_yr.day == 1

# 328: end of current year
e_yr = end of current year
assert e_yr.month == 12
assert e_yr.day == 31

# 329: days in month of <date>
dim = days in month of "2026-02-15"
assert dim == 28

# 330: if <year> is leap year:
leap_2024 = 2024 is leap year
assert leap_2024 == True
leap_2025 = 2025 is leap year
assert leap_2025 == False

# 331: day of year of <date>
doy = day of year of "2026-01-10"
assert doy == 10

# 332: week number of <date>
wk_num = week number of "2026-01-10"
assert wk_num == 2

# 333: quarter of <date>
q1 = quarter of "2026-02-01"
assert q1 == 1
q3 = quarter of "2026-08-01"
assert q3 == 3

# 334: add <n> business days to <date>
dt_next_b = add 5 business days to "2026-10-19"
assert dt_next_b.day == 26

# 335: subtract <n> business days from <date>
dt_prev_b = subtract 5 business days from "2026-10-26"
assert dt_prev_b.day == 19

# 336: business days between <d1> and <d2>
b_count = business days between "2026-10-19" and "2026-10-26"
assert b_count == 5

# 337: next occurrence of weekday <day> after <date>
next_fri = next occurrence of weekday "friday" after "2026-10-19"
assert next_fri.weekday() == 4

# 338: previous occurrence of weekday <day> before <date>
prev_fri = previous occurrence of weekday "friday" before "2026-10-19"
assert prev_fri.weekday() == 4

# 339: time elapsed since <t> in seconds
el_sec = time elapsed since "2026-01-01" in seconds
assert el_sec > 0
"""
    execute(code)


def test_cluster23_human_readable_formatting_and_presentation():
    code = """
# 341: format number <n> with commas
n_commas = format number 1234567 with commas
assert n_commas == "1,234,567"

# 342: format number <n> with <d> decimal places
n_dec = format number 3.14159 with 2 decimal places
assert n_dec == "3.14"

# 343: format currency <amt> with currency <curr>
cur_code = format currency 49.99 with currency "usd"
assert cur_code == "USD 49.99"

# 344: format currency <amt> with symbol <sym>
cur_sym = format currency 1250.5 with symbol "$"
assert cur_sym == "$1,250.50"

# 346: format bytes <b_size> as human readable
b_kb = format bytes 2048 as human readable
assert b_kb == "2.0 KB"
b_mb = format bytes 10485760 as human readable
assert b_mb == "10.0 MB"

# 347: format seconds <s_val> as duration string
dur_str = format seconds 3665 as duration string
assert "1h" in dur_str
assert "1m" in dur_str
assert "5s" in dur_str

# 348: pluralize <word> with count <n>
p1 = pluralize "apple" with count 1
assert p1 == "1 apple"
p2 = pluralize "apple" with count 5
assert p2 == "5 apples"
p3 = pluralize "city" with count 3
assert p3 == "3 cities"

# 349: ordinal representation of <n>
ord1 = ordinal representation of 1
assert ord1 == "1st"
ord2 = ordinal representation of 2
assert ord2 == "2nd"
ord3 = ordinal representation of 3
assert ord3 == "3rd"
ord11 = ordinal representation of 11
assert ord11 == "11th"
ord22 = ordinal representation of 22
assert ord22 == "22nd"

# 351: wrap <str> at <width> columns
wrapped = wrap "DoomScript brings natural English thought directly into executable production code" at 20 columns
assert len(wrapped.splitlines()) > 1

# 352: indent text <str> by <n> spaces
indented = indent text "line 1" by 4 spaces
assert indented == "    line 1"

# 353: align <str> left in <width> spaces
al_left = align "test" left in 10 spaces
assert al_left == "test      "

# 354: align <str> right in <width> spaces
al_right = align "test" right in 10 spaces
assert al_right == "      test"

# 355: align <str> center in <width> spaces
al_center = align "test" center in 10 spaces
assert al_center == "   test   "

# 356: abbreviate text <str> to <len> words
abbr = abbreviate text "the quick brown fox jumps over the lazy dog" to 4 words
assert abbr == "the quick brown fox..."

# 360: format list <items> as oxford comma string
ox1 = format list ["apples", "bananas", "cherries"] as oxford comma string
assert ox1 == "apples, bananas, and cherries"
"""
    execute(code)


def test_cluster24_concurrency_and_async_coordination():
    code = """
# 371: create channel into <chan>
create channel into my_chan
assert channel message count of my_chan == 0

# 372: send <msg> to channel <chan>
send "hello_channel" to channel my_chan
assert channel message count of my_chan == 1

# 373: receive message from channel <chan> into <target>
receive message from channel my_chan into rec_msg
assert rec_msg == "hello_channel"
assert channel message count of my_chan == 0

# 374: receive message from channel with timeout
send "timeout_test" to channel my_chan
receive message from channel my_chan with timeout 50 ms into fast_rec
assert fast_rec == "timeout_test"

# 375: close channel <chan>
close channel my_chan
assert my_chan is closed

# 379: create mutex lock into <lock>
create mutex lock into my_lock
assert my_lock is not None

# 367: run parallel map <fn> over <list> with <workers> workers into <target>
def square_fn(x):
    return x * x

run parallel map square_fn over [1, 2, 3, 4] with 2 workers into squared_parallel
assert squared_parallel == [1, 4, 9, 16]
"""
    execute(code)


def test_cluster25_error_recovery_and_fallback_strategies():
    code = """
# 387: ignore errors and evaluate <expr> with fallback <default>
safe_div = ignore errors and evaluate 10 / 0 with fallback 0
assert safe_div == 0

safe_val = ignore errors and evaluate 100 / 4 with fallback 0
assert safe_val == 25.0

# 386: assert <cond> else log <msg>
assert 5 > 2 else log "Math still works"

# 395: clear current error
clear current error
err_type = current error type
assert err_type == ""

# 385: assert <cond> else raise <msg>
caught_custom = False
try:
    assert 2 == 3 else raise "Custom assertion failed"
if that fails:
    caught_custom = True
assert caught_custom == True

# 390: raise custom error <msg>
caught_err = False
try:
    raise custom error "Failure triggered"
if that fails:
    caught_err = True
assert caught_err == True

# 391: raise validation error <msg>
caught_val_err = False
try:
    raise validation error "Invalid argument value"
if that fails:
    caught_val_err = True
assert caught_val_err == True
"""
    execute(code)
