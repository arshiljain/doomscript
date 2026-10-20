"""Electronics Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class CircuitDomainParser(DomainParser):
    """Parses spoken-English electronics, logic gates, and circuit statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate voltage with current <i> and resistance <r> into <target>
        m_volt = re.match(
            r"^calculate\s+voltage\s+with\s+current\s+(.+?)\s+and\s+resistance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_volt:
            i = m_volt.group(1).strip()
            r = m_volt.group(2).strip()
            target = m_volt.group(3).strip()
            return f"set {target} to circuit_ohm_voltage({i}, {r})"

        # calculate current with voltage <v> and resistance <r> into <target>
        m_curr = re.match(
            r"^calculate\s+current\s+with\s+voltage\s+(.+?)\s+and\s+resistance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_curr:
            v = m_curr.group(1).strip()
            r = m_curr.group(2).strip()
            target = m_curr.group(3).strip()
            return f"set {target} to circuit_ohm_current({v}, {r})"

        # calculate resistance with voltage <v> and current <i> into <target>
        m_res = re.match(
            r"^calculate\s+resistance\s+with\s+voltage\s+(.+?)\s+and\s+current\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_res:
            v = m_res.group(1).strip()
            i = m_res.group(2).strip()
            target = m_res.group(3).strip()
            return f"set {target} to circuit_ohm_resistance({v}, {i})"

        # calculate power with voltage <v> and current <i> into <target>
        m_pow = re.match(
            r"^calculate\s+power\s+with\s+voltage\s+(.+?)\s+and\s+current\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pow:
            v = m_pow.group(1).strip()
            i = m_pow.group(2).strip()
            target = m_pow.group(3).strip()
            return f"set {target} to circuit_power({v}, {i})"

        # decode resistor colors <colors> into <target>
        m_bands = re.match(
            r"^decode\s+resistor\s+colors?\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bands:
            cols = m_bands.group(1).strip()
            target = m_bands.group(2).strip()
            return f"set {target} to circuit_decode_resistor_bands({cols})"

        # calculate voltage divider with vin <vin> and r1 <r1> and r2 <r2> into <target>
        m_vdiv = re.match(
            r"^calculate\s+voltage\s+divider\s+with\s+vin\s+(.+?)\s+and\s+r1\s+(.+?)\s+and\s+r2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vdiv:
            vin = m_vdiv.group(1).strip()
            r1 = m_vdiv.group(2).strip()
            r2 = m_vdiv.group(3).strip()
            target = m_vdiv.group(4).strip()
            return f"set {target} to circuit_voltage_divider({vin}, {r1}, {r2})"

        # calculate 555 timer frequency with r1 <r1> and r2 <r2> and c <c> into <target>
        m_555 = re.match(
            r"^calculate\s+555\s+timer\s+frequency\s+with\s+r1\s+(.+?)\s+and\s+r2\s+(.+?)\s+and\s+c\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_555:
            r1 = m_555.group(1).strip()
            r2 = m_555.group(2).strip()
            c = m_555.group(3).strip()
            target = m_555.group(4).strip()
            return f"set {target} to circuit_555_timer_freq({r1}, {r2}, {c})"

        # calculate rc time constant with r <r> and c <c> into <target>
        m_rc = re.match(
            r"^calculate\s+rc\s+time\s+constant\s+with\s+r\s+(.+?)\s+and\s+c\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rc:
            r = m_rc.group(1).strip()
            c = m_rc.group(2).strip()
            target = m_rc.group(3).strip()
            return f"set {target} to circuit_rc_time_constant({r}, {c})"

        # evaluate logic truth table for <expr> into <target>
        m_tt = re.match(
            r"^evaluate\s+logic\s+truth\s+table\s+for\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tt:
            expr = m_tt.group(1).strip()
            target = m_tt.group(2).strip()
            return f"set {target} to circuit_evaluate_truth_table({expr})"

        # calculate pwm duty cycle for high time <ht> and period <p> into <target>
        m_pwm = re.match(
            r"^calculate\s+pwm\s+duty\s+cycle\s+for\s+(?:high\s+time\s+)?(.+?)\s+and\s+period\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pwm:
            ht = m_pwm.group(1).strip()
            p = m_pwm.group(2).strip()
            target = m_pwm.group(3).strip()
            return f"set {target} to circuit_pwm_duty_cycle({ht}, {p})"

        # set gpio pin <pin> to <val> in <board>
        m_gpio_s = re.match(
            r"^set\s+gpio\s+pin\s+(.+?)\s+to\s+(.+?)\s+in\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_gpio_s:
            pin = m_gpio_s.group(1).strip()
            val = m_gpio_s.group(2).strip()
            board = m_gpio_s.group(3).strip()
            return f"circuit_gpio_set({board}, {pin}, {val})"

        # read gpio pin <pin> from <board> into <target>
        m_gpio_r = re.match(
            r"^read\s+gpio\s+pin\s+(.+?)\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_gpio_r:
            pin = m_gpio_r.group(1).strip()
            board = m_gpio_r.group(2).strip()
            target = m_gpio_r.group(3).strip()
            return f"set {target} to circuit_gpio_read({board}, {pin})"

        # solve diode circuit with v_source <vs> and resistance <r> into <target>
        m_diode = re.match(
            r"^solve\s+diode\s+circuit\s+with\s+v_source\s+(.+?)\s+and\s+resistance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_diode:
            vs, r, target = m_diode.group(1).strip(), m_diode.group(2).strip(), m_diode.group(3).strip()
            return f"set {target} to circuit_solve_diode({vs}, {r})"

        # analyze transmission line r <r> l <l> g <g> c <c> frequency <f> [with z_load <zl>] into <target>
        m_tline = re.match(
            r"^analyze\s+transmission\s+line\s+r\s+(.+?)\s+l\s+(.+?)\s+g\s+(.+?)\s+c\s+(.+?)\s+frequency\s+(.+?)(?:\s+with\s+z_load\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tline:
            r_val, l_val, g_val, c_val = m_tline.group(1).strip(), m_tline.group(2).strip(), m_tline.group(3).strip(), m_tline.group(4).strip()
            f_val = m_tline.group(5).strip()
            zl = m_tline.group(6).strip() if m_tline.group(6) else "50.0"
            target = m_tline.group(7).strip()
            return f"set {target} to circuit_transmission_line({r_val}, {l_val}, {g_val}, {c_val}, {f_val}, z_load_ohms={zl})"

        # simulate rlc step response with r <r> l <l> c <c> [with v_step <vs>] [with duration <dur>] into <target>
        m_rlc = re.match(
            r"^simulate\s+rlc\s+step\s+response\s+with\s+r\s+(.+?)\s+l\s+(.+?)\s+c\s+(.+?)(?:\s+with\s+v_step\s+(.+?))?(?:\s+with\s+duration\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rlc:
            r_val, l_val, c_val = m_rlc.group(1).strip(), m_rlc.group(2).strip(), m_rlc.group(3).strip()
            vs = m_rlc.group(4).strip() if m_rlc.group(4) else "5.0"
            dur = m_rlc.group(5).strip() if m_rlc.group(5) else "0.001"
            target = m_rlc.group(6).strip()
            return f"set {target} to circuit_simulate_rlc_step({r_val}, {l_val}, {c_val}, v_step={vs}, duration={dur})"

        # design sallen key filter type <type> cutoff <fc> [with q <q>] [with gain <k>] into <target>
        m_sk = re.match(
            r"^design\s+sallen\s+key\s+filter\s+type\s+(.+?)\s+cutoff\s+(.+?)(?:\s+with\s+q\s+(.+?))?(?:\s+with\s+gain\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sk:
            ftype = m_sk.group(1).strip()
            if not (ftype.startswith('"') or ftype.startswith("'")):
                ftype = f'"{ftype}"'
            fc = m_sk.group(2).strip()
            q_val = m_sk.group(3).strip() if m_sk.group(3) else "0.7071"
            gain_val = m_sk.group(4).strip() if m_sk.group(4) else "1.0"
            target = m_sk.group(5).strip()
            return f"set {target} to circuit_design_sallen_key({ftype}, {fc}, q_factor={q_val}, gain={gain_val})"

        # solve rlc laplace transient topology <topo> r <r> l <l> c <c> [with v_step <vs>] [with duration <dur>] into <target>
        m_rlc_lap = re.match(
            r"^solve\s+rlc\s+laplace\s+transient\s+topology\s+(.+?)\s+r\s+(.+?)\s+l\s+(.+?)\s+c\s+(.+?)(?:\s+with\s+v_step\s+(.+?))?(?:\s+with\s+duration\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rlc_lap:
            topo = m_rlc_lap.group(1).strip()
            if not (topo.startswith('"') or topo.startswith("'")):
                topo = f'"{topo}"'
            r_val = m_rlc_lap.group(2).strip()
            l_val = m_rlc_lap.group(3).strip()
            c_val = m_rlc_lap.group(4).strip()
            vs = m_rlc_lap.group(5).strip() if m_rlc_lap.group(5) else "1.0"
            dur = m_rlc_lap.group(6).strip() if m_rlc_lap.group(6) else "0.005"
            target = m_rlc_lap.group(7).strip()
            return f"set {target} to circuit_rlc_laplace_transient({topo}, {r_val}, {l_val}, {c_val}, v_step={vs}, duration={dur})"

        # minimize boolean function minterms <minterms> [dont cares <dc>] variables <n> into <target>
        m_qm = re.match(
            r"^minimize\s+boolean\s+function\s+minterms\s+(.+?)(?:\s+dont\s+cares\s+(.+?))?\s+variables\s+(\d+)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_qm:
            mterms, dcares, nvars, target = m_qm.group(1).strip(), m_qm.group(2), m_qm.group(3).strip(), m_qm.group(4).strip()
            dc_arg = f", dont_cares={dcares.strip()}" if dcares else ""
            return f"set {target} to circuit_quine_mccluskey_minimize({mterms}{dc_arg}, num_vars={nvars})"

        # calculate bjt q point vcc <vcc> rb <rb> rc <rc> [beta <beta>] [va <va>] into <target>
        m_bjt = re.match(
            r"^calculate\s+bjt\s+q\s+point\s+vcc\s+(.+?)\s+rb\s+(.+?)\s+rc\s+(.+?)(?:\s+beta\s+(.+?))?(?:\s+va\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bjt:
            vcc, rb, rc, beta, va, target = m_bjt.group(1).strip(), m_bjt.group(2).strip(), m_bjt.group(3).strip(), m_bjt.group(4), m_bjt.group(5), m_bjt.group(6).strip()
            b_arg = f", beta={beta.strip()}" if beta else ""
            va_arg = f", va={va.strip()}" if va else ""
            return f"set {target} to circuit_bjt_operating_point({vcc}, {rb}, {rc}{b_arg}{va_arg})"

        # solve circuit mna components <comps> [ground <gnd>] into <target>
        m_mna = re.match(
            r"^solve\s+circuit\s+mna\s+components\s+(.+?)(?:\s+ground\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mna:
            comps = m_mna.group(1).strip()
            gnd = m_mna.group(2).strip() if m_mna.group(2) else "0"
            target = m_mna.group(3).strip()
            return f"set {target} to circuit_mna_solve({comps}, ground_node={gnd})"

        # analyze digital static timing gates <gates> [clock period <clk>] into <target>
        m_sta = re.match(
            r"^analyze\s+digital\s+static\s+timing\s+gates\s+(.+?)(?:\s+clock\s+period\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sta:
            gates = m_sta.group(1).strip()
            clk = m_sta.group(2).strip() if m_sta.group(2) else "10.0"
            target = m_sta.group(3).strip()
            return f"set {target} to circuit_static_timing_analysis({gates}, clock_period_ns={clk})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Circuit domain does not define declarative blocks")
