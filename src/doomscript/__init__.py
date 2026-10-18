"""
DoomScript: An English-First Programming Language that compiles to Python AST.
"""

from doomscript.compiler.engine import compile_to_ast, transpile, execute
from doomscript.runtime import (
    Record, sleep, percent_of, write_file, append_file, read_file, count_of,
    beep, play_sound, open_window, draw_circle, draw_rectangle, draw_text,
    clear_screen, refresh_screen, fetch_json, fetch_text, download_file,
    time_future, time_past
)

__version__ = "0.8.0"
__all__ = [
    "compile_to_ast", "transpile", "execute", "Record", "sleep", "percent_of",
    "write_file", "append_file", "read_file", "count_of", "beep", "play_sound",
    "open_window", "draw_circle", "draw_rectangle", "draw_text",
    "clear_screen", "refresh_screen", "fetch_json", "fetch_text", "download_file",
    "time_future", "time_past"
]
