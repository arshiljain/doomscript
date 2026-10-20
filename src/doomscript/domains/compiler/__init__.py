"""Compiler, Bytecode VM, Assembler & Pratt Parser Domain Pack for DoomScript.

Enables native spoken-English bytecode execution, instruction assembly,
lexical scanning, and Pratt expression parsing via 'use compiler'.
"""

import re
from typing import List, Optional, Dict, Any
from doomscript.domains.base import (
    DomainContract,
    DomainParser,
    DomainRuntime,
    DomainASTExporter,
    DomainIR,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.compiler.runtime import (
    Opcode,
    Instruction,
    BytecodeVM,
    Assembler,
    LexerGenerator,
    PrattParser,
    compiler_run_bytecode,
    compiler_assemble_string,
    LALR1Parser,
    SSAFormBuilder,
    ChaitinRegisterAllocator,
    compiler_lalr1_parse,
    compiler_build_ssa,
    compiler_allocate_registers,
)
from doomscript.domains.compiler.parser import CompilerDomainParser
from doomscript.domains.compiler.exporter import CompilerASTExporter


class CompilerRuntime(DomainRuntime):
    """Runtime coordinator for compiler routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


def compiler_parse_pratt(expression_str: str) -> Any:
    tokens = [t for t in re.findall(r"\d+|[+*/^()-]|[a-zA-Z_]\w*", expression_str) if t.strip()]
    parser = PrattParser()
    return parser.parse(tokens)


class CompilerDomain(DomainContract):
    """Domain contract for Compiler & Bytecode VM."""

    name = "compiler"
    aliases = ["bytecode", "vm", "assembler"]
    description = "Bytecode Virtual Machine, assembler, and Pratt expression parser"
    parser = CompilerDomainParser()
    runtime = CompilerRuntime()
    exporter = CompilerASTExporter()
    capabilities = ["bytecode_vm", "assembler", "pratt_parser", "lexer"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="assemble bytecode from text {text:expr} into {target:ident}",
            description="Assembles mnemonic assembly into bytecode instructions and constants",
        ),
        VerbSpec(
            pattern="execute bytecode program {prog:expr} into {target:ident}",
            description="Executes bytecode program on stack VM",
        ),
        VerbSpec(
            pattern="parse pratt expression {expr:expr} into {target:ident}",
            description="Parses arithmetic expression using Pratt parser",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("assemble bytecode from text ")
            or s.startswith("execute bytecode program ")
            or s.startswith("parse pratt expression ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


COMPILER_DOMAIN = CompilerDomain()
get_domain_registry().register(COMPILER_DOMAIN)

__all__ = [
    "CompilerDomain",
    "COMPILER_DOMAIN",
    "CompilerRuntime",
    "Opcode",
    "Instruction",
    "BytecodeVM",
    "Assembler",
    "LexerGenerator",
    "PrattParser",
    "compiler_run_bytecode",
    "compiler_assemble_string",
    "compiler_parse_pratt",
    "LALR1Parser",
    "SSAFormBuilder",
    "ChaitinRegisterAllocator",
    "compiler_lalr1_parse",
    "compiler_build_ssa",
    "compiler_allocate_registers",
]
