"""Bytecode Virtual Machine, Assembler, and Pratt Parser for DoomScript."""

import re
from typing import List, Dict, Any, Optional, Union, Tuple, Callable


class Opcode:
    HALT = 0
    LOAD_CONST = 1
    LOAD_FAST = 2
    STORE_FAST = 3
    POP = 4
    ADD = 5
    SUB = 6
    MUL = 7
    DIV = 8
    COMPARE_EQ = 9
    COMPARE_LT = 10
    COMPARE_GT = 11
    JUMP = 12
    JUMP_IF_FALSE = 13
    CALL = 14
    RETURN = 15
    PRINT = 16


OPCODE_NAMES = {
    0: "HALT",
    1: "LOAD_CONST",
    2: "LOAD_FAST",
    3: "STORE_FAST",
    4: "POP",
    5: "ADD",
    6: "SUB",
    7: "MUL",
    8: "DIV",
    9: "COMPARE_EQ",
    10: "COMPARE_LT",
    11: "COMPARE_GT",
    12: "JUMP",
    13: "JUMP_IF_FALSE",
    14: "CALL",
    15: "RETURN",
    16: "PRINT",
}


class Instruction:
    def __init__(self, opcode: int, arg: Any = None, label: Optional[str] = None):
        self.opcode = int(opcode)
        self.arg = arg
        self.label = label

    def __repr__(self) -> str:
        op_name = OPCODE_NAMES.get(self.opcode, f"OP_{self.opcode}")
        return f"{op_name:<16} {str(self.arg) if self.arg is not None else ''}".strip()


class Frame:
    """Execution Call Frame."""

    def __init__(self, return_ip: int = 0, locals_dict: Optional[Dict[str, Any]] = None):
        self.return_ip = return_ip
        self.locals = locals_dict if locals_dict is not None else {}


class BytecodeVM:
    """Stack-based Virtual Machine."""

    def __init__(self):
        self.instructions: List[Instruction] = []
        self.constants: List[Any] = []
        self.stack: List[Any] = []
        self.frames: List[Frame] = [Frame(0, {})]
        self.globals: Dict[str, Any] = {}
        self.ip: int = 0
        self.output: List[str] = []
        self.halted: bool = False

    def load_program(self, instructions: List[Instruction], constants: Optional[List[Any]] = None):
        self.instructions = instructions
        self.constants = constants if constants is not None else []
        self.stack.clear()
        self.frames = [Frame(0, {})]
        self.ip = 0
        self.output.clear()
        self.halted = False

    def step(self) -> bool:
        if self.halted or self.ip >= len(self.instructions):
            self.halted = True
            return False

        inst = self.instructions[self.ip]
        self.ip += 1
        op = inst.opcode
        arg = inst.arg
        curr_frame = self.frames[-1]

        if op == Opcode.HALT:
            self.halted = True
            return False
        elif op == Opcode.LOAD_CONST:
            val = self.constants[arg] if isinstance(arg, int) and arg < len(self.constants) else arg
            self.stack.append(val)
        elif op == Opcode.LOAD_FAST:
            self.stack.append(curr_frame.locals.get(arg, 0))
        elif op == Opcode.STORE_FAST:
            if self.stack:
                curr_frame.locals[arg] = self.stack.pop()
        elif op == Opcode.POP:
            if self.stack:
                self.stack.pop()
        elif op == Opcode.ADD:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a + b)
        elif op == Opcode.SUB:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a - b)
        elif op == Opcode.MUL:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a * b)
        elif op == Opcode.DIV:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a / b if b != 0 else 0)
        elif op == Opcode.COMPARE_EQ:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a == b)
        elif op == Opcode.COMPARE_LT:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a < b)
        elif op == Opcode.COMPARE_GT:
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a > b)
        elif op == Opcode.JUMP:
            self.ip = int(arg)
        elif op == Opcode.JUMP_IF_FALSE:
            cond = self.stack.pop()
            if not cond:
                self.ip = int(arg)
        elif op == Opcode.CALL:
            # target ip is arg
            self.frames.append(Frame(return_ip=self.ip, locals_dict={}))
            self.ip = int(arg)
        elif op == Opcode.RETURN:
            ret_val = self.stack.pop() if self.stack else None
            if len(self.frames) > 1:
                old_frame = self.frames.pop()
                self.ip = old_frame.return_ip
                if ret_val is not None:
                    self.stack.append(ret_val)
            else:
                if ret_val is not None:
                    self.stack.append(ret_val)
                self.halted = True
                return False
        elif op == Opcode.PRINT:
            val = self.stack.pop() if self.stack else None
            self.output.append(str(val))
        return True

    def run(self, max_steps: int = 10000) -> Dict[str, Any]:
        steps = 0
        while steps < max_steps and self.step():
            steps += 1
        return {
            "steps": steps,
            "halted": self.halted,
            "output": self.output,
            "stack": list(self.stack),
            "locals": dict(self.frames[-1].locals),
        }


class Assembler:
    """Bytecode Assembler with 2-pass Label Resolution."""

    def __init__(self):
        self.instructions: List[Instruction] = []
        self.constants: List[Any] = []
        self.labels: Dict[str, int] = {}
        self.fixups: List[Tuple[int, str]] = []

    def emit(self, opcode: int, arg: Any = None):
        idx = len(self.instructions)
        if isinstance(arg, str) and opcode in (Opcode.JUMP, Opcode.JUMP_IF_FALSE, Opcode.CALL):
            # Target is a label
            self.fixups.append((idx, arg))
            self.instructions.append(Instruction(opcode, 0))
        else:
            self.instructions.append(Instruction(opcode, arg))

    def label(self, name: str):
        self.labels[name] = len(self.instructions)

    def add_constant(self, value: Any) -> int:
        if value in self.constants:
            return self.constants.index(value)
        self.constants.append(value)
        return len(self.constants) - 1

    def assemble(self) -> Tuple[List[Instruction], List[Any]]:
        # Second pass: resolve label fixups
        for inst_idx, label_name in self.fixups:
            if label_name in self.labels:
                self.instructions[inst_idx].arg = self.labels[label_name]
            else:
                raise ValueError(f"Undefined label in assembly: '{label_name}'")
        return list(self.instructions), list(self.constants)

    @staticmethod
    def disassemble(instructions: List[Instruction], constants: Optional[List[Any]] = None) -> str:
        lines = []
        for i, inst in enumerate(instructions):
            op_name = OPCODE_NAMES.get(inst.opcode, f"OP_{inst.opcode}")
            arg_str = ""
            if inst.arg is not None:
                if inst.opcode == Opcode.LOAD_CONST and constants and isinstance(inst.arg, int) and inst.arg < len(constants):
                    arg_str = f"{inst.arg} ({repr(constants[inst.arg])})"
                else:
                    arg_str = str(inst.arg)
            lines.append(f"{i:04d}: {op_name:<16} {arg_str}".strip())
        return "\n".join(lines)


class LexerGenerator:
    """Configurable Regex Lexer / Scanner Generator."""

    def __init__(self, rules: List[Tuple[str, str]]):
        self.rules = [(name, re.compile(pat)) for name, pat in rules]

    def tokenize(self, text: str) -> List[Dict[str, Any]]:
        tokens = []
        pos = 0
        line = 1
        col = 1
        length = len(text)

        while pos < length:
            # Skip whitespace
            if text[pos].isspace():
                if text[pos] == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
                pos += 1
                continue

            matched = False
            for token_type, regex in self.rules:
                m = regex.match(text, pos)
                if m:
                    val = m.group(0)
                    tokens.append({
                        "type": token_type,
                        "value": val,
                        "line": line,
                        "col": col,
                    })
                    advance = len(val)
                    pos += advance
                    col += advance
                    matched = True
                    break

            if not matched:
                raise SyntaxError(f"Unexpected character at {line}:{col} -> '{text[pos]}'")
        return tokens


class PrattParser:
    """Top-Down Operator Precedence (Pratt) Expression Parser."""

    def __init__(self):
        # Maps token -> (binding_power, handler)
        self.infix_prec: Dict[str, int] = {
            "+": 10,
            "-": 10,
            "*": 20,
            "/": 20,
            "^": 30,
        }

    def parse(self, tokens: List[str]) -> Any:
        idx = [0]

        def get_tok() -> Optional[str]:
            return tokens[idx[0]] if idx[0] < len(tokens) else None

        def next_tok() -> Optional[str]:
            tok = get_tok()
            idx[0] += 1
            return tok

        def parse_expr(rbp: int = 0) -> Any:
            tok = next_tok()
            if tok is None:
                raise SyntaxError("Unexpected end of expression")

            # Prefix parse
            if tok.isdigit():
                left = int(tok)
            elif tok == "(":
                left = parse_expr(0)
                closing = next_tok()
                if closing != ")":
                    raise SyntaxError(f"Expected ')' but found '{closing}'")
            elif tok == "-":
                operand = parse_expr(25)
                left = ["neg", operand]
            else:
                left = tok

            # Infix loop
            while True:
                cur = get_tok()
                if cur is None or cur == ")":
                    break
                prec = self.infix_prec.get(cur, 0)
                if rbp >= prec:
                    break

                op = next_tok()
                # Right associative for power ^
                next_rbp = prec - 1 if op == "^" else prec
                right = parse_expr(next_rbp)
                left = [op, left, right]

            return left

        return parse_expr(0)


def compiler_run_bytecode(instructions: List[Instruction], constants: Optional[List[Any]] = None) -> Dict[str, Any]:
    vm = BytecodeVM()
    vm.load_program(instructions, constants)
    return vm.run()


def compiler_assemble_string(assembly_text: str) -> Dict[str, Any]:
    asm = Assembler()
    lines = [l.strip() for l in str(assembly_text).strip().splitlines() if l.strip() and not l.strip().startswith("#")]
    for line in lines:
        if line.endswith(":"):
            asm.label(line[:-1].strip())
            continue

        # Clean line of possible normalizer aliases
        cleaned = line
        if cleaned.startswith("_var_"):
            cleaned = cleaned[5:]

        # Check for OPCODE(arg) or OPCODE arg
        m = re.match(r"^([A-Za-z_]\w*)(?:\((.*?)\)|\s+(.*))?$", cleaned)
        if m:
            op_str = m.group(1).upper()
            arg = m.group(2) if m.group(2) is not None else m.group(3)
            if arg:
                arg = arg.strip()
        else:
            parts = cleaned.split(None, 1)
            op_str = parts[0].upper()
            arg = parts[1].strip() if len(parts) > 1 else None

        op_code = getattr(Opcode, op_str, None)
        if op_code is None:
            raise ValueError(f"Unknown opcode '{op_str}' in line: '{line}'")

        if arg is not None and arg != "":
            if arg.isdigit() or (arg.startswith("-") and arg[1:].isdigit()):
                arg = int(arg)
            elif (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                arg = asm.add_constant(arg[1:-1])
        else:
            arg = None

        asm.emit(op_code, arg)

    insts, consts = asm.assemble()
    return {"instructions": insts, "constants": consts}


def compiler_parse_pratt(expression_str: str) -> Any:
    tokens = [t for t in re.findall(r"\d+|[+*/^()-]|[a-zA-Z_]\w*", expression_str) if t.strip()]
    parser = PrattParser()
    return parser.parse(tokens)

