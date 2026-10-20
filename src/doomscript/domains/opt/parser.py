"""Independent Domain Parser for Optimization & Operations Research language constructs."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.opt.spec import LinearProgramSpec, SolveLPSpec


class OptDomainParser(DomainParser):
    """Independent parser for Optimization and Linear Programming syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # create linear program into <target>
        m_clp = re.match(
            r"^create\s+linear\s+program\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_clp:
            target = m_clp.group(1).strip()
            return f"set {target} to opt_create_linear_program()"

        # solve [linear program] <name> into <target>
        m_solve = re.match(
            r"^solve(?:\s+linear\s+program)?\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_solve:
            lp_name = m_solve.group(1).strip()
            target = m_solve.group(2).strip()
            return f'set {target} to solve_linear_program("{lp_name}")'

        # minimize 1d [function] <fn> from <a> to <b> [with tolerance <tol>] into <target>
        min1d_m = re.match(
            r"^minimize\s+1d\s+(?:function\s+)?(.+?)\s+from\s+(.+?)\s+to\s+(.+?)(?:\s+with\s+tolerance\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if min1d_m:
            fn, a, b, tol, target = min1d_m.group(1).strip(), min1d_m.group(2).strip(), min1d_m.group(3).strip(), min1d_m.group(4), min1d_m.group(5).strip()
            tol_arg = f", tol={tol.strip()}" if tol else ""
            return f"set {target} to opt_minimize_1d({fn}, {a}, {b}{tol_arg})"

        # grid search [params] <grid> with <score_fn> into <target>
        gs_m = re.match(
            r"^grid\s+search\s+(?:params\s+)?(.+?)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if gs_m:
            grid, fn, target = gs_m.group(1).strip(), gs_m.group(2).strip(), gs_m.group(3).strip()
            return f"set {target} to opt_grid_search({grid}, {fn})"

        # solve fractional knapsack [items|weights] <weights> values <values> capacity <cap> into <target>
        knap_m = re.match(
            r"^solve\s+fractional\s+knapsack\s+(?:items\s+|weights\s+)?(.+?)\s+values\s+(.+?)\s+capacity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if knap_m:
            w, v, cap, target = knap_m.group(1).strip(), knap_m.group(2).strip(), knap_m.group(3).strip(), knap_m.group(4).strip()
            return f"set {target} to opt_fractional_knapsack({w}, {v}, {cap})"

        # schedule activities with <start_times> and <end_times> into <target>
        act_m = re.match(
            r"^schedule\s+activities\s+with\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if act_m:
            s_times, e_times, target = act_m.group(1).strip(), act_m.group(2).strip(), act_m.group(3).strip()
            return f"set {target} to opt_activity_selection({s_times}, {e_times})"

        # gradient descent step at <pt> with gradient <grad> [learning_rate <lr>] into <target>
        gd_m = re.match(
            r"^gradient\s+descent\s+step\s+at\s+(.+?)\s+with\s+gradient\s+(.+?)(?:\s+(?:learning_rate|lr)\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if gd_m:
            pt, grad, lr, target = gd_m.group(1).strip(), gd_m.group(2).strip(), gd_m.group(3), gd_m.group(4).strip()
            lr_arg = f", learning_rate={lr.strip()}" if lr else ""
            return f"set {target} to opt_gradient_descent_step({pt}, {grad}{lr_arg})"

        # find root of [function] <fn> between <a> and <b> [with tolerance <tol>] into <target>
        root_m = re.match(
            r"^find\s+root\s+of\s+(?:function\s+)?(.+?)\s+between\s+(.+?)\s+and\s+(.+?)(?:\s+with\s+tolerance\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if root_m:
            fn, a, b, tol, target = root_m.group(1).strip(), root_m.group(2).strip(), root_m.group(3).strip(), root_m.group(4), root_m.group(5).strip()
            tol_arg = f", tol={tol.strip()}" if tol else ""
            return f"set {target} to opt_bisection_root({fn}, {a}, {b}{tol_arg})"

        # simulated annealing for <cost_fn> starting at <init> [with temp <temp>] [cooling <cool>] into <target>
        m_sa = re.match(
            r"^simulated\s+annealing\s+for\s+(.+?)\s+starting\s+at\s+(.+?)(?:\s+with\s+temp\s+(.+?))?(?:\s+cooling\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sa:
            fn, init, temp, cool, target = m_sa.group(1).strip(), m_sa.group(2).strip(), m_sa.group(3), m_sa.group(4), m_sa.group(5).strip()
            t_val = temp.strip() if temp else "100.0"
            c_val = cool.strip() if cool else "0.95"
            return f"set {target} to opt_simulated_annealing({fn}, {init}, None, {t_val}, {c_val})"

        # golden section search for <fn> between <a> and <b> [with tolerance <tol>] into <target>
        m_gss = re.match(
            r"^golden\s+section\s+search\s+for\s+(.+?)\s+between\s+(.+?)\s+and\s+(.+?)(?:\s+with\s+tolerance\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_gss:
            fn, a, b, tol, target = m_gss.group(1).strip(), m_gss.group(2).strip(), m_gss.group(3).strip(), m_gss.group(4), m_gss.group(5).strip()
            tol_val = tol.strip() if tol else "1e-5"
            return f"set {target} to opt_golden_section_search({fn}, {a}, {b}, {tol_val})"

        # solve 01 knapsack weights <weights> values <values> capacity <cap> into <target>
        m_ks01 = re.match(
            r"^solve\s+01\s+knapsack\s+weights\s+(.+?)\s+values\s+(.+?)\s+capacity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ks01:
            w, v, cap, target = m_ks01.group(1).strip(), m_ks01.group(2).strip(), m_ks01.group(3).strip(), m_ks01.group(4).strip()
            return f"set {target} to opt_knapsack_01_dp({w}, {v}, {cap})"

        # longest increasing subsequence of <arr> into <target>
        m_lis = re.match(
            r"^longest\s+increasing\s+subsequence\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lis:
            arr, target = m_lis.group(1).strip(), m_lis.group(2).strip()
            return f"set {target} to opt_longest_increasing_subsequence({arr})"

        # minimum coins for amount <amount> with coins <coins> into <target>
        m_mc = re.match(
            r"^minimum\s+coins\s+for\s+amount\s+(.+?)\s+with\s+coins\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mc:
            amt, coins, target = m_mc.group(1).strip(), m_mc.group(2).strip(), m_mc.group(3).strip()
            return f"set {target} to opt_coin_change_minimum({coins}, {amt})"

        # coin combinations for amount <amount> with coins <coins> into <target>
        m_cc = re.match(
            r"^coin\s+combinations\s+for\s+amount\s+(.+?)\s+with\s+coins\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cc:
            amt, coins, target = m_cc.group(1).strip(), m_cc.group(2).strip(), m_cc.group(3).strip()
            return f"set {target} to opt_coin_change_combinations({coins}, {amt})"

        # schedule jobs by deadline <jobs> into <target>
        m_sj = re.match(
            r"^schedule\s+jobs\s+by\s+deadline\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sj:
            jobs, target = m_sj.group(1).strip(), m_sj.group(2).strip()
            return f"set {target} to opt_job_scheduling_deadline({jobs})"

        # huffman encoding for frequencies <freqs> into <target>
        m_he = re.match(
            r"^huffman\s+encoding\s+for\s+frequencies\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_he:
            freqs, target = m_he.group(1).strip(), m_he.group(2).strip()
            return f"set {target} to opt_huffman_encoding({freqs})"

        # matrix chain multiplication order for dimensions <dims> into <target>
        m_mcm = re.match(
            r"^matrix\s+chain\s+multiplication\s+(?:order\s+)?for\s+dimensions\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mcm:
            dims, target = m_mcm.group(1).strip(), m_mcm.group(2).strip()
            return f"set {target} to opt_matrix_chain_multiplication({dims})"

        # levenshtein alignment between <s1> and <s2> into <target>
        m_la = re.match(
            r"^levenshtein\s+alignment\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_la:
            s1, s2, target = m_la.group(1).strip(), m_la.group(2).strip(), m_la.group(3).strip()
            return f"set {target} to opt_levenshtein_alignment({s1}, {s2})"

        # check if subset sum exists in <arr> for target <target_sum> into <target>
        m_sse = re.match(
            r"^check\s+if\s+subset\s+sum\s+exists\s+in\s+(.+?)\s+for\s+target\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sse:
            arr, target_sum, target = m_sse.group(1).strip(), m_sse.group(2).strip(), m_sse.group(3).strip()
            return f"set {target} to opt_subset_sum_exists({arr}, {target_sum})"

        # find subset summing to <target_sum> from <arr> into <target>
        m_ssf = re.match(
            r"^find\s+subset\s+summing\s+to\s+(.+?)\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ssf:
            target_sum, arr, target = m_ssf.group(1).strip(), m_ssf.group(2).strip(), m_ssf.group(3).strip()
            return f"set {target} to opt_subset_sum_find({arr}, {target_sum})"

        # solve rod cutting for length <len> with prices <prices> into <target>
        m_rc = re.match(
            r"^solve\s+rod\s+cutting\s+for\s+length\s+(.+?)\s+with\s+prices\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rc:
            length, prices, target = m_rc.group(1).strip(), m_rc.group(2).strip(), m_rc.group(3).strip()
            return f"set {target} to opt_rod_cutting({prices}, {length})"

        # optimize tsp with 2opt for coordinates <coords> [iterations <iter>] into <target>
        m_tsp = re.match(
            r"^optimize\s+tsp\s+with\s+2opt\s+for\s+coordinates\s+(.+?)(?:\s+iterations\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tsp:
            coords, iters, target = m_tsp.group(1).strip(), m_tsp.group(2), m_tsp.group(3).strip()
            iter_val = iters if iters else "100"
            return f"set {target} to opt_two_opt_tsp({coords}, {iter_val})"

        # interpolate linear value at <tx> from x <x_pts> and y <y_pts> into <target>
        m_li = re.match(
            r"^interpolate\s+linear\s+value\s+at\s+(.+?)\s+from\s+x\s+(.+?)\s+and\s+y\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_li:
            tx, x_pts, y_pts, target = m_li.group(1).strip(), m_li.group(2).strip(), m_li.group(3).strip(), m_li.group(4).strip()
            return f"set {target} to opt_linear_interpolation({x_pts}, {y_pts}, {tx})"

        # weighted interval scheduling for <intervals> into <target>
        m_wis = re.match(
            r"^weighted\s+interval\s+scheduling\s+for\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_wis:
            intervals, target = m_wis.group(1).strip(), m_wis.group(2).strip()
            return f"set {target} to opt_weighted_interval_scheduling({intervals})"

        # find pareto frontier for <points> into <target>
        m_pf = re.match(
            r"^find\s+pareto\s+frontier\s+for\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pf:
            points, target = m_pf.group(1).strip(), m_pf.group(2).strip()
            return f"set {target} to opt_pareto_frontier({points})"

        # hungarian assignment for cost matrix <matrix> into <target>
        m_ha = re.match(
            r"^hungarian\s+assignment\s+for\s+cost\s+matrix\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ha:
            matrix, target = m_ha.group(1).strip(), m_ha.group(2).strip()
            return f"set {target} to opt_hungarian_assignment({matrix})"

        # find peak element in <arr> into <target>
        m_pk = re.match(
            r"^find\s+peak\s+element\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pk:
            arr, target = m_pk.group(1).strip(), m_pk.group(2).strip()
            return f"set {target} to opt_binary_search_peak_1d({arr})"

        # optimize particle swarm objective <obj> bounds <bounds> [with particles <n>] [with iterations <max_it>] into <target>
        m_pso = re.match(
            r"^optimize\s+particle\s+swarm\s+objective\s+(.+?)\s+bounds\s+(.+?)(?:\s+with\s+particles\s+(\d+))?(?:\s+with\s+iterations\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pso:
            obj, bnds = m_pso.group(1).strip(), m_pso.group(2).strip()
            if not (obj.startswith('"') or obj.startswith("'")):
                obj = f'"{obj}"'
            n_part = m_pso.group(3) if m_pso.group(3) else "30"
            max_it = m_pso.group(4) if m_pso.group(4) else "50"
            target = m_pso.group(5).strip()
            return f"set {target} to opt_particle_swarm_optimize({obj}, {bnds}, num_particles={n_part}, max_iterations={max_it})"

        # solve quadratic program active set q <q> c <c> [with ineq_matrix <a>] [with ineq_vec <b>] into <target>
        m_qp = re.match(
            r"^solve\s+quadratic\s+program\s+active\s+set\s+q\s+(.+?)\s+c\s+(.+?)(?:\s+with\s+ineq_matrix\s+(.+?))?(?:\s+with\s+ineq_vec\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_qp:
            q, c = m_qp.group(1).strip(), m_qp.group(2).strip()
            a_ineq = m_qp.group(3).strip() if m_qp.group(3) else "None"
            b_ineq = m_qp.group(4).strip() if m_qp.group(4) else "None"
            target = m_qp.group(5).strip()
            return f"set {target} to opt_solve_quadratic_program_active_set({q}, {c}, ineq_matrix={a_ineq}, ineq_vec={b_ineq})"

        # nelder mead minimize <fn> starting at <pt> [step <step>] [tol <tol>] into <target>
        m_nm = re.match(
            r"^nelder\s+mead\s+minimize\s+(.+?)\s+starting\s+at\s+(.+?)(?:\s+step\s+(.+?))?(?:\s+tol\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_nm:
            fn, pt, st, tl, target = m_nm.group(1).strip(), m_nm.group(2).strip(), m_nm.group(3), m_nm.group(4), m_nm.group(5).strip()
            if not (fn.startswith('"') or fn.startswith("'") or fn.isidentifier()):
                fn = f'"{fn}"'
            st_val = st.strip() if st else "0.05"
            tl_val = tl.strip() if tl else "1e-6"
            return f"set {target} to opt_nelder_mead_minimize({fn}, {pt}, step_size={st_val}, tol={tl_val})"

        # solve interior point lp c <c> a <a> b <b> into <target>
        m_ip = re.match(
            r"^solve\s+interior\s+point\s+lp\s+c\s+(.+?)\s+a\s+(.+?)\s+b\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ip:
            c, a, b, target = m_ip.group(1).strip(), m_ip.group(2).strip(), m_ip.group(3).strip(), m_ip.group(4).strip()
            return f"set {target} to opt_interior_point_solve_lp({c}, {a}, {b})"

        # optimize with cma_es <obj> starting at <pt> [sigma <sig>] [generations <gen>] into <target>
        m_cma = re.match(
            r"^optimize\s+with\s+cma_es\s+(.+?)\s+starting\s+at\s+(.+?)(?:\s+sigma\s+(.+?))?(?:\s+generations\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cma:
            obj, pt, sig, gen, target = m_cma.group(1).strip(), m_cma.group(2).strip(), m_cma.group(3), m_cma.group(4), m_cma.group(5).strip()
            if not (obj.startswith('"') or obj.startswith("'") or obj.isidentifier()):
                obj = f'"{obj}"'
            s_val = sig.strip() if sig else "0.5"
            g_val = gen.strip() if gen else "40"
            return f"set {target} to opt_cma_es_optimize({obj}, {pt}, initial_sigma={s_val}, max_generations={g_val})"

        # minimize nelder mead <objective> from <initial_point> [step <step>] [tol <tol>] into <target>
        m_nm = re.match(
            r"^minimize\s+nelder\s+mead\s+(.+?)\s+from\s+(.+?)(?:\s+step\s+(.+?))?(?:\s+tol\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_nm:
            obj, pt, step, tol, target = m_nm.group(1).strip(), m_nm.group(2).strip(), m_nm.group(3), m_nm.group(4), m_nm.group(5).strip()
            if not (obj.startswith('"') or obj.startswith("'") or obj.isidentifier()):
                obj = f'"{obj}"'
            step_arg = f", step_size={step.strip()}" if step else ""
            tol_arg = f", tol={tol.strip()}" if tol else ""
            return f"set {target} to opt_nelder_mead_minimize({obj}, {pt}{step_arg}{tol_arg})"

        # optimize sqp <objective> from <initial_point> [eq <eq>] [ineq <ineq>] into <target>
        m_sqp = re.match(
            r"^optimize\s+sqp\s+(.+?)\s+from\s+(.+?)(?:\s+eq\s+(.+?))?(?:\s+ineq\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sqp:
            obj, pt, eq, ineq, target = m_sqp.group(1).strip(), m_sqp.group(2).strip(), m_sqp.group(3), m_sqp.group(4), m_sqp.group(5).strip()
            if not (obj.startswith('"') or obj.startswith("'") or obj.isidentifier()):
                obj = f'"{obj}"'
            eq_arg = f", eq_constraints={eq.strip()}" if eq else ""
            ineq_arg = f", ineq_constraints={ineq.strip()}" if ineq else ""
            return f"set {target} to opt_sqp_optimize({obj}, {pt}{eq_arg}{ineq_arg})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[LinearProgramSpec, str]:
        # direct objective block: maximize/minimize <obj> [into <target>] [where]:
        h_strip = header.strip().rstrip(":")
        direct_m = re.match(r"^(maximize|minimize)\s+(.+)$", h_strip, re.IGNORECASE)
        if direct_m:
            sense = direct_m.group(1).lower()
            rest = direct_m.group(2).strip()
            target = "lp_solution"

            # Check for 'into <target>'
            into_match = re.search(r"\binto\s+([A-Za-z_]\w*)\b", rest, re.IGNORECASE)
            if into_match:
                target = into_match.group(1)
                rest = re.sub(r"\binto\s+[A-Za-z_]\w*\b", "", rest, flags=re.IGNORECASE).strip()

            # Remove optional 'where' keyword
            rest = re.sub(r"\bwhere\b", "", rest, flags=re.IGNORECASE).strip()
            obj_expr = rest

            lp_name = "direct_lp"
            spec = LinearProgramSpec(name=lp_name, target_var=target, sense=sense, objective=obj_expr)
            for _, raw_line in body_lines:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                into_m = re.match(r"^into\s+([A-Za-z_]\w*)$", line, re.IGNORECASE)
                if into_m:
                    target = into_m.group(1)
                    spec.target_var = target
                    continue
                if any(op in line for op in ("<=", ">=", "=", "<", ">")):
                    spec.constraints.append(line)
            errors = spec.validate()
            if errors:
                raise SyntaxError(f"Linear program validation error: {'; '.join(errors)}")
            return spec, target

        # linear program <name> [into <target>]:
        m = re.match(
            r"^(?:linear\s+program|optimize)\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?:?$",
            header.strip(),
            re.IGNORECASE,
        )
        if not m:
            raise SyntaxError(f"Invalid linear program block header: {header}")

        lp_name = m.group(1).strip()
        target = m.group(2) or lp_name

        spec = LinearProgramSpec(name=lp_name, target_var=target)
        in_constraints = False

        for _, raw_line in body_lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # maximize: <expr>
            max_m = re.match(r"^maximize\s*:\s*(.+)$", line, re.IGNORECASE)
            if max_m:
                spec.sense = "maximize"
                spec.objective = max_m.group(1).strip()
                in_constraints = False
                continue

            # minimize: <expr>
            min_m = re.match(r"^minimize\s*:\s*(.+)$", line, re.IGNORECASE)
            if min_m:
                spec.sense = "minimize"
                spec.objective = min_m.group(1).strip()
                in_constraints = False
                continue

            # subject to:
            if re.match(r"^subject\s+to\s*:?$", line, re.IGNORECASE):
                in_constraints = True
                continue

            # constraint line
            if in_constraints or any(op in line for op in ("<=", ">=", "=", "<", ">")):
                spec.constraints.append(line)

        errors = spec.validate()
        if errors:
            raise SyntaxError(f"Linear program validation error for '{lp_name}': {'; '.join(errors)}")

        return spec, target
