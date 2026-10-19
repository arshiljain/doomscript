# DoomScript Complete Language & Domain Reference Manual

**DoomScript** (`.doom`) is a general-purpose, English-first programming language designed to make code look, read, and flow like natural human instructions. It compiles deterministically to Python Abstract Syntax Trees (AST) and native standalone executables.

---

## 📑 Table of Contents

1. [Quickstart & CLI Commands](#1-quickstart--cli-commands)
2. [Syntax Philosophy & Core Conventions](#2-syntax-philosophy--core-conventions)
3. [Language Fundamentals](#3-language-fundamentals)
   - [Printing & Output](#printing--output)
   - [Variables & Assignments](#variables--assignments)
   - [Data Types & Collections](#data-types--collections)
   - [Pronoun Tracking (`it`, `that`)](#pronoun-tracking-it-that)
   - [Possessives (`'s`)](#possessives-s)
   - [Arithmetic & In-Place Mutations](#arithmetic--in-place-mutations)
   - [Conditionals & English Predicates](#conditionals--english-predicates)
   - [Loops & Iteration](#loops--iteration)
   - [Function Declarations & Calls](#function-declarations--calls)
   - [Error Handling & Contracts](#error-handling--contracts)
4. [Built-in Standard Utilities (Phases 14–25)](#4-built-in-standard-utilities)
   - [File I/O & Text Files](#file-io--text-files)
   - [JSON & Config Serialization](#json--config-serialization)
   - [Cryptography & Hashing](#cryptography--hashing)
   - [Streaming & Pipelines](#streaming--pipelines)
   - [Job Scheduling & Timers](#job-scheduling--timers)
5. [The 18 Domain Packs (`use <domain>`)](#5-the-18-domain-packs)
   - [1. DSA & Algorithms (`use dsa`)](#1-dsa--algorithms-use-dsa)
   - [2. Data Engineering (`use data`)](#2-data-engineering-use-data)
   - [3. Machine Learning (`use ml`)](#3-machine-learning-use-ml)
   - [4. Quantitative Finance (`use finance`)](#4-quantitative-finance-use-finance)
   - [5. NLP & Text Intelligence (`use nlp`)](#5-nlp--text-intelligence-use-nlp)
   - [6. Graph Theory (`use graph`)](#6-graph-theory-use-graph)
   - [7. Computer Vision & Media (`use image`)](#7-computer-vision--media-use-image)
   - [8. Web Scraping & DOM (`use web`)](#8-web-scraping--dom-use-web)
   - [9. Audio Synthesis & DSP (`use audio`)](#9-audio-synthesis--dsp-use-audio)
   - [10. Relational Database & SQL (`use db`)](#10-relational-database--sql-use-db)
   - [11. Networking & System (`use net`)](#11-networking--system-use-net)
   - [12. Simulation & Stochastics (`use sim`)](#12-simulation--stochastics-use-sim)
   - [13. Geospatial Analytics (`use geo`)](#13-geospatial-analytics-use-geo)
   - [14. Optimization & OR (`use opt`)](#14-optimization--or-use-opt)
   - [15. AI Agents & Multi-Agent Workflows (`use agent`)](#15-ai-agents--multi-agent-workflows-use-agent)
   - [16. Cloud Storage (`use cloud`)](#16-cloud-storage-use-cloud)
   - [17. Office & Documents (`use office`)](#17-office--documents-use-office)
   - [18. Research & Scientific Computing (`use research`)](#18-research--scientific-computing-use-research)
6. [Best Practices & Idioms](#6-best-practices--idioms)

---

## 1. Quickstart & CLI Commands

DoomScript provides a unified command-line tool `doom`:

```bash
# Run a DoomScript file directly
doom run app.doom

# Transpile DoomScript source into clean, standalone Python
doom export app.doom -o app.py

# Compile directly into a native standalone zero-dependency executable (.exe)
doom build app.doom -o dist/app.exe

# Run the built-in unit test runner across all tests/*.doom files
doom test

# Start the interactive REPL shell
doom repl

# Launch the Language Server (LSP) for VS Code / IDE integrations
doom lsp

# Check syntax and contract compliance without running
doom check app.doom --strict
```

---

## 2. Syntax Philosophy & Core Conventions

1. **Colons are Optional**: You can write blocks with or without a trailing colon:
   ```doomscript
   if player's health < 20:
       say "Warning: Low HP!"

   # Or completely colon-free:
   if player's health < 20
       say "Warning: Low HP!"
   ```
2. **Subject-Verb-Object (SVO) Phrasing**: Commands follow natural English verb phrases (`write X to Y`, `read X into Y`, `filter X where Y into Z`).
3. **Prepositional Parameters**: Keywords such as `with`, `from`, `to`, `into`, `using`, `by`, `for`, `at` specify arguments naturally.
4. **Zero Semicolons**: Semicolons are never needed.
5. **No Mandatory External Dependencies**: Standard library fallbacks ensure all algorithms execute in clean Python environments.

---

## 3. Language Fundamentals

### Printing & Output
Use `say`, `print`, `show`, or `display`. You can output multiple comma-separated expressions or use `{var}` string interpolation:

```doomscript
say "Hello world!"
show "Server started on port 8080"

name = "Sam"
score = 98
say "Player: ", name, " | Score: ", score

# String interpolation
message = "Congratulations {name}, your score is {score}!"
say message
```

---

### Variables & Assignments
The canonical assignment operator is `=`. Natural English phrasing is also supported:

```doomscript
# Canonical assignment
x = 10
total = 100

# Natural English aliases
set tax to 0.08
let attempts be 3
put 250 into balance

# Multiple assignments / destructuring
first, second = a list of 10, 20
```

---

### Data Types & Collections

DoomScript supports standard primitive and collection types:

```doomscript
# Numbers & Booleans
pi = 3.14159
is_active = true
flag = false

# Lists
items = a list of "Apple", "Banana", "Cherry"
numbers = [1, 2, 3, 4, 5]

# Records (Key-Value Dictionaries)
user = a new record
user["name"] = "Alice"
user["role"] = "Admin"

# Shorthand Record declaration
hero = {"name": "Slayer", "health": 100, "level": 5}
```

---

### Pronoun Tracking (`it`, `that`)
DoomScript tracks the most recently assigned variable, allowing natural pronoun reference:

```doomscript
price = 200
increase it by 15       # Updates price to 215
say that                # Prints 215

# Name the last computed expression
sqrt of 144
call it result
say result              # Prints 12.0
```

---

### Possessives (`'s`)
Access dictionary keys or object attributes using natural English possessive apostrophes:

```doomscript
player = {"name": "Leon", "hp": 85, "speed": 12}
say player's name
say player's hp

if player's hp < 50
    say "Critical condition"
```

---

### Arithmetic & In-Place Mutations
Modify numeric variables using clear verbs:

```doomscript
counter = 0

increase counter by 1      # counter = counter + 1
decrease counter by 5      # counter = counter - 5
multiply counter by 2      # counter = counter * 2
divide counter by 4        # counter = counter / 4

# Math expressions
val = square root of 64    # 8.0
rounded = round 3.14159 to 2 decimals into val_round
```

---

### Conditionals & English Predicates
Branching logic supports expressive English relational operators:

```doomscript
age = 25
status = "active"
tags = a list of "vip", "developer"

if age is between 18 and 65 and status is "active"
    say "Eligible user"
else if age < 18
    say "Minor"
else
    say "Senior"

# Type & Membership checks
if "vip" is in tags
    say "VIP Access"

if tags is not empty
    say "User has tags"

if user is a record
    say "Valid user payload"
```

---

### Loops & Iteration
Express loops with repetition counts, conditions, or collection traversals:

```doomscript
# Repeat N times
repeat 3 times
    say "Checking heartbeat..."

# While loop
attempts = 3
while attempts > 0
    say "Attempt remaining: ", attempts
    decrease attempts by 1

# For-each loop
fruits = a list of "apple", "pear", "peach"
for each fruit in fruits
    say "Fruit: ", fruit

# For-each with 1-based index count
for each fruit in fruits count from 1 into idx
    say idx, ": ", fruit
```

---

### Function Declarations & Calls
Declare functions with `to <name> with <args>`:

```doomscript
to calculate_total with price, tax_rate:
    return price + (price * tax_rate)

final_bill = calculate_total(100.0, 0.08)
say "Final Bill: $", final_bill

# Zero-argument function
to ping:
    say "pong"

ping()
```

---

### Error Handling & Contracts
Defensive programming with `try`, contracts, and expectations:

```doomscript
# Try-catch with English recovery
try:
    bad_math = 10 / 0
if it fails:
    say "Recovered gracefully from division error"

# Runtime verification contract
balance = 50
verify that balance >= 0 otherwise "Account cannot be negative"

# Unit testing expectation
expect balance to be 50
```

---

## 4. Built-in Standard Utilities

### File I/O & Text Files
Read and write files with direct statements:

```doomscript
write "Initial entry\n" to file "log.txt"
append "Second entry\n" to file "log.txt"
read file "log.txt" into file_content

check if file "log.txt" exists into exists_flag
say "Log exists: ", exists_flag
```

---

### JSON & Config Serialization
Parse and generate JSON or manage INI/JSON configurations:

```doomscript
raw_json = '{"user": "Alice", "active": true}'
parse json raw_json into user_record
say user_record's user

convert user_record to json into exported_str
say exported_str

# Configuration Manager
load config from "settings.ini" into app_cfg
get config "database.host" from app_cfg into db_host
set config "app.debug" to "false" in app_cfg
save config app_cfg to file "config_backup.json"
```

---

### Cryptography & Hashing
Native hashing, token generation, and AES-style symmetric encryption:

```doomscript
hash text "password123" with algorithm "sha256" into hashed_pass
generate secure token of length 32 into auth_token

encrypt text "Sensitive Data" with secret "my-master-key" into encrypted_cipher
decrypt text encrypted_cipher with secret "my-master-key" into plain_text
```

---

### Streaming & Pipelines
Pipe transformations or process items in batches:

```doomscript
to add_ten with x:
    return x + 10

to double_val with x:
    return x * 2

# Functional pipe operator
pipe 5 into add_ten, double_val into piped_result  # (5 + 10) * 2 = 30

raw_items = [1, 2, 3, 4, 5, 6, 7, 8, 9]
take first 3 items from raw_items into top_three
drop first 6 items from raw_items into last_three
batch raw_items by 3 into chunked_matrix
```

---

### Job Scheduling & Timers
Run recurrent jobs or background timers:

```doomscript
counter = 0
to tick:
    increase counter by 1

schedule every 0.5 seconds tick
run scheduler for 2.0 seconds
say "Total ticks: ", counter
```

---

## 5. The 18 Domain Packs

Activate any domain using `use <domain>` at the beginning of your script.

---

### 1. DSA & Algorithms (`use dsa`)
Advanced data structures and algorithmic primitives:

```doomscript
use dsa

# 1. Prefix Trie
create trie into t
insert word "apple" into trie t
insert word "application" into trie t
search trie t for "apple" into found_word
all words in trie t starting with "app" into prefix_matches

# 2. Disjoint Set Union (DSU / Union-Find)
create dsu of size 10 into dsu
union elements 1 and 2 in dsu
check if 1 and 2 are connected in dsu into are_connected
count connected components in dsu into component_count

# 3. LRU Cache
create lru cache with capacity 3 into cache
put key "a" with value 100 into cache cache
get key "a" from cache cache into cached_val

# 4. Search & Order Statistics
binary search 42 in sorted_nums into idx
k-th smallest element in nums with k 3 into third_min
k-th largest element in nums with k 1 into absolute_max

# 5. String & Graph Algorithms
rabin karp search for "pattern" in text into match_indices
manacher longest palindrome in "babad" into longest_pal
count inversions in nums into inversion_count
find bridges in graph_matrix into critical_bridges
```

---

### 2. Data Engineering (`use data`)
Tabular ETL pipelines, SQL-like transforms, and schema enforcement:

```doomscript
use data

read csv "sales.csv" into raw_table

# Data Cleaning & Imputation
forward fill missing values in column "price" of raw_table into ffilled_table
backward fill missing values in column "units" of ffilled_table into clean_table
coalesce columns [clean_table's preferred_phone, clean_table's backup_phone] into primary_contact

# Window Expressions & Rankings
rank rows in clean_table by column "revenue" descending into ranked_table
calculate lead of column "price" with offset 1 in clean_table into future_price
calculate lag of column "price" with offset 1 in clean_table into prev_price

# Aggregations & Joins
cumulative sum of column "revenue" in clean_table into running_revenue
cross join table_a with table_b into cartesian_table
validate schema of clean_table against schema_rules into validation_report
calculate summary of clean_table into statistical_overview
```

---

### 3. Machine Learning (`use ml`)
Classification, regression, clustering, dimensionality reduction, and metrics:

```doomscript
use ml

# 3-Way Train/Val/Test Split
split dataset samples into 70% train, 15% validation, 15% test into partitioned_data

# Classifiers
train knn classifier with features X_train and labels y_train and neighbors 5 into knn_model
train decision stump with features X_train and labels y_train into stump_model
train naive bayes with features X_train and labels y_train into bayes_model

# Clustering & PCA
cluster data X with kmeans using 3 clusters into clusters
apply pca to data X with 2 components into reduced_matrix

# Evaluation Metrics
predict classes for X_test with model knn_model into y_pred
calculate f1 score between y_test and y_pred into f1_res
calculate precision between y_test and y_pred into precision_res
calculate recall between y_test and y_pred into recall_res
calculate log loss between y_true and y_prob into loss_val
calculate brier score between y_true and y_prob into brier_val
```

---

### 4. Quantitative Finance (`use finance`)
Technical indicators, portfolio risk metrics, and option pricing:

```doomscript
use finance

# Technical Indicators
calculate vwap with high prices_high low prices_low close prices_close volume volumes into vwap_series
stochastic oscillator with high prices_high low prices_low close prices_close period 14 into stoch_vals
keltner channels for prices with period 20 and multiplier 2.0 into keltner
average true range for high prices_high low prices_low close prices_close period 14 into atr_vals
williams r for high prices_high low prices_low close prices_close period 14 into will_r
money flow index for high prices_high low prices_low close prices_close volume volumes period 14 into mfi_vals

# Risk & Performance Metrics
sortino ratio of returns with risk_free 0.02 into sortino_val
treynor ratio of returns with beta 1.1 and risk_free 0.02 into treynor_val
calmar ratio of returns with max_drawdown 0.15 into calmar_val
beta of asset_returns against market_returns into beta_val
jensen alpha of asset_returns against market_returns with risk_free 0.02 and beta 1.1 into alpha_val

# Black-Scholes Options Pricing
price call option with spot 100.0 strike 95.0 expiry 0.5 rate 0.05 vol 0.20 into call_price
price put option with spot 100.0 strike 95.0 expiry 0.5 rate 0.05 vol 0.20 into put_price
rebalance portfolio holdings to target_weights into trade_orders
```

---

### 5. NLP & Text Intelligence (`use nlp`)
Text processing, linguistic metrics, information retrieval, and phonetic matching:

```doomscript
use nlp

# Information Retrieval & Distances
rank corpus doc_collection for query "search terms" using bm25 into ranked_docs
levenshtein distance between "kitten" and "sitting" into edit_distance
hamming distance between "1011101" and "1001001" into bit_diff

# Phonetic & Linguistic Analysis
soundex "Robert" into soundex_code
metaphone "Knight" into metaphone_code
porter stem of "generously" into root_word
flesch reading ease of article into readability_score
gunning fog index of article into fog_score
count syllables in "incomprehensible" into syllable_count

# Text Quality & Evaluation
rouge-l score between generated_text and reference_text into rouge_res
bleu score between candidate_phrase and target_phrase into bleu_res
tf cosine similarity between doc_a and doc_b into similarity_val
expand contractions in "don't won't shouldn't" into expanded_text
mask sensitive entities in user_bio into sanitized_bio
vader sentiment of customer_review into sentiment_scores
```

---

### 6. Graph Theory (`use graph`)
Network modeling, pathfinding, and structural topological analysis:

```doomscript
use graph

# Shortest Paths & Traversals
find path in city_map from "A" to "B" using a star with heuristic euclidean into astar_path
find all pairs shortest paths in road_network using floyd warshall into distance_matrix

# Topological Properties
clustering coefficient of social_graph into clustering_score
find bridges in communication_graph into network_bottlenecks
find articulation points in road_network into critical_junctions
transitive closure of dag_graph into reachable_matrix
topological generations of dependency_graph into execution_phases
k core decomposition of graph with k 3 into dense_subgraph

# Link Prediction
predict links in user_network using adamic adar into friend_recommendations
predict links in citation_network using jaccard into related_papers
```

---

### 7. Computer Vision & Media (`use image`)
Image generation, filtering, color manipulation, and spatial transforms:

```doomscript
use image

create canvas with width 640 and height 480 and color "white" into img
load image "photo.jpg" into photo

# Filtering & Edge Detection
apply sobel filter to photo into edges
threshold photo with cutoff 128 into binarized_img
sharpen image photo with factor 1.5 into sharp_photo
invert colors of photo into negative_photo
adjust contrast of photo with factor 1.2 into contrasted_photo
apply sepia filter to photo into vintage_photo

# Spatial & Channel Operations
split channels of photo into rgb_channels
merge channels rgb_channels into restored_photo
flip photo horizontally into mirrored_photo
apply vignette to photo with intensity 0.7 into artistic_photo
pixelate photo with block_size 8 into mosaic_photo
calculate mean color of photo into average_rgb
```

---

### 8. Web Scraping & DOM (`use web`)
Declarative web scraping, form parsing, and protocol auditing:

```doomscript
use web

# DOM Scraping
parse form inputs from html_code into form_data
generate url encoded string from parameters into query_string
extract urls from sitemap sitemap_xml into catalog_urls
check if robots txt robots_content allows url "/admin" for agent "Googlebot" into is_allowed
canonicalize url "https://example.com/item/../index.html" into clean_url

# Element & Security Auditing
extract headings from page_html into heading_structure
check ssl expiry for domain "google.com" into days_remaining
serialize cookies cookie_jar into cookie_header
parse json-ld metadata from page_html into rich_snippets
extract elements from page_html with class "price-tag" into price_nodes
generate curl command for url "https://api.test.com" with method "POST" and headers req_headers into curl_cmd
```

---

### 9. Audio Synthesis & DSP (`use audio`)
Sound generation, envelope control, mixing, and digital signal processing:

```doomscript
use audio

# Waveform Generators
generate square wave with frequency 440.0 and duration 1.0 into sq_tone
generate sawtooth wave with frequency 220.0 and duration 1.0 into saw_tone
generate triangle wave with frequency 880.0 and duration 1.0 into tri_tone
generate white noise with duration 2.0 into ambient_noise

# Signal Processing & Mixing
adjust gain of sq_tone by 3.0 db into boosted_tone
trim silence from recorded_audio with threshold -40 into trimmed_audio
apply fade out to sq_tone with duration 0.2 into smooth_tone
mix audio tracks [sq_tone, ambient_noise] with balance [0.8, 0.2] into mixed_track
apply stereo pan to sq_tone with pan -0.5 into left_leaning_audio
apply lowpass filter to sq_tone with cutoff 1000 into warm_audio
apply highpass filter to ambient_noise with cutoff 500 into bright_noise
calculate rms energy of sq_tone into energy_level
stretch audio sq_tone by factor 1.5 into slow_audio
```

---

### 10. Relational Database & SQL (`use db`)
SQLite querying, index management, and administrative automation:

```doomscript
use db

connect to database "app.db" into db

# DDL & Schema Administration
create index "idx_user_email" on table "users" with column "email" in db
drop index "idx_old_perf" from db
add column "last_login" with type "TEXT" to table "users" in db
vacuum database db
analyze database statistics for db

# Metadata & Introspection
list tables in db into table_names
list views in db into view_names
list indexes on table "users" in db into user_indexes

# Bulk Operations & Migrations
bulk insert records new_users into table "users" in db with batch 500
export table "users" from db to csv "users_backup.csv"
import csv "new_leads.csv" into table "leads" in db
export ddl schema from db into schema_sql
clone database schema from db into in_memory_replica
```

---

### 11. Networking & System (`use net`)
CIDR calculations, address formatting, diagnostics, and reachability:

```doomscript
use net

# IP & CIDR Networking
calculate netmask for cidr "192.168.1.0/24" into subnet_mask
check if ip "192.168.1.55" is in subnet "192.168.1.0/24" into in_local_net
expand cidr range "10.0.0.0/29" into available_ips
validate ipv4 address "172.16.0.1" into is_valid_v4
validate ipv6 address "2001:db8::1" into is_valid_v6
format mac address "001A2B3C4D5E" to standard into formatted_mac

# System & Connectivity
query whois for domain "doomscript.org" into domain_whois
http status message for code 404 into error_phrase
exponential backoff delays with base 1.5 and attempts 5 into retry_schedule
scan open ports on host "127.0.0.1" for ports [80, 443, 8080] into open_ports
```

---

### 12. Simulation & Stochastics (`use sim`)
Stochastic processes, statistical sampling, and queueing theory:

```doomscript
use sim

# Markov Chains & Processes
simulate markov chain with transitions transition_matrix and steps 50 from state 0 into state_history
simulate wiener process with drift 0.05 and volatility 0.2 and steps 100 into stock_path

# Random Variate Distributions
generate geometric variates with probability 0.3 and size 1000 into geo_samples
generate binomial variates with trials 10 and probability 0.5 and size 500 into binom_samples
generate triangular variates with low 0.0 high 10.0 mode 3.0 and size 100 into tri_samples
generate lognormal variates with mean 0.0 and sigma 1.0 and size 200 into lognorm_samples
generate weibull variates with shape 1.5 and scale 2.0 and size 300 into weibull_samples

# Statistical Hypothesis Testing
calculate bootstrap confidence interval for observations with percentiles [2.5, 97.5] and resamples 1000 into conf_int
run permutation test between sample_a and sample_b with permutations 500 into p_value
calculate mm1 queue metrics with arrival_rate 2.0 and service_rate 3.0 into queue_stats
```

---

### 13. Geospatial Analytics (`use geo`)
Geographic coordinates, distance mathematics, bounding boxes, and polygons:

```doomscript
use geo

# Geohash & Distance
encode geohash for latitude 37.7749 and longitude -122.4194 with precision 8 into sfo_hash
decode geohash sfo_hash into sfo_coords
cross track distance from point p to path start_pt, end_pt into off_track_meters
destination point from start_pt with bearing 90.0 and distance 50.0 km into east_pt
calculate initial bearing from city_a to city_b into heading_degrees
calculate final bearing from city_a to city_b into terminal_heading
calculate midpoint between city_a and city_b into halfway_coords

# Polygon & Spatial Hull
check bounding box bbox1 overlaps bbox2 into has_overlap
calculate convex hull of perimeter_points into boundary_polygon
simplify path polyline_coords using douglas peucker with tolerance 0.01 into compressed_path
```

---

### 14. Optimization & OR (`use opt`)
Constrained continuous and discrete mathematical optimization:

```doomscript
use opt

# Continuous Function Optimizers
minimize function "x^2 + 4*x + 4" using simulated annealing with bounds [-10, 10] into optimal_x
minimize function "x^2 - 6*x + 9" using golden section with bounds [0, 5] into min_val

# Dynamic Programming & Combinatorics
solve 0/1 knapsack with weights [2, 3, 4, 5] and values [3, 4, 5, 6] and capacity 8 into knapsack_max
longest increasing subsequence in [10, 9, 2, 5, 3, 7, 101, 18] into lis_seq
minimum coins for amount 11 with denominations [1, 2, 5] into min_coins
count coin change ways for amount 10 with denominations [1, 2, 5] into total_ways
build huffman tree from frequencies char_freqs into huffman_codes
optimal matrix chain multiplication for dimensions [10, 30, 5, 60] into min_operations
subset sum possible for numbers [3, 34, 4, 12, 5, 2] with target 9 into has_subset
solve traveling salesperson for distance_matrix using 2-opt into tsp_tour
solve bipartite matching for cost_matrix using hungarian into optimal_assignment
```

---

### 15. AI Agents & Multi-Agent Workflows (`use agent`)
Autonomous agents, shared memory, task routing, consensus voting, and debates:

```doomscript
use agent

# Agent Creation & Team Assembly
create agent researcher with role "data investigator" into agent_a
create agent critic with role "fact checker" into agent_b
create team review_board with agents [agent_a, agent_b] into editorial_board

# Memory, Routing & Quality
score response quality of text "Well structured answer" into quality_score
format chat history from raw_messages into structured_chat
summarize memory of agent agent_a with limit 5 into memory_summary
route query "fix authentication bug" with keywords {"security": agent_a, "db": agent_b} into chosen_agent
calculate retry delay with jitter for attempt 3 and base 1.0 into delay_seconds
validate json payload with schema user_schema into schema_is_valid

# Multi-Agent Coordination
broadcast message "Prepare Q3 report" to team editorial_board into broadcast_receipt
tally consensus votes from ["approve", "approve", "reject"] with threshold 0.6 into vote_outcome
adjudicate debate between agent_a and agent_b on topic "Microservices vs Monolith" into winner_verdict
```

---

### 16. Cloud Storage (`use cloud`)
Storage bucket lifecycle, checksum integrity, presigned transfers, and auditing:

```doomscript
use cloud

connect to bucket "production-store" into b1
connect to bucket "backup-store" into b2

# Read/Write & Presigned URLs
write text "System log line" to object "logs/app.log" in b1
read text from object "logs/app.log" in b1 into log_data
generate presigned put url for "uploads/data.bin" in b1 with expiry 1800 into upload_url

# Integrity & Tagging
verify sha256 checksum of "logs/app.log" in b1 against expected_hash into sha_ok
verify md5 checksum of "logs/app.log" in b1 against expected_md5 into md5_ok
tags = a new record
tags["env"] = "production"
set object tags for "logs/app.log" in b1 to tags
get object tags for "logs/app.log" in b1 into current_tags
set storage class for "logs/app.log" in b1 to "COLDLINE"

# Audit, Mirroring & Cleanup
filter files in b1 by size between 1024 and 1048576 into medium_files
filter files in b1 modified after "2026-01-01T00:00:00" into fresh_files
count objects by extension in b1 into extension_breakdown
move object "temp/a.txt" to "archive/a.txt" in b1
mirror bucket b1 to b2 into mirror_report
diff bucket b1 with bucket b2 into audit_diff
export bucket manifest for b1 to "manifest.json" into exported_manifest
archive stale files in b1 older than 365 days into archived_count
batch delete keys ["temp/1.tmp", "temp/2.tmp"] from b1 into deleted_count
```

---

### 17. Office & Documents (`use office`)
Document generation, Excel/CSV manipulation, formatting, and structural inspection:

```doomscript
use office

# CSV Delimiter & Header Inspection
detect csv delimiter "records.csv" into detected_delim
read csv header "records.csv" into header_list

# Spreadsheet Operations
load spreadsheet "financials.xlsx" into sheet
calculate sheet summary for sheet in "Q1" at column "Revenue" into revenue_stats
set cell at row 2 and column 3 in sheet "Q1" of sheet to 150000
get cell at row 2 and column 3 from sheet "Q1" of sheet into updated_val
list worksheets in sheet into sheet_names
sort sheet "Q1" in sheet by column 1 descending into sorted_rows
filter sheet "Q1" in sheet where column 2 matches "Enterprise" into filtered_rows
export sheet "Q1" in sheet to json "q1_export.json"
import json "q1_export.json" into sheet "Imported" of sheet into imported_count

# Word & Rich Document Generation
create word document into doc
add heading "Quarterly Operations" at level 1 to doc
add paragraph "Performance exceeded forecast by 14%." to doc
add bulleted list ["KPI met", "Security passed"] to doc
add numbered list ["Milestone 1", "Milestone 2"] to doc
add table with headers ["Dept", "Budget"] and rows [["Eng", 50000], ["Sales", 30000]] to doc

# Document Text Tools
find and replace "Audit" with "Security Audit" in doc into replace_count
count words in doc into total_words
count characters in doc into total_characters
extract document metadata from doc into doc_metadata
```

---

### 18. Research & Scientific Computing (`use research`)
Reverse-mode automatic differentiation combined with exact graph algorithms:

```doomscript
use research

# 1. Reverse-Mode Autograd & Optimization
w1 = scalar 2.0 with gradient
x = scalar 3.0
b = scalar 1.5 with gradient

y = (w1 * x) + b
backward y

say "w1 gradient:", w1's gradient  # dy/dw1 = x = 3.0
say "b gradient:", b's gradient    # dy/db = 1.0

# 2. Graph Construction & Shortest Paths
create a research graph into g
add edge from "A" to "B" with weight 4.0 to g
add edge from "A" to "C" with weight 2.0 to g
add edge from "C" to "B" with weight 1.0 to g
add edge from "B" to "D" with weight 5.0 to g

find shortest path from "A" to "D" in g using dijkstra into dijk_res
find shortest paths from "A" in g using bellman ford into bf_res
find all pairs shortest paths in g using floyd warshall into fw_matrix

# 3. Network Flow & Matching
maximum flow from "A" to "D" in g using edmonds karp into max_flow
find bipartite matching in bg between set_u and set_v into matching_res

# 4. Spanning Trees, Components & Centrality
find strongly connected components in g into sccs
find minimum spanning tree in g using kruskal into mst_kruskal
find minimum spanning tree in g using prim into mst_prim
calculate diameter of g into graph_diameter
calculate radius of g into graph_radius
calculate pagerank of g with damping 0.85 into rank_scores
calculate hits scores of g into hubs_authorities
find eulerian circuit in g into euler_path
calculate degree distribution of g into degree_stats
```

---

## 6. Best Practices & Idioms

1. **Prefer Expressive Verbs Over Inverted Expressions**:
   ```doomscript
   # Idiomatic DoomScript
   filter users where age >= 21 into active_adults
   sort active_adults by score descending into leaderboard

   # Avoid unnecessary Pythonic loop comprehensions
   ```
2. **Take Advantage of Possessive Notation**:
   ```doomscript
   # Clean
   say order's customer's email

   # Avoid bracket clutter
   # say order["customer"]["email"]
   ```
3. **Use Pronouns for Short Sequential Transformations**:
   ```doomscript
   price = 100
   increase it by 20
   multiply it by 1.08
   call it final_price
   ```
4. **Use Explicit Domain Imports**:
   Always place `use <domain>` at the beginning of your file so the domain parser activates and compiles with maximum efficiency.
5. **Zero-Punctuation Formatting**:
   DoomScript's parser is designed around natural line breaks and indentations. Keep statements clean and avoid unnecessary commas or trailing semicolons.
