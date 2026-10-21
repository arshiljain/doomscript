import types
import pytest
from doomscript.compiler.engine import execute
import doomscript.runtime as runtime


def test_get_runtime_exports_returns_defensive_copy():
    exports1 = runtime.get_runtime_exports()
    assert isinstance(exports1, dict)
    
    # Mutating the returned copy must not mutate the registry or future calls
    exports1["__hacked_entry__"] = True
    exports2 = runtime.get_runtime_exports()
    assert "__hacked_entry__" not in exports2


def test_runtime_exports_immutability():
    proxy = getattr(runtime, "_CORE_RUNTIME_EXPORTS", None)
    assert proxy is not None, "_CORE_RUNTIME_EXPORTS must exist on doomscript.runtime"
    assert isinstance(proxy, types.MappingProxyType)
    
    with pytest.raises(TypeError):
        proxy["new_entry"] = 123


def test_no_unwanted_modules_in_exports():
    exports = runtime.get_runtime_exports()
    leaked_modules = [k for k, v in exports.items() if isinstance(v, types.ModuleType)]
    assert leaked_modules == [], f"Found leaked raw modules in runtime exports: {leaked_modules}"
    
    forbidden_names = {"sys", "os", "subprocess", "re", "threading", "sqlite3", "ctypes"}
    for name in forbidden_names:
        assert name not in exports, f"Forbidden module or raw system name '{name}' found in runtime exports"


def test_essential_core_symbols_present():
    exports = runtime.get_runtime_exports()
    required_symbols = [
        "Record", "DoomCLI", "DoomDocument", "DoomScheduler",
        "sleep", "percent_of", "count_of", "write_file", "read_file",
        "fetch_json", "fetch_text", "math_round", "math_abs", "math_sqrt",
        "ask_input", "ask_choice", "ask_number", "ask_boolean",
        "date_today", "date_now", "item_of", "set_item", "sorted_list",
        "crypto_hash", "crypto_token", "benchmark_block",
    ]
    missing = [sym for sym in required_symbols if sym not in exports]
    assert missing == [], f"Missing required core symbols in runtime exports: {missing}"


def test_execution_with_explicit_exports():
    code = """
set a to 10
set b to 20
set total to a + b
set half to percent_of(50, total)
"""
    env = execute(code)
    assert env["total"] == 30
    assert env["half"] == 15.0
