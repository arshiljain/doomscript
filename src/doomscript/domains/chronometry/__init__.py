from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.chronometry.runtime import (
    chrono_julian_day_number, chrono_greenwich_mean_sidereal_time,
    chrono_equation_of_time, chrono_relativistic_time_dilation,
    chrono_gravitational_time_dilation, chrono_solar_declination
)
from doomscript.domains.chronometry.parser import ChronometryDomainParser
from doomscript.domains.chronometry.exporter import ChronometryASTExporter

class ChronometryRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class ChronometryDomain(DomainContract):
    name = "chronometry"
    aliases = ["chrono", "horology", "sidereal_time"]
    description = "Precision timekeeping and astronomical chronology: Julian Day, GMST, Equation of Time, Special & General Relativistic dilation, and Solar declination"
    parser = ChronometryDomainParser()
    runtime = ChronometryRuntime()
    exporter = ChronometryASTExporter()
    capabilities = ["julian_day_number", "gmst", "equation_of_time", "relativistic_time_dilation", "gravitational_dilation", "solar_declination"]
    verbs = [
        VerbSpec(pattern="calculate julian day year {y:expr} month {m:expr} day {d:expr} into {target:ident}", description="Julian Day Number"),
        VerbSpec(pattern="calculate gmst jdn {jdn:expr} into {target:ident}", description="Greenwich Mean Sidereal Time"),
        VerbSpec(pattern="calculate equation of time day {d:expr} into {target:ident}", description="Equation of Time"),
        VerbSpec(pattern="calculate time dilation proper {t0:expr} velocity {v:expr} into {target:ident}", description="Relativistic time dilation"),
        VerbSpec(pattern="calculate gravitational dilation proper {t0:expr} mass {m:expr} radius {r:expr} into {target:ident}", description="Gravitational time dilation"),
        VerbSpec(pattern="calculate solar declination day {d:expr} into {target:ident}", description="Solar declination angle")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate julian day ") or s.startswith("calculate gmst ") or s.startswith("calculate equation of time ") or s.startswith("calculate time dilation ") or s.startswith("calculate gravitational dilation ") or s.startswith("calculate solar declination ")

CHRONOMETRY_DOMAIN = ChronometryDomain()
get_domain_registry().register(CHRONOMETRY_DOMAIN)

__all__ = [
    "ChronometryDomain", "CHRONOMETRY_DOMAIN", "ChronometryRuntime",
    "chrono_julian_day_number", "chrono_greenwich_mean_sidereal_time",
    "chrono_equation_of_time", "chrono_relativistic_time_dilation",
    "chrono_gravitational_time_dilation", "chrono_solar_declination"
]
