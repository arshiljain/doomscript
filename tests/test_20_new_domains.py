"""
Unit test suite verifying all 20 newly added computational and scientific domain packs:
1. genai
2. cache
3. queue
4. crypto_zk
5. climate
6. genomics
7. hydrology
8. materials
9. aerospace
10. control
11. ecology
12. epidemiology
13. logistics
14. forensics
15. microecon
16. risk
17. social
18. linguistics
19. geophysics
20. synthetic_bio
"""

import pytest
from doomscript.compiler.engine import execute


def test_domain_genai():
    code = """
use genai
calculate cosine similarity between [1.0, 0.0] and [1.0, 0.0] into sim
estimate token count for "Hello world DoomScript" into tok_count
chunk text "The quick brown fox jumps over the lazy dog" with size 10 overlap 2 into chunks
"""
    env = execute(code)
    assert env["sim"] == 1.0
    assert env["tok_count"] >= 3
    assert len(env["chunks"]) >= 2


def test_domain_cache():
    code = """
use cache
create lru cache with capacity 2 into c
store in cache c key "user_1" value "Alice"
fetch from cache c key "user_1" into u1
create bloom filter with size 100 hashes 3 into bf
check bloom filter bf for item "key" into present
"""
    env = execute(code)
    assert env["u1"] == "Alice"
    assert env["present"] is False


def test_domain_queue():
    code = """
use queue
create message queue with capacity 10 into q
publish message "task_1" to queue q
consume from queue q into first_task
create priority queue into pq
publish message "urgent" to queue pq with priority 10.0
publish message "normal" to queue pq with priority 1.0
consume from queue pq into top_prio
"""
    env = execute(code)
    assert env["first_task"] == "task_1"
    assert env["top_prio"] == "urgent"


def test_domain_crypto_zk():
    code = """
use crypto_zk
split secret 12345 into 3 shares with threshold 2 into shares
reconstruct secret from shares shares into recovered
create pedersen commitment for message 42 with blinding 13 into commitment
perform diffie hellman between private 5 and public 10 into shared_key
"""
    env = execute(code)
    assert env["recovered"] == 12345
    assert isinstance(env["commitment"], int)
    assert isinstance(env["shared_key"], int)


def test_domain_climate():
    code = """
use climate
calculate dew point for temperature 25.0 humidity 60.0 into dp
calculate heat index for temperature 30.0 humidity 70.0 into hi
calculate barometric pressure at altitude 1000.0 into p_alt
convert emissions 10.0 of gas "ch4" to co2 equivalent into co2_eq
"""
    env = execute(code)
    assert 16.0 <= env["dp"] <= 17.5
    assert env["hi"] > 30.0
    assert env["p_alt"] < 101325.0
    assert env["co2_eq"] == 280.0


def test_domain_genomics():
    code = """
use genomics
calculate gc content for sequence "ATGCGATCGATC" into gc
align sequences local "AGCT" and "AGTT" with match 2 mismatch -1 gap -2 into alignment
find cpg islands in sequence "CGCGCGCGCGATCG" into islands
parse vcf variant record "chr1 100 rs123 A G 50 PASS DP=10" into vcf
"""
    env = execute(code)
    assert env["gc"] == 50.0
    assert env["alignment"]["score"] > 0
    assert len(env["islands"]) >= 1
    assert env["vcf"]["pos"] == 100 and env["vcf"]["ref"] == "A"


def test_domain_hydrology():
    code = """
use hydrology
calculate manning flow for roughness 0.03 area 2.0 radius 0.5 slope 0.001 into q_manning
calculate peak runoff for coeff 0.8 intensity 50.0 area 10.0 into q_runoff
calculate darcy weisbach head loss for friction 0.02 length 100.0 diameter 0.5 velocity 2.0 into hf
calculate reynolds number for velocity 1.5 diameter 0.2 viscosity 0.000001 into re
"""
    env = execute(code)
    assert env["q_manning"] > 0.0
    assert env["q_runoff"] > 0.0
    assert env["hf"] > 0.0
    assert env["re"] == 300000.0


def test_domain_materials():
    code = """
use materials
calculate engineering stress and strain for force 1000.0 area 10.0 delta 0.5 initial length 100.0 into ss
calculate mohrs circle principal stresses for sigma x 100.0 sigma y 50.0 tau 25.0 into mohr
calculate thermal expansion for length 10.0 coeff 0.000012 delta temp 50.0 into delta_l
"""
    env = execute(code)
    assert env["ss"]["stress_pa"] == 100.0
    assert env["ss"]["strain"] == 0.005
    assert env["mohr"]["sigma1"] > env["mohr"]["sigma2"]
    assert env["delta_l"] == 0.006


def test_domain_aerospace():
    code = """
use aerospace
calculate lift and drag for density 1.225 velocity 50.0 area 15.0 cl 0.5 cd 0.03 into ld
calculate mach number for velocity 680.0 at temp 288.15 into mach
calculate breguet range for ld 15.0 velocity 200.0 sfc 0.000015 w0 50000.0 w1 40000.0 into rng
"""
    env = execute(code)
    assert env["ld"]["lift_n"] > 0.0 and env["ld"]["drag_n"] > 0.0
    assert 1.95 <= env["mach"] <= 2.05
    assert env["rng"] > 0.0


def test_domain_control():
    code = """
use control
step state space a [[1.0, 0.1], [0.0, 1.0]] b [0.0, 0.1] state [0.0, 0.0] input 1.0 into ss_step
step kalman filter prior 10.0 cov 1.0 measurement 10.5 noise 0.5 into k_step
calculate pid step for error 10.0 dt 0.1 integral 5.0 prev_err 8.0 kp 1.0 ki 0.1 kd 0.05 into pid_res
"""
    env = execute(code)
    assert len(env["ss_step"]) == 2
    assert 10.0 <= env["k_step"]["estimate"] <= 10.5
    assert env["pid_res"]["output"] > 0.0


def test_domain_ecology():
    code = """
use ecology
calculate shannon diversity for abundances [50, 30, 20] into shannon
calculate simpson diversity for abundances [50, 30, 20] into simpson
step lotka volterra prey 100.0 pred 10.0 alpha 0.1 beta 0.01 gamma 0.1 delta 0.001 into lv
calculate logistic growth for n0 10.0 r 0.2 k 1000.0 time 5.0 into n_t
"""
    env = execute(code)
    assert 1.0 <= env["shannon"] <= 1.1
    assert 0.6 <= env["simpson"] <= 0.7
    assert "prey" in env["lv"] and "predator" in env["lv"]
    assert env["n_t"] > 10.0


def test_domain_epidemiology():
    code = """
use epidemiology
calculate reproduction number r0 for beta 0.5 gamma 0.2 into r0
calculate herd immunity threshold for r0 2.5 into hit
step sir model s 990.0 i 10.0 r 0.0 beta 0.3 gamma 0.1 into sir
"""
    env = execute(code)
    assert env["r0"] == 2.5
    assert env["hit"] == 60.0
    assert env["sir"]["s"] < 990.0 and env["sir"]["i"] > 10.0


def test_domain_logistics():
    code = """
use logistics
calculate economic order quantity for demand 1000.0 order cost 20.0 holding cost 2.0 into eoq
calculate reorder point for lead time 5.0 daily demand 50.0 safety stock 10.0 into rop
calculate safety stock for z 1.65 std demand 10.0 lead time 4.0 into ss
solve tsp nearest neighbor for matrix [[0, 10, 15], [10, 0, 20], [15, 20, 0]] into tsp_res
"""
    env = execute(code)
    assert 140.0 <= env["eoq"] <= 142.0
    assert env["rop"] == 260.0
    assert env["ss"] == 33.0
    assert "tour" in env["tsp_res"]


def test_domain_forensics():
    code = """
use forensics
identify file type by magic bytes "%PDF-1.4" into ftype
calculate shannon entropy for data "AAABBBCCCDDD" into entropy
deobfuscate nested base64 "VjJ0a1MySnVTWGhhUjNocFlsZDRjZz09" into decoded
"""
    env = execute(code)
    assert env["ftype"] == "PDF document"
    assert 1.9 <= env["entropy"] <= 2.1
    assert isinstance(env["decoded"], str)


def test_domain_microecon():
    code = """
use microecon
calculate price elasticity for q1 100.0 q2 80.0 p1 10.0 p2 12.0 into ped
calculate surplus for p_max 50.0 p_min 10.0 price 30.0 quantity 100.0 into surplus
calculate deadweight loss for tax 5.0 quantity reduction 20.0 into dwl
calculate gini coefficient for incomes [10.0, 20.0, 30.0, 40.0] into gini
"""
    env = execute(code)
    assert abs(env["ped"]) > 0.0
    assert "consumer_surplus" in env["surplus"] and "producer_surplus" in env["surplus"]
    assert env["dwl"] == 50.0
    assert 0.0 <= env["gini"] <= 1.0


def test_domain_risk():
    code = """
use risk
calculate historical var for returns [-0.05, -0.02, 0.01, 0.03, 0.04, -0.01] confidence 0.95 into var95
calculate cvar for returns [-0.05, -0.02, 0.01, 0.03, 0.04, -0.01] confidence 0.95 into cvar95
calculate max drawdown for prices [100.0, 120.0, 90.0, 110.0, 80.0, 105.0] into mdd
calculate sharpe ratio for returns [0.02, 0.03, -0.01, 0.04, 0.01] risk free 0.005 into sharpe
calculate sortino ratio for returns [0.02, 0.03, -0.01, 0.04, 0.01] target 0.0 into sortino
"""
    env = execute(code)
    assert env["var95"] >= 0.02
    assert env["cvar95"] >= 0.02
    assert env["mdd"]["max_drawdown"] > 0.3
    assert env["sharpe"] > 0.0
    assert env["sortino"] > 0.0


def test_domain_social():
    code = """
use social
calculate degree centrality for graph {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B", "D"], "D": ["C"]} into deg
calculate closeness centrality for graph {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B", "D"], "D": ["C"]} into close
calculate network density for graph {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B", "D"], "D": ["C"]} into density
calculate clustering coefficient for graph {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B", "D"], "D": ["C"]} into clust
"""
    env = execute(code)
    assert env["deg"]["C"] == 1.0  # C connects to all other 3 nodes
    assert env["close"]["C"] == 1.0
    assert 0.6 <= env["density"] <= 0.7
    assert env["clust"] > 0.0


def test_domain_linguistics():
    code = """
use linguistics
calculate edit distance for word1 "kitten" word2 "sitting" into dist
calculate soundex for word "Robert" into robert_code
calculate soundex for word "Rupert" into rupert_code
calculate syllables for word "DoomScript" into syl
calculate flesch readability for text "The cat sat on the mat. It was a good cat." into flesch
calculate lexical diversity for text "one two three one two" into ttr
"""
    env = execute(code)
    assert env["dist"] == 3
    assert env["robert_code"] == env["rupert_code"] == "R163"
    assert env["syl"] >= 2
    assert env["flesch"] > 80.0
    assert env["ttr"] == 0.6


def test_domain_geophysics():
    code = """
use geophysics
calculate epicentral distance for p arrival 10.0 s arrival 25.0 into dist
calculate richter magnitude for amplitude 100.0 distance 50.0 into mag
calculate seismic refraction for angle 30.0 v1 5.0 v2 8.0 into angle_refract
calculate bouguer anomaly for observed 980000.0 theoretical 979950.0 elevation 100.0 into bouguer
calculate geothermal heat flow for conductivity 2.5 gradient 30.0 into q_flow
"""
    env = execute(code)
    assert env["dist"] > 0.0
    assert env["mag"] > 0.0
    assert env["angle_refract"] > 30.0
    assert env["bouguer"] != 0.0
    assert env["q_flow"] == 75.0


def test_domain_synthetic_bio():
    code = """
use synthetic_bio
calculate hill activation for conc 2.0 k 1.0 n 2.0 into act
calculate hill repression for conc 2.0 k 1.0 n 2.0 into rep
step toggle switch u 1.0 v 0.1 into tog
step repressilator p1 1.0 p2 0.5 p3 0.2 into rep_res
calculate codon adaptation index for seq "AUGGCCAUG" weights {"AUG": 1.0, "GCC": 0.8} into cai
"""
    env = execute(code)
    assert env["act"] == 0.8  # 2^2 / (1^2 + 2^2) = 4/5 = 0.8
    assert env["rep"] == 0.2  # 1 / (1 + 2^2) = 1/5 = 0.2
    assert "u" in env["tog"] and "v" in env["tog"]
    assert "p1" in env["rep_res"] and "p2" in env["rep_res"] and "p3" in env["rep_res"]
    assert env["cai"] > 0.5
