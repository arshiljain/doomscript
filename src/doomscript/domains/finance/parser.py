"""Independent Domain Parser for Quantitative Finance & Time Series domain."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.finance.spec import (
    FinanceFetchSpec,
    FinanceMavSpec,
    FinanceRsiSpec,
    FinanceReturnsSpec,
    FinanceSharpeSpec,
    FinanceBacktestSpec,
)


class FinanceDomainParser(DomainParser):
    """Independent parser for Quantitative Finance syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # fetch stock [prices for] <symbol> [from <start> to <end>] into <target>
        m_fetch = re.match(
            r"^fetch\s+stock(?:\s+prices\s+for)?\s+(.+?)(?:\s+from\s+(.+?)\s+to\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fetch:
            sym_expr = m_fetch.group(1).strip()
            start_expr = m_fetch.group(2).strip() if m_fetch.group(2) else '"2024-01-01"'
            end_expr = m_fetch.group(3).strip() if m_fetch.group(3) else '"2024-12-31"'
            target = m_fetch.group(4).strip()
            return f"set {target} to fetch_stock_prices({sym_expr}, start_date={start_expr}, end_date={end_expr})"

        # calculate <n> day (moving average|sma|ema) of <series> into <target>
        m_mav = re.match(
            r"^(?:calculate\s+)?(\d+)\s+day\s+(moving\s+average|sma|ema|exponential\s+moving\s+average)\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mav:
            window = m_mav.group(1).strip()
            kind_raw = m_mav.group(2).lower()
            kind = "ema" if "e" in kind_raw else "sma"
            series_expr = m_mav.group(3).strip()
            target = m_mav.group(4).strip()
            return f'set {target} to moving_average({series_expr}, window={window}, kind="{kind}")'

        # calculate rsi of <series> [over <n> days] into <target>
        m_rsi = re.match(
            r"^(?:calculate\s+)?rsi\s+of\s+(.+?)(?:\s+over\s+(\d+)\s+days?)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rsi:
            series_expr = m_rsi.group(1).strip()
            period = m_rsi.group(2).strip() if m_rsi.group(2) else "14"
            target = m_rsi.group(3).strip()
            return f"set {target} to relative_strength_index({series_expr}, period={period})"

        # calculate daily returns of <series> into <target>
        m_ret = re.match(
            r"^(?:calculate\s+)?daily\s+returns\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ret:
            series_expr = m_ret.group(1).strip()
            target = m_ret.group(2).strip()
            return f"set {target} to calculate_daily_returns({series_expr})"

        # calculate sharpe ratio of <series> [with risk_free / risk_free_rate <rf>] into <target>
        m_sharpe = re.match(
            r"^(?:calculate\s+)?sharpe\s+ratio\s+of\s+(.+?)(?:\s+with\s+risk_free(?:_rate)?\s+([^\s]+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sharpe:
            series_expr = m_sharpe.group(1).strip()
            rf = m_sharpe.group(2).strip() if m_sharpe.group(2) else "0.04"
            target = m_sharpe.group(3).strip()
            return f"set {target} to calculate_sharpe_ratio({series_expr}, risk_free_rate={rf})"

        # backtest strategy on <prices> [where <cond>] into <target>
        m_bt = re.match(
            r"^backtest\s+strategy\s+on\s+(.+?)(?:\s+where\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bt:
            prices_expr = m_bt.group(1).strip()
            cond = f'"{m_bt.group(2).strip()}"' if m_bt.group(2) else '"crossover"'
            target = m_bt.group(3).strip()
            return f"set {target} to backtest_strategy({prices_expr}, condition={cond})"

        # bollinger bands for <prices> with period <p>, std <s> into <target>
        m_bb = re.match(
            r"^bollinger\s+bands\s+for\s+(.+?)\s+with\s+period\s+(.+?),\s*std\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bb:
            prices, p, std, target = m_bb.group(1), m_bb.group(2), m_bb.group(3), m_bb.group(4)
            return f"set {target} to finance_bollinger_bands({prices}, period={p}, num_std={std})"

        # rsi for <prices> with period <p> into <target>
        m_rsi2 = re.match(
            r"^rsi\s+for\s+(.+?)\s+with\s+period\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rsi2:
            prices, p, target = m_rsi2.group(1), m_rsi2.group(2), m_rsi2.group(3)
            return f"set {target} to finance_rsi({prices}, period={p})"

        # macd for <prices> with fast <f>, slow <s>, signal <sig> into <target>
        m_macd = re.match(
            r"^macd\s+for\s+(.+?)\s+with\s+fast\s+(.+?),\s*slow\s+(.+?),\s*signal\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_macd:
            prices, f, slow, sig, target = m_macd.group(1), m_macd.group(2), m_macd.group(3), m_macd.group(4), m_macd.group(5)
            return f"set {target} to finance_macd({prices}, fast={f}, slow={slow}, signal={sig})"

        # maximum drawdown of <prices> into <target>
        m_mdd = re.match(
            r"^maximum\s+drawdown\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mdd:
            prices, target = m_mdd.group(1), m_mdd.group(2)
            return f"set {target} to finance_maximum_drawdown({prices})"

        # value at risk of <returns> at confidence <conf> into <target>
        m_var = re.match(
            r"^value\s+at\s+risk\s+of\s+(.+?)\s+at\s+confidence\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_var:
            rets, conf, target = m_var.group(1), m_var.group(2), m_var.group(3)
            return f"set {target} to finance_value_at_risk({rets}, confidence={conf})"

        # cagr of <prices> into <target>
        m_cagr = re.match(
            r"^cagr\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cagr:
            prices, target = m_cagr.group(1), m_cagr.group(2)
            return f"set {target} to finance_cagr({prices})"

        # 350-Expansion Finance Operations
        vwap_m = re.match(
            r"^volume\s+weighted\s+average\s+price\s+of\s+(.+?)\s+with\s+volumes\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if vwap_m:
            ps, vs, target = vwap_m.group(1).strip(), vwap_m.group(2).strip(), vwap_m.group(3).strip()
            return f"set {target} to fin_vwap({ps}, {vs})"

        stoch_m = re.match(
            r"^stochastic\s+oscillator\s+of\s+(.+?)\s+(.+?)\s+(.+?)(?:\s+with\s+period\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if stoch_m:
            hs, ls, cs = stoch_m.group(1).strip(), stoch_m.group(2).strip(), stoch_m.group(3).strip()
            p = stoch_m.group(4).strip() if stoch_m.group(4) else "14"
            target = stoch_m.group(5).strip()
            return f"set {target} to fin_stochastic_oscillator({hs}, {ls}, {cs}, k_period={p})"

        sortino_m = re.match(
            r"^sortino\s+ratio\s+of\s+returns\s+(.+?)(?:\s+with\s+risk\s+free\s+rate\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if sortino_m:
            rets = sortino_m.group(1).strip()
            rf = sortino_m.group(2).strip() if sortino_m.group(2) else "0.02"
            target = sortino_m.group(3).strip()
            return f"set {target} to fin_sortino_ratio({rets}, risk_free_rate={rf})"

        treynor_m = re.match(
            r"^treynor\s+ratio\s+of\s+returns\s+(.+?)\s+vs\s+market\s+(.+?)(?:\s+with\s+risk\s+free\s+rate\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if treynor_m:
            rets, mkt = treynor_m.group(1).strip(), treynor_m.group(2).strip()
            rf = treynor_m.group(3).strip() if treynor_m.group(3) else "0.02"
            target = treynor_m.group(4).strip()
            return f"set {target} to fin_treynor_ratio({rets}, {mkt}, risk_free_rate={rf})"

        calmar_m = re.match(
            r"^calmar\s+ratio\s+of\s+returns\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if calmar_m:
            rets, target = calmar_m.group(1).strip(), calmar_m.group(2).strip()
            return f"set {target} to fin_calmar_ratio({rets})"

        beta_m = re.match(
            r"^beta\s+coefficient\s+of\s+(.+?)\s+vs\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if beta_m:
            asset, mkt, target = beta_m.group(1).strip(), beta_m.group(2).strip(), beta_m.group(3).strip()
            return f"set {target} to fin_beta({asset}, {mkt})"

        alpha_m = re.match(
            r"^jensen\s+alpha\s+of\s+(.+?)\s+vs\s+(.+?)(?:\s+with\s+risk\s+free\s+rate\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if alpha_m:
            asset, mkt = alpha_m.group(1).strip(), alpha_m.group(2).strip()
            rf = alpha_m.group(3).strip() if alpha_m.group(3) else "0.02"
            target = alpha_m.group(4).strip()
            return f"set {target} to fin_alpha({asset}, {mkt}, risk_free_rate={rf})"

        bsc_m = re.match(
            r"^black\s+scholes\s+call\s+price\s+for\s+spot\s+(.+?)\s+strike\s+(.+?)\s+expiry\s+(.+?)\s+rate\s+(.+?)\s+volatility\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if bsc_m:
            spot, strike, t, rate, vol, target = bsc_m.group(1).strip(), bsc_m.group(2).strip(), bsc_m.group(3).strip(), bsc_m.group(4).strip(), bsc_m.group(5).strip(), bsc_m.group(6).strip()
            return f"set {target} to fin_black_scholes_call({spot}, {strike}, {t}, {rate}, {vol})"

        bsp_m = re.match(
            r"^black\s+scholes\s+put\s+price\s+for\s+spot\s+(.+?)\s+strike\s+(.+?)\s+expiry\s+(.+?)\s+rate\s+(.+?)\s+volatility\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if bsp_m:
            spot, strike, t, rate, vol, target = bsp_m.group(1).strip(), bsp_m.group(2).strip(), bsp_m.group(3).strip(), bsp_m.group(4).strip(), bsp_m.group(5).strip(), bsp_m.group(6).strip()
            return f"set {target} to fin_black_scholes_put({spot}, {strike}, {t}, {rate}, {vol})"

        atr_m = re.match(
            r"^average\s+true\s+range\s+of\s+(.+?)\s+(.+?)\s+(.+?)(?:\s+with\s+period\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if atr_m:
            hs, ls, cs = atr_m.group(1).strip(), atr_m.group(2).strip(), atr_m.group(3).strip()
            p = atr_m.group(4).strip() if atr_m.group(4) else "14"
            target = atr_m.group(5).strip()
            return f"set {target} to fin_average_true_range({hs}, {ls}, {cs}, period={p})"

        kelt_m = re.match(
            r"^keltner\s+channels\s+for\s+(.+?)\s+(.+?)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if kelt_m:
            hs, ls, cs, target = kelt_m.group(1).strip(), kelt_m.group(2).strip(), kelt_m.group(3).strip(), kelt_m.group(4).strip()
            return f"set {target} to fin_keltner_channels({hs}, {ls}, {cs})"

        wr_m = re.match(
            r"^williams\s+percent\s+r\s+of\s+(.+?)\s+(.+?)\s+(.+?)(?:\s+with\s+period\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if wr_m:
            hs, ls, cs = wr_m.group(1).strip(), wr_m.group(2).strip(), wr_m.group(3).strip()
            p = wr_m.group(4).strip() if wr_m.group(4) else "14"
            target = wr_m.group(5).strip()
            return f"set {target} to fin_williams_r({hs}, {ls}, {cs}, period={p})"

        mfi_m = re.match(
            r"^money\s+flow\s+index\s+of\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)(?:\s+with\s+period\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if mfi_m:
            hs, ls, cs, vs = mfi_m.group(1).strip(), mfi_m.group(2).strip(), mfi_m.group(3).strip(), mfi_m.group(4).strip()
            p = mfi_m.group(5).strip() if mfi_m.group(5) else "14"
            target = mfi_m.group(6).strip()
            return f"set {target} to fin_money_flow_index({hs}, {ls}, {cs}, {vs}, period={p})"

        reb_m = re.match(
            r"^rebalance\s+portfolio\s+weights\s+(.+?)\s+to\s+target\s+(.+?)\s+with\s+value\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if reb_m:
            cur, tgt, val, target = reb_m.group(1).strip(), reb_m.group(2).strip(), reb_m.group(3).strip(), reb_m.group(4).strip()
            return f"set {target} to fin_portfolio_rebalance({cur}, {tgt}, {val})"

        twap_m = re.match(
            r"^time\s+weighted\s+average\s+price\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if twap_m:
            ps, target = twap_m.group(1).strip(), twap_m.group(2).strip()
            return f"set {target} to fin_twap({ps})"

        donch_m = re.match(
            r"^donchian\s+channels\s+for\s+(.+?)\s+and\s+(.+?)(?:\s+with\s+period\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if donch_m:
            hs, ls = donch_m.group(1).strip(), donch_m.group(2).strip()
            p = donch_m.group(3).strip() if donch_m.group(3) else "20"
            target = donch_m.group(4).strip()
            return f"set {target} to fin_donchian_channels({hs}, {ls}, period={p})"

        info_m = re.match(
            r"^information\s+ratio\s+of\s+(.+?)\s+vs\s+benchmark\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if info_m:
            asset, bench, target = info_m.group(1).strip(), info_m.group(2).strip(), info_m.group(3).strip()
            return f"set {target} to fin_information_ratio({asset}, {bench})"

        dd_ser_m = re.match(
            r"^drawdown\s+series\s+for\s+returns\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if dd_ser_m:
            rets, target = dd_ser_m.group(1).strip(), dd_ser_m.group(2).strip()
            return f"set {target} to fin_drawdown_series({rets})"

        iv_m = re.match(
            r"^implied\s+volatility\s+of\s+(call|put)\s+for\s+price\s+(.+?)\s+spot\s+(.+?)\s+strike\s+(.+?)\s+expiry\s+(.+?)\s+rate\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if iv_m:
            is_call = iv_m.group(1).lower() == "call"
            price, spot, strike, t, rate, target = iv_m.group(2).strip(), iv_m.group(3).strip(), iv_m.group(4).strip(), iv_m.group(5).strip(), iv_m.group(6).strip(), iv_m.group(7).strip()
            return f"set {target} to fin_implied_volatility_bisection({price}, {spot}, {strike}, {t}, {rate}, is_call={is_call})"

        var_hist_m = re.match(
            r"^historical\s+value\s+at\s+risk\s+of\s+(.+?)\s+at\s+confidence\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if var_hist_m:
            rets, conf, target = var_hist_m.group(1).strip(), var_hist_m.group(2).strip(), var_hist_m.group(3).strip()
            return f"set {target} to fin_var_historical({rets}, confidence={conf})"

        # calculate analytical greeks for spot <spot> strike <strike> expiry <t> rate <r> vol <v> [type <type>] into <target>
        greeks_m = re.match(
            r"^calculate\s+(?:analytical\s+)?greeks\s+for\s+spot\s+(.+?)\s+strike\s+(.+?)\s+expiry\s+(.+?)\s+rate\s+(.+?)\s+vol\s+(.+?)(?:\s+type\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if greeks_m:
            spot, strike, t, r, v = greeks_m.group(1).strip(), greeks_m.group(2).strip(), greeks_m.group(3).strip(), greeks_m.group(4).strip(), greeks_m.group(5).strip()
            opt_type = greeks_m.group(6).strip() if greeks_m.group(6) else '"call"'
            target = greeks_m.group(7).strip()
            return f"set {target} to finance_analytical_greeks({spot}, {strike}, {t}, {r}, {v}, option_type={opt_type})"

        # calculate binomial price for spot <spot> strike <strike> expiry <t> rate <r> vol <v> [steps <steps>] [type <type>] [american] into <target>
        binom_m = re.match(
            r"^calculate\s+binomial\s+price\s+for\s+spot\s+(.+?)\s+strike\s+(.+?)\s+expiry\s+(.+?)\s+rate\s+(.+?)\s+vol\s+(.+?)(?:\s+steps\s+(\d+))?(?:\s+type\s+([\"']?\w+[\"']?))?(?:\s+(american))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if binom_m:
            spot, strike, t, r, v = binom_m.group(1).strip(), binom_m.group(2).strip(), binom_m.group(3).strip(), binom_m.group(4).strip(), binom_m.group(5).strip()
            steps = binom_m.group(6).strip() if binom_m.group(6) else "100"
            opt_type = binom_m.group(7).strip() if binom_m.group(7) else '"put"'
            is_amer = "True" if binom_m.group(8) else "False"
            target = binom_m.group(9).strip()
            return f"set {target} to finance_binomial_price({spot}, {strike}, {t}, {r}, {v}, steps={steps}, option_type={opt_type}, is_american={is_amer})"

        # simulate vasicek rate from r0 <r0> speed <a> mean <b> vol <sigma> expiry <t> into <target>
        m_vas = re.match(
            r"^simulate\s+vasicek\s+rate\s+from\s+r0\s+(.+?)\s+speed\s+(.+?)\s+mean\s+(.+?)\s+vol\s+(.+?)\s+expiry\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vas:
            r0, a, b, sigma, t, target = m_vas.group(1).strip(), m_vas.group(2).strip(), m_vas.group(3).strip(), m_vas.group(4).strip(), m_vas.group(5).strip(), m_vas.group(6).strip()
            return f"set {target} to fin_vasicek_simulate({r0}, {a}, {b}, {sigma}, {t})"

        # analyze bond duration with face <f> coupon <c> maturity <t> ytm <y> into <target>
        m_bond = re.match(
            r"^analyze\s+bond\s+duration\s+with\s+face\s+(.+?)\s+coupon\s+(.+?)\s+maturity\s+(.+?)\s+ytm\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bond:
            f, c, t, y, target = m_bond.group(1).strip(), m_bond.group(2).strip(), m_bond.group(3).strip(), m_bond.group(4).strip(), m_bond.group(5).strip()
            return f"set {target} to fin_bond_duration_convexity({f}, {c}, {t}, {y})"

        # simulate heston volatility spot <s0> vol <v0> kappa <k> theta <th> xi <xi> rho <rho> into <target>
        m_heston = re.match(
            r"^simulate\s+heston\s+volatility\s+spot\s+(.+?)\s+vol\s+(.+?)\s+kappa\s+(.+?)\s+theta\s+(.+?)\s+xi\s+(.+?)\s+rho\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_heston:
            s0, v0, k, th, xi, rho, target = m_heston.group(1).strip(), m_heston.group(2).strip(), m_heston.group(3).strip(), m_heston.group(4).strip(), m_heston.group(5).strip(), m_heston.group(6).strip(), m_heston.group(7).strip()
            return f"set {target} to fin_heston_simulate({s0}, {v0}, {k}, {th}, {xi}, {rho})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Finance domain does not currently define declarative blocks")
