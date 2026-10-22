"""Hydrology & Fluid Dynamics Runtime: Reynolds number, Darcy-Weisbach head loss, Manning channel flow, and runoff."""
import math

def hydro_reynolds_number(velocity: float, diameter: float, kinematic_viscosity: float = 1.004e-6) -> float:
    """Calculates Reynolds Number to determine fluid flow regime (laminar vs turbulent)."""
    v = float(velocity)
    d = float(diameter)
    nu = float(kinematic_viscosity)
    if nu == 0.0:
        return 0.0
    return round((v * d) / nu, 2)

def hydro_darcy_weisbach_head_loss(friction_factor: float, length: float, diameter: float, velocity: float, g: float = 9.80665) -> float:
    """Calculates friction head loss h_f = f * (L/D) * (v^2 / (2g))."""
    f = float(friction_factor)
    l = float(length)
    d = float(diameter)
    v = float(velocity)
    if d == 0.0 or g == 0.0:
        return 0.0
    return round(f * (l / d) * ((v ** 2) / (2.0 * g)), 4)

def hydro_manning_flow(roughness: float, area: float, hydraulic_radius: float, slope: float) -> float:
    """Calculates flow discharge Q = (1/n) * A * R^(2/3) * S^(1/2) via Manning formula."""
    n = float(roughness)
    a = float(area)
    r = float(hydraulic_radius)
    s = float(slope)
    if n == 0.0 or s < 0.0 or r < 0.0:
        return 0.0
    return round((1.0 / n) * a * math.pow(r, 2.0 / 3.0) * math.sqrt(s), 4)

def hydro_rational_peak_runoff(runoff_coeff: float, rainfall_intensity_mm_hr: float, area_hectares: float) -> float:
    """Estimates peak stormwater runoff Q = (C * I * A) / 360 in cubic meters per second."""
    c = float(runoff_coeff)
    i = float(rainfall_intensity_mm_hr)
    a = float(area_hectares)
    return round((c * i * a) / 360.0, 4)
