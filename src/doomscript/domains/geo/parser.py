"""Independent Domain Parser for Geospatial Analytics language constructs."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.geo.spec import (
    GeoPointSpec,
    GeoPolygonSpec,
    GeoDistanceSpec,
    GeoContainmentSpec,
    GeoBoundingBoxSpec,
    GeoSpatialJoinSpec,
)


class GeoDomainParser(DomainParser):
    """Independent parser for Geospatial Analytics syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # bounding box of <geom> into <target>
        m_box = re.match(
            r"^bounding\s+box\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_box:
            geom_expr = m_box.group(1).strip()
            target = m_box.group(2).strip()
            return f"set {target} to bounding_box({geom_expr})"

        # check if <pt> is inside <poly> into <target> OR is <pt> inside <poly> into <target>
        m_cont = re.match(
            r"^(?:check\s+if\s+([A-Za-z_]\w*)\s+is|is\s+([A-Za-z_]\w*))\s+inside\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cont:
            pt = (m_cont.group(1) or m_cont.group(2)).strip()
            poly = m_cont.group(3).strip()
            target = m_cont.group(4).strip()
            return f"set {target} to is_point_in_polygon({pt}, {poly})"

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # point [at] <lat>, <lon> into <target>
        m_pt = re.match(
            r"^point(?:\s+at)?\s+([-\d.]+)\s*,\s*([-\d.]+)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pt:
            lat = m_pt.group(1)
            lon = m_pt.group(2)
            target = m_pt.group(3)
            return f"set {target} to point({lat}, {lon})"

        # polygon from / with coords <expr> into <target>
        m_poly = re.match(
            r"^polygon\s+(?:from|with\s+coords)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_poly:
            coords = m_poly.group(1).strip()
            target = m_poly.group(2).strip()
            return f"set {target} to polygon({coords})"

        # distance between <p1> and <p2> / distance from <p1> to <p2> [in (km|miles|meters)] into <target>
        m_dist = re.match(
            r"^distance\s+(?:between\s+([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)|from\s+([A-Za-z_]\w*)\s+to\s+([A-Za-z_]\w*))(?:\s+in\s+([A-Za-z]+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dist:
            p1 = m_dist.group(1) or m_dist.group(3)
            p2 = m_dist.group(2) or m_dist.group(4)
            unit = m_dist.group(5) or "km"
            target = m_dist.group(6).strip()
            return f'set {target} to distance_between({p1}, {p2}, unit="{unit}")'

        # spatial join <pts> with <polys> into <target>
        m_join = re.match(
            r"^spatial\s+join\s+(.+?)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_join:
            pts = m_join.group(1).strip()
            polys = m_join.group(2).strip()
            target = m_join.group(3).strip()
            return f"set {target} to spatial_join({pts}, {polys})"

        # convert <geom> to geojson into <target>
        m_gj = re.match(
            r"^convert\s+(.+?)\s+to\s+geojson\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_gj:
            geom = m_gj.group(1).strip()
            target = m_gj.group(2).strip()
            return f"set {target} to to_geojson({geom})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Geospatial domain operations are declarative single-line statements.")
