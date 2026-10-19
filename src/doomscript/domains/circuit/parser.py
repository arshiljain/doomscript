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

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Circuit domain does not define declarative blocks")
