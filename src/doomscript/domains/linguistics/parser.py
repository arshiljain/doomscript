import re
from typing import Optional
from doomscript.domains.base import DomainParser

class LinguisticsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_dist = re.match(r"^calculate\s+edit\s+distance\s+for\s+word1\s+(.+?)\s+word2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dist:
            return f"set {m_dist.group(3)} to ling_levenshtein_distance({m_dist.group(1)}, {m_dist.group(2)})"

        m_snd = re.match(r"^calculate\s+soundex\s+for\s+word\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_snd:
            return f"set {m_snd.group(2)} to ling_soundex({m_snd.group(1)})"

        m_syl = re.match(r"^calculate\s+syllables\s+for\s+word\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_syl:
            return f"set {m_syl.group(2)} to ling_count_syllables({m_syl.group(1)})"

        m_read = re.match(r"^calculate\s+flesch\s+readability\s+for\s+text\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_read:
            return f"set {m_read.group(2)} to ling_flesch_reading_ease({m_read.group(1)})"

        m_ttr = re.match(r"^calculate\s+lexical\s+diversity\s+for\s+text\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ttr:
            return f"set {m_ttr.group(2)} to ling_type_token_ratio({m_ttr.group(1)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Linguistics domain does not define declarative blocks")
