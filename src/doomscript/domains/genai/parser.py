"""GenAI Domain Natural Language Parser."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class GenaiDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        
        # chunk text <text> with size <size> overlap <overlap> into <target>
        m_chunk = re.match(r"^chunk\s+text\s+(.+?)\s+with\s+size\s+(\d+|[A-Za-z_]\w*)\s+overlap\s+(\d+|[A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_chunk:
            return f"set {m_chunk.group(4)} to genai_chunk_text({m_chunk.group(1)}, {m_chunk.group(2)}, {m_chunk.group(3)})"

        # calculate cosine similarity between <v1> and <v2> into <target>
        m_cos = re.match(r"^calculate\s+cosine\s+similarity\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cos:
            return f"set {m_cos.group(3)} to genai_cosine_similarity({m_cos.group(1)}, {m_cos.group(2)})"

        # estimate token count for <text> into <target>
        m_tok = re.match(r"^estimate\s+token\s+count\s+for\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tok:
            return f"set {m_tok.group(2)} to genai_estimate_tokens({m_tok.group(1)})"

        # apply prompt template <tpl> with variables <vars> into <target>
        m_tpl = re.match(r"^apply\s+prompt\s+template\s+(.+?)\s+with\s+variables\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tpl:
            return f"set {m_tpl.group(3)} to genai_apply_template({m_tpl.group(1)}, {m_tpl.group(2)})"

        # fuse rankings for lists <lists> into <target>
        m_rrf = re.match(r"^fuse\s+rankings\s+for\s+lists\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rrf:
            return f"set {m_rrf.group(2)} to genai_reciprocal_rank_fusion({m_rrf.group(1)})"

        # check prompt injection for text <text> into <target>
        m_inj = re.match(r"^check\s+prompt\s+injection\s+for\s+text\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_inj:
            return f"set {m_inj.group(2)} to genai_detect_prompt_injection({m_inj.group(1)})"

        # calculate rouge score candidate <cand> reference <ref> into <target>
        m_rouge = re.match(r"^calculate\s+rouge\s+score\s+candidate\s+(.+?)\s+reference\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rouge:
            return f"set {m_rouge.group(3)} to genai_rouge_l({m_rouge.group(1)}, {m_rouge.group(2)})"

        # calculate bleu score candidate <cand> reference <ref> into <target>
        m_bleu = re.match(r"^calculate\s+bleu\s+score\s+candidate\s+(.+?)\s+reference\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bleu:
            return f"set {m_bleu.group(3)} to genai_bleu_score({m_bleu.group(1)}, {m_bleu.group(2)})"

        # redact pii in text <text> into <target>
        m_redact = re.match(r"^redact\s+pii\s+in\s+text\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_redact:
            return f"set {m_redact.group(2)} to genai_redact_pii({m_redact.group(1)})"

        # calculate kv memory for layers <l> heads <h> dim <d> seq <seq> into <target>
        m_kv = re.match(r"^calculate\s+kv\s+memory\s+for\s+layers\s+(.+?)\s+heads\s+(.+?)\s+dim\s+(.+?)\s+seq\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_kv:
            return f"set {m_kv.group(5)} to genai_calculate_kv_cache_memory({m_kv.group(1)}, {m_kv.group(2)}, {m_kv.group(3)}, {m_kv.group(4)})"

        # sample logits <logits> with temperature <temp> into <target>
        m_samp = re.match(r"^sample\s+logits\s+(.+?)\s+with\s+temperature\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_samp:
            return f"set {m_samp.group(3)} to genai_sample_logits({m_samp.group(1)}, {m_samp.group(2)})"

        # retrieve top <k> chunks from <chunks> for query <query> into <target>
        m_ret = re.match(r"^retrieve\s+top\s+(\d+|[A-Za-z_]\w*)\s+chunks\s+from\s+(.+?)\s+for\s+query\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ret:
            return f"set {m_ret.group(4)} to genai_retrieve_top_k({m_ret.group(2)}, {m_ret.group(3)}, k={m_ret.group(1)})"

        # train bpe for corpus <corpus> merges <n> into <target>
        m_bpe = re.match(r"^train\s+bpe\s+for\s+corpus\s+(.+?)\s+merges\s+(\d+|[A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bpe:
            return f"set {m_bpe.group(3)} to genai_train_bpe({m_bpe.group(1)}, {m_bpe.group(2)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("GenAI domain does not define declarative blocks")
