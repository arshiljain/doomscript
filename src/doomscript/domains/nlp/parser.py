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
        # analyze sentiment of <expr> [into <target>]
        m_sent = re.match(
            r"^analyze\s+sentiment\s+of\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
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

        # calculate tfidf of <corpus> [with max_features <n>] into <target>
        m_tfidf = re.match(
            r"^calculate\s+tfidf\s+of\s+(.+?)(?:\s+with\s+max_features\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
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

        # extract entities from <expr> into <target>
        m_ent = re.match(
            r"^extract\s+entities\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ent:
            expr = m_ent.group(1).strip()
            target = m_ent.group(2).strip()
            return f"set {target} to extract_entities({expr})"

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
