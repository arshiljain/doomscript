"""Linguistics Domain Natural Language Parser."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class LinguisticsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate edit distance for word1 <w1> word2 <w2> into <target>
        m_edit = re.match(r"^calculate\s+edit\s+distance\s+for\s+word1\s+(.+?)\s+word2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_edit:
            return f"set {m_edit.group(3)} to ling_levenshtein_distance({m_edit.group(1)}, {m_edit.group(2)})"

        # calculate jaro winkler for word1 <w1> word2 <w2> into <target>
        m_jw = re.match(r"^calculate\s+jaro\s+winkler\s+for\s+word1\s+(.+?)\s+word2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_jw:
            return f"set {m_jw.group(3)} to ling_jaro_winkler({m_jw.group(1)}, {m_jw.group(2)})"

        # calculate soundex for word <w> into <target>
        m_snd = re.match(r"^calculate\s+soundex\s+for\s+word\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_snd:
            return f"set {m_snd.group(2)} to ling_soundex({m_snd.group(1)})"

        # calculate syllables for word <w> into <target>
        m_syl = re.match(r"^calculate\s+syllables\s+for\s+word\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_syl:
            return f"set {m_syl.group(2)} to ling_count_syllables({m_syl.group(1)})"

        # calculate flesch readability for text <t> into <target>
        m_fl = re.match(r"^calculate\s+flesch\s+readability\s+for\s+text\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_fl:
            return f"set {m_fl.group(2)} to ling_flesch_reading_ease({m_fl.group(1)})"

        # calculate gunning fog for text <t> into <target>
        m_fog = re.match(r"^calculate\s+gunning\s+fog\s+for\s+text\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_fog:
            return f"set {m_fog.group(2)} to ling_gunning_fog({m_fog.group(1)})"

        # calculate lexical diversity for text <t> into <target>
        m_ttr = re.match(r"^calculate\s+lexical\s+diversity\s+for\s+text\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ttr:
            return f"set {m_ttr.group(2)} to ling_type_token_ratio({m_ttr.group(1)})"

        # stem word <w> into <target>
        m_stem = re.match(r"^stem\s+word\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_stem:
            return f"set {m_stem.group(2)} to ling_porter_stem({m_stem.group(1)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Linguistics domain does not define declarative blocks")
