"""Actuarial Domain Runtime: Gompertz/Makeham mortality, life annuities, term insurance NSP, Chain Ladder loss reserving, and ruin theory."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED EXISTING EQUATIONS
# ============================================================================

def actuarial_gompertz_mortality_rate(age: float, base_rate_b: float = 0.0003, growth_factor_c: float = 1.08) -> float:
    """Calculates instantaneous mortality hazard rate mu(x) = B * c^x under Gompertz law."""
    x = float(age)
    b = float(base_rate_b)
    c = float(growth_factor_c)
    if x < 0.0 or b <= 0.0 or c <= 1.0:
        return 0.0
    mu = b * (c ** x)
    return round(mu, 6)

def actuarial_makeham_mortality_rate(age: float, accident_rate_a: float = 0.001, base_rate_b: float = 0.0003, growth_factor_c: float = 1.08) -> float:
    """Calculates mortality hazard rate under Gompertz-Makeham law: mu(x) = A + B * c^x."""
    x = float(age)
    a = float(accident_rate_a)
    b = float(base_rate_b)
    c = float(growth_factor_c)
    if x < 0.0:
        return 0.0
    mu = a + b * (c ** x)
    return round(mu, 6)

def actuarial_annuity_present_value(payment_amount: float, annual_interest_rate: float, term_years: int) -> float:
    """Calculates present value of an annuity: PV = P * (1 - (1+r)^(-n)) / r."""
    p = float(payment_amount)
    r = float(annual_interest_rate)
    n = int(term_years)
    if r <= 0.0:
        return round(p * n, 2)
    pv = p * (1.0 - ((1.0 + r) ** (-n))) / r
    return round(pv, 2)

def actuarial_term_insurance_premium(death_benefit: float, annual_mortality_rate: float, annual_interest_rate: float, term_years: int) -> float:
    """Calculates net single premium (NSP) for a term life insurance policy assuming uniform mortality."""
    benefit = float(death_benefit)
    q = float(annual_mortality_rate)
    r = float(annual_interest_rate)
    n = int(term_years)
    v = 1.0 / (1.0 + r)
    nsp = 0.0
    p_survival = 1.0
    for t in range(1, n + 1):
        discount = v ** t
        prob_death = p_survival * q
        nsp += benefit * prob_death * discount
        p_survival *= (1.0 - q)
        if p_survival <= 0.0:
            break
    return round(nsp, 2)

def actuarial_loss_reserve(claim_amounts: List[float], severity_multiplier: float, discount_rate: float) -> float:
    """Calculates discounted aggregate loss reserve: sum(claims * multiplier) / (1 + r)."""
    mult = float(severity_multiplier)
    r = float(discount_rate)
    total_claims = sum(float(c) for c in claim_amounts)
    gross_loss = total_claims * mult
    discounted = gross_loss / (1.0 + r)
    return round(discounted, 2)

def actuarial_chain_ladder_projection(cumulative_losses_by_dev_year: List[float], link_ratio: float) -> float:
    """Projects ultimate claim losses using standard Chain-Ladder link ratio: Ultimate = Latest * f."""
    if not cumulative_losses_by_dev_year:
        return 0.0
    latest = float(cumulative_losses_by_dev_year[-1])
    f = float(link_ratio)
    return round(latest * f, 2)

# ============================================================================
# 2. ADVANCED ACTUARIAL MATHEMATICS & LOSS RESERVING
# ============================================================================

def actuarial_chain_ladder_triangle(triangle: List[List[float]]) -> Dict[str, Any]:
    """Performs full Mack Chain-Ladder loss reserving on a cumulative claims triangle."""
    n = len(triangle)
    if n == 0:
        return {"link_ratios": [], "ultimate_losses": [], "total_ibnr": 0.0}

    # Calculate volume-weighted link ratios f_j
    link_ratios = []
    for j in range(n - 1):
        sum_curr = 0.0
        sum_next = 0.0
        for i in range(n - 1 - j):
            if j < len(triangle[i]) and j + 1 < len(triangle[i]):
                sum_curr += triangle[i][j]
                sum_next += triangle[i][j + 1]
        factor = (sum_next / sum_curr) if sum_curr > 0 else 1.0
        link_ratios.append(round(factor, 4))

    # Project ultimate losses and IBNR reserves
    latest_losses = []
    ultimate_losses = []
    ibnr_reserves = []
    for i in range(n):
        curr_len = len(triangle[i])
        latest = triangle[i][-1]
        latest_losses.append(latest)
        ult = latest
        for j in range(curr_len - 1, n - 1):
            ult *= link_ratios[j]
        ultimate_losses.append(round(ult, 2))
        ibnr_reserves.append(round(max(0.0, ult - latest), 2))

    return {
        "link_ratios": link_ratios,
        "latest_losses": latest_losses,
        "ultimate_losses": ultimate_losses,
        "ibnr_by_origin_year": ibnr_reserves,
        "total_ibnr": round(sum(ibnr_reserves), 2)
    }

def actuarial_curtate_life_expectancy(age: float, base_rate_b: float = 0.0003, growth_factor_c: float = 1.08, max_age: int = 110) -> float:
    """Calculates curtate life expectancy e_x = sum_{k=1}^{omega - x} k_p_x under Gompertz law."""
    x = float(age)
    b = float(base_rate_b)
    c = float(growth_factor_c)
    log_c = math.log(c)

    # Gompertz survival function S(t) = exp(-B/ln(c) * (c^t - 1))
    def s_age(a):
        return math.exp(-(b / log_c) * (c ** a - 1.0))

    sx = s_age(x)
    if sx <= 0:
        return 0.0
    ex = 0.0
    for k in range(1, int(max_age - x) + 1):
        k_px = s_age(x + k) / sx
        ex += k_px
        if k_px < 1e-5:
            break
    return round(ex, 2)

def actuarial_cramer_lundberg_ruin(initial_surplus: float, premium_rate: float, claim_frequency_lambda: float, mean_claim_size: float) -> Dict[str, float]:
    """Calculates ruin probability upper bound psi(u) <= exp(-R * u) in the classical Cramér-Lundberg risk model."""
    u = float(initial_surplus)
    c = float(premium_rate)
    lam = float(claim_frequency_lambda)
    mu_claim = float(mean_claim_size)

    # Net profit condition: c > lambda * mu
    expected_loss_rate = lam * mu_claim
    safety_loading_theta = (c - expected_loss_rate) / expected_loss_rate if expected_loss_rate > 0 else 0.0
    if safety_loading_theta <= 0:
        return {"ruin_probability_upper_bound": 1.0, "safety_loading": safety_loading_theta, "adjustment_coefficient_r": 0.0}

    # For exponentially distributed claim sizes: R = (c - lambda * mu) / (c * mu) = theta / ((1 + theta) * mu)
    r_coeff = (c - lam * mu_claim) / (c * mu_claim)
    psi_u = (1.0 / (1.0 + safety_loading_theta)) * math.exp(-r_coeff * u)

    return {
        "ruin_probability_upper_bound": round(min(1.0, max(0.0, psi_u)), 6),
        "safety_loading": round(safety_loading_theta, 4),
        "adjustment_coefficient_r": round(r_coeff, 6)
    }

class ActuarialRuntime(DomainRuntime):
    """Runtime engine for Actuarial domain calculations."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def gompertz(self, age: float, b: float = 0.0003, c: float = 1.08) -> float:
        return actuarial_gompertz_mortality_rate(age, b, c)
    def makeham(self, age: float, a: float = 0.001, b: float = 0.0003, c: float = 1.08) -> float:
        return actuarial_makeham_mortality_rate(age, a, b, c)
    def annuity_pv(self, p: float, r: float, n: int) -> float:
        return actuarial_annuity_present_value(p, r, n)
    def term_premium(self, b: float, q: float, r: float, n: int) -> float:
        return actuarial_term_insurance_premium(b, q, r, n)
    def loss_reserve(self, claims: List[float], mult: float, r: float) -> float:
        return actuarial_loss_reserve(claims, mult, r)
    def chain_ladder(self, losses: List[float], f: float) -> float:
        return actuarial_chain_ladder_projection(losses, f)
    def chain_ladder_triangle(self, tri: List[List[float]]) -> Dict[str, Any]:
        return actuarial_chain_ladder_triangle(tri)
    def life_expectancy(self, age: float, b: float = 0.0003, c: float = 1.08) -> float:
        return actuarial_curtate_life_expectancy(age, b, c)
    def ruin(self, u: float, c: float, lam: float, mu: float) -> Dict[str, float]:
        return actuarial_cramer_lundberg_ruin(u, c, lam, mu)
