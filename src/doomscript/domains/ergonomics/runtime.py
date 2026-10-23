"""Ergonomics Domain Runtime: NIOSH lifting equation, RULA/REBA postural scoring, spinal L5/S1 compression, and anthropometrics."""
import math
from typing import Dict, Any, List, Optional
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED ERGONOMIC ASSESSMENTS
# ============================================================================

def ergo_niosh_rwl(load_constant_kg: float, horiz_cm: float, vert_cm: float, dist_cm: float, angle_deg: float, freq_lifts_min: float, coupling_factor: float = 1.0) -> Dict[str, float]:
    """Calculates NIOSH Recommended Weight Limit (RWL) and Lifting Index (LI)."""
    lc = float(load_constant_kg)
    hm = min(1.0, max(0.0, 25.0 / max(1.0, float(horiz_cm))))
    vm = max(0.0, 1.0 - 0.003 * abs(float(vert_cm) - 75.0))
    dm = max(0.0, 0.82 + (4.5 / max(1.0, float(dist_cm))))
    am = max(0.0, 1.0 - 0.0032 * abs(float(angle_deg)))
    fm = max(0.0, 1.0 - 0.05 * float(freq_lifts_min))
    cm = float(coupling_factor)
    rwl = lc * hm * vm * dm * am * fm * cm
    li = (lc / rwl) if rwl > 0 else float("inf")
    return {
        "rwl_kg": round(rwl, 2),
        "lifting_index": round(li, 2),
        "hm": round(hm, 3), "vm": round(vm, 3), "dm": round(dm, 3),
        "am": round(am, 3), "fm": round(fm, 3), "cm": round(cm, 3)
    }

def ergo_rula_score(upper_arm_deg: float, lower_arm_deg: float, wrist_deg: float, neck_deg: float, trunk_deg: float, load_kg: float) -> Dict[str, Any]:
    """Calculates Rapid Upper Limb Assessment (RULA) score."""
    # Score upper arm
    ua = 1
    if upper_arm_deg > 20: ua = 2
    if upper_arm_deg > 45: ua = 3
    if upper_arm_deg > 90: ua = 4
    # Score lower arm
    la = 1 if 60 <= lower_arm_deg <= 100 else 2
    # Score wrist
    w = 1 if abs(wrist_deg) < 15 else 2
    # Score neck
    n = 1
    if neck_deg > 10: n = 2
    if neck_deg > 20: n = 3
    # Score trunk
    t = 1
    if trunk_deg > 10: t = 2
    if trunk_deg > 20: t = 3
    if trunk_deg > 60: t = 4
    load_score = 0 if load_kg < 2.0 else (1 if load_kg <= 10.0 else 2)
    arm_wrist = ua + la + w
    neck_trunk = n + t
    grand_score = min(7, max(1, (arm_wrist + neck_trunk) // 2 + load_score))
    action_levels = {
        1: "Action Level 1: Posture is acceptable if not repeated or held for long periods.",
        2: "Action Level 2: Further investigation is needed, changes may be required.",
        3: "Action Level 3: Further investigation and change are required soon.",
        4: "Action Level 4: Investigation and change are required immediately."
    }
    lvl = 1 if grand_score <= 2 else (2 if grand_score <= 4 else (3 if grand_score <= 6 else 4))
    return {
        "grand_score": grand_score, "rula_grand_score": grand_score,
        "action_level": lvl,
        "recommendation": action_levels[lvl]
    }

def ergo_metabolic_expenditure(body_weight_kg: float, met_multiplier: float, duration_minutes: float) -> float:
    """Calculates caloric expenditure: Calories = MET * 3.5 * weight_kg / 200 * duration_min."""
    calories = float(met_multiplier) * float(body_weight_kg) * (float(duration_minutes) / 60.0)
    return round(calories, 2)

def ergo_reba_score(trunk_score: int, neck_score: int, legs_score: int, upper_arm_score: int, lower_arm_score: int, wrist_score: int, load_force_score: int = 0) -> Dict[str, Any]:
    """Calculates Rapid Entire Body Assessment (REBA) score (1-15) and risk category."""
    score_a = int(trunk_score) + int(neck_score) + int(legs_score) + int(load_force_score)
    score_b = int(upper_arm_score) + int(lower_arm_score) + int(wrist_score)
    final_score = min(15, max(1, score_a + score_b))
    risk_level = "negligible"
    if final_score >= 11:
        risk_level = "very high (implement change immediately)"
    elif final_score >= 8:
        risk_level = "high (investigate and implement change soon)"
    elif final_score >= 4:
        risk_level = "medium (further investigation, change soon)"
    elif final_score >= 2:
        risk_level = "low (change may be needed)"
    return {"reba_score": final_score, "risk_level": risk_level, "action_needed": final_score >= 8}

def ergo_strain_index(intensity_multiplier: float, duration_multiplier: float, efforts_per_min_multiplier: float, posture_multiplier: float) -> float:
    """Calculates Moore-Garg Strain Index for distal upper extremity risk."""
    si = float(intensity_multiplier) * float(duration_multiplier) * float(efforts_per_min_multiplier) * float(posture_multiplier)
    return round(si, 2)

# ============================================================================
# 2. BIOMECHANICS: L5/S1 SPINAL COMPRESSION & ANTHROPOMETRICS
# ============================================================================

def ergo_l5_s1_compression(lift_weight_kg: float, horizontal_dist_cm: float, torso_flexion_deg: float = 30.0) -> Dict[str, Any]:
    """Estimates sagittal lumbar spinal compression force at L5/S1 (Chaffin 2D biomechanical model)."""
    rad = math.radians(torso_flexion_deg)
    # Upper body mass ~40kg, center of mass ~20cm anterior to L5/S1
    m_body = 40.0 * 9.81 * math.sin(rad) * 0.20
    # Load moment
    m_load = lift_weight_kg * 9.81 * (horizontal_dist_cm / 100.0)
    total_moment = m_body + m_load
    # Lever arm of erector spinae muscles ~ 5cm
    f_muscle = total_moment / 0.05
    # Compressive force = muscle force + body weight component + load weight component
    f_comp = f_muscle + 40.0 * 9.81 * math.cos(rad) + lift_weight_kg * 9.81 * math.cos(rad)
    status = "Within NIOSH limit (<3400N)" if f_comp <= 3400 else ("Action required (>3400N)" if f_comp <= 6400 else "Hazardous (>6400N)")
    return {
        "moment_nm": round(total_moment, 1),
        "muscle_force_n": round(f_muscle, 1),
        "compression_force_n": round(f_comp, 1),
        "niosh_status": status,
        "is_safe": f_comp <= 3400
    }

def ergo_anthropometric_percentile(mean_cm: float, std_dev_cm: float, target_percentile: float = 50.0) -> float:
    """Calculates body dimension at specified anthropometric percentile (e.g. 5th, 50th, 95th)."""
    p = float(target_percentile) / 100.0
    # Standard normal quantile approx (Winitzki inverse error function)
    # z approx via Acklam rational approximation or common constants
    z_table = {5: -1.6449, 10: -1.2816, 25: -0.6745, 50: 0.0, 75: 0.6745, 90: 1.2816, 95: 1.6449}
    z = z_table.get(int(target_percentile), math.sqrt(2.0) * (p - 0.5) * 2.5)
    dim = mean_cm + z * std_dev_cm
    return round(dim, 2)

# ============================================================================
# 3. DOMAIN RUNTIME
# ============================================================================

class ErgonomicsRuntime(DomainRuntime):
    """Unified runtime bridge for the Ergonomics computational domain."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def niosh(self, lc: float, h: float, v: float, d: float, a: float, f: float, c: float = 1.0) -> Dict[str, float]:
        return ergo_niosh_rwl(lc, h, v, d, a, f, c)
    def rula(self, u: float, l: float, w: float, n: float, t: float, load: float) -> Dict[str, Any]:
        return ergo_rula_score(u, l, w, n, t, load)
    def metabolic(self, w: float, met: float, t: float) -> float:
        return ergo_metabolic_expenditure(w, met, t)
    def reba(self, t: int, n: int, leg: int, ua: int, la: int, w: int, f: int = 0) -> Dict[str, Any]:
        return ergo_reba_score(t, n, leg, ua, la, w, f)
    def strain_index(self, im: float, dm: float, em: float, pm: float) -> float:
        return ergo_strain_index(im, dm, em, pm)
    def l5_s1(self, load_kg: float, dist_cm: float, angle_deg: float = 30.0) -> Dict[str, Any]:
        return ergo_l5_s1_compression(load_kg, dist_cm, angle_deg)
    def percentile(self, mean: float, std: float, p: float = 50.0) -> float:
        return ergo_anthropometric_percentile(mean, std, p)
