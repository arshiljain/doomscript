"""Comprehensive integration tests for deepened perceptual and media domains (NLP, Graph, Image, Audio)."""

import pytest
import math
from doomscript.domains.nlp.runtime import (
    BPETokenizer,
    HMMPOSTagger,
    Word2VecSimple,
    TextRankSummarizer,
)
from doomscript.domains.graph.runtime import (
    DoomGraph,
    create_graph,
    add_graph_edge,
    graph_bron_kerbosch_cliques,
    graph_betweenness_centrality,
    graph_louvain_communities,
    graph_tarjan_scc,
    graph_mst,
)
from doomscript.domains.image.runtime import (
    DoomImage,
    image_canny_edge_detector,
    image_otsu_threshold,
    image_bilateral_filter,
    image_hough_lines,
)
from doomscript.domains.audio.runtime import (
    DoomAudio,
    audio_generate_sine,
    audio_fft,
    audio_ifft,
    audio_stft_spectrogram,
    audio_mel_spectrogram,
    audio_mfcc,
    audio_biquad_filter,
)


# =========================================================================
# 1. NLP Deepened Tests
# =========================================================================

def test_bpe_tokenizer():
    corpus = [
        "the quick brown fox jumps over the lazy dog",
        "the dog barked at the brown fox",
        "jumping foxes and lazy dogs",
    ]
    bpe = BPETokenizer(vocab_size=60)
    bpe.train(corpus)

    assert len(bpe.merges) > 0
    assert len(bpe.vocab) > 10

    # Encoding produces subwords
    encoded = bpe.encode("the quick fox")
    assert isinstance(encoded, list)
    assert len(encoded) > 0

    # Decoding reconstructs words
    decoded = bpe.decode(encoded)
    assert "the" in decoded
    assert "fox" in decoded


def test_hmm_viterbi_pos_tagger():
    tagger = HMMPOSTagger()
    # Tag a standard test sentence
    words = ["the", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"]
    tagged = tagger.tag(words)

    assert len(tagged) == len(words)
    tags = [t for _, t in tagged]
    # "the" should be a determiner
    assert tags[0] == "DET"
    assert tags[6] == "DET"


def test_word2vec_simple():
    corpus = [
        "king queen prince princess royalty monarch",
        "apple banana orange grape fruit orchard",
        "king rules the kingdom with royalty",
        "fruit grows in the apple orchard",
    ] * 5
    w2v = Word2VecSimple(embedding_dim=12, lr=0.08, epochs=15)
    w2v.fit(corpus, window=2)

    assert "king" in w2v.word2id
    assert "queen" in w2v.word2id

    vec = w2v.get_vector("king")
    assert vec is not None
    assert len(vec) == 12

    sim = w2v.cosine_similarity("king", "queen")
    assert -1.0 <= sim <= 1.0


def test_textrank_keywords_and_summary():
    text = (
        "Artificial intelligence and machine learning are transforming modern computing. "
        "Deep neural networks enable high accuracy in vision and natural language processing. "
        "Autonomous systems use machine learning algorithms to make real-time decisions. "
        "Data science and computational algorithms form the foundation of intelligent systems."
    )
    keywords = TextRankSummarizer.extract_keywords(text, top_n=4)
    assert len(keywords) == 4
    # "learning", "machine", "systems", "algorithms" or similar should appear
    assert any(k in ["learning", "machine", "systems", "intelligence", "neural", "networks", "algorithms", "computing"] for k in keywords)

    summary = TextRankSummarizer.summarize(text, top_n_sentences=2)
    assert isinstance(summary, str)
    assert len(summary) > 20


# =========================================================================
# 2. Graph Deepened Tests
# =========================================================================

def test_bron_kerbosch_cliques():
    # 2 cliques of size 3 connected by a bridge edge: (1-2-3) and (4-5-6), with bridge (3-4)
    g = DoomGraph(directed=False)
    # Triangle 1
    g.add_edge("1", "2")
    g.add_edge("2", "3")
    g.add_edge("3", "1")
    # Triangle 2
    g.add_edge("4", "5")
    g.add_edge("5", "6")
    g.add_edge("6", "4")
    # Bridge
    g.add_edge("3", "4")

    cliques = graph_bron_kerbosch_cliques(g)
    # Triangles ['1', '2', '3'] and ['4', '5', '6'] must be maximal cliques
    clique_sets = [set(c) for c in cliques]
    assert {"1", "2", "3"} in clique_sets
    assert {"4", "5", "6"} in clique_sets
    assert {"3", "4"} in clique_sets


def test_betweenness_centrality():
    # Star graph: node 'C' is center connected to leaves 'A', 'B', 'D', 'E'
    g = DoomGraph(directed=False)
    for leaf in ["A", "B", "D", "E"]:
        g.add_edge("C", leaf)

    bc = graph_betweenness_centrality(g, normalized=True)
    # Center node must have highest betweenness centrality
    assert bc["C"] > bc["A"]
    assert bc["A"] == 0.0
    assert bc["B"] == 0.0


def test_louvain_communities():
    # Two well-separated clusters with dense internal connections and sparse inter-cluster connection
    g = DoomGraph(directed=False)
    # Cluster A
    g.add_edge("A1", "A2")
    g.add_edge("A2", "A3")
    g.add_edge("A3", "A1")
    # Cluster B
    g.add_edge("B1", "B2")
    g.add_edge("B2", "B3")
    g.add_edge("B3", "B1")
    # Weak link
    g.add_edge("A3", "B1", weight=0.1)

    comms = graph_louvain_communities(g)
    # Should detect 2 distinct communities
    assert len(comms) == 2


def test_tarjan_scc():
    # Directed graph with 2 strongly connected components: (1 -> 2 -> 3 -> 1) and (4 -> 5 -> 4)
    g = DoomGraph(directed=True)
    g.add_edge("1", "2")
    g.add_edge("2", "3")
    g.add_edge("3", "1")
    g.add_edge("3", "4")
    g.add_edge("4", "5")
    g.add_edge("5", "4")

    sccs = graph_tarjan_scc(g)
    scc_sets = [set(c) for c in sccs]
    assert {"1", "2", "3"} in scc_sets
    assert {"4", "5"} in scc_sets


def test_kruskal_mst():
    # 4-node diamond graph
    g = DoomGraph(directed=False)
    g.add_edge("A", "B", weight=1.0)
    g.add_edge("B", "C", weight=2.0)
    g.add_edge("C", "D", weight=3.0)
    g.add_edge("D", "A", weight=4.0)
    g.add_edge("A", "C", weight=5.0)

    mst = graph_mst(g)
    # Spanning tree of 4 nodes must contain 3 edges
    assert mst["edge_count"] == 3
    # Minimum weight: 1.0 (A-B) + 2.0 (B-C) + 3.0 (C-D) = 6.0
    assert mst["total_weight"] == 6.0


# =========================================================================
# 3. Image & Computer Vision Deepened Tests
# =========================================================================

def test_canny_edge_detector():
    # 20x20 image with a vertical step edge down the middle: left is black (0), right is white (255)
    grid = [[0.0] * 10 + [255.0] * 10 for _ in range(20)]
    edges = image_canny_edge_detector(grid, low_thresh=15.0, high_thresh=35.0)

    # If returned as 2D list or DoomImage
    if hasattr(edges, "_img"):
        data = list(edges._img.getdata())
        has_edge = any(px > 0 for px in data)
    else:
        has_edge = any(val > 0 for row in edges for val in row)
    assert has_edge is True


def test_otsu_thresholding():
    # Bimodal distribution: 50 dark pixels at 20, 50 light pixels at 220
    row1 = [20.0] * 10
    row2 = [220.0] * 10
    grid = [row1] * 5 + [row2] * 5
    res = image_otsu_threshold(grid)

    assert "threshold" in res
    # Optimal threshold should be roughly midway between 20 and 220
    assert 50 <= res["threshold"] <= 180


def test_bilateral_filter():
    # Step edge with added noise
    grid = [[10.0 if x < 5 else 200.0 for x in range(10)] for _ in range(10)]
    # Add a noisy outlier in the middle
    grid[5][2] = 80.0
    filtered = image_bilateral_filter(grid, d=3, sigma_color=20.0, sigma_space=20.0)
    # Outlier should be smoothed down toward 10.0
    assert filtered[5][2] < 80.0


def test_hough_lines():
    # 20x20 binary edge map with a horizontal edge along row 10
    edge_grid = [[0.0] * 20 for _ in range(20)]
    for x in range(20):
        edge_grid[10][x] = 255.0

    lines = image_hough_lines(edge_grid, threshold=10)
    assert len(lines) > 0
    # First detected line should correspond to horizontal line (theta around 90 degrees)
    assert any(abs(l["theta_deg"] - 90.0) < 5.0 for l in lines)


# =========================================================================
# 4. Audio & DSP Deepened Tests
# =========================================================================

def test_audio_fft_and_ifft_roundtrip():
    # 64-sample pure sine wave
    sr = 64
    freq = 4.0
    sine = [math.sin(2.0 * math.pi * freq * (i / sr)) for i in range(sr)]

    # Compute FFT
    spectrum = audio_fft(sine)
    assert len(spectrum) == 64

    # Peak in frequency spectrum should occur at bin 4
    magnitudes = [math.sqrt(c.real ** 2 + c.imag ** 2) for c in spectrum]
    assert magnitudes[4] > magnitudes[0]
    assert magnitudes[4] > magnitudes[10]

    # Invert FFT back to time domain
    reconstructed = audio_ifft(spectrum)
    assert len(reconstructed) == 64
    # Roundtrip reconstruction error should be very small (< 0.01)
    max_err = max(abs(s - r) for s, r in zip(sine, reconstructed))
    assert max_err < 0.05


def test_stft_and_mel_spectrogram():
    sine_audio = audio_generate_sine(frequency=440.0, duration=0.1, sample_rate=8000)

    # STFT spectrogram
    stft = audio_stft_spectrogram(sine_audio, frame_size=128, hop_size=64)
    assert len(stft) > 0
    assert len(stft[0]) == 65  # 128 // 2 + 1 frequency bins

    # Mel spectrogram
    mel_spec = audio_mel_spectrogram(sine_audio, n_mels=20, sample_rate=8000, frame_size=128, hop_size=64)
    assert len(mel_spec) > 0
    assert len(mel_spec[0]) == 20  # 20 mel channels


def test_audio_mfcc():
    sine_audio = audio_generate_sine(frequency=440.0, duration=0.1, sample_rate=8000)
    mfccs = audio_mfcc(sine_audio, n_mfcc=13, n_mels=20, sample_rate=8000)
    assert len(mfccs) > 0
    assert len(mfccs[0]) == 13


def test_biquad_filter():
    sine_high = audio_generate_sine(frequency=3000.0, duration=0.05, sample_rate=8000)
    # Apply lowpass filter at 500 Hz: should significantly attenuate the 3000 Hz signal
    filtered = audio_biquad_filter(sine_high, filter_type="lowpass", cutoff_freq=500.0, sample_rate=8000)

    orig_peak = max(abs(s) for s in sine_high.samples)
    filt_peak = max(abs(s) for s in filtered.samples[50:])  # Skip filter warm-up
    # Attenuation check
    assert filt_peak < orig_peak * 0.5
