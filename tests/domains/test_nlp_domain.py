"""Unit and integration tests for the NLP & Text Analytics domain pack (use nlp)."""

import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.nlp.runtime import (
    clean_text,
    tokenize_text,
    extract_ngrams,
    analyze_sentiment,
    calculate_tfidf,
    extract_entities,
)


def test_nlp_runtime_clean_and_tokenize():
    raw = "   Hello, WORLD!! This is a TEST with 123 numbers...   "
    cleaned = clean_text(raw)
    assert cleaned == "hello world this is a test with 123 numbers"

    cleaned_no_stops = clean_text(raw, remove_stopwords=True)
    assert "is" not in cleaned_no_stops.split()
    assert "a" not in cleaned_no_stops.split()
    assert "with" not in cleaned_no_stops.split()
    assert "world" in cleaned_no_stops.split()
    assert "test" in cleaned_no_stops.split()

    tokens = tokenize_text("DoomScript makes domain programming fast and readable.")
    assert len(tokens) == 7
    assert tokens[0] == "DoomScript"
    assert tokens[-1] == "readable"

    sentences = tokenize_text("First sentence! Second sentence? Third sentence.", mode="sentence")
    assert len(sentences) == 3


def test_nlp_runtime_ngrams():
    text = "the quick brown fox jumps"
    bigrams = extract_ngrams(text, n=2)
    assert bigrams == [
        "the quick",
        "quick brown",
        "brown fox",
        "fox jumps",
    ]

    trigrams = extract_ngrams(text, n=3)
    assert trigrams == [
        "the quick brown",
        "quick brown fox",
        "brown fox jumps",
    ]


def test_nlp_runtime_sentiment():
    pos = analyze_sentiment("This programming language is fantastic, elegant, and awesome!")
    assert pos["label"] == "positive"
    assert pos["polarity"] > 0
    assert pos["positive_count"] >= 3

    neg = analyze_sentiment("This execution failed with horrible and terrible errors.")
    assert neg["label"] == "negative"
    assert neg["polarity"] < 0
    assert neg["negative_count"] >= 3

    negated = analyze_sentiment("The tool is not good.")
    assert negated["label"] == "negative"
    assert negated["polarity"] < 0


def test_nlp_runtime_tfidf():
    docs = [
        "machine learning algorithms analyze data",
        "deep learning and algorithms for vision",
        "data science and machine learning pipelines",
    ]
    model = calculate_tfidf(docs)
    assert "vocabulary" in model
    assert "matrix" in model
    assert len(model["matrix"]) == 3
    assert "learning" in model["vocabulary"]
    assert "machine" in model["vocabulary"]


def test_nlp_runtime_entities():
    text = "Reach out to Alice at alice@example.com or visit https://doomscript.org on 2026-10-19."
    entities = extract_entities(text)
    labels = {e["label"]: e["entity"] for e in entities}
    assert "EMAIL" in labels
    assert labels["EMAIL"] == "alice@example.com"
    assert "URL" in labels
    assert labels["URL"] == "https://doomscript.org"
    assert "DATE" in labels
    assert labels["DATE"] == "2026-10-19"


def test_nlp_domain_execution():
    source = """use nlp

raw_doc = "Antigravity and DoomScript are amazing technologies!"
clean text in raw_doc into clean_doc
tokenize clean_doc into words
extract 2-grams from clean_doc into word_bigrams
analyze sentiment of raw_doc into sent
extract entities from "Contact support@doom.io today" into found_entities
"""
    env = execute(source)
    assert env["clean_doc"] == "antigravity and doomscript are amazing technologies"
    assert len(env["words"]) == 6
    assert len(env["word_bigrams"]) == 5
    assert env["sent"]["label"] == "positive"
    assert any(e["label"] == "EMAIL" for e in env["found_entities"])


def test_nlp_domain_tfidf_execution():
    source = """use nlp

corpus = ["apple banana cherry", "banana cherry date", "cherry date elderberry"]
calculate tfidf of corpus with max_features 10 into tfidf_res
"""
    env = execute(source)
    assert "tfidf_res" in env
    res = env["tfidf_res"]
    assert "vocabulary" in res
    assert len(res["matrix"]) == 3


def test_nlp_domain_ast_export():
    source = """use nlp

corpus = ["hello world", "world of code"]
calculate tfidf of corpus into tfidf_out
"""
    py_code = export_to_python(source)
    assert "calculate_tfidf" in py_code or "TfidfVectorizer" in py_code
