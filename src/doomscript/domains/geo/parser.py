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

        # point [at] [lat] <lat> [,] [and lon] <lon> into <target>
        m_pt = re.match(
            r"^point(?:\s+at)?(?:\s+lat)?\s+([-\d.]+)\s*(?:,\s*|and\s+lon\s+)\s*([-\d.]+)\s+into\s+([A-Za-z_]\w*)$",
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

        # calculate haversine distance from <p1> to <p2> [in <unit>] into <target>
        hav_m = re.match(
            r"^(?:calculate\s+)?haversine\s+distance\s+from\s+(.+?)\s+to\s+(.+?)(?:\s+in\s+([A-Za-z]+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if hav_m:
            p1 = hav_m.group(1).strip()
            p2 = hav_m.group(2).strip()
            if "," in p1 and not (p1.startswith("(") or p1.startswith("[")):
                p1 = f"({p1})"
            if "," in p2 and not (p2.startswith("(") or p2.startswith("[")):
                p2 = f"({p2})"
            unit = hav_m.group(3) or "km"
            target = hav_m.group(4).strip()
            return f'set {target} to geo_haversine_distance({p1}, {p2}, unit="{unit}")'

        # check if bounding box <bbox> contains <pt> into <target>
        bbox_m = re.match(
            r"^check\s+if\s+bounding\s+box\s+(.+?)\s+contains\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if bbox_m:
            bbox, pt, target = bbox_m.group(1).strip(), bbox_m.group(2).strip(), bbox_m.group(3).strip()
            return f"set {target} to geo_bounding_box_contains({bbox}, {pt})"

        # calculate centroid of [coordinates] <coords> into <target>
        cent_m = re.match(
            r"^(?:calculate\s+)?centroid\s+of\s+(?:coordinates\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if cent_m:
            coords, target = cent_m.group(1).strip(), cent_m.group(2).strip()
            return f"set {target} to geo_centroid({coords})"

        # calculate polygon area for/of [coordinates] <coords> into <target>
        parea_m = re.match(
            r"^(?:calculate\s+)?polygon\s+area\s+(?:for|of)\s+(?:coordinates\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if parea_m:
            coords, target = parea_m.group(1).strip(), parea_m.group(2).strip()
            return f"set {target} to geo_polygon_area({coords})"

        # convert coordinate <pt> to geojson point into <target>
        gjp_m = re.match(
            r"^convert\s+coordinate\s+(.+?)\s+to\s+geojson\s+point\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if gjp_m:
            pt, target = gjp_m.group(1).strip(), gjp_m.group(2).strip()
            return f"set {target} to geo_to_geojson_point({pt})"

        # find nearest coordinate to <pt> from <list> into <target>
        near_m = re.match(
            r"^find\s+nearest\s+coordinate\s+to\s+(.+?)\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if near_m:
            pt, candidates, target = near_m.group(1).strip(), near_m.group(2).strip(), near_m.group(3).strip()
            return f"set {target} to geo_nearest_coordinate({pt}, {candidates})"

        # encode geohash lat <lat> lon <lon> [with precision <p>] into <target>
        m_egh = re.match(
            r"^encode\s+geohash\s+lat\s+(.+?)\s+lon\s+(.+?)(?:\s+with\s+precision\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_egh:
            lt, ln, prec, target = m_egh.group(1).strip(), m_egh.group(2).strip(), m_egh.group(3), m_egh.group(4).strip()
            p_val = prec if prec else "12"
            return f"set {target} to geo_encode_geohash({lt}, {ln}, {p_val})"

        # decode geohash <gh> into <target>
        m_dgh = re.match(
            r"^decode\s+geohash\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dgh:
            gh, target = m_dgh.group(1).strip(), m_dgh.group(2).strip()
            return f"set {target} to geo_decode_geohash({gh})"

        # cross track distance of <pt> from <start> to <end> into <target>
        m_xtd = re.match(
            r"^cross\s+track\s+distance\s+of\s+(.+?)\s+from\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_xtd:
            pt, st, end, target = m_xtd.group(1).strip(), m_xtd.group(2).strip(), m_xtd.group(3).strip(), m_xtd.group(4).strip()
            return f"set {target} to geo_cross_track_distance({pt}, {st}, {end})"

        # destination point from lat <lat> lon <lon> distance <d> bearing <brng> into <target>
        m_dest = re.match(
            r"^destination\s+point\s+from\s+lat\s+(.+?)\s+lon\s+(.+?)\s+distance\s+(.+?)\s+bearing\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dest:
            lt, ln, d, brng, target = m_dest.group(1).strip(), m_dest.group(2).strip(), m_dest.group(3).strip(), m_dest.group(4).strip(), m_dest.group(5).strip()
            return f"set {target} to geo_destination_point({lt}, {ln}, {d}, {brng})"

        # initial bearing from <p1> to <p2> into <target>
        m_ib = re.match(
            r"^initial\s+bearing\s+from\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ib:
            p1, p2, target = m_ib.group(1).strip(), m_ib.group(2).strip(), m_ib.group(3).strip()
            return f"set {target} to geo_initial_bearing({p1}, {p2})"

        # final bearing from <p1> to <p2> into <target>
        m_fb = re.match(
            r"^final\s+bearing\s+from\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fb:
            p1, p2, target = m_fb.group(1).strip(), m_fb.group(2).strip(), m_fb.group(3).strip()
            return f"set {target} to geo_final_bearing({p1}, {p2})"

        # midpoint between <p1> and <p2> into <target>
        m_mid = re.match(
            r"^midpoint\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mid:
            p1, p2, target = m_mid.group(1).strip(), m_mid.group(2).strip(), m_mid.group(3).strip()
            return f"set {target} to geo_midpoint({p1}, {p2})"

        # bounding box intersection of <b1> and <b2> into <target>
        m_bbi = re.match(
            r"^bounding\s+box\s+intersection\s+of\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bbi:
            b1, b2, target = m_bbi.group(1).strip(), m_bbi.group(2).strip(), m_bbi.group(3).strip()
            return f"set {target} to geo_bounding_box_intersection({b1}, {b2})"

        # bounding box union of <b1> and <b2> into <target>
        m_bbu = re.match(
            r"^bounding\s+box\s+union\s+of\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bbu:
            b1, b2, target = m_bbu.group(1).strip(), m_bbu.group(2).strip(), m_bbu.group(3).strip()
            return f"set {target} to geo_bounding_box_union({b1}, {b2})"

        # convex hull of <coords> into <target>
        m_hull = re.match(
            r"^(?:calculate\s+|compute\s+)?convex\s+hull\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hull:
            coords, target = m_hull.group(1).strip(), m_hull.group(2).strip()
            return f"set {target} to geo_convex_hull_graham({coords})"

        # distance from point <pt> to line segment from <ls> to <le> into <target>
        m_ptl = re.match(
            r"^distance\s+from\s+point\s+(.+?)\s+to\s+line\s+segment\s+from\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ptl:
            pt, ls, le, target = m_ptl.group(1).strip(), m_ptl.group(2).strip(), m_ptl.group(3).strip(), m_ptl.group(4).strip()
            return f"set {target} to geo_point_to_line_distance({pt}, {ls}, {le})"

        # simplify polyline <coords> with tolerance <eps> into <target>
        m_simp = re.match(
            r"^simplify\s+polyline\s+(.+?)\s+with\s+tolerance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_simp:
            coords, eps, target = m_simp.group(1).strip(), m_simp.group(2).strip(), m_simp.group(3).strip()
            return f"set {target} to geo_simplify_douglas_peucker({coords}, {eps})"

        # convert coordinates <coords> to geojson polygon into <target>
        m_gpoly = re.match(
            r"^convert\s+coordinates\s+(.+?)\s+to\s+geojson\s+polygon\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_gpoly:
            coords, target = m_gpoly.group(1).strip(), m_gpoly.group(2).strip()
            return f"set {target} to geo_to_geojson_polygon({coords})"

        # convert features <features> to geojson feature collection into <target>
        m_gfc = re.match(
            r"^convert\s+features\s+(.+?)\s+to\s+geojson\s+feature\s+collection\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_gfc:
            feats, target = m_gfc.group(1).strip(), m_gfc.group(2).strip()
            return f"set {target} to geo_to_geojson_feature_collection({feats})"

        # calculate perimeter of polygon <coords> into <target>
        m_perim = re.match(
            r"^(?:calculate\s+)?perimeter\s+of\s+polygon\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_perim:
            coords, target = m_perim.group(1).strip(), m_perim.group(2).strip()
            return f"set {target} to geo_polygon_perimeter({coords})"

        # circular buffer around <pt> with radius <r> [and <n> points] into <target>
        m_circ = re.match(
            r"^circular\s+buffer\s+around\s+(.+?)\s+with\s+radius\s+(.+?)(?:\s+and\s+(\d+)\s+points)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_circ:
            pt, r, n, target = m_circ.group(1).strip(), m_circ.group(2).strip(), m_circ.group(3), m_circ.group(4).strip()
            n_val = n if n else "32"
            return f"set {target} to geo_buffer_point_circle({pt}, {r}, {n_val})"

        # utm zone for longitude <lon> into <target>
        m_utm = re.match(
            r"^utm\s+zone\s+for\s+longitude\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_utm:
            lon, target = m_utm.group(1).strip(), m_utm.group(2).strip()
            return f"set {target} to geo_utm_zone_number({lon})"

        # rhumb line distance between <p1> and <p2> into <target>
        m_rld = re.match(
            r"^rhumb\s+line\s+distance\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rld:
            p1, p2, target = m_rld.group(1).strip(), m_rld.group(2).strip(), m_rld.group(3).strip()
            return f"set {target} to geo_rhumb_line_distance({p1}, {p2})"

        # rhumb line bearing from <p1> to <p2> into <target>
        m_rlb = re.match(
            r"^rhumb\s+line\s+bearing\s+from\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rlb:
            p1, p2, target = m_rlb.group(1).strip(), m_rlb.group(2).strip(), m_rlb.group(3).strip()
            return f"set {target} to geo_rhumb_line_bearing({p1}, {p2})"

        # calculate vincenty distance from lat <lat1> lon <lon1> to lat <lat2> lon <lon2> into <target>
        m_vinc = re.match(
            r"^calculate\s+vincenty\s+distance\s+from\s+lat\s+(.+?)\s+lon\s+(.+?)\s+to\s+lat\s+(.+?)\s+lon\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vinc:
            lat1, lon1, lat2, lon2, target = m_vinc.group(1).strip(), m_vinc.group(2).strip(), m_vinc.group(3).strip(), m_vinc.group(4).strip(), m_vinc.group(5).strip()
            return f"set {target} to geo_vincenty_distance({lat1}, {lon1}, {lat2}, {lon2})"

        # simplify polyline <pts> with epsilon <eps> into <target>
        m_dp = re.match(
            r"^simplify\s+polyline\s+(.+?)\s+with\s+epsilon\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dp:
            pts, eps, target = m_dp.group(1).strip(), m_dp.group(2).strip(), m_dp.group(3).strip()
            return f"set {target} to geo_douglas_peucker({pts}, {eps})"

        # clip polygon <subject> against <clipper> into <target>
        m_clip = re.match(
            r"^clip\s+polygon\s+(.+?)\s+against\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_clip:
            subj, clip, target = m_clip.group(1).strip(), m_clip.group(2).strip(), m_clip.group(3).strip()
            return f"set {target} to geo_sutherland_hodgman_clip({subj}, {clip})"

        # project utm coordinates lat <lat> lon <lon> into <target>
        m_utm_fwd = re.match(
            r"^project\s+utm\s+coordinates\s+lat\s+(.+?)\s+lon\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_utm_fwd:
            lat, lon, target = m_utm_fwd.group(1).strip(), m_utm_fwd.group(2).strip(), m_utm_fwd.group(3).strip()
            return f"set {target} to geo_utm_forward({lat}, {lon})"

        # invert utm coordinates easting <e> northing <n> zone <z> [northern <bool>] into <target>
        m_utm_inv = re.match(
            r"^invert\s+utm\s+coordinates\s+easting\s+(.+?)\s+northing\s+(.+?)\s+zone\s+(.+?)(?:\s+northern\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_utm_inv:
            east = m_utm_inv.group(1).strip()
            north = m_utm_inv.group(2).strip()
            zone = m_utm_inv.group(3).strip()
            northern = m_utm_inv.group(4).strip() if m_utm_inv.group(4) else "True"
            target = m_utm_inv.group(5).strip()
            return f"set {target} to geo_utm_inverse({east}, {north}, {zone}, {northern})"

        # encode spatial geohash lat <lat> lon <lon> [precision <p>] into <target>
        m_sge = re.match(
            r"^encode\s+spatial\s+geohash\s+lat\s+(.+?)\s+lon\s+(.+?)(?:\s+precision\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sge:
            lat, lon, prec, target = m_sge.group(1).strip(), m_sge.group(2).strip(), m_sge.group(3), m_sge.group(4).strip()
            p_val = prec.strip() if prec else "7"
            return f"set {target} to geo_geohash_encode({lat}, {lon}, {p_val})"

        # decode spatial geohash <hash> into <target>
        m_sgd = re.match(
            r"^decode\s+spatial\s+geohash\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sgd:
            gh, target = m_sgd.group(1).strip(), m_sgd.group(2).strip()
            return f"set {target} to geo_geohash_decode({gh})"

        # partition voronoi diagram sites <sites> into <target>
        # compute voronoi partition [for points|sites] <sites> into <target>
        m_vor = re.match(
            r"^(?:partition\s+voronoi\s+diagram\s+sites|compute\s+voronoi\s+partition(?:\s+for\s+(?:points|sites))?)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vor:
            sites_arg, target = m_vor.group(1).strip(), m_vor.group(2).strip()
            return f"set {target} to geo_voronoi_partition({sites_arg})"

        # interpolate kriging known/points <known> queries/targets <queries> [nugget <n>] [sill <s>] [range <r>] into <target>
        m_krig = re.match(
            r"^interpolate\s+kriging\s+(?:known|points)\s+(.+?)\s+(?:queries|targets)\s+(.+?)(?:\s+nugget\s+(.+?))?(?:\s+sill\s+(.+?))?(?:\s+range\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_krig:
            known_arg, query_arg = m_krig.group(1).strip(), m_krig.group(2).strip()
            nug = m_krig.group(3).strip() if m_krig.group(3) else "0.0"
            sill = m_krig.group(4).strip() if m_krig.group(4) else "1.0"
            rng = m_krig.group(5).strip() if m_krig.group(5) else "10.0"
            target = m_krig.group(6).strip()
            return f"set {target} to geo_kriging_interpolate({known_arg}, {query_arg}, nugget={nug}, sill={sill}, range_a={rng})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Geospatial domain operations are declarative single-line statements.")
