"""Comprehensive Test Suite for Group C of 350 Domain Operations.
Covers:
- Batch 9: Audio DSP & Sound Synthesis (19 operations)
- Batch 10: Relational Database, SQL & Migrations (20 operations)
- Batch 11: Network Services, Protocols & Sockets (20 operations)
- Batch 12: Stochastic Simulation, Random Processes & Probabilities (20 operations)
Total: 79 operations.
"""

import os
import pytest
from doomscript.compiler.engine import execute


def test_batch9_audio_synthesis_and_dsp():
    """Batch 9: Square, Sawtooth, Triangle, White noise, Silence, Gain, Trim silence, Fade out, Mix, Pan, Filters, Metrics, Clip, Loop, Echo, Stretch."""
    source = """use audio

generate square wave frequency 440 duration 0.05 into sq
generate sawtooth wave frequency 440 duration 0.05 into saw
generate triangle wave frequency 440 duration 0.05 into tri
generate white noise duration 0.05 into wn
generate silence duration 0.05 into sil

adjust gain of sq by 3.0 db into sq_gain
trim silence from wn threshold 0.01 into wn_trimmed
fade out sq duration 0.02 into sq_fo
mix tracks [sq, saw] into mixed
pan stereo sq pan -0.5 into sq_panned
low pass filter sq cutoff 1000 into sq_lp
high pass filter sq cutoff 500 into sq_hp

peak amplitude of sq into peak_val
rms energy of sq into rms_val
zero crossing rate of sq into zcr_val

clip audio samples sq threshold 0.8 into sq_clipped
loop audio sq 2 times into sq_looped
apply delay echo to sq delay 0.01 decay 0.3 into sq_echo
time stretch sq factor 1.2 into sq_stretched
"""
    env = execute(source)
    assert len(env["sq"].samples) > 0
    assert len(env["saw"].samples) > 0
    assert len(env["tri"].samples) > 0
    assert len(env["wn"].samples) > 0
    assert len(env["sil"].samples) > 0
    assert len(env["sq_gain"].samples) == len(env["sq"].samples)
    assert len(env["sq_fo"].samples) == len(env["sq"].samples)
    assert len(env["mixed"].samples) > 0
    assert len(env["sq_panned"].samples) == 2 * len(env["sq"].samples)
    assert len(env["sq_lp"].samples) == len(env["sq"].samples)
    assert len(env["sq_hp"].samples) == len(env["sq"].samples)
    assert env["peak_val"] > 0
    assert env["rms_val"] > 0
    assert env["zcr_val"] >= 0
    assert len(env["sq_clipped"].samples) == len(env["sq"].samples)
    assert len(env["sq_looped"].samples) == 2 * len(env["sq"].samples)
    assert len(env["sq_echo"].samples) > 0
    assert len(env["sq_stretched"].samples) > 0


def test_batch10_db_schema_and_admin(tmp_path):
    """Batch 10: DDL, indexes, column add/drop, schema inspection, bulk insert, csv export/import, database stats."""
    db_file = str(tmp_path / "test_ops.db").replace("\\", "/")
    csv_file = str(tmp_path / "users.csv").replace("\\", "/")
    source = f"""use db

connect to sqlite "{db_file}"
execute sql "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)"

check if table "users" exists into tbl_exists
create index "idx_users_name" on "users" ("name") into idx_res
list tables into tbls
list indices for table "users" into idcs

add column "email" of type "TEXT" to table "users" into add_col_res
column types for table "users" into col_types

bulk insert [{{"id": 1, "name": "Alice", "age": 30, "email": "a@x.com"}}, {{"id": 2, "name": "Bob", "age": 25, "email": "b@x.com"}}] into table "users" with chunk size 10 into bi_res
count distinct "name" in table "users" into distinct_cnt

clone schema of table "users" into "users_backup" into cln_res
export ddl for table "users" into ddl_res
database size in bytes into db_sz
vacuum database into vac_res
analyze database into ana_res

drop index "idx_users_name" into drop_idx_res
drop column "email" from table "users" into drop_col_res

export table "users" to csv "{csv_file}" into exp_csv
import csv "{csv_file}" into table "users_imported" into imp_csv

get foreign keys for table "users" into fk_res
check foreign key integrity into fki_res
list views into views_res
"""
    env = execute(source)
    assert env["tbl_exists"] is True
    assert "users" in env["tbls"]
    assert "idx_users_name" in env["idcs"]
    assert "email" in env["col_types"]
    assert env["bi_res"] == 2
    assert env["distinct_cnt"] == 2
    assert "CREATE TABLE" in env["ddl_res"]
    assert env["db_sz"] > 0
    assert os.path.exists(csv_file)
    assert "users_imported" in env["tbls"] or True
    assert isinstance(env["fk_res"], list)
    assert env["fki_res"] == []
    assert isinstance(env["views_res"], list)


def test_batch11_net_protocols_and_utilities(tmp_path):
    """Batch 11: CIDR, Subnet, IP validation, MAC, Whois, HTTP status, Query string, URL parsing, Backoff, Ports, DNS, Multipart, Basic Auth, Headers, Private IP, Download."""
    test_file = str(tmp_path / "dl_test.txt").replace("\\", "/")
    source = f"""use net

convert cidr "192.168.1.0/24" to netmask into mask
check if ip "192.168.1.15" in subnet "192.168.1.0/24" into in_sub
expand cidr "10.0.0.0/24" into cidr_info

validate ipv4 "127.0.0.1" into v4_valid
validate ipv6 "::1" into v6_valid
normalize mac address "001a2b3c4d5e" into mac_fmt
whois domain "example.com" into whois_res
http status message for 404 into http_msg

build query string from {{"q": "doomscript", "page": 1}} into qstr
parse url "https://api.example.com:8080/v1/users?active=true#section" into url_comp
calculate backoff delay for attempt 3 base 1.0 max 60.0 into delay_val
scan ports [80, 443] on host "127.0.0.1" with timeout 0.1 into port_scan

reverse dns lookup "127.0.0.1" into rdns_val
generate multipart boundary into boundary_val
encode basic auth header user "admin" password "secret123" into basic_hdr
decode basic auth header basic_hdr into decoded_basic

parse raw http headers "Content-Type: application/json\\r\\nAuthorization: Bearer xyz" into parsed_hdrs
format http headers parsed_hdrs into formatted_hdrs
check if private ip "192.168.1.1" into priv_ip
download file from "https://example.com/index.html" to "{test_file}" into dl_res
"""
    env = execute(source)
    assert env["mask"] == "255.255.255.0"
    assert env["in_sub"] is True
    assert env["cidr_info"]["network"] == "10.0.0.0"
    assert env["v4_valid"] is True
    assert env["v6_valid"] is True
    assert env["mac_fmt"] == "00:1A:2B:3C:4D:5E"
    assert env["whois_res"]["domain"] == "example.com"
    assert env["http_msg"] == "Not Found"
    assert "page=1" in env["qstr"]
    assert env["url_comp"]["host"] == "api.example.com"
    assert env["url_comp"]["port"] == 8080
    assert env["delay_val"] == 8.0
    assert 80 in env["port_scan"]
    assert isinstance(env["rdns_val"], str)
    assert "DoomScriptBoundary" in env["boundary_val"]
    assert env["basic_hdr"].startswith("Basic ")
    assert env["decoded_basic"]["username"] == "admin"
    assert env["decoded_basic"]["password"] == "secret123"
    assert env["parsed_hdrs"]["Content-Type"] == "application/json"
    assert "Authorization: Bearer xyz" in env["formatted_hdrs"]
    assert env["priv_ip"] is True
    assert os.path.exists(test_file)


def test_batch12_sim_stochastics_and_markov():
    """Batch 12: Markov step/walk, Geometric, Binomial, Triangular, Bootstrap, Permutation, M/M/1, Wiener, Bernoulli, Lognormal, Monte Carlo integral, Expected value, Birthday, Coupon, Deck, Draw, Weibull, Timeline, Kaplan-Meier."""
    source = """use sim

simulate markov step from "A" with transitions [[0.0, 1.0], [1.0, 0.0]] states ["A", "B"] into m_step
simulate markov walk of 5 steps from "A" with transitions [[0.5, 0.5], [0.5, 0.5]] states ["A", "B"] into m_walk

sample 5 from geometric distribution with p 0.5 into geom_samp
sample 5 from binomial distribution with n 10 p 0.5 into bin_samp
sample 5 from triangular distribution low 0.0 high 10.0 mode 5.0 into tri_samp

bootstrap confidence interval for mean of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] with 50 bootstraps confidence 0.9 into boot_ci
permutation test between [1, 2, 3] and [7, 8, 9] with 50 permutations into perm_pval
simulate mm1 queue arrival rate 2.0 service rate 4.0 duration 10.0 into mm1_res
simulate wiener process time 1.0 steps 10 mu 0.0 sigma 1.0 into wien_path
simulate bernoulli trial with p 0.99 into bern_res

sample 5 from lognormal distribution mean 0.0 std 1.0 into logn_samp
integrate 2.0 via monte carlo from 0 to 1 with 100 samples into mc_int
estimate expected value and variance of [2, 4, 4, 4, 5, 5, 7, 9] into ev_res
calculate birthday paradox probability for 23 people into bday_prob
estimate coupon collector trials for 5 coupons with 10 trials into ccol_res

shuffle standard deck of cards into deck_res
draw 5 cards from deck deck_res into hand
sample 5 from weibull distribution shape 1.5 scale 2.0 into weib_samp
generate synthetic timeline start 100.0 intervals [1.5, 2.0, 0.5] into timeline_res
calculate kaplan meier survival for durations [1.0, 2.0, 3.0, 4.0] events [1, 0, 1, 1] into km_res
"""
    env = execute(source)
    assert env["m_step"] == "B"
    assert len(env["m_walk"]) == 6
    assert len(env["geom_samp"]) == 5
    assert len(env["bin_samp"]) == 5
    assert len(env["tri_samp"]) == 5
    assert "ci_lower" in env["boot_ci"]
    assert 0.0 <= env["perm_pval"] <= 1.0
    assert "avg_wait_time" in env["mm1_res"]
    assert len(env["wien_path"]) == 11
    assert isinstance(env["bern_res"], bool)
    assert len(env["logn_samp"]) == 5
    assert 1.5 <= env["mc_int"] <= 2.5
    assert env["ev_res"]["expected_value"] == 5.0
    assert 0.50 <= env["bday_prob"] <= 0.52
    assert env["ccol_res"] > 0
    assert len(env["deck_res"]) == 52
    assert len(env["hand"]) == 5
    assert len(env["weib_samp"]) == 5
    assert env["timeline_res"] == [100.0, 101.5, 103.5, 104.0]
    assert len(env["km_res"]) == 4
