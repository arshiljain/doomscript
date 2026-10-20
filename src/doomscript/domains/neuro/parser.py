"""Neuro Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class NeuroDomainParser(DomainParser):
    """Parses spoken-English neuromorphic, LIF neuron, and STDP statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # create lif neuron [with tau <tau>] into <target>
        m_lif = re.match(
            r"^create\s+lif\s+neuron(?:\s+with\s+tau\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lif:
            tau = m_lif.group(1).strip() if m_lif.group(1) else None
            target = m_lif.group(2).strip()
            if tau is not None:
                return f"set {target} to neuro_create_lif(tau_m={tau})"
            return f"set {target} to neuro_create_lif()"

        # generate poisson spikes with rate <rate> duration <dur> into <target>
        m_pois = re.match(
            r"^generate\s+poisson\s+spikes\s+with\s+rate\s+(.+?)\s+duration\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pois:
            rate, dur, target = m_pois.group(1).strip(), m_pois.group(2).strip(), m_pois.group(3).strip()
            return f"set {target} to neuro_poisson_spikes({rate}, {dur})"

        # apply stdp to weight <w> with delta t <dt> into <target>
        m_stdp = re.match(
            r"^apply\s+stdp\s+to\s+weight\s+(.+?)\s+with\s+delta\s+t\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_stdp:
            w, dt, target = m_stdp.group(1).strip(), m_stdp.group(2).strip(), m_stdp.group(3).strip()
            return f"set {target} to neuro_stdp_update({w}, {dt})"

        # simulate hodgkin huxley with current <curr> duration <dur> into <target>
        m_hh = re.match(
            r"^simulate\s+hodgkin\s+huxley\s+with\s+current\s+(.+?)\s+duration\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hh:
            curr, dur, target = m_hh.group(1).strip(), m_hh.group(2).strip(), m_hh.group(3).strip()
            return f"set {target} to neuro_simulate_hodgkin_huxley({curr}, {dur})"

        # simulate wilson cowan with p_ext <p_ext> duration <dur> into <target>
        m_wc = re.match(
            r"^simulate\s+wilson\s+cowan\s+with\s+p_ext\s+(.+?)\s+duration\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_wc:
            p_ext, dur, target = m_wc.group(1).strip(), m_wc.group(2).strip(), m_wc.group(3).strip()
            return f"set {target} to neuro_simulate_wilson_cowan({p_ext}, {dur})"

        # analyze eeg bands in <sig> [with sample rate <sr>] into <target>
        m_eeg = re.match(
            r"^analyze\s+eeg\s+bands\s+in\s+(.+?)(?:\s+with\s+sample\s+rate\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_eeg:
            sig = m_eeg.group(1).strip()
            sr = m_eeg.group(2).strip() if m_eeg.group(2) else "250"
            target = m_eeg.group(3).strip()
            return f"set {target} to neuro_analyze_eeg_bands({sig}, {sr})"

        # compute psth for trials <trials> duration <dur> [with bin width <bw>] into <target>
        m_psth = re.match(
            r"^compute\s+psth\s+for\s+trials\s+(.+?)\s+duration\s+(.+?)(?:\s+with\s+bin\s+width\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_psth:
            trials, dur = m_psth.group(1).strip(), m_psth.group(2).strip()
            bw = m_psth.group(3).strip() if m_psth.group(3) else "10.0"
            target = m_psth.group(4).strip()
            return f"set {target} to neuro_compute_psth({trials}, {dur}, {bw})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Neuro domain does not define declarative blocks")
