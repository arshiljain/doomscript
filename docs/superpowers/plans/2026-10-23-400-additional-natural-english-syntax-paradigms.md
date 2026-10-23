# 400 Additional Natural English Syntax Paradigms Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

## Goal
Implement and verify 400 additional natural English syntax paradigms (Items 101 to 500) across 20 linguistic clusters in DoomScript, ensuring zero regressions on the existing test suite and a 100% green CI matrix.

## Structure & Architecture
- **Runtime Library:** `src/doomscript/runtime.py` implements all underlying utility and algorithmic functions.
- **Compiler Exports:** `src/doomscript/compiler/exports.py` and `src/doomscript/compiler/engine.py` expose the runtime helpers to DoomScript scripts.
- **Phrase Normalizer:** `src/doomscript/grammar/phrases.py` lowers natural English sentences into standard AST-compatible constructs.
- **Regression Test Suites:**
  - `tests/test_natural_syntax_paradigms_101_to_200.py`
  - `tests/test_natural_syntax_paradigms_201_to_300.py`
  - `tests/test_natural_syntax_paradigms_301_to_400.py`
  - `tests/test_natural_syntax_paradigms_401_to_500.py`

---

## Tasks

### Task 1: Batch 1 (Items 101–200, Clusters 11–15)
File System, Network/HTTP, Tabular CSV, System/OS, and Unit Conversions.
- [ ] Write test suite `tests/test_natural_syntax_paradigms_101_to_200.py`.
- [ ] Implement runtime functions in `src/doomscript/runtime.py` (`ds_file_*`, `ds_folder_*`, `ds_http_*`, `ds_csv_*`, `ds_table_*`, `ds_sys_*`, `ds_convert_*`).
- [ ] Export runtime functions in `src/doomscript/compiler/exports.py` and `src/doomscript/compiler/engine.py`.
- [ ] Add phrase lowerings in `src/doomscript/grammar/phrases.py`.
- [ ] Verify `tests/test_natural_syntax_paradigms_101_to_200.py` passes locally.

### Task 2: Batch 2 (Items 201–300, Clusters 16–20)
Vector Math, Regex & Search, Sets & Combinatorics, Serialization (JSON/YAML/B64), Cryptography & Hashing.
- [ ] Write test suite `tests/test_natural_syntax_paradigms_201_to_300.py`.
- [ ] Implement runtime functions in `src/doomscript/runtime.py` (`ds_vector_*`, `ds_regex_*`, `ds_extract_*`, `ds_set_*`, `ds_json_*`, `ds_yaml_*`, `ds_base64_*`, `ds_crypto_*`).
- [ ] Export runtime functions in `src/doomscript/compiler/exports.py` and `src/doomscript/compiler/engine.py`.
- [ ] Add phrase lowerings in `src/doomscript/grammar/phrases.py`.
- [ ] Verify `tests/test_natural_syntax_paradigms_201_to_300.py` passes locally.

### Task 3: Batch 3 (Items 301–400, Clusters 21–25)
Stream & Batching, Advanced Date/Time, Formatting & Presentation, Concurrency & Async, Error Fallback & Resilience.
- [ ] Write test suite `tests/test_natural_syntax_paradigms_301_to_400.py`.
- [ ] Implement runtime functions in `src/doomscript/runtime.py` (`ds_chunk_*`, `ds_sliding_window`, `ds_calendar_*`, `ds_format_*`, `ds_async_*`, `ds_retry_*`).
- [ ] Export runtime functions in `src/doomscript/compiler/exports.py` and `src/doomscript/compiler/engine.py`.
- [ ] Add phrase lowerings in `src/doomscript/grammar/phrases.py`.
- [ ] Verify `tests/test_natural_syntax_paradigms_301_to_400.py` passes locally.

### Task 4: Batch 4 (Items 401–500, Clusters 26–30)
Linguistic & Distance Algorithms, Graphs & Trees, Interactive CLI, Caching & Memoization, Validation & Type Casting.
- [ ] Write test suite `tests/test_natural_syntax_paradigms_401_to_500.py`.
- [ ] Implement runtime functions in `src/doomscript/runtime.py` (`ds_soundex`, `ds_levenshtein_*`, `ds_graph_*`, `ds_cli_*`, `ds_cache_*`, `ds_validate_*`, `ds_cast_*`).
- [ ] Export runtime functions in `src/doomscript/compiler/exports.py` and `src/doomscript/compiler/engine.py`.
- [ ] Add phrase lowerings in `src/doomscript/grammar/phrases.py`.
- [ ] Verify `tests/test_natural_syntax_paradigms_401_to_500.py` passes locally.

### Task 5: Full Regression Suite & CI Verification
- [ ] Run all test files:
  - `tests/test_100_natural_syntax_paradigms.py`
  - `tests/test_natural_syntax_paradigms_101_to_200.py`
  - `tests/test_natural_syntax_paradigms_201_to_300.py`
  - `tests/test_natural_syntax_paradigms_301_to_400.py`
  - `tests/test_natural_syntax_paradigms_401_to_500.py`
  - `tests/test_vspython_all_examples.py`
  - `tests/test_phase6_errors.py`
- [ ] Git commit and push to `origin/main`.
- [ ] Monitor GitHub Actions CI run across all 24 OS/Python matrix jobs to achieve 100% green.
