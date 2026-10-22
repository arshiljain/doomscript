import re
from typing import Optional
from doomscript.domains.base import DomainParser

class RiskDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_var = re.match(r"^calculate\s+historical\s+var\s+for\s+returns\s+(.+?)\s+confidence\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_var:
            return f"set {m_var.group(3)} to risk_value_at_risk_historical({m_var.group(1)}, {m_var.group(2)})"

        m_cvar = re.match(r"^calculate\s+cvar\s+for\s+returns\s+(.+?)\s+confidence\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cvar:
            return f"set {m_cvar.group(3)} to risk_conditional_var({m_cvar.group(1)}, {m_cvar.group(2)})"

        m_mdd = re.match(r"^calculate\s+max\s+drawdown\s+for\s+prices\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mdd:
            return f"set {m_mdd.group(2)} to risk_max_drawdown({m_mdd.group(1)})"

        m_sharpe = re.match(r"^calculate\s+sharpe\s+ratio\s+for\s+returns\s+(.+?)\s+risk\s+free\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sharpe:
            return f"set {m_sharpe.group(3)} to risk_sharpe_ratio({m_sharpe.group(1)}, {m_sharpe.group(2)})"

        m_sortino = re.match(r"^calculate\s+sortino\s+ratio\s+for\s+returns\s+(.+?)\s+target\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sortino:
            return f"set {m_sortino.group(3)} to risk_sortino_ratio({m_sortino.group(1)}, {m_sortino.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Risk domain does not define declarative blocks")
