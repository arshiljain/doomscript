"""Acoustics Domain Runtime: Sound Pressure Level, Sabine/Eyring RT60, Doppler shift, A-weighting, room modes, and psychoacoustics."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

P_REF = 20e-6  # 20 microPascals (reference threshold of human hearing)

# ============================================================================
# 1. PRESERVED EXISTING EQUATIONS
# ============================================================================

def acoustics_spl_db(pressure_pa: float) -> float:
    """Calculates Sound Pressure Level SPL = 20 * log10(p / p_ref) in decibels (dB SPL)."""
    p = float(pressure_pa)
    if p <= 0.0:
        return 0.0
    spl = 20.0 * math.log10(p / P_REF)
    return round(spl, 1)

def acoustics_sabine_rt60(room_volume_m3: float, total_absorption_sabins: float) -> float:
    """Calculates reverberation time RT60 = 0.161 * V / A in seconds using Sabine formula."""
    v = float(room_volume_m3)
    a = float(total_absorption_sabins)
    if a <= 0.0 or v <= 0.0:
        return 0.0
    rt60 = (0.161 * v) / a
    return round(rt60, 3)

def acoustics_eyring_rt60(room_volume_m3: float, total_surface_area_m2: float, avg_absorption_coeff: float) -> float:
    """Calculates Eyring reverberation time RT60 = 0.161 * V / (-S * ln(1 - alpha_bar))."""
    v = float(room_volume_m3)
    s = float(total_surface_area_m2)
    alpha = float(avg_absorption_coeff)
    if v <= 0.0 or s <= 0.0 or alpha <= 0.0 or alpha >= 1.0:
        return 0.0
    rt60 = (0.161 * v) / (-s * math.log(1.0 - alpha))
    return round(rt60, 3)

def acoustics_doppler_shift(source_freq_hz: float, source_velocity_m_s: float, observer_velocity_m_s: float = 0.0, speed_of_sound_m_s: float = 343.0) -> float:
    """Calculates Doppler shifted observed frequency f_obs = f_src * (c + v_obs) / (c - v_src)."""
    f = float(source_freq_hz)
    vs = float(source_velocity_m_s)
    vo = float(observer_velocity_m_s)
    c = float(speed_of_sound_m_s)
    denom = c - vs
    if abs(denom) < 1e-6:
        return float("inf")
    f_obs = f * (c + vo) / denom
    return round(f_obs, 2)

def acoustics_inverse_square_decay(spl_source_db: float, r1_meters: float, r2_meters: float) -> float:
    """Calculates sound level drop over distance L2 = L1 - 20 * log10(r2 / r1)."""
    spl1 = float(spl_source_db)
    r1 = float(r1_meters)
    r2 = float(r2_meters)
    if r1 <= 0.0 or r2 <= 0.0:
        return spl1
    decay = 20.0 * math.log10(r2 / r1)
    return round(spl1 - decay, 2)

def acoustics_characteristic_impedance(air_density_kg_m3: float = 1.225, speed_of_sound_m_s: float = 343.0) -> float:
    """Calculates acoustic specific impedance z = rho * c in Pa*s/m (Rayls)."""
    rho = float(air_density_kg_m3)
    c = float(speed_of_sound_m_s)
    return round(rho * c, 2)

def acoustics_sound_transmission_loss(mass_surface_kg_m2: float, frequency_hz: float) -> float:
    """Calculates acoustic mass law Sound Transmission Loss STL = 20 * log10(m * f) - 47 in dB."""
    m = float(mass_surface_kg_m2)
    f = float(frequency_hz)
    if m <= 0.0 or f <= 0.0:
        return 0.0
    stl = 20.0 * math.log10(m * f) - 47.0
    return round(max(0.0, stl), 1)

# ============================================================================
# 2. ADVANCED ACOUSTICAL ENGINEERING & PSYCHOACOUSTICS
# ============================================================================

def acoustics_a_weighting(frequency_hz: float) -> float:
    """Calculates standard IEC 61672-1 A-weighting filter gain Delta dB(A) for a frequency in Hz."""
    f = float(frequency_hz)
    if f <= 0.0:
        return -100.0
    f2 = f ** 2
    c1 = 12194.0 ** 2
    c2 = 20.6 ** 2
    c3 = 107.7 ** 2
    c4 = 737.9 ** 2
    num = c1 * (f ** 4)
    den = (f2 + c2) * math.sqrt((f2 + c3) * (f2 + c4)) * (f2 + c1)
    if den <= 0.0:
        return -100.0
    ra = num / den
    # Normalized offset at 1000 Hz = +2.00 dB
    delta_a = 20.0 * math.log10(ra) + 2.00
    return round(delta_a, 2)

def acoustics_phon_to_sone(loudness_level_phon: float) -> float:
    """Converts Stevens loudness level in Phons to perceived linear loudness in Sones: S = 2^((LN - 40)/10)."""
    ln = float(loudness_level_phon)
    if ln < 20.0:
        return round(max(0.0, (ln / 40.0) ** 2), 3)
    return round(2.0 ** ((ln - 40.0) / 10.0), 3)

def acoustics_schroeder_frequency(room_volume_m3: float, rt60_seconds: float) -> float:
    """Calculates Schroeder cutoff frequency fs = 2000 * sqrt(RT60 / V) separating modal and statistical acoustic regimes."""
    v = float(room_volume_m3)
    rt = float(rt60_seconds)
    if v <= 0.0 or rt <= 0.0:
        return 0.0
    return round(2000.0 * math.sqrt(rt / v), 1)

def acoustics_room_modes(length_m: float, width_m: float, height_m: float, max_order: int = 3, speed_of_sound_m_s: float = 343.0) -> List[Dict[str, Any]]:
    """Calculates axial, tangential, and oblique acoustic eigenmodes for a rectangular room."""
    c = float(speed_of_sound_m_s)
    modes = []
    for nx in range(max_order + 1):
        for ny in range(max_order + 1):
            for nz in range(max_order + 1):
                if nx == 0 and ny == 0 and nz == 0:
                    continue
                f = (c / 2.0) * math.sqrt((nx / length_m)**2 + (ny / width_m)**2 + (nz / height_m)**2)
                zeros = (1 if nx == 0 else 0) + (1 if ny == 0 else 0) + (1 if nz == 0 else 0)
                mtype = "axial" if zeros == 2 else ("tangential" if zeros == 1 else "oblique")
                modes.append({"mode": (nx, ny, nz), "frequency_hz": round(f, 2), "type": mtype})
    modes.sort(key=lambda m: m["frequency_hz"])
    return modes

class AcousticsRuntime(DomainRuntime):
    """Runtime engine for Acoustics domain operations."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def spl(self, p: float) -> float:
        return acoustics_spl_db(p)
    def sabine(self, v: float, a: float) -> float:
        return acoustics_sabine_rt60(v, a)
    def eyring(self, v: float, s: float, alpha: float) -> float:
        return acoustics_eyring_rt60(v, s, alpha)
    def doppler(self, f: float, vs: float, vo: float = 0.0, c: float = 343.0) -> float:
        return acoustics_doppler_shift(f, vs, vo, c)
    def decay(self, spl: float, r1: float, r2: float) -> float:
        return acoustics_inverse_square_decay(spl, r1, r2)
    def impedance(self, rho: float = 1.225, c: float = 343.0) -> float:
        return acoustics_characteristic_impedance(rho, c)
    def stl(self, m: float, f: float) -> float:
        return acoustics_sound_transmission_loss(m, f)
    def a_weighting(self, f: float) -> float:
        return acoustics_a_weighting(f)
    def sone(self, phon: float) -> float:
        return acoustics_phon_to_sone(phon)
    def schroeder(self, v: float, rt: float) -> float:
        return acoustics_schroeder_frequency(v, rt)
