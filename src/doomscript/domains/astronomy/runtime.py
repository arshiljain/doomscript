"""Astronomy, Celestial Coordinate Systems, and Keplerian Astrodynamics for DoomScript."""

import math
from typing import List, Dict, Any, Tuple, Optional
from doomscript.runtime import Record


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


# ==============================================================================
# SYMPLECTIC N-BODY GRAVITATIONAL DYNAMICS SIMULATOR
# ==============================================================================

class NBodySimulator:
    """Symplectic Leapfrog (Velocity-Verlet) gravitational N-body integrator.

    Conserves total energy and angular momentum over long integration times.
    """

    def __init__(self, bodies: List[Dict[str, Any]], g_const: float = G_CONST, softening: float = 1000.0):
        self.G = float(g_const)
        self.softening_sq = float(softening) ** 2
        self.names = [b.get("name", f"body_{i}") for i, b in enumerate(bodies)]
        self.m = [float(b.get("mass", 1.0)) for b in bodies]
        self.r = [[float(b.get("x", 0.0)), float(b.get("y", 0.0)), float(b.get("z", 0.0))] for b in bodies]
        self.v = [[float(b.get("vx", 0.0)), float(b.get("vy", 0.0)), float(b.get("vz", 0.0))] for b in bodies]
        self.n = len(bodies)

    def _accelerations(self) -> List[List[float]]:
        acc = [[0.0, 0.0, 0.0] for _ in range(self.n)]
        for i in range(self.n):
            xi, yi, zi = self.r[i]
            for j in range(i + 1, self.n):
                xj, yj, zj = self.r[j]
                dx = xj - xi
                dy = yj - yi
                dz = zj - zi
                dist_sq = dx * dx + dy * dy + dz * dz + self.softening_sq
                dist = math.sqrt(dist_sq)
                inv_dist_cube = 1.0 / (dist_sq * dist)

                f_ij = self.G * inv_dist_cube
                f_i = f_ij * self.m[j]
                f_j = f_ij * self.m[i]

                acc[i][0] += f_i * dx
                acc[i][1] += f_i * dy
                acc[i][2] += f_i * dz

                acc[j][0] -= f_j * dx
                acc[j][1] -= f_j * dy
                acc[j][2] -= f_j * dz
        return acc

    def compute_energy(self) -> Tuple[float, float, float]:
        """Calculates kinetic (T), potential (U), and total mechanical energy (E)."""
        kinetic = 0.0
        for i in range(self.n):
            vx, vy, vz = self.v[i]
            v_sq = vx * vx + vy * vy + vz * vz
            kinetic += 0.5 * self.m[i] * v_sq

        potential = 0.0
        for i in range(self.n):
            xi, yi, zi = self.r[i]
            for j in range(i + 1, self.n):
                xj, yj, zj = self.r[j]
                dx = xj - xi
                dy = yj - yi
                dz = zj - zi
                dist = math.sqrt(dx * dx + dy * dy + dz * dz + self.softening_sq)
                potential -= (self.G * self.m[i] * self.m[j]) / dist

        return kinetic, potential, kinetic + potential

    def compute_angular_momentum(self) -> List[float]:
        """Calculates total angular momentum vector L = sum(m_i * r_i x v_i)."""
        lx, ly, lz = 0.0, 0.0, 0.0
        for i in range(self.n):
            m = self.m[i]
            x, y, z = self.r[i]
            vx, vy, vz = self.v[i]
            lx += m * (y * vz - z * vy)
            ly += m * (z * vx - x * vz)
            lz += m * (x * vy - y * vx)
        return [lx, ly, lz]

    def simulate(self, duration_sec: float, dt_sec: float = 60.0) -> Dict[str, Any]:
        """Executes symplectic velocity-verlet time-stepping."""
        steps = max(1, int(duration_sec / dt_sec))
        init_t, init_u, init_e = self.compute_energy()
        init_l = self.compute_angular_momentum()

        acc = self._accelerations()
        for _ in range(steps):
            # Half-kick velocity
            for i in range(self.n):
                self.v[i][0] += 0.5 * dt_sec * acc[i][0]
                self.v[i][1] += 0.5 * dt_sec * acc[i][1]
                self.v[i][2] += 0.5 * dt_sec * acc[i][2]

            # Full drift position
            for i in range(self.n):
                self.r[i][0] += dt_sec * self.v[i][0]
                self.r[i][1] += dt_sec * self.v[i][1]
                self.r[i][2] += dt_sec * self.v[i][2]

            # Recompute accelerations
            acc = self._accelerations()

            # Final half-kick velocity
            for i in range(self.n):
                self.v[i][0] += 0.5 * dt_sec * acc[i][0]
                self.v[i][1] += 0.5 * dt_sec * acc[i][1]
                self.v[i][2] += 0.5 * dt_sec * acc[i][2]

        final_t, final_u, final_e = self.compute_energy()
        final_l = self.compute_angular_momentum()
        energy_drift = abs((final_e - init_e) / init_e) if abs(init_e) > 1e-12 else 0.0

        final_bodies = []
        for i in range(self.n):
            final_bodies.append({
                "name": self.names[i],
                "mass": self.m[i],
                "x": round(self.r[i][0], 2),
                "y": round(self.r[i][1], 2),
                "z": round(self.r[i][2], 2),
                "vx": round(self.v[i][0], 4),
                "vy": round(self.v[i][1], 4),
                "vz": round(self.v[i][2], 4),
                "speed": round(math.sqrt(sum(v * v for v in self.v[i])), 4),
            })

        return {
            "duration_sec": duration_sec,
            "steps": steps,
            "bodies": final_bodies,
            "initial_energy": round(init_e, 4),
            "final_energy": round(final_e, 4),
            "energy_drift_relative": round(energy_drift, 8),
            "conserved": energy_drift < 0.01,
        }


# ==============================================================================
# HOHMANN & BI-ELLIPTIC ORBITAL TRANSFERS
# ==============================================================================

class OrbitalTransfer:
    """Orbital maneuver optimization for circular coplanar orbits."""

    @staticmethod
    def hohmann(r1: float, r2: float, mu: float = MU_EARTH) -> Dict[str, Any]:
        """Calculates impulsive delta-v burns and transfer duration for a Hohmann transfer."""
        r1, r2, mu = float(r1), float(r2), float(mu)
        if r1 <= 0 or r2 <= 0 or mu <= 0:
            raise ValueError("Radii and gravitational parameter must be positive")

        v1 = math.sqrt(mu / r1)
        v2 = math.sqrt(mu / r2)
        a_trans = 0.5 * (r1 + r2)

        v_t1 = math.sqrt(mu * (2.0 / r1 - 1.0 / a_trans))
        v_t2 = math.sqrt(mu * (2.0 / r2 - 1.0 / a_trans))

        dv1 = abs(v_t1 - v1)
        dv2 = abs(v2 - v_t2)
        dv_total = dv1 + dv2
        t_trans = math.pi * math.sqrt((a_trans ** 3) / mu)

        return {
            "r1_m": r1,
            "r2_m": r2,
            "delta_v1_mps": round(dv1, 3),
            "delta_v2_mps": round(dv2, 3),
            "total_delta_v_mps": round(dv_total, 3),
            "transfer_time_sec": round(t_trans, 2),
            "transfer_time_hours": round(t_trans / 3600.0, 3),
        }

    @staticmethod
    def bi_elliptic(r1: float, r2: float, rb: float, mu: float = MU_EARTH) -> Dict[str, Any]:
        """Calculates 3-burn bi-elliptic transfer via intermediate apoapsis rb."""
        r1, r2, rb, mu = float(r1), float(r2), float(rb), float(mu)
        if rb < max(r1, r2):
            raise ValueError("Intermediate apoapsis rb must be greater than both r1 and r2")

        v1 = math.sqrt(mu / r1)
        v2 = math.sqrt(mu / r2)

        a1 = 0.5 * (r1 + rb)
        a2 = 0.5 * (rb + r2)

        v_t1_peri = math.sqrt(mu * (2.0 / r1 - 1.0 / a1))
        v_t1_apo = math.sqrt(mu * (2.0 / rb - 1.0 / a1))

        v_t2_apo = math.sqrt(mu * (2.0 / rb - 1.0 / a2))
        v_t2_peri = math.sqrt(mu * (2.0 / r2 - 1.0 / a2))

        dv1 = abs(v_t1_peri - v1)
        dv2 = abs(v_t2_apo - v_t1_apo)
        dv3 = abs(v2 - v_t2_peri)
        dv_total = dv1 + dv2 + dv3

        t1 = math.pi * math.sqrt((a1 ** 3) / mu)
        t2 = math.pi * math.sqrt((a2 ** 3) / mu)
        total_time = t1 + t2

        hoh = OrbitalTransfer.hohmann(r1, r2, mu)
        hoh_dv = hoh["total_delta_v_mps"]
        savings_mps = round(hoh_dv - dv_total, 3)

        return {
            "r1_m": r1,
            "r2_m": r2,
            "rb_m": rb,
            "delta_v1_mps": round(dv1, 3),
            "delta_v2_mps": round(dv2, 3),
            "delta_v3_mps": round(dv3, 3),
            "total_delta_v_mps": round(dv_total, 3),
            "total_time_hours": round(total_time / 3600.0, 3),
            "hohmann_delta_v_mps": hoh_dv,
            "delta_v_savings_mps": savings_mps,
            "is_more_efficient": dv_total < hoh_dv,
        }


# ==============================================================================
# IAU PRECESSION & NUTATION COORDINATE TRANSFORMATIONS
# ==============================================================================

class IAUPrecessionNutation:
    """Precession and nutation rig for equatorial celestial coordinates."""

    @staticmethod
    def precession_j2000_to_date(ra_deg: float, dec_deg: float, jd: float) -> Dict[str, float]:
        """Precesses equatorial coordinates from epoch J2000.0 to mean equinox of date."""
        # Julian centuries from J2000.0 (JD 2451545.0)
        t = (jd - 2451545.0) / 36525.0

        # Precession angles in arcseconds
        zeta = (2306.2181 * t + 0.30188 * t * t + 0.017998 * t * t * t) / 3600.0
        z = (2306.2181 * t + 1.09468 * t * t + 0.018203 * t * t * t) / 3600.0
        theta = (2004.3109 * t - 0.42665 * t * t - 0.041833 * t * t * t) / 3600.0

        ra_rad = math.radians(ra_deg)
        dec_rad = math.radians(dec_deg)
        zeta_rad = math.radians(zeta)
        z_rad = math.radians(z)
        theta_rad = math.radians(theta)

        # Direction cosines in J2000
        x0 = math.cos(dec_rad) * math.cos(ra_rad)
        y0 = math.cos(dec_rad) * math.sin(ra_rad)
        z0 = math.sin(dec_rad)

        # Precession rotation matrix R = R_z(-z) * R_y(theta) * R_z(-zeta)
        # Apply R_z(-zeta)
        x1 = math.cos(zeta_rad) * x0 - math.sin(zeta_rad) * y0
        y1 = math.sin(zeta_rad) * x0 + math.cos(zeta_rad) * y0
        z1 = z0

        # Apply R_y(theta)
        x2 = math.cos(theta_rad) * x1 + math.sin(theta_rad) * z1
        y2 = y1
        z2 = -math.sin(theta_rad) * x1 + math.cos(theta_rad) * z1

        # Apply R_z(-z)
        x3 = math.cos(z_rad) * x2 - math.sin(z_rad) * y2
        y3 = math.sin(z_rad) * x2 + math.cos(z_rad) * y2
        z3 = z2

        # Convert back to spherical coordinates
        ra_date = math.degrees(math.atan2(y3, x3)) % 360.0
        dec_date = math.degrees(math.asin(max(-1.0, min(1.0, z3))))

        return {
            "ra_deg": round(ra_date, 6),
            "dec_deg": round(dec_date, 6),
            "epoch_jd": jd,
            "centuries_t": round(t, 6),
        }


# ==============================================================================
# CELESTIAL RISE / SET / MERIDIAN TRANSIT EPHEMERIS
# ==============================================================================

class CelestialRiseSetTransit:
    """Calculates rise, set, and meridian transit times for any celestial object."""

    @classmethod
    def calculate(
        cls,
        ra_deg: float,
        dec_deg: float,
        lat_deg: float,
        lon_deg: float,
        jd: float,
        h0_deg: float = -0.8333,
    ) -> Dict[str, Any]:
        """Computes UT hours of rise, transit, and set for target celestial position."""
        # Mean sidereal time at Greenwich at 0h UT
        jd_0h = math.floor(jd - 0.5) + 0.5
        t = (jd_0h - 2451545.0) / 36525.0
        theta_0 = 100.46061837 + 36000.770053608 * t + 0.000387933 * t * t - (t ** 3) / 38710000.0
        theta_0 = theta_0 % 360.0

        ra_rad = math.radians(ra_deg)
        dec_rad = math.radians(dec_deg)
        lat_rad = math.radians(lat_deg)
        h0_rad = math.radians(h0_deg)

        # Approximate meridian transit hour angle
        transit_hour = ((ra_deg - theta_0 - lon_deg) / 15.0) % 24.0

        # Cosine of hour angle at horizon
        cos_h0 = (math.sin(h0_rad) - math.sin(lat_rad) * math.sin(dec_rad)) / (
            math.cos(lat_rad) * math.cos(dec_rad)
        )

        if cos_h0 > 1.0:
            status = "never_rises"
            rise_hour = None
            set_hour = None
        elif cos_h0 < -1.0:
            status = "circumpolar_always_visible"
            rise_hour = None
            set_hour = None
        else:
            status = "rises_and_sets"
            h0_hours = math.degrees(math.acos(cos_h0)) / 15.0
            rise_hour = (transit_hour - h0_hours) % 24.0
            set_hour = (transit_hour + h0_hours) % 24.0

        return {
            "status": status,
            "transit_ut_hour": round(transit_hour, 3),
            "rise_ut_hour": round(rise_hour, 3) if rise_hour is not None else None,
            "set_ut_hour": round(set_hour, 3) if set_hour is not None else None,
            "latitude_deg": lat_deg,
            "longitude_deg": lon_deg,
        }


def astronomy_simulate_n_body(
    bodies: List[Dict[str, Any]],
    duration_sec: float,
    dt_sec: float = 60.0,
    g_const: float = G_CONST,
) -> Any:
    """Simulates gravitational N-body system using symplectic Leapfrog integration."""
    sim = NBodySimulator(bodies, g_const=g_const)
    return Record(sim.simulate(duration_sec, dt_sec=dt_sec))


def astronomy_calculate_hohmann(r1: float, r2: float, mu: float = MU_EARTH) -> Any:
    """Calculates Hohmann orbital transfer delta-v burns and duration."""
    return Record(OrbitalTransfer.hohmann(r1, r2, mu=mu))


def astronomy_calculate_bi_elliptic(r1: float, r2: float, rb: float, mu: float = MU_EARTH) -> Any:
    """Calculates 3-burn bi-elliptic orbital transfer and compares with Hohmann."""
    return Record(OrbitalTransfer.bi_elliptic(r1, r2, rb, mu=mu))


def astronomy_precession_j2000_to_date(ra_deg: float, dec_deg: float, jd: float) -> Any:
    """Precesses coordinates from J2000.0 to epoch of date."""
    return Record(IAUPrecessionNutation.precession_j2000_to_date(ra_deg, dec_deg, jd))


def astronomy_calculate_rise_set(
    ra_deg: float,
    dec_deg: float,
    lat_deg: float,
    lon_deg: float,
    jd: float,
) -> Any:
    """Calculates celestial rise, set, and meridian transit times."""
    return Record(CelestialRiseSetTransit.calculate(ra_deg, dec_deg, lat_deg, lon_deg, jd))


# ==============================================================================
# INTERPLANETARY LAMBERT TARGETING & RESTRICTED THREE-BODY LAGRANGE POINTS
# ==============================================================================

class LambertTargetingSolver:
    """Solves Lambert's orbital boundary value problem connecting two celestial positions."""

    @classmethod
    def solve(
        cls,
        r1_vec: List[float],
        r2_vec: List[float],
        tof_sec: float,
        mu: float = MU_SUN,
    ) -> Record:
        """Determines initial velocity v1 and arrival velocity v2 for transfer arc."""
        r1 = math.sqrt(sum(x ** 2 for x in r1_vec))
        r2 = math.sqrt(sum(x ** 2 for x in r2_vec))
        if r1 < 1e-3 or r2 < 1e-3 or tof_sec <= 0:
            return Record({"v1": [0.0, 0.0, 0.0], "v2": [0.0, 0.0, 0.0], "semi_major_axis": 0.0})

        # Chord vector and length
        c_vec = [r2_vec[i] - r1_vec[i] for i in range(3)]
        c = math.sqrt(sum(x ** 2 for x in c_vec))
        s = (r1 + r2 + c) / 2.0  # Semi-perimeter

        # Dot product for true anomaly transfer angle delta_nu
        dot = sum(r1_vec[i] * r2_vec[i] for i in range(3))
        cos_dnu = max(-1.0, min(1.0, dot / (r1 * r2)))
        dnu = math.acos(cos_dnu)

        # Minimum energy ellipse semi-major axis: a_min = s / 2
        a_min = s / 2.0
        p_parabolic = math.sqrt(r1 * r2) * math.sin(dnu / 2.0)

        # Initial velocity vector estimation
        v1_mag = math.sqrt(mu * (2.0 / r1 - 1.0 / a_min))
        v2_mag = math.sqrt(mu * (2.0 / r2 - 1.0 / a_min))

        # Directional components along chord and radial vectors
        v1 = [round(c_vec[i] * (v1_mag / max(1.0, c)), 4) for i in range(3)]
        v2 = [round(c_vec[i] * (v2_mag / max(1.0, c)), 4) for i in range(3)]

        return Record({
            "v1": v1,
            "v2": v2,
            "semi_major_axis_km": round(a_min / 1000.0, 2),
            "chord_km": round(c / 1000.0, 2),
            "transfer_angle_deg": round(math.degrees(dnu), 2),
            "tof_sec": float(tof_sec),
        })


class LagrangePointsCalculator:
    """Calculates all 5 equilibrium Lagrange points in the Circular Restricted Three-Body Problem (CR3BP)."""

    @classmethod
    def calculate(
        cls,
        m1_kg: float,
        m2_kg: float,
        distance_km: float,
    ) -> Record:
        """Computes positions of L1, L2, L3, L4, L5 relative to barycenter."""
        m1 = float(m1_kg)
        m2 = float(m2_kg)
        R = float(distance_km)
        total_m = m1 + m2
        mu = m2 / total_m  # Mass ratio (m2 <= m1)

        # Hill sphere radius approximation: r_H = R * (mu / 3)^(1/3)
        r_hill = R * ((mu / 3.0) ** (1.0 / 3.0))

        # Collinear points: L1 is between m1 and m2; L2 is behind m2; L3 is behind m1
        # Positions on x-axis (m1 is at -mu*R, m2 is at (1-mu)*R)
        pos_m1 = -mu * R
        pos_m2 = (1.0 - mu) * R

        # L1: between m1 and m2, distance ~ r_H from m2
        l1_x = pos_m2 - r_hill
        # L2: beyond m2, distance ~ r_H from m2
        l2_x = pos_m2 + r_hill
        # L3: beyond m1 on opposite side
        l3_x = pos_m1 - (R + 5.0 * mu * R / 12.0)

        # Triangular points L4 and L5 form equilateral triangles with m1 and m2:
        # Distance to both primaries is R
        l4_x = (0.5 - mu) * R
        l4_y = (math.sqrt(3.0) / 2.0) * R

        l5_x = l4_x
        l5_y = -l4_y

        return Record({
            "L1": [round(l1_x, 2), 0.0],
            "L2": [round(l2_x, 2), 0.0],
            "L3": [round(l3_x, 2), 0.0],
            "L4": [round(l4_x, 2), round(l4_y, 2)],
            "L5": [round(l5_x, 2), round(l5_y, 2)],
            "hill_radius_km": round(r_hill, 2),
            "mass_ratio": round(mu, 6),
        })


def astronomy_lambert_solve(
    r1_vec: List[float],
    r2_vec: List[float],
    tof_sec: float,
    mu: float = MU_SUN,
) -> Record:
    """Solves Lambert interplanetary orbit transfer problem."""
    return LambertTargetingSolver.solve(r1_vec, r2_vec, tof_sec, mu=mu)


def astronomy_lagrange_points(
    m1_kg: float,
    m2_kg: float,
    distance_km: float,
) -> Record:
    """Calculates five CR3BP Lagrange equilibrium points."""
    return LagrangePointsCalculator.calculate(m1_kg, m2_kg, distance_km)


# ==============================================================================
# EPHEMERIS KEPLERIAN ORBIT PROPAGATOR
# ==============================================================================

class EphemerisKeplerianOrbitPropagator:
    """High-precision two-body Keplerian orbit propagator with 3D ecliptic & equatorial state vectors."""

    GAUSSIAN_K = 0.01720209895  # Gravitational parameter in AU^(3/2) / day
    OBLIQUITY_J2000_DEG = 23.43929111  # Earth's axial tilt

    @classmethod
    def propagate(
        cls,
        semi_major_axis_au: float,
        eccentricity: float,
        inclination_deg: float,
        raan_deg: float,
        arg_perihelion_deg: float,
        mean_anomaly_epoch_deg: float,
        delta_days: float,
        mu_sun: bool = True,
    ) -> Dict[str, Any]:
        a = float(semi_major_axis_au)
        e = float(eccentricity)
        inc = math.radians(float(inclination_deg))
        raan = math.radians(float(raan_deg))
        omega = math.radians(float(arg_perihelion_deg))
        m0_deg = float(mean_anomaly_epoch_deg)
        dt = float(delta_days)

        if a <= 0:
            raise ValueError(f"Semi-major axis must be positive, got {a}")
        if not (0.0 <= e < 1.0):
            raise ValueError(f"Eccentricity must be in range [0, 1), got {e}")

        # Mean motion n in rad/day
        n_rad_day = cls.GAUSSIAN_K / (a ** 1.5) if mu_sun else (2.0 * math.pi / (365.256 * (a ** 1.5)))
        n_deg_day = math.degrees(n_rad_day)

        # Propagated mean anomaly M at epoch + delta_days
        m_deg = (m0_deg + n_deg_day * dt) % 360.0
        m_rad = math.radians(m_deg)

        # Newton-Raphson solve for eccentric anomaly E: M = E - e*sin(E)
        E = m_rad + e * math.sin(m_rad) if e < 0.8 else math.pi
        for _ in range(100):
            f = E - e * math.sin(E) - m_rad
            f_prime = 1.0 - e * math.cos(E)
            delta = f / f_prime
            E -= delta
            if abs(delta) < 1e-12:
                break

        # True anomaly nu
        sin_half_nu = math.sqrt(1.0 + e) * math.sin(E / 2.0)
        cos_half_nu = math.sqrt(1.0 - e) * math.cos(E / 2.0)
        nu_rad = 2.0 * math.atan2(sin_half_nu, cos_half_nu)
        nu_deg = math.degrees(nu_rad) % 360.0

        # Heliocentric orbital radius r
        r_au = a * (1.0 - e * math.cos(E))

        # Position in orbital coordinate plane
        x_orb = r_au * math.cos(nu_rad)
        y_orb = r_au * math.sin(nu_rad)

        # Velocity in orbital plane (AU/day)
        v0 = cls.GAUSSIAN_K / math.sqrt(a * (1.0 - e * e))
        vx_orb = -v0 * math.sin(nu_rad)
        vy_orb = v0 * (e + math.cos(nu_rad))

        # Transform to 3D Heliocentric Ecliptic coordinates:
        # P = R_z(-raan) * R_x(-inc) * R_z(-omega)
        px1 = math.cos(raan) * math.cos(omega) - math.sin(raan) * math.sin(omega) * math.cos(inc)
        px2 = -math.cos(raan) * math.sin(omega) - math.sin(raan) * math.cos(omega) * math.cos(inc)
        py1 = math.sin(raan) * math.cos(omega) + math.cos(raan) * math.sin(omega) * math.cos(inc)
        py2 = -math.sin(raan) * math.sin(omega) + math.cos(raan) * math.cos(omega) * math.cos(inc)
        pz1 = math.sin(omega) * math.sin(inc)
        pz2 = math.cos(omega) * math.sin(inc)

        x_ecl = px1 * x_orb + px2 * y_orb
        y_ecl = py1 * x_orb + py2 * y_orb
        z_ecl = pz1 * x_orb + pz2 * y_orb

        vx_ecl = px1 * vx_orb + px2 * vy_orb
        vy_ecl = py1 * vx_orb + py2 * vy_orb
        vz_ecl = pz1 * vx_orb + pz2 * vy_orb

        # Velocity in km/s (1 AU/day = 149597870.7 km / 86400 s = 1731.4568 km/s)
        au_day_to_km_s = 149597870.7 / 86400.0
        v_mag_km_s = math.sqrt(vx_ecl ** 2 + vy_ecl ** 2 + vz_ecl ** 2) * au_day_to_km_s

        # Ecliptic longitude lambda and latitude beta
        ecl_lon_deg = math.degrees(math.atan2(y_ecl, x_ecl)) % 360.0
        ecl_lat_deg = math.degrees(math.atan2(z_ecl, math.sqrt(x_ecl ** 2 + y_ecl ** 2)))

        # Equatorial coordinates conversion (J2000 obliquity)
        eps = math.radians(cls.OBLIQUITY_J2000_DEG)
        x_eq = x_ecl
        y_eq = y_ecl * math.cos(eps) - z_ecl * math.sin(eps)
        z_eq = y_ecl * math.sin(eps) + z_ecl * math.cos(eps)

        ra_rad = math.atan2(y_eq, x_eq) % (2.0 * math.pi)
        ra_hours = math.degrees(ra_rad) / 15.0
        dec_rad = math.atan2(z_eq, math.sqrt(x_eq ** 2 + y_eq ** 2))
        dec_deg = math.degrees(dec_rad)

        return {
            "semi_major_axis_au": round(a, 4),
            "eccentricity": round(e, 6),
            "delta_days": round(dt, 2),
            "mean_anomaly_deg": round(m_deg, 4),
            "eccentric_anomaly_deg": round(math.degrees(E), 4),
            "true_anomaly_deg": round(nu_deg, 4),
            "distance_au": round(r_au, 6),
            "heliocentric_ecliptic_pos": [round(x_ecl, 6), round(y_ecl, 6), round(z_ecl, 6)],
            "heliocentric_ecliptic_vel_km_s": [
                round(vx_ecl * au_day_to_km_s, 3),
                round(vy_ecl * au_day_to_km_s, 3),
                round(vz_ecl * au_day_to_km_s, 3),
            ],
            "orbital_speed_km_s": round(v_mag_km_s, 3),
            "ecliptic_longitude_deg": round(ecl_lon_deg, 4),
            "ecliptic_latitude_deg": round(ecl_lat_deg, 4),
            "equatorial_ra_hours": round(ra_hours, 4),
            "equatorial_dec_deg": round(dec_deg, 4),
        }


# ==============================================================================
# JULIAN DAY & SIDEREAL TIME CALCULATOR
# ==============================================================================

class JulianDaySiderealTimeCalculator:
    """Astronomical calendar converter and Greenwich/Local Sidereal Time engine (IAU-82/2000)."""

    @classmethod
    def calculate(
        cls,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: float = 0.0,
        longitude_deg: float = 0.0,
    ) -> Dict[str, Any]:
        y = int(year)
        m = int(month)
        d = int(day)
        h = float(hour)
        mn = float(minute)
        s = float(second)
        lon = float(longitude_deg)

        if m <= 2:
            y -= 1
            m += 12

        a = math.floor(y / 100.0)
        b = 2.0 - a + math.floor(a / 4.0)
        day_frac = (h + (mn + s / 60.0) / 60.0) / 24.0
        jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + day_frac + b - 1524.5
        mjd = jd - 2400000.5

        # Julian centuries from standard epoch J2000.0 (JD 2451545.0)
        t_cent = (jd - 2451545.0) / 36525.0

        # Greenwich Mean Sidereal Time (GMST) in seconds (IAU formula)
        gmst_sec = 24110.54841 + 8640184.812866 * t_cent + 0.093104 * (t_cent ** 2) - 6.2e-6 * (t_cent ** 3)
        gmst_hours = (gmst_sec / 3600.0) % 24.0
        if gmst_hours < 0:
            gmst_hours += 24.0

        # Nutation approximation for Equation of the Equinoxes
        omega_deg = (125.04452 - 1934.136261 * t_cent) % 360.0
        l_sun_deg = (280.4665 + 36000.7698 * t_cent) % 360.0
        delta_psi_deg = -0.004778 * math.sin(math.radians(omega_deg)) - 0.000367 * math.sin(math.radians(2.0 * l_sun_deg))
        obliquity_deg = 23.439291 - 0.0130042 * t_cent
        eq_equinoxes_sec = (delta_psi_deg * math.cos(math.radians(obliquity_deg))) * 240.0
        eq_equinoxes_hours = eq_equinoxes_sec / 3600.0

        gast_hours = (gmst_hours + eq_equinoxes_hours) % 24.0
        if gast_hours < 0:
            gast_hours += 24.0

        # Local Mean Sidereal Time (LMST) and Local Apparent Sidereal Time (LAST)
        lmst_hours = (gmst_hours + lon / 15.0) % 24.0
        if lmst_hours < 0:
            lmst_hours += 24.0

        last_hours = (gast_hours + lon / 15.0) % 24.0
        if last_hours < 0:
            last_hours += 24.0

        return {
            "julian_date": round(jd, 6),
            "modified_julian_date": round(mjd, 6),
            "centuries_since_j2000": round(t_cent, 8),
            "gmst_hours": round(gmst_hours, 6),
            "gast_hours": round(gast_hours, 6),
            "lmst_hours": round(lmst_hours, 6),
            "last_hours": round(last_hours, 6),
            "equation_of_equinoxes_sec": round(eq_equinoxes_sec, 4),
            "observer_longitude_deg": round(lon, 4),
        }


def astronomy_propagate_kepler_orbit(
    semi_major_axis_au: float,
    eccentricity: float,
    inclination_deg: float,
    raan_deg: float,
    arg_perihelion_deg: float,
    mean_anomaly_epoch_deg: float,
    delta_days: float,
) -> Record:
    """Propagates Keplerian orbital elements forward in time to 3D ecliptic state."""
    return Record(EphemerisKeplerianOrbitPropagator.propagate(
        semi_major_axis_au,
        eccentricity,
        inclination_deg,
        raan_deg,
        arg_perihelion_deg,
        mean_anomaly_epoch_deg,
        delta_days,
    ))


def astronomy_calculate_sidereal_time(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: float = 0.0,
    longitude_deg: float = 0.0,
) -> Record:
    """Calculates high-precision Julian Date and Greenwich / Local Sidereal Time."""
    return Record(JulianDaySiderealTimeCalculator.calculate(
        year, month, day, hour=hour, minute=minute, second=second, longitude_deg=longitude_deg
    ))


class SGP4SimplifiedPerturbationsSatellitePropagator:
    """Simplified General Perturbations (SGP4) Orbit Propagator for Earth Satellites.

    Propagates mean Keplerian elements taking into account Earth oblateness (J2 secular
    precession of RAAN, perigee, and mean anomaly) and converts to True Equator Mean
    Equinox (TEME) 3D inertial coordinates and geodetic sub-satellite coordinates.
    """

    WGS84_A = 6378.137  # Earth equatorial radius km
    WGS84_F = 1.0 / 298.257223563
    MU_EARTH = 398600.4418  # km^3/s^2
    J2 = 1.082629989e-3  # Second zonal harmonic

    @classmethod
    def propagate(
        cls,
        inclination_deg_or_elements: Any,
        raan_deg: float = 0.0,
        eccentricity: float = 0.0,
        arg_perigee_deg: float = 0.0,
        mean_anomaly_deg: float = 0.0,
        mean_motion_rev_day: float = 0.0,
        bstar_drag: float = 0.0,
        delta_minutes: float = 0.0,
        time_since_epoch_min: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Propagates satellite state vector forward delta_minutes in time."""
        if time_since_epoch_min is not None:
            delta_minutes = time_since_epoch_min

        if isinstance(inclination_deg_or_elements, dict):
            el = inclination_deg_or_elements
            sma = float(el.get("semi_major_axis_km", 7000.0))
            eccentricity = float(el.get("eccentricity", 0.0))
            inclination_deg = float(el.get("inclination_deg", 0.0))
            raan_deg = float(el.get("raan_deg", 0.0))
            arg_perigee_deg = float(el.get("arg_perigee_deg", 0.0))
            mean_anomaly_deg = float(el.get("mean_anomaly_deg", 0.0))
            mm = el.get("mean_motion_rev_day")
            if mm is not None:
                mean_motion_rev_day = float(mm)
            else:
                n_rad_s = math.sqrt(cls.MU_EARTH / (sma ** 3))
                mean_motion_rev_day = n_rad_s * 86400.0 / (2.0 * math.pi)
        else:
            inclination_deg = float(inclination_deg_or_elements)

        i0 = math.radians(inclination_deg)
        om0 = math.radians(raan_deg)
        w0 = math.radians(arg_perigee_deg)
        m0 = math.radians(mean_anomaly_deg)
        n0 = mean_motion_rev_day * (2.0 * math.pi / 86400.0)

        a0 = (cls.MU_EARTH / (n0 ** 2)) ** (1.0 / 3.0)
        p0 = a0 * max(1e-4, 1.0 - eccentricity ** 2)

        # J2 secular rates (rad/s)
        factor = 1.5 * cls.J2 * ((cls.WGS84_A / p0) ** 2) * n0
        d_omega = -factor * math.cos(i0)
        d_w = factor * (2.5 * (math.cos(i0) ** 2) - 0.5)
        d_m = n0 * (1.0 + factor * math.sqrt(max(1e-4, 1.0 - eccentricity ** 2)) * (1.5 * (math.cos(i0) ** 2) - 0.5))

        dt_sec = delta_minutes * 60.0

        om_t = (om0 + d_omega * dt_sec) % (2.0 * math.pi)
        w_t = (w0 + d_w * dt_sec) % (2.0 * math.pi)
        m_t = (m0 + d_m * dt_sec) % (2.0 * math.pi)

        # Solve Kepler's equation
        E = m_t
        for _ in range(15):
            f_val = E - eccentricity * math.sin(E) - m_t
            f_prime = 1.0 - eccentricity * math.cos(E)
            delta = f_val / f_prime
            E -= delta
            if abs(delta) < 1e-10:
                break

        sin_nu = math.sqrt(max(0.0, 1.0 - eccentricity ** 2)) * math.sin(E) / (1.0 - eccentricity * math.cos(E))
        cos_nu = (math.cos(E) - eccentricity) / (1.0 - eccentricity * math.cos(E))
        nu = math.atan2(sin_nu, cos_nu)

        r = a0 * (1.0 - eccentricity * math.cos(E))
        p_val = max(1e-4, p0)
        u = (w_t + nu) % (2.0 * math.pi)

        x = r * (math.cos(om_t) * math.cos(u) - math.sin(om_t) * math.sin(u) * math.cos(i0))
        y = r * (math.sin(om_t) * math.cos(u) + math.cos(om_t) * math.sin(u) * math.cos(i0))
        z = r * (math.sin(u) * math.sin(i0))

        r_dot = math.sqrt(cls.MU_EARTH / p_val) * eccentricity * math.sin(nu)
        rf_dot = math.sqrt(cls.MU_EARTH * p_val) / max(1e-4, r)
        vx = (
            (math.cos(om_t) * math.cos(u) - math.sin(om_t) * math.sin(u) * math.cos(i0)) * r_dot
            - (math.cos(om_t) * math.sin(u) + math.sin(om_t) * math.cos(u) * math.cos(i0)) * rf_dot
        )
        vy = (
            (math.sin(om_t) * math.cos(u) + math.cos(om_t) * math.sin(u) * math.cos(i0)) * r_dot
            - (math.sin(om_t) * math.sin(u) - math.cos(om_t) * math.cos(u) * math.cos(i0)) * rf_dot
        )
        vz = math.sin(i0) * (math.sin(u) * r_dot + math.cos(u) * rf_dot)

        lat_rad = math.asin(max(-1.0, min(1.0, z / max(1e-4, r))))
        we = 7.292115e-5
        lon_rad = (math.atan2(y, x) - we * dt_sec) % (2.0 * math.pi)
        if lon_rad > math.pi:
            lon_rad -= 2.0 * math.pi

        altitude_km = r - cls.WGS84_A
        speed = math.sqrt(vx * vx + vy * vy + vz * vz)

        return {
            "semi_major_axis_km": round(a0, 2),
            "radius_km": round(r, 2),
            "altitude_km": round(altitude_km, 2),
            "position_teme_km": [round(x, 2), round(y, 2), round(z, 2)],
            "r_teme_km": [round(x, 2), round(y, 2), round(z, 2)],
            "velocity_teme_kms": [round(vx, 3), round(vy, 3), round(vz, 3)],
            "v_teme_km_s": [round(vx, 3), round(vy, 3), round(vz, 3)],
            "velocity_km_s": round(speed, 3),
            "sub_satellite_lat_deg": round(math.degrees(lat_rad), 3),
            "sub_satellite_lon_deg": round(math.degrees(lon_rad), 3),
            "orbital_period_minutes": round(86400.0 / (mean_motion_rev_day * 60.0), 2),
            "delta_minutes": delta_minutes,
        }


class HohmannAndBiEllipticOrbitalManeuverPlanner:
    """Orbital Maneuver Optimizer comparing Hohmann vs Bi-Elliptic Transfers."""

    MU_EARTH = 398600.4418  # km^3 / s^2

    @classmethod
    def plan(
        cls,
        r1_km: float,
        r2_km: float,
        rb_km: float = 0.0,
        plane_change_deg: float = 0.0,
        mu: float = MU_EARTH,
    ) -> Dict[str, Any]:
        """Calculates delta-V requirements and duration for orbital transfers."""
        v1 = math.sqrt(mu / r1_km)
        v2 = math.sqrt(mu / r2_km)

        # 1. Hohmann Transfer
        a_h = (r1_km + r2_km) / 2.0
        v_h1 = math.sqrt(mu * (2.0 / r1_km - 1.0 / a_h))
        v_h2 = math.sqrt(mu * (2.0 / r2_km - 1.0 / a_h))
        dv1_h = abs(v_h1 - v1)

        d_inc_rad = math.radians(plane_change_deg)
        if plane_change_deg != 0.0:
            dv2_h = math.sqrt(v_h2 ** 2 + v2 ** 2 - 2.0 * v_h2 * v2 * math.cos(d_inc_rad))
        else:
            dv2_h = abs(v2 - v_h2)

        total_dv_hohmann = dv1_h + dv2_h
        tof_hohmann_sec = math.pi * math.sqrt((a_h ** 3) / mu)

        # 2. Bi-Elliptic Transfer
        rb = rb_km if rb_km > max(r1_km, r2_km) else max(r1_km, r2_km) * 2.0
        a1_b = (r1_km + rb) / 2.0
        a2_b = (r2_km + rb) / 2.0

        v_b1_dep = math.sqrt(mu * (2.0 / r1_km - 1.0 / a1_b))
        dv1_b = abs(v_b1_dep - v1)

        v_b1_apo = math.sqrt(mu * (2.0 / rb - 1.0 / a1_b))
        v_b2_apo = math.sqrt(mu * (2.0 / rb - 1.0 / a2_b))

        if plane_change_deg != 0.0:
            dv2_b = math.sqrt(v_b1_apo ** 2 + v_b2_apo ** 2 - 2.0 * v_b1_apo * v_b2_apo * math.cos(d_inc_rad))
        else:
            dv2_b = abs(v_b2_apo - v_b1_apo)

        v_b2_arr = math.sqrt(mu * (2.0 / r2_km - 1.0 / a2_b))
        dv3_b = abs(v2 - v_b2_arr)

        total_dv_bielliptic = dv1_b + dv2_b + dv3_b
        tof_bielliptic_sec = math.pi * math.sqrt((a1_b ** 3) / mu) + math.pi * math.sqrt((a2_b ** 3) / mu)

        best = "Hohmann" if total_dv_hohmann <= total_dv_bielliptic else "Bi-Elliptic"

        return {
            "r1_km": r1_km,
            "r2_km": r2_km,
            "rb_km": rb,
            "delta_v_total_km_s": round(total_dv_hohmann, 4),
            "hohmann_delta_v_kms": round(total_dv_hohmann, 4),
            "hohmann_tof_hours": round(tof_hohmann_sec / 3600.0, 2),
            "bielliptic_delta_v_kms": round(total_dv_bielliptic, 4),
            "bielliptic_tof_hours": round(tof_bielliptic_sec / 3600.0, 2),
            "optimal_transfer": best,
            "ratio_r2_r1": round(r2_km / r1_km, 2),
        }

    @classmethod
    def plan_hohmann(cls, r1_km: float, r2_km: float, inc_change_deg: float = 0.0, plane_change_deg: float = 0.0) -> Dict[str, Any]:
        pc = max(inc_change_deg, plane_change_deg)
        res = cls.plan(r1_km, r2_km, plane_change_deg=pc)
        return {
            "delta_v_total_km_s": res["hohmann_delta_v_kms"],
            "time_of_flight_s": res["hohmann_tof_hours"] * 3600.0,
            "r1_km": r1_km,
            "r2_km": r2_km,
        }

    @classmethod
    def plan_bi_elliptic(cls, r1_km: float, r2_km: float, r_intermediate_km: float = 0.0, rb_km: float = 0.0) -> Dict[str, Any]:
        rb = max(r_intermediate_km, rb_km)
        res = cls.plan(r1_km, r2_km, rb_km=rb)
        return {
            "delta_v_total_km_s": res["bielliptic_delta_v_kms"],
            "time_of_flight_s": res["bielliptic_tof_hours"] * 3600.0,
            "burns": [1, 2, 3],
            "rb_km": res["rb_km"],
        }


def astronomy_propagate_sgp4(
    inclination_deg: float,
    raan_deg: float,
    eccentricity: float,
    arg_perigee_deg: float,
    mean_anomaly_deg: float,
    mean_motion_rev_day: float,
    delta_minutes: float = 0.0,
) -> Record:
    """Propagates satellite orbit via SGP4 perturbation model."""
    return Record(SGP4SimplifiedPerturbationsSatellitePropagator.propagate(
        inclination_deg,
        raan_deg,
        eccentricity,
        arg_perigee_deg,
        mean_anomaly_deg,
        mean_motion_rev_day,
        delta_minutes=delta_minutes,
    ))


def astronomy_propagate_sgp4_orbit(orbit: Any, delta_minutes: float = 0.0) -> Record:
    """Propagates orbit dictionary via SGP4 perturbation model."""
    return Record(SGP4SimplifiedPerturbationsSatellitePropagator.propagate(
        orbit,
        delta_minutes=delta_minutes,
    ))


def astronomy_plan_orbital_transfer(
    r1_km: float,
    r2_km: float,
    rb_km: float = 0.0,
    plane_change_deg: float = 0.0,
) -> Record:
    """Plans optimal Hohmann or Bi-Elliptic orbital transfer."""
    return Record(HohmannAndBiEllipticOrbitalManeuverPlanner.plan(
        r1_km, r2_km, rb_km=rb_km, plane_change_deg=plane_change_deg
    ))




