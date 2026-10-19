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
