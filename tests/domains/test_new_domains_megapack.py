"""Comprehensive tests for the 7 new DoomScript domain megapacks:
- bio (Bioinformatics & Genomics)
- physics (Classical Mechanics, Collisions & Controls)
- sec (Cybersecurity & Cryptography)
- game (Game Mechanics & Procedural Simulation)
- quantum (Quantum State Vectors & Logic Gates)
- circuit (Electronics & Embedded Systems)
- chain (Blockchain & Distributed Ledgers)
"""

import pytest
from doomscript.compiler.engine import execute


def test_bio_domain():
    code = """
use bio
dna = "ATGCGATCGATCGATCGTAA"
gc = bio_gc_content(dna)
rna = bio_transcribe(dna)
rev = bio_reverse_complement("ATGC")
aa = bio_translate("AUGUUUUAA")
orfs = bio_find_orfs("ATGCGATAA", 1)
kmers = bio_kmer_counts("ATGCAT", 2)
motifs = bio_find_motif("ATGCATGC", "ATG")
mw = bio_molecular_weight("ATGC")
nw = bio_needleman_wunsch("GATTACA", "GCATGCU", 1, -1, -1)
sw = bio_smith_waterman("TGTTACGG", "GGTTGACTA", 2, -1, -2)
fasta = bio_parse_fasta(">seq1 description\\nATGC\\nTTTA\\n>seq2\\nCCGG")
"""
    env = execute(code)
    assert 40.0 <= env["gc"] <= 60.0
    assert env["rna"] == "AUGCGAUCGAUCGAUCGUAA"
    assert env["rev"] == "GCAT"
    assert env["aa"] == "MF"
    assert len(env["orfs"]) >= 1
    assert env["kmers"]["AT"] == 2
    assert env["motifs"] == [0, 4]
    assert env["mw"] > 0
    assert "score" in env["nw"]
    assert "alignment1" in env["nw"]
    assert "score" in env["sw"]
    assert "alignment1" in env["sw"]
    assert len(env["fasta"]) == 2
    assert env["fasta"][0]["id"] == "seq1 description"
    assert env["fasta"][0]["sequence"] == "ATGCTTTA"


def test_physics_domain():
    code = """
use physics
traj = physics_projectile_trajectory(20.0, 45.0, 9.8, 10)
r = physics_projectile_range(20.0, 45.0, 9.8)
drag = physics_drag_trajectory(20.0, 45.0, 0.05, 1.0, 9.8, 0.05, 100)
hit_box = physics_check_aabb_collision(0, 0, 10, 10, 5, 5, 10, 10)
miss_box = physics_check_aabb_collision(0, 0, 10, 10, 20, 20, 10, 10)
poly1 = [[0, 0], [10, 0], [10, 10], [0, 10]]
poly2 = [[5, 5], [15, 5], [15, 15], [5, 15]]
poly3 = [[20, 20], [30, 20], [30, 30], [20, 30]]
hit_sat = physics_check_sat_collision(poly1, poly2)
miss_sat = physics_check_sat_collision(poly1, poly3)
osc = physics_harmonic_oscillator(1.0, 10.0, 0.5, 1.0, 0.0, 0.02, 50)
v_orb = physics_orbital_velocity(5972000000000000000000000.0, 6371000.0)
v_esc = physics_escape_velocity(5972000000000000000000000.0, 6371000.0)
pid = physics_create_pid(1.5, 0.1, 0.05)
u1 = physics_update_pid(pid, 100.0, 90.0, 0.1)
"""
    env = execute(code)
    assert len(env["traj"]) > 0
    assert env["r"] > 0
    assert len(env["drag"]) > 0
    assert env["hit_box"] is True
    assert env["miss_box"] is False
    assert env["hit_sat"] is True
    assert env["miss_sat"] is False
    assert len(env["osc"]) == 50
    assert env["v_orb"] > 7000
    assert env["v_esc"] > env["v_orb"]
    assert env["u1"] > 0


def test_sec_domain():
    code = """
use sec
ent = sec_entropy("CorrectHorseBatteryStaple123!")
pwd_eval = sec_audit_password("Admin@123456!")
caesar = sec_caesar_cipher("Hello World", 3)
cracked = sec_caesar_crack(caesar)
vig = sec_vigenere_cipher("ATTACKATDAWN", "LEMON", True)
vig_dec = sec_vigenere_cipher(vig, "LEMON", False)
freq = sec_frequency_analysis("HELLO")
xor_c = sec_xor_cipher("SecretText", "mykey")
xor_d = sec_xor_cipher(xor_c, "mykey")
token = sec_decode_jwt("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.XbPfbIHMI6arZ3Y922BhjWgQzWXcXNrz0ogtVhfEd2o")
hd = sec_hexdump("DoomScript")
cvss = sec_cvss_score(8.0, 3.0, 2.0)
banner = sec_parse_banner("SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\\r\\n")
"""
    env = execute(code)
    assert env["ent"] > 0
    assert env["pwd_eval"]["score"] >= 3
    assert env["caesar"] == "Khoor Zruog"
    assert env["cracked"]["shift"] == 3
    assert env["cracked"]["plaintext"] == "Hello World"
    assert env["vig_dec"] == "ATTACKATDAWN"
    assert env["freq"]["H"] == 20.0
    assert env["xor_d"] == "SecretText"
    assert env["token"]["claims"]["name"] == "John Doe"
    assert "44 6f 6f 6d" in env["hd"]
    assert 0 <= env["cvss"] <= 10
    assert env["banner"]["service"] == "SSH"
    assert "8.2p1" in env["banner"]["version"]


def test_game_domain():
    code = """
use game
dice_roll = game_roll_dice("2d6 + 3")
loot = game_weighted_choice(["common_sword", "rare_bow", "legendary_staff"], [70, 25, 5])
tilemap = game_create_tilemap(5, 5, 0)
game_set_tile(tilemap, 2, 2, 1)
val = game_get_tile(tilemap, 2, 2)
path = game_astar_grid(tilemap, 0, 0, 4, 4)
los = game_has_line_of_sight(tilemap, 0, 0, 0, 4)
atk = Record({"name": "Knight", "atk": 25, "hp": 100})
df = Record({"name": "Goblin", "defense": 5, "hp": 30})
turn = game_resolve_turn(atk, df, 1.0)
status = game_apply_status_effect(df, "poison", 3, 5)
"""
    env = execute(code)
    assert 5 <= env["dice_roll"] <= 15
    assert env["loot"] in ["common_sword", "rare_bow", "legendary_staff"]
    assert env["val"] == 1
    assert len(env["path"]) > 0
    assert env["path"][0] == [0, 0]
    assert env["path"][-1] == [4, 4]
    assert env["los"] is True
    assert env["turn"]["damage"] == 20
    assert env["turn"]["defender_hp_remaining"] == 10
    assert env["df"]["hp"] == 5


def test_quantum_domain():
    code = """
use quantum
reg = quantum_create_register(2)
quantum_apply_h(reg, 0)
quantum_apply_cnot(reg, 0, 1)
bell = quantum_state_vector(reg)
samples = quantum_sample(reg, 100)
reg1 = quantum_create_register(1)
quantum_apply_x(reg1, 0)
m = quantum_measure(reg1, 0)
bell_prep = quantum_bell_state("phi_plus")
phi_vec = quantum_state_vector(bell_prep)
"""
    env = execute(code)
    assert len(env["bell"]) == 4
    assert abs(env["bell"][0] ** 2 - 0.5) < 1e-4
    assert abs(env["bell"][3] ** 2 - 0.5) < 1e-4
    assert "00" in env["samples"] or "11" in env["samples"]
    assert env["m"] == 1
    assert abs(env["phi_vec"][0] ** 2 - 0.5) < 1e-4


def test_circuit_domain():
    code = """
use circuit
ohm = circuit_ohms_law(None, 2.0, 5.0)
res = circuit_resistor_bands("brown", "black", "red", "gold")
div = circuit_voltage_divider(12.0, 1000.0, 2000.0)
timer555 = circuit_555_timer(1000.0, 2000.0, 0.000001)
rc = circuit_rc_time_constant(10000.0, 0.000001)
log_res = circuit_eval_logic("AND", [True, True, False])
pwm = circuit_pwm_analog_value(50.0, 5.0)
gpio = circuit_create_gpio([1, 2, 3])
circuit_set_pin(gpio, 2, 1)
p2 = circuit_read_pin(gpio, 2)
"""
    env = execute(code)
    assert env["ohm"]["voltage"] == 10.0
    assert env["ohm"]["power"] == 20.0
    assert env["res"]["resistance"] == 1000.0
    assert env["res"]["tolerance"] == 5.0
    assert env["div"]["v_out"] == 8.0
    assert env["timer555"]["frequency"] > 0
    assert abs(env["rc"]["tau"] - 0.01) < 1e-6
    assert env["log_res"] is False
    assert env["pwm"] == 2.5
    assert env["p2"] == 1


def test_chain_domain():
    code = """
use chain
leaves = ["tx1_alice_to_bob_10", "tx2_bob_to_carol_5", "tx3_carol_to_dave_2"]
mt = chain_create_merkle_tree(leaves)
root = chain_get_merkle_root(mt)
proof = chain_get_merkle_proof(mt, 0)
valid = chain_verify_merkle_proof(leaves[0], proof, root)
block = chain_mine_pow_block(1, root, "0000000000000000", 2)
pow_ok = chain_verify_pow_block(block, 2)
ledger = chain_create_utxo_ledger()
chain_add_utxo_tx(ledger, "tx_genesis", [], [Record({"address": "Alice", "amount": 100})])
chain_add_utxo_tx(ledger, "tx_send", [Record({"tx_id": "tx_genesis", "output_index": 0})], [Record({"address": "Bob", "amount": 40}), Record({"address": "Alice", "amount": 60})])
bal_alice = chain_get_utxo_balance(ledger, "Alice")
bal_bob = chain_get_utxo_balance(ledger, "Bob")
addr = chain_eip55_address("0xfb6916095ca1df60bb79ce92ce3ea74c37c5d359")
"""
    env = execute(code)
    assert len(env["root"]) == 64
    assert env["valid"] is True
    assert env["pow_ok"] is True
    assert env["bal_alice"] == 60
    assert env["bal_bob"] == 40
    assert env["addr"] == "0xfB6916095ca1df60bB79Ce92cE3Ea74c37c5d359"
