"""Acoustics Domain Runtime: Sound Pressure Level (SPL), Sabine & Eyring RT60, Doppler shift, and sound transmission loss."""
import math
from typing import Dict, Any

P_REF = 20e-6  # 20 microPascals (reference threshold of human hearing)

def acoustics_spl_db(pressure_pa: float) -> float:
    """Calculates Sound Pressure Level SPL = 20 * log10(p / p_ref) in decibels (dB SPL)."""
    p = float(pressure_pa)
    if p <= 0.0:
        return 0.0
    spl = 20.0 * math.log10(p / P_REF)
    return round(spl, 1)

def acoustics_sabine_rt60(room_volume_m3: float, total_absorption_sabins: float) -> float:
    """Calculates reverberation time RT60 = 0.161 * V / A in seconds using Sabine's formula."""
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
