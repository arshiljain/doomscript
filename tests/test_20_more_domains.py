"""
Unit test suite verifying the 20 newly added computational, scientific, and engineering domain packs:
62. thermodynamics
63. optics
64. acoustics
65. oceanography
66. astrophysics
67. petroleum
68. metallurgy
69. ergonomics
70. biomechanics
71. actuarial
72. pharmacology
73. electromagnetics
74. combustion
75. nuclear
76. cartography
77. chronometry
78. agronomy
79. crystallography
80. aviation
81. structural
"""

import pytest
from doomscript.compiler.engine import execute
from doomscript.domains import get_domain_registry


def test_domain_thermodynamics():
    code = """
use thermodynamics
calculate carnot efficiency hot 600.0 cold 300.0 into eff
calculate entropy change mass 2.0 specific heat 4184.0 t1 290.0 t2 350.0 into delta_s
step polytropic p1 100000.0 v1 1.0 v2 2.0 index 1.4 into poly_res
calculate vapor pressure p1 101325.0 t1 373.15 t2 393.15 delta h 40650.0 into p_vap
calculate rankine cycle boiler 200.0 turbine 3200.0 condenser 2100.0 pump 190.0 into rank_res
calculate joule thomson drop pressure 50.0 coefficient -0.2 into delta_t
"""
    env = execute(code)
    assert env["eff"] == 50.0
    assert env["delta_s"] > 1500.0
    assert env["poly_res"]["p2_pa"] > 0
    assert env["p_vap"] > 101325.0
    assert env["rank_res"]["thermal_efficiency_pct"] > 30.0
    assert env["delta_t"] == -10.0


def test_domain_optics():
    code = """
use optics
calculate thin lens focal 50.0 distance 200.0 into lens_res
calculate snell refraction n1 1.0 n2 1.5 angle 30.0 into snell_res
calculate fresnel reflectance n1 1.0 n2 1.5 into r_norm
calculate rayleigh resolution wavelength 550.0 na 0.85 into res_limit
calculate grating diffraction lines 600.0 order 1 wavelength 500.0 into angle_deg
calculate brewster angle n1 1.0 n2 1.5 into brew_angle
calculate fiber aperture core 1.48 clad 1.46 into fiber_res
"""
    env = execute(code)
    assert env["lens_res"]["image_distance_mm"] == 66.67
    assert env["snell_res"]["total_internal_reflection"] is False
    assert 19.0 < env["snell_res"]["refracted_angle_deg"] < 20.0
    assert env["r_norm"] == 0.04
    assert env["res_limit"] > 350.0
    assert 17.0 < env["angle_deg"] < 18.0
    assert 56.0 < env["brew_angle"] < 57.0
    assert env["fiber_res"]["numerical_aperture"] > 0.2


def test_domain_acoustics():
    code = """
use acoustics
calculate spl pressure 2.0 into spl_db
calculate sabine rt60 volume 500.0 absorption 120.0 into rt60_sab
calculate eyring rt60 volume 500.0 area 400.0 absorption 0.25 into rt60_eyr
calculate doppler shift freq 1000.0 source_v 34.3 into shifted_f
calculate sound decay spl 90.0 r1 1.0 r2 10.0 into decay_spl
calculate sound transmission loss mass 20.0 freq 500.0 into stl_db
"""
    env = execute(code)
    assert env["spl_db"] == 100.0
    assert 0.5 < env["rt60_sab"] < 1.0
    assert 0.5 < env["rt60_eyr"] < 1.0
    assert env["shifted_f"] > 1000.0
    assert env["decay_spl"] == 70.0
    assert env["stl_db"] > 30.0


def test_domain_oceanography():
    code = """
use oceanography
calculate seawater density temp 15.0 salinity 35.0 into rho_sea
calculate coriolis parameter lat 45.0 into f_cor
calculate ocean wave speed wavelength 100.0 depth 200.0 into wave_res
calculate depth pressure depth 1000.0 into gauge_p
calculate seawater sound speed temp 10.0 salinity 35.0 depth 500.0 into snd_spd
calculate wind stress speed 15.0 into tau_wind
"""
    env = execute(code)
    assert 1020.0 < env["rho_sea"] < 1030.0
    assert env["f_cor"] > 1e-5
    assert env["wave_res"]["regime"] == "deep_water"
    assert env["wave_res"]["phase_velocity_m_s"] > 10.0
    assert env["gauge_p"] > 10000.0
    assert 1480.0 < env["snd_spd"] < 1520.0
    assert env["tau_wind"] > 0.2


def test_domain_astrophysics():
    code = """
use astrophysics
calculate schwarzschild radius mass 1.989e30 into r_sch
calculate stellar luminosity radius 6.963e8 temp 5778.0 into sol_lum
calculate eddington luminosity mass 10.0 into l_edd
calculate hubble velocity distance 100.0 into v_hub
calculate jeans mass temp 50.0 density 1e10 into m_jeans
calculate critical density h0 70.0 into rho_crit
"""
    env = execute(code)
    assert 2900.0 < env["r_sch"] < 3000.0
    assert env["sol_lum"] > 3.0e26
    assert env["l_edd"] > 1e32
    assert env["v_hub"] == 7000.0
    assert env["m_jeans"] > 0.0
    assert env["rho_crit"] > 1e-27


def test_domain_petroleum():
    code = """
use petroleum
calculate darcy radial flow perm 50.0 pay 30.0 pres 3000.0 pwell 1500.0 visc 1.2 re 1000.0 rw 0.3 skin 0.0 into q_oil
calculate archie water saturation phi 0.22 rt 25.0 rw 0.05 into sw
convert specific gravity 0.85 to api into api_val
calculate gas oil ratio gas 500.0 oil 250.0 into gor_val
calculate bubble point gor 300.0 gas_grav 0.75 api 35.0 temp 160.0 into pb_psi
calculate pseudocritical gas grav 0.65 into pc_res
"""
    env = execute(code)
    assert env["q_oil"] > 1000.0
    assert 0.1 < env["sw"] < 0.4
    assert 30.0 < env["api_val"] < 40.0
    assert env["gor_val"] == 2000.0
    assert env["pb_psi"] > 500.0
    assert env["pc_res"]["ppc_psia"] > 600.0


def test_domain_metallurgy():
    code = """
use metallurgy
calculate hall petch strength friction 70.0 locking 0.74 grain 25.0 into sigma_y
calculate hollomon true stress k 600.0 strain 0.15 n 0.2 into true_stress
calculate lever rule overall 0.4 alpha 0.1 beta 0.9 into phase_weights
calculate scheil composition initial 2.0 partition 0.15 solid 0.5 into c_liquid
calculate jmak recrystallization time 120.0 k 0.001 exponent 1.5 into x_rex
calculate metal diffusion d0 2.3e-5 energy 140000.0 temp 1100.0 into d_coeff
"""
    env = execute(code)
    assert env["sigma_y"] > 200.0
    assert env["true_stress"] > 300.0
    assert env["phase_weights"]["weight_alpha"] == 0.625
    assert env["phase_weights"]["weight_beta"] == 0.375
    assert env["c_liquid"] > 2.0
    assert 0.5 < env["x_rex"] < 1.0
    assert env["d_coeff"] > 1e-12


def test_domain_ergonomics():
    code = """
use ergonomics
calculate niosh lifting limit load 23.0 horiz 30.0 vert 75.0 dist 25.0 angle 0.0 freq 2.0 coupling 1.0 into niosh_res
calculate rula score upper 30.0 lower 80.0 wrist 10.0 neck 15.0 trunk 25.0 load 5.0 into rula_res
calculate metabolic expenditure weight 75.0 met 4.5 minutes 60.0 into calories_burned
calculate reba score trunk 2 neck 1 legs 2 uarm 2 larm 1 wrist 1 into reba_res
calculate strain index intensity 3.0 duration 1.5 efforts 2.0 posture 1.0 into si_val
"""
    env = execute(code)
    assert env["niosh_res"]["rwl_kg"] > 15.0
    assert 1 <= env["rula_res"]["grand_score"] <= 7
    assert env["calories_burned"] == 337.5
    assert env["reba_res"]["reba_score"] >= 8
    assert env["si_val"] == 9.0


def test_domain_biomechanics():
    code = """
use biomechanics
calculate joint moment force 250.0 arm 0.35 angle 90.0 into torque
calculate center of mass masses [5.0, 10.0, 15.0] positions [0.1, 0.4, 0.9] into com_x
calculate grf impulse forces [100.0, 300.0, 500.0, 200.0] dt 0.01 into impulse_ns
calculate muscle tendon force muscle 800.0 pennation 15.0 into f_tendon
calculate hill muscle force velocity 0.2 f0 600.0 param_a 150.0 param_b 0.25 into f_hill
calculate segment inertia mass 4.5 radius 0.08 into moi_seg
"""
    env = execute(code)
    assert env["torque"] == 87.5
    assert 0.5 < env["com_x"] < 0.8
    assert env["impulse_ns"] == 11.0
    assert 750.0 < env["f_tendon"] < 800.0
    assert env["f_hill"] > 250.0
    assert env["moi_seg"] > 0.01


def test_domain_actuarial():
    code = """
use actuarial
calculate gompertz mortality age 65.0 base 0.0003 factor 1.08 into mu_65
calculate makeham mortality age 65.0 accident 0.001 base 0.0003 factor 1.08 into mu_makeham
calculate annuity present value payment 10000.0 rate 0.05 years 20 into pv_annuity
calculate term insurance premium benefit 100000.0 mortality 0.005 rate 0.04 term 10 into nsp_premium
calculate loss reserve claims [5000.0, 12000.0, 8500.0] severity 1.15 rate 0.03 into reserve_val
calculate chain ladder losses [10000.0, 25000.0, 38000.0] ratio 1.25 into ultimate_loss
"""
    env = execute(code)
    assert env["mu_65"] > 0.03
    assert env["mu_makeham"] > env["mu_65"]
    assert env["pv_annuity"] > 120000.0
    assert env["nsp_premium"] > 3000.0
    assert env["reserve_val"] > 25000.0
    assert env["ultimate_loss"] == 47500.0


def test_domain_pharmacology():
    code = """
use pharmacology
calculate elimination rate halflife 12.0 into ke_val
calculate steady state conc dose 500.0 bioavailability 0.8 clearance 4.0 interval 8.0 into css_val
calculate volume distribution dose 500.0 c0 25.0 into vd_liters
calculate hill response conc 10.0 emax 100.0 ec50 5.0 hill 2.0 into pd_effect
calculate saturable elimination vmax 20.0 km 5.0 conc 15.0 into sat_rate
calculate loading dose vd 35.0 target 15.0 bio 0.9 into load_dose
"""
    env = execute(code)
    assert 0.05 < env["ke_val"] < 0.06
    assert env["css_val"] == 12.5
    assert env["vd_liters"] == 20.0
    assert env["pd_effect"] == 80.0
    assert env["sat_rate"] == 15.0
    assert 550.0 < env["load_dose"] < 600.0


def test_domain_electromagnetics():
    code = """
use electromagnetics
calculate magnetic field wire current 10.0 distance 0.05 into b_wire
calculate skin depth freq 1000000.0 conductivity 5.8e7 perm 1.0 into skin_copper
calculate poynting vector efield 100.0 hfield 0.265 into power_density
calculate coax impedance inner 1.0 outer 3.5 eps 2.25 into z0_coax
calculate wave attenuation freq 1e9 conductivity 0.01 eps 4.0 perm 1.0 into alpha_wave
calculate faraday emf turns 150 flux 0.04 time 0.02 into ind_emf
"""
    env = execute(code)
    assert env["b_wire"] == 4.0e-5
    assert env["skin_copper"] < 0.0001
    assert env["power_density"] == 26.5
    assert 45.0 < env["z0_coax"] < 55.0
    assert env["alpha_wave"] > 0.0
    assert env["ind_emf"] == -300.0


def test_domain_combustion():
    code = """
use combustion
calculate equivalence ratio fuel 1.0 air 14.7 stoich 0.068 into phi_val
calculate arrhenius rate preexp 1e11 ea 120000.0 temp 1500.0 into k_rxn
calculate heat release rate flow 2.5 lhv 45.0 eff 0.98 into hrr_mw
calculate adiabatic flame temp t0 298.15 lhv 45000000.0 cp 1150.0 afr 17.2 into tad_flame
calculate mixture flammability fractions [0.7, 0.3] limits [5.0, 2.1] into lfl_mix
calculate thermal nox temp 1800.0 oxygen 0.03 into nox_index
"""
    env = execute(code)
    assert 0.99 < env["phi_val"] < 1.01
    assert env["k_rxn"] > 1e6
    assert env["hrr_mw"] == 110.25
    assert 2400.0 < env["tad_flame"] < 2500.0
    assert 3.0 < env["lfl_mix"] < 4.0
    assert env["nox_index"] > 1e-11


def test_domain_nuclear():
    code = """
use nuclear
calculate radioactive decay initial 1000.0 halflife 30.17 time 60.34 into a_cs137
calculate decay constant halflife 3600.0 into lam_val
calculate nuclear q value mass_in 2.0141 mass_out 2.0135 into q_mev
calculate radiation shielding initial 500.0 attenuation 0.77 thickness 5.0 into shielded_i
calculate four factor eta 1.34 epsilon 1.03 p 0.89 f 0.85 into k_inf
calculate half value layer attenuation 0.77 into hvl_cm
"""
    env = execute(code)
    assert 249.0 < env["a_cs137"] < 251.0
    assert env["lam_val"] > 1e-4
    assert env["q_mev"] > 0.5
    assert env["shielded_i"] < 15.0
    assert 1.0 < env["k_inf"] < 1.1
    assert 0.8 < env["hvl_cm"] < 1.0


def test_domain_cartography():
    code = """
use cartography
calculate haversine distance lat1 40.7128 lon1 -74.0060 lat2 51.5074 lon2 -0.1278 into dist_nyc_lon
calculate initial bearing lat1 40.7128 lon1 -74.0060 lat2 51.5074 lon2 -0.1278 into az_nyc_lon
calculate mercator projection lat 45.0 lon 10.0 into merc_pos
calculate utm zone lon -73.935242 into utm_nyc
calculate ground distance map_cm 5.0 scale 50000.0 into real_dist_m
calculate mercator distortion lat 60.0 into distortion_res
"""
    env = execute(code)
    assert 5500.0 < env["dist_nyc_lon"] < 5600.0
    assert 50.0 < env["az_nyc_lon"] < 55.0
    assert env["merc_pos"]["y_km"] > 5000.0
    assert env["utm_nyc"] == 18
    assert env["real_dist_m"] == 2500.0
    assert env["distortion_res"]["linear_scale_factor"] == 2.0


def test_domain_chronometry():
    code = """
use chronometry
calculate julian day year 2026 month 10 day 22 into jdn_val
calculate gmst jdn 2460200.5 into gmst_hrs
calculate equation of time day 300 into eot_mins
calculate time dilation proper 3600.0 velocity 260000000.0 into dilated_sec
calculate gravitational dilation proper 3600.0 mass 5.972e24 radius 6371000.0 into grav_dilated
calculate solar declination day 172 into summer_solstice_decl
"""
    env = execute(code)
    assert env["jdn_val"] > 2460000.0
    assert 0.0 <= env["gmst_hrs"] <= 24.0
    assert abs(env["eot_mins"]) < 20.0
    assert env["dilated_sec"] > 7000.0
    assert env["grav_dilated"] < 3600.0
    assert 22.0 < env["summer_solstice_decl"] < 24.0


def test_domain_agronomy():
    code = """
use agronomy
calculate crop water requirement et0 6.5 kc 1.15 into etc_val
calculate growing degree days tmax 28.0 tmin 14.0 tbase 10.0 into gdd_val
calculate fertilizer rate nutrient 120.0 percent 46.0 into urea_kg_ha
calculate cation exchange ca 12.5 mg 3.2 k 0.8 na 0.4 into cec_res
calculate soil porosity bulk 1.3 into soil_por
"""
    env = execute(code)
    assert 7.4 < env["etc_val"] < 7.5
    assert env["gdd_val"] == 11.0
    assert 260.0 < env["urea_kg_ha"] < 262.0
    assert env["cec_res"]["cec_cmol_kg"] == 16.9
    assert env["cec_res"]["base_saturation_pct"] == 100.0
    assert 0.5 < env["soil_por"] < 0.52


def test_domain_crystallography():
    code = """
use crystallography
calculate bragg angle wavelength 0.154 spacing 0.282 order 1 into theta_deg
calculate interplanar spacing lattice 0.405 h 1 k 1 l 1 into d111_al
calculate atomic packing factor system "fcc" into apf_fcc
calculate crystal density atoms 4.0 weight 63.55 volume 4.72e-23 into cu_density
calculate crystallite size wavelength 0.154 fwhm 0.005 theta 20.0 into domain_size
"""
    env = execute(code)
    assert 15.0 < env["theta_deg"] < 16.5
    assert 0.23 < env["d111_al"] < 0.24
    assert env["apf_fcc"] == 0.740
    assert 8.8 < env["cu_density"] < 9.1
    assert env["domain_size"] > 25.0


def test_domain_aviation():
    code = """
use aviation
calculate pressure altitude altimeter 29.82 elevation 1200.0 into pa_ft
calculate density altitude pressure_alt 1300.0 oat 28.0 into da_ft
calculate wind components wind_speed 25.0 wind_dir 040.0 runway 090.0 into wind_comp
calculate turn radius tas 150.0 bank 30.0 into r_turn_ft
calculate banked stall speed vs0 50.0 bank 60.0 into vs_60deg
calculate climb gradient roc 800.0 tas 100.0 into grad_pct
"""
    env = execute(code)
    assert env["pa_ft"] == 1300.0
    assert env["da_ft"] > 2500.0
    assert 18.0 < env["wind_comp"]["crosswind_kts"] < 20.0
    assert 15.0 < env["wind_comp"]["headwind_kts"] < 17.0
    assert 3000.0 < env["r_turn_ft"] < 3500.0
    assert 70.0 < env["vs_60deg"] < 71.5
    assert 7.5 < env["grad_pct"] < 8.0


def test_domain_structural():
    code = """
use structural
calculate beam max moment load 12.0 span 6.0 into m_max
calculate beam max deflection load 12.0 span 6.0 modulus 200.0 inertia 8.0e-5 into delta_max
calculate column buckling load modulus 200.0 inertia 4.5e-5 length 4.0 factor 1.0 into p_buckle
calculate section modulus width 150.0 height 300.0 into s_elastic
calculate mohr principal stresses sx 80.0 sy 20.0 txy 40.0 into mohr_res
calculate slenderness ratio length 3.5 radius 0.05 into lambda_col
"""
    env = execute(code)
    assert env["m_max"] == 54.0
    assert 10.0 < env["delta_max"] < 15.0
    assert env["p_buckle"] > 5000.0
    assert env["s_elastic"] == 2250000.0
    assert env["mohr_res"]["sigma_1_mpa"] == 100.0
    assert env["mohr_res"]["sigma_2_mpa"] == 0.0
    assert env["mohr_res"]["tau_max_mpa"] == 50.0
    assert env["lambda_col"] == 70.0


def test_all_20_domains_registration_and_aliases():
    reg = get_domain_registry()
    domains_to_verify = [
        ("thermodynamics", ["heat_transfer", "thermal_physics", "thermo"]),
        ("optics", ["ray_optics", "wave_optics", "photonics"]),
        ("acoustics", ["sound_engineering", "psychoacoustics", "reverberation"]),
        ("oceanography", ["marine_science", "ocean_dynamics", "ocean_waves"]),
        ("astrophysics", ["stellar_physics", "cosmology", "black_holes"]),
        ("petroleum", ["petro", "oilgas", "reservoir"]),
        ("metallurgy", ["metal", "alloys", "materials_science"]),
        ("ergonomics", ["ergo", "human_factors", "workplace_safety"]),
        ("biomechanics", ["biomech", "kinesiology", "human_motion"]),
        ("actuarial", ["actuary", "insurance_math", "mortality"]),
        ("pharmacology", ["pharm", "pharmacokinetics", "pk_pd"]),
        ("electromagnetics", ["em", "emag", "maxwell"]),
        ("combustion", ["flame", "thermal_combustion", "reaction_kinetics"]),
        ("nuclear", ["radioactive", "atomic", "radiation_physics"]),
        ("cartography", ["carto", "map_projection", "geodesy"]),
        ("chronometry", ["chrono", "horology", "sidereal_time"]),
        ("agronomy", ["agri", "crop_science", "soil_science"]),
        ("crystallography", ["crystal", "xray_diffraction", "lattice"]),
        ("aviation", ["flight", "aero", "avionics"]),
        ("structural", ["civil_structures", "structural_analysis", "beams"]),
    ]
    for dom_name, aliases in domains_to_verify:
        assert dom_name in reg._domains, f"Domain {dom_name} not registered"
        dom = reg._domains[dom_name]
        for a in aliases:
            assert a in reg._alias_map, f"Alias {a} not mapped for {dom_name}"
            assert reg._alias_map[a] == dom_name, f"Alias {a} mapped to {reg._alias_map[a]}, expected {dom_name}"


def test_domain_isolation_and_cross_execution():
    code = """
use acoustics
use aviation
calculate spl pressure 1.5 into sound_p
calculate turn radius tas 120.0 bank 25.0 into turn_r
"""
    env = execute(code)
    assert env["sound_p"] > 90.0
    assert env["turn_r"] > 2500.0
