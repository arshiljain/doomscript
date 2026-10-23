from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.chronometry.runtime import (
    ChronometryRuntime, chrono_julian_day_number,
    chrono_greenwich_mean_sidereal_time, chrono_equation_of_time,
    chrono_relativistic_time_dilation, chrono_gravitational_time_dilation,
    chrono_solar_declination, chrono_gps_relativistic_drift,
    chrono_sunrise_sunset_hours
)
from doomscript.domains.chronometry.parser import ChronometryDomainParser
from doomscript.domains.chronometry.exporter import ChronometryASTExporter

class ChronometryDomain(DomainContract):
    name = "chronometry"
    aliases = ["chrono", "horology", "sidereal_time"]
    description = "Deepened Chronometry domain: Julian Day Numbers, GMST, Equation of Time, Special & General Relativity, GPS clock drift, and solar ephemeris"
    parser = ChronometryDomainParser()
    runtime = ChronometryRuntime()
    exporter = ChronometryASTExporter()
    capabilities = ["julian_day", "gmst", "equation_of_time", "relativistic_dilation", "gravitational_dilation", "solar_declination", "gps_drift", "daylight"]
    verbs = [
        VerbSpec(pattern="calculate julian day year {y:expr} month {m:expr} day {d:expr} into {target:ident}", description="Julian Day Number"),
        VerbSpec(pattern="calculate gmst jdn {jdn:expr} into {target:ident}", description="Greenwich Mean Sidereal Time"),
        VerbSpec(pattern="calculate equation of time day {d:expr} into {target:ident}", description="Equation of Time"),
        VerbSpec(pattern="calculate time dilation proper {t0:expr} velocity {v:expr} into {target:ident}", description="Special relativistic time dilation"),
        VerbSpec(pattern="calculate gravitational dilation proper {t0:expr} mass {m:expr} radius {r:expr} into {target:ident}", description="General relativistic gravitational time dilation"),
        VerbSpec(pattern="calculate solar declination day {d:expr} into {target:ident}", description="Solar declination angle"),
        VerbSpec(pattern="calculate gps drift altitude {alt:expr} velocity {v:expr} into {target:ident}", description="GPS relativistic net clock drift")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate julian day ") or
            s.startswith("calculate gmst ") or
            s.startswith("calculate equation of time ") or
            s.startswith("calculate time dilation ") or
            s.startswith("calculate gravitational dilation ") or
            s.startswith("calculate solar declination ") or
            s.startswith("calculate gps drift ")
        )

CHRONOMETRY_DOMAIN = ChronometryDomain()
get_domain_registry().register(CHRONOMETRY_DOMAIN)

__all__ = [
    "CHRONOMETRY_DOMAIN", "ChronometryDomain", "ChronometryRuntime",
    "chrono_julian_day_number", "chrono_greenwich_mean_sidereal_time",
    "chrono_equation_of_time", "chrono_relativistic_time_dilation",
    "chrono_gravitational_time_dilation", "chrono_solar_declination",
    "chrono_gps_relativistic_drift", "chrono_sunrise_sunset_hours"
]
