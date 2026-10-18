import pytest
from doomscript.compiler.engine import execute


def test_english_verbs_and_discourse_fillers(capsys):
    code = """
go ahead and echo "echoed text"
please log "logged text"
simply print out "printed out text"
now output "output text"
finally say "final text"
"""
    execute(code)
    out = capsys.readouterr().out
    assert "echoed text" in out
    assert "logged text" in out
    assert "printed out text" in out
    assert "output text" in out
    assert "final text" in out


def test_english_variable_assignments():
    code = """
assign 10 to a
store 20 in b
save 30 as c
initialize d to 40
reset d to 50
"""
    ns = execute(code)
    assert ns["a"] == 10
    assert ns["b"] == 20
    assert ns["c"] == 30
    assert ns["d"] == 50


def test_english_arithmetic_mutators():
    code = """
set a to 10
increment a
increment a by 4
bump a
bump a by 5
decrement a
decrement a by 3
multiply a by 2
divide a by 4
halve a
triple a
"""
    # 10 + 1 = 11 + 4 = 15 + 1 = 16 + 5 = 21 - 1 = 20 - 3 = 17 * 2 = 34 / 4 = 8.5 / 2 = 4.25 * 3 = 12.75
    ns = execute(code)
    assert ns["a"] == 12.75


def test_english_list_mutations():
    code = """
set xs to [1, 2]
append 3 to xs
push 4 into xs
discard 2 from xs
set ys to [10, 20]
clear ys
"""
    ns = execute(code)
    assert ns["xs"] == [1, 3, 4]
    assert ns["ys"] == []


def test_english_predicates():
    code = """
set a to 15
is_div = a is divisible by 5
is_not_div = a is not divisible by 4
is_mult = a is a multiple of 3
is_pos = a is positive
is_neg = a is negative
is_zero = a is zero
is_nonzero = a is non-zero

set empty_txt to ""
is_blank = empty_txt is blank
is_not_blank = empty_txt is not blank

set s to "DoomScript Language"
does_not_have = s does not contain "Java"
does_not_begin = s does not start with "Py"
does_not_finish = s does not end with "Language"

set num to 25
is_not_bet = num is not between 1 and 10
is_outside = num is outside 1 and 10
is_neither = num is neither 10 nor 20

set items to [1, 2, 3]
is_in = 2 is inside items
is_not_in = 5 is not inside items
"""
    ns = execute(code)
    assert ns["is_div"] is True
    assert ns["is_not_div"] is True
    assert ns["is_mult"] is True
    assert ns["is_pos"] is True
    assert ns["is_neg"] is False
    assert ns["is_zero"] is False
    assert ns["is_nonzero"] is True
    assert ns["is_blank"] is True
    assert ns["is_not_blank"] is False
    assert ns["does_not_have"] is True
    assert ns["does_not_begin"] is True
    assert ns["does_not_finish"] is False
    assert ns["is_not_bet"] is True
    assert ns["is_outside"] is True
    assert ns["is_neither"] is True
    assert ns["is_in"] is True
    assert ns["is_not_in"] is True


def test_english_loop_constructs():
    code = """
set sum1 to 0
for all x in [1, 2, 3]:
    sum1 = sum1 + x

set sum2 to 0
for each y of [4, 5, 6]:
    sum2 = sum2 + y

set sum3 to 0
loop through [7, 8] as z:
    sum3 = sum3 + z

set counter to 0
as long as counter < 3:
    counter = counter + 1

set hits to 0
repeat while hits < 2:
    hits = hits + 1

set until_val to 0
until until_val is 4:
    until_val = until_val + 1

# Loop controls
set collected to []
for each n in [1, 2, 3, 4, 5]:
    if n is 2:
        skip to next
    if n is 4:
        break out of loop
    add n to collected
"""
    ns = execute(code)
    assert ns["sum1"] == 6
    assert ns["sum2"] == 15
    assert ns["sum3"] == 15
    assert ns["counter"] == 3
    assert ns["hits"] == 2
    assert ns["until_val"] == 4
    assert ns["collected"] == [1, 3]


def test_english_unless_and_conditionals():
    code = """
set flag to false
unless flag then set result1 to "was false"
unless not flag then set result2 to "was true"

unless flag:
    set result3 to "block unless executed"
"""
    ns = execute(code)
    assert ns["result1"] == "was false"
    assert "result2" not in ns or ns["result2"] is None
    assert ns["result3"] == "block unless executed"


def test_english_function_styles():
    code = """
how to add_nums with x, y:
    result is x + y

define sub_nums with x, y:
    the result is x - y

function mul_nums with x, y:
    give back x * y

sum_val = add_nums(10, 5)
diff_val = sub_nums(10, 5)
prod_val = mul_nums(10, 5)
"""
    ns = execute(code)
    assert ns["sum_val"] == 15
    assert ns["diff_val"] == 5
    assert ns["prod_val"] == 50


def test_english_verifications():
    code = """
set a to 10
make sure that a is 10
assert that a is greater than 0
check that a is positive
"""
    ns = execute(code)
    assert ns["a"] == 10


def test_english_math_and_aggregates():
    code = """
h = half of 50
q = quarter of 100
d = double of 12
t = triple of 7
rem = remainder of 19 divided by 5

data = [10, 20, 30]
avg = average of data
m = mean of data
s = sum of all data
sz = number of items in data
prod = product of [2, 3, 4]
rev = reverse of [1, 2, 3]
"""
    ns = execute(code)
    assert ns["h"] == 25.0
    assert ns["q"] == 25.0
    assert ns["d"] == 24
    assert ns["t"] == 21
    assert ns["rem"] == 4
    assert ns["avg"] == 20.0
    assert ns["m"] == 20.0
    assert ns["s"] == 60
    assert ns["sz"] == 3
    assert ns["prod"] == 24
    assert ns["rev"] == [3, 2, 1]


def test_english_string_and_type_conversions():
    code = """
set raw to "   untrimmed text   "
set cleaned to strip spaces from raw
set title_res to title case of "the quick brown fox"

convert 1234 to text into text_res
turn "5678" into number into num_res
"""
    ns = execute(code)
    assert ns["cleaned"] == "untrimmed text"
    assert ns["title_res"] == "The Quick Brown Fox"
    assert ns["text_res"] == "1234"
    assert ns["num_res"] == 5678


def test_english_dates():
    code = """
set y to yesterday
set tm to tomorrow
set cd to current date
set ct to current timestamp
"""
    ns = execute(code)
    assert len(ns["y"]) == 10
    assert len(ns["tm"]) == 10
    assert len(ns["cd"]) == 10
    assert len(ns["ct"]) >= 19
