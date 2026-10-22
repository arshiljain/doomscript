"""Ergonomics Domain Runtime: NIOSH lifting equation, RULA assessment, metabolic expenditure, REBA score, and Moore-Garg Strain Index."""
import math
from typing import Dict, Any

def ergo_niosh_rwl(load_constant_kg: float, horiz_cm: float, vert_cm: float, dist_cm: float, angle_deg: float, freq_lifts_min: float, coupling_factor: float = 1.0) -> Dict[str, float]:
    """Calculates NIOSH Recommended Weight Limit (RWL) and Lifting Index (LI = load / RWL)."""
    lc = float(load_constant_kg)
    h = float(horiz_cm)
    v = float(vert_cm)
    d = float(dist_cm)
    a = float(angle_deg)
    f = float(freq_lifts_min)
    c = float(coupling_factor)

    hm = min(1.0, max(0.0, 25.0 / h)) if h > 0.0 else 0.0
    vm = max(0.0, 1.0 - (0.003 * abs(v - 75.0)))
    dm = max(0.0, 0.82 + (4.5 / d)) if d > 0.0 else 0.0
    am = max(0.0, 1.0 - (0.0032 * abs(a)))
    fm = max(0.0, 1.0 - (0.05 * f))

    rwl = lc * hm * vm * dm * am * fm * c
    return {
        "rwl_kg": round(rwl, 2),
        "horizontal_multiplier": round(hm, 3),
        "vertical_multiplier": round(vm, 3),
        "asymmetry_multiplier": round(am, 3),
    }

def ergo_rula_score(upper_arm_deg: float, lower_arm_deg: float, wrist_deg: float, neck_deg: float, trunk_deg: float, load_kg: float) -> Dict[str, Any]:
    """Calculates Rapid Upper Limb Assessment (RULA) grand score (1-7) and action risk category."""
    score_arm = 1
    u = abs(float(upper_arm_deg))
    if u > 90: score_arm += 4
    elif u > 45: score_arm += 3
    elif u > 20: score_arm += 2

    score_neck = 1
    n = abs(float(neck_deg))
    if n > 20: score_neck += 2
    elif n > 10: score_neck += 1

    score_trunk = 1
    t = abs(float(trunk_deg))
    if t > 60: score_trunk += 4
    elif t > 20: score_trunk += 2
    elif t > 0: score_trunk += 1

    load = float(load_kg)
    load_score = 0
    if load > 10.0: load_score = 3
    elif load > 2.0: load_score = 1

    grand_score = min(7, max(1, int(round((score_arm + score_neck + score_trunk) / 3.0 + load_score))))
    action_level = "acceptable"
    if grand_score >= 7:
        action_level = "investigate and implement change immediately"
    elif grand_score >= 5:
        action_level = "investigate and change soon"
    elif grand_score >= 3:
        action_level = "further investigation required"

    return {"grand_score": grand_score, "action_level": action_level}

def ergo_metabolic_expenditure(body_weight_kg: float, met_multiplier: float, duration_minutes: float) -> float:
    """Calculates total energy expenditure in kcal: E = MET * weight_kg * (duration / 60)."""
    w = float(body_weight_kg)
    met = float(met_multiplier)
    t = float(duration_minutes)
    if w <= 0.0 or met <= 0.0 or t <= 0.0:
        return 0.0
    return round(met * w * (t / 60.0), 2)

def ergo_reba_score(trunk_score: int, neck_score: int, legs_score: int, upper_arm_score: int, lower_arm_score: int, wrist_score: int, load_force_score: int = 0) -> Dict[str, Any]:
    """Calculates Rapid Entire Body Assessment (REBA) score (1-15) and risk category."""
    score_a = trunk_score + neck_score + legs_score + load_force_score
    score_b = upper_arm_score + lower_arm_score + wrist_score
    raw_c = score_a + score_b
    final_score = min(15, max(1, raw_c))
    risk_level = "negligible"
    if final_score >= 11:
        risk_level = "very high (implement change immediately)"
    elif final_score >= 8:
        risk_level = "high (investigate and implement change soon)"
    elif final_score >= 4:
        risk_level = "medium (further investigation, change soon)"
    elif final_score >= 2:
        risk_level = "low (change may be needed)"
    return {"reba_score": final_score, "risk_level": risk_level}

def ergo_strain_index(intensity_multiplier: float, duration_multiplier: float, efforts_per_min_multiplier: float, posture_multiplier: float) -> float:
    """Calculates Moore-Garg Strain Index (SI) for distal upper extremity musculoskeletal risk."""
    si = float(intensity_multiplier) * float(duration_multiplier) * float(efforts_per_min_multiplier) * float(posture_multiplier)
    return round(si, 2)
