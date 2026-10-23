"""
Regression Suite for Paradigms 401 to 500 (Clusters 26 to 30) in DoomScript.
Verifies Linguistic Distance, Graph Traversal, Interactive CLI, Caching/Memoization, and Validation/Casting.
"""

from unittest.mock import patch
import pytest
from doomscript.compiler.engine import execute


def test_cluster26_linguistic_and_string_distance():
    code = """
# 401: levenshtein distance between <s1> and <s2>
set lev1 to levenshtein distance between "kitten" and "sitting"
assert lev1 == 3

# 402: similarity ratio between <s1> and <s2>
set sim1 to similarity ratio between "hello" and "hello"
assert sim1 == 1.0

# 403: soundex code of <word>
set sx1 to soundex code of "Robert"
assert sx1 == "R163"

# 404: metaphone code of <word>
set mp1 to metaphone code of "Smith"
assert mp1 == "SM0"

# 405: if <s1> sounds like <s2>:
set sounds_matched to False
if "Smith" sounds like "Smyth":
    set sounds_matched to True
assert sounds_matched == True

# 406: slugify text <str> into <target>
slugify text "Hello World! This is DoomScript" into slug1
assert slug1 == "hello-world-this-is-doomscript"

# 407: convert <str> to camel case into <target>
convert "hello_world_variable" to camel case into camel1
assert camel1 == "helloWorldVariable"

# 408: convert <str> to snake case into <target>
convert "HelloWorldVariable" to snake case into snake1
assert snake1 == "hello_world_variable"

# 409: convert <str> to kebab case into <target>
convert "hello_world_variable" to kebab case into kebab1
assert kebab1 == "hello-world-variable"

# 410: convert <str> to pascal case into <target>
convert "hello_world_variable" to pascal case into pascal1
assert pascal1 == "HelloWorldVariable"

# 411: convert <str> to title case into <target>
convert "hello_world_variable" to title case into title1
assert title1 == "Hello World Variable"

# 412: convert <str> to sentence case into <target>
convert "hello_world_variable" to sentence case into sent1
assert sent1 == "Hello world variable"

# 413: convert <str> to constant case into <target>
convert "hello_world_variable" to constant case into const1
assert const1 == "HELLO_WORLD_VARIABLE"

# 414: stem word <w> into <target>
stem word "testing" into stem1
assert stem1 == "test"

# 415: jaccard similarity between <s1> and <s2>
set jacc to jaccard similarity between [1, 2, 3] and [2, 3, 4]
assert jacc == 0.5

# 416: hamming distance between <s1> and <s2>
set ham1 to hamming distance between "karolin" and "kathrin"
assert ham1 == 3

# 417: find closest string to <target> in <candidates>
fruits = ["apple", "applet", "orange", "grape"]
find closest string to "appl" in fruits into closest1
assert closest1 == "apple"

# 418: find top <n> closest strings to <target> in <candidates>
find top 2 closest strings to "appl" in fruits into top_fruits
assert count of top_fruits == 2
assert top_fruits[0] == "apple"

# 419: remove accents and diacritics from <str> into <target>
remove accents and diacritics from "café naïve résumé" into clean_accents
assert clean_accents == "cafe naive resume"

# 420: transliterate <str> to ascii into <target>
transliterate "café naïve résumé" to ascii into ascii_str
assert ascii_str == "cafe naive resume"
"""
    scope = execute(code)
    assert scope.get("lev1") == 3
    assert scope.get("sounds_matched") is True
    assert scope.get("slug1") == "hello-world-this-is-doomscript"
    assert scope.get("camel1") == "helloWorldVariable"
    assert scope.get("snake1") == "hello_world_variable"
    assert scope.get("kebab1") == "hello-world-variable"
    assert scope.get("pascal1") == "HelloWorldVariable"
    assert scope.get("const1") == "HELLO_WORLD_VARIABLE"
    assert scope.get("stem1") == "test"
    assert scope.get("closest1") == "apple"
    assert scope.get("clean_accents") == "cafe naive resume"


def test_cluster27_graph_and_tree_traversal():
    code = """
# 421: create empty graph into <g>
create empty graph into g
assert is graph g connected == True

# 422: create empty directed graph into <g>
create empty directed graph into dg

# 423: add node <n> to graph <g>
add node "A" to graph g
add node "B" to graph g
add node "C" to graph g
assert node count of graph g == 3

# 424: add edge from <u> to <v> in graph <g>
add edge from "A" to "B" in graph g
add edge from "B" to "C" in graph g
assert edge count of graph g == 2

# 425: add weighted edge from <u> to <v> with weight <w> in graph <g>
add weighted edge from "A" to "C" with weight 10.0 in graph g

# 426: remove edge from <u> to <v> in graph <g>
remove edge from "A" to "C" in graph g

# 427: neighbors of node <n> in graph <g>
set a_neighbors to neighbors of node "A" in graph g
assert "B" in a_neighbors

# 428: shortest path from <u> to <v> in graph <g>
set path_ac to shortest path from "A" to "C" in graph g
assert path_ac == ["A", "B", "C"]

# 429: shortest path length from <u> to <v> in graph <g>
set len_ac to shortest path length from "A" to "C" in graph g
assert len_ac == 2

# 430: if path exists from <u> to <v> in graph <g>:
set has_path_ab to False
if path exists from "A" to "B" in graph g:
    set has_path_ab to True
assert has_path_ab == True

# 431: all connected components of graph <g>
set comps to all connected components of graph g
assert count of comps == 1

# 432: is graph <g> connected
assert is graph g connected == True

# 433: is graph <g> acyclic
assert is graph g acyclic == True

# 434: topological sort of graph <g>
add node "X" to graph dg
add node "Y" to graph dg
add edge from "X" to "Y" in graph dg
set topo to topological sort of graph dg
assert topo == ["X", "Y"]

# 435: depth first search of graph <g> from <start>
set dfs_res to depth first search of graph g from "A"
assert count of dfs_res == 3
assert dfs_res[0] == "A"

# 436: breadth first search of graph <g> from <start>
set bfs_res to breadth first search of graph g from "A"
assert count of bfs_res == 3
assert bfs_res[0] == "A"

# 437: node count of graph <g>
set n_count to node count of graph g
assert n_count == 3

# 438: edge count of graph <g>
set e_count to edge count of graph g
assert e_count == 2

# 439: in-degree of node <n> in graph <g>
set b_in to in-degree of node "B" in graph g
assert b_in == 2

# 440: out-degree of node <n> in graph <g>
set b_out to out-degree of node "B" in graph g
assert b_out == 2
"""
    scope = execute(code)
    assert scope.get("path_ac") == ["A", "B", "C"]
    assert scope.get("len_ac") == 2
    assert scope.get("has_path_ab") is True
    assert scope.get("topo") == ["X", "Y"]
    assert scope.get("n_count") == 3
    assert scope.get("e_count") == 2


def test_cluster28_interactive_cli_and_terminal():
    code = """
# 441: ask user <prompt> into <target>
ask user "Enter username: " into user_val
assert user_val == "antigravity_coder"

# 442: ask user password <prompt> into <target>
ask user password "Enter password: " into pass_val
assert pass_val == "secret_pass"

# 443: ask user boolean <prompt> into <target>
ask user boolean "Confirm action? (y/n): " into bool_val
assert bool_val == True

# 444: ask user integer <prompt> into <target>
ask user integer "Enter age: " into age_val
assert age_val == 42

# 445: ask user number <prompt> into <target>
ask user number "Enter rating: " into rate_val
assert rate_val == 4.75

# 446: prompt user with choices <choices> into <target>
prompt user with choices ["Option A", "Option B"] into chosen_val
assert chosen_val == "Option A"

# 447: print colored <color> text <text>
print colored "green" text "Success completed!"

# 448: print styled bold text <text>
print styled bold text "Important Warning"

# 449: print styled italic text <text>
print styled italic text "Footnote Notice"

# 450: print styled underline text <text>
print styled underline text "Hyperlink Underline"

# 451: print styled text <text> with color <c> on background <bg>
print styled text "Banner Alert" with color "yellow" on background "black"

# 452: clear terminal screen
clear terminal screen

# 453: move cursor to row <r>, column <c>
move cursor to row 10, column 20

# 454: print banner text <text>
print banner text "DoomScript Terminal"

# 455: print divider line with character <ch> of length <n>
print divider line with character "=" of length 50

# 456: show progress bar with current <cur>, total <tot>
show progress bar with current 75, total 100

# 457: render table header <cols> and rows <rows>
render table header ["ID", "Name"] and rows [[1, "Alice"], [2, "Bob"]]

# 458: terminal width in columns
set term_w to terminal width in columns
assert term_w >= 10

# 459: terminal height in rows
set term_h to terminal height in rows
assert term_h >= 5

# 460: beep alert
beep alert
"""
    with patch("builtins.input", side_effect=["antigravity_coder", "yes", "42", "4.75", "1"]):
        with patch("getpass.getpass", return_value="secret_pass"):
            with patch("os.system", return_value=0):
                scope = execute(code)

    assert scope.get("user_val") == "antigravity_coder"
    assert scope.get("pass_val") == "secret_pass"
    assert scope.get("bool_val") is True
    assert scope.get("age_val") == 42
    assert scope.get("rate_val") == 4.75
    assert scope.get("chosen_val") == "Option A"
    assert scope.get("term_w") >= 10
    assert scope.get("term_h") >= 5


def test_cluster29_caching_and_memoization():
    code = """
# 461: create cache into <c>
create cache into my_cache
assert cache size of my_cache == 0

# 462: create cache with max size <n> into <c>
create cache with max size 5 into lru_cache

# 463: create cache with ttl <s> seconds into <c>
create cache with ttl 3600 seconds into ttl_cache

# 465: set in cache <c> key <k> to <v>
set in cache my_cache key "user_1" to "Alice"

# 466: set in cache <c> key <k> to <v> with ttl <s> seconds
set in cache my_cache key "user_2" to "Bob" with ttl 100 seconds

# 464: get from cache <c> key <k> into <target>
get from cache my_cache key "user_1" into u1
assert u1 == "Alice"

# 467: if key <k> in cache <c>:
set has_u1 to False
if key "user_1" in cache my_cache:
    set has_u1 to True
assert has_u1 == True

# 470: cache size of <c>
set sz to cache size of my_cache
assert sz == 2

# 475: cache keys of <c>
set c_keys to cache keys of my_cache
assert "user_1" in c_keys
assert "user_2" in c_keys

# 476: cache hit count of <c>
set hits to cache hit count of my_cache
assert hits >= 1

# 477: cache miss count of <c>
get from cache my_cache key "nonexistent" into no_val
set misses to cache miss count of my_cache
assert misses >= 1

# 478: cache hit ratio of <c>
set ratio to cache hit ratio of my_cache
assert ratio > 0.0

# 474: get or compute in cache <c> key <k> with <fn>
def compute_val(k):
    return k + "_computed"

set comp1 to get or compute in cache my_cache key "calc_key" with compute_val
assert comp1 == "calc_key_computed"
get from cache my_cache key "calc_key" into comp2
assert comp2 == "calc_key_computed"

# 468: remove key <k> from cache <c>
remove key "user_2" from cache my_cache
assert key "user_2" in cache my_cache == False

# 479: invalidate cache keys matching <prefix> in <c>
set in cache my_cache key "temp_1" to 10
set in cache my_cache key "temp_2" to 20
invalidate cache keys matching "temp_" in my_cache
assert key "temp_1" in cache my_cache == False

# 480: evict oldest item in cache <c>
set in cache lru_cache key "k1" to 1
set in cache lru_cache key "k2" to 2
evict oldest item in cache lru_cache
assert key "k1" in cache lru_cache == False

# 471: memoize function <fn>
def double_num(x):
    return x * 2

memoize function double_num
assert double_num(5) == 10
assert double_num(5) == 10

# 472: memoize function <fn> with max size <n>
def triple_num(x):
    return x * 3

memoize function triple_num with max size 16
assert triple_num(4) == 12

# 473: memoize function <fn> with ttl <s> seconds
def quad_num(x):
    return x * 4

memoize function quad_num with ttl 60 seconds
assert quad_num(3) == 12

# 469: clear cache <c>
clear cache my_cache
assert cache size of my_cache == 0
"""
    scope = execute(code)
    assert scope.get("u1") == "Alice"
    assert scope.get("has_u1") is True
    assert scope.get("comp1") == "calc_key_computed"


def test_cluster30_data_validation_and_schema():
    code = """
# 481: if <text> is valid email:
set email_ok to False
email_str = "support@doomscript.org"
if email_str is valid email:
    set email_ok to True
assert email_ok == True

# 482: if <text> is valid ipv4:
set ip4_ok to False
ip4_str = "127.0.0.1"
if ip4_str is valid ipv4:
    set ip4_ok to True
assert ip4_ok == True

# 483: if <text> is valid ipv6:
set ip6_ok to False
ip6_str = "2001:db8::1"
if ip6_str is valid ipv6:
    set ip6_ok to True
assert ip6_ok == True

# 484: if <text> is valid url:
set url_ok to False
url_str = "https://doomscript.org/docs"
if url_str is valid url:
    set url_ok to True
assert url_ok == True

# 485: if <text> is valid phone number:
set phone_ok to False
phone_str = "+1-800-555-0199"
if phone_str is valid phone number:
    set phone_ok to True
assert phone_ok == True

# 486: if <text> is valid credit card:
set cc_ok to False
cc_str = "4111 1111 1111 1111"
if cc_str is valid credit card:
    set cc_ok to True
assert cc_ok == True

# 487: if <text> is valid uuid:
set uuid_ok to False
uuid_str = "123e4567-e89b-12d3-a456-426614174000"
if uuid_str is valid uuid:
    set uuid_ok to True
assert uuid_ok == True

# 488: if <text> is valid date:
set date_ok to False
date_str = "2026-10-23"
if date_str is valid date:
    set date_ok to True
assert date_ok == True

# 489: if <text> is numeric:
set num_ok to False
num_str = "123456"
if num_str is numeric:
    set num_ok to True
assert num_ok == True

# 490: if <text> is alphabetic:
set alpha_ok to False
alpha_str = "DoomScript"
if alpha_str is alphabetic:
    set alpha_ok to True
assert alpha_ok == True

# 491: if <text> is alphanumeric:
set alnum_ok to False
alnum_str = "DoomScript2026"
if alnum_str is alphanumeric:
    set alnum_ok to True
assert alnum_ok == True

# 492: if <text> is lowercase:
set lower_ok to False
lower_str = "alllowercase"
if lower_str is lowercase:
    set lower_ok to True
assert lower_ok == True

# 493: if <text> is uppercase:
set upper_ok to False
upper_str = "ALLUPPERCASE"
if upper_str is uppercase:
    set upper_ok to True
assert upper_ok == True

# 494: if <text> is whitespace:
set ws_ok to False
ws_str = "   \t  "
if ws_str is whitespace:
    set ws_ok to True
assert ws_ok == True

# 495: validate record <r> has required fields <fields>
user_rec = {"id": 101, "name": "DoomCoder", "email": "coder@doom.org"}
req_fields = ["id", "name"]
set valid_fields to validate record user_rec has required fields req_fields
assert valid_fields == True

# 496: validate record <r> against field types <schema>
types_schema = {"id": "int", "name": "str", "email": "str"}
set valid_types to validate record user_rec against field types types_schema
assert valid_types == True

# 497: cast <v> to integer or fallback <d>
set c_int to cast "42" to integer or fallback 0
assert c_int == 42
set c_int_fb to cast "invalid" to integer or fallback 99
assert c_int_fb == 99

# 498: cast <v> to float or fallback <d>
set c_flt to cast "3.14159" to float or fallback 0.0
assert c_flt == 3.14159
set c_flt_fb to cast "not_a_float" to float or fallback -1.0
assert c_flt_fb == -1.0

# 499: cast <v> to boolean or fallback <d>
set c_bool to cast "true" to boolean or fallback False
assert c_bool == True
set c_bool_fb to cast "maybe" to boolean or fallback True
assert c_bool_fb == True

# 500: cast <v> to string or fallback <d>
set c_str to cast 12345 to string or fallback ""
assert c_str == "12345"
"""
    scope = execute(code)
    assert scope.get("email_ok") is True
    assert scope.get("ip4_ok") is True
    assert scope.get("ip6_ok") is True
    assert scope.get("url_ok") is True
    assert scope.get("phone_ok") is True
    assert scope.get("cc_ok") is True
    assert scope.get("uuid_ok") is True
    assert scope.get("date_ok") is True
    assert scope.get("num_ok") is True
    assert scope.get("alpha_ok") is True
    assert scope.get("alnum_ok") is True
    assert scope.get("lower_ok") is True
    assert scope.get("upper_ok") is True
    assert scope.get("ws_ok") is True
    assert scope.get("valid_fields") is True
    assert scope.get("valid_types") is True
    assert scope.get("c_int") == 42
    assert scope.get("c_int_fb") == 99
    assert scope.get("c_flt") == 3.14159
    assert scope.get("c_flt_fb") == -1.0
    assert scope.get("c_bool") is True
    assert scope.get("c_str") == "12345"
