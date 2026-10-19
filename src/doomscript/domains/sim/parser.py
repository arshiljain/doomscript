"""Independent Domain Parser for Simulation & Optimization language constructs."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.sim.spec import SimulationSpec, OptimizationSpec


class SimDomainParser(DomainParser):
    """Independent parser for Simulation & Optimization syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        # inspect simulation <name> [into <target>]
        m = re.match(
            r"^inspect\s+simulation\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m:
            sim_name = m.group(1)
            target = m.group(2) or "sim_inspection"
            return f'set {target} to ({sim_name}["summary"])'

        # summarize uncertainty of <var> [into <target>]
        m_unc = re.match(
            r"^summarize\s+uncertainty\s+of\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_unc:
            var_name = m_unc.group(1)
            target = m_unc.group(2) or f"{var_name}_uncertainty"
            return f"set {target} to summarize_uncertainty({var_name})"

        # summarize <var> [into <target>]
        m2 = re.match(
            r"^summarize\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m2:
            var_name = m2.group(1)
            target = m2.group(2) or f"{var_name}_summary"
            return f"set {target} to summarize_metric({var_name})"

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        # run <n> trials of <sim> [into <target>]
        m_tr = re.match(
            r"^run\s+(\d+)\s+trials\s+of\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_tr:
            trials_cnt = int(m_tr.group(1))
            sim_name = m_tr.group(2)
            target = m_tr.group(3) or f"{sim_name}_trials"
            return f'set {target} to run_trials("{sim_name}", trials={trials_cnt})'

        # sweep <param> over <values> [for <sim>] [into <target>]
        m_sw = re.match(
            r"^sweep\s+([A-Za-z_]\w*)\s+over\s+(.+?)(?:\s+(?:for|on)\s+([A-Za-z_]\w+))?(?:\s+into\s+([A-Za-z_]\w+))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_sw:
            param = m_sw.group(1)
            values = m_sw.group(2).strip()
            sim_name = m_sw.group(3) or ""
            target = m_sw.group(4) or f"{param}_sweep"
            return f'set {target} to sweep_parameter("{sim_name}", "{param}", {values})'

        # sample normal with mean <m> and std <s> [count <n>] into <target>
        s_norm_m = re.match(
            r"^sample\s+normal\s+with\s+mean\s+([-\d.]+)\s+and\s+std\s+([-\d.]+)(?:\s+count\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if s_norm_m:
            m = float(s_norm_m.group(1))
            s = float(s_norm_m.group(2))
            count = int(s_norm_m.group(3)) if s_norm_m.group(3) else 1000
            target = s_norm_m.group(4)
            return f"set {target} to sim_sample_normal({m}, {s}, {count})"

        # sample uniform between <a> and <b> [count <n>] into <target>
        s_uni_m = re.match(
            r"^sample\s+uniform\s+between\s+([-\d.]+)\s+and\s+([-\d.]+)(?:\s+count\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if s_uni_m:
            a = float(s_uni_m.group(1))
            b = float(s_uni_m.group(2))
            count = int(s_uni_m.group(3)) if s_uni_m.group(3) else 1000
            target = s_uni_m.group(4)
            return f"set {target} to sim_sample_uniform({a}, {b}, {count})"

        # sample <dist> with rate <r> [count <n>] into <target>
        s_rate_m = re.match(
            r"^sample\s+([A-Za-z_]\w+)\s+with\s+rate\s+(\d+(?:\.\d+)?)(?:\s+count\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if s_rate_m:
            dist = s_rate_m.group(1).lower()
            rate = float(s_rate_m.group(2))
            count = int(s_rate_m.group(3)) if s_rate_m.group(3) else 1000
            target = s_rate_m.group(4)
            return f'set {target} to sample_distribution("{dist}", {{"rate": {rate}}}, {count})'

        # optimize <fn> [starting at <guess>] into <target>
        opt_m = re.match(
            r"^optimize\s+([A-Za-z_]\w*)(?:\s+starting\s+at\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if opt_m:
            fn_name = opt_m.group(1)
            guess = opt_m.group(2) or "[0.0]"
            target = opt_m.group(3)
            return f'set {target} to optimize_function("{fn_name}", initial_guess={guess})'

        # simulate random walk with <steps> steps [starting at <start>] [with step size <size>] into <target>
        rw_m = re.match(
            r"^simulate\s+random\s+walk\s+with\s+(.+?)\s+steps?(?:\s+starting\s+at\s+(.+?))?(?:\s+with\s+step\s+size\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if rw_m:
            steps, start, step_size, target = rw_m.group(1).strip(), rw_m.group(2), rw_m.group(3), rw_m.group(4).strip()
            start_arg = f", start={start.strip()}" if start else ""
            size_arg = f", step_size={step_size.strip()}" if step_size else ""
            return f"set {target} to sim_random_walk({steps}{start_arg}{size_arg})"

        # generate exponential sample with rate <rate> into <target>
        exp_m = re.match(
            r"^generate\s+exponential\s+sample\s+with\s+rate\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if exp_m:
            rate, target = exp_m.group(1).strip(), exp_m.group(2).strip()
            return f"set {target} to sim_exponential({rate})"

        # generate poisson sample with lambda/rate <lam> into <target>
        poi_m = re.match(
            r"^generate\s+poisson\s+sample\s+with\s+(?:lambda|rate)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if poi_m:
            lam, target = poi_m.group(1).strip(), poi_m.group(2).strip()
            return f"set {target} to sim_poisson({lam})"

        # estimate pi with <samples> monte carlo samples into <target>
        pi_m = re.match(
            r"^estimate\s+pi\s+with\s+(.+?)\s+monte\s+carlo\s+samples\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if pi_m:
            samples, target = pi_m.group(1).strip(), pi_m.group(2).strip()
            return f"set {target} to sim_monte_carlo_pi({samples})"

        # roll <count> dice with <sides> sides into <target>
        dice_m = re.match(
            r"^roll\s+(.+?)\s+dice\s+with\s+(.+?)\s+sides?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if dice_m:
            count, sides, target = dice_m.group(1).strip(), dice_m.group(2).strip(), dice_m.group(3).strip()
            return f"set {target} to sim_roll_dice({count}, {sides})"

        # simulate <count> coin tosses with probability <p> into <target>
        coin_m = re.match(
            r"^simulate\s+(.+?)\s+coin\s+tosses\s+with\s+probability\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if coin_m:
            count, p, target = coin_m.group(1).strip(), coin_m.group(2).strip(), coin_m.group(3).strip()
            return f"set {target} to sim_coin_tosses({count}, {p})"

        # simulate markov step from <curr> with transitions <matrix> states <states> into <target>
        m_mstep = re.match(
            r"^simulate\s+markov\s+step\s+from\s+(.+?)\s+with\s+transitions\s+(.+?)\s+states\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_mstep:
            curr, mat, st, target = m_mstep.group(1).strip(), m_mstep.group(2).strip(), m_mstep.group(3).strip(), m_mstep.group(4).strip()
            return f"set {target} to sim_markov_chain_step({curr}, {mat}, {st})"

        # simulate markov walk of <steps> steps from <start> with transitions <matrix> states <states> into <target>
        m_mwalk = re.match(
            r"^simulate\s+markov\s+walk\s+of\s+(.+?)\s+steps\s+from\s+(.+?)\s+with\s+transitions\s+(.+?)\s+states\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_mwalk:
            steps, start, mat, st, target = m_mwalk.group(1).strip(), m_mwalk.group(2).strip(), m_mwalk.group(3).strip(), m_mwalk.group(4).strip(), m_mwalk.group(5).strip()
            return f"set {target} to sim_markov_chain_walk({start}, {mat}, {st}, {steps})"

        # sample <count> from geometric distribution with p <p> into <target>
        m_geom = re.match(
            r"^sample\s+(.+?)\s+from\s+geometric\s+distribution\s+with\s+p\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_geom:
            count, p, target = m_geom.group(1).strip(), m_geom.group(2).strip(), m_geom.group(3).strip()
            return f"set {target} to sim_sample_geometric({p}, {count})"

        # sample <count> from binomial distribution with n <n> p <p> into <target>
        m_bin = re.match(
            r"^sample\s+(.+?)\s+from\s+binomial\s+distribution\s+with\s+n\s+(.+?)\s+p\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bin:
            count, n, p, target = m_bin.group(1).strip(), m_bin.group(2).strip(), m_bin.group(3).strip(), m_bin.group(4).strip()
            return f"set {target} to sim_sample_binomial({n}, {p}, {count})"

        # sample <count> from triangular distribution low <low> high <high> mode <mode> into <target>
        m_tri = re.match(
            r"^sample\s+(.+?)\s+from\s+triangular\s+distribution\s+low\s+(.+?)\s+high\s+(.+?)\s+mode\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_tri:
            count, lo, hi, md, target = m_tri.group(1).strip(), m_tri.group(2).strip(), m_tri.group(3).strip(), m_tri.group(4).strip(), m_tri.group(5).strip()
            return f"set {target} to sim_sample_triangular({lo}, {hi}, {md}, {count})"

        # bootstrap confidence interval for mean of <data> [with <n> bootstraps] [confidence <conf>] into <target>
        m_boot = re.match(
            r"^bootstrap\s+confidence\s+interval\s+for\s+mean\s+of\s+(.+?)(?:\s+with\s+(\d+)\s+bootstraps)?(?:\s+confidence\s+([0-9.]+))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_boot:
            data = m_boot.group(1).strip()
            b_cnt = m_boot.group(2)
            conf = m_boot.group(3)
            target = m_boot.group(4).strip()
            b_val = b_cnt if b_cnt else "1000"
            c_val = conf if conf else "0.95"
            return f"set {target} to sim_bootstrap_mean_ci({data}, {b_val}, {c_val})"

        # permutation test between <g1> and <g2> [with <n> permutations] into <target>
        m_perm = re.match(
            r"^permutation\s+test\s+between\s+(.+?)\s+and\s+(.+?)(?:\s+with\s+(\d+)\s+permutations)?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_perm:
            g1, g2, p_cnt, target = m_perm.group(1).strip(), m_perm.group(2).strip(), m_perm.group(3), m_perm.group(4).strip()
            p_val = p_cnt if p_cnt else "1000"
            return f"set {target} to sim_permutation_test({g1}, {g2}, {p_val})"

        # simulate mm1 queue arrival rate <ar> service rate <sr> [duration <dur>] into <target>
        m_mm1 = re.match(
            r"^simulate\s+mm1\s+queue\s+arrival\s+rate\s+(.+?)\s+service\s+rate\s+(.+?)(?:\s+duration\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_mm1:
            ar, sr, dur, target = m_mm1.group(1).strip(), m_mm1.group(2).strip(), m_mm1.group(3), m_mm1.group(4).strip()
            d_val = dur.strip() if dur else "100.0"
            return f"set {target} to sim_mm1_queue({ar}, {sr}, {d_val})"

        # simulate wiener process [time <t>] [steps <steps>] [mu <mu>] [sigma <sigma>] into <target>
        m_wien = re.match(
            r"^simulate\s+wiener\s+process(?:\s+time\s+(.+?))?(?:\s+steps\s+(\d+))?(?:\s+mu\s+(.+?))?(?:\s+sigma\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_wien:
            t = m_wien.group(1)
            steps = m_wien.group(2)
            mu = m_wien.group(3)
            sig = m_wien.group(4)
            target = m_wien.group(5).strip()
            t_val = t.strip() if t else "1.0"
            s_val = steps if steps else "100"
            mu_val = mu.strip() if mu else "0.0"
            sig_val = sig.strip() if sig else "1.0"
            return f"set {target} to sim_wiener_process({t_val}, {s_val}, {mu_val}, {sig_val})"

        # simulate bernoulli trial with p <p> into <target>
        m_bern = re.match(
            r"^simulate\s+bernoulli\s+trial\s+with\s+p\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bern:
            p, target = m_bern.group(1).strip(), m_bern.group(2).strip()
            return f"set {target} to sim_bernoulli_trial({p})"

        # sample <count> from lognormal distribution mean <mean> std <std> into <target>
        m_logn = re.match(
            r"^sample\s+(.+?)\s+from\s+lognormal\s+distribution\s+mean\s+(.+?)\s+std\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_logn:
            count, mean, std, target = m_logn.group(1).strip(), m_logn.group(2).strip(), m_logn.group(3).strip(), m_logn.group(4).strip()
            return f"set {target} to sim_sample_lognormal({mean}, {std}, {count})"

        # integrate <fn> via monte carlo from <a> to <b> [with <n> samples] into <target>
        m_mcint = re.match(
            r"^integrate\s+(.+?)\s+via\s+monte\s+carlo\s+from\s+(.+?)\s+to\s+(.+?)(?:\s+with\s+(\d+)\s+samples)?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_mcint:
            fn, a, b, s_cnt, target = m_mcint.group(1).strip(), m_mcint.group(2).strip(), m_mcint.group(3).strip(), m_mcint.group(4), m_mcint.group(5).strip()
            s_val = s_cnt if s_cnt else "10000"
            return f"set {target} to sim_monte_carlo_integral({fn}, {a}, {b}, {s_val})"

        # estimate expected value and variance of <samples> into <target>
        m_expv = re.match(
            r"^estimate\s+expected\s+value\s+and\s+variance\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_expv:
            samples, target = m_expv.group(1).strip(), m_expv.group(2).strip()
            return f"set {target} to sim_estimate_expected_value({samples})"

        # calculate birthday paradox probability for <n> people into <target>
        m_bday = re.match(
            r"^calculate\s+birthday\s+paradox\s+probability\s+for\s+(.+?)\s+people\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_bday:
            n, target = m_bday.group(1).strip(), m_bday.group(2).strip()
            return f"set {target} to sim_birthday_paradox_prob({n})"

        # estimate coupon collector trials for <n> coupons [with <t> trials] into <target>
        m_ccol = re.match(
            r"^estimate\s+coupon\s+collector\s+trials\s+for\s+(.+?)\s+coupons?(?:\s+with\s+(\d+)\s+trials)?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_ccol:
            n, t_cnt, target = m_ccol.group(1).strip(), m_ccol.group(2), m_ccol.group(3).strip()
            t_val = t_cnt if t_cnt else "100"
            return f"set {target} to sim_coupon_collector_estimate({n}, {t_val})"

        # shuffle standard deck of cards into <target>
        m_sdeck = re.match(
            r"^shuffle\s+(?:standard\s+)?deck(?:\s+of\s+cards)?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_sdeck:
            target = m_sdeck.group(1).strip()
            return f"set {target} to sim_shuffle_deck()"

        # draw <n> cards from deck <deck> into <target>
        m_dcards = re.match(
            r"^draw\s+(.+?)\s+cards\s+from\s+deck\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_dcards:
            n, deck, target = m_dcards.group(1).strip(), m_dcards.group(2).strip(), m_dcards.group(3).strip()
            return f"set {target} to sim_draw_cards({deck}, {n})"

        # sample <count> from weibull distribution shape <k> scale <lam> into <target>
        m_weib = re.match(
            r"^sample\s+(.+?)\s+from\s+weibull\s+distribution\s+shape\s+(.+?)\s+scale\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_weib:
            count, k, lam, target = m_weib.group(1).strip(), m_weib.group(2).strip(), m_weib.group(3).strip(), m_weib.group(4).strip()
            return f"set {target} to sim_sample_weibull({k}, {lam}, {count})"

        # generate synthetic timeline start <st> intervals <intervals> into <target>
        m_time = re.match(
            r"^generate\s+synthetic\s+timeline\s+start\s+(.+?)\s+intervals\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_time:
            st, intervals, target = m_time.group(1).strip(), m_time.group(2).strip(), m_time.group(3).strip()
            return f"set {target} to sim_generate_synthetic_timeline({st}, {intervals})"

        # calculate kaplan meier survival for durations <dur> events <ev> into <target>
        m_km = re.match(
            r"^calculate\s+kaplan\s+meier\s+survival\s+for\s+durations\s+(.+?)\s+events\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_km:
            dur, ev, target = m_km.group(1).strip(), m_km.group(2).strip(), m_km.group(3).strip()
            return f"set {target} to sim_survival_rate_kaplan_meier({dur}, {ev})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[SimulationSpec, str]:
        # simulate <name> [into <target>]:
        m = re.match(
            r"^simulate\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?:?$",
            header.strip(),
            re.IGNORECASE,
        )
        if not m:
            raise SyntaxError(f"Invalid simulation header: {header}")

        sim_name = m.group(1)
        target = m.group(2) or sim_name

        spec = SimulationSpec(name=sim_name, target_var=target)

        for l_no, raw_line in body_lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # arrivals: (poisson|exponential) with rate <r>
            arr_m = re.match(
                r"^arrivals\s*:\s*([A-Za-z_]\w+)(?:\s+with\s+rate\s+(\d+(?:\.\d+)?))?",
                line,
                re.IGNORECASE,
            )
            if arr_m:
                spec.arrival_dist = arr_m.group(1).lower()
                rate = float(arr_m.group(2)) if arr_m.group(2) else 10.0
                spec.arrival_params = {"rate": rate}
                continue

            # service: (exponential|normal) with rate <r>
            srv_m = re.match(
                r"^service\s*:\s*([A-Za-z_]\w+)(?:\s+with\s+rate\s+(\d+(?:\.\d+)?))?",
                line,
                re.IGNORECASE,
            )
            if srv_m:
                spec.service_dist = srv_m.group(1).lower()
                rate = float(srv_m.group(2)) if srv_m.group(2) else 12.0
                spec.service_params = {"rate": rate}
                continue

            # duration: <n> events
            dur_m = re.match(r"^duration\s*:\s*(\d+)", line, re.IGNORECASE)
            if dur_m:
                spec.duration = int(dur_m.group(1))
                continue

            # servers: <n>
            srv_cnt_m = re.match(r"^servers\s*:\s*(\d+)", line, re.IGNORECASE)
            if srv_cnt_m:
                spec.servers = int(srv_cnt_m.group(1))
                continue

            # seed: <n>
            seed_m = re.match(r"^seed\s*(?::|\s+simulation\s+with)\s*(\d+)", line, re.IGNORECASE)
            if seed_m:
                spec.seed = int(seed_m.group(1))
                continue

        errors = spec.validate()
        if errors:
            raise SyntaxError(f"Simulation validation error for '{sim_name}': {'; '.join(errors)}")

        return spec, target
