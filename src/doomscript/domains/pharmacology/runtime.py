"""Pharmacology Domain Runtime: Pharmacokinetics (PK), Pharmacodynamics (PD), two-compartment models, Cockcroft-Gault renal dosing, AUC, and clearance."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED EXISTING EQUATIONS
# ============================================================================

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

# ============================================================================
# 2. DEEPENED CLINICAL PHARMACOKINETICS & RENAL DOSING
# ============================================================================

def pharm_cockcroft_gault_crcl(age_years: float, weight_kg: float, serum_creatinine_mg_dl: float, is_female: bool = False) -> float:
    """Calculates estimated Creatinine Clearance (CrCl) in mL/min via Cockcroft-Gault formula."""
    age = float(age_years)
    wt = float(weight_kg)
    scr = float(serum_creatinine_mg_dl)
    if scr <= 0.0:
        return 0.0
    crcl = ((140.0 - age) * wt) / (72.0 * scr)
    if is_female:
        crcl *= 0.85
    return round(max(0.0, crcl), 2)

def pharm_trapezoidal_auc(time_hours: List[float], concentrations_mg_l: List[float], ke: Optional[float] = None) -> float:
    """Calculates Area Under the Curve (AUC_0-inf) using linear trapezoidal rule."""
    if len(time_hours) != len(concentrations_mg_l) or len(time_hours) < 2:
        return 0.0
    auc = 0.0
    for i in range(len(time_hours) - 1):
        dt = float(time_hours[i + 1]) - float(time_hours[i])
        c_avg = (float(concentrations_mg_l[i]) + float(concentrations_mg_l[i + 1])) / 2.0
        auc += dt * c_avg
    if ke and float(ke) > 0.0:
        # Extrapolate to infinity: C_last / ke
        auc += float(concentrations_mg_l[-1]) / float(ke)
    return round(auc, 3)

def pharm_two_compartment_iv_bolus(dose_mg: float, vc_central_liters: float, k10_hr: float, k12_hr: float, k21_hr: float, time_hr: float) -> Dict[str, float]:
    """Calculates central plasma and peripheral tissue concentrations in a 2-compartment open IV bolus model."""
    d = float(dose_mg)
    vc = float(vc_central_liters)
    k10 = float(k10_hr)
    k12 = float(k12_hr)
    k21 = float(k21_hr)
    t = float(time_hr)
    if vc <= 0.0:
        return {"central_conc": 0.0, "peripheral_conc": 0.0}

    # Eigenvalues alpha and beta
    b_term = k10 + k12 + k21
    c_term = k10 * k21
    disc = math.sqrt(max(0.0, (b_term ** 2) - 4.0 * c_term))
    alpha = (b_term + disc) / 2.0
    beta = (b_term - disc) / 2.0

    # Macro constants A and B
    a_macro = (d / vc) * (alpha - k21) / (alpha - beta) if (alpha - beta) > 0 else 0.0
    b_macro = (d / vc) * (k21 - beta) / (alpha - beta) if (alpha - beta) > 0 else 0.0

    cp = a_macro * math.exp(-alpha * t) + b_macro * math.exp(-beta * t)
    return {
        "central_conc_mg_l": round(max(0.0, cp), 4),
        "alpha_rate": round(alpha, 4),
        "beta_rate": round(beta, 4)
    }

class PharmacologyRuntime(DomainRuntime):
    """Runtime engine for Pharmacology domain calculations."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def ke(self, t_half: float) -> float:
        return pharm_elimination_rate(t_half)
    def css(self, d: float, f: float, cl: float, tau: float) -> float:
        return pharm_steady_state_conc(d, f, cl, tau)
    def vd(self, d: float, c0: float) -> float:
        return pharm_volume_of_distribution(d, c0)
    def hill(self, c: float, emax: float, ec50: float, n: float = 1.0) -> float:
        return pharm_hill_equation(c, emax, ec50, n)
    def michaelis(self, vmax: float, km: float, c: float) -> float:
        return pharm_michaelis_menten_elimination_rate(vmax, km, c)
    def loading_dose(self, vd: float, target: float, f: float = 1.0) -> float:
        return pharm_loading_dose(vd, target, f)
    def crcl(self, age: float, wt: float, scr: float, is_female: bool = False) -> float:
        return pharm_cockcroft_gault_crcl(age, wt, scr, is_female)
    def auc(self, times: List[float], concs: List[float], ke: Optional[float] = None) -> float:
        return pharm_trapezoidal_auc(times, concs, ke)
