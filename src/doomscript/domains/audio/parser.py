"""Independent Domain Parser for Audio & Sound domain."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.audio.spec import (
    AudioLoadSpec,
    AudioCreateSpec,
    AudioTrimSpec,
    AudioFadeSpec,
    AudioVolumeSpec,
    AudioCombineSpec,
    AudioSaveSpec,
)


class AudioDomainParser(DomainParser):
    """Independent parser for Audio & Sound syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # duration of [audio] <audio_var> into <target>
        m_dur = re.match(
            r"^duration\s+of\s+(?:audio\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dur:
            a_var = m_dur.group(1).strip()
            target = m_dur.group(2).strip()
            return f"set {target} to audio_duration({a_var})"

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # load audio <path> into <target>
        m_load = re.match(
            r"^load\s+audio\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_load:
            path_expr = m_load.group(1).strip()
            target = m_load.group(2).strip()
            return f"set {target} to load_audio({path_expr})"

        # create blank audio with duration <d> [seconds] into <target>
        m_create = re.match(
            r"^create\s+blank\s+audio\s+(?:with\s+duration|of)\s+(\d+(?:\.\d+)?)(?:\s+seconds?)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_create:
            dur = m_create.group(1).strip()
            target = m_create.group(2).strip()
            return f"set {target} to create_blank_audio({dur})"

        # trim [audio] <var> from <start> to <end> [seconds] into <target>
        m_trim = re.match(
            r"^trim\s+(?:audio\s+)?([A-Za-z_]\w*)\s+from\s+(\d+(?:\.\d+)?)\s+to\s+(\d+(?:\.\d+)?)(?:\s+seconds?)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_trim:
            a_var = m_trim.group(1).strip()
            start = m_trim.group(2).strip()
            end = m_trim.group(3).strip()
            target = m_trim.group(4).strip()
            return f"set {target} to trim_audio({a_var}, {start}, {end})"

        # fade [audio] <var> in <fin> [seconds] and fade out <fout> [seconds] into <target>
        m_fade_both = re.match(
            r"^fade\s+(?:audio\s+)?([A-Za-z_]\w*)\s+in\s+(\d+(?:\.\d+)?)(?:\s+seconds?)?\s+and\s+fade\s+out\s+(\d+(?:\.\d+)?)(?:\s+seconds?)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fade_both:
            a_var = m_fade_both.group(1).strip()
            fin = m_fade_both.group(2).strip()
            fout = m_fade_both.group(3).strip()
            target = m_fade_both.group(4).strip()
            return f"set {target} to fade_audio({a_var}, fade_in_sec={fin}, fade_out_sec={fout})"

        # fade [audio] <var> in <fin> [seconds] into <target>
        m_fade_in = re.match(
            r"^fade\s+(?:audio\s+)?([A-Za-z_]\w*)\s+in\s+(\d+(?:\.\d+)?)(?:\s+seconds?)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fade_in:
            a_var = m_fade_in.group(1).strip()
            fin = m_fade_in.group(2).strip()
            target = m_fade_in.group(3).strip()
            return f"set {target} to fade_audio({a_var}, fade_in_sec={fin})"

        # fade [audio] <var> out <fout> [seconds] into <target>
        m_fade_out = re.match(
            r"^fade\s+(?:audio\s+)?([A-Za-z_]\w*)\s+out\s+(\d+(?:\.\d+)?)(?:\s+seconds?)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fade_out:
            a_var = m_fade_out.group(1).strip()
            fout = m_fade_out.group(2).strip()
            target = m_fade_out.group(3).strip()
            return f"set {target} to fade_audio({a_var}, fade_out_sec={fout})"

        # adjust volume of [audio] <var> by <db> [db] into <target>
        m_vol = re.match(
            r"^adjust\s+volume\s+of\s+(?:audio\s+)?([A-Za-z_]\w*)\s+by\s+(-?\d+(?:\.\d+)?)(?:\s*db)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vol:
            a_var = m_vol.group(1).strip()
            db = m_vol.group(2).strip()
            target = m_vol.group(3).strip()
            return f"set {target} to adjust_audio_volume({a_var}, {db})"

        # combine audio <list_expr> into <target>
        m_comb = re.match(
            r"^combine\s+audio\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_comb:
            clips = m_comb.group(1).strip()
            target = m_comb.group(2).strip()
            return f"set {target} to combine_audio({clips})"

        # save audio <var> to <path>
        m_save = re.match(
            r"^save\s+audio\s+([A-Za-z_]\w*)\s+to\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_save:
            a_var = m_save.group(1).strip()
            path_expr = m_save.group(2).strip()
            return f"save_audio({a_var}, {path_expr})"

        # generate sine tone [at] <freq> hz for <dur> seconds into <target>
        m_sine = re.match(
            r"^generate\s+sine\s+tone\s+(?:at\s+)?(.+?)\s*hz\s+for\s+(.+?)\s+seconds?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sine:
            freq, dur, target = m_sine.group(1).strip(), m_sine.group(2).strip(), m_sine.group(3).strip()
            return f"set {target} to audio_generate_sine({freq}, {dur})"

        # normalize audio track <var> into <target>
        m_norm = re.match(
            r"^normalize\s+audio\s+(?:track\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_norm:
            a_var, target = m_norm.group(1).strip(), m_norm.group(2).strip()
            return f"set {target} to audio_normalize({a_var})"

        # [audio|get] duration of [audio] [track] <var> into <target>
        m_adur = re.match(
            r"^(?:audio\s+duration\s+of|get\s+duration\s+of|duration\s+of)\s+(?:audio\s+)?(?:track\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_adur:
            a_var, target = m_adur.group(1).strip(), m_adur.group(2).strip()
            return f"set {target} to audio_duration({a_var})"

        # fade in audio track <var> for <sec> seconds into <target> OR apply fade in of <sec> seconds to audio track <var> into <target>
        m_fade_for = re.match(
            r"^(?:apply\s+fade\s+in\s+of\s+(.+?)\s+seconds?\s+to\s+audio\s+(?:track\s+)?([A-Za-z_]\w*)|fade\s+in\s+audio\s+(?:track\s+)?([A-Za-z_]\w*)\s+for\s+(.+?)\s+seconds?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fade_for:
            if m_fade_for.group(1) is not None:
                sec, a_var, target = m_fade_for.group(1).strip(), m_fade_for.group(2).strip(), m_fade_for.group(5).strip()
            else:
                a_var, sec, target = m_fade_for.group(3).strip(), m_fade_for.group(4).strip(), m_fade_for.group(5).strip()
            return f"set {target} to audio_fade_in({a_var}, {sec})"

        # reverse audio track <var> into <target>
        m_rev = re.match(
            r"^reverse\s+audio\s+(?:track\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rev:
            a_var, target = m_rev.group(1).strip(), m_rev.group(2).strip()
            return f"set {target} to audio_reverse({a_var})"

        # concatenate audio tracks <tracks> into <target> OR concatenate audio track <t1> with <t2> into <target>
        m_concat = re.match(
            r"^(?:concatenate\s+audio\s+track\s+(.+?)\s+with\s+(.+?)|concatenate\s+audio\s+tracks\s+(.+?))\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_concat:
            if m_concat.group(1) is not None:
                t1, t2, target = m_concat.group(1).strip(), m_concat.group(2).strip(), m_concat.group(4).strip()
                return f"set {target} to audio_concatenate([{t1}, {t2}])"
            else:
                tracks_expr, target = m_concat.group(3).strip(), m_concat.group(4).strip()
                return f"set {target} to audio_concatenate({tracks_expr})"

        # generate square wave [with] frequency <f> [and] duration <d> into <target>
        m_sq = re.match(
            r"^generate\s+square\s+wave\s+(?:with\s+)?frequency\s+(.+?)\s+(?:and\s+)?duration\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sq:
            f, d, target = m_sq.group(1).strip(), m_sq.group(2).strip(), m_sq.group(3).strip()
            return f"set {target} to audio_generate_square({f}, {d})"

        # generate sawtooth wave [with] frequency <f> [and] duration <d> into <target>
        m_saw = re.match(
            r"^generate\s+sawtooth\s+wave\s+(?:with\s+)?frequency\s+(.+?)\s+(?:and\s+)?duration\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_saw:
            f, d, target = m_saw.group(1).strip(), m_saw.group(2).strip(), m_saw.group(3).strip()
            return f"set {target} to audio_generate_sawtooth({f}, {d})"

        # generate triangle wave [with] frequency <f> [and] duration <d> into <target>
        m_tri = re.match(
            r"^generate\s+triangle\s+wave\s+(?:with\s+)?frequency\s+(.+?)\s+(?:and\s+)?duration\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tri:
            f, d, target = m_tri.group(1).strip(), m_tri.group(2).strip(), m_tri.group(3).strip()
            return f"set {target} to audio_generate_triangle({f}, {d})"

        # generate white noise [with] duration <d> into <target>
        m_wn = re.match(
            r"^generate\s+white\s+noise\s+(?:with\s+)?duration\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_wn:
            d, target = m_wn.group(1).strip(), m_wn.group(2).strip()
            return f"set {target} to audio_generate_white_noise({d})"

        # adjust gain of <track> by <db> [db] into <target>
        m_gain = re.match(
            r"^adjust\s+gain\s+of\s+(?:audio\s+)?(.+?)\s+by\s+(.+?)(?:\s+db)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_gain:
            t, db, target = m_gain.group(1).strip(), m_gain.group(2).strip(), m_gain.group(3).strip()
            return f"set {target} to audio_adjust_gain_db({t}, {db})"

        # trim silence from <track> [with] threshold <th> into <target>
        m_ts = re.match(
            r"^trim\s+silence\s+from\s+(?:audio\s+)?(.+?)(?:\s+(?:with\s+)?threshold\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ts:
            t, th, target = m_ts.group(1).strip(), m_ts.group(2), m_ts.group(3).strip()
            th_arg = f", {th.strip()}" if th else ""
            return f"set {target} to audio_trim_silence({t}{th_arg})"

        # apply fade out of <dur> seconds to <track> into <target> OR fade out <track> duration <dur> into <target>
        m_fo = re.match(
            r"^(?:apply\s+fade\s+out\s+of\s+(.+?)\s+seconds?\s+to\s+(?:audio\s+)?(.+?)|fade\s+out\s+(?:audio\s+)?(.+?)\s+duration\s+(.+?))\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fo:
            if m_fo.group(1) is not None:
                dur, t, target = m_fo.group(1).strip(), m_fo.group(2).strip(), m_fo.group(5).strip()
            else:
                t, dur, target = m_fo.group(3).strip(), m_fo.group(4).strip(), m_fo.group(5).strip()
            return f"set {target} to audio_apply_fade_out({t}, {dur})"

        # mix [audio] tracks <t1> and <t2> [with weights <w1> and <w2>] into <target> OR mix tracks <list> into <target>
        m_mix_list = re.match(
            r"^mix\s+(?:audio\s+)?tracks\s+\[(.+?)\]\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mix_list:
            items, target = m_mix_list.group(1).strip(), m_mix_list.group(2).strip()
            parts = [x.strip() for x in items.split(",")]
            t1 = parts[0]
            t2 = parts[1] if len(parts) > 1 else parts[0]
            return f"set {target} to audio_mix_tracks({t1}, {t2})"

        m_mix = re.match(
            r"^mix\s+(?:audio\s+)?tracks\s+(.+?)\s+and\s+(.+?)(?:\s+with\s+weights\s+(.+?)\s+and\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mix:
            t1, t2, w1, w2, target = m_mix.group(1).strip(), m_mix.group(2).strip(), m_mix.group(3), m_mix.group(4), m_mix.group(5).strip()
            w_arg = f", {w1.strip()}, {w2.strip()}" if w1 and w2 else ""
            return f"set {target} to audio_mix_tracks({t1}, {t2}{w_arg})"

        # pan [audio|stereo] <track> [with] pan <pan> into <target>
        m_pan = re.match(
            r"^pan\s+(?:audio\s+|stereo\s+)?(.+?)\s+(?:with\s+)?pan\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pan:
            t, p, target = m_pan.group(1).strip(), m_pan.group(2).strip(), m_pan.group(3).strip()
            return f"set {target} to audio_pan_stereo({t}, {p})"

        # [apply] low pass filter [to] <track> [with] cutoff <fc> into <target>
        m_lpf = re.match(
            r"^(?:apply\s+)?low\s+pass\s+filter\s+(?:to\s+)?(?:audio\s+)?(.+?)\s+(?:with\s+)?cutoff\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lpf:
            t, fc, target = m_lpf.group(1).strip(), m_lpf.group(2).strip(), m_lpf.group(3).strip()
            return f"set {target} to audio_low_pass_filter({t}, {fc})"

        # [apply] high pass filter [to] <track> [with] cutoff <fc> into <target>
        m_hpf = re.match(
            r"^(?:apply\s+)?high\s+pass\s+filter\s+(?:to\s+)?(?:audio\s+)?(.+?)\s+(?:with\s+)?cutoff\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hpf:
            t, fc, target = m_hpf.group(1).strip(), m_hpf.group(2).strip(), m_hpf.group(3).strip()
            return f"set {target} to audio_high_pass_filter({t}, {fc})"

        # peak amplitude of <track> into <target>
        m_pa = re.match(
            r"^peak\s+amplitude\s+of\s+(?:audio\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pa:
            t, target = m_pa.group(1).strip(), m_pa.group(2).strip()
            return f"set {target} to audio_peak_amplitude({t})"

        # rms energy of <track> into <target>
        m_rms = re.match(
            r"^rms\s+energy\s+of\s+(?:audio\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rms:
            t, target = m_rms.group(1).strip(), m_rms.group(2).strip()
            return f"set {target} to audio_rms_energy({t})"

        # zero crossing rate of <track> into <target>
        m_zcr = re.match(
            r"^zero\s+crossing\s+rate\s+of\s+(?:audio\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_zcr:
            t, target = m_zcr.group(1).strip(), m_zcr.group(2).strip()
            return f"set {target} to audio_zero_crossing_rate({t})"

        # clip audio [samples] <track> [between <min> and <max> | threshold <th>] into <target>
        m_clip = re.match(
            r"^clip\s+audio(?:\s+samples)?\s+(.+?)\s+(?:between\s+(.+?)\s+and\s+(.+?)|threshold\s+(.+?))\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_clip:
            t = m_clip.group(1).strip()
            if m_clip.group(2) is not None:
                mn, mx = m_clip.group(2).strip(), m_clip.group(3).strip()
                target = m_clip.group(5).strip()
            else:
                th = m_clip.group(4).strip()
                mn, mx = f"-{th}", th
                target = m_clip.group(5).strip()
            return f"set {target} to audio_clip_samples({t}, {mn}, {mx})"

        # loop audio <track> <count> times into <target>
        m_loop = re.match(
            r"^loop\s+(?:audio\s+)?(.+?)\s+(\d+)\s+times\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_loop:
            t, cnt, target = m_loop.group(1).strip(), m_loop.group(2).strip(), m_loop.group(3).strip()
            return f"set {target} to audio_loop_track({t}, {cnt})"

        # apply [delay] echo to <track> [with] delay <del> [and] decay <dec> into <target>
        m_echo = re.match(
            r"^apply\s+(?:delay\s+)?echo\s+to\s+(?:audio\s+)?(.+?)\s+(?:with\s+)?delay\s+(.+?)\s+(?:and\s+)?decay\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_echo:
            t, dly, dcy, target = m_echo.group(1).strip(), m_echo.group(2).strip(), m_echo.group(3).strip(), m_echo.group(4).strip()
            return f"set {target} to audio_delay_echo({t}, {dly}, {dcy})"

        # time stretch [audio] <track> [with] (rate|factor) <rate> into <target>
        m_tsr = re.match(
            r"^time\s+stretch\s+(?:audio\s+)?(.+?)\s+(?:with\s+)?(?:rate|factor)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tsr:
            t, r, target = m_tsr.group(1).strip(), m_tsr.group(2).strip(), m_tsr.group(3).strip()
            return f"set {target} to audio_time_stretch_naive({t}, {r})"

        # generate silence [with] duration <dur> into <target>
        m_sil = re.match(
            r"^generate\s+silence\s+(?:with\s+)?duration\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sil:
            d, target = m_sil.group(1).strip(), m_sil.group(2).strip()
            return f"set {target} to audio_generate_silence({d})"

        # encode ambisonics / hoa 3d [samples] azimuth / with azimuth <az> elevation / and elevation <el> [with order <ord>] into <target>
        m_enc_hoa = re.match(
            r"^(?:encode\s+ambisonics\s+3d|encode\s+hoa\s+3d)(?:\s+([A-Za-z_]\w*))?\s+(?:with\s+azimuth\s+|azimuth\s+)(.+?)\s+(?:and\s+elevation\s+|elevation\s+)(.+?)(?:\s+with\s+order\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_enc_hoa:
            sig = m_enc_hoa.group(1)
            az = m_enc_hoa.group(2).strip()
            el = m_enc_hoa.group(3).strip()
            ord_val = m_enc_hoa.group(4) if m_enc_hoa.group(4) else "1"
            target = m_enc_hoa.group(5).strip()
            sig_arg = f", samples={sig.strip()}" if sig else ""
            return f"set {target} to audio_hoa_3d_encode({az}, {el}, order={ord_val}{sig_arg})"

        # decode ambisonics 3d channels <chans> [with order <ord>] into <target>
        m_dec_hoa = re.match(
            r"^decode\s+(?:ambisonics\s+3d|hoa\s+3d)\s+channels\s+(.+?)(?:\s+with\s+order\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dec_hoa:
            chans = m_dec_hoa.group(1).strip()
            ord_val = m_dec_hoa.group(2) if m_dec_hoa.group(2) else "1"
            target = m_dec_hoa.group(3).strip()
            return f"set {target} to audio_hoa_binaural_decode({chans}, order={ord_val})"

        # apply dynamic compressor / compress dynamic range to <samples> [with threshold <th>] [with ratio <rat>] into <target>
        m_comp = re.match(
            r"^(?:apply\s+dynamic\s+compressor\s+to|compress\s+dynamic\s+range)\s+(.+?)(?:\s+with\s+threshold\s+(.+?))?(?:\s+(?:with|and)\s+ratio\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_comp:
            smps = m_comp.group(1).strip()
            th = m_comp.group(2).strip() if m_comp.group(2) else "-12.0"
            rat = m_comp.group(3).strip() if m_comp.group(3) else "4.0"
            target = m_comp.group(4).strip()
            return f"set {target} to audio_dynamic_compressor({smps}, threshold_db={th}, ratio={rat})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Audio domain does not currently define declarative blocks")
