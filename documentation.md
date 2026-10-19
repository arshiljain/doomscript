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
5. [The 25 Domain Packs (`use <domain>`)](#5-the-25-domain-packs)
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
   - [19. Bioinformatics & Genomics (`use bio`)](#19-bioinformatics--genomics-use-bio)
   - [20. Classical & Modern Physics (`use physics`)](#20-classical--modern-physics-use-physics)
   - [21. Cybersecurity & Cryptographic Primitives (`use sec`)](#21-cybersecurity--cryptographic-primitives-use-sec)
   - [22. Game Systems & Physics Simulation (`use game`)](#22-game-systems--physics-simulation-use-game)
   - [23. Quantum Computing & State Simulation (`use quantum`)](#23-quantum-computing--state-simulation-use-quantum)
   - [24. Electrical Engineering & Circuit Analysis (`use circuit`)](#24-electrical-engineering--circuit-analysis-use-circuit)
   - [25. Blockchain, Cryptographic Ledgers & Merkle Trees (`use chain`)](#25-blockchain-cryptographic-ledgers--merkle-trees-use-chain)
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

## 5. The 25 Domain Packs

Activate any domain using `use <domain>` at the beginning of your script.

---

### 1. DSA & Algorithms (`use dsa`)
Advanced self-balancing trees, string automata, caches, and algorithmic primitives:

```doomscript
use dsa

# 1. Prefix Trie & Suffix Automaton
create trie into t
insert word "apple" into trie t
insert word "application" into trie t
search trie t for "apple" into found_word
all words in trie t starting with "app" into prefix_matches

sam = dsa_suffix_automaton("banana")
can_match = dsa_sam_contains(sam, "nan")
sub_count = dsa_sam_distinct_substrings(sam)

# 2. AVL Self-Balancing Binary Search Tree
avl = dsa_avl_create()
dsa_avl_insert(avl, 50)
dsa_avl_insert(avl, 20)
dsa_avl_insert(avl, 70)
has_twenty = dsa_avl_search(avl, 20)
sorted_elements = dsa_avl_inorder(avl)

# 3. Aho-Corasick Multi-Pattern String Matcher
ac = dsa_ahocorasick_create(["he", "she", "his", "hers"])
ac_matches = dsa_ahocorasick_search(ac, "ushers")

# 4. Disjoint Set Union (DSU) & Fenwick / Segment Trees
create dsu of size 10 into dsu
union elements 1 and 2 in dsu
check if 1 and 2 are connected in dsu into are_connected
count connected components in dsu into component_count

fenwick = dsa_fenwick_create([1, 3, 5, 7, 9, 11])
range_sum = dsa_fenwick_query(fenwick, 1, 4)
dsa_fenwick_update(fenwick, 2, 6)

# 5. LRU Cache & Monotonic Queue
create lru cache with capacity 3 into cache
put key "a" with value 100 into cache cache
get key "a" from cache cache into cached_val

mq = dsa_monotonic_queue_create()
dsa_monotonic_queue_push(mq, 10)
dsa_monotonic_queue_push(mq, 20)
current_max = dsa_monotonic_queue_max(mq)

# 6. Search, Order Statistics & Graph Invariants
binary search 42 in sorted_nums into idx
k-th smallest element in nums with k 3 into third_min
k-th largest element in nums with k 1 into absolute_max
rabin karp search for "pattern" in text into match_indices
manacher longest palindrome in "babad" into longest_pal
count inversions in nums into inversion_count
find bridges in graph_matrix into critical_bridges
```

---

### 2. Data Engineering (`use data`)
Tabular ETL pipelines, SQL-like transforms, statistical profiling, and window functions:

```doomscript
use data

read csv "sales.csv" into raw_table

# 1. Statistical Data Profiler & Pivot Tables
profile = data_profile_dataframe(raw_table)
say "Data Profile Summary: ", profile["summary"]

pivot = data_pivot_table(raw_table, "region", "quarter", "revenue", "sum")

# 2. Data Cleaning & Imputation
forward fill missing values in column "price" of raw_table into ffilled_table
backward fill missing values in column "units" of ffilled_table into clean_table
coalesce columns [clean_table's preferred_phone, clean_table's backup_phone] into primary_contact

# 3. Window Expressions & Analytical Rankings
rank rows in clean_table by column "revenue" descending into ranked_table
future_price = data_window_lead(clean_table, "price", 1)
prev_price = data_window_lag(clean_table, "price", 1)
rolling_rev_30d = data_window_rolling_sum(clean_table, "revenue", 7)
rolling_avg_price = data_window_rolling_avg(clean_table, "price", 14)

# 4. Aggregations, Schema Validation & Joins
cumulative sum of column "revenue" in clean_table into running_revenue
cross join table_a with table_b into cartesian_table
validate schema of clean_table against schema_rules into validation_report
calculate summary of clean_table into statistical_overview
```

---

### 3. Machine Learning (`use ml`)
Full classification, CART decision trees, multilayer perceptrons, clustering, and metrics:

```doomscript
use ml

# 1. 3-Way Train/Val/Test Split & Preprocessing
split dataset samples into 70% train, 15% validation, 15% test into partitioned_data

# 2. CART Decision Tree (Gini/Entropy with Pruning)
cart_model = ml_train_cart_decision_tree(X_train, y_train, 5, 2, "gini")
cart_preds = ml_predict_cart_decision_tree(cart_model, X_test)

# 3. Multilayer Perceptron (Neural Network with Backpropagation)
mlp_model = ml_train_mlp(X_train, y_train, [16, 8], 0.01, 100, 32, "relu")
mlp_preds = ml_predict_mlp(mlp_model, X_test)

# 4. Classical Classifiers & Regressors
train knn classifier with features X_train and labels y_train and neighbors 5 into knn_model
train decision stump with features X_train and labels y_train into stump_model
train naive bayes with features X_train and labels y_train into bayes_model

# 5. Clustering & Dimensionality Reduction
cluster data X with kmeans using 3 clusters into clusters
apply pca to data X with 2 components into reduced_matrix

# 6. Evaluation Metrics
predict classes for X_test with model knn_model into y_pred
calculate f1 score between y_test and y_pred into f1_res
calculate precision between y_test and y_pred into precision_res
calculate recall between y_test and y_pred into recall_res
calculate log loss between y_true and y_prob into loss_val
calculate brier score between y_true and y_prob into brier_val
```

---

### 4. Quantitative Finance (`use finance`)
Technical indicators, portfolio risk metrics, Black-Scholes/Binomial options, GARCH volatility:

```doomscript
use finance

# 1. Advanced Options Pricing & Greeks
bs_res = finance_black_scholes(100.0, 95.0, 0.5, 0.05, 0.20, "call")
say "Call Price: ", bs_res["price"], " Delta: ", bs_res["delta"], " Vega: ", bs_res["vega"]

american_put = finance_binomial_option_tree(100.0, 95.0, 0.5, 0.05, 0.20, 100, False, True)
say "American Put Tree Price: ", american_put["price"]

# 2. GARCH Volatility & Momentum Oscillators
garch_vols = finance_garch11_volatility(daily_returns, 0.00001, 0.08, 0.90)
macd_data = finance_macd(closing_prices, 12, 26, 9)
rsi_val = finance_rsi(closing_prices, 14)

# 3. Technical Indicators
calculate vwap with high prices_high low prices_low close prices_close volume volumes into vwap_series
stochastic oscillator with high prices_high low prices_low close prices_close period 14 into stoch_vals
keltner channels for prices with period 20 and multiplier 2.0 into keltner
average true range for high prices_high low prices_low close prices_close period 14 into atr_vals
williams r for high prices_high low prices_low close prices_close period 14 into will_r
money flow index for high prices_high low prices_low close prices_close volume volumes period 14 into mfi_vals

# 4. Risk & Performance Metrics
sortino ratio of returns with risk_free 0.02 into sortino_val
treynor ratio of returns with beta 1.1 and risk_free 0.02 into treynor_val
calmar ratio of returns with max_drawdown 0.15 into calmar_val
beta of asset_returns against market_returns into beta_val
jensen alpha of asset_returns against market_returns with risk_free 0.02 and beta 1.1 into alpha_val
rebalance portfolio holdings to target_weights into trade_orders
```

---

### 5. NLP & Text Intelligence (`use nlp`)
Text processing, HMM POS tagging, Byte-Pair Encoding, BLEU evaluation, and vectorization:

```doomscript
use nlp

# 1. Hidden Markov Model (HMM) Part-of-Speech Tagging
train_corpus = [[["The", "DT"], ["dog", "NN"], ["barks", "VBZ"]]]
hmm_tagger = nlp_hmm_pos_tagger(train_corpus)
tagged_sent = nlp_hmm_tag_sequence(hmm_tagger, ["The", "dog", "runs"])

# 2. Byte Pair Encoding (BPE) Subword Tokenizer
bpe_model = nlp_byte_pair_encoder(["low", "lower", "newest", "widest"], 10)
bpe_tokens = nlp_bpe_encode(bpe_model, "lowest")
reconstructed_text = nlp_bpe_decode(bpe_model, bpe_tokens)

# 3. Translation Quality & Vectorization
bleu = nlp_bleu_score(["the", "cat", "sat", "on", "mat"], [["the", "cat", "sat", "on", "the", "mat"]], 4)
tfidf_model = nlp_tfidf_vectorizer(["machine learning in python", "deep learning natural language"])
doc_vector = nlp_tfidf_transform(tfidf_model, "machine learning algorithms")

# 4. Information Retrieval & Linguistic Distances
rank corpus doc_collection for query "search terms" using bm25 into ranked_docs
levenshtein distance between "kitten" and "sitting" into edit_distance
hamming distance between "1011101" and "1001001" into bit_diff

# 5. Phonetics & Readability Metrics
soundex "Robert" into soundex_code
metaphone "Knight" into metaphone_code
porter stem of "generously" into root_word
flesch reading ease of article into readability_score
gunning fog index of article into fog_score
count syllables in "incomprehensible" into syllable_count

# 6. Sentiment & Sanitization
rouge-l score between generated_text and reference_text into rouge_res
expand contractions in "don't won't shouldn't" into expanded_text
mask sensitive entities in user_bio into sanitized_bio
vader sentiment of customer_review into sentiment_scores
```

---

### 6. Graph Theory (`use graph`)
Network modeling, Tarjan SCC, Edmonds-Karp max flow, A* search, and Louvain communities:

```doomscript
use graph

# 1. Tarjan Strongly Connected Components (SCC)
adj = {"A": ["B"], "B": ["C"], "C": ["A", "D"], "D": ["E"], "E": ["D"]}
sccs = graph_tarjan_scc(adj)
say "Strongly Connected Components: ", sccs

# 2. Maximum Flow (Edmonds-Karp Residual Network)
flow_adj = {"S": {"A": 10, "B": 5}, "A": {"B": 15, "T": 10}, "B": {"T": 10}, "T": {}}
flow_res = graph_max_flow_edmonds_karp(flow_adj, "S", "T")
say "Maximum Network Flow: ", flow_res["max_flow"]

# 3. A* Heuristic Search & Louvain Community Detection
astar_res = graph_astar_search(grid_graph, node_coordinates, "start", "goal")
communities = graph_louvain_community_detection(social_adj)

# 4. Structural Properties & Link Prediction
clustering coefficient of social_graph into clustering_score
find bridges in communication_graph into network_bottlenecks
find articulation points in road_network into critical_junctions
transitive closure of dag_graph into reachable_matrix
topological generations of dependency_graph into execution_phases
k core decomposition of graph with k 3 into dense_subgraph
predict links in user_network using adamic adar into friend_recommendations
predict links in citation_network using jaccard into related_papers
```

---

### 7. Computer Vision & Media (`use image`)
Image generation, Canny edge detection, Otsu thresholding, Gaussian blur, and filters:

```doomscript
use image

create canvas with width 640 and height 480 and color "white" into img
load image "photo.jpg" into photo

# 1. Advanced Computer Vision Filters
blurred = image_gaussian_blur(photo_pixels, 640, 480, 2, 1.4)
canny_edges = image_canny_edge_detector(blurred, 640, 480, 50, 150)
otsu_binary = image_otsu_threshold(photo_pixels, 640, 480)
equalized = image_histogram_equalize(photo_pixels, 640, 480)

# 2. Filtering & Pixel Manipulation
apply sobel filter to photo into edges
threshold photo with cutoff 128 into binarized_img
sharpen image photo with factor 1.5 into sharp_photo
invert colors of photo into negative_photo
adjust contrast of photo with factor 1.2 into contrasted_photo
apply sepia filter to photo into vintage_photo

# 3. Spatial & Channel Operations
split channels of photo into rgb_channels
merge channels rgb_channels into restored_photo
flip photo horizontally into mirrored_photo
apply vignette to photo with intensity 0.7 into artistic_photo
pixelate photo with block_size 8 into mosaic_photo
calculate mean color of photo into average_rgb
```

---

### 8. Web Scraping & DOM (`use web`)
Declarative CSS selectors, OpenGraph/JSON-LD metadata extraction, and RFC 9309 robots.txt:

```doomscript
use web

# 1. Pure-Python CSS Selector Engine
matched_nodes = web_select_css(page_html, "div.content > article#main-story p.highlight")

# 2. Rich Social Metadata & JSON-LD Extraction
meta = web_extract_metadata(page_html)
say "Page Title: ", meta["title"]
say "OpenGraph Image: ", meta["opengraph"]["image"]
say "JSON-LD Entities: ", meta["json_ld"]

# 3. RFC 9309 Robots.txt Parser
can_crawl = web_parse_robots_txt(robots_txt_content, "Googlebot", "/api/v1/users")

# 4. Form Parsing & Link Inspection
parse form inputs from html_code into form_data
generate url encoded string from parameters into query_string
extract urls from sitemap sitemap_xml into catalog_urls
canonicalize url "https://example.com/item/../index.html" into clean_url
extract headings from page_html into heading_structure
serialize cookies cookie_jar into cookie_header
generate curl command for url "https://api.test.com" with method "POST" and headers req_headers into curl_cmd
```

---

### 9. Audio Synthesis & DSP (`use audio`)
Sound generation, STFT spectrograms, MFCC feature extraction, and pitch shifting:

```doomscript
use audio

# 1. STFT Spectrogram & Inverse Reconstruction
stft_spec = audio_stft(audio_samples, 512, 128)
reconstructed_audio = audio_istft(stft_spec, 128)

# 2. Speech Feature Extraction & Pitch Shifting
mfcc_matrix = audio_mfcc(speech_samples, 16000, 13, 512, 256)
shifted_pitch = audio_pitch_shift(speech_samples, 4.0, 16000)

# 3. Waveform Generators
generate square wave with frequency 440.0 and duration 1.0 into sq_tone
generate sawtooth wave with frequency 220.0 and duration 1.0 into saw_tone
generate triangle wave with frequency 880.0 and duration 1.0 into tri_tone
generate white noise with duration 2.0 into ambient_noise

# 4. Signal Processing & Mixing
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
Fluent SQL Query Builder, In-Memory Relational Engine, and Migration Manager:

```doomscript
use db

# 1. Fluent SQL AST Query Builder
qb = db_query_builder("users")
sql_ast = qb.select(["id", "name", "email"]).where("status = 'active'").join("orders", "users.id = orders.user_id").order_by("created_at", "DESC").build()
say "Generated SQL: ", sql_ast["sql"]

# 2. In-Memory Relational Database Engine
mem_db = db_in_memory_engine()
mem_db.create_table("products", ["id", "name", "price", "stock"])
mem_db.insert("products", {"id": 1, "name": "Laptop", "price": 1200, "stock": 15})
low_stock = mem_db.select("products", lambda r: r["stock"] < 20)

# 3. Schema Migration Manager with Rollback
migrator = db_migration_manager()
migrator.add_migration("v1_init", "CREATE TABLE items (id INT);", "DROP TABLE items;")
migrator.migrate()
migrator.rollback()

# 4. SQLite Administration & Automation
connect to database "app.db" into db
create index "idx_user_email" on table "users" with column "email" in db
vacuum database db
analyze database statistics for db
list tables in db into table_names
list indexes on table "users" in db into user_indexes
bulk insert records new_users into table "users" in db with batch 500
export table "users" from db to csv "users_backup.csv"
export ddl schema from db into schema_sql
```

---

### 11. Networking & System (`use net`)
RFC 7540 HTTP/2 frames, IPv4/TCP packet dissector, RFC 6455 WebSockets, and CIDR math:

```doomscript
use net

# 1. HTTP/2 Binary Framing (RFC 7540)
parsed_frame = net_http2_parse_frame(raw_h2_bytes)
say "HTTP/2 Frame Type: ", parsed_frame["type"], " Stream ID: ", parsed_frame["stream_id"]

# 2. Raw Packet Dissector & Internet Checksum
packet = net_dissect_ipv4_packet(ethernet_payload_bytes)
say "Source IP: ", packet["src_ip"], " Destination: ", packet["dst_ip"], " Protocol: ", packet["protocol"]

# 3. WebSocket Masking & Framing (RFC 6455)
ws_frame = net_websocket_frame("Hello, DoomScript Server!", True, True)

# 4. IP & CIDR Networking
calculate netmask for cidr "192.168.1.0/24" into subnet_mask
check if ip "192.168.1.55" is in subnet "192.168.1.0/24" into in_local_net
expand cidr range "10.0.0.0/29" into available_ips
validate ipv4 address "172.16.0.1" into is_valid_v4
validate ipv6 address "2001:db8::1" into is_valid_v6
format mac address "001A2B3C4D5E" to standard into formatted_mac
query whois for domain "doomscript.org" into domain_whois
exponential backoff delays with base 1.5 and attempts 5 into retry_schedule
scan open ports on host "127.0.0.1" for ports [80, 443, 8080] into open_ports
```

---

### 12. Simulation & Stochastics (`use sim`)
M/M/c queuing networks, Conway 2D Cellular Automata, Reynolds Boids, and Markov processes:

```doomscript
use sim

# 1. Multi-Server Queuing Network (M/M/c)
mmc = sim_queue_system(5.0, 3.0, 2)
say "M/M/c System Utilization: ", mmc["utilization"], " Mean Wait: ", mmc["mean_wait_time"]

# 2. 2D Cellular Automata (Conway's Game of Life / B3/S23)
ca = sim_cellular_automaton(50, 50, "B3/S23", glider_gun_seed, 100)

# 3. Autonomous Swarm & Flocking Simulation (Reynolds Boids)
flock = sim_boids_flocking(50, 200, [500, 500], 50.0)

# 4. Markov Chains & Processes
simulate markov chain with transitions transition_matrix and steps 50 from state 0 into state_history
simulate wiener process with drift 0.05 and volatility 0.2 and steps 100 into stock_path

# 5. Random Variate Distributions & Bootstrap Testing
generate geometric variates with probability 0.3 and size 1000 into geo_samples
generate binomial variates with trials 10 and probability 0.5 and size 500 into binom_samples
generate triangular variates with low 0.0 high 10.0 mode 3.0 and size 100 into tri_samples
calculate bootstrap confidence interval for observations with percentiles [2.5, 97.5] and resamples 1000 into conf_int
run permutation test between sample_a and sample_b with permutations 500 into p_value
```

---

### 13. Geospatial Analytics (`use geo`)
Vincenty WGS-84 geodesic distance, point-in-polygon raycasting, spherical area, and R-Trees:

```doomscript
use geo

# 1. Vincenty Geodesic Distance (WGS-84 Ellipsoid Precision)
dist_meters = geo_vincenty_distance(37.7749, -122.4194, 34.0522, -118.2437)
say "Vincenty Distance: ", dist_meters, " meters"

# 2. Point-In-Polygon & Spherical Polygon Area
inside = geo_point_in_polygon([37.75, -122.42], city_boundary_polygon)
area_sqkm = geo_polygon_area_sq_km(national_park_polygon)

# 3. 2D Spatial R-Tree Indexing
rtree = geo_rtree_create()
rtree.insert("store_101", [37.77, -122.42, 37.78, -122.41])
nearby_stores = rtree.search([37.76, -122.43, 37.79, -122.40])

# 4. Geohash, Navigation & Douglas-Peucker Simplification
encode geohash for latitude 37.7749 and longitude -122.4194 with precision 8 into sfo_hash
decode geohash sfo_hash into sfo_coords
cross track distance from point p to path start_pt, end_pt into off_track_meters
destination point from start_pt with bearing 90.0 and distance 50.0 km into east_pt
calculate convex hull of perimeter_points into boundary_polygon
simplify path polyline_coords using douglas peucker with tolerance 0.01 into compressed_path
```

---

### 14. Optimization & OR (`use opt`)
Simulated Annealing, Genetic Algorithms, Particle Swarm (PSO), and Nelder-Mead:

```doomscript
use opt

# 1. Heuristic Metaheuristic Optimizers
sa_sol = opt_simulated_annealing(cost_function, [0.0, 0.0], neighbor_generator, 100.0, 0.95, 1000)
say "Simulated Annealing Best: ", sa_sol["best_cost"]

ga_sol = opt_genetic_algorithm(fitness_function, 32, 50, 100, 0.02)
say "Genetic Algorithm Best Fitness: ", ga_sol["best_fitness"]

pso_sol = opt_particle_swarm(sphere_cost, 30, 5, [[-5.0, 5.0]] * 5, 200)
simplex_sol = opt_nelder_mead(rosenbrock_cost, [1.5, 1.5], 0.1, 500)

# 2. Dynamic Programming & Discrete Optimization
solve 0/1 knapsack with weights [2, 3, 4, 5] and values [3, 4, 5, 6] and capacity 8 into knapsack_max
longest increasing subsequence in [10, 9, 2, 5, 3, 7, 101, 18] into lis_seq
minimum coins for amount 11 with denominations [1, 2, 5] into min_coins
build huffman tree from frequencies char_freqs into huffman_codes
solve traveling salesperson for distance_matrix using 2-opt into tsp_tour
solve bipartite matching for cost_matrix using hungarian into optimal_assignment
```

---

### 15. AI Agents & Multi-Agent Workflows (`use agent`)
Tool Execution Harness, Sliding-Window Token Memory, ReAct Reasoning Agent:

```doomscript
use agent

# 1. Strict Tool Execution Harness
harness = agent_tool_harness()
harness.register_tool("fetch_weather", weather_fn, weather_schema)
tool_result = harness.execute_tool("fetch_weather", {"city": "San Francisco"})

# 2. Sliding-Window Agent Memory Buffer
memory = agent_memory_buffer(20, 2048)
memory.add_message("user", "Analyze recent sales report")
memory.add_message("assistant", "Starting analysis on Q3 dataset...")
active_context = memory.get_context()

# 3. Autonomous ReAct (Reasoning + Acting) Agent
react_agent = agent_react_agent([search_tool, calculator_tool], "You are an autonomous research analyst.")
solution = react_agent.run("What is 15% of the market cap of Apple?")

# 4. Multi-Agent Team Coordination
create agent researcher with role "data investigator" into agent_a
create agent critic with role "fact checker" into agent_b
create team review_board with agents [agent_a, agent_b] into editorial_board
tally consensus votes from ["approve", "approve", "reject"] with threshold 0.6 into vote_outcome
adjudicate debate between agent_a and agent_b on topic "Microservices vs Monolith" into winner_verdict
```

---

### 16. Cloud Storage & Infrastructure (`use cloud`)
Storage bucket lifecycle, IAM policy evaluation, multipart uploads, and multi-cloud cost calculator:

```doomscript
use cloud

# 1. Pure Cloud Storage Manager (Multipart & Versioning)
csm = cloud_storage_manager()
csm.upload_part("dataset-2026", "chunks/part1.bin", 1, chunk1_bytes)
csm.upload_part("dataset-2026", "chunks/part1.bin", 2, chunk2_bytes)
csm.complete_multipart("dataset-2026", "chunks/part1.bin")
versions = csm.list_versions("dataset-2026", "chunks/part1.bin")

# 2. IAM Policy Engine (Allow/Deny, Actions, Resources, Conditions)
iam = cloud_iam_policy_engine()
iam.add_policy("DeveloperAccess", {
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject"],
    "Resource": "arn:aws:s3:::prod-bucket/*"
})
can_read = iam.evaluate("DeveloperAccess", "s3:GetObject", "arn:aws:s3:::prod-bucket/app.json")

# 3. Multi-Cloud Cost Calculator (AWS, GCP, Azure)
calc = cloud_cost_calculator()
monthly_cost = calc.estimate_monthly({
    "provider": "aws",
    "instances": [{"type": "t4g.xlarge", "count": 4}],
    "storage_gb": 500,
    "egress_gb": 200
})
say "Estimated Monthly Infrastructure Cost: $", monthly_cost["total_usd"]

# 4. Storage Bucket Operations & Mirroring
connect to bucket "production-store" into b1
connect to bucket "backup-store" into b2
write text "System log line" to object "logs/app.log" in b1
read text from object "logs/app.log" in b1 into log_data
generate presigned put url for "uploads/data.bin" in b1 with expiry 1800 into upload_url
verify sha256 checksum of "logs/app.log" in b1 against expected_hash into sha_ok
mirror bucket b1 to b2 into mirror_report
diff bucket b1 with bucket b2 into audit_diff
export bucket manifest for b1 to "manifest.json" into exported_manifest
```

---

### 17. Office & Documents (`use office`)
Zero-dependency OpenXML `.xlsx`, `.docx`, `.pptx` generators and spreadsheet analytics:

```doomscript
use office

# 1. Pure-Python OpenXML Excel Generator (.xlsx)
wb = office_xlsx_workbook()
wb.add_sheet("Financials")
wb.set_cell("Financials", "A1", "Quarter")
wb.set_cell("Financials", "B1", "Revenue")
wb.set_cell("Financials", "A2", "Q1")
wb.set_cell("Financials", "B2", 150000)
wb.set_cell("Financials", "A3", "Q2")
wb.set_cell("Financials", "B3", 220000)
wb.set_cell("Financials", "B4", "=SUM(B2:B3)")
wb.save("reports/financials.xlsx")

# 2. Pure-Python OpenXML Word Generator (.docx)
doc_gen = office_docx_document()
doc_gen.add_heading("Quarterly Performance Review", 1)
doc_gen.add_paragraph("Enterprise ARR expanded by 42% year-over-year.")
doc_gen.add_table(["Department", "Headcount", "Budget"], [["Engineering", "28", "$1.4M"], ["Product", "12", "$0.6M"]])
doc_gen.save("reports/review.docx")

# 3. Pure-Python Presentation Generator (.pptx)
deck = office_pptx_presentation()
deck.add_slide("Board Meeting", "Q3 Strategy & Financial Highlights")
deck.save("reports/board.pptx")

# 4. CSV & Spreadsheet Utilities
detect csv delimiter "records.csv" into detected_delim
read csv header "records.csv" into header_list
load spreadsheet "financials.xlsx" into sheet
calculate sheet summary for sheet in "Financials" at column "Revenue" into revenue_stats
```

---

### 18. Research & Scientific Computing (`use research`)
Autograd reverse-mode autodiff, BibTeX citations, and citation networks:

```doomscript
use research

# 1. BibTeX Reference Engine (Parsing & IEEE/APA Formatting)
bib = research_bibtex_engine()
bib.parse_bibtex_entry("""@article{turing1936,
    author = {Turing, Alan M.},
    title = {On Computable Numbers},
    journal = {Proc. London Math. Soc.},
    year = {1936}
}""")
apa_citation = bib.format_citation("turing1936", "apa")
ieee_citation = bib.format_citation("turing1936", "ieee")

# 2. Citation Network Analytics (h-index, i10-index, PageRank Prestige)
cnet = research_citation_network()
cnet.add_paper("p1", "Attention Is All You Need", "Vaswani et al.", 2017)
cnet.add_paper("p2", "BERT", "Devlin et al.", 2018)
cnet.add_citation("p2", "p1")
h_index = cnet.calculate_author_h_index("Vaswani et al.")
prestige_scores = cnet.calculate_pagerank_prestige()

# 3. Reverse-Mode Autograd Engine
w1 = scalar 2.0 with gradient
x = scalar 3.0
b = scalar 1.5 with gradient
y = (w1 * x) + b
backward y
say "w1 gradient: ", w1's gradient  # dy/dw1 = 3.0
say "b gradient: ", b's gradient    # dy/db = 1.0

# 4. Exact Graph Algorithms & Network Flow
create a research graph into g
add edge from "A" to "B" with weight 4.0 to g
add edge from "A" to "C" with weight 2.0 to g
add edge from "C" to "B" with weight 1.0 to g
find shortest path from "A" to "B" in g using dijkstra into dijk_res
maximum flow from "A" to "B" in g using edmonds karp into max_flow
calculate pagerank of g with damping 0.85 into rank_scores
```

---

### 19. Bioinformatics & Genomics (`use bio`)
DNA/RNA transcription, reverse complement, Needleman-Wunsch & Smith-Waterman alignment, ORF finding:

```doomscript
use bio

dna = "ATGCGATCGATCGATCGTAA"

# 1. Sequence Metrics & Central Dogma
gc_val = bio_gc_content(dna)
say "GC Content: ", gc_val, "%"

transcribed_rna = bio_transcribe(dna)
say "Transcribed RNA: ", transcribed_rna

rev_comp = bio_reverse_complement("ATGC")
say "Reverse Complement: ", rev_comp

protein_seq = bio_translate("AUGUUUUAA")
say "Translated Peptides: ", protein_seq

# 2. Open Reading Frames (ORFs) & Motifs
open_frames = bio_find_orfs("ATGCGATAA", 1)
kmer_counts = bio_kmer_counts("ATGCAT", 2)
motif_positions = bio_find_motif("ATGCATGC", "ATG")
weight_daltons = bio_molecular_weight("ATGC")

# 3. Dynamic Programming Sequence Alignment
global_alignment = bio_needleman_wunsch("GATTACA", "GCATGCU", 1, -1, -1)
say "Needleman-Wunsch Score: ", global_alignment["score"]
say "Alignment Seq 1: ", global_alignment["alignment1"]
say "Alignment Seq 2: ", global_alignment["alignment2"]

local_alignment = bio_smith_waterman("TGTTACGG", "GGTTGACTA", 2, -1, -2)
say "Smith-Waterman Local Alignment Score: ", local_alignment["score"]

# 4. FASTA Parsing
fasta_records = bio_parse_fasta(">seq1 Human Actin\\nATGCGAT\\n>seq2 Mouse Beta\\nCCGGAAT")
say "First Record ID: ", fasta_records[0]["id"]
```

---

### 20. Classical & Modern Physics (`use physics`)
Ballistic trajectories with drag, SAT polygon collisions, harmonic oscillators, and PID control:

```doomscript
use physics

# 1. Projectile Kinematics (Ideal & Aerodynamic Drag)
ideal_traj = physics_projectile_trajectory(20.0, 45.0, 9.81, 10)
ideal_range = physics_projectile_range(20.0, 45.0, 9.81)

drag_traj = physics_drag_trajectory(20.0, 45.0, 0.05, 1.0, 9.81, 0.05, 100)
say "Range with Drag: ", drag_traj[-1]["x"], " meters"

# 2. Rigid Body Collision Detection (AABB & SAT)
is_colliding = physics_check_aabb_collision(0, 0, 10, 10, 5, 5, 10, 10)

poly_a = [[0, 0], [10, 0], [10, 10], [0, 10]]
poly_b = [[5, 5], [15, 5], [15, 15], [5, 15]]
sat_overlap = physics_check_sat_collision(poly_a, poly_b)

# 3. Dynamic Systems & Astrophysics
damped_wave = physics_harmonic_oscillator(1.0, 10.0, 0.5, 1.0, 0.0, 0.02, 50)
v_orbit = physics_orbital_velocity(5.972e24, 6371000.0)
v_escape = physics_escape_velocity(5.972e24, 6371000.0)

# 4. Closed-Loop PID Controller
pid = physics_create_pid(1.5, 0.1, 0.05)
control_output = physics_update_pid(pid, 100.0, 92.5, 0.1)
say "PID Correction Voltage: ", control_output
```

---

### 21. Cybersecurity & Cryptographic Primitives (`use sec`)
Shannon entropy, password audits, Caesar/Vigenere/XOR ciphers, JWT decoding, CVSS v3.1:

```doomscript
use sec

# 1. Password Strength Auditing & Shannon Entropy
pwd_entropy = sec_entropy("CorrectHorseBatteryStaple123!")
audit_report = sec_audit_password("Admin@123456!")
say "Password Strength Score: ", audit_report["score"], "/4"

# 2. Classical & Symmetric Cryptography
caesar_cipher = sec_caesar_cipher("Hello World", 3)
cracked_caesar = sec_caesar_crack(caesar_cipher)
say "Cracked Plaintext: ", cracked_caesar["plaintext"], " (Shift: ", cracked_caesar["shift"], ")"

vigenere_cipher = sec_vigenere_cipher("ATTACKATDAWN", "LEMON", True)
vigenere_plain = sec_vigenere_cipher(vigenere_cipher, "LEMON", False)

xor_ciphertext = sec_xor_cipher("SecretMessage", "MySecretKey")
xor_recovered = sec_xor_cipher(xor_ciphertext, "MySecretKey")

# 3. Security Inspection & Forensics
token_data = sec_decode_jwt(jwt_token_string)
say "Token Subject: ", token_data["claims"]["sub"]

hex_representation = sec_hexdump("DoomScript Security Domain")
cvss_score = sec_cvss_score(8.0, 3.0, 2.0)
banner_info = sec_parse_banner("SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\\r\\n")
say "Detected Service: ", banner_info["service"], " Version: ", banner_info["version"]
```

---

### 22. Game Systems & Physics Simulation (`use game`)
Dice notation evaluation, loot tables, tilemaps, A* grid pathfinding, and turn resolution:

```doomscript
use game

# 1. Dice Rolling & Weighted Loot Generation
dice_result = game_roll_dice("2d6 + 3")
say "Rolled 2d6 + 3: ", dice_result

dropped_item = game_weighted_choice(["common_sword", "rare_bow", "legendary_staff"], [70, 25, 5])
say "Loot Drop: ", dropped_item

# 2. 2D Tilemap & A* Grid Pathfinding
tilemap = game_create_tilemap(10, 10, 0)
game_set_tile(tilemap, 3, 3, 1)  # 1 = Wall / Obstacle
path = game_astar_grid(tilemap, 0, 0, 8, 8)
has_los = game_has_line_of_sight(tilemap, 0, 0, 0, 8)

# 3. Turn-Based RPG Combat & Status Effects
attacker = Record({"name": "Warrior", "atk": 35, "hp": 120})
defender = Record({"name": "Dragon", "defense": 10, "hp": 250})
combat_round = game_resolve_turn(attacker, defender, 1.2)
say "Damage Dealt: ", combat_round["damage"], " Dragon HP: ", defender["hp"]

status_report = game_apply_status_effect(defender, "burn", 3, 15)
```

---

### 23. Quantum Computing & State Simulation (`use quantum`)
Statevector quantum registers, Hadamard, Pauli, CNOT gates, Bell state preparation, measurement:

```doomscript
use quantum

# 1. Quantum Register & Superposition
reg = quantum_create_register(2)
quantum_apply_h(reg, 0)         # Put qubit 0 into (|0> + |1>)/sqrt(2)
quantum_apply_cnot(reg, 0, 1)     # Entangle qubit 0 and qubit 1 into Bell state

# 2. Quantum State Vector & Measurement
bell_state = quantum_state_vector(reg)
say "Bell State Amplitudes: ", bell_state

# 3. Multi-Shot Quantum Circuit Sampling
measurement_counts = quantum_sample(reg, 1000)
say "Measurement Distribution: ", measurement_counts

# 4. Standard Bell States & Single Qubit Gates
phi_plus = quantum_bell_state("phi_plus")
reg_single = quantum_create_register(1)
quantum_apply_x(reg_single, 0)    # Pauli-X (NOT gate)
measured_bit = quantum_measure(reg_single, 0)
say "Measured Qubit State: ", measured_bit  # 1
```

---

### 24. Electrical Engineering & Circuit Analysis (`use circuit`)
Ohm's law, resistor color code bands, voltage dividers, 555 timers, logic gates, GPIO pins:

```doomscript
use circuit

# 1. Ohm's Law & Power
circuit_sol = circuit_ohms_law(None, 2.5, 10.0)  # voltage = None, current = 2.5A, resistance = 10 Ohm
say "Calculated Voltage: ", circuit_sol["voltage"], "V, Power: ", circuit_sol["power"], "W"

# 2. Resistor Color Band Decoding
resistor = circuit_resistor_bands("brown", "black", "red", "gold")
say "Resistance: ", resistor["resistance"], " Ohms, Tolerance: ±", resistor["tolerance"], "%"

# 3. Analog Electronics: Voltage Dividers & 555 Timers
vdiv = circuit_voltage_divider(12.0, 1000.0, 2000.0)
say "Output Voltage: ", vdiv["v_out"], "V"

timer = circuit_555_timer(1000.0, 2000.0, 0.000001)
say "555 Astable Frequency: ", timer["frequency"], " Hz, Duty Cycle: ", timer["duty_cycle"], "%"

rc_circuit = circuit_rc_time_constant(10000.0, 0.000001)
say "RC Time Constant (tau): ", rc_circuit["tau"], " seconds"

# 4. Digital Logic & Virtual GPIO
logic_val = circuit_eval_logic("XOR", [True, False])
effective_pwm = circuit_pwm_analog_value(75.0, 5.0)  # 75% duty cycle at 5V = 3.75V

gpio = circuit_create_gpio([1, 2, 3, 4])
circuit_set_pin(gpio, 2, 1)
pin_state = circuit_read_pin(gpio, 2)
```

---

### 25. Blockchain, Cryptographic Ledgers & Merkle Trees (`use chain`)
Merkle tree proofs, Proof-of-Work mining, UTXO transaction ledger, EIP-55 checksum addresses:

```doomscript
use chain

# 1. Cryptographic Merkle Tree & Inclusion Proofs
transactions = ["tx1_alice_to_bob_10", "tx2_bob_to_carol_5", "tx3_carol_to_dave_2"]
mt = chain_create_merkle_tree(transactions)
merkle_root = chain_get_merkle_root(mt)
say "Merkle Root: ", merkle_root

proof = chain_get_merkle_proof(mt, 0)
is_valid = chain_verify_merkle_proof(transactions[0], proof, merkle_root)
say "Inclusion Proof Valid: ", is_valid

# 2. Proof-of-Work Mining Simulation
block = chain_mine_pow_block(1, merkle_root, "0000000000000000", 2)
say "Mined Block Nonce: ", block["nonce"], " Hash: ", block["hash"]
pow_valid = chain_verify_pow_block(block, 2)

# 3. UTXO Transaction Ledger
ledger = chain_create_utxo_ledger()
# Genesis transaction
chain_add_utxo_tx(ledger, "tx_genesis", [], [Record({"address": "Alice", "amount": 100})])
# Spend transaction
chain_add_utxo_tx(ledger, "tx_spend", 
    [Record({"tx_id": "tx_genesis", "output_index": 0})], 
    [Record({"address": "Bob", "amount": 40}), Record({"address": "Alice", "amount": 60})])

alice_bal = chain_get_utxo_balance(ledger, "Alice")
bob_bal = chain_get_utxo_balance(ledger, "Bob")
say "Alice Balance: ", alice_bal, " Bob Balance: ", bob_bal

# 4. Ethereum EIP-55 Checksum Address
eip55_address = chain_eip55_address("0xfb6916095ca1df60bb79ce92ce3ea74c37c5d359")
say "Checksummed Address: ", eip55_address
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
