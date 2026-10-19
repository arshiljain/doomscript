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
            r"^create\s+blank\s+audio\s+with\s+duration\s+(\d+(?:\.\d+)?)(?:\s+seconds?)?\s+into\s+([A-Za-z_]\w*)$",
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

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Audio domain does not currently define declarative blocks")
