"""Independent Domain Parser for NLP & Text Analytics domain."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.nlp.spec import (
    NLPCleanSpec,
    NLPTokenizeSpec,
    NLPNgramSpec,
    NLPSentimentSpec,
    NLPTfidfSpec,
    NLPEntitiesSpec,
)


class NLPDomainParser(DomainParser):
    """Independent parser for NLP and Text Analytics syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        # [analyze] sentiment of <expr> [into <target>]
        m_sent = re.match(
            r"^(?:analyze\s+)?sentiment\s+of\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_sent:
            expr = m_sent.group(1).strip()
            target = m_sent.group(2) or "sentiment_result"
            return f"set {target} to analyze_sentiment({expr})"

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()
        # train bpe tokenizer on <texts> [with vocab size <size>] into <target>
        m_bpe = re.match(
            r"^train\s+bpe\s+tokenizer\s+on\s+(.+?)(?:\s+with\s+vocab\s+size\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bpe:
            texts = m_bpe.group(1).strip()
            sz = m_bpe.group(2).strip() if m_bpe.group(2) else "100"
            target = m_bpe.group(3).strip()
            return f"set {target} to nlp_bpe_train({texts}, vocab_size={sz})"



        # words in <expr> into <target>
        m_words = re.match(
            r"^words\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_words:
            expr = m_words.group(1).strip()
            target = m_words.group(2).strip()
            return f'set {target} to tokenize_text({expr}, mode="word")'

        # sentences in <expr> into <target>
        m_sents = re.match(
            r"^sentences\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sents:
            expr = m_sents.group(1).strip()
            target = m_sents.group(2).strip()
            return f'set {target} to tokenize_text({expr}, mode="sentence")'

        # bigrams / trigrams of <expr> into <target>
        m_bi_tri = re.match(
            r"^(?:extract\s+)?(bigrams|trigrams)\s+(?:of|from)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bi_tri:
            kind = m_bi_tri.group(1).lower()
            deg = 2 if "bi" in kind else 3
            expr = m_bi_tri.group(2).strip()
            target = m_bi_tri.group(3).strip()
            return f"set {target} to extract_ngrams({expr}, n={deg})"

        # clean text [in] <expr> [removing stopwords] into <target>
        # or clean <expr> [removing stopwords] into <target>
        m_clean = re.match(
            r"^clean(?:\s+text)?(?:\s+in)?\s+(.+?)(?:\s+removing\s+stopwords)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_clean:
            expr = m_clean.group(1).strip()
            target = m_clean.group(2).strip()
            rem_stops = "removing stopwords" in s.lower()
            return f"set {target} to clean_text({expr}, remove_stopwords={rem_stops})"

        # tokenize [text] <expr> [by (words|sentences)] into <target>
        m_tok = re.match(
            r"^tokenize(?:\s+text)?\s+(.+?)(?:\s+by\s+(words|sentences))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tok:
            expr = m_tok.group(1).strip()
            mode = "sentence" if m_tok.group(2) and m_tok.group(2).lower() == "sentences" else "word"
            target = m_tok.group(3).strip()
            return f'set {target} to tokenize_text({expr}, mode="{mode}")'

        # extract <n>-grams from <expr> into <target>
        m_ng = re.match(
            r"^extract\s+(\d+)-?grams\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ng:
            n_deg = int(m_ng.group(1))
            expr = m_ng.group(2).strip()
            target = m_ng.group(3).strip()
            return f"set {target} to extract_ngrams({expr}, n={n_deg})"

        # tfidf of / calculate tfidf of <corpus> [with max_features <n>] into <target>
        m_tfidf = re.match(
            r"^(?:calculate\s+)?tfidf\s+of\s+(.+?)(?:\s+with\s+max_features\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tfidf:
            corpus = m_tfidf.group(1).strip()
            max_f = m_tfidf.group(2)
            target = m_tfidf.group(3).strip()
            if max_f:
                return f"set {target} to calculate_tfidf({corpus}, max_features={max_f})"
            return f"set {target} to calculate_tfidf({corpus})"

        # entities in / extract entities from <expr> into <target>
        m_ent = re.match(
            r"^(?:extract\s+entities\s+from|entities\s+in)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ent:
            expr = m_ent.group(1).strip()
            target = m_ent.group(2).strip()
            return f"set {target} to extract_entities({expr})"

        # extractive summary of <text> with <n> sentences into <target>
        m_sum = re.match(
            r"^extractive\s+summary\s+of\s+(.+?)\s+with\s+(.+?)\s+sentences?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sum:
            text, n, target = m_sum.group(1), m_sum.group(2), m_sum.group(3)
            return f"set {target} to nlp_extractive_summary({text}, num_sentences={n})"

        # remove stopwords from <text> into <target>
        m_stop = re.match(
            r"^remove\s+stopwords\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_stop:
            text, target = m_stop.group(1), m_stop.group(2)
            return f"set {target} to nlp_remove_stopwords({text})"

        # word frequencies of <text> into <target>
        m_wfreq = re.match(
            r"^word\s+frequencies\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_wfreq:
            text, target = m_wfreq.group(1), m_wfreq.group(2)
            return f"set {target} to nlp_word_frequencies({text})"

        # text similarity between <s1> and <s2> into <target>
        m_sim = re.match(
            r"^text\s+similarity\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sim:
            s1, s2, target = m_sim.group(1), m_sim.group(2), m_sim.group(3)
            return f"set {target} to nlp_text_similarity({s1}, {s2})"

        # jaccard similarity of <s1> and <s2> into <target>
        m_jacc = re.match(
            r"^jaccard\s+similarity\s+of\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_jacc:
            s1, s2, target = m_jacc.group(1), m_jacc.group(2), m_jacc.group(3)
            return f"set {target} to nlp_jaccard_similarity({s1}, {s2})"

        # extract top <k> keywords from <text> into <target>
        m_kw = re.match(
            r"^extract\s+top\s+(.+?)\s+keywords\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_kw:
            k, text, target = m_kw.group(1), m_kw.group(2), m_kw.group(3)
            return f"set {target} to nlp_extract_keywords({text}, {k})"

        # extract all matches of pattern <pat> in <text> into <target>
        m_match = re.match(
            r"^extract\s+all\s+matches\s+of\s+pattern\s+(.+?)\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_match:
            pat, text, target = m_match.group(1), m_match.group(2), m_match.group(3)
            return f"set {target} to nlp_extract_matches({text}, {pat})"

        # 350-Expansion NLP Operations
        bm25_m = re.match(
            r"^(?:rank\s+corpus\s+(.+?)\s+for\s+query\s+(.+?)\s+using\s+bm25|bm25\s+score\s+for\s+(.+?)\s+with\s+query\s+(.+?))\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if bm25_m:
            if bm25_m.group(1) is not None:
                corpus, q, target = bm25_m.group(1).strip(), bm25_m.group(2).strip(), bm25_m.group(5).strip()
            else:
                corpus, q, target = bm25_m.group(3).strip(), bm25_m.group(4).strip(), bm25_m.group(5).strip()
            return f"set {target} to nlp_bm25_score({corpus}, {q})"

        lev_m = re.match(
            r"^levenshtein\s+distance\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if lev_m:
            s1, s2, target = lev_m.group(1).strip(), lev_m.group(2).strip(), lev_m.group(3).strip()
            return f"set {target} to nlp_levenshtein_distance({s1}, {s2})"

        hamm_m = re.match(
            r"^hamming\s+distance\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if hamm_m:
            s1, s2, target = hamm_m.group(1).strip(), hamm_m.group(2).strip(), hamm_m.group(3).strip()
            return f"set {target} to nlp_hamming_distance({s1}, {s2})"

        stem_m = re.match(
            r"^porter\s+stem\s+of\s+(?:word\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if stem_m:
            w, target = stem_m.group(1).strip(), stem_m.group(2).strip()
            return f"set {target} to nlp_stem_porter({w})"

        sound_m = re.match(
            r"^soundex\s+(?:phonetic\s+code\s+of\s+)?(?:of\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if sound_m:
            w, target = sound_m.group(1).strip(), sound_m.group(2).strip()
            return f"set {target} to nlp_soundex({w})"

        meta_m = re.match(
            r"^metaphone\s+(?:phonetic\s+key\s+of\s+)?(?:of\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if meta_m:
            w, target = meta_m.group(1).strip(), meta_m.group(2).strip()
            return f"set {target} to nlp_metaphone({w})"

        rouge_m = re.match(
            r"^rouge[- ]?l\s+score\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if rouge_m:
            c, r, target = rouge_m.group(1).strip(), rouge_m.group(2).strip(), rouge_m.group(3).strip()
            return f"set {target} to nlp_rouge_l({c}, {r})"

        bleu_m = re.match(
            r"^bleu\s+score\s+between\s+(?:candidate\s+)?(.+?)\s+and\s+(?:reference\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if bleu_m:
            c, r, target = bleu_m.group(1).strip(), bleu_m.group(2).strip(), bleu_m.group(3).strip()
            return f"set {target} to nlp_bleu_score({c}, {r})"

        cos_tf_m = re.match(
            r"^(?:term\s+frequency\s+cosine\s+similarity|tf\s+cosine\s+similarity)\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if cos_tf_m:
            t1, t2, target = cos_tf_m.group(1).strip(), cos_tf_m.group(2).strip(), cos_tf_m.group(3).strip()
            return f"set {target} to nlp_cosine_similarity_tf({t1}, {t2})"

        exp_cont_m = re.match(
            r"^expand\s+contractions\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if exp_cont_m:
            text, target = exp_cont_m.group(1).strip(), exp_cont_m.group(2).strip()
            return f"set {target} to nlp_expand_contractions({text})"

        mask_m = re.match(
            r"^mask\s+sensitive\s+entities\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if mask_m:
            text, target = mask_m.group(1).strip(), mask_m.group(2).strip()
            return f"set {target} to nlp_mask_sensitive_entities({text})"

        flesch_m = re.match(
            r"^flesch\s+reading\s+ease\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if flesch_m:
            text, target = flesch_m.group(1).strip(), flesch_m.group(2).strip()
            return f"set {target} to nlp_readability_flesch({text})"

        fog_m = re.match(
            r"^gunning\s+fog\s+index\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if fog_m:
            text, target = fog_m.group(1).strip(), fog_m.group(2).strip()
            return f"set {target} to nlp_readability_gunning_fog({text})"

        syll_m = re.match(
            r"^count\s+syllables\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if syll_m:
            word, target = syll_m.group(1).strip(), syll_m.group(2).strip()
            return f"set {target} to nlp_syllable_count({word})"

        s_split_m = re.match(
            r"^(?:split\s+(.+?)\s+into\s+sentences|split\s+into\s+sentences\s+(.+?))\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if s_split_m:
            text = (s_split_m.group(1) or s_split_m.group(2)).strip()
            target = s_split_m.group(3).strip()
            return f"set {target} to nlp_sentence_split({text})"

        pos_m = re.match(
            r"^(?:tag\s+parts\s+of\s+speech\s+in|pos\s+tag)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if pos_m:
            toks, target = pos_m.group(1).strip(), pos_m.group(2).strip()
            return f"set {target} to nlp_pos_tag_rule_based({toks})"

        vader_m = re.match(
            r"^(?:heuristic\s+sentiment\s+score\s+for|vader\s+sentiment\s+of)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if vader_m:
            text, target = vader_m.group(1).strip(), vader_m.group(2).strip()
            return f"set {target} to nlp_sentiment_vader_heuristic({text})"

        c_ngram_m = re.match(
            r"^(?:extract\s+(\d+)-character\s+ngrams\s+from\s+(.+?)|character\s+ngrams\s+from\s+(.+?)\s+with\s+n\s+(\d+))\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if c_ngram_m:
            if c_ngram_m.group(1) is not None:
                n_val, text = c_ngram_m.group(1).strip(), c_ngram_m.group(2).strip()
            else:
                text, n_val = c_ngram_m.group(3).strip(), c_ngram_m.group(4).strip()
            target = c_ngram_m.group(5).strip()
            return f"set {target} to nlp_character_ngrams({text}, n={n_val})"

        colloc_m = re.match(
            r"^(?:find\s+collocations\s+in|collocations\s+in)\s+(.+?)(?:\s+with\s+min\s+frequency\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if colloc_m:
            toks = colloc_m.group(1).strip()
            k_val = colloc_m.group(2) or "2"
            target = colloc_m.group(3).strip()
            return f"set {target} to nlp_collocations({toks}, min_freq={k_val})"

        wrap_m = re.match(
            r"^(?:wrap\s+text|word\s+wrap)\s+(.+?)\s+(?:at|with)\s+width\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if wrap_m:
            text, w, target = wrap_m.group(1).strip(), wrap_m.group(2).strip(), wrap_m.group(3).strip()
            return f"set {target} to nlp_word_wrap({text}, width={w})"

        # summarize text <text> [with <n> sentences] into <target>
        summ_m = re.match(
            r"^summarize\s+text\s+(.+?)(?:\s+with\s+(\d+)\s+sentences)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if summ_m:
            text = summ_m.group(1).strip()
            n_sent = summ_m.group(2) or "3"
            target = summ_m.group(3).strip()
            return f"set {target} to nlp_textrank_summarize({text}, num_sentences={n_sent})"

        # fuzzy match <query> in dictionary <vocab> [with max distance <k>] into <target>
        fuz_dict_m = re.match(
            r"^fuzzy\s+match\s+(.+?)\s+in\s+dictionary\s+(.+?)(?:\s+with\s+max\s+distance\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if fuz_dict_m:
            q = fuz_dict_m.group(1).strip()
            vocab = fuz_dict_m.group(2).strip()
            max_d = fuz_dict_m.group(3) or "2"
            target = fuz_dict_m.group(4).strip()
            return f"set {target} to nlp_fuzzy_match({q}, {vocab}, max_distance={max_d})"

        # fuzzy search <query> in text <text> [with max distance <k>] into <target>
        fuz_txt_m = re.match(
            r"^fuzzy\s+search\s+(.+?)\s+in\s+text\s+(.+?)(?:\s+with\s+max\s+distance\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if fuz_txt_m:
            q = fuz_txt_m.group(1).strip()
            txt = fuz_txt_m.group(2).strip()
            max_d = fuz_txt_m.group(3) or "2"
            target = fuz_txt_m.group(4).strip()
            return f"set {target} to nlp_fuzzy_search_text({q}, {txt}, max_distance={max_d})"

        # search bm25 corpus <corpus> query <query> [top <k>] into <target>
        bm25_m = re.match(
            r"^search\s+bm25\s+corpus\s+(.+?)\s+query\s+(.+?)(?:\s+top\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if bm25_m:
            corpus = bm25_m.group(1).strip()
            query = bm25_m.group(2).strip()
            top_k = bm25_m.group(3) or "5"
            target = bm25_m.group(4).strip()
            if not (query.startswith('"') or query.startswith("'") or query.isidentifier()):
                query = f'"{query}"'
            return f"set {target} to nlp_bm25_search({corpus}, {query}, top_k={top_k})"

        # parse pcfg grammar <grammar> tokens <tokens> [start <start>] into <target>
        pcfg_m = re.match(
            r"^parse\s+pcfg\s+grammar\s+(.+?)\s+tokens\s+(.+?)(?:\s+start\s+([A-Za-z_]\w*|\"[^\"]+\"))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if pcfg_m:
            grammar = pcfg_m.group(1).strip()
            tokens = pcfg_m.group(2).strip()
            start_sym = pcfg_m.group(3) or '"S"'
            if not (start_sym.startswith('"') or start_sym.startswith("'")):
                start_sym = f'"{start_sym}"'
            target = pcfg_m.group(4).strip()
            return f"set {target} to nlp_pcfg_parse({grammar}, {tokens}, start_symbol={start_sym})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[NLPTfidfSpec, str]:
        # tfidf <corpus> into <target>:
        m = re.match(r"^tfidf\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*):?$", header.strip(), re.IGNORECASE)
        if not m:
            raise SyntaxError(f"Invalid tfidf block header: {header}")

        corpus = m.group(1)
        target = m.group(2)
        spec = NLPTfidfSpec(corpus_var=corpus, target_var=target)

        for _, raw_line in body_lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            mf_m = re.match(r"^max_features\s*:\s*(\d+)", line, re.IGNORECASE)
            if mf_m:
                spec.max_features = int(mf_m.group(1))

        errors = spec.validate()
        if errors:
            raise SyntaxError(f"TFIDF block validation error: {'; '.join(errors)}")

        return spec, target
