# DoomScript Centurion Domain Expansion Plan (15 New Domains & 25 Deepened Domains)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand DoomScript from 25 to 40 production domains and further deepen existing domains with ~100k lines of rigorous code and tests, 100% test pass rate, and updated comprehensive documentation.

**Architecture:** Each domain pack contains:
1. `runtime.py`: Pure Python zero-dependency algorithms and models.
2. `parser.py`: Spoken English grammar rules subclassing `DomainParser`.
3. `exporter.py`: Python AST transpiler subclassing `DomainExporter`.
4. `__init__.py`: Registration functions tying the domain into `DOMAIN_REGISTRY`.
5. Unit and integration tests in `tests/domains/`.

**Tech Stack:** Pure Python 3.10+ standard library (math, cmath, struct, collections, heapq, re, json, itertools, typing).

**Spec:** `docs/superpowers/specs/2026-10-20-domain-centurion-expansion-design.md`

---

## Global Constraints
- Pure Python standard library only; no pip dependencies required at runtime.
- Colons optional, spoken English grammar patterns.
- 100% test pass rate across all 655+ existing tests with 0 regressions.
- Full output enforcement: no placeholder comments, no truncated skeletons.

---

## Tasks Breakdown

### Phase 1: Core Mathematical, Graphics & System Domains (Domains 26–30)
- [ ] **Task 1: `math3d` Domain**: Vector, Matrix4, Quaternion, Ray Tracing, SDFs
- [ ] **Task 2: `compiler` Domain**: Bytecode VM, Assembler, Pratt Expression Parser
- [ ] **Task 3: `robotics` Domain**: DH-Kinematics, Numerical IK, Trajectory Planning, EKF
- [ ] **Task 4: `signals` Domain**: Wavelet DWT, FIR/IIR Filters, Hilbert Transform, Peak Detection
- [ ] **Task 5: `astronomy` Domain**: Keplerian Orbits, Julian Dates, Coordinate Conversions, Hohmann Transfer
- [ ] **Task 6: Verification & Tests for Phase 1**: Comprehensive tests in `tests/domains/test_domains_26_to_30.py`

### Phase 2: Scientific, Computational & Data Domains (Domains 31–35)
- [ ] **Task 7: `chem` Domain**: SMILES Parsing, Molecular Mass, Aromaticity, Reaction Balancer
- [ ] **Task 8: `compression` Domain**: RLE, Huffman, LZ77, LZW, Arithmetic Coding
- [ ] **Task 9: `time_series` Domain**: STL Decomposition, ACF/PACF, Holt-Winters, ARMA
- [ ] **Task 10: `symbolic` Domain**: CAS Expression AST, Differentiation, Polynomial Long Division, GCD
- [ ] **Task 11: `graphics` Domain**: Software Rasterizer, Bresenham, Barycentric Z-Buffer, Gouraud Shading
- [ ] **Task 12: Verification & Tests for Phase 2**: Comprehensive tests in `tests/domains/test_domains_31_to_35.py`

### Phase 3: Telecommunications, Automata, Neural & Metrics (Domains 36–40)
- [ ] **Task 13: `telecom` Domain**: Hamming(7,4), CRC-8/16/32/64, GF(2^8), Reed-Solomon RS(255,223)
- [ ] **Task 14: `neuro` Domain**: LIF Spiking Neurons, STDP Plasticity, Spike Rasters
- [ ] **Task 15: `automata` Domain**: DFA/NFA Simulation, Hopcroft Minimization, PDA, Turing Machine
- [ ] **Task 16: `metrics` Domain**: Prometheus Text Exposition, HDR Reservoirs, Quantiles, Tracing
- [ ] **Task 17: `spatial_audio` Domain**: 3D Binaural HRTF, First-Order Ambisonics, Doppler, Schroeder Reverb
- [ ] **Task 18: Verification & Tests for Phase 3**: Comprehensive tests in `tests/domains/test_domains_36_to_40.py`

### Phase 4: Deepening the Existing 25 Domains
- [ ] **Task 19: Deepen Core Algorithms**: Red-Black Tree, B-Tree, Skip List in `dsa`; Random Forest & Logistic Regression in `ml`; Monte Carlo & VaR in `finance`
- [ ] **Task 20: Deepen Systems & Networking**: Johnson's AP-SP in `graph`; Affine & Morphological in `image`; DNS Wire Format & TLS 1.3 ClientHello in `net`; Discrete Event Sim in `sim`; QuadTree in `geo`
- [ ] **Task 21: Verification & Tests for Deepened Suites**: Tests in `tests/domains/test_deepened_centurion.py`

### Phase 5: Documentation & Git Commit
- [ ] **Task 22: Update `documentation.md`**: Add sections for domains 26–40 and deepened capabilities
- [ ] **Task 23: Update `vspython.md`**: Add side-by-side examples for new domains
- [ ] **Task 24: Full Test Suite Run**: Verify 100% pass across all tests
- [ ] **Task 25: Git Commit & Push**: Commit all changes and push to GitHub
