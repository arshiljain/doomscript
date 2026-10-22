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
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("GenAI domain does not define declarative blocks")
