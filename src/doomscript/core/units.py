"""
DoomScript Physical, Temporal, Computational, and Financial Units System.
Provides first-class Quantity objects with automatic dimensional analysis,
unit conversions, and natural English expression support.
"""

import math
from typing import Any, Union, Dict, Tuple, Optional
from doomscript.exceptions import DoomTypeError, DoomValueError, DoomZeroDivisionError

# Base reference units per dimension:
# - length: meters (m)
# - time: seconds (s)
# - mass: kilograms (kg)
# - speed: meters per second (m/s)
# - data: bytes (B)
# - temperature: Kelvin (K)
# - volume: liters (L)
# - currency: USD ($)
# - energy: joules (J)
# - power: watts (W)

UNIT_DEFINITIONS: Dict[str, Tuple[str, Union[float, str]]] = {
    # Length (base: meter)
    "nanometer": ("length", 1e-9),
    "nanometers": ("length", 1e-9),
    "nm": ("length", 1e-9),
    "micrometer": ("length", 1e-6),
    "micrometers": ("length", 1e-6),
    "micron": ("length", 1e-6),
    "microns": ("length", 1e-6),
    "um": ("length", 1e-6),
    "millimeter": ("length", 1e-3),
    "millimeters": ("length", 1e-3),
    "mm": ("length", 1e-3),
    "centimeter": ("length", 0.01),
    "centimeters": ("length", 0.01),
    "cm": ("length", 0.01),
    "meter": ("length", 1.0),
    "meters": ("length", 1.0),
    "m": ("length", 1.0),
    "kilometer": ("length", 1000.0),
    "kilometers": ("length", 1000.0),
    "km": ("length", 1000.0),
    "inch": ("length", 0.0254),
    "inches": ("length", 0.0254),
    "foot": ("length", 0.3048),
    "feet": ("length", 0.3048),
    "ft": ("length", 0.3048),
    "yard": ("length", 0.9144),
    "yards": ("length", 0.9144),
    "yd": ("length", 0.9144),
    "mile": ("length", 1609.344),
    "miles": ("length", 1609.344),
    "mi": ("length", 1609.344),
    "nautical mile": ("length", 1852.0),
    "nautical miles": ("length", 1852.0),

    # Time (base: second)
    "nanosecond": ("time", 1e-9),
    "nanoseconds": ("time", 1e-9),
    "ns": ("time", 1e-9),
    "microsecond": ("time", 1e-6),
    "microseconds": ("time", 1e-6),
    "us": ("time", 1e-6),
    "millisecond": ("time", 0.001),
    "milliseconds": ("time", 0.001),
    "ms": ("time", 0.001),
    "second": ("time", 1.0),
    "seconds": ("time", 1.0),
    "s": ("time", 1.0),
    "minute": ("time", 60.0),
    "minutes": ("time", 60.0),
    "min": ("time", 60.0),
    "hour": ("time", 3600.0),
    "hours": ("time", 3600.0),
    "hr": ("time", 3600.0),
    "day": ("time", 86400.0),
    "days": ("time", 86400.0),
    "d": ("time", 86400.0),
    "week": ("time", 604800.0),
    "weeks": ("time", 604800.0),

    # Mass (base: kilogram)
    "microgram": ("mass", 1e-9),
    "micrograms": ("mass", 1e-9),
    "ug": ("mass", 1e-9),
    "milligram": ("mass", 1e-6),
    "milligrams": ("mass", 1e-6),
    "mg": ("mass", 1e-6),
    "gram": ("mass", 1e-3),
    "grams": ("mass", 1e-3),
    "g": ("mass", 1e-3),
    "kilogram": ("mass", 1.0),
    "kilograms": ("mass", 1.0),
    "kg": ("mass", 1.0),
    "ounce": ("mass", 0.028349523125),
    "ounces": ("mass", 0.028349523125),
    "oz": ("mass", 0.028349523125),
    "pound": ("mass", 0.45359237),
    "pounds": ("mass", 0.45359237),
    "lb": ("mass", 0.45359237),
    "lbs": ("mass", 0.45359237),
    "ton": ("mass", 907.18474),
    "tons": ("mass", 907.18474),
    "tonne": ("mass", 1000.0),
    "tonnes": ("mass", 1000.0),

    # Speed (base: m/s)
    "meter per second": ("speed", 1.0),
    "meters per second": ("speed", 1.0),
    "m/s": ("speed", 1.0),
    "mps": ("speed", 1.0),
    "kilometer per hour": ("speed", 1.0 / 3.6),
    "kilometers per hour": ("speed", 1.0 / 3.6),
    "km/h": ("speed", 1.0 / 3.6),
    "kph": ("speed", 1.0 / 3.6),
    "mile per hour": ("speed", 0.44704),
    "miles per hour": ("speed", 0.44704),
    "mph": ("speed", 0.44704),
    "foot per second": ("speed", 0.3048),
    "feet per second": ("speed", 0.3048),
    "fps": ("speed", 0.3048),
    "knot": ("speed", 0.514444444444),
    "knots": ("speed", 0.514444444444),

    # Digital Storage (base: byte)
    "bit": ("data", 0.125),
    "bits": ("data", 0.125),
    "byte": ("data", 1.0),
    "bytes": ("data", 1.0),
    "b": ("data", 1.0),
    "kilobyte": ("data", 1024.0),
    "kilobytes": ("data", 1024.0),
    "kb": ("data", 1024.0),
    "megabyte": ("data", 1024.0**2),
    "megabytes": ("data", 1024.0**2),
    "mb": ("data", 1024.0**2),
    "gigabyte": ("data", 1024.0**3),
    "gigabytes": ("data", 1024.0**3),
    "gb": ("data", 1024.0**3),
    "terabyte": ("data", 1024.0**4),
    "terabytes": ("data", 1024.0**4),
    "tb": ("data", 1024.0**4),
    "petabyte": ("data", 1024.0**5),
    "petabytes": ("data", 1024.0**5),
    "pb": ("data", 1024.0**5),

    # Temperature (affine conversion)
    "celsius": ("temperature", "C"),
    "degree celsius": ("temperature", "C"),
    "degrees celsius": ("temperature", "C"),
    "fahrenheit": ("temperature", "F"),
    "degree fahrenheit": ("temperature", "F"),
    "degrees fahrenheit": ("temperature", "F"),
    "kelvin": ("temperature", "K"),

    # Volume (base: liter)
    "milliliter": ("volume", 1e-3),
    "milliliters": ("volume", 1e-3),
    "ml": ("volume", 1e-3),
    "liter": ("volume", 1.0),
    "liters": ("volume", 1.0),
    "l": ("volume", 1.0),
    "gallon": ("volume", 3.785411784),
    "gallons": ("volume", 3.785411784),
    "quart": ("volume", 0.946352946),
    "quarts": ("volume", 0.946352946),
    "pint": ("volume", 0.473176473),
    "pints": ("volume", 0.473176473),
    "cup": ("volume", 0.2365882365),
    "cups": ("volume", 0.2365882365),
    "fluid ounce": ("volume", 0.0295735295625),
    "fluid ounces": ("volume", 0.0295735295625),
    "fl oz": ("volume", 0.0295735295625),

    # Currency (base: USD)
    "dollar": ("currency", 1.0),
    "dollars": ("currency", 1.0),
    "usd": ("currency", 1.0),
    "cent": ("currency", 0.01),
    "cents": ("currency", 0.01),
    "euro": ("currency", 1.08),
    "euros": ("currency", 1.08),
    "eur": ("currency", 1.08),
    "pound sterling": ("currency", 1.27),
    "pounds sterling": ("currency", 1.27),
    "gbp": ("currency", 1.27),
    "yen": ("currency", 0.0067),
    "jpy": ("currency", 0.0067),

    # Energy & Power (base: Joule / Watt)
    "joule": ("energy", 1.0),
    "joules": ("energy", 1.0),
    "kilojoule": ("energy", 1000.0),
    "kilojoules": ("energy", 1000.0),
    "calorie": ("energy", 4.184),
    "calories": ("energy", 4.184),
    "kilocalorie": ("energy", 4184.0),
    "kilocalories": ("energy", 4184.0),
    "watt": ("power", 1.0),
    "watts": ("power", 1.0),
    "kilowatt": ("power", 1000.0),
    "kilowatts": ("power", 1000.0),
    "horsepower": ("power", 745.699872),
    "hp": ("power", 745.699872),
    "kilowatt hour": ("energy", 3.6e6),
    "kilowatt hours": ("energy", 3.6e6),
    "kwh": ("energy", 3.6e6),
}


class Quantity:
    """Represents a numeric value with physical, temporal, computational, or financial units."""

    __slots__ = ("value", "unit", "dimension")

    def __init__(self, value: Union[int, float], unit: str, dimension: Optional[str] = None):
        unit_lower = unit.strip().lower()
        if unit_lower not in UNIT_DEFINITIONS:
            raise DoomValueError(f"Unknown unit of measurement '{unit}'.")
        dim, _ = UNIT_DEFINITIONS[unit_lower]
        self.value = float(value)
        self.unit = unit_lower
        self.dimension = dimension or dim

    def to(self, target_unit: str) -> "Quantity":
        """Converts quantity to target unit within the same physical dimension."""
        t_lower = target_unit.strip().lower()
        if t_lower not in UNIT_DEFINITIONS:
            raise DoomValueError(f"Unknown target unit of measurement '{target_unit}'.")
        target_dim, target_factor = UNIT_DEFINITIONS[t_lower]
        if target_dim != self.dimension:
            raise DoomTypeError(
                f"Cannot convert '{self.unit}' ({self.dimension}) to '{target_unit}' ({target_dim}). Dimensions must match."
            )

        if self.dimension == "temperature":
            # Convert source temperature to Kelvin
            _, s_code = UNIT_DEFINITIONS[self.unit]
            if s_code == "K":
                k = self.value
            elif s_code == "C":
                k = self.value + 273.15
            elif s_code == "F":
                k = (self.value - 32.0) * (5.0 / 9.0) + 273.15
            else:
                k = self.value

            # Convert Kelvin to target
            if target_factor == "K":
                res = k
            elif target_factor == "C":
                res = k - 273.15
            elif target_factor == "F":
                res = (k - 273.15) * (9.0 / 5.0) + 32.0
            else:
                res = k
            return Quantity(res, t_lower, self.dimension)

        # Standard linear dimension conversion
        _, source_factor = UNIT_DEFINITIONS[self.unit]
        base_value = self.value * float(source_factor)
        new_value = base_value / float(target_factor)
        return Quantity(new_value, t_lower, self.dimension)

    def __repr__(self) -> str:
        rounded = round(self.value, 6)
        if rounded.is_integer():
            v_str = str(int(rounded))
        else:
            v_str = f"{rounded:g}"
        return f"{v_str} {self.unit}"

    def __str__(self) -> str:
        return self.__repr__()

    def __float__(self) -> float:
        return float(self.value)

    def __int__(self) -> int:
        return int(self.value)

    def __round__(self, ndigits: int = 0) -> "Quantity":
        return Quantity(round(self.value, ndigits), self.unit, self.dimension)

    def __getattr__(self, name: str) -> Any:
        if name in ("value", "magnitude", "amount"):
            return self.value
        if name in ("unit", "units"):
            return self.unit
        if name in ("dimension", "dim", "type"):
            return self.dimension
        raise AttributeError(f"'Quantity' object has no property '{name}'")

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __add__(self, other: Any) -> "Quantity":
        if isinstance(other, Quantity):
            if other.dimension != self.dimension:
                raise DoomTypeError(
                    f"Cannot add {self} and {other}. Dimensions '{self.dimension}' and '{other.dimension}' are incompatible."
                )
            converted = other.to(self.unit)
            return Quantity(self.value + converted.value, self.unit, self.dimension)
        if other == 0:
            return self
        raise DoomTypeError(f"Cannot add scalar {other} to Quantity {self}. Both operands must have compatible units.")

    def __radd__(self, other: Any) -> "Quantity":
        return self.__add__(other)

    def __sub__(self, other: Any) -> "Quantity":
        if isinstance(other, Quantity):
            if other.dimension != self.dimension:
                raise DoomTypeError(
                    f"Cannot subtract {other} from {self}. Dimensions '{self.dimension}' and '{other.dimension}' are incompatible."
                )
            converted = other.to(self.unit)
            return Quantity(self.value - converted.value, self.unit, self.dimension)
        raise DoomTypeError(f"Cannot subtract {other} from Quantity {self}. Both operands must have compatible units.")

    def __mul__(self, other: Any) -> Union["Quantity", float]:
        if isinstance(other, (int, float)):
            return Quantity(self.value * float(other), self.unit, self.dimension)
        if isinstance(other, Quantity):
            # Speed * Time -> Length
            if (self.dimension == "speed" and other.dimension == "time") or (
                self.dimension == "time" and other.dimension == "speed"
            ):
                sp = self if self.dimension == "speed" else other
                tm = other if self.dimension == "speed" else self
                sp_mps = sp.to("meters per second").value
                tm_s = tm.to("seconds").value
                dist_m = sp_mps * tm_s
                target_len = (
                    "miles"
                    if "mile" in sp.unit
                    else ("kilometers" if "kilometer" in sp.unit else "meters")
                )
                return Quantity(dist_m, "meters", "length").to(target_len)

            # Power * Time -> Energy
            if (self.dimension == "power" and other.dimension == "time") or (
                self.dimension == "time" and other.dimension == "power"
            ):
                pw = self if self.dimension == "power" else other
                tm = other if self.dimension == "power" else self
                if "kilowatt" in pw.unit and "hour" in tm.unit:
                    return Quantity(
                        pw.to("kilowatts").value * tm.to("hours").value,
                        "kilowatt hours",
                        "energy",
                    )
                j = pw.to("watts").value * tm.to("seconds").value
                return Quantity(j, "joules", "energy")

        raise DoomTypeError(f"Cannot multiply Quantity {self} by {other}.")

    def __rmul__(self, other: Any) -> Union["Quantity", float]:
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> Union["Quantity", float]:
        if isinstance(other, (int, float)):
            if other == 0:
                raise DoomZeroDivisionError("Cannot divide quantity by zero.")
            return Quantity(self.value / float(other), self.unit, self.dimension)
        if isinstance(other, Quantity):
            if other.value == 0:
                raise DoomZeroDivisionError("Cannot divide by quantity of zero.")
            # Same dimension -> dimensionless scalar ratio
            if self.dimension == other.dimension:
                return self.value / other.to(self.unit).value

            # Length / Time -> Speed
            if self.dimension == "length" and other.dimension == "time":
                dist_m = self.to("meters").value
                tm_s = other.to("seconds").value
                speed_mps = dist_m / tm_s
                target_spd = (
                    "miles per hour"
                    if "mile" in self.unit
                    else ("kilometers per hour" if "kilometer" in self.unit else "meters per second")
                )
                return Quantity(speed_mps, "meters per second", "speed").to(target_spd)

            # Length / Speed -> Time
            if self.dimension == "length" and other.dimension == "speed":
                dist_m = self.to("meters").value
                spd_mps = other.to("meters per second").value
                tm_s = dist_m / spd_mps
                target_tm = (
                    "hours"
                    if ("hour" in other.unit or "mile" in self.unit or "kilometer" in self.unit)
                    else "seconds"
                )
                return Quantity(tm_s, "seconds", "time").to(target_tm)

            # Energy / Time -> Power
            if self.dimension == "energy" and other.dimension == "time":
                w = self.to("joules").value / other.to("seconds").value
                return Quantity(w, "watts", "power")

            # Energy / Power -> Time
            if self.dimension == "energy" and other.dimension == "power":
                s = self.to("joules").value / other.to("watts").value
                return Quantity(s, "seconds", "time")

        raise DoomTypeError(f"Cannot divide Quantity {self} by {other}.")

    def __neg__(self) -> "Quantity":
        return Quantity(-self.value, self.unit, self.dimension)

    def __abs__(self) -> "Quantity":
        return Quantity(abs(self.value), self.unit, self.dimension)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Quantity):
            return False
        if self.dimension != other.dimension:
            return False
        return math.isclose(self.value, other.to(self.unit).value, rel_tol=1e-7, abs_tol=1e-9)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Quantity) or self.dimension != other.dimension:
            raise DoomTypeError(f"Cannot compare {self} with {other}.")
        return self.value < other.to(self.unit).value

    def __le__(self, other: Any) -> bool:
        return self < other or self == other

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, Quantity) or self.dimension != other.dimension:
            raise DoomTypeError(f"Cannot compare {self} with {other}.")
        return self.value > other.to(self.unit).value

    def __ge__(self, other: Any) -> bool:
        return self > other or self == other


def make_quantity(val: Union[int, float], unit_name: str) -> Quantity:
    """Creates a Quantity instance from a numeric value and English unit name."""
    return Quantity(val, unit_name)


def convert_unit(val: Any, target_unit: str) -> Quantity:
    """Converts a Quantity to a target unit."""
    if isinstance(val, Quantity):
        return val.to(target_unit)
    raise DoomTypeError(
        f"Cannot convert value '{val}' to '{target_unit}' because it has no source unit of measurement."
    )
