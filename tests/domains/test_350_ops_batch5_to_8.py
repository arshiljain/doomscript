"""Comprehensive Test Suite for Group B of 350 Domain Operations.
Covers:
- Batch 5: NLP, Information Retrieval & Linguistics (20 operations)
- Batch 6: Complex Networks & Graph Theory (20 operations)
- Batch 7: Image & Computer Vision Manipulation (20 operations)
- Batch 8: Web Automation, Scraping & URLs (20 operations)
Total: 80 operations.
"""

import pytest
from doomscript.compiler.engine import execute


def test_batch5_nlp_metrics_and_similarity():
    """Batch 5: BM25, Levenshtein, Hamming, Porter stemmer, Soundex, Metaphone, ROUGE-L, BLEU, TF Cosine."""
    source = """use nlp

bm25 score for "cat sat on mat" with query "cat mat" into bm25_val
levenshtein distance between "kitten" and "sitting" into lev_dist
hamming distance between "karolin" and "kathrin" into ham_dist
porter stem of "running" into stem_val
soundex of "Robert" into soundex_val
metaphone of "Knight" into metaphone_val
rouge l score between "the quick brown fox" and "the brown fox jumps" into rouge_val
bleu score between candidate "the cat is on the mat" and reference "the cat sat on the mat" into bleu_val
tf cosine similarity between "apple banana" and "banana orange" into cos_sim
"""
    env = execute(source)
    assert env["bm25_val"][0]["score"] > 0
    assert env["lev_dist"] == 3
    assert env["ham_dist"] == 3
    assert env["stem_val"] == "run"
    assert env["soundex_val"].startswith("R")
    assert isinstance(env["metaphone_val"], str)
    assert env["rouge_val"]["f1"] > 0.5
    assert env["bleu_val"] > 0.0
    assert 0.0 < env["cos_sim"] < 1.0


def test_batch5_nlp_text_processing():
    """Batch 5: Contractions, Masking, Readability, Syllables, Sentences, POS tag, VADER heuristic, Wrap."""
    source = """use nlp

expand contractions in "don't won't shouldn't" into expanded_text
mask sensitive entities in "Call me at test@example.com or 555-123-4567" into masked_text
flesch reading ease of "This is a simple sentence. It is very easy to read." into flesch_score
gunning fog index of "The sophisticated methodology yielded advantageous paradigms." into fog_score
count syllables in "unbelievable" into syl_count
split into sentences "Hello world! How are you doing? I am well." into sents
pos tag "The quick dog runs quickly" into pos_tags
vader sentiment of "This is wonderful and truly magnificent!" into vader_res
character ngrams from "doom" with n 2 into char_ngrams
collocations in "data science machine learning data science" with min frequency 2 into coll_res
word wrap "The quick brown fox jumps over the lazy dog" with width 15 into wrapped_text
"""
    env = execute(source)
    assert "do not" in env["expanded_text"]
    assert "[EMAIL]" in env["masked_text"]
    assert "[PHONE]" in env["masked_text"]
    assert env["flesch_score"] > 60
    assert env["fog_score"] > 0
    assert env["syl_count"] in (4, 5)
    assert len(env["sents"]) == 3
    assert len(env["pos_tags"]) >= 4
    assert env["vader_res"]["compound"] > 0
    assert "do" in env["char_ngrams"] and "oo" in env["char_ngrams"]
    assert ("data", "science") in env["coll_res"]
    assert "\n" in env["wrapped_text"]


def test_batch6_graph_algorithms_and_paths():
    """Batch 6: Graph Dijkstra, Bellman-Ford, Floyd-Warshall, Kruskal, Prim, Eigenvector."""
    source = """use graph

create directed graph into g_dir
add node 0 to g_dir
add node 1 to g_dir
add node 2 to g_dir
connect 0 to 1 with weight 4.0 in g_dir
connect 1 to 2 with weight 3.0 in g_dir
connect 0 to 2 with weight 10.0 in g_dir

dijkstra shortest path in g_dir from 0 to 2 into dijk_res
bellman ford in g_dir from 0 into bf_res
floyd warshall in g_dir into fw_res

create undirected graph into g_undir
add node 0 to g_undir
add node 1 to g_undir
add node 2 to g_undir
add node 3 to g_undir
connect 0 to 1 with weight 1.0 in g_undir
connect 1 to 2 with weight 2.0 in g_undir
connect 2 to 3 with weight 3.0 in g_undir
connect 3 to 0 with weight 4.0 in g_undir

kruskal mst of g_undir into k_mst
prim mst of g_undir starting at 0 into p_mst
eigenvector centrality of g_undir into ev_cent
"""
    env = execute(source)
    assert env["dijk_res"]["path"] == ["0", "1", "2"]
    assert env["dijk_res"]["distance"] == 7.0
    assert env["bf_res"]["distances"]["2"] == 7.0
    assert env["fw_res"]["0"]["2"] == 7.0
    assert env["k_mst"]["total_weight"] == 6.0
    assert env["p_mst"]["total_weight"] == 6.0
    assert len(env["ev_cent"]) == 4


def test_batch6_graph_properties_and_metrics():
    """Batch 6: Max flow, Articulation points, Bridges, Radius, Center, Clustering, Transitivity, Density, Jaccard."""
    source = """use graph

create directed graph into net
add node "s" to net
add node "u" to net
add node "v" to net
add node "t" to net
connect "s" to "u" with weight 10.0 in net
connect "s" to "v" with weight 5.0 in net
connect "u" to "v" with weight 15.0 in net
connect "u" to "t" with weight 10.0 in net
connect "v" to "t" with weight 10.0 in net

max flow in net from "s" to "t" into mf_val

create undirected graph into star
add node "c" to star
add node "a" to star
add node "b" to star
add node "d" to star
connect "c" to "a" with weight 1.0 in star
connect "c" to "b" with weight 1.0 in star
connect "c" to "d" with weight 1.0 in star

find articulation points of star into cut_vertices
find bridges in star into bridge_edges
radius of star into rad_val
center of star into ctr_nodes
density of star into dens_val
degree histogram of star into deg_hist
jaccard similarity between nodes "a" and "b" in star into jacc_ab
check if star is tree into is_tree_res
transitive closure of star into tc_res
k core of star with k 1 into k_core_res
laplacian matrix of star into lap_mat
"""
    env = execute(source)
    assert env["mf_val"] == 15.0
    assert env["cut_vertices"] == ["c"]
    assert len(env["bridge_edges"]) == 3
    assert env["rad_val"] == 1
    assert env["ctr_nodes"] == ["c"]
    assert env["dens_val"] == 0.5  # 3 edges out of 4*3/2 = 6 possible -> 0.5
    assert len(env["deg_hist"]) > 0
    assert env["jacc_ab"] == 1.0  # both only connect to c
    assert env["is_tree_res"] is True
    assert "c" in env["tc_res"]["a"]
    assert len(env["k_core_res"]) == 4
    assert len(env["lap_mat"]) == 4


def test_batch7_image_processing():
    """Batch 7: Creation, Sobel edge, Binarize, Sharpen, Invert, Contrast, Sepia, Vignette, Pad, Center crop, Posterize."""
    source = """use image

create blank image with width 30 and height 30 and color "red" into img1
create blank image with width 30 and height 30 and color "blue" into img2

sobel edge detection on img1 into edge_img
binarize img1 with threshold 100 into bin_img
sharpen img1 into sharp_img
invert colors of img1 into inv_img
adjust contrast of img1 by factor 1.5 into cont_img
split channels of img1 into chs
apply sepia to img1 into sepia_img
flip img1 horizontally into fh_img
flip img1 vertically into fv_img
apply vignette to img1 with radius 0.9 into vig_img
pad borders of img1 with 5 and color "black" into pad_img
mean color of img1 into mean_rgb
center crop img1 to width 20 and height 20 into cc_img
apply gamma correction to img1 with gamma 1.5 into gam_img
apply emboss to img1 into emb_img
posterize img1 with 4 levels into post_img
pixelate img1 with block size 5 into pix_img
blend img1 and img2 with alpha 0.5 into blend_img
difference between img1 and img2 into diff_img
"""
    env = execute(source)
    assert env["edge_img"] is not None
    assert env["bin_img"] is not None
    assert env["sharp_img"] is not None
    assert env["inv_img"] is not None
    assert env["cont_img"] is not None
    assert "r" in env["chs"]
    assert env["sepia_img"] is not None
    assert env["fh_img"] is not None
    assert env["fv_img"] is not None
    assert env["vig_img"] is not None
    assert env["pad_img"].width == 40
    assert env["mean_rgb"][0] > 200  # red channel is high
    assert env["cc_img"].width == 20
    assert env["gam_img"] is not None
    assert env["emb_img"] is not None
    assert env["post_img"] is not None
    assert env["pix_img"] is not None
    assert env["blend_img"] is not None
    assert env["diff_img"] is not None


def test_batch8_web_scraping_and_urls():
    """Batch 8: Images, Forms, Form data, Sitemap, Robots, Canonicalize, Meta, Headings, Cookie, JSON-LD, Tags, cURL."""
    source = """use web

set sample_html to '<html><head><title>Test</title><meta name="description" content="A great page"/></head><body><h1>Main Title</h1><h2>Subtitle</h2><div id="content" class="article text"><p>Some text</p></div><form action="/login" method="post"><input name="user" type="text" value="alice"/><input name="pass" type="password"/></form><img src="/logo.png" alt="Logo"/><script type="application/ld+json">{"@context": "https://schema.org", "@type": "WebPage", "name": "TestPage"}</script></body></html>'

extract images from sample_html into imgs
extract forms from sample_html into forms
extract meta description from sample_html into mdesc
extract headings from sample_html into hds
extract json ld from sample_html into jld
extract text with class "article" from sample_html into art_text
extract element with id "content" from sample_html into content_text
count tag "h2" in sample_html into h2_count

encode form data {"query": "doomscript", "limit": 10} into query_encoded
decode form data query_encoded into query_decoded
parse sitemap xml '<urlset><loc>https://example.com/page1</loc><loc>https://example.com/page2</loc></urlset>' into sitemap_urls
check robots txt "User-agent: *\\nDisallow: /admin/" for user agent "bot" and path "/admin/panel" into disallowed_res
check robots txt "User-agent: *\\nDisallow: /admin/" for user agent "bot" and path "/public" into allowed_res
canonicalize url "https://example.com/blog/" with "post-1.html" into canon_url
strip query params from "https://example.com/search?q=doom#section" into stripped_url
parse cookie header "session=xyz123; Path=/; Secure" into cookies_parsed
build cookie header from {"session": "abc456", "theme": "dark"} into cookie_hdr_str
parse content type header "text/html; charset=UTF-8" into ctype
check if url "https://example.com" is valid into url_valid
check if url "not-a-valid-url" is valid into url_invalid
generate curl command for "GET" to "https://api.example.com/data" into curl_cmd
"""
    env = execute(source)
    assert len(env["imgs"]) == 1
    assert env["imgs"][0]["src"] == "/logo.png"
    assert len(env["forms"]) == 1
    assert env["forms"][0]["method"] == "POST"
    assert env["mdesc"] == "A great page"
    assert len(env["hds"]) == 2
    assert env["hds"][0]["text"] == "Main Title"
    assert len(env["jld"]) == 1
    assert env["jld"][0]["name"] == "TestPage"
    assert "Some text" in env["art_text"][0]
    assert "Some text" in env["content_text"]
    assert env["h2_count"] == 1

    assert "query=doomscript" in env["query_encoded"]
    assert env["query_decoded"]["query"] == "doomscript"
    assert len(env["sitemap_urls"]) == 2
    assert env["disallowed_res"] is False
    assert env["allowed_res"] is True
    assert env["canon_url"] == "https://example.com/blog/post-1.html"
    assert env["stripped_url"] == "https://example.com/search"
    assert env["cookies_parsed"]["session"] == "xyz123"
    assert "session=abc456" in env["cookie_hdr_str"]
    assert env["ctype"]["mime_type"] == "text/html"
    assert env["ctype"]["charset"].upper() == "UTF-8"
    assert env["url_valid"] is True
    assert env["url_invalid"] is False
    assert 'curl -X GET "https://api.example.com/data"' in env["curl_cmd"]
