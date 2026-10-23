"""Nuclear Physics Domain Runtime: Radioactive decay, decay constant, Q-value release, radiation shielding, Four-Factor Formula, Half-Value Layer, critical slab thickness, inhour reactor period, secular equilibrium, and SEMF binding energy."""
import math
from typing import Dict, Any, List
from doomscript.domains.base import DomainRuntime

def nuclear_radioactive_decay(initial_activity_a0: float, half_life_years: float, elapsed_years: float) -> float:
    """Calculates remaining radioactive activity A(t) = A0 * (0.5)^(t / t_half) in Becquerels or Curies."""
    a0 = float(initial_activity_a0)
    hl = float(half_life_years)
    t = float(elapsed_years)
    if hl <= 0.0 or a0 <= 0.0:
        return 0.0
    activity = a0 * (0.5 ** (t / hl))
    return round(activity, 4)

def nuclear_decay_constant(half_life_seconds: float) -> float:
    """Calculates decay constant lambda = ln(2) / t_half in s^-1."""
    hl = float(half_life_seconds)
    if hl <= 0.0:
        return 0.0
    lam = math.log(2) / hl
    return float(f"{lam:.6e}")

def nuclear_reaction_q_value(initial_mass_amu: float, final_mass_amu: float) -> float:
    """Calculates nuclear reaction energy Q = (m_initial - m_final) * 931.494 MeV."""
    mi = float(initial_mass_amu)
    mf = float(final_mass_amu)
    q = (mi - mf) * 931.494
    return round(q, 4)

def nuclear_radiation_shielding(i0_intensity: float, linear_attenuation_mu_cm: float, thickness_cm: float) -> float:
    """Calculates transmitted radiation intensity I = I_0 * exp(-mu * x)."""
    i0 = float(i0_intensity)
    mu = float(linear_attenuation_mu_cm)
    x = float(thickness_cm)
    if i0 <= 0.0 or mu < 0.0 or x < 0.0:
        return 0.0
    transmitted = i0 * math.exp(-mu * x)
    return round(transmitted, 4)

def nuclear_four_factor_formula(eta_reproduction: float, epsilon_fast_fission: float, p_resonance_escape: float, f_thermal_utilization: float) -> float:
    """Calculates infinite multiplication factor k_inf = eta * epsilon * p * f in a nuclear reactor lattice."""
    eta = float(eta_reproduction)
    eps = float(epsilon_fast_fission)
    p = float(p_resonance_escape)
    f = float(f_thermal_utilization)
    k_inf = eta * eps * p * f
    return round(k_inf, 4)

def nuclear_half_value_layer(linear_attenuation_mu_cm: float) -> float:
    """Calculates radiation Half-Value Layer HVL = ln(2) / mu in cm."""
    mu = float(linear_attenuation_mu_cm)
    if mu <= 0.0:
        return 0.0
    return round(math.log(2) / mu, 4)

def nuclear_critical_slab_thickness(diffusion_coeff_d_cm: float, absorption_cross_section_sigma_a: float, nu_sigma_f: float) -> Dict[str, float]:
    """Calculates critical bare slab reactor thickness a = pi / B_m - 2*d using 1-group diffusion theory."""
    d = float(diffusion_coeff_d_cm)
    sa = float(absorption_cross_section_sigma_a)
    nsf = float(nu_sigma_f)
    if d <= 0 or nsf <= sa:
        return {"material_buckling_cm2": 0.0, "critical_thickness_cm": 0.0, "extrapolation_distance_cm": 0.0}
    b_sq = (nsf - sa) / d
    b = math.sqrt(b_sq)
    d_extrap = 2.13 * d
    crit_thickness = (math.pi / b) - 2.0 * d_extrap
    return {
        "material_buckling_cm2": round(b_sq, 6),
        "critical_thickness_cm": round(max(0.0, crit_thickness), 2),
        "extrapolation_distance_cm": round(d_extrap, 3)
    }

def nuclear_inhour_equation(prompt_neutron_lifetime_s: float, delayed_fraction_beta: float, decay_constant_lambda: float, reactivity_rho: float) -> Dict[str, float]:
    """Calculates asymptotic reactor period T from simplified 1-delayed group inhour equation."""
    l_prompt = float(prompt_neutron_lifetime_s)
    beta = float(delayed_fraction_beta)
    lam = float(decay_constant_lambda)
    rho = float(reactivity_rho)
    if rho <= 0.0:
        return {"reactor_period_s": -1.0, "prompt_jump_factor": 1.0, "stable": True}
    # For small rho << beta: T ~= (beta - rho) / (lambda * rho)
    # Full quadratic for 1 group: rho = l/(T) + beta / (1 + lambda*T)
    # rho * T * (1 + lambda * T) = l * (1 + lambda * T) + beta * T
    # (rho * lambda) * T^2 + (rho - beta - lambda * l) * T - l = 0
    a_coef = rho * lam
    b_coef = rho - beta - lam * l_prompt
    c_coef = -l_prompt
    disc = (b_coef ** 2) - 4.0 * a_coef * c_coef
    period = (-b_coef + math.sqrt(max(0.0, disc))) / (2.0 * a_coef) if a_coef > 0 else 0.0
    prompt_jump = beta / (beta - rho) if (beta - rho) > 0 else float('inf')
    return {
        "reactor_period_s": round(period, 2),
        "prompt_jump_factor": round(prompt_jump, 3),
        "stable": rho < beta
    }

def nuclear_secular_equilibrium(parent_half_life_yr: float, daughter_half_life_hr: float, parent_activity_ci: float, elapsed_hr: float) -> Dict[str, float]:
    """Calculates parent and daughter activities under Bateman parent->daughter secular equilibrium."""
    t1_hr = float(parent_half_life_yr) * 8766.0
    t2_hr = float(daughter_half_life_hr)
    a1_0 = float(parent_activity_ci)
    t = float(elapsed_hr)
    if t1_hr <= 0 or t2_hr <= 0:
        return {"parent_activity_ci": 0.0, "daughter_activity_ci": 0.0, "t_max_hr": 0.0}
    lam1 = math.log(2) / t1_hr
    lam2 = math.log(2) / t2_hr
    # A1(t) = A1(0) * exp(-lam1 * t)
    a1_t = a1_0 * math.exp(-lam1 * t)
    # A2(t) = A1(0) * [lam2 / (lam2 - lam1)] * (exp(-lam1 * t) - exp(-lam2 * t))
    ratio = lam2 / (lam2 - lam1) if (lam2 - lam1) != 0 else 1.0
    a2_t = a1_0 * ratio * (math.exp(-lam1 * t) - math.exp(-lam2 * t))
    t_max = math.log(lam2 / lam1) / (lam2 - lam1) if lam2 > lam1 else 0.0
    return {
        "parent_activity_ci": round(a1_t, 4),
        "daughter_activity_ci": round(a2_t, 4),
        "t_max_hr": round(t_max, 2)
    }

def nuclear_binding_energy_weizsacker(protons_z: int, neutrons_n: int) -> Dict[str, float]:
    """Calculates nuclear binding energy using the Bethe-Weizsacker Semi-Empirical Mass Formula (SEMF)."""
    z = int(protons_z)
    n = int(neutrons_n)
    a = z + n
    if a <= 0:
        return {"binding_energy_mev": 0.0, "binding_energy_per_nucleon_mev": 0.0}
    # Coefficients in MeV
    av = 15.75
    as_term = 17.8
    ac = 0.711
    aa = 23.7
    # Pairing term delta
    if a % 2 != 0:
        delta = 0.0
    elif z % 2 == 0 and n % 2 == 0:
        delta = 11.18 / math.sqrt(a)
    else:
        delta = -11.18 / math.sqrt(a)
    vol = av * a
    surf = as_term * (a ** (2.0 / 3.0))
    coul = ac * z * (z - 1) / (a ** (1.0 / 3.0))
    asym = aa * ((a - 2 * z) ** 2) / a
    be = vol - surf - coul - asym + delta
    be_per_a = be / a
    return {
        "binding_energy_mev": round(be, 2),
        "binding_energy_per_nucleon_mev": round(be_per_a, 3),
        "volume_term_mev": round(vol, 2),
        "surface_term_mev": round(surf, 2),
        "coulomb_term_mev": round(coul, 2),
        "asymmetry_term_mev": round(asym, 2)
    }

def nuclear_dose_rate_gamma(source_activity_ci: float, gamma_energy_mev: float, distance_m: float, photons_per_decay: float = 1.0) -> Dict[str, float]:
    """Estimates unshielded gamma radiation dose rate in R/hr and mSv/hr at distance R."""
    a_ci = float(source_activity_ci)
    e_mev = float(gamma_energy_mev)
    r_m = float(distance_m)
    n_p = float(photons_per_decay)
    if r_m <= 0:
        return {"dose_rate_r_hr": 0.0, "dose_rate_msv_hr": 0.0}
    # Rule of thumb: Gamma constant Gamma = 0.53 * E * n in R * m^2 / (hr * Ci)
    gamma_const = 0.53 * e_mev * n_p
    dose_r_hr = (gamma_const * a_ci) / (r_m ** 2)
    # 1 R ~= 9.6 mSv in tissue / air
    dose_msv_hr = dose_r_hr * 9.6
    return {
        "gamma_constant_r_m2_hr_ci": round(gamma_const, 3),
        "dose_rate_r_hr": round(dose_r_hr, 4),
        "dose_rate_msv_hr": round(dose_msv_hr, 3)
    }

def nuclear_thermal_neutron_flux(reactor_power_mw: float, core_volume_m3: float, u235_enrichment_pct: float = 4.0) -> Dict[str, float]:
    """Estimates average thermal neutron flux in a thermal fission reactor."""
    p_w = float(reactor_power_mw) * 1e6
    vol_cm3 = float(core_volume_m3) * 1e6
    enrich = float(u235_enrichment_pct) / 100.0
    # 200 MeV per fission = 3.204e-11 Joules
    fissions_per_sec = p_w / 3.204e-11
    # Typical macroscopic fission cross section Sigma_f ~ 0.05 cm^-1 for LWR core
    sigma_f = 0.015 * (enrich / 0.04)
    vol_safe = max(1.0, vol_cm3)
    flux = fissions_per_sec / (sigma_f * vol_safe)
    return {
        "fission_rate_per_sec": float(f"{fissions_per_sec:.4e}"),
        "macroscopic_fission_cs_cm": round(sigma_f, 4),
        "thermal_neutron_flux_cm2_s": float(f"{flux:.4e}")
    }

class NuclearRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

__all__ = [
    "NuclearRuntime",
    "nuclear_radioactive_decay",
    "nuclear_decay_constant",
    "nuclear_reaction_q_value",
    "nuclear_radiation_shielding",
    "nuclear_four_factor_formula",
    "nuclear_half_value_layer",
    "nuclear_critical_slab_thickness",
    "nuclear_inhour_equation",
    "nuclear_secular_equilibrium",
    "nuclear_binding_energy_weizsacker",
    "nuclear_dose_rate_gamma",
    "nuclear_thermal_neutron_flux"
]
