"""Spatial Audio Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class SpatialAudioDomainParser(DomainParser):
    """Parses spoken-English binaural, Ambisonics, and 3D spatial audio statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # spatialize audio <sig> at azimuth <az> into <target>
        m_bin = re.match(
            r"^spatialize\s+audio\s+(.+?)\s+at\s+azimuth\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bin:
            sig, az, target = m_bin.group(1).strip(), m_bin.group(2).strip(), m_bin.group(3).strip()
            return f"set {target} to spatial_audio_binaural({sig}, {az})"

        # encode ambisonics <sig> at azimuth <az> elevation <el> into <target>
        m_amb = re.match(
            r"^encode\s+ambisonics\s+(.+?)\s+at\s+azimuth\s+(.+?)\s+elevation\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_amb:
            sig, az, el, target = (
                m_amb.group(1).strip(),
                m_amb.group(2).strip(),
                m_amb.group(3).strip(),
                m_amb.group(4).strip(),
            )
            return f"set {target} to spatial_audio_ambisonics_encode({sig}, {az}, {el})"

        # apply reverb to <sig> with rt60 <rt60> into <target>
        m_rev = re.match(
            r"^apply\s+reverb\s+to\s+(.+?)\s+with\s+rt60\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rev:
            sig, rt60, target = m_rev.group(1).strip(), m_rev.group(2).strip(), m_rev.group(3).strip()
            return f"set {target} to spatial_audio_schroeder_reverb({sig}, rt60={rt60})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Spatial audio domain does not define declarative blocks")
