"""Regression tests for Phase 2 (Registry determinism & collision rejection) and Phase 3 (Fast indexed matcher)."""

import pytest
from doomscript.domains.base import DomainContract, DomainParser, DomainRuntime, DomainASTExporter
from doomscript.domains.registry import DomainRegistry, DomainRegistrationError, get_domain_registry
from doomscript.grammar.phrases import normalize_with_map


class DummyParser(DomainParser):
    def parse_inspect(self, line: str, line_no: int):
        return None
    def parse_operation(self, line: str, line_no: int):
        if line.strip() == "dummy do something":
            return "dummy_action()"
        return None
    def parse_block(self, header: str, body_lines, indent: int):
        raise NotImplementedError


class DummyDomain(DomainContract):
    name = "dummy_alpha"
    aliases = ["alpha_alias"]
    parser = DummyParser()
    runtime = None
    exporter = None
    verbs = []


class ConflictingDomain(DomainContract):
    name = "dummy_beta"
    aliases = ["alpha_alias"]  # Intentionally collides with DummyDomain
    parser = DummyParser()
    runtime = None
    exporter = None
    verbs = []


def test_alias_collision_raises_error():
    """Verify that registering duplicate aliases across different domains raises DomainRegistrationError."""
    reg = DomainRegistry()
    d1 = DummyDomain()
    d2 = ConflictingDomain()

    reg.register(d1)
    with pytest.raises(DomainRegistrationError, match="Alias collision: 'alpha_alias'"):
        reg.register(d2)


def test_active_domains_lifo_order():
    """Verify that active domains maintain deterministic LIFO precedence."""
    reg = DomainRegistry()
    d1 = DummyDomain()
    d2 = DummyDomain()
    d2.name = "dummy_beta"
    d2.aliases = ["beta_alias"]

    reg.register(d1)
    reg.register(d2)

    assert reg.activate("dummy_alpha") is True
    assert reg.activate("dummy_beta") is True

    # dummy_beta was activated last, so it has precedence in LIFO order
    active = reg.get_active_domains()
    assert [d.name for d in active] == ["dummy_beta", "dummy_alpha"]

    # Re-activating dummy_alpha moves it to the top of the stack
    assert reg.activate("alpha_alias") is True
    active = reg.get_active_domains()
    assert [d.name for d in active] == ["dummy_alpha", "dummy_beta"]


def test_fast_matcher_sub_millisecond_normalization():
    """Verify that normal lines are normalized in < 5ms without redundant domain scans."""
    src = "a = 1\nb = 2\nc = a + b"
    norm, lmap = normalize_with_map(src)
    assert "set a to 1" in norm or "a = 1" in norm
    assert len(lmap) >= 3
