"""Astronomy Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class AstronomyDomainParser(DomainParser):
    """Parses spoken-English astronomy, Keplerian orbits, and celestial coordinate statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate julian date for year <y> month <m> day <d> into <target>
        m_jd = re.match(
            r"^calculate\s+julian\s+date\s+for\s+year\s+(.+?)\s+month\s+(.+?)\s+day\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_jd:
            y, m, d, target = m_jd.group(1).strip(), m_jd.group(2).strip(), m_jd.group(3).strip(), m_jd.group(4).strip()
            return f"set {target} to astronomy_julian_date({y}, {m}, {d})"

        # calculate hohmann transfer from radius <r1> to <r2> into <target>
        m_hoh = re.match(
            r"^calculate\s+hohmann\s+transfer\s+(?:from\s+(?:radius\s+)?)?(.+?)\s+to\s+(.+?)(?:\s+around\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hoh:
            r1, r2 = m_hoh.group(1).strip(), m_hoh.group(2).strip()
            mu = m_hoh.group(3).strip() if m_hoh.group(3) else "3.986004418e14"
            target = m_hoh.group(4).strip()
            return f"set {target} to astronomy_calculate_hohmann({r1}, {r2}, {mu})"

        # simulate n body system with bodies <bodies> duration <dur> [with dt <dt>] into <target>
        m_nb = re.match(
            r"^simulate\s+n\s+body\s+system\s+with\s+bodies\s+(.+?)\s+duration\s+(.+?)(?:\s+with\s+dt\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_nb:
            bodies, dur = m_nb.group(1).strip(), m_nb.group(2).strip()
            dt = m_nb.group(3).strip() if m_nb.group(3) else "60.0"
            target = m_nb.group(4).strip()
            return f"set {target} to astronomy_simulate_n_body({bodies}, {dur}, {dt})"

        # calculate bi-elliptic transfer from <r1> to <r2> via <rb> [around <mu>] into <target>
        m_bi = re.match(
            r"^calculate\s+bi-elliptic\s+transfer\s+from\s+(.+?)\s+to\s+(.+?)\s+via\s+(.+?)(?:\s+around\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bi:
            r1, r2, rb = m_bi.group(1).strip(), m_bi.group(2).strip(), m_bi.group(3).strip()
            mu = m_bi.group(4).strip() if m_bi.group(4) else "3.986004418e14"
            target = m_bi.group(5).strip()
            return f"set {target} to astronomy_calculate_bi_elliptic({r1}, {r2}, {rb}, {mu})"

        # precess coordinates ra <ra> dec <dec> to date <jd> into <target>
        m_pr = re.match(
            r"^precess\s+coordinates\s+ra\s+(.+?)\s+dec\s+(.+?)\s+to\s+date\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pr:
            ra, dec, jd, target = m_pr.group(1).strip(), m_pr.group(2).strip(), m_pr.group(3).strip(), m_pr.group(4).strip()
            return f"set {target} to astronomy_precession_j2000_to_date({ra}, {dec}, {jd})"

        # calculate celestial rise and set for ra <ra> dec <dec> at lat <lat> lon <lon> on <jd> into <target>
        m_rs = re.match(
            r"^calculate\s+celestial\s+rise\s+and\s+set\s+for\s+ra\s+(.+?)\s+dec\s+(.+?)\s+at\s+lat\s+(.+?)\s+lon\s+(.+?)\s+on\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rs:
            ra, dec, lat, lon, jd = m_rs.group(1).strip(), m_rs.group(2).strip(), m_rs.group(3).strip(), m_rs.group(4).strip(), m_rs.group(5).strip()
            target = m_rs.group(6).strip()
            return f"set {target} to astronomy_calculate_rise_set({ra}, {dec}, {lat}, {lon}, {jd})"

        # solve lambert transfer from <r1> to <r2> with tof <tof> into <target>
        m_lamb = re.match(
            r"^solve\s+lambert\s+transfer\s+from\s+(.+?)\s+to\s+(.+?)\s+with\s+tof\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lamb:
            r1, r2, tof, target = m_lamb.group(1).strip(), m_lamb.group(2).strip(), m_lamb.group(3).strip(), m_lamb.group(4).strip()
            return f"set {target} to astronomy_lambert_solve({r1}, {r2}, {tof})"

        # calculate lagrange points for mass1 <m1> and mass2 <m2> at distance <dist> into <target>
        m_lag = re.match(
            r"^calculate\s+lagrange\s+points\s+for\s+mass1\s+(.+?)\s+and\s+mass2\s+(.+?)\s+at\s+distance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lag:
            m1, m2, dist, target = m_lag.group(1).strip(), m_lag.group(2).strip(), m_lag.group(3).strip(), m_lag.group(4).strip()
            return f"set {target} to astronomy_lagrange_points({m1}, {m2}, {dist})"

        # propagate kepler orbit semi_major <a> eccentricity <e> inclination <i> raan <raan> arg_peri <arg> mean_anomaly <m0> delta_days <dt> into <target>
        m_prop = re.match(
            r"^propagate\s+kepler\s+orbit\s+semi_major\s+(.+?)\s+eccentricity\s+(.+?)\s+inclination\s+(.+?)\s+raan\s+(.+?)\s+arg_peri\s+(.+?)\s+mean_anomaly\s+(.+?)\s+delta_days\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_prop:
            a, e, inc, raan, arg, m0, dt, target = (
                m_prop.group(1).strip(),
                m_prop.group(2).strip(),
                m_prop.group(3).strip(),
                m_prop.group(4).strip(),
                m_prop.group(5).strip(),
                m_prop.group(6).strip(),
                m_prop.group(7).strip(),
                m_prop.group(8).strip(),
            )
            return f"set {target} to astronomy_propagate_kepler_orbit({a}, {e}, {inc}, {raan}, {arg}, {m0}, {dt})"

        # calculate sidereal time year <y> month <m> day <d> hour <h> min <mn> sec <s> lon <lon> into <target>
        m_sid = re.match(
            r"^calculate\s+sidereal\s+time\s+year\s+(.+?)\s+month\s+(.+?)\s+day\s+(.+?)\s+hour\s+(.+?)\s+min\s+(.+?)\s+sec\s+(.+?)\s+lon\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sid:
            y, m, d, h, mn, sc, lon, target = (
                m_sid.group(1).strip(),
                m_sid.group(2).strip(),
                m_sid.group(3).strip(),
                m_sid.group(4).strip(),
                m_sid.group(5).strip(),
                m_sid.group(6).strip(),
                m_sid.group(7).strip(),
                m_sid.group(8).strip(),
            )
            return f"set {target} to astronomy_calculate_sidereal_time({y}, {m}, {d}, {h}, {mn}, {sc}, {lon})"

        # propagate sgp4 [satellite] orbit <orbit> [after <dt> minutes] into <target>
        m_sgp4_orb = re.match(
            r"^propagate\s+sgp4\s+(?:satellite\s+)?orbit\s+(.+?)(?:\s+after\s+(.+?)\s+minutes)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sgp4_orb:
            orb, dt, target = m_sgp4_orb.group(1).strip(), m_sgp4_orb.group(2), m_sgp4_orb.group(3).strip()
            dt_arg = f", delta_minutes={dt.strip()}" if dt else ""
            return f"set {target} to astronomy_propagate_sgp4_orbit({orb}{dt_arg})"

        # propagate sgp4 orbit inc <inc> raan <raan> ecc <ecc> argp <argp> ma <ma> mm <mm> [delta minutes <dt>] into <target>
        m_sgp4 = re.match(
            r"^propagate\s+sgp4\s+orbit\s+inc\s+(.+?)\s+raan\s+(.+?)\s+ecc\s+(.+?)\s+argp\s+(.+?)\s+ma\s+(.+?)\s+mm\s+(.+?)(?:\s+delta\s+minutes\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sgp4:
            inc, raan, ecc, argp, ma, mm, dt, target = (
                m_sgp4.group(1).strip(),
                m_sgp4.group(2).strip(),
                m_sgp4.group(3).strip(),
                m_sgp4.group(4).strip(),
                m_sgp4.group(5).strip(),
                m_sgp4.group(6).strip(),
                m_sgp4.group(7),
                m_sgp4.group(8).strip(),
            )
            dt_arg = f", delta_minutes={dt.strip()}" if dt else ""
            return f"set {target} to astronomy_propagate_sgp4({inc}, {raan}, {ecc}, {argp}, {ma}, {mm}{dt_arg})"

        # plan hohmann transfer from <r1> to <r2> into <target>
        m_hoh = re.match(
            r"^plan\s+hohmann\s+transfer\s+from\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hoh:
            r1, r2, target = m_hoh.group(1).strip(), m_hoh.group(2).strip(), m_hoh.group(3).strip()
            return f"set {target} to astronomy_plan_orbital_transfer({r1}, {r2})"

        # plan orbital transfer r1 <r1> r2 <r2> [rb <rb>] [plane change <pc>] into <target>
        m_trans = re.match(
            r"^plan\s+orbital\s+transfer\s+r1\s+(.+?)\s+r2\s+(.+?)(?:\s+rb\s+(.+?))?(?:\s+plane\s+change\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_trans:
            r1, r2, rb, pc, target = (
                m_trans.group(1).strip(),
                m_trans.group(2).strip(),
                m_trans.group(3),
                m_trans.group(4),
                m_trans.group(5).strip(),
            )
            rb_arg = f", rb_km={rb.strip()}" if rb else ""
            pc_arg = f", plane_change_deg={pc.strip()}" if pc else ""
            return f"set {target} to astronomy_plan_orbital_transfer({r1}, {r2}{rb_arg}{pc_arg})"

        # calculate position of planet <planet> at [jd] <jd> into <target>
        m_pos = re.match(
            r"^calculate\s+position\s+of\s+planet\s+(.+?)\s+at(?:\s+jd)?\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pos:
            planet, jd, target = m_pos.group(1).strip(), m_pos.group(2).strip(), m_pos.group(3).strip()
            if not (planet.startswith('"') or planet.startswith("'") or planet.isidentifier()):
                planet = f'"{planet}"'
            return f"set {target} to astronomy_planet_position({planet}, {jd})"

        # predict eclipse at [jd] <jd> into <target>
        m_ecl = re.match(
            r"^predict\s+eclipse\s+at(?:\s+jd)?\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ecl:
            jd, target = m_ecl.group(1).strip(), m_ecl.group(2).strip()
            return f"set {target} to Record(astronomy_predict_eclipse({jd}))"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Astronomy domain does not define declarative blocks")
