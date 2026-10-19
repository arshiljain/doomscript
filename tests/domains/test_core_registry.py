"""Unit tests for the Core Domain Extension Architecture and Registry."""

import pytest
from doomscript.domains.base import (
    DomainContract,
    DomainParser,
    DomainIR,
    DomainRuntime,
    DomainASTExporter,
)
from doomscript.domains.registry import DomainRegistry, get_domain_registry


class MockIR(DomainIR):
    def __init__(self, value: str):
        self.value = value

    def validate(self):
        return []


class MockParser(DomainParser):
    def parse_inspect(self, line: str, line_no: int):
        if line.startswith("inspect mock"):
            return MockIR(line)
        return None

    def parse_operation(self, line: str, line_no: int):
        return None

    def parse_block(self, header: str, body_lines, indent: int):
        return MockIR(header), "mock_target"


class MockRuntime(DomainRuntime):
    def execute_ir(self, ir, scope):
        return f"executed:{ir.value}"


class MockExporter(DomainASTExporter):
    def to_ast(self, ir, var_name, scope=None):
        return set(), []


class MockDomain(DomainContract):
    name = "mock"
    aliases = ["mock_domain", "fake"]
    parser = MockParser()
    runtime = MockRuntime()
    exporter = MockExporter()

    def can_handle_line(self, line: str) -> bool:
        return line.strip().startswith("inspect mock")

    def can_handle_block(self, header: str) -> bool:
        return header.strip().startswith("mock ")


def test_registry_registration_and_activation():
    reg = DomainRegistry()
    mock_domain = MockDomain()
    reg.register(mock_domain)

    # Domain exists but not active initially in a fresh session
    assert reg.has_domain("mock")
    assert reg.has_domain("mock_domain")
    assert not reg.is_active("mock")

    # Activation via primary name or alias
    reg.activate("mock")
    assert reg.is_active("mock")
    assert reg.is_active("mock_domain")

    # Deactivation / reset
    reg.reset_active()
    assert not reg.is_active("mock")


def test_registry_auto_detection():
    reg = DomainRegistry()
    reg.register(MockDomain())

    # Line handler dispatch
    matched = reg.find_domain_for_line("inspect mock dataset")
    assert matched is not None
    assert matched.name == "mock"

    # Block handler dispatch
    matched_block = reg.find_domain_for_block("mock block header:")
    assert matched_block is not None
    assert matched_block.name == "mock"


def test_compiler_use_domain_statement():
    from doomscript.compiler.engine import execute
    reg = get_domain_registry()
    reg.register(MockDomain())
    source = """use mock
say "Domain activated"
"""
    # Verifies that `use <domain>` compiles and executes without syntax error
    env = execute(source)
    assert env is not None
