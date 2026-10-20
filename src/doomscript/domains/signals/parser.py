"""Signals Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class SignalsDomainParser(DomainParser):
    """Parses spoken-English DSP, wavelet, and signal filtering statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # decompose signal <sig> using haar wavelet into <target>
        m_haar = re.match(
            r"^decompose\s+signal\s+(.+?)\s+using\s+haar\s+wavelet\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_haar:
            sig, target = m_haar.group(1).strip(), m_haar.group(2).strip()
            return f"set {target} to signals_haar_dwt({sig})"

        # apply fir lowpass filter to <sig> with cutoff <cut> and rate <rate> into <target>
        m_fir = re.match(
            r"^apply\s+fir\s+lowpass\s+filter\s+to\s+(.+?)\s+with\s+cutoff\s+(.+?)\s+and\s+rate\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fir:
            sig, cut, rate, target = m_fir.group(1).strip(), m_fir.group(2).strip(), m_fir.group(3).strip(), m_fir.group(4).strip()
            return f"set {target} to signals_fir_lowpass({sig}, 31, {cut}, {rate})"

        # calculate analytic signal of <sig> using hilbert into <target>
        m_hilb = re.match(
            r"^calculate\s+analytic\s+signal\s+of\s+(.+?)\s+using\s+hilbert\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hilb:
            sig, target = m_hilb.group(1).strip(), m_hilb.group(2).strip()
            return f"set {target} to signals_hilbert({sig})"

        # find peaks in signal <sig> [with prominence <p>] [distance <d>] into <target>
        m_peaks = re.match(
            r"^find\s+peaks\s+in\s+signal\s+(.+?)(?:\s+with\s+prominence\s+(.+?))?(?:\s+distance\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_peaks:
            sig = m_peaks.group(1).strip()
            prom = m_peaks.group(2).strip() if m_peaks.group(2) else "0.1"
            dist = m_peaks.group(3).strip() if m_peaks.group(3) else "1"
            target = m_peaks.group(4).strip()
            return f"set {target} to signals_find_peaks({sig}, min_prominence={prom}, min_distance={dist})"

        # compute fft of signal <sig> into <target>
        m_fft = re.match(
            r"^compute\s+fft\s+of\s+(?:signal\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fft:
            sig, target = m_fft.group(1).strip(), m_fft.group(2).strip()
            return f"set {target} to signals_fft({sig})"

        # compute ifft of spectrum <spec> into <target>
        m_ifft = re.match(
            r"^compute\s+ifft\s+of\s+(?:spectrum\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ifft:
            spec, target = m_ifft.group(1).strip(), m_ifft.group(2).strip()
            return f"set {target} to signals_ifft({spec})"

        # cross correlate signal <x> with <y> into <target>
        m_xcorr = re.match(
            r"^(?:cross\s+correlate|correlate)\s+(?:signal\s+)?(.+?)\s+with\s+(?:signal\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_xcorr:
            x, y, target = m_xcorr.group(1).strip(), m_xcorr.group(2).strip(), m_xcorr.group(3).strip()
            return f"set {target} to signals_cross_correlation({x}, {y})"

        # detect pitch in signal <sig> [with rate <rate>] into <target>
        m_pitch = re.match(
            r"^detect\s+pitch\s+in\s+(?:signal\s+)?(.+?)(?:\s+with\s+rate\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pitch:
            sig = m_pitch.group(1).strip()
            rate = m_pitch.group(2).strip() if m_pitch.group(2) else "44100"
            target = m_pitch.group(3).strip()
            return f"set {target} to signals_detect_pitch({sig}, sample_rate={rate})"

        # compute lomb scargle periodogram for times <t> and values <y> at frequencies <f> into <target>
        m_lsp = re.match(
            r"^compute\s+lomb\s+scargle\s+(?:periodogram\s+)?for\s+times\s+(.+?)\s+and\s+values\s+(.+?)\s+at\s+frequencies\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lsp:
            t, y, freqs, target = m_lsp.group(1).strip(), m_lsp.group(2).strip(), m_lsp.group(3).strip(), m_lsp.group(4).strip()
            return f"set {target} to signals_lomb_scargle({t}, {y}, {freqs})"

        # smooth signal <sig> using savitzky golay [with window <w>] [order <o>] into <target>
        m_sg = re.match(
            r"^smooth\s+signal\s+(.+?)\s+using\s+savitzky\s+golay(?:\s+with\s+window\s+(.+?))?(?:\s+order\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sg:
            sig = m_sg.group(1).strip()
            win = m_sg.group(2).strip() if m_sg.group(2) else "7"
            order = m_sg.group(3).strip() if m_sg.group(3) else "2"
            target = m_sg.group(4).strip()
            return f"set {target} to signals_savitzky_golay({sig}, window_length={win}, poly_order={order})"

        # filter measurements <z> using kalman with transition <F> and observation <H> and process noise <Q> and measurement noise <R> into <target>
        m_kf = re.match(
            r"^filter\s+measurements\s+(.+?)\s+using\s+kalman\s+with\s+transition\s+(.+?)\s+and\s+observation\s+(.+?)\s+and\s+process\s+noise\s+(.+?)\s+and\s+measurement\s+noise\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_kf:
            z, F, H, Q, R, target = (
                m_kf.group(1).strip(),
                m_kf.group(2).strip(),
                m_kf.group(3).strip(),
                m_kf.group(4).strip(),
                m_kf.group(5).strip(),
                m_kf.group(6).strip(),
            )
            return f"set {target} to signals_kalman_filter({z}, {F}, {H}, {Q}, {R})"

        # apply butterworth lowpass filter to <sig> with cutoff <cut> [order <ord>] [rate <rate>] into <target>
        m_bw = re.match(
            r"^apply\s+butterworth\s+lowpass\s+filter\s+to\s+(.+?)\s+with\s+cutoff\s+(.+?)(?:\s+order\s+(.+?))?(?:\s+rate\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bw:
            sig = m_bw.group(1).strip()
            cut = m_bw.group(2).strip()
            order = m_bw.group(3).strip() if m_bw.group(3) else "4"
            rate = m_bw.group(4).strip() if m_bw.group(4) else "1000.0"
            target = m_bw.group(5).strip()
            return f"set {target} to signals_butterworth_lowpass({sig}, cutoff_hz={cut}, order={order}, sample_rate={rate})"

        # decompose signal <sig> into imfs [max <n>] into <target>
        m_emd = re.match(
            r"^decompose\s+signal\s+(.+?)\s+into\s+imfs(?:\s+max\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_emd:
            sig = m_emd.group(1).strip()
            max_imfs = m_emd.group(2).strip() if m_emd.group(2) else "4"
            target = m_emd.group(3).strip()
            return f"set {target} to signals_emd_decompose({sig}, max_imfs={max_imfs})"

        # compute chirp z-transform / czt of <sig> [with <n> bins] into <target>
        m_czt = re.match(
            r"^(?:compute\s+chirp\s+z-transform\s+of|compute\s+czt\s+of|czt\s+of)\s+(.+?)(?:\s+with\s+(\d+)\s+bins)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_czt:
            sig = m_czt.group(1).strip()
            bins = m_czt.group(2) or "16"
            target = m_czt.group(3).strip()
            return f"set {target} to signals_czt({sig}, num_bins={bins})"

        # solve levinson durbin for <autocorr> [with order <p>] into <target>
        m_lev = re.match(
            r"^(?:solve\s+levinson\s+durbin\s+for|levinson\s+durbin\s+for)\s+(.+?)(?:\s+with\s+order\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lev:
            ac = m_lev.group(1).strip()
            p = m_lev.group(2) or "4"
            target = m_lev.group(3).strip()
            return f"set {target} to signals_levinson_durbin({ac}, order={p})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Signals domain does not define declarative blocks")
