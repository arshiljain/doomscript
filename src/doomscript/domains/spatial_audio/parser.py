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

        # calculate spherical harmonics azimuth <az> elevation <el> [order <ord>] into <target>
        m_sh = re.match(
            r"^calculate\s+spherical\s+harmonics\s+azimuth\s+(.+?)\s+elevation\s+(.+?)(?:\s+order\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sh:
            az, el = m_sh.group(1).strip(), m_sh.group(2).strip()
            ord_val = m_sh.group(3).strip() if m_sh.group(3) else "2"
            target = m_sh.group(4).strip()
            return f"set {target} to spatial_audio_spherical_harmonics_encode({az}, {el}, order={ord_val})"

        # simulate acoustic ray tracing room <dims> source <src> receiver <rec> [absorption <abs>] [rays <rays>] into <target>
        m_rt = re.match(
            r"^simulate\s+acoustic\s+ray\s+tracing\s+room\s+(.+?)\s+source\s+(.+?)\s+receiver\s+(.+?)(?:\s+absorption\s+(.+?))?(?:\s+rays\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rt:
            dims, src, rec = m_rt.group(1).strip(), m_rt.group(2).strip(), m_rt.group(3).strip()
            abs_val = m_rt.group(4).strip() if m_rt.group(4) else "0.15"
            rays_val = m_rt.group(5).strip() if m_rt.group(5) else "60"
            target = m_rt.group(6).strip()
            return f"set {target} to spatial_audio_ray_trace_room({dims}, {src}, {rec}, absorption={abs_val}, num_rays={rays_val})"

        # generate binaural room impulse response room <dims> source <src> listener <lis> [order <ord>] [absorption <abs>] [sample rate <fs>] into <target>
        m_brir = re.match(
            r"^generate\s+binaural\s+room\s+impulse\s+response\s+room\s+(.+?)\s+source\s+(.+?)\s+listener\s+(.+?)(?:\s+order\s+(\d+))?(?:\s+absorption\s+(.+?))?(?:\s+sample\s+rate\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_brir:
            dims, src, lis = m_brir.group(1).strip(), m_brir.group(2).strip(), m_brir.group(3).strip()
            ord_val = m_brir.group(4).strip() if m_brir.group(4) else "2"
            abs_val = m_brir.group(5).strip() if m_brir.group(5) else "0.2"
            fs = m_brir.group(6).strip() if m_brir.group(6) else "16000"
            target = m_brir.group(7).strip()
            return f"set {target} to spatial_generate_brir({dims}, {src}, {lis}, max_order={ord_val}, absorption={abs_val}, sample_rate={fs})"

        # decode b format ambisonics to binaural w <w> x <x> y <y> z <z> [virtual speakers <num>] into <target>
        m_amb_dec = re.match(
            r"^decode\s+b\s+format\s+ambisonics\s+to\s+binaural\s+w\s+(.+?)\s+x\s+(.+?)\s+y\s+(.+?)\s+z\s+(.+?)(?:\s+virtual\s+speakers\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_amb_dec:
            w, x, y, z = m_amb_dec.group(1).strip(), m_amb_dec.group(2).strip(), m_amb_dec.group(3).strip(), m_amb_dec.group(4).strip()
            vs = m_amb_dec.group(5).strip() if m_amb_dec.group(5) else "8"
            target = m_amb_dec.group(6).strip()
            return f"set {target} to spatial_ambisonics_binaural_decode({w}, {x}, {y}, {z}, num_virtual_speakers={vs})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Spatial audio domain does not define declarative blocks")
