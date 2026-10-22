"""Actuarial Domain Runtime: Gompertz & Makeham mortality, annuity PV, term life insurance NSP, and Chain Ladder loss reserves."""
import math
from typing import List, Dict, Any

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
    """Calculates simplified net single premium (NSP) for a term life insurance policy assuming uniform mortality."""
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
