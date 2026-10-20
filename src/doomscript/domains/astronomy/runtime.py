"""Astronomy, Celestial Coordinate Systems, and Keplerian Astrodynamics for DoomScript."""

import math
from typing import List, Dict, Any, Tuple, Optional


G_CONST = 6.67430e-11  # m^3 kg^-1 s^-2
MU_EARTH = 3.986004418e14  # m^3 s^-2
MU_SUN = 1.32712440018e20  # m^3 s^-2


class CelestialTime:
    """Julian Date and Sidereal Time conversions."""

    @staticmethod
    def gregorian_to_jd(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: float = 0.0) -> float:
        """Convert Gregorian calendar date to Julian Date."""
        if month <= 2:
            year -= 1
            month += 12
        a = math.floor(year / 100.0)
        b = 2.0 - a + math.floor(a / 4.0)
        day_fraction = (hour + (minute + second / 60.0) / 60.0) / 24.0
        jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + day_fraction + b - 1524.5
        return float(jd)

    @staticmethod
    def jd_to_mjd(jd: float) -> float:
        """Convert Julian Date to Modified Julian Date."""
        return jd - 2400000.5

    @staticmethod
    def jd_to_gmst(jd: float) -> float:
        """Greenwich Mean Sidereal Time in hours [0, 24)."""
        d = jd - 2451545.0
        gmst = 18.697374558 + 24.06570982441908 * d
        return gmst % 24.0


class KeplerianOrbit:
    """Two-Body Problem and Kepler's Equation solver."""

    @staticmethod
    def solve_kepler(mean_anomaly_rad: float, eccentricity: float, tol: float = 1e-9, max_iter: int = 100) -> float:
        """Newton-Raphson solver for Kepler's Equation: M = E - e*sin(E)."""
        m = mean_anomaly_rad % (2.0 * math.pi)
        e = eccentricity
        # Initial guess
        E = m + e * math.sin(m) if e < 0.8 else math.pi
        for _ in range(max_iter):
            f = E - e * math.sin(E) - m
            f_prime = 1.0 - e * math.cos(E)
            delta = f / f_prime
            E -= delta
            if abs(delta) < tol:
                break
        return E

    @staticmethod
    def elements_to_cartesian(
        semi_major_axis_m: float,
        eccentricity: float,
        inclination_rad: float,
        raan_rad: float,
        arg_periapsis_rad: float,
        mean_anomaly_rad: float,
        mu: float = MU_EARTH,
    ) -> Dict[str, List[float]]:
        """Convert Keplerian orbital elements to 3D Cartesian position and velocity."""
        a = semi_major_axis_m
        e = eccentricity
        inc = inclination_rad
        raan = raan_rad
        arg_p = arg_periapsis_rad

        E = KeplerianOrbit.solve_kepler(mean_anomaly_rad, e)
        # True anomaly nu
        sin_nu = (math.sqrt(max(0.0, 1.0 - e * e)) * math.sin(E)) / (1.0 - e * math.cos(E))
        cos_nu = (math.cos(E) - e) / (1.0 - e * math.cos(E))
        nu = math.atan2(sin_nu, cos_nu)

        # Distance r
        r = a * (1.0 - e * math.cos(E))

        # Position in orbital plane
        x_orb = r * math.cos(nu)
        y_orb = r * math.sin(nu)

        # Velocity in orbital plane
        h = math.sqrt(mu * a * (1.0 - e * e))
        vx_orb = -(mu / h) * math.sin(nu)
        vy_orb = (mu / h) * (e + math.cos(nu))

        # 3D Euler rotation matrix from orbital plane to inertial frame
        # R = R_z(-raan) * R_x(-inc) * R_z(-arg_p)
        P11 = math.cos(raan) * math.cos(arg_p) - math.sin(raan) * math.sin(arg_p) * math.cos(inc)
        P12 = -math.cos(raan) * math.sin(arg_p) - math.sin(raan) * math.cos(arg_p) * math.cos(inc)
        P21 = math.sin(raan) * math.cos(arg_p) + math.cos(raan) * math.sin(arg_p) * math.cos(inc)
        P22 = -math.sin(raan) * math.sin(arg_p) + math.cos(raan) * math.cos(arg_p) * math.cos(inc)
        P31 = math.sin(arg_p) * math.sin(inc)
        P32 = math.cos(arg_p) * math.sin(inc)

        x = P11 * x_orb + P12 * y_orb
        y = P21 * x_orb + P22 * y_orb
        z = P31 * x_orb + P32 * y_orb

        vx = P11 * vx_orb + P12 * vy_orb
        vy = P21 * vx_orb + P22 * vy_orb
        vz = P31 * vx_orb + P32 * vy_orb

        return {
            "position": [x, y, z],
            "velocity": [vx, vy, vz],
            "true_anomaly_deg": math.degrees(nu),
            "distance_m": r,
        }


class CelestialCoordinates:
    """Equatorial and Horizontal Coordinate Transforms."""

    @staticmethod
    def equatorial_to_horizontal(ra_hours: float, dec_deg: float, lat_deg: float, lst_hours: float) -> Dict[str, float]:
        """Convert Right Ascension & Declination to Altitude and Azimuth."""
        # Local Hour Angle H = LST - RA
        H_hours = (lst_hours - ra_hours) % 24.0
        H_rad = math.radians(H_hours * 15.0)
        dec_rad = math.radians(dec_deg)
        lat_rad = math.radians(lat_deg)

        sin_alt = math.sin(dec_rad) * math.sin(lat_rad) + math.cos(dec_rad) * math.cos(lat_rad) * math.cos(H_rad)
        alt_rad = math.asin(max(-1.0, min(1.0, sin_alt)))

        cos_az = (math.sin(dec_rad) - math.sin(alt_rad) * math.sin(lat_rad)) / (math.cos(alt_rad) * math.cos(lat_rad))
        cos_az = max(-1.0, min(1.0, cos_az))
        az_rad = math.acos(cos_az)
        if math.sin(H_rad) > 0.0:
            az_rad = 2.0 * math.pi - az_rad

        return {
            "altitude_deg": math.degrees(alt_rad),
            "azimuth_deg": math.degrees(az_rad),
        }


class Astrodynamics:
    """Hohmann transfers and orbital delta-v."""

    @staticmethod
    def hohmann_transfer(r1_m: float, r2_m: float, mu: float = MU_EARTH) -> Dict[str, float]:
        """Calculate Hohmann transfer delta-v and time-of-flight between circular orbits."""
        v1 = math.sqrt(mu / r1_m)
        v2 = math.sqrt(mu / r2_m)
        a_trans = (r1_m + r2_m) / 2.0
        v_trans1 = math.sqrt(mu * (2.0 / r1_m - 1.0 / a_trans))
        v_trans2 = math.sqrt(mu * (2.0 / r2_m - 1.0 / a_trans))

        dv1 = abs(v_trans1 - v1)
        dv2 = abs(v2 - v_trans2)
        total_dv = dv1 + dv2
        time_of_flight_sec = math.pi * math.sqrt((a_trans ** 3) / mu)

        return {
            "delta_v1": dv1,
            "delta_v2": dv2,
            "total_delta_v": total_dv,
            "transfer_time_sec": time_of_flight_sec,
            "transfer_time_hours": time_of_flight_sec / 3600.0,
        }

    @staticmethod
    def orbital_period(semi_major_axis_m: float, mu: float = MU_EARTH) -> float:
        return 2.0 * math.pi * math.sqrt((semi_major_axis_m ** 3) / mu)


def astronomy_julian_date(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: float = 0.0) -> float:
    return CelestialTime.gregorian_to_jd(year, month, day, hour, minute, second)


def astronomy_kepler_orbit(a: float, e: float, inc_deg: float, raan_deg: float, arg_p_deg: float, m_deg: float) -> Dict[str, Any]:
    return KeplerianOrbit.elements_to_cartesian(
        a, e, math.radians(inc_deg), math.radians(raan_deg), math.radians(arg_p_deg), math.radians(m_deg)
    )


def astronomy_eq_to_horiz(ra_hours: float, dec_deg: float, lat_deg: float, lst_hours: float) -> Dict[str, float]:
    return CelestialCoordinates.equatorial_to_horizontal(ra_hours, dec_deg, lat_deg, lst_hours)


def astronomy_hohmann_transfer(r1: float, r2: float) -> Dict[str, float]:
    return Astrodynamics.hohmann_transfer(r1, r2)


# ==============================================================================
# Advanced Astronomy Deepening: Ephemerides, Eclipse Geometry & Refraction
# ==============================================================================

class PlanetaryEphemeris:
    """Semi-analytical Keplerian ephemeris for the 8 solar system planets referenced to J2000."""

    AU_TO_KM = 149597870.7
    AU_TO_M = 149597870700.0

    # Orbital elements at J2000.0 and secular rates per Julian century (T):
    # [a0, a_rate, e0, e_rate, I0, I_rate, L0, L_rate, w0, w_rate, O0, O_rate]
    # a in AU, e dimensionless, angles in degrees
    PLANET_DATA = {
        "mercury": (0.38709893, 0.00000066, 0.20563069, 0.00002527, 7.00487, -0.2454, 252.25084, 149472.67411, 77.45645, 1.55648, 48.33167, -0.44638),
        "venus":   (0.72333199, 0.00000092, 0.00677323, -0.00004938, 3.39471, -0.0435, 181.97973, 58517.81539, 131.57294, 1.40222, 76.68069, -0.77264),
        "earth":   (1.00000011, -0.00000005, 0.01671022, -0.00003804, 0.00005, -0.0129, 100.46435, 35999.37245, 102.94719, 1.19828, 174.873, -0.241),
        "mars":    (1.52366231, -0.00007221, 0.09341233, 0.00011902, 1.85061, -0.0664, 355.45332, 19140.30268, 336.04084, 1.84104, 49.57854, -1.02096),
        "jupiter": (5.20336301, 0.00060737, 0.04839266, -0.00012880, 1.30530, -0.0415, 34.40438, 3034.74612, 14.75385, 1.61933, 100.55615, 1.21172),
        "saturn":  (9.53707032, -0.00301530, 0.05415060, -0.00036762, 2.48446, 0.0165, 49.94432, 1222.49362, 92.43194, 1.95842, 113.71504, -0.79156),
        "uranus":  (19.19126393, 0.00152025, 0.04716771, -0.00019150, 0.76986, -0.0047, 313.23218, 428.48203, 170.96424, 1.31068, 74.22988, 0.07436),
        "neptune": (30.06896348, -0.00125196, 0.00858587, 0.00002514, 1.76917, -0.0051, 304.88003, 218.45945, 44.97135, -0.32241, 131.72169, -0.00599),
    }

    @classmethod
    def get_heliocentric_position(cls, planet: str, jd: float) -> Dict[str, Any]:
        """Calculates 3D heliocentric ecliptic coordinates (X, Y, Z in AU) for given JD."""
        key = planet.strip().lower()
        if key not in cls.PLANET_DATA:
            raise ValueError(f"Unknown planet '{planet}'. Available: {list(cls.PLANET_DATA.keys())}")

        d = cls.PLANET_DATA[key]
        T = (jd - 2451545.0) / 36525.0  # Julian centuries since J2000.0

        a = d[0] + d[1] * T
        e = d[2] + d[3] * T
        inc = math.radians(d[4] + d[5] * T)
        L = math.radians((d[6] + d[7] * T) % 360.0)
        varpi = math.radians((d[8] + d[9] * T) % 360.0)
        raan = math.radians((d[10] + d[11] * T) % 360.0)

        arg_p = varpi - raan
        M = (L - varpi) % (2.0 * math.pi)

        # Solve Kepler's equation
        E = KeplerianOrbit.solve_kepler(M, e)
        nu = 2.0 * math.atan2(math.sqrt(max(0.0, 1.0 + e)) * math.sin(E / 2.0), math.sqrt(max(0.0, 1.0 - e)) * math.cos(E / 2.0))
        r = a * (1.0 - e * math.cos(E))

        # Position in orbital plane
        x_orb = r * math.cos(nu)
        y_orb = r * math.sin(nu)

        # 3D ecliptic coords
        cos_o, sin_o = math.cos(raan), math.sin(raan)
        cos_w, sin_w = math.cos(arg_p), math.sin(arg_p)
        cos_i = math.cos(inc)

        P11 = cos_o * cos_w - sin_o * sin_w * cos_i
        P12 = -cos_o * sin_w - sin_o * cos_w * cos_i
        P21 = sin_o * cos_w + cos_o * sin_w * cos_i
        P22 = -sin_o * sin_w + cos_o * cos_w * cos_i
        P31 = sin_w * math.sin(inc)
        P32 = cos_w * math.sin(inc)

        x = P11 * x_orb + P12 * y_orb
        y = P21 * x_orb + P22 * y_orb
        z = P31 * x_orb + P32 * y_orb

        lon = math.degrees(math.atan2(y, x)) % 360.0
        lat = math.degrees(math.asin(max(-1.0, min(1.0, z / r))))

        return {
            "planet": key,
            "jd": jd,
            "x_au": round(x, 6),
            "y_au": round(y, 6),
            "z_au": round(z, 6),
            "radius_au": round(r, 6),
            "ecliptic_longitude_deg": round(lon, 4),
            "ecliptic_latitude_deg": round(lat, 4),
        }

    @classmethod
    def get_geocentric_position(cls, planet: str, jd: float) -> Dict[str, Any]:
        """Calculates Earth-centered coordinates, phase angle, and illumination."""
        key = planet.strip().lower()
        if key == "earth":
            return {"planet": "earth", "distance_au": 0.0, "elongation_deg": 0.0, "illuminated_fraction": 1.0}

        p_helio = cls.get_heliocentric_position(key, jd)
        e_helio = cls.get_heliocentric_position("earth", jd)

        dx = p_helio["x_au"] - e_helio["x_au"]
        dy = p_helio["y_au"] - e_helio["y_au"]
        dz = p_helio["z_au"] - e_helio["z_au"]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)

        # Sun-Planet-Earth angle (Phase Angle phi)
        # Using Law of Cosines: R_E^2 = R_P^2 + D^2 - 2 R_P D cos(phi)
        rp = p_helio["radius_au"]
        re = e_helio["radius_au"]
        cos_phi = (rp * rp + dist * dist - re * re) / (2.0 * rp * dist)
        cos_phi = max(-1.0, min(1.0, cos_phi))
        phi_rad = math.acos(cos_phi)

        illuminated = (1.0 + math.cos(phi_rad)) / 2.0

        return {
            "planet": key,
            "distance_au": round(dist, 6),
            "distance_km": round(dist * cls.AU_TO_KM, 1),
            "phase_angle_deg": round(math.degrees(phi_rad), 3),
            "illuminated_fraction": round(illuminated, 4),
        }


class EclipsePredictor:
    """Predicts solar and lunar eclipses from orbital alignments and node proximity."""

    SYNODIC_MONTH = 29.530588853
    DRACONIC_MONTH = 27.212220817
    J2000_JD = 2451545.0

    @classmethod
    def predict_eclipse_conditions(cls, jd: float) -> Dict[str, Any]:
        """
        Assesses eclipse possibility and type for a given Julian Date.
        """
        days_since_j2000 = jd - cls.J2000_JD

        # Mean Lunar Phase (0.0 = New Moon, 0.5 = Full Moon)
        phase = (days_since_j2000 / cls.SYNODIC_MONTH) % 1.0

        # Mean Node Proximity (0.0 or 0.5 = at orbital node)
        node_cycle = (days_since_j2000 / cls.DRACONIC_MONTH) % 1.0
        dist_to_node = min(node_cycle, abs(node_cycle - 0.5), abs(node_cycle - 1.0)) * 360.0

        # Ecliptic latitude of moon is approximately 5.145 * sin(node_angle)
        node_angle_rad = 2.0 * math.pi * node_cycle
        moon_beta_deg = abs(5.145 * math.sin(node_angle_rad))

        eclipse_type = "None"
        target = "None"
        magnitude = 0.0

        # Solar Eclipse occurs near New Moon (phase near 0.0 or 1.0)
        dist_to_new = min(phase, 1.0 - phase) * cls.SYNODIC_MONTH
        if dist_to_new < 1.2:
            target = "Solar"
            if moon_beta_deg < 0.99:
                if moon_beta_deg < 0.25:
                    eclipse_type = "Total or Annular Solar Eclipse"
                    magnitude = round(1.0 - moon_beta_deg / 0.5, 3)
                else:
                    eclipse_type = "Partial Solar Eclipse"
                    magnitude = round(max(0.1, 1.0 - moon_beta_deg / 1.5), 3)

        # Lunar Eclipse occurs near Full Moon (phase near 0.5)
        dist_to_full = abs(phase - 0.5) * cls.SYNODIC_MONTH
        if dist_to_full < 1.2:
            target = "Lunar"
            if moon_beta_deg < 1.5:
                if moon_beta_deg < 0.45:
                    eclipse_type = "Total Lunar Eclipse"
                    magnitude = round(1.0 + (0.45 - moon_beta_deg) / 0.45, 3)
                elif moon_beta_deg < 0.95:
                    eclipse_type = "Partial Lunar Eclipse"
                    magnitude = round((0.95 - moon_beta_deg) / 0.5, 3)
                else:
                    eclipse_type = "Penumbral Lunar Eclipse"
                    magnitude = round((1.5 - moon_beta_deg) / 0.55, 3)

        return {
            "jd": jd,
            "target": target,
            "eclipse_type": eclipse_type,
            "moon_phase": round(phase, 4),
            "lunar_ecliptic_latitude_deg": round(moon_beta_deg, 4),
            "magnitude": round(magnitude, 3),
        }


class AtmosphericRefraction:
    """Atmospheric refraction and optical airmass calculator."""

    @staticmethod
    def calculate_refraction(
        apparent_altitude_deg: float,
        temp_c: float = 10.0,
        pressure_mbar: float = 1013.25,
    ) -> Dict[str, float]:
        """
        Calculates atmospheric refraction correction using Saemundsson / Bennett formula.
        """
        ha = max(-2.0, min(90.0, float(apparent_altitude_deg)))

        # Standard refraction in arcminutes at 10 deg C and 1010 mbar via Bennett (1982)
        if ha < 0.0:
            r0_arcmin = 34.5
        else:
            r0_arcmin = 1.0 / math.tan(math.radians(ha + 7.31 / (ha + 4.4)))

        # Temperature and pressure scale factor
        f_tp = (pressure_mbar / 1010.0) * (283.15 / (273.15 + temp_c))
        refraction_arcmin = r0_arcmin * f_tp
        refraction_deg = refraction_arcmin / 60.0

        true_altitude_deg = ha - refraction_deg

        # Optical Airmass (Kasten-Young formula)
        h_eval = max(0.1, true_altitude_deg)
        airmass = 1.0 / (math.sin(math.radians(h_eval)) + 0.50572 * ((h_eval + 6.07995) ** -1.6364))

        return {
            "apparent_altitude_deg": round(ha, 4),
            "true_altitude_deg": round(true_altitude_deg, 4),
            "refraction_arcmin": round(refraction_arcmin, 4),
            "refraction_deg": round(refraction_deg, 6),
            "airmass": round(airmass, 4),
        }


def astronomy_planet_position(planet: str, jd: float) -> Dict[str, Any]:
    """Calculates heliocentric coordinates for a planet at JD."""
    return PlanetaryEphemeris.get_heliocentric_position(planet, jd)


def astronomy_planet_geocentric(planet: str, jd: float) -> Dict[str, Any]:
    """Calculates geocentric distance, phase angle, and illumination."""
    return PlanetaryEphemeris.get_geocentric_position(planet, jd)


def astronomy_predict_eclipse(jd: float) -> Dict[str, Any]:
    """Assesses eclipse conditions and type for a given date."""
    return EclipsePredictor.predict_eclipse_conditions(jd)


def astronomy_atmospheric_refraction(apparent_alt_deg: float, temp_c: float = 10.0, pressure_mbar: float = 1013.25) -> Dict[str, float]:
    """Calculates apparent to true altitude refraction correction and airmass."""
    return AtmosphericRefraction.calculate_refraction(apparent_alt_deg, temp_c, pressure_mbar)
