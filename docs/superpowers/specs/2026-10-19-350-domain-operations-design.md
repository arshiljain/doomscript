# Specification: 350 Spoken-English Domain Operations for DoomScript

**Date:** 2026-10-19  
**Status:** In Review / Approved Design Brief  
**Goal:** Implement 350 additional spoken-English domain operations distributed across all 18 DoomScript domains (~19-20 operations per domain), bringing the total library of high-level algorithmic domain verbs to ~470+, all implemented with 100% natural English syntax, zero heavy third-party dependencies, and zero regressions.

---

## Architecture & System Design

Each domain adheres to the clean architectural layering of DoomScript:
1. **Core Language & Grammar**: Maintains generic expressions, loops, control flow, and statements.
2. **Domain Runtime Modules (`src/doomscript/domains/<domain>/runtime.py`)**: Pure Python computational algorithms with 0 external C/cloud dependencies.
3. **Domain Parsers (`src/doomscript/domains/<domain>/parser.py`)**: Natural regex pattern matchers that compile spoken-English phrases into runtime invocations.
4. **Domain Registry & Contracts (`src/doomscript/domains/<domain>/__init__.py`)**: `can_handle_line` interception and `VerbSpec` registration for introspection (`explain domain`).
5. **Standard Runtime Re-export (`src/doomscript/runtime.py`)**: Central re-export of all domain helper functions for global availability across the compiler and execution runtime.

---

## Domain Allocation Matrix (352 Total Operations)

### 1. DSA (Advanced Data Structures & Algorithms) - 19 Operations
- `dsa_trie_insert(trie, word)`: Insert string into prefix tree.
- `dsa_trie_search(trie, word)`: Check if word exists in prefix tree.
- `dsa_trie_starts_with(trie, prefix)`: Check if any word starts with prefix.
- `dsa_dsu_create(size)`: Create Disjoint Set Union (Union-Find) with path compression & union-by-rank.
- `dsa_dsu_find(dsu, x)`: Find root representative of element.
- `dsa_dsu_union(dsu, x, y)`: Union sets containing elements x and y.
- `dsa_lru_create(capacity)`: Initialize an LRU Cache with O(1) get and put.
- `dsa_lru_get(cache, key, default)`: Retrieve item from LRU Cache.
- `dsa_lru_put(cache, key, value)`: Put item into LRU Cache, evicting oldest if full.
- `dsa_binary_search_left(arr, target)`: Find leftmost insertion index (bisect_left).
- `dsa_binary_search_right(arr, target)`: Find rightmost insertion index (bisect_right).
- `dsa_quickselect(arr, k)`: Find k-th smallest element in O(n) expected time.
- `dsa_kadane_2d(matrix)`: Find maximum sum subgrid in 2D array.
- `dsa_count_inversions(arr)`: Count number of inversions in list via merge-sort in O(n log n).
- `dsa_next_permutation(arr)`: Generate lexicographically next permutation.
- `dsa_prev_permutation(arr)`: Generate lexicographically previous permutation.
- `dsa_rabin_karp_search(text, pattern)`: Find occurrences of pattern using rolling polynomial hash.
- `dsa_manacher(text)`: Find longest palindromic substring in O(n) time.
- `dsa_tarjan_bridges(graph_or_adj)`: Find all critical bridges in an undirected graph.

### 2. Data (Tabular Processing & Wrangling) - 20 Operations
- `data_rank_column(data, col, method)`: Compute rank of elements (dense, min, average).
- `data_lag_column(data, col, offset, default)`: Shift column down by offset (LAG).
- `data_lead_column(data, col, offset, default)`: Shift column up by offset (LEAD).
- `data_cumulative_sum(data, col)`: Compute running cumulative sum.
- `data_cumulative_max(data, col)`: Compute running cumulative maximum.
- `data_cumulative_min(data, col)`: Compute running cumulative minimum.
- `data_coalesce_columns(data, cols, target)`: First non-null value across candidate columns.
- `data_multi_sort(data, specs)`: Multi-column sort by list of (col, ascending).
- `data_cross_join(data1, data2)`: Cartesian product cross join of two tables.
- `data_validate_schema(data, schema_dict)`: Check column existence and types.
- `data_rename_columns(data, rename_map)`: Rename columns in table.
- `data_clip_column(data, col, low, high)`: Clamp values in column between [low, high].
- `data_format_date_column(data, col, fmt)`: Parse and reformat date strings.
- `data_string_trim(data, col)`: Strip whitespace across text column.
- `data_string_upper(data, col)`: Convert text column to uppercase.
- `data_string_lower(data, col)`: Convert text column to lowercase.
- `data_fill_null_forward(data, col)`: Forward fill missing values.
- `data_fill_null_backward(data, col)`: Backward fill missing values.
- `data_extract_year(data, col)`: Extract year component from date column.
- `data_sample_fraction(data, frac, seed)`: Sample random fraction of rows.

### 3. ML (Classical Machine Learning & Metrics) - 20 Operations
- `ml_train_knn_classifier(train_x, train_y, k)`: K-Nearest Neighbors classifier.
- `ml_predict_knn_classifier(model, test_x)`: Predict with KNN classifier.
- `ml_train_decision_stump(train_x, train_y)`: Train single-level decision tree stump.
- `ml_predict_decision_stump(model, test_x)`: Predict with decision stump.
- `ml_naive_bayes_classifier(train_x, train_y)`: Gaussian Naive Bayes classifier.
- `ml_predict_naive_bayes(model, test_x)`: Predict with Gaussian Naive Bayes.
- `ml_kmeans_clustering(data, k, max_iters)`: K-Means clustering algorithm.
- `ml_pca_transform(data, n_components)`: Principal Component Analysis via power iteration.
- `ml_log_loss(y_true, y_prob)`: Binary cross-entropy log loss.
- `ml_brier_score(y_true, y_prob)`: Brier score loss for calibrated probabilities.
- `ml_label_encode(values)`: Encode categorical strings into integers.
- `ml_label_decode(encoded_vals, classes)`: Decode integer classes back to labels.
- `ml_f1_score(y_true, y_pred)`: Calculate harmonic mean F1-score.
- `ml_precision_score(y_true, y_pred)`: Calculate precision metric.
- `ml_recall_score(y_true, y_pred)`: Calculate recall metric.
- `ml_cosine_decay_lr(initial_lr, step, total_steps)`: Compute cosine learning rate schedule.
- `ml_polynomial_features(features, degree)`: Generate polynomial feature combinations.
- `ml_standardize_features(features)`: Zero-mean unit-variance scaling.
- `ml_clip_gradients(gradients, max_norm)`: Gradient norm clipping.
- `ml_train_test_val_split(data, ratios)`: 3-way split into train, val, and test.

### 4. Finance (Quantitative Finance & Portfolio Analytics) - 20 Operations
- `finance_vwap(prices, volumes)`: Volume-Weighted Average Price.
- `finance_stochastic_oscillator(high, low, close, k_period, d_period)`: Full Stochastic Oscillator.
- `finance_sortino_ratio(returns, risk_free, target_ret)`: Downside deviation Sortino ratio.
- `finance_treynor_ratio(returns, market_returns, risk_free)`: Systematic risk Treynor ratio.
- `finance_calmar_ratio(returns, prices)`: Annualized return over maximum drawdown.
- `finance_beta(asset_returns, market_returns)`: Beta covariance over market variance.
- `finance_alpha(asset_returns, market_returns, risk_free)`: Jensen's Alpha.
- `finance_black_scholes_call(s, k, t, r, sigma)`: European call option analytical price.
- `finance_black_scholes_put(s, k, t, r, sigma)`: European put option analytical price.
- `finance_hull_moving_average(prices, period)`: Hull Moving Average (HMA).
- `finance_keltner_channels(high, low, close, period, multiplier)`: Keltner Channel bands.
- `finance_atr(high, low, close, period)`: Average True Range volatility.
- `finance_williams_r(high, low, close, period)`: Williams %R momentum indicator.
- `finance_commodity_channel_index(high, low, close, period)`: Commodity Channel Index (CCI).
- `finance_money_flow_index(high, low, close, volume, period)`: Money Flow Index (MFI).
- `finance_rate_of_change(prices, period)`: Rate of Change (ROC).
- `finance_rebalance_portfolio(weights, target_weights, total_val)`: Optimal dollar trades to rebalance.
- `finance_compound_growth(principal, annual_rate, years, compounds_per_year)`: Future compounded value.
- `finance_bond_yield_to_maturity(price, par, coupon, periods)`: Bond YTM calculation via root finding.
- `finance_portfolio_variance(weights, cov_matrix)`: Aggregate portfolio variance.

### 5. NLP (Natural Language Processing & Linguistics) - 20 Operations
- `nlp_levenshtein_distance(s1, s2)`: Edit distance between strings.
- `nlp_flesch_reading_ease(text)`: Flesch Reading Ease score.
- `nlp_flesch_kincaid_grade(text)`: Flesch-Kincaid Grade level.
- `nlp_bleu_score(candidate, references)`: BLEU n-gram precision score.
- `nlp_rouge_l_score(candidate, reference)`: ROUGE-L longest common subsequence score.
- `nlp_extract_emails(text)`: Extract all valid email addresses.
- `nlp_extract_urls(text)`: Extract all web URLs from unstructured text.
- `nlp_extract_phone_numbers(text)`: Extract international/domestic phone numbers.
- `nlp_porter_stem(word)`: Algorithmic Porter Stemming.
- `nlp_character_frequencies(text)`: Distribution of characters in text.
- `nlp_count_syllables(word)`: Rule-based English syllable counter.
- `nlp_split_into_sentences(text)`: Linguistic sentence boundary tokenizer.
- `nlp_mask_sensitive_terms(text, terms, mask)`: Redact sensitive terms/PII.
- `nlp_jaro_winkler_similarity(s1, s2)`: Jaro-Winkler string similarity.
- `nlp_hamming_distance(s1, s2)`: Hamming distance between equal-length strings.
- `nlp_generate_text_ngrams(words, n)`: Contiguous n-gram tuples generator.
- `nlp_strip_accents(text)`: Unicode accent diacritic stripping.
- `nlp_slugify(text)`: URL slug generator from title string.
- `nlp_truncate_words(text, num_words, suffix)`: Word-boundary-aware truncation.
- `nlp_collocations(words, min_count)`: Bigram collocation association extractor.

### 6. Graph (Complex Networks & Graph Theory) - 20 Operations
- `graph_a_star_path(graph, start, goal, heuristic_fn)`: A* optimal heuristic pathfinder.
- `graph_floyd_warshall(graph)`: All-pairs shortest path matrix.
- `graph_clustering_coefficient(graph, node)`: Local clustering coefficient.
- `graph_average_clustering_coefficient(graph)`: Global average clustering coefficient.
- `graph_find_bridges(graph)`: Find critical bridge edges.
- `graph_find_articulation_points(graph)`: Cut vertices / articulation points.
- `graph_transitive_closure(graph)`: Reachability matrix of graph.
- `graph_is_tree(graph)`: Check if undirected graph is an acyclic tree.
- `graph_topological_generations(graph)`: Group DAG nodes into parallel execution tiers.
- `graph_k_core(graph, k)`: Subgraph of vertices with degree >= k.
- `graph_density(graph)`: Ratio of actual edges to possible edges.
- `graph_complement(graph)`: Complement graph with non-edges inverted.
- `graph_adamic_adar_index(graph, u, v)`: Adamic-Adar link prediction metric.
- `graph_jaccard_coefficient(graph, u, v)`: Neighborhood Jaccard similarity between nodes.
- `graph_preferential_attachment(graph, u, v)`: Preferential attachment link score.
- `graph_laplacian_matrix(graph)`: Degree matrix minus adjacency matrix.
- `graph_is_planar_heuristic(graph)`: Planarity check using Kuratowski / Euler criteria.
- `graph_eccentricity(graph, node)`: Maximum distance from node to any other node.
- `graph_radius(graph)`: Minimum eccentricity among all nodes.
- `graph_center(graph)`: Set of vertices whose eccentricity equals graph radius.

### 7. Image (Computer Vision & Manipulation) - 20 Operations
- `image_sobel_edge_detection(img)`: 2D Sobel convolution for edge magnitude.
- `image_threshold_binarize(img, threshold)`: Binarize image to pure black/white.
- `image_sharpen(img)`: High-pass sharpening convolution kernel.
- `image_invert_colors(img)`: Negative color inversion.
- `image_adjust_contrast(img, factor)`: Contrast stretching around midpoint 128.
- `image_split_channels(img)`: Separate RGB image into red, green, blue layers.
- `image_merge_channels(r_img, g_img, b_img)`: Combine 3 grayscale channels into RGB.
- `image_apply_sepia(img)`: Classic sepia photographic tone transformation.
- `image_flip_horizontal(img)`: Mirror image along vertical axis.
- `image_flip_vertical(img)`: Flip image upside down.
- `image_color_vignette(img, radius)`: Darkened photographic vignette border.
- `image_pad_borders(img, pad_size, color)`: Pad borders of image with color.
- `image_compute_mean_color(img)`: Average [R, G, B] color across all pixels.
- `image_crop_center(img, width, height)`: Symmetrical center crop of image.
- `image_gamma_correction(img, gamma)`: Exponential gamma luminance correction.
- `image_emboss(img)`: Directional 3D embossing convolution filter.
- `image_posterize(img, levels)`: Reduce color depth quantization to N levels.
- `image_mosaic_pixelate(img, block_size)`: Pixelate image into uniform mosaic tiles.
- `image_blend_overlay(img1, img2, alpha)`: Linear alpha blend of two equal-sized images.
- `image_difference(img1, img2)`: Absolute pixel-by-pixel difference map.

### 8. Web (Automation, Scraping & URLs) - 20 Operations
- `web_extract_images(html)`: Find all `<img src="...">` URLs.
- `web_extract_forms(html)`: Extract all `<form>` tags, actions, and inputs.
- `web_encode_form_data(params)`: URL-encode dictionary into `application/x-www-form-urlencoded`.
- `web_decode_form_data(query_str)`: Parse URL-encoded query string into dictionary.
- `web_parse_sitemap_xml(sitemap_xml)`: Extract all `<loc>` entries from XML sitemap.
- `web_parse_robots_txt(robots_txt, user_agent, path)`: Evaluate allowed/disallowed paths.
- `web_canonicalize_url(base_url, relative_url)`: Resolve relative link against base URL.
- `web_extract_meta_description(html)`: Extract `<meta name="description" content="...">`.
- `web_extract_headings(html)`: Hierarchical list of all `h1`, `h2`, `h3` tags.
- `web_check_ssl_expiry(domain)`: Query TLS socket and get days until certificate expiration.
- `web_parse_cookie_header(header_str)`: Parse HTTP `Set-Cookie` into structured dictionary.
- `web_build_cookie_header(cookies_dict)`: Format dictionary into standard `Cookie` header.
- `web_extract_json_ld(html)`: Parse `<script type="application/ld+json">` schema data.
- `web_strip_query_params(url)`: Clean URL removing all query strings and hashes.
- `web_count_element_tags(html, tag_name)`: Count occurrences of specific HTML tag.
- `web_extract_text_by_class(html, class_name)`: Extract text from elements with CSS class.
- `web_extract_element_by_id(html, id_name)`: Extract element contents with specific HTML id.
- `web_parse_content_type(header_str)`: Extract mime-type and charset from HTTP header.
- `web_is_valid_url(url)`: Validate well-formed RFC URL structure.
- `web_generate_curl_command(method, url, headers, body)`: Format cURL command equivalent.

### 9. Audio (Sound Synthesis & DSP) - 19 Operations
- `audio_generate_square(freq, duration, sample_rate)`: Square wave synthesis.
- `audio_generate_sawtooth(freq, duration, sample_rate)`: Sawtooth wave synthesis.
- `audio_generate_triangle(freq, duration, sample_rate)`: Triangle wave synthesis.
- `audio_generate_white_noise(duration, sample_rate)`: Uniform white noise generator.
- `audio_adjust_gain_db(audio, decibels)`: Amplitude scaling via dB change: $10^{(dB/20)}$.
- `audio_trim_silence(audio, threshold)`: Cut leading/trailing silence below threshold.
- `audio_apply_fade_out(audio, duration)`: Linear fade-out at end of track.
- `audio_mix_tracks(track1, track2, weight1, weight2)`: Weighted polyphonic track mixer.
- `audio_pan_stereo(audio, pan)`: Stereo panning from -1.0 (left) to +1.0 (right).
- `audio_low_pass_filter(audio, cutoff_freq)`: Single-pole IIR low-pass filter.
- `audio_high_pass_filter(audio, cutoff_freq)`: Single-pole IIR high-pass filter.
- `audio_peak_amplitude(audio)`: Find maximum absolute sample value.
- `audio_rms_energy(audio)`: Root-Mean-Square energy calculation.
- `audio_zero_crossing_rate(audio)`: Measure rate of sign changes across audio waveform.
- `audio_clip_samples(audio, min_val, max_val)`: Hard clipping distortion filter.
- `audio_loop_track(audio, count)`: Repeat audio track N times.
- `audio_delay_echo(audio, delay_sec, decay)`: Add echo delay feedback loop.
- `audio_time_stretch_naive(audio, rate)`: Linear interpolation time stretcher.
- `audio_generate_silence(duration, sample_rate)`: Silent track generator.

### 10. DB (Relational & Analytical Database) - 20 Operations
- `db_create_index(conn, table, col, index_name)`: Create SQLite index on column.
- `db_drop_index(conn, index_name)`: Drop index.
- `db_add_column(conn, table, col_name, col_type)`: Alter table to append new column.
- `db_drop_column_sqlite(conn, table, col_name)`: Safely drop column from table.
- `db_vacuum(conn)`: Reclaim unused space and defragment database.
- `db_analyze(conn)`: Collect optimizer statistics on indices.
- `db_list_tables(conn)`: List all user tables in database.
- `db_list_views(conn)`: List all views in database.
- `db_list_indices(conn, table)`: List indices attached to table.
- `db_table_exists(conn, table)`: Check if table exists in database.
- `db_bulk_insert(conn, table, records, chunk_size)`: Chunked parameterized bulk insert.
- `db_export_table_to_csv(conn, table, csv_path)`: Stream table rows directly to CSV file.
- `db_import_csv_to_table(conn, csv_path, table)`: Import CSV directly into SQLite table.
- `db_get_foreign_keys(conn, table)`: PRAGMA foreign key list inspector.
- `db_check_foreign_key_integrity(conn)`: Verify referential integrity constraints.
- `db_export_ddl(conn, table)`: Export SQL `CREATE TABLE` DDL statement.
- `db_table_column_types(conn, table)`: Column name to declared type mapping.
- `db_database_size_bytes(conn)`: Total on-disk file size of SQLite database.
- `db_count_distinct_values(conn, table, col)`: Count unique values in column.
- `db_clone_table_schema(conn, src_table, new_table)`: Clone structure without rows.

### 11. Net (Network Services & Protocols) - 20 Operations
- `net_cidr_to_netmask(cidr)`: Convert `/24` into `255.255.255.0`.
- `net_ip_in_subnet(ip, cidr)`: Check if IP address falls inside CIDR block.
- `net_expand_cidr_range(cidr)`: Compute start IP, end IP, and total host capacity.
- `net_is_valid_ipv4(ip)`: Validate IPv4 octet format.
- `net_is_valid_ipv6(ip)`: Validate IPv6 address format.
- `net_format_mac_address(mac)`: Normalize MAC address into standard colon format.
- `net_whois_domain(domain)`: Query standard RDAP / WHOIS registry for domain.
- `net_http_status_message(code)`: Look up standard HTTP status code description.
- `net_build_query_string(params)`: Build URL encoded query string.
- `net_parse_url_components(url)`: Break URL into scheme, host, port, path, query.
- `net_exponential_backoff_delay(attempt, base_delay, max_delay)`: Compute backoff with jitter.
- `net_check_multiple_ports(host, ports, timeout)`: Concurrent multi-port scanner.
- `net_reverse_dns_lookup(ip)`: Resolve IP address to host PTR record.
- `net_generate_multipart_boundary()`: Generate random MIME multipart boundary.
- `net_encode_basic_auth_header(user, pw)`: Format Authorization: Basic string.
- `net_decode_basic_auth_header(header)`: Decode username and password from basic header.
- `net_parse_http_headers(raw_headers)`: Parse raw HTTP header lines into dictionary.
- `net_format_http_headers(headers_dict)`: Format dictionary into RFC HTTP header lines.
- `net_is_private_ip(ip)`: Check if IP is in RFC 1918 private address space.
- `net_download_file(url, target_path)`: Download file from URL to disk.

### 12. Sim (Stochastic Simulation & Probabilities) - 20 Operations
- `sim_markov_chain_step(current_state, transition_matrix, states)`: Next Markov state.
- `sim_markov_chain_walk(start_state, transition_matrix, states, steps)`: N-step Markov path.
- `sim_sample_geometric(p, count)`: Sample Geometric distribution variates.
- `sim_sample_binomial(n, p, count)`: Sample Binomial distribution variates.
- `sim_sample_triangular(low, high, mode, count)`: Sample Triangular distribution.
- `sim_bootstrap_mean_ci(data, n_bootstraps, confidence)`: Bootstrap confidence interval for mean.
- `sim_permutation_test(group1, group2, n_permutations)`: Two-sample permutation test p-value.
- `sim_mm1_queue(arrival_rate, service_rate, duration)`: M/M/1 queuing model simulation.
- `sim_wiener_process(t, n_steps, mu, sigma)`: Continuous Wiener (Brownian) process path.
- `sim_bernoulli_trial(p)`: Single boolean Bernoulli trial with probability p.
- `sim_sample_lognormal(mean, std, count)`: Sample Log-Normal distribution.
- `sim_monte_carlo_integral(fn, a, b, n_samples)`: Monte Carlo 1D numerical integration.
- `sim_estimate_expected_value(samples)`: Empirical expected value and variance.
- `sim_birthday_paradox_prob(people_count)`: Theoretical probability of shared birthday.
- `sim_coupon_collector_estimate(num_coupons, trials)`: Monte Carlo coupon collector trials.
- `sim_shuffle_deck()`: Fisher-Yates shuffle of 52 playing cards.
- `sim_draw_cards(deck, count)`: Draw cards from deck without replacement.
- `sim_sample_weibull(k, lam, count)`: Sample Weibull reliability distribution.
- `sim_generate_synthetic_timeline(start_time, intervals)`: Generate chronological timestamps.
- `sim_survival_rate_kaplan_meier(durations, events)`: Kaplan-Meier empirical survival curve.

### 13. Geo (Geospatial Analysis & GIS) - 19 Operations
- `geo_encode_geohash(lat, lon, precision)`: Convert coordinate to standard Geohash string.
- `geo_decode_geohash(geohash)`: Decode Geohash string to [lat, lon, error_lat, error_lon].
- `geo_cross_track_distance(pt, start_pt, end_pt)`: Distance of point from great circle path.
- `geo_destination_point(lat, lon, distance_km, bearing_deg)`: Coordinate given bearing and range.
- `geo_initial_bearing(p1, p2)`: Initial compass bearing from coordinate 1 to 2.
- `geo_final_bearing(p1, p2)`: Final compass bearing arriving at destination.
- `geo_midpoint(p1, p2)`: Spherical great-circle midpoint.
- `geo_bounding_box_intersection(box1, box2)`: Overlapping region of two bounding boxes.
- `geo_bounding_box_union(box1, box2)`: Enclosing union of two bounding boxes.
- `geo_convex_hull_graham(coords)`: 2D convex hull via Graham scan algorithm.
- `geo_point_to_line_distance(pt, line_start, line_end)`: Euclidean distance from point to segment.
- `geo_simplify_douglas_peucker(coords, epsilon)`: Douglas-Peucker polyline simplification.
- `geo_to_geojson_polygon(coords)`: Format coordinates into GeoJSON Polygon Feature.
- `geo_to_geojson_feature_collection(features)`: Combine features into FeatureCollection.
- `geo_polygon_perimeter(coords)`: Calculate perimeter distance of polygon.
- `geo_buffer_point_circle(center_pt, radius_km, num_points)`: Circular polygon perimeter points.
- `geo_degrees_to_meters(lat_deg, lon_deg)`: Approximation of degrees to meters.
- `geo_meters_to_degrees(meters)`: Approximation of meters to decimal degrees.
- `geo_is_clockwise(coords)`: Check if polygon coordinates are oriented clockwise.

### 14. Opt (Optimization & Combinatorics) - 19 Operations
- `opt_simulated_annealing(cost_fn, initial_state, neighbor_fn, temp, cooling_rate)`: Global heuristic search.
- `opt_golden_section_search(fn, a, b, tol)`: 1D unimodal function minimizer.
- `opt_knapsack_01_dp(weights, values, capacity)`: Exact 0/1 knapsack dynamic programming.
- `opt_longest_increasing_subsequence(arr)`: O(n log n) patient sorting LIS.
- `opt_coin_change_minimum(coins, amount)`: Fewest coins needed to make change.
- `opt_coin_change_combinations(coins, amount)`: Total distinct combinations to make change.
- `opt_job_scheduling_deadline(jobs)`: Maximum profit job scheduling with deadlines.
- `opt_huffman_encoding(char_frequencies)`: Generate optimal prefix Huffman codes.
- `opt_matrix_chain_multiplication(dimensions)`: Minimum scalar multiplications order.
- `opt_levenshtein_alignment(s1, s2)`: Full sequence alignment backtrace.
- `opt_subset_sum_exists(arr, target_sum)`: Check if subset sums to exact target.
- `opt_subset_sum_find(arr, target_sum)`: Extract subset elements summing to target.
- `opt_rod_cutting(prices, rod_length)`: Maximum revenue rod cutting dynamic programming.
- `opt_two_opt_tsp(coords, max_iterations)`: 2-opt Traveling Salesperson heuristic tour.
- `opt_linear_interpolation(x_points, y_points, target_x)`: 1D piecewise linear interpolator.
- `opt_weighted_interval_scheduling(intervals_with_weights)`: Dynamic programming weighted scheduling.
- `opt_pareto_frontier(points)`: Extract non-dominated Pareto optimal frontier points.
- `opt_hungarian_assignment(cost_matrix)`: Optimal bipartite assignment min-cost matching.
- `opt_binary_search_peak_1d(arr)`: Find any local peak element in O(log n).

### 15. Agent (Autonomous Agents & Teams) - 19 Operations
- `agent_evaluate_response_quality(response, rubric)`: Heuristic rubric-based scoring.
- `agent_format_chat_history(history, format_style)`: Reformat memory into Markdown, XML, or JSON.
- `agent_summarize_memory(agent, max_tokens)`: Condense agent memory window.
- `agent_route_task_by_keywords(task, agent_skill_map)`: Direct task routing via keyword weights.
- `agent_retry_with_backoff(agent, task, max_retries)`: Autonomous failure retry handler.
- `agent_validate_json_output(response, schema)`: Validate agent response against JSON schema.
- `agent_extract_action_calls(response)`: Parse tool/function call directives from response.
- `agent_chain_of_thought_step(task, context)`: Format zero-shot reasoning prompt.
- `agent_calculate_consensus_agreement(responses)`: Lexical agreement index among multiple agents.
- `agent_debate_round(agent1, agent2, topic, rounds)`: Multi-turn agent deliberation.
- `agent_plan_task_breakdown(agent, high_level_goal)`: Decompose goal into subtask checklist.
- `agent_filter_memory_by_date(agent, start_date, end_date)`: Temporal window memory query.
- `agent_merge_agent_memories(agent1, agent2, target_agent)`: Merge knowledge bases.
- `agent_register_dynamic_tool(agent, tool_name, tool_fn, desc)`: Attach callable tool.
- `agent_inspect_available_tools(agent)`: List tool signatures and schemas.
- `agent_set_system_persona(agent, new_role, new_instructions)`: Dynamically swap persona.
- `agent_audit_conversation_safety(history, banned_terms)`: Content moderation check.
- `agent_count_conversation_turns(agent)`: Count user/assistant turns in history.
- `agent_export_chat_transcript(agent, output_file)`: Write full session log to file.

### 16. Cloud (Storage, Metadata & Lifecycle) - 19 Operations
- `cloud_generate_presigned_put_url(bucket, key, expiry)`: Presigned URL for direct client upload.
- `cloud_verify_md5_checksum(bucket, key, expected_hash)`: Checksum integrity verification.
- `cloud_verify_sha256_checksum(bucket, key, expected_hash)`: SHA-256 integrity verification.
- `cloud_set_object_tags(bucket, key, tags_dict)`: Attach key-value metadata tags to object.
- `cloud_get_object_tags(bucket, key)`: Retrieve object tags.
- `cloud_batch_delete_keys(bucket, keys_list)`: Delete list of keys in single call.
- `cloud_filter_files_by_size(bucket, min_bytes, max_bytes)`: Filter objects by size threshold.
- `cloud_filter_files_by_date(bucket, after_date)`: Filter objects modified after timestamp.
- `cloud_create_directory_marker(bucket, dir_path)`: Create empty prefix marker.
- `cloud_move_object(bucket, src_key, dst_key)`: Copy and delete source key.
- `cloud_mirror_buckets(src_bucket, dst_bucket)`: One-way sync from source to destination.
- `cloud_archive_stale_files(bucket, days_old, archive_prefix)`: Move old files to archive.
- `cloud_export_bucket_manifest(bucket, manifest_file)`: Write CSV/JSON catalog of all objects.
- `cloud_diff_buckets(bucket1, bucket2)`: Find unique, missing, or mismatched objects.
- `cloud_count_objects_by_extension(bucket)`: Aggregate file counts grouped by file extension.
- `cloud_read_object_text(bucket, key)`: Read text contents of object into memory.
- `cloud_write_object_text(bucket, key, text_content)`: Write text directly into cloud object.
- `cloud_get_storage_class(bucket, key)`: Get simulated tier (Standard, Glacier, Coldline).
- `cloud_set_storage_class(bucket, key, storage_class)`: Update simulated storage tier.

### 17. Office (Spreadsheets, Words & Formatting) - 19 Operations
- `office_calculate_sheet_summary(spreadsheet, sheet_name, col)`: Quick sum, avg, min, max on col.
- `office_detect_csv_delimiter(csv_path)`: Detect `,`, `\t`, `;`, or `|` delimiter automatically.
- `office_read_csv_header(csv_path)`: Extract first header row from CSV without loading whole file.
- `office_create_table_in_document(doc, headers, rows)`: Add OpenXML table structure to Word doc.
- `office_add_bulleted_list(doc, items)`: Add bullet list to Word document.
- `office_add_numbered_list(doc, items)`: Add numbered list to Word document.
- `office_set_spreadsheet_cell(spreadsheet, sheet_name, row, col, val)`: Set value of specific cell.
- `office_get_spreadsheet_cell(spreadsheet, sheet_name, row, col)`: Get value of specific cell.
- `office_find_replace_in_document(doc, find_text, replace_text)`: Global find and replace across doc.
- `office_list_worksheet_names(spreadsheet)`: List all sheet tabs in workbook.
- `office_delete_worksheet(spreadsheet, sheet_name)`: Remove sheet tab from workbook.
- `office_rename_worksheet(spreadsheet, old_name, new_name)`: Rename sheet tab.
- `office_sort_spreadsheet_by_column(spreadsheet, sheet_name, col_idx, descending)`: Sort sheet rows.
- `office_filter_spreadsheet_rows(spreadsheet, sheet_name, col_idx, filter_fn)`: Filter sheet rows.
- `office_export_sheet_to_json(spreadsheet, sheet_name, json_path)`: Export sheet as JSON records.
- `office_import_json_to_sheet(spreadsheet, json_path, sheet_name)`: Load JSON records into sheet.
- `office_count_words_in_document(doc)`: Count total words in Word document.
- `office_count_characters_in_document(doc)`: Count total characters in Word document.
- `office_extract_document_metadata(doc_or_path)`: Extract title, author, and timestamp metadata.

### 18. Research (Scientific Reproducibility & Graph Algorithms) - 19 Operations
- `research_topological_sort(graph)`: Deterministic topological sort with insertion order tie-breaking.
- `research_dijkstra_shortest_path(graph, src, dst)`: Dijkstra with deterministic tie-breaking.
- `research_bellman_ford(graph, src)`: Shortest path with negative weight cycle detection.
- `research_floyd_warshall_all_pairs(graph)`: All-pairs shortest paths matrix.
- `research_edmonds_karp_max_flow(graph, src, sink)`: Maximum network flow via BFS augmenting paths.
- `research_hopcroft_karp_bipartite_matching(graph, u_nodes, v_nodes)`: Maximum cardinality bipartite matching in O(E √V).
- `research_tarjan_strongly_connected(graph)`: SCCs in directed graph.
- `research_kruskal_minimum_spanning_tree(graph)`: Minimum Spanning Tree with DSU.
- `research_prim_minimum_spanning_tree(graph)`: Prim's algorithm MST.
- `research_graph_diameter(graph)`: Maximum eccentricity of research graph.
- `research_graph_radius(graph)`: Minimum eccentricity of research graph.
- `research_connected_components(graph)`: Disjoint components in undirected research graph.
- `research_pagerank(graph, damping, max_iter)`: Deterministic PageRank with damping factor.
- `research_hits_algorithm(graph, max_iter)`: Hyperlink-Induced Topic Search (Hubs and Authorities).
- `research_eulerian_circuit_hierholzer(graph)`: Hierholzer's algorithm for Eulerian circuit.
- `research_graph_isomorphism_hash(graph)`: Canonical Weisfeiler-Lehman color refinement hash.
- `research_transitive_reduction(graph)`: Minimal graph with identical reachability.
- `research_find_negative_cycle(graph)`: Extract negative weight cycle vertices if present.
- `research_degree_distribution(graph)`: In-degree and out-degree histogram distribution.

---

## Testing Strategy
- Continuous implementation across domain modules and parser rules.
- 5 comprehensive verification test suites:
  - `tests/domains/test_350_ops_batch1_to_4.py`: DSA, Data, ML, Finance (79 operations)
  - `tests/domains/test_350_ops_batch5_to_8.py`: NLP, Graph, Image, Web (80 operations)
  - `tests/domains/test_350_ops_batch9_to_12.py`: Audio, DB, Net, Sim (79 operations)
  - `tests/domains/test_350_ops_batch13_to_15.py`: Geo, Opt, Agent (57 operations)
  - `tests/domains/test_350_ops_batch16_to_18.py`: Cloud, Office, Research (57 operations)
- Final full regression: `py -m pytest` across all 555+ existing tests plus all new tests, verifying 100% pass rate.
