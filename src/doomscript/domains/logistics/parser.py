"""Logistics Domain Natural Language Parser."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class LogisticsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate economic order quantity for demand <d> order cost <s> holding cost <h> into <target>
        m_eoq = re.match(r"^calculate\s+economic\s+order\s+quantity\s+for\s+demand\s+(.+?)\s+order\s+cost\s+(.+?)\s+holding\s+cost\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_eoq:
            return f"set {m_eoq.group(4)} to logistics_economic_order_quantity({m_eoq.group(1)}, {m_eoq.group(2)}, {m_eoq.group(3)})"

        # calculate reorder point for lead time <lt> daily demand <d> into <target>
        m_rop = re.match(r"^calculate\s+reorder\s+point\s+for\s+lead\s+time\s+(.+?)\s+daily\s+demand\s+(.+?)(?:\s+safety\s+stock\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rop:
            if m_rop.group(3) is not None:
                return f"set {m_rop.group(4)} to logistics_reorder_point({m_rop.group(1)}, {m_rop.group(2)}, {m_rop.group(3)})"
            return f"set {m_rop.group(4)} to logistics_reorder_point({m_rop.group(1)}, {m_rop.group(2)})"

        # calculate safety stock for z <z> std <std> lead time <lt> into <target>
        m_ss = re.match(r"^calculate\s+safety\s+stock\s+for\s+z\s+(.+?)\s+(?:std\s+demand|std)\s+(.+?)\s+lead\s+time\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ss:
            return f"set {m_ss.group(4)} to logistics_safety_stock({m_ss.group(1)}, {m_ss.group(2)}, {m_ss.group(3)})"

        # solve tsp nearest neighbor for matrix <m> into <target>
        m_tsp = re.match(r"^solve\s+tsp\s+nearest\s+neighbor\s+for\s+matrix\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tsp:
            return f"set {m_tsp.group(2)} to logistics_tsp_nearest_neighbor({m_tsp.group(1)})"

        # calculate bullwhip effect for orders <o> demand <d> into <target>
        m_bw = re.match(r"^calculate\s+bullwhip\s+effect\s+(?:for\s+)?orders\s+(.+?)\s+demand\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bw:
            return f"set {m_bw.group(3)} to logistics_bullwhip_effect({m_bw.group(1)}, {m_bw.group(2)})"

        
        m_eoq_alt = re.match(r"^calculate\s+eoq\s+for\s+demand\s+(.+?)\s+order\s+cost\s+(.+?)\s+holding\s+cost\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_eoq_alt:
            return f"set {m_eoq_alt.group(4)} to logistics_economic_order_quantity({m_eoq_alt.group(1)}, {m_eoq_alt.group(2)}, {m_eoq_alt.group(3)})"

        m_nv_opt = re.match(r"^calculate\s+newsvendor\s+(?:for\s+)?cost\s+(.+?)\s+price\s+(.+?)\s+salvage\s+(.+?)\s+demand\s+(.+?)\s+std\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_nv_opt:
            return f"set {m_nv_opt.group(6)} to logistics_newsvendor_optimal({m_nv_opt.group(1)}, {m_nv_opt.group(2)}, {m_nv_opt.group(3)}, {m_nv_opt.group(4)}, {m_nv_opt.group(5)})"

        m_nv_alt = re.match(r"^calculate\s+newsvendor\s+for\s+cost\s+(.+?)\s+price\s+(.+?)\s+salvage\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_nv_alt:
            return f"set {m_nv_alt.group(4)} to logistics_newsvendor_fractile({m_nv_alt.group(1)}, {m_nv_alt.group(2)}, {m_nv_alt.group(3)})"

        m_bw_alt = re.match(r"^calculate\s+bullwhip\s+for\s+order\s+var\s+(.+?)\s+demand\s+var\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bw_alt:
            return f"set {m_bw_alt.group(3)} to logistics_bullwhip_effect({m_bw_alt.group(1)}, {m_bw_alt.group(2)})"

        m_tsp_alt = re.match(r"^solve\s+tsp\s+nearest\s+neighbor\s+for\s+dist\s+matrix\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tsp_alt:
            return f"set {m_tsp_alt.group(2)} to logistics_tsp_nearest_neighbor({m_tsp_alt.group(1)})"

        m_cog_alt = re.match(r"^solve\s+center\s+of\s+gravity\s+for\s+points\s+(.+?)\s+weights\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cog_alt:
            return f"set {m_cog_alt.group(3)} to logistics_center_of_gravity({m_cog_alt.group(1)}, {m_cog_alt.group(2)})"

        m_abc_alt = re.match(r"^classify\s+abc\s+inventory\s+for\s+items\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_abc_alt:
            return f"set {m_abc_alt.group(2)} to logistics_abc_classification({m_abc_alt.group(1)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Logistics domain does not define declarative blocks")
