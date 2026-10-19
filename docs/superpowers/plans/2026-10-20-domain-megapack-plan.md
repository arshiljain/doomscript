# 30,000 LOC Domain MegaPack & Deepening Master Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 30,000+ lines of high-leverage spoken-English code across 7 brand-new domain packs and deep algorithmic expansions across all 18 existing domains with 100% test coverage and zero regressions.

**Architecture:** 
1. Build 7 new domain modules (`bio`, `physics`, `sec`, `game`, `quantum`, `circuit`, `chain`) following the standard domain architecture (`__init__.py`, `parser.py`, `runtime.py`, `exporter.py`).
2. Deepen all 18 existing domains with advanced algorithmic engines, state machines, and analytic routines.
3. Integrate all runtime engines via `src/doomscript/runtime.py` and register with `DomainRegistry`.
4. Enforce pure Python standard library implementations with zero mandatory external dependencies, zero semicolons, and strictly positional AST arguments.

**Tech Stack:** Python 3.10+, Lark parser, standard library `math`, `collections`, `itertools`, `re`, `struct`, `hashlib`, `random`, `time`, `typing`.

**Spec:** `docs/superpowers/specs/2026-10-20-domain-megapack-design.md`

## Global Constraints
- Pure spoken-English syntax with zero semicolons or punctuation noise.
- Zero mandatory external dependencies (pure Python standard library).
- Strictly positional arguments when emitting AST calls from domain parsers (`fn(a, b)` not `fn(a, opt=b)`).
- Preserve 100% backwards compatibility and zero regressions across all 580 pre-existing tests.

## Review Focus
- Incomplete input validation on genomic or binary strings gracefully handled.
- Division-by-zero or singular matrices in physics / circuit / finance calculations handled with numeric safety clamps.
- Qubit registers scaling gracefully up to 10 qubits with normalized probabilities.
- Re-exports in `src/doomscript/runtime.py` maintain clean namespace without shadowing built-ins.
- Domain `can_handle_line` regexes strictly bound to avoid intercepting core language assignments or grammar rules.

---

## Tasks Breakdown

### Phase 1: 7 Brand-New Domain Packs (New Horizons)

#### Task 1: Bioinformatics & Computational Biology (`use bio`)
- [ ] Create `src/doomscript/domains/bio/__init__.py` with `BioDomain(DomainContract)`, verb specs, and selective `can_handle_line`.
- [ ] Create `src/doomscript/domains/bio/runtime.py` implementing:
  - `bio_gc_content`, `bio_transcribe_dna`, `bio_translate_rna`, `bio_reverse_complement`.
  - `bio_find_orfs`, `bio_count_kmers`, `bio_find_motif`, `bio_molecular_weight`.
  - `bio_needleman_wunsch` (global alignment with scoring matrix & traceback).
  - `bio_smith_waterman` (local alignment with scoring matrix & traceback).
  - `bio_parse_fasta` (multi-sequence FASTA parser).
- [ ] Create `src/doomscript/domains/bio/parser.py` parsing spoken-English phrases into positional calls.
- [ ] Create `src/doomscript/domains/bio/exporter.py` for AST code generation.

#### Task 2: Physics, Kinematics & Controls (`use physics`)
- [ ] Create `src/doomscript/domains/physics/__init__.py` with `PhysicsDomain` registration.
- [ ] Create `src/doomscript/domains/physics/runtime.py` implementing:
  - `physics_trajectory` (2D ballistic trajectory points with velocity, angle, gravity).
  - `physics_ballistic_range`, `physics_projectile_drag` (numerical drag integrator).
  - `physics_aabb_collision`, `physics_sat_polygon_collision` (Separating Axis Theorem).
  - `physics_spring_damper` (harmonic oscillator simulation states).
  - `physics_orbital_velocity`, `physics_escape_velocity`.
  - `physics_pid_create`, `physics_pid_update` (Proportional-Integral-Derivative controller).
- [ ] Create `src/doomscript/domains/physics/parser.py` and `exporter.py`.

#### Task 3: Cybersecurity, Cryptanalysis & Forensics (`use sec`)
- [ ] Create `src/doomscript/domains/sec/__init__.py` with `SecDomain` registration.
- [ ] Create `src/doomscript/domains/sec/runtime.py` implementing:
  - `sec_password_entropy`, `sec_password_audit` (zxcvbn-style entropy scoring).
  - `sec_caesar_crack` (frequency analysis chi-squared solver).
  - `sec_vigenere_encode`, `sec_vigenere_decode`.
  - `sec_frequency_analysis`, `sec_xor_cipher`.
  - `sec_jwt_decode`, `sec_jwt_verify`.
  - `sec_hexdump` (formatted hex + ASCII view).
  - `sec_cvss_score` (CVSS v3.1 calculator from metric vector).
  - `sec_parse_banner` (banner grabbing service analyzer).
- [ ] Create `src/doomscript/domains/sec/parser.py` and `exporter.py`.

#### Task 4: Game Mechanics, Tilemaps & Dice (`use game`)
- [ ] Create `src/doomscript/domains/game/__init__.py` with `GameDomain` registration.
- [ ] Create `src/doomscript/domains/game/runtime.py` implementing:
  - `game_roll_dice` (dice notation parser `XdY + Z` with min, max, total).
  - `game_loot_table_pick` (weighted random drop table).
  - `game_tilemap_create`, `game_tilemap_set`, `game_tilemap_get`.
  - `game_grid_astar_path` (2D grid obstacle-avoidance A* navigation).
  - `game_line_of_sight` (Bresenham's line algorithm raycasting).
  - `game_combatant_create`, `game_resolve_turn`, `game_apply_buff`.
- [ ] Create `src/doomscript/domains/game/parser.py` and `exporter.py`.

#### Task 5: Quantum Computing Simulation (`use quantum`)
- [ ] Create `src/doomscript/domains/quantum/__init__.py` with `QuantumDomain` registration.
- [ ] Create `src/doomscript/domains/quantum/runtime.py` implementing:
  - `quantum_register_create` ($2^N$ complex state vector representation).
  - `quantum_apply_hadamard`, `quantum_apply_pauli_x`, `quantum_apply_pauli_y`, `quantum_apply_pauli_z`.
  - `quantum_apply_phase`, `quantum_apply_cnot` (entangling controlled-NOT gate).
  - `quantum_measure_qubit`, `quantum_measure_all` (Monte Carlo projective measurement).
  - `quantum_state_probabilities`, `quantum_create_bell_state`.
- [ ] Create `src/doomscript/domains/quantum/parser.py` and `exporter.py`.

#### Task 6: Electronics, Logic Gates & IoT (`use circuit`)
- [ ] Create `src/doomscript/domains/circuit/__init__.py` with `CircuitDomain` registration.
- [ ] Create `src/doomscript/domains/circuit/runtime.py` implementing:
  - `circuit_ohm_voltage`, `circuit_ohm_current`, `circuit_ohm_resistance`, `circuit_power`.
  - `circuit_decode_resistor_bands` (4-band and 5-band color decoder with tolerance).
  - `circuit_voltage_divider`, `circuit_555_timer_freq`, `circuit_rc_time_constant`.
  - `circuit_evaluate_truth_table` (boolean expression evaluation across all input permutations).
  - `circuit_pwm_duty_cycle`, `circuit_gpio_set`, `circuit_gpio_read`.
- [ ] Create `src/doomscript/domains/circuit/parser.py` and `exporter.py`.

#### Task 7: Blockchain, Merkle Trees & Cryptoeconomics (`use chain`)
- [ ] Create `src/doomscript/domains/chain/__init__.py` with `ChainDomain` registration.
- [ ] Create `src/doomscript/domains/chain/runtime.py` implementing:
  - `chain_merkle_tree_create`, `chain_merkle_root`, `chain_merkle_proof_verify`.
  - `chain_mine_block` (SHA-256 proof-of-work nonce search with target difficulty).
  - `chain_verify_block`.
  - `chain_utxo_ledger_create`, `chain_process_tx`, `chain_get_balance`.
  - `chain_checksum_address` (EIP-55 mixed-case Ethereum address generator).
- [ ] Create `src/doomscript/domains/chain/parser.py` and `exporter.py`.

#### Task 8: Integration & Test Suite for the 7 New Domains
- [ ] Re-export all new functions in `src/doomscript/runtime.py`.
- [ ] Create `tests/domains/test_new_domains_megapack.py` covering all 7 new domains.
- [ ] Run test suite and verify 100% pass rate.

---

### Phase 2: Deepening Core Algorithmic & Analytical Domains

#### Task 9: Deepen DSA (`dsa`)
- [ ] Add AVL Self-Balancing Tree (`dsa_avl_insert`, `dsa_avl_delete`, `dsa_avl_inorder`).
- [ ] Add Suffix Automaton (`dsa_suffix_automaton_build`, `dsa_count_distinct_substrings`).
- [ ] Add Aho-Corasick Multi-Pattern Automaton (`dsa_aho_corasick_build`, `dsa_aho_corasick_search`).
- [ ] Add Treap (Cartesian Tree) (`dsa_treap_insert`, `dsa_treap_split`, `dsa_treap_merge`).
- [ ] Add Dinic's Algorithm for Blocking Max Flow ($O(V^2 E)$).
- [ ] Update `dsa/parser.py`, `dsa/__init__.py`, and `runtime.py`.

#### Task 10: Deepen Data Engineering (`data`)
- [ ] Add Apache Arrow-style columnar arrays & typed chunking (`data_columnar_table`).
- [ ] Add Pivot Table & Unpivot / Melt (`data_pivot_table`, `data_unpivot_table`).
- [ ] Add JSON unnesting & array flattening (`data_unnest_json`).
- [ ] Add Fuzzy string join with Levenshtein similarity cutoff (`data_fuzzy_join`).
- [ ] Update `data/parser.py`, `data/__init__.py`, and `runtime.py`.

#### Task 11: Deepen Machine Learning (`ml`)
- [ ] Add Multi-Layer Perceptron (MLP) Classifier with backprop & sigmoid/ReLU activation (`ml_train_mlp`, `ml_predict_mlp`).
- [ ] Add CART Decision Tree Classifier & Regressor with Gini/MSE splitting (`ml_train_cart_tree`, `ml_predict_cart`).
- [ ] Add Gradient Boosted Decision Trees (GBDT) with residual boosting (`ml_train_gbdt`, `ml_predict_gbdt`).
- [ ] Add Isolation Forest for multidimensional anomaly detection (`ml_isolation_forest`).
- [ ] Update `ml/parser.py`, `ml/__init__.py`, and `runtime.py`.

#### Task 12: Deepen Quantitative Finance (`finance`)
- [ ] Add Black-Litterman optimal portfolio allocation (`finance_black_litterman`).
- [ ] Add Monte Carlo Value at Risk (VaR) with Cholesky correlated returns (`finance_monte_carlo_var`).
- [ ] Add Hull-White interest rate short rate tree (`finance_hull_white_tree`).
- [ ] Add Ichimoku Cloud indicators (`finance_ichimoku_cloud`).
- [ ] Update `finance/parser.py`, `finance/__init__.py`, and `runtime.py`.

#### Task 13: Verify Deepened Core Domains
- [ ] Create `tests/domains/test_deepened_core_domains.py` testing DSA, Data, ML, and Finance.
- [ ] Run test suite and verify 100% pass rate.

---

### Phase 3: Deepening Media, Analytics & Graph Domains

#### Task 14: Deepen NLP (`nlp`)
- [ ] Add Byte-Pair Encoding (BPE) subword tokenizer (`nlp_train_bpe`, `nlp_tokenize_bpe`).
- [ ] Add Word Embedding Semantic Cosine Matrix (`nlp_word_embedding_similarity`).
- [ ] Add Named Entity Recognition rule engine (`nlp_extract_named_entities`).
- [ ] Add N-gram Markov chain text generator (`nlp_markov_text_generate`).
- [ ] Update `nlp/parser.py`, `nlp/__init__.py`, and `runtime.py`.

#### Task 15: Deepen Graph Theory (`graph`)
- [ ] Add Tarjan's Dominator Tree algorithm (`graph_dominator_tree`).
- [ ] Add Maximum Weight Bipartite Matching (`graph_max_weight_bipartite`).
- [ ] Add Louvain Modularity Community Detection (`graph_louvain_communities`).
- [ ] Add Personalized PageRank with teleportation set (`graph_personalized_pagerank`).
- [ ] Update `graph/parser.py`, `graph/__init__.py`, and `runtime.py`.

#### Task 16: Deepen Computer Vision (`image`)
- [ ] Add Morphological Operations: Dilation, Erosion, Opening, Closing (`image_morphology`).
- [ ] Add Hough Transform Line Detection (`image_hough_lines`).
- [ ] Add 5x5 Gaussian Convolution Blur with kernel generation (`image_gaussian_blur_5x5`).
- [ ] Add Harris Corner Detector (`image_harris_corners`).
- [ ] Update `image/parser.py`, `image/__init__.py`, and `runtime.py`.

#### Task 17: Deepen Audio & DSP (`audio`)
- [ ] Add Fast Fourier Transform (FFT) magnitude spectrum (`audio_fft_spectrum`).
- [ ] Add Short-Time Fourier Transform (STFT) spectrogram frame generator (`audio_stft`).
- [ ] Add ADSR (Attack, Decay, Sustain, Release) envelope generator (`audio_adsr_envelope`).
- [ ] Add Acoustic Chorus, Flanger, and Reverb effects (`audio_reverb_effect`, `audio_chorus_effect`).
- [ ] Update `audio/parser.py`, `audio/__init__.py`, and `runtime.py`.

#### Task 18: Verify Deepened Media Domains
- [ ] Create `tests/domains/test_deepened_media_domains.py` testing NLP, Graph, Image, and Audio.
- [ ] Run test suite and verify 100% pass rate.

---

### Phase 4: Deepening Systems, Cloud, Scientific & Agentic Domains

#### Task 19: Deepen Cloud, Office & Research (`cloud`, `office`, `research`)
- [ ] `cloud`: S3 multipart upload simulation (`cloud_multipart_upload`), IAM policy evaluator (`cloud_eval_iam_policy`), CloudWatch metric alarms (`cloud_eval_alarm`).
- [ ] `office`: Spreadsheet formula evaluator for arithmetic and functions (`office_eval_formula`), Presentation slide generator (`office_create_presentation`, `office_add_slide`).
- [ ] `research`: Runge-Kutta 4th order (RK4) differential equation solver (`research_rk4_solve`), Numerical Quadrature with Gauss-Legendre (`research_gauss_legendre`), Symbolic polynomial algebra (`research_poly_derivative`, `research_poly_integral`).
- [ ] Update corresponding domain parsers, `__init__.py`, and runtimes.

#### Task 20: Deepen Sim, Geo, Opt & Agent (`sim`, `geo`, `opt`, `agent`)
- [ ] `sim`: Gillespie stochastic simulation algorithm for chemical kinetics (`sim_gillespie`), Non-homogeneous Poisson process (`sim_nonhomogeneous_poisson`).
- [ ] `geo`: 2D R-Tree spatial indexing (`geo_rtree_create`, `geo_rtree_search`), Isochrone distance bounds (`geo_isochrone_bounds`).
- [ ] `opt`: Branch-and-Bound Integer Linear Programming (`opt_branch_and_bound_ilp`), Quadratic Programming gradient solver (`opt_quadratic_program`).
- [ ] `agent`: Plan-and-Solve coordinator (`agent_plan_and_solve`), ReAct (Reasoning + Acting) thought-action loop (`agent_react_loop`).
- [ ] Update corresponding domain parsers, `__init__.py`, and runtimes.

#### Task 21: Deepen DB, Net & Web (`db`, `net`, `web`)
- [ ] `db`: In-memory B-Tree page engine simulator (`db_btree_page_create`, `db_btree_insert`), Write-Ahead Logging (WAL) and rollback (`db_wal_append`, `db_wal_rollback`).
- [ ] `net`: DNS query packet decoder (`net_dns_decode`), TCP 3-way handshake state machine (`net_tcp_handshake_step`).
- [ ] `web`: CSS selector parser and DOM query engine (`web_css_select`), Markdown-to-DOM compiler (`web_markdown_to_dom`).
- [ ] Update corresponding domain parsers, `__init__.py`, and runtimes.

#### Task 22: Verify Deepened Systems Domains
- [ ] Create `tests/domains/test_deepened_systems_domains.py` testing Cloud, Office, Research, Sim, Geo, Opt, Agent, DB, Net, and Web.
- [ ] Run test suite and verify 100% pass rate.

---

### Phase 5: Full Regression, Documentation & Final Review

#### Task 23: Complete Repository Regression Test Suite
- [ ] Run `py -m pytest -q` verifying 100% pass across all pre-existing 580 tests and all new test suites with 0 regressions.

#### Task 24: Synchronize Documentation & Git Commit
- [ ] Update `documentation.md` and `vspython.md` to document all 7 new domains and deepened operations.
- [ ] Commit all changes and push to GitHub.
