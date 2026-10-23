"""
Regression Suite for Paradigms 201 to 300 (Clusters 16 to 20) in DoomScript.
Verifies Vector Math, Regex & Pattern Matching, Sets & Combinatorics, Serialization, and Cryptography.
"""

import pytest
from doomscript.compiler.engine import execute


def test_cluster16_mathematical_distributions_and_vector_math():
    code = """
v1 = [1.0, 2.0, 3.0]
v2 = [4.0, 5.0, 6.0]

# 201: dot product of <v1> and <v2>
dot_val = dot product of v1 and v2
assert dot_val == 32.0

# 202: cross product of <v1> and <v2>
cp = cross product of [1, 0, 0] and [0, 1, 0]
assert cp == [0, 0, 1]

# 203: vector magnitude of <v>
mag = vector magnitude of [3.0, 4.0]
assert abs(mag - 5.0) < 1e-5

# 204: normalize vector <v> into <target>
normalize vector [0.0, 10.0] into unit_v
assert abs(unit_v[1] - 1.0) < 1e-5

# 205: vector add <v1> and <v2> into <target>
vector add [1, 2] and [3, 4] into v_sum
assert v_sum == [4, 6]

# 206: vector subtract <v2> from <v1> into <target>
vector subtract [2, 1] from [5, 4] into v_diff
assert v_diff == [3, 3]

# 207: vector scale <v> by <s> into <target>
vector scale [2, 3] by 2 into v_scaled
assert v_scaled == [4, 6]

# 208: euclidean distance between <p1> and <p2>
d_euc = euclidean distance between [0, 0] and [3, 4]
assert abs(d_euc - 5.0) < 1e-5

# 209: manhattan distance between <p1> and <p2>
d_man = manhattan distance between [1, 1] and [4, 5]
assert d_man == 7.0

# 210: cosine similarity between <v1> and <v2>
cos_sim = cosine similarity between [1, 0] and [1, 0]
assert abs(cos_sim - 1.0) < 1e-5

# 211: angle between vectors <v1> and <v2> in degrees
ang_deg = angle between vectors [1, 0] and [0, 1] in degrees
assert abs(ang_deg - 90.0) < 1e-4

# 212: angle between vectors <v1> and <v2> in radians
ang_rad = angle between vectors [1, 0] and [0, 1] in radians
assert abs(ang_rad - 1.570796) < 1e-4

# 213: random float between <low> and <high>
rf = random float between 1.0 and 5.0
assert 1.0 <= rf <= 5.0

# 214: random integer between <low> and <high>
ri = random integer between 10 and 20
assert 10 <= ri <= 20

# 215: random choice from <list>
rc = random choice from ["apple", "banana", "cherry"]
assert rc in ["apple", "banana", "cherry"]

# 218: clamp <x> between <min> and <max>
clamped1 = clamp 15 between 0 and 10
assert clamped1 == 10
clamped2 = clamp -5 between 0 and 10
assert clamped2 == 0

# 219: linear interpolate from <a> to <b> with fraction <t>
lerp_val = linear interpolate from 10 to 20 with fraction 0.5
assert lerp_val == 15.0

# 220: sigmoid of <x>
sig_zero = sigmoid of 0
assert abs(sig_zero - 0.5) < 1e-5
"""
    execute(code)


def test_cluster17_pattern_matching_extraction_and_search():
    code = """
sample_text = "Reach us at contact@doom.org or support@doom.com with code #release2026 and @admin"

# 226: extract all numbers from <text> into <target>
extract all numbers from "Item 42 costs 99 dollars" into nums
assert nums == [42, 99]

# 227: extract all emails from <text> into <target>
extract all emails from sample_text into email_list
assert "contact@doom.org" in email_list
assert "support@doom.com" in email_list

# 229: extract all hashtags from <text> into <target>
extract all hashtags from sample_text into tags
assert "#release2026" in tags

# 230: extract all mentions from <text> into <target>
extract all mentions from sample_text into mentions
assert "@admin" in mentions

# 228: extract all urls from <text> into <target>
extract all urls from "Visit https://doomscript.org/docs for info" into url_list
assert "https://doomscript.org/docs" in url_list

# 221: find all matches of <regex> in <text> into <target>
find all matches of "[A-Z]+" in "ABC def GHI jkl" into cap_words
assert cap_words == ["ABC", "GHI"]

# 222: first match of <regex> in <text> into <target>
first match of "\\d+" in "Version 2.4.1" into first_digit
assert first_digit == "2"

# 223: if <text> matches regex <pattern>:
has_match = False
if "hello world" matches regex "^hello.*":
    has_match = True
assert has_match == True

# 224: if <text> contains regex <pattern>:
contains_match = False
if "user 123 active" contains regex "\\d+":
    contains_match = True
assert contains_match == True

# 225: replace all regex <pattern> with <subst> in <text> into <target>
replace all regex "\\d+" with "X" in "Order 1234 ID 5678" into masked_order
assert masked_order == "Order X ID X"

# 231: search <text> for <subst> ignoring case
search_idx = search "DOOMSCRIPT IS FAST" for "fast" ignoring case
assert search_idx >= 0

# 232: index of <subst> in <text> into <target>
index of "world" in "hello world" into idx_w
assert idx_w == 6

# 233: last index of <subst> in <text> into <target>
last index of "a" in "banana" into last_a
assert last_a == 5

# 235: count occurrences of <pattern> in <text>
occ_count = count occurrences of "an" in "banana"
assert occ_count == 2

# 239: strip html tags from <text> into <target>
strip html tags from "<p>Hello <b>World</b></p>" into plain_text
assert plain_text == "Hello World"

# 240: escape regex pattern <str> into <target>
escape regex pattern "a.b+c?" into escaped_pattern
assert "\\\\." in escaped_pattern or "\\." in escaped_pattern
"""
    execute(code)


def test_cluster18_sets_logic_and_combinatorics():
    code = """
s1 = [1, 2, 3, 4]
s2 = [3, 4, 5, 6]

# 241: set intersection of <s1> and <s2>
inter = set intersection of s1 and s2
assert sorted(inter) == [3, 4]

# 242: set union of <s1> and <s2>
u = set union of s1 and s2
assert sorted(u) == [1, 2, 3, 4, 5, 6]

# 243: set difference of <s1> and <s2>
diff = set difference of s1 and s2
assert sorted(diff) == [1, 2]

# 244: symmetric difference of <s1> and <s2>
sym_diff = symmetric difference of s1 and s2
assert sorted(sym_diff) == [1, 2, 5, 6]

# 245: if <s1> is subset of <s2>:
sub_check = False
if [1, 2] is subset of [1, 2, 3]:
    sub_check = True
assert sub_check == True

# 248: if <s1> is disjoint from <s2>:
disj_check = False
if [1, 2] is disjoint from [3, 4]:
    disj_check = True
assert disj_check == True

# 249: cartesian product of <l1> and <l2> into <target>
cartesian product of [1, 2] and ["a", "b"] into cp_res
assert count of cp_res == 4
cp_first = cp_res[0]
assert cp_first[0] == 1
assert cp_first[1] == "a"

# 250: all permutations of <list> into <target>
all permutations of [1, 2, 3] into perms
assert count of perms == 6

# 251: all combinations of <list> of size <k> into <target>
all combinations of [1, 2, 3, 4] of size 2 into combs
assert count of combs == 6

# 253: factorial of <n>
f5 = factorial of 5
assert f5 == 120

# 254: combinations count of <n> choose <k>
ncr = combinations count of 5 choose 2
assert ncr == 10

# 255: permutations count of <n> take <k>
npr = permutations count of 5 take 2
assert npr == 20

# 256: convert <list> to set into <target>
convert [1, 2, 2, 3] to set into my_set
assert count of my_set == 3

# 257: convert <set> to list into <target>
convert my_set to list into back_to_list
assert count of back_to_list == 3

# 259: add <item> to set <s1>
add 4 to set my_set
assert 4 in my_set

# 260: remove <item> from set <s1>
remove 4 from set my_set
assert 4 not in my_set
"""
    execute(code)


def test_cluster19_serialization_and_data_formats():
    code = """
data_dict = {"name": "Doom", "version": 2, "tags": ["fast", "intuitive"]}

# 262: convert <obj> to json into <target>
convert data_dict to json into json_str
assert "Doom" in json_str

# 261: parse json <text> into <target>
parse json json_str into parsed_data
assert parsed_data["name"] == "Doom"
assert parsed_data["version"] == 2

# 265: if <text> is valid json:
is_v_json = False
if json_str is valid json:
    is_v_json = True
assert is_v_json == True

# 269: base64 encode <text> into <target>
base64 encode "Hello DoomScript" into b64_text
assert len(b64_text) > 0

# 270: base64 decode <b64> into <target>
base64 decode b64_text into decoded_text
assert decoded_text == "Hello DoomScript"

# 273: hex encode <text> into <target>
hex encode "abc" into h_str
assert h_str == "616263"

# 274: hex decode <hex> into <target>
hex decode "616263" into plain_abc
assert plain_abc == "abc"

# 275: parse query string <qs> into <target>
parse query string "search=doom&mode=fast&limit=10" into q_map
assert q_map["search"] == "doom"
assert q_map["mode"] == "fast"

# 276: build query string from <dict> into <target>
build query string from {"lang": "ds", "active": 1} into built_qs
assert "lang=ds" in built_qs
assert "active=1" in built_qs
"""
    execute(code)


def test_cluster20_cryptography_hashing_and_security():
    code = """
# 281: sha256 hash of <text>
h256 = sha256 hash of "doomscript"
assert len(h256) == 64

# 282: sha512 hash of <text>
h512 = sha512 hash of "doomscript"
assert len(h512) == 128

# 284: md5 hash of <text>
h_md5 = md5 hash of "doomscript"
assert len(h_md5) == 32

# 285: hmac sha256 of <text> with key <key>
mac = hmac sha256 of "payload" with key "secret_key"
assert len(mac) == 64

# 286: generate uuid into <target>
generate uuid into uid1
assert len(uid1) == 36

# 288: generate secure token of <n> bytes into <target>
generate secure token of 16 bytes into sec_token
assert len(sec_token) == 32

# 291: constant time compare <h1> with <h2>
is_match = constant time compare h256 with h256
assert is_match == True
is_diff = constant time compare h256 with h_md5
assert is_diff == False

# 296: generate random hex string of length <n>
r_hex = generate random hex string of length 16
assert len(r_hex) == 16

# 298: mask string <str> keeping first <n> and last <m> characters
masked_id = mask string "1234567890" keeping first 2 and last 2 characters
assert masked_id == "12******90"

# 299: mask email <email>
masked_m = mask email "kanha@example.com"
assert "@" in masked_m
assert "example.com" in masked_m

# 300: mask credit card <card>
masked_cc = mask credit card "1234-5678-9876-5432"
assert masked_cc.endswith("5432")
"""
    execute(code)
