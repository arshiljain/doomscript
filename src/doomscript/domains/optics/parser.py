"""Optics Domain Natural Language Parser."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class OpticsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate thin lens focal <f> distance <do> into <target>
        m_lens = re.match(r"^calculate\s+thin\s+lens\s+focal\s+(.+?)\s+distance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_lens:
            return f"set {m_lens.group(3)} to optics_thin_lens({m_lens.group(1)}, {m_lens.group(2)})"

        # calculate snell refraction n1 <n1> n2 <n2> angle <theta> into <target>
        m_snell = re.match(r"^calculate\s+snell\s+refraction\s+n1\s+(.+?)\s+n2\s+(.+?)\s+angle\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_snell:
            return f"set {m_snell.group(4)} to optics_snell_refraction({m_snell.group(1)}, {m_snell.group(2)}, {m_snell.group(3)})"

        # calculate fresnel reflectance n1 <n1> n2 <n2> into <target>
        m_fresnel = re.match(r"^calculate\s+fresnel\s+reflectance\s+n1\s+(.+?)\s+n2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_fresnel:
            return f"set {m_fresnel.group(3)} to optics_fresnel_reflectance({m_fresnel.group(1)}, {m_fresnel.group(2)})"

        # calculate rayleigh resolution wavelength <lam> na <na> into <target>
        m_rayleigh = re.match(r"^calculate\s+rayleigh\s+resolution\s+wavelength\s+(.+?)\s+na\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rayleigh:
            return f"set {m_rayleigh.group(3)} to optics_rayleigh_resolution({m_rayleigh.group(1)}, {m_rayleigh.group(2)})"

        # calculate grating diffraction lines <lines> order <m> wavelength <lam> into <target>
        m_grating = re.match(r"^calculate\s+grating\s+diffraction\s+lines\s+(.+?)\s+order\s+(.+?)\s+wavelength\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_grating:
            return f"set {m_grating.group(4)} to optics_diffraction_grating({m_grating.group(1)}, {m_grating.group(2)}, {m_grating.group(3)})"

        # calculate brewster angle n1 <n1> n2 <n2> into <target>
        m_brew = re.match(r"^calculate\s+brewster\s+angle\s+n1\s+(.+?)\s+n2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_brew:
            return f"set {m_brew.group(3)} to optics_brewster_angle({m_brew.group(1)}, {m_brew.group(2)})"

        # calculate fiber aperture core <n1> clad <n2> into <target>
        m_fiber = re.match(r"^calculate\s+fiber\s+aperture\s+core\s+(.+?)\s+clad\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_fiber:
            return f"set {m_fiber.group(3)} to optics_fiber_numerical_aperture({m_fiber.group(1)}, {m_fiber.group(2)})"

        # calculate gaussian beam wavelength <lam> waist <w0> distance <z> into <target>
        m_gauss = re.match(r"^calculate\s+gaussian\s+beam\s+wavelength\s+(.+?)\s+waist\s+(.+?)\s+distance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gauss:
            return f"set {m_gauss.group(4)} to optics_gaussian_beam({m_gauss.group(1)}, {m_gauss.group(2)}, {m_gauss.group(3)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Optics domain does not define declarative blocks")
