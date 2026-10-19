"""Electronics, Logic Gates & IoT Domain Runtime for DoomScript.

Pure Python standard library implementation of Ohm's Law, resistor color code decoding,
voltage dividers, 555 astable timer frequencies, RC time constants, logic truth table evaluation,
PWM duty cycle calculation, and GPIO pin state management.
"""

import math
import re
from typing import Any, Dict, List, Optional, Tuple, Set
from doomscript.domains.base import DomainRuntime, DomainIR


# Resistor color code values
RESISTOR_COLORS: Dict[str, int] = {
    "black": 0, "brown": 1, "red": 2, "orange": 3, "yellow": 4,
    "green": 5, "blue": 6, "violet": 7, "gray": 8, "white": 9
}

RESISTOR_TOLERANCES: Dict[str, float] = {
    "brown": 1.0, "red": 2.0, "green": 0.5, "blue": 0.25,
    "violet": 0.1, "gray": 0.05, "gold": 5.0, "silver": 10.0
}


class CircuitRuntime(DomainRuntime):
    """Runtime coordinator for electronics and circuit routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


def circuit_ohm_voltage(current: Any, resistance: Any) -> float:
    """Calculate voltage from Ohm's Law: V = I * R."""
    return round(float(current) * float(resistance), 4)


def circuit_ohm_current(voltage: Any, resistance: Any) -> float:
    """Calculate current from Ohm's Law: I = V / R."""
    r = max(1e-9, float(resistance))
    return round(float(voltage) / r, 4)


def circuit_ohm_resistance(voltage: Any, current: Any) -> float:
    """Calculate resistance from Ohm's Law: R = V / I."""
    i = max(1e-9, float(current))
    return round(float(voltage) / i, 4)


def circuit_power(voltage: Any, current: Any) -> float:
    """Calculate electrical power in Watts: P = V * I."""
    return round(float(voltage) * float(current), 4)


def circuit_decode_resistor_bands(colors: Any) -> Dict[str, Any]:
    """Decode 4-band or 5-band standard EIA resistor color codes."""
    cols = [str(c).lower().strip() for c in list(colors)]
    if len(cols) < 3:
        return {"resistance": 0.0, "tolerance_pct": 20.0}

    if len(cols) == 3 or len(cols) == 4:
        # 4-band: band1, band2, multiplier, [tolerance]
        d1 = RESISTOR_COLORS.get(cols[0], 0)
        d2 = RESISTOR_COLORS.get(cols[1], 0)
        mult_exp = RESISTOR_COLORS.get(cols[2], 0)
        tol = RESISTOR_TOLERANCES.get(cols[3] if len(cols) > 3 else "gold", 5.0)
        val = (d1 * 10 + d2) * (10 ** mult_exp)
    else:
        # 5-band: band1, band2, band3, multiplier, tolerance
        d1 = RESISTOR_COLORS.get(cols[0], 0)
        d2 = RESISTOR_COLORS.get(cols[1], 0)
        d3 = RESISTOR_COLORS.get(cols[2], 0)
        mult_exp = RESISTOR_COLORS.get(cols[3], 0)
        tol = RESISTOR_TOLERANCES.get(cols[4], 1.0)
        val = (d1 * 100 + d2 * 10 + d3) * (10 ** mult_exp)

    return {
        "resistance": float(val),
        "tolerance_pct": tol,
        "formatted": f"{val:g} Ω ±{tol}%",
    }


def circuit_voltage_divider(vin: Any, r1: Any, r2: Any) -> float:
    """Calculate unloaded voltage divider output: Vout = Vin * (R2 / (R1 + R2))."""
    v_in = float(vin)
    res1 = max(0.0, float(r1))
    res2 = max(0.0, float(r2))
    denom = max(1e-9, res1 + res2)
    return round(v_in * (res2 / denom), 4)


def circuit_555_timer_freq(r1: Any, r2: Any, c: Any) -> float:
    """Calculate astable 555 timer output frequency: f = 1.44 / ((R1 + 2*R2) * C)."""
    res1 = float(r1)
    res2 = float(r2)
    cap = float(c)
    denom = max(1e-12, (res1 + 2.0 * res2) * cap)
    return round(1.44 / denom, 2)


def circuit_rc_time_constant(r: Any, c: Any) -> float:
    """Calculate RC circuit time constant tau = R * C (in seconds)."""
    return round(float(r) * float(c), 6)


def circuit_evaluate_truth_table(expression: Any) -> List[Dict[str, Any]]:
    """Evaluate a boolean expression across all input variable permutations."""
    expr = str(expression)
    var_names = sorted(list(set(re.findall(r"\b[A-Za-z]\b", expr))))
    n = len(var_names)
    table: List[Dict[str, Any]] = []

    # Safe evaluation environment
    safe_env = {
        "and": lambda a, b: a and b,
        "or": lambda a, b: a or b,
        "not": lambda a: not a,
        "True": True,
        "False": False,
    }

    py_expr = expr
    py_expr = re.sub(r"\band\b", " and ", py_expr, flags=re.IGNORECASE)
    py_expr = re.sub(r"\bor\b", " or ", py_expr, flags=re.IGNORECASE)
    py_expr = re.sub(r"\bnot\b", " not ", py_expr, flags=re.IGNORECASE)

    for i in range(1 << n):
        row_inputs: Dict[str, Any] = {}
        eval_locals: Dict[str, Any] = {}
        for bit_idx, v in enumerate(var_names):
            val = bool((i >> (n - 1 - bit_idx)) & 1)
            row_inputs[v] = 1 if val else 0
            eval_locals[v] = val

        try:
            out_val = bool(eval(py_expr, {"__builtins__": None}, {**safe_env, **eval_locals}))
        except Exception:
            out_val = False

        row_entry = {**row_inputs, "output": 1 if out_val else 0}
        table.append(row_entry)

    return table


def circuit_pwm_duty_cycle(high_time: Any, period: Any) -> float:
    """Calculate PWM duty cycle percentage: (high_time / period) * 100%."""
    t_high = max(0.0, float(high_time))
    t_period = max(1e-9, float(period))
    return round(min(100.0, (t_high / t_period) * 100.0), 2)


class CircuitBoard:
    """Virtual GPIO pin state simulator."""

    def __init__(self):
        self.pins: Dict[int, int] = {}

    def set_pin(self, pin: int, val: int) -> None:
        self.pins[int(pin)] = 1 if str(val).lower() in ("1", "high", "true") else 0

    def read_pin(self, pin: int) -> int:
        return self.pins.get(int(pin), 0)


def circuit_gpio_set(board: Any, pin: Any, val: Any) -> Any:
    if isinstance(board, CircuitBoard):
        board.set_pin(int(pin), val)
    return board


def circuit_gpio_read(board: Any, pin: Any) -> int:
    if isinstance(board, CircuitBoard):
        return board.read_pin(int(pin))
    return 0


def circuit_create_gpio(pins: Any = None) -> CircuitBoard:
    board = CircuitBoard()
    if pins and isinstance(pins, (list, tuple)):
        for p in pins:
            board.set_pin(int(p), 0)
    return board


def circuit_pwm_analog_value(duty_cycle: Any, v_max: Any = 5.0) -> float:
    return round((float(duty_cycle) / 100.0) * float(v_max), 4)


def circuit_eval_logic(gate_type: str, inputs: Any) -> bool:
    g = str(gate_type).upper()
    inp = list(inputs) if isinstance(inputs, (list, tuple)) else [bool(inputs)]
    if g == "AND":
        return all(bool(x) for x in inp)
    elif g == "OR":
        return any(bool(x) for x in inp)
    elif g == "NOT":
        return not bool(inp[0]) if inp else True
    elif g == "XOR":
        return (bool(inp[0]) != bool(inp[1])) if len(inp) >= 2 else bool(inp[0])
    elif g == "NAND":
        return not all(bool(x) for x in inp)
    elif g == "NOR":
        return not any(bool(x) for x in inp)
    return False


def circuit_ohms_law(voltage: Any = None, current: Any = None, resistance: Any = None) -> Dict[str, float]:
    v = float(voltage) if voltage is not None else None
    i = float(current) if current is not None else None
    r = float(resistance) if resistance is not None else None

    if v is None and i is not None and r is not None:
        v = i * r
    elif i is None and v is not None and r is not None:
        i = v / max(1e-9, r)
    elif r is None and v is not None and i is not None:
        r = v / max(1e-9, i)

    v = v if v is not None else 0.0
    i = i if i is not None else 0.0
    r = r if r is not None else 0.0
    p = v * i
    return {"voltage": round(v, 4), "current": round(i, 4), "resistance": round(r, 4), "power": round(p, 4)}


def circuit_resistor_bands(*colors) -> Dict[str, Any]:
    if len(colors) == 1 and isinstance(colors[0], (list, tuple)):
        cols = list(colors[0])
    else:
        cols = list(colors)
    res = circuit_decode_resistor_bands(cols)
    res["tolerance"] = res.get("tolerance_pct", 5.0)
    return res


class CircuitDivResult(float):
    def __new__(cls, val):
        obj = super().__new__(cls, val)
        obj.v_out = val
        return obj

    def __getitem__(self, key):
        if key in ("v_out", "vout"):
            return self.v_out
        raise KeyError(key)

    def get(self, key, default=None):
        if key in ("v_out", "vout"):
            return self.v_out
        return default


_orig_voltage_divider = circuit_voltage_divider
def circuit_voltage_divider(vin: Any, r1: Any, r2: Any) -> Any:
    val = _orig_voltage_divider(vin, r1, r2)
    return CircuitDivResult(val)


def circuit_555_timer(r1: Any, r2: Any, c: Any) -> Dict[str, float]:
    freq = circuit_555_timer_freq(r1, r2, c)
    return {"frequency": freq}


class CircuitRCResult(float):
    def __new__(cls, val):
        obj = super().__new__(cls, val)
        obj.tau = val
        return obj

    def __getitem__(self, key):
        if key == "tau":
            return self.tau
        raise KeyError(key)

    def get(self, key, default=None):
        if key == "tau":
            return self.tau
        return default


_orig_rc_time_constant = circuit_rc_time_constant
def circuit_rc_time_constant(r: Any, c: Any) -> Any:
    val = _orig_rc_time_constant(r, c)
    return CircuitRCResult(val)


circuit_set_pin = circuit_gpio_set
circuit_read_pin = circuit_gpio_read


def execute_circuit_ir(spec_id: str) -> Any:
    """Executes a stored Circuit IR specification."""
    from doomscript.domains.registry import get_domain_registry
    reg = get_domain_registry()
    spec = reg.get_spec(spec_id)
    if spec is None:
        raise ValueError(f"Unknown circuit spec: {spec_id}")
    return CircuitRuntime().execute_ir(spec, {})
