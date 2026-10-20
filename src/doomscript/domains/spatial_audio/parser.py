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

        # encode hoa 2nd order audio <sig> at azimuth <az> elevation <el> into <target>
        m_hoa = re.match(
            r"^encode\s+hoa\s+(?:2nd\s+order\s+)?audio\s+(.+?)\s+at\s+azimuth\s+(.+?)\s+elevation\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hoa:
            sig, az, el, target = m_hoa.group(1).strip(), m_hoa.group(2).strip(), m_hoa.group(3).strip(), m_hoa.group(4).strip()
            return f"set {target} to spatial_audio_hoa_encode({sig}, {az}, {el})"

        # decode hoa audio <hoa> to speakers <speakers> into <target>
        m_hdec = re.match(
            r"^decode\s+hoa\s+audio\s+(.+?)\s+to\s+speakers\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hdec:
            hoa, spk, target = m_hdec.group(1).strip(), m_hdec.group(2).strip(), m_hdec.group(3).strip()
            return f"set {target} to HigherOrderAmbisonics.decode_to_loudspeakers({hoa}, {spk})"

        # simulate room impulse response in room <dims> with source <src> and listener <lis> [duration <dur>] into <target>
        m_rir = re.match(
            r"^simulate\s+room\s+impulse\s+response\s+in\s+room\s+(.+?)\s+with\s+source\s+(.+?)\s+and\s+listener\s+(.+?)(?:\s+duration\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rir:
            dims, src, lis = m_rir.group(1).strip(), m_rir.group(2).strip(), m_rir.group(3).strip()
            dur = m_rir.group(4).strip() if m_rir.group(4) else "0.1"
            target = m_rir.group(5).strip()
            return f"set {target} to spatial_audio_room_impulse_response({dims}, {src}, {lis}, duration_sec={dur})"

        # render hrtf binaural audio <sig> at azimuth <az> elevation <el> into <target>
        m_hrtf = re.match(
            r"^render\s+hrtf\s+binaural\s+audio\s+(.+?)\s+at\s+azimuth\s+(.+?)\s+elevation\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hrtf:
            sig, az, el, target = m_hrtf.group(1).strip(), m_hrtf.group(2).strip(), m_hrtf.group(3).strip(), m_hrtf.group(4).strip()
            return f"set {target} to spatial_audio_hrtf_binaural({sig}, {az}, {el})"

        # calculate vbap gains for azimuth <az> on speakers <speakers> into <target>
        m_vbap = re.match(
            r"^calculate\s+vbap\s+gains\s+for\s+azimuth\s+(.+?)\s+on\s+speakers\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vbap:
            az, spk, target = m_vbap.group(1).strip(), m_vbap.group(2).strip(), m_vbap.group(3).strip()
            return f"set {target} to spatial_audio_vbap_2d({az}, {spk})"

        # attenuate audio <sig> at distance <dist> [reference <ref>] [rolloff <ro>] into <target>
        m_att = re.match(
            r"^attenuate\s+audio\s+(.+?)\s+at\s+distance\s+(.+?)(?:\s+reference\s+(.+?))?(?:\s+rolloff\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_att:
            sig, dist = m_att.group(1).strip(), m_att.group(2).strip()
            ref = m_att.group(3).strip() if m_att.group(3) else "1.0"
            ro = m_att.group(4).strip() if m_att.group(4) else "1.0"
            target = m_att.group(5).strip()
            return f"set {target} to spatial_audio_distance_attenuate({sig}, {dist}, ref_distance={ref}, rolloff={ro})"

        # calculate early reflections in room <dims> from source <src> to receiver <rec> into <target>
        m_refl = re.match(
            r"^calculate\s+early\s+reflections\s+in\s+room\s+(.+?)\s+from\s+source\s+(.+?)\s+to\s+receiver\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_refl:
            dims, src, rec, target = m_refl.group(1).strip(), m_refl.group(2).strip(), m_refl.group(3).strip(), m_refl.group(4).strip()
            return f"set {target} to spatial_audio_early_reflections({dims}, {src}, {rec})"

        # convolve audio <sig> with impulse response <ir> into <target>
        m_conv = re.match(
            r"^convolve\s+audio\s+(.+?)\s+with\s+impulse\s+response\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_conv:
            sig, ir, target = m_conv.group(1).strip(), m_conv.group(2).strip(), m_conv.group(3).strip()
            return f"set {target} to spatial_audio_convolve_ir({sig}, {ir})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Spatial audio domain does not define declarative blocks")
