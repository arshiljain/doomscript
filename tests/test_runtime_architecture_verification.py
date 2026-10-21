"""Verification of Runtime Architecture & Explicit Registry.

Validates:
1. Clean imports and zero unvetted leakage into execution globals.
2. Defensive copying and immutability of the internal mapping.
3. Decoupling of domain IR executors into domain packages with backward-compatible re-exports.
4. Security non-sandbox documentation clarity.
"""

import sys
import types
import pytest
from doomscript import runtime
from doomscript.core.exports import (
    CORE_EXPORT_NAMES,
    COMPATIBILITY_DOMAIN_EXPORT_NAMES,
    ALL_RUNTIME_EXPORT_NAMES,
)


def test_registry_defensive_copy():
    """Verify get_runtime_exports() returns a new mutable dict copy from frozen mapping."""
    exports1 = runtime.get_runtime_exports()
    exports2 = runtime.get_runtime_exports()
    assert exports1 is not exports2
    assert isinstance(exports1, dict)

    # Modifying the returned copy must not mutate the internal registry
    exports1["__malicious_injected_var__"] = 12345
    fresh_exports = runtime.get_runtime_exports()
    assert "__malicious_injected_var__" not in fresh_exports


def test_registry_internal_immutability():
    """Verify _CORE_RUNTIME_EXPORTS is a MappingProxyType and cannot be mutated."""
    assert isinstance(runtime._CORE_RUNTIME_EXPORTS, types.MappingProxyType)
    with pytest.raises(TypeError):
        runtime._CORE_RUNTIME_EXPORTS["new_key"] = "test"


def test_absence_of_accidental_exports():
    """Verify that no unvetted private or accidental globals leak into get_runtime_exports()."""
    exports = runtime.get_runtime_exports()
    for name in exports:
        assert name in ALL_RUNTIME_EXPORT_NAMES, f"Accidental export found in runtime: {name}"
        assert not name.startswith("_"), f"Private identifier leaked: {name}"


def test_domain_implementation_extraction_parity():
    """Verify that domain IR executors and helpers live in domain modules and are re-exported by runtime."""
    from doomscript.domains.data.runtime import execute_data_ir as data_ir_orig, load_table as load_table_orig
    from doomscript.domains.ml.runtime import execute_ml_ir as ml_ir_orig, accuracy_score_fn as acc_orig
    from doomscript.domains.dsa.runtime import execute_dsa_ir as dsa_ir_orig, dsa_push as push_orig
    from doomscript.domains.db.runtime import execute_db_ir as db_ir_orig, insert_rows as insert_orig
    from doomscript.domains.sim.runtime import execute_sim_ir as sim_ir_orig, run_trials as trials_orig
    from doomscript.domains.opt.runtime import execute_opt_ir as opt_ir_orig, solve_linear_program as solve_lp_orig
    from doomscript.domains.net.runtime import execute_net_ir as net_ir_orig
    from doomscript.domains.nlp.runtime import execute_nlp_ir as nlp_ir_orig
    from doomscript.domains.geo.runtime import execute_geo_ir as geo_ir_orig
    from doomscript.viz import plot_table as plot_orig, show_plot as show_orig

    # Ensure runtime re-exports refer to the exact domain implementations
    assert runtime.execute_data_ir is data_ir_orig
    assert runtime.load_table is load_table_orig
    assert runtime.execute_ml_ir is ml_ir_orig
    assert runtime.accuracy_score_fn is acc_orig
    assert runtime.execute_dsa_ir is dsa_ir_orig
    assert runtime.dsa_push is push_orig
    assert runtime.execute_db_ir is db_ir_orig
    assert runtime.insert_rows is insert_orig
    assert runtime.execute_sim_ir is sim_ir_orig
    assert runtime.run_trials is trials_orig
    assert runtime.execute_opt_ir is opt_ir_orig
    assert runtime.solve_linear_program is solve_lp_orig
    assert runtime.execute_net_ir is net_ir_orig
    assert runtime.execute_nlp_ir is nlp_ir_orig
    assert runtime.execute_geo_ir is geo_ir_orig
    assert runtime.plot_table is plot_orig
    assert runtime.show_plot is show_orig


def test_basic_doomscript_execution():
    """Verify standard execution works cleanly with explicit runtime exports."""
    from doomscript.compiler.engine import execute
    code = """
set x to 10
set y to 20
set z to x + y
"""
    result = execute(code)
    assert result["z"] == 30


def test_security_notice_in_docstring():
    """Verify documentation clearly specifies that explicit runtime registry is not a security sandbox."""
    doc = runtime.get_runtime_exports.__doc__
    assert doc is not None
    assert "Security Notice" in doc
    assert "NOT an isolated security sandbox" in doc
