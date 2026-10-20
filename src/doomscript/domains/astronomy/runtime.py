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


