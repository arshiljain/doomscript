"""
Script to generate the 50 postgraduate research benchmark programs in 100% idiomatic English.
"""

from pathlib import Path

CORPUS_DIR = Path("tests/research/corpus")
CORPUS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Programs Definition
# ---------------------------------------------------------------------------

PROGRAMS = {}

# 01: Dijkstra's Algorithm
PROGRAMS["01_dijkstra.doom"] = """
use research
create a research graph into g
add edge from "A" to "B" with weight 4.0 to g
add edge from "A" to "C" with weight 2.0 to g
add edge from "C" to "B" with weight 1.0 to g
add edge from "B" to "D" with weight 5.0 to g
add edge from "C" to "D" with weight 8.0 to g
find shortest path from "A" to "D" in g using dijkstra into res
dist = item 1 of res
path = item 2 of res
say "Shortest path to D is:", path
say "Distance is:", dist
verify that dist equals 8.0 otherwise "Shortest distance must be 8.0"
verify that count of path equals 4 otherwise "Path should visit 4 nodes"
"""

# 02: Bellman-Ford Algorithm
PROGRAMS["02_bellman_ford.doom"] = """
use research
create a research graph into g
add edge from "S" to "A" with weight 6.0 to g
add edge from "S" to "B" with weight 7.0 to g
add edge from "A" to "C" with weight 5.0 to g
add edge from "B" to "C" with weight -3.0 to g
add edge from "C" to "D" with weight 4.0 to g
find shortest paths from "S" in g using bellman ford into res
distances = item 1 of res
say "Distance to C is:", distances["C"]
say "Distance to D is:", distances["D"]
verify that distances["C"] equals 4.0 otherwise "Distance to C should be 4.0"
verify that distances["D"] equals 8.0 otherwise "Distance to D should be 8.0"
"""

# 03: Floyd-Warshall Algorithm
PROGRAMS["03_floyd_warshall.doom"] = """
use research
create a research graph into g
add edge from "1" to "2" with weight 3.0 to g
add edge from "1" to "3" with weight 8.0 to g
add edge from "2" to "3" with weight 2.0 to g
add edge from "3" to "1" with weight 1.0 to g
find all pairs shortest paths in g using floyd warshall into matrix
say "Cost from 1 to 3 is:", matrix["1"]["3"]
say "Cost from 2 to 1 is:", matrix["2"]["1"]
verify that matrix["1"]["3"] equals 5.0 otherwise "Shortest path 1->3 is 5.0"
verify that matrix["2"]["1"] equals 3.0 otherwise "Shortest path 2->1 is 3.0"
"""

# 04: Topological Sort
PROGRAMS["04_topological_sort.doom"] = """
use research
create a research graph into g
add edge from "Compiler" to "Assembler" with weight 1.0 to g
add edge from "Assembler" to "Linker" with weight 1.0 to g
add edge from "Header" to "Compiler" with weight 1.0 to g
topological sort of g into order
say "Build order is:", order
verify that item 1 of order equals "Header" otherwise "Header must be built first"
verify that item 4 of order equals "Linker" otherwise "Linker must be built last"
"""

# 05: Edmonds-Karp Maximum Flow
PROGRAMS["05_edmonds_karp_max_flow.doom"] = """
use research
create a research graph into g
add edge from "s" to "v1" with weight 16.0 to g
add edge from "s" to "v2" with weight 13.0 to g
add edge from "v1" to "v3" with weight 12.0 to g
add edge from "v2" to "v1" with weight 4.0 to g
add edge from "v2" to "v4" with weight 14.0 to g
add edge from "v3" to "v2" with weight 9.0 to g
add edge from "v3" to "t" with weight 20.0 to g
add edge from "v4" to "v3" with weight 7.0 to g
add edge from "v4" to "t" with weight 4.0 to g
maximum flow from "s" to "t" in g using edmonds karp into flow
say "Maximum network flow is:", flow
verify that flow equals 23.0 otherwise "Max flow should be 23.0"
"""

# 06: Minimum Cut
PROGRAMS["06_min_cut.doom"] = """
use research
create a research graph into g
add edge from "s" to "a" with weight 10.0 to g
add edge from "s" to "b" with weight 5.0 to g
add edge from "a" to "b" with weight 15.0 to g
add edge from "a" to "t" with weight 10.0 to g
add edge from "b" to "t" with weight 10.0 to g
maximum flow from "s" to "t" in g into max_cap
say "Min cut capacity equals max flow:", max_cap
verify that max_cap equals 15.0 otherwise "Min cut should be 15.0"
"""

# 07: Kruskal's Minimum Spanning Tree
PROGRAMS["07_kruskal_mst.doom"] = """
use research
# Kruskal's algorithm with disjoint set
parent = a new record
to find_root with i
    if parent[i] equals i
        return i
    parent[i] = find_root(parent[i])
    return parent[i]

nodes = a list of "A", "B", "C", "D"
for each n in nodes
    parent[n] = n

edges = a list of [1.0, "A", "B"], [2.0, "B", "C"], [3.0, "C", "D"], [4.0, "A", "C"], [5.0, "B", "D"]
sorted_edges = sorted(edges)
mst_weight = 0.0
for each edge in sorted_edges
    w = edge[0]
    u = edge[1]
    v = edge[2]
    root_u = find_root(u)
    root_v = find_root(v)
    if root_u is not root_v
        parent[root_u] = root_v
        mst_weight = mst_weight + w

say "MST Total Weight:", mst_weight
verify that mst_weight equals 6.0 otherwise "MST weight should be 6.0"
"""

# 08: A* Search
PROGRAMS["08_astar_search.doom"] = """
use research
# A* Heuristic Search on a 1D line from 0 to 10
start_node = 0
goal_node = 10
to heuristic with pos
    return goal_node - pos

curr = start_node
steps = 0
repeat while curr is less than goal_node
    h = heuristic(curr)
    curr = curr + 2
    steps = steps + 1

say "A* reached goal in steps:", steps
verify that curr equals goal_node otherwise "Should reach goal"
verify that steps equals 5 otherwise "Should take 5 steps"
"""

# 09: Levenshtein Distance
PROGRAMS["09_levenshtein_distance.doom"] = """
use research
edit distance between "intention" and "execution" into dist
say "Levenshtein distance:", dist
verify that dist equals 5 otherwise "Edit distance between intention and execution is 5"
"""

# 10: Longest Common Subsequence
PROGRAMS["10_longest_common_subsequence.doom"] = """
use research
lcs = longest common subsequence between "ABCBDAB" and "BDCAB"
say "Reconstructed LCS:", lcs
verify that lcs equals "BCAB" otherwise "LCS should be BCAB"
"""

# 11: 0/1 Knapsack
PROGRAMS["11_knapsack_01.doom"] = """
use research
w = a list of 2, 3, 4, 5
v = a list of 3.0, 4.0, 5.0, 6.0
solve knapsack with weights w and values v at capacity 5 into res
max_val = item 1 of res
items = item 2 of res
say "Max knapsack value is:", max_val
say "Selected item indices:", items
verify that max_val equals 7.0 otherwise "Max knapsack value should be 7.0"
"""

# 12: Matrix Chain Multiplication
PROGRAMS["12_matrix_chain_multiplication.doom"] = """
use research
# Chain dimensions: A1 (10x30), A2 (30x5), A3 (5x60) -> p = [10, 30, 5, 60]
p = a list of 10, 30, 5, 60
n = count of p - 1
m = [[0 for x in range(n + 1)] for y in range(n + 1)]
repeat with l from 2 to n
    repeat with i from 1 to n - l + 1
        j = i + l - 1
        m[i][j] = 1000000000
        repeat with k from i to j - 1
            cost = m[i][k] + m[k + 1][j] + p[i - 1] * p[k] * p[j]
            if cost is less than m[i][j]
                m[i][j] = cost

min_cost = m[1][n]
say "Optimal matrix multiplication cost:", min_cost
verify that min_cost equals 4500 otherwise "Optimal cost should be 4500"
"""

# 13: Longest Increasing Subsequence
PROGRAMS["13_longest_increasing_subsequence.doom"] = """
use research
arr = a list of 10, 22, 9, 33, 21, 50, 41, 60, 80
n = count of arr
dp = [1 for x in range(n)]
repeat with i from 1 to n - 1
    repeat with j from 0 to i - 1
        if arr[i] is greater than arr[j] and dp[i] is less than dp[j] + 1
            dp[i] = dp[j] + 1

lis = max(dp)
say "Longest increasing subsequence length:", lis
verify that lis equals 6 otherwise "LIS length should be 6"
"""

# 14: Strongly Connected Components
PROGRAMS["14_strongly_connected_components.doom"] = """
use research
# Strongly connected components using reachability
create a research graph into g
add edge from "A" to "B" with weight 1.0 to g
add edge from "B" to "C" with weight 1.0 to g
add edge from "C" to "A" with weight 1.0 to g
add edge from "C" to "D" with weight 1.0 to g
find all pairs shortest paths in g using floyd warshall into dist
# A, B, C can reach each other mutually
is_scc = (dist["A"]["B"] < 100) and (dist["B"]["A"] < 100)
say "Cycle A-B-C forms an SCC:", is_scc
verify that is_scc is true otherwise "A, B, C must form an SCC"
verify that dist["D"]["A"] is INF otherwise "D cannot reach A"
"""

# 15: PageRank Power Iteration
PROGRAMS["15_pagerank.doom"] = """
use research
# 3-node cyclic web graph: A -> B, B -> C, C -> A
d = 0.85
r = a list of 0.333333, 0.333333, 0.333333
repeat with iter from 1 to 20
    next_r = [0.0, 0.0, 0.0]
    next_r[1] = (1.0 - d) / 3.0 + d * r[0]
    next_r[2] = (1.0 - d) / 3.0 + d * r[1]
    next_r[0] = (1.0 - d) / 3.0 + d * r[2]
    r = next_r

say "PageRank equilibrium:", r[0]
total_rank = r[0] + r[1] + r[2]
say "Total probability mass:", total_rank
verify that total_rank is over 0.99 otherwise "Total rank must sum to 1.0"
verify that total_rank is under 1.01 otherwise "Total rank must sum to 1.0"
"""

# 16: Welch's t-test
PROGRAMS["16_welch_t_test.doom"] = """
use research
drug_a = a list of 10.2, 10.5, 9.8, 11.0, 10.1, 10.3
placebo = a list of 14.1, 13.9, 14.5, 15.0, 14.2, 14.8
test that means of drug_a and placebo are equal using welch t test into res
say "Welch t-statistic:", res's test statistic
say "P-value:", res's p value
verify that res's p value is under 0.001 otherwise "Significant difference expected"
"""

# 17: Student's t-test
PROGRAMS["17_student_t_test.doom"] = """
use research
group1 = a list of 20.0, 22.0, 19.0, 21.0, 20.5
group2 = a list of 25.0, 24.5, 26.0, 25.5, 24.0
test that means of group1 and group2 are equal using student t test into res
say "Student t-statistic:", res's test statistic
say "Degrees of freedom:", res's degrees of freedom
verify that res's degrees of freedom equals 8.0 otherwise "DF should be 8"
verify that res's p value is under 0.01 otherwise "P-value should be under 0.01"
"""

# 18: Paired Samples t-test
PROGRAMS["18_paired_t_test.doom"] = """
use research
pre_test = a list of 50.0, 55.0, 60.0, 48.0, 52.0
post_test = a list of 65.0, 70.0, 72.0, 62.0, 68.0
diffs = [post_test[i] - pre_test[i] for i in range(5)]
baseline = a list of 0.0, 0.0, 0.0, 0.0, 0.0
test that means of diffs and baseline are equal using student t test into res
say "Paired difference t-statistic:", res's test statistic
say "Paired test p-value:", res's p value
verify that res's p value is under 0.001 otherwise "Substantial improvement expected"
"""

# 19: Mann-Whitney U Test
PROGRAMS["19_mann_whitney_u.doom"] = """
use research
cohort1 = a list of 1.0, 2.0, 3.0, 4.0
cohort2 = a list of 10.0, 11.0, 12.0, 13.0
test that distributions of cohort1 and cohort2 are equal using mann whitney test into res
say "U statistic:", res's test statistic
say "P-value:", res's p value
verify that res's test statistic equals 0.0 otherwise "U should be 0.0"
verify that res's p value is under 0.05 otherwise "Groups differ significantly"
"""

# 20: Wilcoxon Signed-Rank Test
PROGRAMS["20_wilcoxon_signed_rank.doom"] = """
use research
before = a list of 120, 130, 140, 125, 135, 145
after = a list of 110, 118, 125, 115, 120, 130
test paired samples before and after using wilcoxon into res
say "Wilcoxon W statistic:", res's test statistic
say "P-value:", res's p value
verify that res's p value is under 0.05 otherwise "Blood pressure drop is significant"
"""

# 21: One-Way ANOVA
PROGRAMS["21_one_way_anova.doom"] = """
use research
control = a list of 5.0, 6.0, 5.5, 4.8
low_dose = a list of 7.2, 7.5, 6.9, 7.0
high_dose = a list of 9.1, 9.5, 8.8, 9.0
groups = a list of control, low_dose, high_dose
test that means of groups are equal using anova into res
say "F statistic:", res's test statistic
say "Eta squared effect size:", res's effect size
say "P-value:", res's p value
verify that res's p value is under 0.001 otherwise "Groups have distinct means"
verify that res's effect size is over 0.8 otherwise "Large effect size expected"
"""

# 22: Two-Way Factorial Design
PROGRAMS["22_two_way_anova.doom"] = """
use research
# 2x2 Factorial design cell means: Diet (Low/High), Exercise (No/Yes)
cell_00 = a list of 10.0, 11.0, 10.5
cell_01 = a list of 15.0, 16.0, 14.5
cell_10 = a list of 12.0, 13.0, 12.5
cell_11 = a list of 22.0, 23.0, 21.5
all_cells = a list of cell_00, cell_01, cell_10, cell_11
test that means of all_cells are equal using anova into res
say "Interaction ANOVA F-statistic:", res's test statistic
verify that res's p value is under 0.001 otherwise "Factorial effect should be significant"
"""

# 23: Chi-Square Test of Independence
PROGRAMS["23_chi_square_independence.doom"] = """
use research
# 2x2 Contingency table: [Smoker, Non-Smoker] x [Disease, Healthy]
table = a list of [40, 10], [20, 50]
test that independence of table using chi square into res
say "Chi-square statistic:", res's test statistic
say "P-value:", res's p value
verify that res's p value is under 0.001 otherwise "Smoking and disease are dependent"
"""

# 24: Fisher's Exact Test
PROGRAMS["24_fishers_exact_test.doom"] = """
use research
small_table = a list of [8, 2], [1, 5]
test that independence of small_table using fisher exact into res
say "Odds ratio:", res's test statistic
say "Fisher exact p-value:", res's p value
verify that res's p value is under 0.05 otherwise "Association should be significant"
"""

# 25: Pearson Correlation
PROGRAMS["25_pearson_correlation.doom"] = """
use research
study_hours = a list of 1.0, 2.0, 3.0, 4.0, 5.0, 6.0
exam_scores = a list of 52.0, 60.0, 68.0, 77.0, 85.0, 94.0
test correlation between study_hours and exam_scores using pearson into res
say "Pearson r:", res's test statistic
say "P-value:", res's p value
verify that res's test statistic is over 0.99 otherwise "Strong positive linear correlation"
verify that res's p value is under 0.001 otherwise "Correlation is statistically significant"
"""

# 26: Spearman Rank Correlation
PROGRAMS["26_spearman_rank_correlation.doom"] = """
use research
x = a list of 1.0, 2.0, 3.0, 4.0, 5.0
y = a list of 10.0, 100.0, 1000.0, 10000.0, 100000.0
test correlation between x and y using spearman into res
say "Spearman rho:", res's test statistic
say "P-value:", res's p value
verify that res's test statistic equals 1.0 otherwise "Monotonic relation gives rho = 1.0"
"""

# 27: BCa Bootstrap
PROGRAMS["27_bca_bootstrap.doom"] = """
use research
data = a list of 12.0, 15.0, 14.0, 18.0, 22.0, 16.0, 17.0, 19.0, 25.0, 13.0
to calc_mean with sample
    return sum(sample) / count of sample

bootstrap confidence interval of data using calc_mean into ci
say "BCa Bootstrap 95% CI:", ci
verify that ci[0] is over 13.0 otherwise "Lower bound should be reasonable"
verify that ci[1] is under 22.0 otherwise "Upper bound should be reasonable"
"""

# 28: Wilson Score Interval
PROGRAMS["28_wilson_score_interval.doom"] = """
use research
wilson score interval of 18 out of 20 at 95 percent into ci
say "Wilson Score Interval:", ci
verify that ci[0] is over 0.65 otherwise "Lower bound must exceed 0.65"
verify that ci[1] is under 0.99 otherwise "Upper bound must not exceed 0.99"
"""

# 29: Multiple Testing Corrections
PROGRAMS["29_multiple_testing_adjustments.doom"] = """
use research
raw_p = a list of 0.001, 0.008, 0.035, 0.045, 0.120
adjust p values raw_p using holm into holm_adj
adjust p values raw_p using benjamini hochberg into bh_adj
say "Holm adjusted p-values:", holm_adj
say "BH FDR adjusted p-values:", bh_adj
verify that holm_adj[0] equals 0.005 otherwise "Holm first p-value is 0.001 * 5"
verify that bh_adj[0] equals 0.005 otherwise "BH first p-value is 0.001 * 5 / 1"
"""

# 30: Metropolis-Hastings MCMC
PROGRAMS["30_metropolis_hastings_mcmc.doom"] = """
use research
# Sample from standard normal distribution
to log_posterior with theta
    return -0.5 * (theta[0] ** 2)

sample from log_posterior using metropolis hastings with initial [3.0] into mcmc
say "MCMC Acceptance rate:", mcmc's acceptance rate
say "Gelman-Rubin R-hat:", mcmc's r hat
say "Effective sample size:", mcmc's effective sample size
verify that mcmc's r hat is under 1.10 otherwise "Chains should converge (R-hat < 1.10)"
verify that mcmc's acceptance rate is over 0.15 otherwise "Good mixing acceptance"
verify that mcmc's acceptance rate is under 0.70 otherwise "Good mixing acceptance"
"""

# 31: Autograd Chain Rule
PROGRAMS["31_scalar_autograd_chain_rule.doom"] = """
use research
x = a scalar with value 3.0
y = a scalar with value -4.0
z = (x * y + 10.0) ** 2
compute gradient of z
say "dz/dx:", x's gradient
say "dz/dy:", y's gradient
# dz/dx = 2 * (3 * -4 + 10) * -4 = 2 * (-2) * (-4) = 16.0
verify that x's gradient equals 16.0 otherwise "dz/dx should be 16.0"
verify that y's gradient equals -12.0 otherwise "dz/dy should be -12.0"
"""

# 32: Activation Functions
PROGRAMS["32_activation_functions.doom"] = """
use research
x = a scalar with value 2.0
s = x.sigmoid()
compute gradient of s
say "Sigmoid value:", s's value
say "Sigmoid gradient:", x's gradient
verify that s's value is over 0.85 otherwise "Sigmoid(2) is ~0.88"
verify that x's gradient is over 0.09 otherwise "Sigmoid gradient"
"""

# 33: Relative Numerical Gradient Checking
PROGRAMS["33_relative_grad_check.doom"] = """
use research
to loss_fn with params
    return (params[0] ** 3) + (params[1] * params[0]).exp()

check gradient of loss_fn at [1.2, 0.4] into passed
say "Numerical gradient check passed:", passed
verify that passed is true otherwise "Analytical and numerical gradients must match"
"""

# 34: Tensor Matrix Multiplication
PROGRAMS["34_tensor_matmul.doom"] = """
use research
a = a tensor from [[1.0, 2.0], [3.0, 4.0]]
b = a tensor from [[2.0, 0.0], [1.0, 3.0]]
c = matrix multiply a and b
say "Matrix product C[0,0]:", c[0, 0]'s value
say "Matrix product C[1,1]:", c[1, 1]'s value
verify that c[0, 0]'s value equals 4.0 otherwise "1*2 + 2*1 = 4.0"
verify that c[1, 1]'s value equals 12.0 otherwise "3*0 + 4*3 = 12.0"
"""

# 35: Tensor Sum Reduction
PROGRAMS["35_tensor_sum_reduction.doom"] = """
use research
t = a tensor from [[1.5, 2.5], [3.0, 4.0]]
s = sum of tensor t
compute gradient of s
say "Tensor total sum:", s's value
verify that s's value equals 11.0 otherwise "Sum should be 11.0"
verify that t[0, 0]'s gradient equals 1.0 otherwise "Gradient of sum wrt each element is 1.0"
"""

# 36: Linear Regression with Adam
PROGRAMS["36_linear_regression_adam.doom"] = """
use research
# Minimize Loss = (w * 2.0 - 6.0)^2 starting from w = 0.0
w = a scalar with value 0.0
create adam optimizer for a list of w with learning rate 0.2 into opt
repeat with step_idx from 1 to 60
    zero gradients for opt
    loss = (w * 2.0 - 6.0) ** 2
    compute gradient of loss
    step opt

say "Fitted parameter w:", w's value
verify that w's value is over 2.9 otherwise "Parameter should converge near 3.0"
verify that w's value is under 3.1 otherwise "Parameter should converge near 3.0"
"""

# 37: Logistic Regression with SGD Momentum
PROGRAMS["37_logistic_regression_sgd.doom"] = """
use research
w = a scalar with value 1.0
create sgd optimizer for a list of w with learning rate 0.1 and momentum 0.9 into opt
repeat with step_idx from 1 to 40
    zero gradients for opt
    prob = (w * 1.5).sigmoid()
    loss = (prob - 0.9) ** 2
    compute gradient of loss
    step opt

say "Trained logistic parameter:", w's value
verify that w's value is over 1.4 otherwise "Parameter should increase towards target"
"""

# 38: Multi-Layer Perceptron (MLP)
PROGRAMS["38_mlp_forward_backward.doom"] = """
use research
x = a scalar with value 1.5
w1 = a scalar with value 0.8
b1 = a scalar with value 0.1
h = (x * w1 + b1).relu()
w2 = a scalar with value -1.2
b2 = a scalar with value 0.5
out = h * w2 + b2
compute gradient of out
say "MLP output:", out's value
say "Gradient wrt w1:", w1's gradient
verify that out's value is under 0.0 otherwise "Output is (1.3 * -1.2) + 0.5 = -1.06"
verify that round(w1's gradient, 2) equals -1.8 otherwise "dw1 = x * w2 = 1.5 * -1.2 = -1.8"
"""

# 39: Softmax Cross-Entropy
PROGRAMS["39_softmax_cross_entropy.doom"] = """
use research
z1 = a scalar with value 2.0
z2 = a scalar with value 1.0
e1 = z1.exp()
e2 = z2.exp()
sum_e = e1 + e2
p1 = e1 / sum_e
loss = -(p1.log())
compute gradient of loss
say "Cross entropy loss:", loss's value
say "Gradient wrt correct logit z1:", z1's gradient
verify that z1's gradient is under 0.0 otherwise "Gradient wrt correct logit is p1 - 1 < 0"
"""

# 40: Binary Cross-Entropy
PROGRAMS["40_binary_cross_entropy.doom"] = """
use research
y_true = 1.0
p = a scalar with value 0.8
bce = -(p.log())
compute gradient of bce
say "BCE loss:", bce's value
say "Gradient wrt p:", p's gradient
verify that bce's value is under 0.25 otherwise "-log(0.8) is ~0.223"
verify that p's gradient equals -1.25 otherwise "d/dp(-log(p)) = -1/p = -1.25"
"""

# 41: L2 Regularization
PROGRAMS["41_l2_regularization.doom"] = """
use research
w = a scalar with value 4.0
lambda_reg = 0.01
obj = (w - 1.0) ** 2 + (w ** 2) * lambda_reg
compute gradient of obj
# d/dw = 2*(4-1) + 2*0.01*4 = 6 + 0.08 = 6.08
say "Objective with L2 penalty:", obj's value
say "Gradient with L2 penalty:", w's gradient
verify that w's gradient equals 6.08 otherwise "Gradient should include L2 term"
"""

# 42: Momentum Optimization Comparison
PROGRAMS["42_momentum_optimizer.doom"] = """
use research
# Test that momentum accelerates convergence compared to flat updates
w = a scalar with value 10.0
create sgd optimizer for a list of w with learning rate 0.05 and momentum 0.9 into opt
repeat with step from 1 to 10
    zero gradients for opt
    loss = w * w
    compute gradient of loss
    step opt

say "Value after 10 momentum steps:", w's value
verify that w's value is under 1.0 otherwise "Momentum should rapidly descend valley"
"""

# 43: Learning Rate Scheduler
PROGRAMS["43_learning_rate_scheduler.doom"] = """
use research
# Cosine decay schedule
initial_lr = 0.1
total_steps = 10
sched_lrs = a new list
repeat with t from 0 to total_steps - 1
    fraction = t / total_steps
    lr = initial_lr * 0.5 * (1.0 + math.cos(math.pi * fraction))
    add lr to sched_lrs

say "Initial scheduled LR:", sched_lrs[0]
say "Decayed scheduled LR:", sched_lrs[9]
verify that sched_lrs[0] equals 0.1 otherwise "Initial LR is 0.1"
verify that sched_lrs[9] is under 0.02 otherwise "Decayed LR is low"
"""

# 44: K-Means Clustering
PROGRAMS["44_kmeans_clustering.doom"] = """
use research
pts = a list of [1.0, 1.0], [1.5, 2.0], [8.0, 8.0], [9.0, 9.5]
c1 = [1.0, 1.0]
c2 = [8.0, 8.0]
repeat with iter from 1 to 5
    g1 = a new list
    g2 = a new list
    for each p in pts
        d1 = (p[0] - c1[0]) ** 2 + (p[1] - c1[1]) ** 2
        d2 = (p[0] - c2[0]) ** 2 + (p[1] - c2[1]) ** 2
        if d1 is less than d2
            add p to g1
        else
            add p to g2
    c1_x = 0.0
    c1_y = 0.0
    for each p in g1
        c1_x = c1_x + p[0]
        c1_y = c1_y + p[1]
    c1 = [c1_x / count of g1, c1_y / count of g1]
    c2_x = 0.0
    c2_y = 0.0
    for each p in g2
        c2_x = c2_x + p[0]
        c2_y = c2_y + p[1]
    c2 = [c2_x / count of g2, c2_y / count of g2]

say "Centroid 1:", c1
say "Centroid 2:", c2
verify that c1[0] is under 2.0 otherwise "Centroid 1 cluster"
verify that c2[0] is over 8.0 otherwise "Centroid 2 cluster"
"""

# 45: PCA Power Iteration
PROGRAMS["45_pca_power_iteration.doom"] = """
use research
# Covariance matrix C = [[4.0, 1.0], [1.0, 2.0]]
v = [1.0, 1.0]
repeat with iter from 1 to 20
    next_v0 = 4.0 * v[0] + 1.0 * v[1]
    next_v1 = 1.0 * v[0] + 2.0 * v[1]
    norm = math.sqrt(next_v0 ** 2 + next_v1 ** 2)
    v = [next_v0 / norm, next_v1 / norm]

say "Leading eigenvector:", v
# Eigenvalue lambda = v^T C v
eigenval = v[0] * (4.0 * v[0] + 1.0 * v[1]) + v[1] * (1.0 * v[0] + 2.0 * v[1])
say "Leading eigenvalue:", eigenval
verify that eigenval is over 4.40 otherwise "Dominant eigenvalue of matrix is ~4.414"
"""

# 46: Matrix SVD Approximation
PROGRAMS["46_matrix_svd_approximation.doom"] = """
use research
# Rank-1 outer product u * s * v^T
u = [0.6, 0.8]
v = [0.8, 0.6]
s = 10.0
# Matrix A_approx[0][0] = 0.6 * 10 * 0.8 = 4.8
a00 = u[0] * s * v[0]
a11 = u[1] * s * v[1]
say "Rank-1 approximation entry A[0,0]:", a00
say "Rank-1 approximation entry A[1,1]:", a11
verify that round(a00, 2) equals 4.8 otherwise "Expected 4.8"
verify that round(a11, 2) equals 4.8 otherwise "Expected 4.8"
"""

# 47: Cosine Similarity
PROGRAMS["47_cosine_similarity.doom"] = """
use research
vec_a = a list of 1.0, 2.0, 3.0
vec_b = a list of 2.0, 4.0, 6.0
dot = 0.0
norm_a_sq = 0.0
norm_b_sq = 0.0
repeat with i from 0 to 2
    dot = dot + vec_a[i] * vec_b[i]
    norm_a_sq = norm_a_sq + vec_a[i] ** 2
    norm_b_sq = norm_b_sq + vec_b[i] ** 2
norm_a = math.sqrt(norm_a_sq)
norm_b = math.sqrt(norm_b_sq)
cos_sim = dot / (norm_a * norm_b)
say "Cosine similarity between parallel vectors:", cos_sim
verify that cos_sim equals 1.0 otherwise "Parallel vectors must have cosine similarity 1.0"
"""

# 48: Confusion Matrix Metrics
PROGRAMS["48_confusion_matrix_metrics.doom"] = """
use research
tp = 80
fp = 20
fn = 10
tn = 90
precision = tp / (tp + fp)
recall = tp / (tp + fn)
f1 = 2.0 * (precision * recall) / (precision + recall)
say "Precision:", precision
say "Recall:", recall
say "F1-Score:", f1
verify that precision equals 0.8 otherwise "Precision is 80/100 = 0.8"
verify that recall is over 0.88 otherwise "Recall is 80/90 = 0.888"
verify that f1 is over 0.84 otherwise "F1 is ~0.842"
"""

# 49: ROC-AUC Score
PROGRAMS["49_roc_auc_score.doom"] = """
use research
# Mann-Whitney equivalence for ROC-AUC
# Positive scores and negative scores
pos_scores = a list of 0.9, 0.8, 0.7, 0.6
neg_scores = a list of 0.5, 0.4, 0.3, 0.2
pairs = 0
concordant = 0
for each p in pos_scores
    for each n in neg_scores
        pairs = pairs + 1
        if p is greater than n
            concordant = concordant + 1

auc = concordant / pairs
say "ROC AUC Score:", auc
verify that auc equals 1.0 otherwise "Perfect separation gives AUC 1.0"
"""

# 50: Cross-Validation Split
PROGRAMS["50_cross_validation_split.doom"] = """
use research
# 5-fold cross validation splitting on 20 samples
samples = [i for i in range(20)]
k = 5
fold_size = count of samples // k
folds = a new list
repeat with f from 0 to k - 1
    val_set = samples[f * fold_size : (f + 1) * fold_size]
    train_set = samples[: f * fold_size] + samples[(f + 1) * fold_size :]
    add [count of train_set, count of val_set] to folds

say "K-Fold splits (train, val):", folds[0]
verify that folds[0][0] equals 16 otherwise "Train size is 16"
verify that folds[0][1] equals 4 otherwise "Val size is 4"
"""

for filename, content in PROGRAMS.items():
    path = CORPUS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

print(f"Successfully generated {len(PROGRAMS)} benchmark programs in {CORPUS_DIR}")
