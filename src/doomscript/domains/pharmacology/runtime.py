"""Pharmacology Domain Runtime: Half-life, steady-state concentration, volume of distribution, Hill dose-response, Michaelis-Menten kinetics, and loading dose."""
import math
from typing import Dict, Any

def pharm_elimination_rate(half_life_hours: float) -> float:
    """Calculates elimination rate constant ke = ln(2) / t_half in hr^-1."""
    t_half = float(half_life_hours)
    if t_half <= 0.0:
        return 0.0
    return round(math.log(2) / t_half, 5)

def pharm_steady_state_conc(dose_mg: float, bioavailability_f: float, clearance_l_hr: float, interval_tau_hr: float) -> float:
    """Calculates average steady-state plasma concentration Css = (F * Dose) / (CL * tau) in mg/L."""
    d = float(dose_mg)
    f = float(bioavailability_f)
    cl = float(clearance_l_hr)
    tau = float(interval_tau_hr)
    if cl <= 0.0 or tau <= 0.0:
        return 0.0
    css = (f * d) / (cl * tau)
    return round(css, 3)

def pharm_volume_of_distribution(dose_mg: float, initial_concentration_mg_l: float) -> float:
    """Calculates apparent volume of distribution Vd = Dose / C0 in Liters."""
    d = float(dose_mg)
    c0 = float(initial_concentration_mg_l)
    if c0 <= 0.0:
        return 0.0
    return round(d / c0, 2)

def pharm_hill_equation(concentration_c: float, e_max: float, ec50: float, hill_n: float = 1.0) -> float:
    """Calculates drug pharmacodynamic effect E = (Emax * C^n) / (EC50^n + C^n)."""
    c = float(concentration_c)
    emax = float(e_max)
    ec = float(ec50)
    n = float(hill_n)
    if c <= 0.0 or ec <= 0.0:
        return 0.0
    c_n = c ** n
    ec_n = ec ** n
    effect = (emax * c_n) / (ec_n + c_n)
    return round(effect, 4)

def pharm_michaelis_menten_elimination_rate(v_max_mg_hr: float, km_mg_l: float, plasma_conc_mg_l: float) -> float:
    """Calculates non-linear saturable elimination rate dC/dt = (Vmax * C) / (Km + C) in mg/hr."""
    vmax = float(v_max_mg_hr)
    km = float(km_mg_l)
    c = float(plasma_conc_mg_l)
    denom = km + c
    if denom <= 0.0 or c <= 0.0:
        return 0.0
    rate = (vmax * c) / denom
    return round(rate, 3)

def pharm_loading_dose(volume_dist_l: float, target_conc_mg_l: float, bioavailability_f: float = 1.0) -> float:
    """Calculates target loading dose LD = (Vd * C_target) / F in mg."""
    vd = float(volume_dist_l)
    ctarget = float(target_conc_mg_l)
    f = float(bioavailability_f)
    if f <= 0.0:
        return 0.0
    ld = (vd * ctarget) / f
    return round(ld, 1)
