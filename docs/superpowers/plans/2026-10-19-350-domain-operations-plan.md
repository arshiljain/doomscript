# 350 Spoken-English Operations Master Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and verify 352 spoken-English operations across all 18 DoomScript domains in a continuous full run with comprehensive test coverage and zero regressions.

**Architecture:**
1. Runtime: Implement pure algorithmic and standard library logic in `src/doomscript/domains/<domain>/runtime.py`.
2. Parser: Add natural spoken-English regex matching in `src/doomscript/domains/<domain>/parser.py`.
3. Interception & Spec: Register verbs and patterns in `can_handle_line` and `__all__` in `src/doomscript/domains/<domain>/__init__.py`.
4. Re-export: Expose functions in `src/doomscript/runtime.py` so they are immediately accessible in user scripts.
5. Verification: Write dedicated test suites covering all operations and run full repository regression.

---

## Tasks Breakdown

### Group A: DSA, Data, ML & Finance (79 Operations)
- [x] Task 1: Implement 19 DSA operations in `domains/dsa/` (Trie, DSU, LRU, QuickSelect, Kadane 2D, Rabin-Karp, Manacher, Inversions, Permutations, Bridges).
- [x] Task 2: Implement 20 Data operations in `domains/data/` (Rank, Lead/Lag, Cumulative Sum/Max/Min, Coalesce, Multi-Sort, Cross Join, Schema Validation, String Formatting, Forward/Backward Fill).
- [x] Task 3: Implement 20 ML operations in `domains/ml/` (KNN, Decision Stump, Naive Bayes, KMeans, PCA, Log Loss, Brier Score, F1/Precision/Recall, Polynomial Features, Cosine Decay, 3-Way Split).
- [x] Task 4: Implement 20 Finance operations in `domains/finance/` (VWAP, Stochastic Oscillator, Sortino, Treynor, Calmar, Beta, Alpha, Black-Scholes Call/Put, Keltner, ATR, Williams %R, MFI, Rebalance).
- [x] Task 5: Re-export Group A in `src/doomscript/runtime.py` and verify via `tests/domains/test_350_ops_batch1_to_4.py`.

### Group B: NLP, Graph, Image & Web (80 Operations)
- [x] Task 6: Implement 20 NLP operations in `domains/nlp/` (Levenshtein, Flesch-Kincaid, BLEU, ROUGE-L, Entity Extractors, Porter Stemming, Syllable Count, Jaro-Winkler, Slugify, Masking).
- [x] Task 7: Implement 20 Graph operations in `domains/graph/` (A*, Floyd-Warshall, Clustering Coefficients, Bridges, Articulation Points, Transitive Closure, Topological Generations, K-Core, Link Prediction).
- [x] Task 8: Implement 20 Image operations in `domains/image/` (Sobel Edge, Threshold Binarize, Sharpen, Invert, Contrast, Channel Split/Merge, Sepia, Flips, Vignette, Mean Color, Mosaic).
- [x] Task 9: Implement 20 Web operations in `domains/web/` (Forms, URL Encoded, Sitemap XML, Robots.txt, Canonicalize, Headings, SSL Expiry, Cookies, JSON-LD, Text by Class/ID, cURL generator).
- [x] Task 10: Re-export Group B in `src/doomscript/runtime.py` and verify via `tests/domains/test_350_ops_batch5_to_8.py`.

### Group C: Audio, DB, Net & Sim (79 Operations)
- [x] Task 11: Implement 19 Audio operations in `domains/audio/` (Square/Sawtooth/Triangle/Noise, Gain dB, Silence Trimming, Fade Out, Polyphonic Mixer, Panning, IIR Filters, RMS Energy, Time Stretch).
- [x] Task 12: Implement 20 DB operations in `domains/db/` (Create/Drop Index, Add Column, Vacuum, Analyze, List Tables/Views/Indices, Bulk Insert, CSV Import/Export, DDL Export, Schema Clone).
- [x] Task 13: Implement 20 Net operations in `domains/net/` (CIDR Netmask, Subnet Check, CIDR Expansion, IP Validators, MAC Formatter, WHOIS, Status Message, Exponential Backoff, Multi-Port Scan).
- [x] Task 14: Implement 20 Sim operations in `domains/sim/` (Markov Chain, Geometric/Binomial/Triangular/Lognormal/Weibull Variates, Bootstrap CI, Permutation Test, M/M/1 Queue, Wiener Process).
- [x] Task 15: Re-export Group C in `src/doomscript/runtime.py` and verify via `tests/domains/test_350_ops_batch9_to_12.py`.

### Group D: Geo, Opt, Agent, Cloud, Office & Research (114 Operations)
- [x] Task 16: Implement 19 Geo operations in `domains/geo/` (Geohash Encode/Decode, Cross-Track Distance, Destination Point, Bearings, Midpoint, Bounding Box Overlap, Convex Hull, Douglas-Peucker).
- [x] Task 17: Implement 19 Opt operations in `domains/opt/` (Simulated Annealing, Golden Section, 0/1 Knapsack DP, LIS, Coin Change Min/Ways, Huffman, Matrix Chain, Subset Sum, 2-opt TSP, Hungarian).
- [x] Task 18: Implement 19 Agent operations in `domains/agent/` (Response Quality, History Formatter, Memory Summarize, Keyword Routing, Retry Backoff, JSON Schema Validate, Debate Round, Tool Registry).
- [x] Task 19: Implement 19 Cloud operations in `domains/cloud/` (Presigned PUT, MD5/SHA256 Verify, Object Tags, Batch Delete, Size/Date Filters, Mirror Buckets, Archive Stale, Bucket Manifest, Storage Classes).
- [x] Task 20: Implement 19 Office operations in `domains/office/` (Sheet Summary, CSV Delimiter Detect, Document Tables, Lists, Cell Get/Set, Worksheet Management, Word/Char Counts, Document Metadata).
- [x] Task 21: Implement 19 Research operations in `domains/research/` (Topological Sort, Dijkstra, Bellman-Ford, Max Flow, Hopcroft-Karp Matching, Prim/Kruskal MST, PageRank, HITS, Eulerian Circuit).
- [x] Task 22: Re-export Groups D & E in `src/doomscript/runtime.py` and verify via `tests/domains/test_350_ops_batch13_to_15.py` and `tests/domains/test_350_ops_batch16_to_18.py`.

### Group E: Full Repository Regression & Wrap-up
- [x] Task 23: Run full repository regression `py -m pytest -q` verifying 100% test pass with 0 regressions across all 555+ existing tests and all new test suites.
