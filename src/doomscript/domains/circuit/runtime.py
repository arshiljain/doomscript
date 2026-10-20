"""Electronics, Logic Gates & IoT Domain Runtime for DoomScript.

Pure Python standard library implementation of Ohm's Law, resistor color code decoding,
voltage dividers, 555 astable timer frequencies, RC time constants, logic truth table evaluation,
PWM duty cycle calculation, and GPIO pin state management.
"""

import math
import re
from typing import Any, Dict, List, Optional, Tuple, Set
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.runtime import Record


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


# ==============================================================================
# Advanced Circuit Deepening: MNA Matrix Solver, Bode Analyzer & Op-Amp Models
# ==============================================================================

class ModifiedNodalAnalysis:
    """Pure-Python Modified Nodal Analysis (MNA) linear circuit simulator."""

    def __init__(self):
        self.elements: List[Dict[str, Any]] = []

    def add_resistor(self, name: str, node1: Any, node2: Any, resistance: float) -> None:
        self.elements.append({
            "type": "R", "name": str(name), "n1": str(node1), "n2": str(node2), "value": float(resistance)
        })

    def add_voltage_source(self, name: str, node_pos: Any, node_neg: Any, voltage: float) -> None:
        self.elements.append({
            "type": "V", "name": str(name), "n1": str(node_pos), "n2": str(node_neg), "value": float(voltage)
        })

    def add_current_source(self, name: str, node_pos: Any, node_neg: Any, current: float) -> None:
        self.elements.append({
            "type": "I", "name": str(name), "n1": str(node_pos), "n2": str(node_neg), "value": float(current)
        })

    def add_capacitor(self, name: str, node1: Any, node2: Any, capacitance: float) -> None:
        self.elements.append({
            "type": "C", "name": str(name), "n1": str(node1), "n2": str(node2), "value": float(capacitance)
        })

    def add_inductor(self, name: str, node1: Any, node2: Any, inductance: float) -> None:
        self.elements.append({
            "type": "L", "name": str(name), "n1": str(node1), "n2": str(node2), "value": float(inductance)
        })

    @staticmethod
    def _solve_linear_system(matrix: List[List[float]], rhs: List[float]) -> List[float]:
        n = len(matrix)
        # Augment matrix
        aug = [list(matrix[i]) + [rhs[i]] for i in range(n)]

        for col in range(n):
            pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
            aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
            pivot = aug[col][col]
            if abs(pivot) < 1e-14:
                continue
            for c in range(col, n + 1):
                aug[col][c] /= pivot
            for r in range(n):
                if r != col:
                    factor = aug[r][col]
                    for c in range(col, n + 1):
                        aug[r][c] -= factor * aug[col][c]

        return [aug[i][n] for i in range(n)]

    def solve_dc(self) -> Dict[str, Any]:
        """Solves steady-state DC operating point using MNA matrix."""
        # Collect non-ground nodes (ground is '0')
        all_nodes = set()
        v_sources = []
        for el in self.elements:
            if el["type"] in ("R", "V", "I"):
                all_nodes.add(el["n1"])
                all_nodes.add(el["n2"])
                if el["type"] == "V":
                    v_sources.append(el)

        non_gnd_nodes = sorted([n for n in all_nodes if n not in ("0", 0)])
        node_map = {n: i for i, n in enumerate(non_gnd_nodes)}
        n_nodes = len(non_gnd_nodes)
        n_v = len(v_sources)
        dim = n_nodes + n_v

        A = [[0.0] * dim for _ in range(dim)]
        z = [0.0] * dim

        # Fill G matrix for Resistors
        for el in self.elements:
            if el["type"] == "R":
                r = max(1e-9, el["value"])
                g = 1.0 / r
                n1, n2 = el["n1"], el["n2"]
                if n1 in node_map:
                    i1 = node_map[n1]
                    A[i1][i1] += g
                if n2 in node_map:
                    i2 = node_map[n2]
                    A[i2][i2] += g
                if n1 in node_map and n2 in node_map:
                    i1, i2 = node_map[n1], node_map[n2]
                    A[i1][i2] -= g
                    A[i2][i1] -= g
            elif el["type"] == "I":
                # Current source pushes current from n1 to n2
                i_val = el["value"]
                n1, n2 = el["n1"], el["n2"]
                if n1 in node_map:
                    z[node_map[n1]] -= i_val
                if n2 in node_map:
                    z[node_map[n2]] += i_val

        # Fill B and C for Voltage sources
        for idx, vs in enumerate(v_sources):
            v_idx = n_nodes + idx
            n_pos, n_neg = vs["n1"], vs["n2"]
            if n_pos in node_map:
                A[node_map[n_pos]][v_idx] += 1.0
                A[v_idx][node_map[n_pos]] += 1.0
            if n_neg in node_map:
                A[node_map[n_neg]][v_idx] -= 1.0
                A[v_idx][node_map[n_neg]] -= 1.0
            z[v_idx] = vs["value"]

        sol = self._solve_linear_system(A, z)

        node_voltages = {"0": 0.0}
        for n, i in node_map.items():
            node_voltages[n] = round(sol[i], 6)

        source_currents = {}
        for idx, vs in enumerate(v_sources):
            source_currents[vs["name"]] = round(sol[n_nodes + idx], 6)

        return {
            "node_voltages": node_voltages,
            "source_currents": source_currents,
        }

    def simulate_transient(self, t_stop: float, dt: float = 0.001) -> Dict[str, Any]:
        """Performs transient companion model simulation for RLC circuits."""
        # Companion model:
        # C -> resistor Geq = C / dt in parallel with current source Ieq = Geq * Vprev
        # L -> resistor Geq = dt / L in parallel with current source Ieq = Iprev
        all_nodes = set()
        v_sources = []
        caps = []
        inds = []
        resistors = []

        for el in self.elements:
            all_nodes.add(el["n1"])
            all_nodes.add(el["n2"])
            if el["type"] == "V":
                v_sources.append(el)
            elif el["type"] == "C":
                caps.append(el)
            elif el["type"] == "L":
                inds.append(el)
            elif el["type"] == "R":
                resistors.append(el)

        non_gnd_nodes = sorted([n for n in all_nodes if n not in ("0", 0)])
        node_map = {n: i for i, n in enumerate(non_gnd_nodes)}
        n_nodes = len(non_gnd_nodes)
        n_v = len(v_sources)
        dim = n_nodes + n_v

        # Static conductance matrix
        A_static = [[0.0] * dim for _ in range(dim)]
        for r_el in resistors:
            g = 1.0 / max(1e-9, r_el["value"])
            n1, n2 = r_el["n1"], r_el["n2"]
            if n1 in node_map:
                A_static[node_map[n1]][node_map[n1]] += g
            if n2 in node_map:
                A_static[node_map[n2]][node_map[n2]] += g
            if n1 in node_map and n2 in node_map:
                A_static[node_map[n1]][node_map[n2]] -= g
                A_static[node_map[n2]][node_map[n1]] -= g

        # Add companion conductances for C and L
        for c_el in caps:
            geq = c_el["value"] / dt
            n1, n2 = c_el["n1"], c_el["n2"]
            if n1 in node_map:
                A_static[node_map[n1]][node_map[n1]] += geq
            if n2 in node_map:
                A_static[node_map[n2]][node_map[n2]] += geq
            if n1 in node_map and n2 in node_map:
                A_static[node_map[n1]][node_map[n2]] -= geq
                A_static[node_map[n2]][node_map[n1]] -= geq

        for l_el in inds:
            geq = dt / max(1e-9, l_el["value"])
            n1, n2 = l_el["n1"], l_el["n2"]
            if n1 in node_map:
                A_static[node_map[n1]][node_map[n1]] += geq
            if n2 in node_map:
                A_static[node_map[n2]][node_map[n2]] += geq
            if n1 in node_map and n2 in node_map:
                A_static[node_map[n1]][node_map[n2]] -= geq
                A_static[node_map[n2]][node_map[n1]] -= geq

        # Add voltage source connections
        for idx, vs in enumerate(v_sources):
            v_idx = n_nodes + idx
            n_pos, n_neg = vs["n1"], vs["n2"]
            if n_pos in node_map:
                A_static[node_map[n_pos]][v_idx] += 1.0
                A_static[v_idx][node_map[n_pos]] += 1.0
            if n_neg in node_map:
                A_static[node_map[n_neg]][v_idx] -= 1.0
                A_static[v_idx][node_map[n_neg]] -= 1.0

        # State memory
        v_prev = {n: 0.0 for n in all_nodes}
        i_l_prev = {l_el["name"]: 0.0 for l_el in inds}

        time_points = []
        node_trajectories = {n: [] for n in all_nodes}

        t = 0.0
        steps = int(math.ceil(t_stop / dt))
        for _ in range(steps):
            z = [0.0] * dim
            # Source values
            for idx, vs in enumerate(v_sources):
                z[n_nodes + idx] = vs["value"]

            # Companion currents for C: Ieq = (C/dt) * (v1_prev - v2_prev)
            for c_el in caps:
                geq = c_el["value"] / dt
                ieq = geq * (v_prev[c_el["n1"]] - v_prev[c_el["n2"]])
                n1, n2 = c_el["n1"], c_el["n2"]
                if n1 in node_map:
                    z[node_map[n1]] += ieq
                if n2 in node_map:
                    z[node_map[n2]] -= ieq

            # Companion currents for L: Ieq = I_prev
            for l_el in inds:
                ieq = i_l_prev[l_el["name"]]
                n1, n2 = l_el["n1"], l_el["n2"]
                if n1 in node_map:
                    z[node_map[n1]] -= ieq
                if n2 in node_map:
                    z[node_map[n2]] += ieq

            A_copy = [list(r) for r in A_static]
            sol = self._solve_linear_system(A_copy, z)

            for n, i in node_map.items():
                v_prev[n] = sol[i]
            v_prev["0"] = 0.0

            # Update inductor currents
            for l_el in inds:
                v_diff = v_prev[l_el["n1"]] - v_prev[l_el["n2"]]
                i_l_prev[l_el["name"]] += (dt / l_el["value"]) * v_diff

            t += dt
            time_points.append(round(t, 6))
            for n in all_nodes:
                node_trajectories[n].append(round(v_prev[n], 6))

        return {
            "time": time_points,
            "nodes": node_trajectories,
        }


class BodePlotAnalyzer:
    """Frequency response & Bode plot analyzer for linear transfer functions H(s)."""

    @staticmethod
    def _eval_poly(coeffs: List[float], s: complex) -> complex:
        val = 0.0 + 0.0j
        for p, c in enumerate(coeffs):
            val += c * (s ** p)
        return val

    @classmethod
    def analyze(
        cls,
        numerator: List[float],
        denominator: List[float],
        f_min: float = 1.0,
        f_max: float = 100000.0,
        num_points: int = 50,
    ) -> Dict[str, Any]:
        """
        Evaluates H(s) = P(s)/Q(s) over a logarithmic frequency sweep.
        `numerator` and `denominator` are listed in ascending power: [a0, a1, a2, ...]
        """
        log_min = math.log10(max(1e-3, f_min))
        log_max = math.log10(max(1e-2, f_max))
        freqs = [10.0 ** (log_min + (log_max - log_min) * i / max(1, num_points - 1)) for i in range(num_points)]

        magnitudes_db: List[float] = []
        phases_deg: List[float] = []

        for f in freqs:
            w = 2.0 * math.pi * f
            s = complex(0.0, w)
            num_val = cls._eval_poly(numerator, s)
            den_val = cls._eval_poly(denominator, s)

            if abs(den_val) < 1e-15:
                h = 1e6
            else:
                h = num_val / den_val

            mag = abs(h)
            mag_db = 20.0 * math.log10(max(1e-9, mag))
            phase = math.degrees(math.atan2(h.imag, h.real))

            magnitudes_db.append(round(mag_db, 3))
            phases_deg.append(round(phase, 2))

        # Find 3dB cutoff frequency (relative to DC or peak)
        ref_mag = magnitudes_db[0]
        cutoff_hz = None
        for i, m in enumerate(magnitudes_db):
            if m <= ref_mag - 3.0:
                cutoff_hz = round(freqs[i], 2)
                break

        return {
            "frequencies_hz": [round(f, 2) for f in freqs],
            "magnitude_db": magnitudes_db,
            "phase_deg": phases_deg,
            "cutoff_3db_hz": cutoff_hz,
            "dc_gain_db": round(magnitudes_db[0], 2),
        }


class OpAmpModel:
    """Operational amplifier model with finite gain, input/output impedance and saturation."""

    def __init__(
        self,
        gain_ol: float = 100000.0,
        v_sat_pos: float = 15.0,
        v_sat_neg: float = -15.0,
        slew_rate_v_us: float = 1.0,
        r_in: float = 1e6,
        r_out: float = 75.0,
    ):
        self.gain_ol = float(gain_ol)
        self.v_sat_pos = float(v_sat_pos)
        self.v_sat_neg = float(v_sat_neg)
        self.slew_rate_v_s = float(slew_rate_v_us) * 1e6
        self.r_in = float(r_in)
        self.r_out = float(r_out)

    def amplify(self, v_plus: float, v_minus: float) -> float:
        """Computes instantaneous amplified output with rail clipping."""
        diff = float(v_plus) - float(v_minus)
        v_out_ideal = self.gain_ol * diff
        return max(self.v_sat_neg, min(self.v_sat_pos, v_out_ideal))

    def step_transient(self, v_plus: float, v_minus: float, current_v_out: float, dt: float) -> float:
        """Updates output considering slew-rate limiting."""
        target_v = self.amplify(v_plus, v_minus)
        max_delta = self.slew_rate_v_s * dt
        diff = target_v - current_v_out
        if abs(diff) <= max_delta:
            new_v = target_v
        else:
            new_v = current_v_out + math.copysign(max_delta, diff)
        return max(self.v_sat_neg, min(self.v_sat_pos, new_v))


def circuit_mna_dc_solve(elements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Solves DC circuit node voltages and source currents via MNA."""
    sim = ModifiedNodalAnalysis()
    for el in elements:
        t = el.get("type", "R").upper()
        if t == "R":
            sim.add_resistor(el["name"], el["n1"], el["n2"], el["value"])
        elif t == "V":
            sim.add_voltage_source(el["name"], el["n1"], el["n2"], el["value"])
        elif t == "I":
            sim.add_current_source(el["name"], el["n1"], el["n2"], el["value"])
    return sim.solve_dc()


def circuit_bode_plot(num: List[float], den: List[float], f_min: float = 1.0, f_max: float = 100000.0) -> Dict[str, Any]:
    """Calculates frequency response Bode plot."""
    return BodePlotAnalyzer.analyze(num, den, f_min, f_max)


def circuit_opamp_amplify(v_plus: float, v_minus: float, gain: float = 100000.0, v_sat: float = 15.0) -> float:
    """Simulates operational amplifier differential gain with rails."""
    op = OpAmpModel(gain_ol=gain, v_sat_pos=v_sat, v_sat_neg=-v_sat)
    return op.amplify(v_plus, v_minus)


# ==============================================================================
# NONLINEAR SHOCKLEY DIODE OPERATING POINT SOLVER (NEWTON-RAPHSON)
# ==============================================================================

class NonlinearDiodeSolver:
    """Solves non-linear DC operating point for a Shockley diode in series with a resistor.

    I_D = I_s * (exp(V_D / (n * V_T)) - 1)
    """

    @classmethod
    def solve(
        cls,
        v_source: float,
        resistance: float,
        i_sat: float = 1e-14,
        ideality: float = 1.0,
        temp_k: float = 300.0,
        max_iters: int = 50,
        tol: float = 1e-9,
    ) -> Dict[str, Any]:
        vs = float(v_source)
        r = float(resistance)
        isat = float(i_sat)
        n = float(ideality)
        k_b = 1.380649e-23
        q = 1.60217663e-19
        vt = (k_b * temp_k) / q  # ~0.02585 V at 300K

        if r <= 0:
            raise ValueError("Resistance must be positive")

        # Initial guess: 0.65V for forward bias, vs for reverse bias
        vd = 0.65 if vs > 0 else vs
        converged = False
        iters_taken = 0

        for it in range(max_iters):
            iters_taken = it + 1
            # Bound exponent to avoid math.exp overflow
            exponent = max(-50.0, min(40.0, vd / (n * vt)))
            exp_val = math.exp(exponent)

            # Diode current
            id_val = isat * (exp_val - 1.0)
            # Dynamic conductance gd = dId / dVd
            gd = (isat / (n * vt)) * exp_val

            # KCL error at diode anode: f(vd) = (vs - vd)/r - id = 0
            f_val = (vs - vd) / r - id_val
            f_prime = -1.0 / r - gd

            delta_vd = -f_val / f_prime

            # Voltage damping limit to prevent oscillation
            max_step = 2.0 * vt
            if abs(delta_vd) > max_step:
                delta_vd = math.copysign(max_step, delta_vd)

            vd += delta_vd

            if abs(f_val) < tol or abs(delta_vd) < 1e-7:
                converged = True
                break

        final_exp = max(-50.0, min(40.0, vd / (n * vt)))
        id_final = isat * (math.exp(final_exp) - 1.0)
        vr_final = vs - vd
        power_diode = vd * id_final
        rd_small_signal = (n * vt) / max(1e-12, id_final + isat)

        return {
            "v_source": vs,
            "resistance": r,
            "v_diode": round(vd, 4),
            "i_diode_mA": round(id_final * 1000.0, 4),
            "v_resistor": round(vr_final, 4),
            "power_diode_mW": round(power_diode * 1000.0, 4),
            "dynamic_resistance_ohms": round(rd_small_signal, 2),
            "converged": converged,
            "iterations": iters_taken,
        }


# ==============================================================================
# TRANSMISSION LINE DISTRIBUTED RLGC PARAMETER SOLVER
# ==============================================================================

class TransmissionLineRLGC:
    """Distributed Telegrapher's transmission line characteristics and reflections."""

    @classmethod
    def analyze(
        cls,
        r_per_m: float,
        l_per_m: float,
        g_per_m: float,
        c_per_m: float,
        freq_hz: float,
        length_m: float = 1.0,
        z_load: complex = 50.0 + 0.0j,
    ) -> Dict[str, Any]:
        r, l, g, c = float(r_per_m), float(l_per_m), float(g_per_m), float(c_per_m)
        f = max(1.0, float(freq_hz))
        omega = 2.0 * math.pi * f

        # Complex series impedance Z = R + j*omega*L
        z_ser = complex(r, omega * l)
        # Complex shunt admittance Y = G + j*omega*C
        y_sh = complex(g, omega * c)

        # Characteristic impedance Z0 = sqrt(Z / Y)
        z0 = (z_ser / y_sh) ** 0.5

        # Propagation constant gamma = alpha + j*beta = sqrt(Z * Y)
        gamma = (z_ser * y_sh) ** 0.5
        alpha = gamma.real  # attenuation (Np/m)
        beta = gamma.imag   # phase constant (rad/m)

        alpha_db_per_m = alpha * 8.68589  # 1 Np = 8.68589 dB
        wavelength_m = (2.0 * math.pi / beta) if beta > 1e-12 else float("inf")
        v_phase_mps = (omega / beta) if beta > 1e-12 else float("inf")

        # Voltage reflection coefficient Gamma = (ZL - Z0) / (ZL + Z0)
        refl_coeff = (z_load - z0) / (z_load + z0)
        gamma_mag = abs(refl_coeff)

        # VSWR = (1 + |Gamma|) / (1 - |Gamma|)
        vswr = (1.0 + gamma_mag) / max(1e-6, (1.0 - gamma_mag)) if gamma_mag < 0.999999 else 999.0
        return_loss_db = -20.0 * math.log10(max(1e-6, gamma_mag)) if gamma_mag > 0 else 999.0

        return {
            "frequency_hz": f,
            "z0_ohms_real": round(z0.real, 2),
            "z0_ohms_imag": round(z0.imag, 2),
            "attenuation_db_per_m": round(alpha_db_per_m, 6),
            "phase_constant_rad_per_m": round(beta, 4),
            "wavelength_m": round(wavelength_m, 4),
            "phase_velocity_mps": round(v_phase_mps, 1),
            "reflection_coefficient_mag": round(gamma_mag, 4),
            "vswr": round(vswr, 3),
            "return_loss_db": round(return_loss_db, 2),
        }


# ==============================================================================
# STATE-SPACE RLC RESONANT NETWORK SIMULATOR
# ==============================================================================

class StateSpaceRLCSimulator:
    """Transient state-space step response and resonant tuning of RLC circuits."""

    @classmethod
    def simulate_series_step(
        cls,
        r: float,
        l: float,
        c: float,
        v_step: float = 5.0,
        duration: float = 0.001,
        steps: int = 50,
    ) -> Dict[str, Any]:
        r, l, c, v_in = float(r), float(l), float(c), float(v_step)
        if l <= 0 or c <= 0:
            raise ValueError("L and C must be positive")

        w0 = 1.0 / math.sqrt(l * c)
        alpha = r / (2.0 * l)
        zeta = alpha / w0
        q_factor = w0 * l / r if r > 0 else float("inf")

        if zeta < 0.999:
            regime = "underdamped"
        elif zeta > 1.001:
            regime = "overdamped"
        else:
            regime = "critically_damped"

        dt = duration / steps
        vc = 0.0
        il = 0.0
        voltages = []

        for _ in range(steps):
            voltages.append(round(vc, 3))
            # dvc/dt = il / C
            dvc = il / c
            # dil/dt = (Vin - vc - R*il) / L
            dil = (v_in - vc - r * il) / l

            vc += dt * dvc
            il += dt * dil

        max_vc = max(voltages)
        overshoot_pct = max(0.0, ((max_vc - v_in) / v_in) * 100.0) if v_in > 0 else 0.0

        return {
            "resonant_freq_hz": round(w0 / (2.0 * math.pi), 2),
            "damping_ratio": round(zeta, 4),
            "quality_factor": round(q_factor, 2),
            "regime": regime,
            "v_step": v_in,
            "max_capacitor_voltage": round(max_vc, 3),
            "overshoot_percent": round(overshoot_pct, 2),
            "final_capacitor_voltage": round(vc, 3),
        }


def circuit_solve_diode(
    v_source: float,
    resistance: float,
    i_sat: float = 1e-14,
    ideality: float = 1.0,
) -> Any:
    """Solves non-linear Shockley diode DC operating point."""
    return Record(NonlinearDiodeSolver.solve(v_source, resistance, i_sat=i_sat, ideality=ideality))


def circuit_transmission_line(
    r_per_m: float,
    l_per_m: float,
    g_per_m: float,
    c_per_m: float,
    freq_hz: float,
    z_load_ohms: float = 50.0,
) -> Any:
    """Analyzes distributed RLGC transmission line parameters and VSWR."""
    return Record(TransmissionLineRLGC.analyze(r_per_m, l_per_m, g_per_m, c_per_m, freq_hz, z_load=complex(z_load_ohms, 0.0)))


def circuit_simulate_rlc_step(
    r: float,
    l: float,
    c: float,
    v_step: float = 5.0,
    duration: float = 0.001,
) -> Any:
    """Simulates transient state-space step response of series RLC network."""
    return Record(StateSpaceRLCSimulator.simulate_series_step(r, l, c, v_step=v_step, duration=duration))


class ActiveSallenKeyFilterDesigner:
    """Designs active 2nd-order Sallen-Key filters and calculates frequency response."""

    E24_SERIES = [
        1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
        3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1,
    ]

    @classmethod
    def find_nearest_e24(cls, val: float) -> float:
        if val <= 0:
            return val
        dec = math.floor(math.log10(val))
        mant = val / (10 ** dec)
        best = min(cls.E24_SERIES, key=lambda x: abs(x - mant))
        return round(best * (10 ** dec), 2)

    @classmethod
    def design(
        cls,
        filter_type: str,
        cutoff_hz: float,
        q_factor: float = 0.7071,
        gain: float = 1.0,
    ) -> Dict[str, Any]:
        w0 = 2.0 * math.pi * cutoff_hz
        ft = filter_type.lower().strip()
        c1 = 1e-8  # 10 nF standard base capacitor

        if ft in ("lowpass", "low_pass", "lp"):
            # Low-pass Sallen-Key
            c2 = c1 / (4.0 * (q_factor ** 2))
            r1 = 1.0 / (w0 * math.sqrt(c1 * c2))
            r2 = r1
        elif ft in ("highpass", "high_pass", "hp"):
            # High-pass Sallen-Key
            c2 = c1
            r2 = 1.0 / (2.0 * q_factor * w0 * c1)
            r1 = 4.0 * (q_factor ** 2) * r2
        else:
            # Band-pass Sallen-Key
            c2 = c1
            r1 = 1.0 / (w0 * c1 * (2.0 * q_factor))
            r2 = (2.0 * q_factor) / (w0 * c1)

        r1_std = cls.find_nearest_e24(r1)
        r2_std = cls.find_nearest_e24(r2)

        if ft in ("lowpass", "low_pass", "lp"):
            actual_w0 = 1.0 / math.sqrt(r1_std * r2_std * c1 * c2)
            actual_q = math.sqrt(r1_std * r2_std * c1 * c2) / (c2 * (r1_std + r2_std))
        elif ft in ("highpass", "high_pass", "hp"):
            actual_w0 = 1.0 / math.sqrt(r1_std * r2_std * c1 * c2)
            actual_q = math.sqrt(r1_std * r2_std * c1 * c2) / (r1_std * (c1 + c2))
        else:
            actual_w0 = 1.0 / math.sqrt(r1_std * r2_std * c1 * c2)
            actual_q = 0.5 * math.sqrt(r2_std / r1_std)

        actual_fc = actual_w0 / (2.0 * math.pi)

        freq_points = [0.1 * cutoff_hz, 0.5 * cutoff_hz, cutoff_hz, 2.0 * cutoff_hz, 10.0 * cutoff_hz]
        response = []
        for f in freq_points:
            w = 2.0 * math.pi * f
            s = complex(0.0, w)
            if ft in ("lowpass", "low_pass", "lp"):
                num = gain * (actual_w0 ** 2)
                den = (s ** 2) + (actual_w0 / actual_q) * s + (actual_w0 ** 2)
            elif ft in ("highpass", "high_pass", "hp"):
                num = gain * (s ** 2)
                den = (s ** 2) + (actual_w0 / actual_q) * s + (actual_w0 ** 2)
            else:
                num = gain * (actual_w0 / actual_q) * s
                den = (s ** 2) + (actual_w0 / actual_q) * s + (actual_w0 ** 2)
            h = num / den
            mag_db = 20.0 * math.log10(max(abs(h), 1e-12))
            phase_deg = math.degrees(math.atan2(h.imag, h.real))
            response.append({
                "freq_hz": round(f, 2),
                "gain_db": round(mag_db, 2),
                "phase_deg": round(phase_deg, 2),
            })

        return {
            "filter_type": ft,
            "target_cutoff_hz": cutoff_hz,
            "actual_cutoff_hz": round(actual_fc, 2),
            "target_q": q_factor,
            "actual_q": round(actual_q, 4),
            "r1_ohms": round(r1, 2),
            "r2_ohms": round(r2, 2),
            "r1_e24_ohms": r1_std,
            "r2_e24_ohms": r2_std,
            "c1_farads": c1,
            "c2_farads": c2,
            "response_points": [Record(pt) for pt in response],
        }


class RLCTransientLaplaceSolver:
    """Solves exact analytical transient step response of series or parallel RLC network."""

    @classmethod
    def solve(
        cls,
        topology: str,
        r: float,
        l: float,
        c: float,
        v_step: float = 1.0,
        duration: float = 0.005,
        points: int = 50,
    ) -> Dict[str, Any]:
        top = topology.lower().strip()
        if top not in ("series", "parallel"):
            top = "series"

        if top == "series":
            alpha = r / (2.0 * l)
        else:
            alpha = 1.0 / (2.0 * r * c)

        w0 = 1.0 / math.sqrt(l * c)
        zeta = alpha / w0

        dt = duration / max(points - 1, 1)
        time_points = [i * dt for i in range(points)]
        v_t = []

        if abs(zeta - 1.0) < 1e-5:
            regime = "critically_damped"
            for t in time_points:
                val = v_step * (1.0 - (1.0 + alpha * t) * math.exp(-alpha * t))
                v_t.append(round(val, 5))
            overshoot = 0.0
            peak_time = 0.0
        elif zeta > 1.0:
            regime = "overdamped"
            s1 = -alpha + math.sqrt(alpha ** 2 - w0 ** 2)
            s2 = -alpha - math.sqrt(alpha ** 2 - w0 ** 2)
            for t in time_points:
                val = v_step * (1.0 - (s2 * math.exp(s1 * t) - s1 * math.exp(s2 * t)) / (s2 - s1))
                v_t.append(round(val, 5))
            overshoot = 0.0
            peak_time = 0.0
        else:
            regime = "underdamped"
            wd = math.sqrt(w0 ** 2 - alpha ** 2)
            phi = math.atan2(wd, alpha)
            max_v = 0.0
            peak_t_val = 0.0
            for t in time_points:
                val = v_step * (1.0 - (w0 / wd) * math.exp(-alpha * t) * math.sin(wd * t + phi))
                if val > max_v:
                    max_v = val
                    peak_t_val = t
                v_t.append(round(val, 5))
            overshoot = max(0.0, (max_v - v_step) / v_step * 100.0)
            peak_time = round(math.pi / wd, 6)

        settling_time = round(4.0 / alpha, 6) if alpha > 0 else duration

        return {
            "topology": top,
            "damping_factor_alpha": round(alpha, 3),
            "resonant_freq_w0": round(w0, 3),
            "damping_ratio_zeta": round(zeta, 4),
            "regime": regime,
            "v_step": v_step,
            "overshoot_percent": round(overshoot, 2),
            "peak_time": peak_time,
            "settling_time": settling_time,
            "samples_count": len(v_t),
            "final_voltage": v_t[-1] if v_t else 0.0,
        }


def circuit_design_sallen_key(
    filter_type: str,
    cutoff_hz: float,
    q_factor: float = 0.7071,
    gain: float = 1.0,
) -> Any:
    """Designs active 2nd-order Sallen-Key filter with standard E24 components."""
    return Record(ActiveSallenKeyFilterDesigner.design(filter_type, cutoff_hz, q_factor=q_factor, gain=gain))


def circuit_rlc_laplace_transient(
    topology: str,
    r: float,
    l: float,
    c: float,
    v_step: float = 1.0,
    duration: float = 0.005,
    points: int = 50,
) -> Any:
    """Solves analytical transient Laplace step response for series or parallel RLC circuit."""
    return Record(RLCTransientLaplaceSolver.solve(topology, r, l, c, v_step=v_step, duration=duration, points=points))

