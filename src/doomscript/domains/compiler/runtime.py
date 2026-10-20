"""Bytecode Virtual Machine, Assembler, and Pratt Parser for DoomScript."""

import re
from typing import List, Dict, Any, Optional, Union, Tuple, Callable
from doomscript.runtime import Record


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


class LALR1Parser:
    """Deterministic LALR(1) parser generator and runtime parser."""

    def __init__(self, grammar: Dict[str, Any]):
        self.start_sym = grammar.get("start", "S")
        self.terminals = set(grammar.get("terminals", [])) | {"$"}
        self.nonterminals = set(grammar.get("nonterminals", []))
        self.rules: List[Tuple[str, List[str]]] = [
            (r[0], list(r[1])) for r in grammar.get("rules", [])
        ]
        # Augmented start rule: S' -> S
        self.augmented_start = f"{self.start_sym}'"
        self.rules.insert(0, (self.augmented_start, [self.start_sym]))
        self.nonterminals.add(self.augmented_start)

        self.first_sets: Dict[str, set] = {}
        self._compute_first_sets()
        self.states: List[List[Tuple[str, Tuple[str, ...], int, frozenset]]] = []
        self.action_table: Dict[Tuple[int, str], Tuple[str, Any]] = {}
        self.goto_table: Dict[Tuple[int, str], int] = {}
        self._build_tables()

    def _compute_first_sets(self):
        for t in self.terminals:
            self.first_sets[t] = {t}
        for nt in self.nonterminals:
            self.first_sets[nt] = set()

        changed = True
        while changed:
            changed = False
            for lhs, rhs in self.rules:
                if not rhs:
                    if "" not in self.first_sets[lhs]:
                        self.first_sets[lhs].add("")
                        changed = True
                    continue
                can_be_empty = True
                for sym in rhs:
                    sym_first = self.first_sets.get(sym, {sym})
                    before = len(self.first_sets[lhs])
                    self.first_sets[lhs] |= (sym_first - {""})
                    if len(self.first_sets[lhs]) > before:
                        changed = True
                    if "" not in sym_first:
                        can_be_empty = False
                        break
                if can_be_empty and "" not in self.first_sets[lhs]:
                    self.first_sets[lhs].add("")
                    changed = True

    def _first_of_sequence(self, symbols: List[str]) -> set:
        res = set()
        can_be_empty = True
        for sym in symbols:
            s_first = self.first_sets.get(sym, {sym})
            res |= (s_first - {""})
            if "" not in s_first:
                can_be_empty = False
                break
        if can_be_empty:
            res.add("")
        return res

    def _closure(self, items: set) -> set:
        """Computes LR(1) closure of a set of items: (lhs, rhs_tuple, dot, lookahead_frozenset)."""
        closure_map: Dict[Tuple[str, Tuple[str, ...], int], set] = {}
        for lhs, rhs, dot, la in items:
            key = (lhs, rhs, dot)
            closure_map.setdefault(key, set()).update(la)

        changed = True
        while changed:
            changed = False
            curr_keys = list(closure_map.keys())
            for lhs, rhs, dot in curr_keys:
                if dot < len(rhs):
                    b = rhs[dot]
                    if b in self.nonterminals:
                        beta = list(rhs[dot + 1:])
                        current_las = list(closure_map[(lhs, rhs, dot)])
                        for la in current_las:
                            seq = beta + [la]
                            b_las = self._first_of_sequence(seq) - {""}
                            for prod_lhs, prod_rhs in self.rules:
                                if prod_lhs == b:
                                    rule_key = (prod_lhs, tuple(prod_rhs), 0)
                                    target_set = closure_map.setdefault(rule_key, set())
                                    before_len = len(target_set)
                                    target_set.update(b_las)
                                    if len(target_set) > before_len:
                                        changed = True

        return {(k[0], k[1], k[2], frozenset(v)) for k, v in closure_map.items()}

    def _goto(self, items: set, symbol: str) -> set:
        moved = set()
        for lhs, rhs, dot, la in items:
            if dot < len(rhs) and rhs[dot] == symbol:
                moved.add((lhs, rhs, dot + 1, la))
        return self._closure(moved)

    def _build_tables(self):
        init_item = (self.augmented_start, (self.start_sym,), 0, frozenset(["$"]))
        init_state = self._closure({init_item})

        lr1_states = [init_state]
        state_map = {frozenset(init_state): 0}

        transitions: Dict[Tuple[int, str], int] = {}
        all_symbols = sorted(list(self.terminals | self.nonterminals))

        queue = [0]
        while queue:
            s_idx = queue.pop(0)
            cur_items = lr1_states[s_idx]

            for sym in all_symbols:
                if sym == "$":
                    continue
                next_items = self._goto(cur_items, sym)
                if not next_items:
                    continue
                frozen = frozenset(next_items)
                if frozen not in state_map:
                    new_idx = len(lr1_states)
                    state_map[frozen] = new_idx
                    lr1_states.append(next_items)
                    queue.append(new_idx)
                transitions[(s_idx, sym)] = state_map[frozen]

        # Merge LR(1) states into LALR(1) states based on LR(0) cores
        core_map: Dict[frozenset, List[int]] = {}
        for idx, state in enumerate(lr1_states):
            core = frozenset((lhs, rhs, dot) for lhs, rhs, dot, _ in state)
            core_map.setdefault(core, []).append(idx)

        state_relabel: Dict[int, int] = {}
        merged_states: List[set] = []
        for core, old_indices in core_map.items():
            new_idx = len(merged_states)
            merged_item_map: Dict[Tuple[str, Tuple[str, ...], int], set] = {}
            for old_idx in old_indices:
                state_relabel[old_idx] = new_idx
                for lhs, rhs, dot, la in lr1_states[old_idx]:
                    merged_item_map.setdefault((lhs, rhs, dot), set()).update(la)
            merged_state = {
                (k[0], k[1], k[2], frozenset(v)) for k, v in merged_item_map.items()
            }
            merged_states.append(merged_state)

        self.states = [list(s) for s in merged_states]

        # Populate action and goto tables
        for old_from, sym in transitions:
            old_to = transitions[(old_from, sym)]
            new_from = state_relabel[old_from]
            new_to = state_relabel[old_to]
            if sym in self.terminals:
                self.action_table[(new_from, sym)] = ("shift", new_to)
            elif sym in self.nonterminals:
                self.goto_table[(new_from, sym)] = new_to

        for s_idx, state in enumerate(merged_states):
            for lhs, rhs, dot, lookaheads in state:
                if dot == len(rhs):
                    if lhs == self.augmented_start:
                        self.action_table[(s_idx, "$")] = ("accept", 0)
                    else:
                        rule_idx = -1
                        for r_i, (r_lhs, r_rhs) in enumerate(self.rules):
                            if r_lhs == lhs and tuple(r_rhs) == rhs:
                                rule_idx = r_i
                                break
                        for la in lookaheads:
                            existing = self.action_table.get((s_idx, la))
                            if existing is None:
                                self.action_table[(s_idx, la)] = ("reduce", rule_idx)
                            elif existing[0] == "shift":
                                pass  # Standard shift preference

    def parse(self, tokens: List[str]) -> Dict[str, Any]:
        """Parses a sequence of terminal tokens and returns parse tree."""
        in_tokens = list(tokens) + ["$"]
        state_stack = [0]
        sym_stack: List[Any] = []
        cursor = 0
        steps = []

        while True:
            cur_state = state_stack[-1]
            tok = in_tokens[cursor] if cursor < len(in_tokens) else "$"
            action = self.action_table.get((cur_state, tok))

            if action is None:
                return {
                    "success": False,
                    "error": f"Syntax error at token '{tok}' in state {cur_state}",
                    "steps": steps,
                    "tree": None,
                }

            act_type, act_val = action
            steps.append({
                "state": cur_state,
                "token": tok,
                "action": act_type,
                "value": act_val,
            })

            if act_type == "shift":
                state_stack.append(act_val)
                sym_stack.append({"type": "terminal", "value": tok})
                cursor += 1
            elif act_type == "reduce":
                rule_lhs, rule_rhs = self.rules[act_val]
                rhs_len = len(rule_rhs)
                popped_children = []
                for _ in range(rhs_len):
                    state_stack.pop()
                    popped_children.insert(0, sym_stack.pop())
                node = {
                    "type": "nonterminal",
                    "symbol": rule_lhs,
                    "rule_idx": act_val,
                    "children": popped_children,
                }
                sym_stack.append(node)
                top_state = state_stack[-1]
                next_state = self.goto_table.get((top_state, rule_lhs))
                if next_state is None:
                    return {
                        "success": False,
                        "error": f"Goto missing for nonterminal '{rule_lhs}' in state {top_state}",
                        "steps": steps,
                        "tree": None,
                    }
                state_stack.append(next_state)
            elif act_type == "accept":
                return {
                    "success": True,
                    "steps": steps,
                    "tree": sym_stack[0] if sym_stack else None,
                }


class SSAFormBuilder:
    """Transforms Control Flow Graph (CFG) basic blocks into Static Single Assignment (SSA) form."""

    def __init__(self):
        pass

    def build_ssa(self, cfg: Dict[str, Any]) -> Dict[str, Any]:
        """Converts basic blocks CFG to SSA form."""
        entry = cfg.get("entry", "b0")
        blocks = {k: dict(v) for k, v in cfg.get("blocks", {}).items()}

        # Build predecessor map
        preds: Dict[str, List[str]] = {b: [] for b in blocks}
        for b, data in blocks.items():
            for succ in data.get("succs", []):
                if succ in preds:
                    preds[succ].append(b)

        # 1. Compute Dominators Dom(n)
        all_blocks = set(blocks.keys())
        dom: Dict[str, set] = {}
        for b in blocks:
            dom[b] = {b} if b == entry else set(all_blocks)

        changed = True
        while changed:
            changed = False
            for b in blocks:
                if b == entry:
                    continue
                p_doms = [dom[p] for p in preds[b] if p in dom]
                new_dom = {b} | (set.intersection(*p_doms) if p_doms else set())
                if new_dom != dom[b]:
                    dom[b] = new_dom
                    changed = True

        # 2. Compute Immediate Dominator idom(n)
        idom: Dict[str, Optional[str]] = {b: None for b in blocks}
        for b in blocks:
            if b == entry:
                continue
            strict_doms = dom[b] - {b}
            for d in strict_doms:
                # d is idom if no other strict dominator in strict_doms is strictly dominated by d
                is_idom = True
                for other in strict_doms:
                    if other != d and other in dom[d]:
                        is_idom = False
                        break
                if is_idom:
                    idom[b] = d
                    break

        # 3. Compute Dominance Frontiers DF(n)
        df: Dict[str, set] = {b: set() for b in blocks}
        for b in blocks:
            if len(preds[b]) >= 2:
                for p in preds[b]:
                    runner = p
                    while runner != idom[b] and runner is not None:
                        df[runner].add(b)
                        runner = idom[runner]

        # 4. Insert Phi Nodes
        # Collect all variables and their assignment sites
        def_sites: Dict[str, set] = {}
        for b, data in blocks.items():
            for inst in data.get("instructions", []):
                target = inst.get("target")
                if target:
                    def_sites.setdefault(target, set()).add(b)

        phi_placed: Dict[str, set] = {v: set() for v in def_sites}
        phi_nodes: Dict[str, List[Dict[str, Any]]] = {b: [] for b in blocks}

        for var, sites in def_sites.items():
            work = list(sites)
            while work:
                site = work.pop(0)
                for df_block in df.get(site, set()):
                    if df_block not in phi_placed[var]:
                        phi_placed[var].add(df_block)
                        phi_nodes[df_block].append({
                            "op": "phi",
                            "var": var,
                            "target": var,
                            "sources": {p: var for p in preds[df_block]},
                        })
                        if df_block not in sites:
                            work.append(df_block)

        # 5. Variable Renaming
        var_stacks: Dict[str, List[str]] = {v: [f"{v}_0"] for v in def_sites}
        var_counters: Dict[str, int] = {v: 0 for v in def_sites}
        new_blocks: Dict[str, Any] = {}

        # Dom tree children
        dom_children: Dict[str, List[str]] = {b: [] for b in blocks}
        for b, d in idom.items():
            if d is not None:
                dom_children[d].append(b)

        def rename(block_id: str):
            pushed: Dict[str, int] = {v: 0 for v in def_sites}
            renamed_insts = []

            # Process phi nodes in this block
            for phi in phi_nodes.get(block_id, []):
                var = phi["var"]
                var_counters[var] += 1
                new_name = f"{var}_{var_counters[var]}"
                var_stacks[var].append(new_name)
                pushed[var] += 1
                phi["target"] = new_name
                renamed_insts.append(phi)

            # Process ordinary instructions
            for inst in blocks[block_id].get("instructions", []):
                new_inst = dict(inst)
                args = new_inst.get("args", [])
                new_args = []
                for a in args:
                    if a in var_stacks and var_stacks[a]:
                        new_args.append(var_stacks[a][-1])
                    else:
                        new_args.append(a)
                new_inst["args"] = new_args

                target = new_inst.get("target")
                if target in var_stacks:
                    var_counters[target] += 1
                    new_target = f"{target}_{var_counters[target]}"
                    var_stacks[target].append(new_target)
                    pushed[target] += 1
                    new_inst["target"] = new_target

                renamed_insts.append(new_inst)

            # Update phi nodes in successors
            for succ in blocks[block_id].get("succs", []):
                for phi in phi_nodes.get(succ, []):
                    var = phi["var"]
                    if var in var_stacks and var_stacks[var]:
                        phi["sources"][block_id] = var_stacks[var][-1]

            new_blocks[block_id] = {
                "instructions": renamed_insts,
                "succs": list(blocks[block_id].get("succs", [])),
                "preds": list(preds[block_id]),
            }

            # Recurse on dom children
            for child in dom_children.get(block_id, []):
                rename(child)

            # Pop stacks
            for var, count in pushed.items():
                for _ in range(count):
                    var_stacks[var].pop()

        rename(entry)

        return {
            "entry": entry,
            "blocks": new_blocks,
            "dominance_frontiers": {k: sorted(list(v)) for k, v in df.items()},
            "idom": idom,
        }

    def deconstruct_ssa(self, ssa_cfg: Dict[str, Any]) -> Dict[str, Any]:
        """Deconstructs SSA form back to standard form with parallel copies."""
        blocks = {k: dict(v) for k, v in ssa_cfg.get("blocks", {}).items()}
        for b_id, b_data in blocks.items():
            non_phi_insts = []
            for inst in b_data.get("instructions", []):
                if inst.get("op") == "phi":
                    target = inst.get("target")
                    for pred, source in inst.get("sources", {}).items():
                        if pred in blocks:
                            copy_inst = {
                                "op": "copy",
                                "target": target,
                                "args": [source],
                            }
                            # Insert before branch or at end of pred
                            pred_insts = blocks[pred].setdefault("instructions", [])
                            pred_insts.append(copy_inst)
                else:
                    non_phi_insts.append(inst)
            b_data["instructions"] = non_phi_insts

        return {"entry": ssa_cfg.get("entry", "b0"), "blocks": blocks}


class ChaitinRegisterAllocator:
    """Interference graph register allocator using Kempe's degree-K coloring heuristic."""

    def __init__(self, k_registers: int = 4):
        self.k = max(1, int(k_registers))

    def allocate(self, instructions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Allocates registers for a sequence of instructions.
        Each instruction has format:
        {"id": int, "def": ["x"], "use": ["y", "z"], "op": "add"}
        """
        # 1. Compute liveness intervals
        all_vars = set()
        first_def: Dict[str, int] = {}
        last_use: Dict[str, int] = {}

        for idx, inst in enumerate(instructions):
            defs = inst.get("def", [])
            uses = inst.get("use", [])
            for d in defs:
                all_vars.add(d)
                if d not in first_def:
                    first_def[d] = idx
            for u in uses:
                all_vars.add(u)
                last_use[u] = max(last_use.get(u, idx), idx)

        intervals: Dict[str, Tuple[int, int]] = {}
        for v in all_vars:
            start = first_def.get(v, 0)
            end = max(last_use.get(v, start), start)
            intervals[v] = (start, end)

        # 2. Build Interference Graph
        adj: Dict[str, set] = {v: set() for v in all_vars}
        var_list = sorted(list(all_vars))
        for i in range(len(var_list)):
            v1 = var_list[i]
            s1, e1 = intervals[v1]
            for j in range(i + 1, len(var_list)):
                v2 = var_list[j]
                s2, e2 = intervals[v2]
                # Overlap test: not (e1 < s2 or e2 < s1)
                if not (e1 < s2 or e2 < s1):
                    adj[v1].add(v2)
                    adj[v2].add(v1)

        # 3. Kempe degree-K heuristic simplification
        current_graph = {v: set(neighbors) for v, neighbors in adj.items()}
        stack: List[str] = []
        spilled_candidates: set = set()

        while current_graph:
            # Find candidate with degree < K
            low_deg_cand = None
            for v, neighbors in current_graph.items():
                if len(neighbors) < self.k:
                    low_deg_cand = v
                    break

            if low_deg_cand is not None:
                stack.append(low_deg_cand)
                # Remove from graph
                for n in current_graph[low_deg_cand]:
                    current_graph[n].discard(low_deg_cand)
                del current_graph[low_deg_cand]
            else:
                # Potential spill: select node with max degree (or min cost/deg)
                spill_cand = max(current_graph.keys(), key=lambda node: len(current_graph[node]))
                spilled_candidates.add(spill_cand)
                stack.append(spill_cand)
                for n in current_graph[spill_cand]:
                    current_graph[n].discard(spill_cand)
                del current_graph[spill_cand]

        # 4. Color Assignment (Select phase)
        allocations: Dict[str, Dict[str, Any]] = {}
        next_spill_slot = 0

        while stack:
            v = stack.pop()
            neighbor_colors = set()
            for n in adj[v]:
                if n in allocations and allocations[n].get("type") == "register":
                    neighbor_colors.add(allocations[n]["reg"])

            assigned_color = None
            for c in range(self.k):
                if c not in neighbor_colors:
                    assigned_color = c
                    break

            if assigned_color is not None:
                allocations[v] = {"type": "register", "reg": assigned_color}
            else:
                allocations[v] = {"type": "spill", "slot": next_spill_slot}
                next_spill_slot += 1

        return {
            "k_registers": self.k,
            "allocations": allocations,
            "spill_count": next_spill_slot,
            "intervals": intervals,
            "interference_graph": {v: sorted(list(neighbors)) for v, neighbors in adj.items()},
        }


def compiler_lalr1_parse(grammar: Dict[str, Any], tokens: List[str]) -> Dict[str, Any]:
    """Generates LALR(1) tables and parses token sequence."""
    parser = LALR1Parser(grammar)
    return parser.parse(tokens)


def compiler_build_ssa(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Transforms a basic block CFG into SSA form with phi nodes and renamed variables."""
    builder = SSAFormBuilder()
    return builder.build_ssa(cfg)


def compiler_allocate_registers(instructions: List[Dict[str, Any]], k_registers: int = 4) -> Dict[str, Any]:
    """Allocates hardware registers via Chaitin's Kempe graph-coloring heuristic."""
    allocator = ChaitinRegisterAllocator(k_registers)
    return allocator.allocate(instructions)


# ==============================================================================
# DEAD CODE ELIMINATION & CONSTANT FOLDING OPTIMIZATION PASS
# ==============================================================================

class OptimizationPassDCEAndFold:
    """Multi-pass optimizer performing constant propagation, folding, and dead code elimination."""

    @classmethod
    def optimize(cls, tac_instructions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Iteratively optimizes Three-Address Code instructions to fixed point."""
        instructions = [dict(inst) for inst in tac_instructions]
        total_folded = 0
        total_eliminated = 0
        changed = True

        while changed:
            changed = False
            # Pass 1: Constant Propagation & Algebraic Folding
            const_map: Dict[str, Union[int, float]] = {}
            new_instructions = []

            for inst in instructions:
                op = inst.get("op", "").lower()
                target = inst.get("target")
                arg1 = inst.get("arg1")
                arg2 = inst.get("arg2")

                # Substitute known constants
                val1 = const_map.get(arg1, arg1) if isinstance(arg1, str) else arg1
                val2 = const_map.get(arg2, arg2) if isinstance(arg2, str) else arg2

                # Fold binary constants
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    res_val = None
                    if op in ("+", "add"):
                        res_val = val1 + val2
                    elif op in ("-", "sub"):
                        res_val = val1 - val2
                    elif op in ("*", "mul"):
                        res_val = val1 * val2
                    elif op in ("/", "div"):
                        res_val = (val1 / val2) if val2 != 0 else None

                    if res_val is not None:
                        total_folded += 1
                        changed = True
                        if target:
                            const_map[target] = res_val
                        new_instructions.append({"op": "const", "target": target, "value": res_val})
                        continue

                # Algebraic identities
                if op in ("*", "mul") and (val1 == 0 or val2 == 0):
                    total_folded += 1
                    changed = True
                    if target:
                        const_map[target] = 0
                    new_instructions.append({"op": "const", "target": target, "value": 0})
                    continue

                if op in ("+", "add") and val2 == 0:
                    total_folded += 1
                    changed = True
                    new_instructions.append({"op": "copy", "target": target, "arg1": val1})
                    continue

                if op == "const" and target and "value" in inst:
                    const_map[target] = inst["value"]

                inst_copy = dict(inst)
                if val1 != arg1:
                    inst_copy["arg1"] = val1
                if val2 != arg2:
                    inst_copy["arg2"] = val2
                new_instructions.append(inst_copy)

            # Pass 2: Dead Code Elimination
            # Find all used variables
            used_vars: Set[str] = set()
            for inst in new_instructions:
                if inst.get("op") == "return":
                    val = inst.get("value")
                    if isinstance(val, str):
                        used_vars.add(val)
                for key in ("arg1", "arg2"):
                    arg = inst.get(key)
                    if isinstance(arg, str):
                        used_vars.add(arg)

            pruned = []
            for inst in new_instructions:
                t = inst.get("target")
                op = inst.get("op")
                # If instruction defines a variable that is never used and has no side effects, eliminate it
                if t and t not in used_vars and op not in ("call", "print", "return"):
                    total_eliminated += 1
                    changed = True
                else:
                    pruned.append(inst)

            instructions = pruned

        return {
            "optimized_instructions": instructions,
            "constants_folded": total_folded,
            "dead_instructions_eliminated": total_eliminated,
            "instruction_count": len(instructions),
        }


# ==============================================================================
# DOMINATOR TREE & LOOP IDENTIFIER
# ==============================================================================

class DominatorTreeBuilder:
    """Computes immediate dominators, dominance frontiers, and natural loops in a CFG."""

    @classmethod
    def compute(cls, entry: str, nodes: List[str], edges: List[Tuple[str, str]]) -> Dict[str, Any]:
        node_set = set(nodes)
        preds: Dict[str, Set[str]] = {n: set() for n in node_set}
        succs: Dict[str, Set[str]] = {n: set() for n in node_set}

        for u, v in edges:
            if u in node_set and v in node_set:
                succs[u].add(v)
                preds[v].add(u)

        # Iterative Dominator algorithm
        # Dom(entry) = {entry}
        # Dom(n) = {n} union (intersection of Dom(p) for p in preds(n))
        dom: Dict[str, Set[str]] = {}
        for n in node_set:
            dom[n] = set(node_set) if n != entry else {entry}

        changed = True
        while changed:
            changed = False
            for n in node_set:
                if n == entry:
                    continue
                p_doms = [dom[p] for p in preds[n] if p in dom]
                if p_doms:
                    common = set.intersection(*p_doms)
                else:
                    common = set()
                new_dom = {n} | common
                if new_dom != dom[n]:
                    dom[n] = new_dom
                    changed = True

        # Compute immediate dominators (idom)
        # idom(n) is the unique d in Dom(n) - {n} that is dominated by all other nodes in Dom(n) - {n}
        idom: Dict[str, Optional[str]] = {entry: None}
        for n in node_set:
            if n == entry:
                continue
            strict_doms = dom[n] - {n}
            # The idom is the strict dominator whose dom set has size len(strict_doms)
            idom_node = None
            max_size = -1
            for d in strict_doms:
                if len(dom[d]) > max_size:
                    max_size = len(dom[d])
                    idom_node = d
            idom[n] = idom_node

        # Compute Dominance Frontiers (DF)
        df: Dict[str, Set[str]] = {n: set() for n in node_set}
        for u in node_set:
            if len(preds[u]) >= 2:
                for p in preds[u]:
                    runner = p
                    while runner != idom.get(u) and runner is not None:
                        df[runner].add(u)
                        runner = idom.get(runner)

        # Detect natural loops: back edges m -> h where h dominates m
        loops: List[Dict[str, Any]] = []
        for u, v in edges:
            if v in dom.get(u, set()):
                # v is loop header, u is loop latch
                # Loop body = nodes that can reach u without going through v
                loop_body = {v, u}
                stack = [u]
                while stack:
                    curr = stack.pop()
                    for p in preds[curr]:
                        if p not in loop_body:
                            loop_body.add(p)
                            stack.append(p)
                loops.append({
                    "header": v,
                    "latch": u,
                    "body": sorted(list(loop_body)),
                })

        return {
            "entry": entry,
            "idom": idom,
            "dominance_frontiers": {k: sorted(list(v)) for k, v in df.items()},
            "natural_loops": loops,
        }


def compiler_optimize_dce_and_fold(instructions: List[Dict[str, Any]]) -> Any:
    """Optimizes instruction stream with constant folding and dead code elimination."""
    return Record(OptimizationPassDCEAndFold.optimize(instructions))


def compiler_build_dominator_tree(entry: str, nodes: List[str], edges: List[Tuple[str, str]]) -> Any:
    """Computes immediate dominators, dominance frontiers, and natural loops in CFG."""
    return Record(DominatorTreeBuilder.compute(entry, nodes, edges))


class LL1GrammarTableGenerator:
    """Computes FIRST and FOLLOW sets, conflict detection, and LL(1) predictive parsing tables."""

    EPSILON = "ε"

    @classmethod
    def compute(
        cls,
        start_symbol: str,
        grammar: Dict[str, List[Any]],
    ) -> Dict[str, Any]:
        prods: Dict[str, List[List[str]]] = {}
        nonterminals = set(grammar.keys())
        all_symbols = set()

        for lhs, rhs_list in grammar.items():
            prods[str(lhs)] = []
            for rhs in rhs_list:
                if isinstance(rhs, str):
                    tokens = rhs.strip().split() if rhs.strip() else []
                elif isinstance(rhs, (list, tuple)):
                    tokens = [str(t) for t in rhs]
                else:
                    tokens = [str(rhs)]
                if not tokens or tokens == ["ε"] or tokens == ["EPS"] or tokens == ["epsilon"]:
                    prods[str(lhs)].append([cls.EPSILON])
                else:
                    prods[str(lhs)].append(tokens)
                for t in tokens:
                    all_symbols.add(t)

        terminals = {s for s in all_symbols if s not in nonterminals and s != cls.EPSILON}
        terminals.add("$")

        first: Dict[str, Set[str]] = {nt: set() for nt in nonterminals}
        for t in terminals:
            first[t] = {t}
        first[cls.EPSILON] = {cls.EPSILON}

        changed = True
        while changed:
            changed = False
            for A, rhs_list in prods.items():
                for alpha in rhs_list:
                    can_be_eps = True
                    for sym in alpha:
                        sym_first = first.get(sym, {sym})
                        for f_sym in sym_first:
                            if f_sym != cls.EPSILON:
                                if f_sym not in first[A]:
                                    first[A].add(f_sym)
                                    changed = True
                        if cls.EPSILON not in sym_first:
                            can_be_eps = False
                            break
                    if can_be_eps:
                        if cls.EPSILON not in first[A]:
                            first[A].add(cls.EPSILON)
                            changed = True

        def first_of_seq(seq: List[str]) -> Tuple[Set[str], bool]:
            res = set()
            is_nullable = True
            for sym in seq:
                sym_first = first.get(sym, {sym})
                res.update({s for s in sym_first if s != cls.EPSILON})
                if cls.EPSILON not in sym_first:
                    is_nullable = False
                    break
            if is_nullable:
                res.add(cls.EPSILON)
            return res, is_nullable

        follow: Dict[str, Set[str]] = {nt: set() for nt in nonterminals}
        follow[str(start_symbol)].add("$")

        changed = True
        while changed:
            changed = False
            for A, rhs_list in prods.items():
                for alpha in rhs_list:
                    for i, B in enumerate(alpha):
                        if B in nonterminals:
                            beta = alpha[i + 1:]
                            beta_first, beta_nullable = first_of_seq(beta)
                            for s in beta_first:
                                if s != cls.EPSILON and s not in follow[B]:
                                    follow[B].add(s)
                                    changed = True
                            if beta_nullable or not beta:
                                for s in follow[A]:
                                    if s not in follow[B]:
                                        follow[B].add(s)
                                        changed = True

        table: Dict[str, Dict[str, List[str]]] = {nt: {} for nt in nonterminals}
        conflicts = []

        for A, rhs_list in prods.items():
            for alpha in rhs_list:
                alpha_first, alpha_nullable = first_of_seq(alpha)
                for a in alpha_first:
                    if a != cls.EPSILON:
                        if a in table[A]:
                            conflicts.append({
                                "nonterminal": A,
                                "lookahead": a,
                                "existing": table[A][a],
                                "conflict": alpha,
                                "type": "FIRST-FIRST",
                            })
                        else:
                            table[A][a] = alpha
                if alpha_nullable:
                    for b in follow[A]:
                        if b in table[A]:
                            conflicts.append({
                                "nonterminal": A,
                                "lookahead": b,
                                "existing": table[A][b],
                                "conflict": alpha,
                                "type": "FIRST-FOLLOW",
                            })
                        else:
                            table[A][b] = alpha

        is_ll1 = len(conflicts) == 0

        formatted_table = {}
        for nt, row in table.items():
            formatted_table[nt] = {term: " ".join(prod) if prod != [cls.EPSILON] else "ε" for term, prod in row.items()}

        return {
            "start_symbol": str(start_symbol),
            "is_ll1": is_ll1,
            "conflicts_count": len(conflicts),
            "conflicts": conflicts,
            "first_sets": {k: sorted(list(v)) for k, v in first.items() if k in nonterminals},
            "follow_sets": {k: sorted(list(v)) for k, v in follow.items()},
            "table": formatted_table,
            "terminals": sorted(list(terminals)),
            "nonterminals": sorted(list(nonterminals)),
        }


class LoopInvariantCodeMotionLICM:
    """Analyzes and hoists loop-invariant instructions into loop pre-headers."""

    @classmethod
    def optimize(
        cls,
        blocks: List[Dict[str, Any]],
        loop_header: str,
        loop_body_labels: List[str],
    ) -> Dict[str, Any]:
        body_set = set(loop_body_labels)
        defs_inside_loop = set()
        all_block_map = {b["label"]: b for b in blocks}

        for lbl in body_set:
            if lbl in all_block_map:
                for inst in all_block_map[lbl].get("instructions", []):
                    dest = inst.get("dest")
                    if dest:
                        defs_inside_loop.add(dest)

        invariant_insts = []
        invariant_defs = set()
        changed = True

        while changed:
            changed = False
            for lbl in body_set:
                if lbl in all_block_map:
                    for inst in all_block_map[lbl].get("instructions", []):
                        dest = inst.get("dest")
                        if not dest or dest in invariant_defs:
                            continue
                        op = inst.get("op", "")
                        if op in ("call", "store", "print", "ret", "br", "cbr"):
                            continue
                        args = inst.get("args", [])
                        is_invariant = True
                        for a in args:
                            a_str = str(a)
                            if a_str.lstrip("-").replace(".", "", 1).isdigit():
                                continue
                            if a_str in defs_inside_loop and a_str not in invariant_defs:
                                is_invariant = False
                                break
                        if is_invariant:
                            invariant_defs.add(dest)
                            invariant_insts.append({
                                "source_block": lbl,
                                "instruction": inst,
                            })
                            changed = True

        hoisted = [inv["instruction"] for inv in invariant_insts]

        return {
            "loop_header": loop_header,
            "loop_blocks_count": len(body_set),
            "hoisted_instructions_count": len(hoisted),
            "invariant_variables": sorted(list(invariant_defs)),
            "hoisted_instructions": hoisted,
        }


def compiler_build_ll1_table(start_symbol: str, grammar: Dict[str, List[Any]]) -> Any:
    """Computes FIRST/FOLLOW sets and constructs LL(1) predictive parse table."""
    return Record(LL1GrammarTableGenerator.compute(start_symbol, grammar))


def compiler_optimize_licm(
    blocks: List[Dict[str, Any]],
    loop_header: str,
    loop_body_labels: List[str],
) -> Any:
    """Identifies and hoists loop-invariant instructions into loop pre-header."""
    return Record(LoopInvariantCodeMotionLICM.optimize(blocks, loop_header, loop_body_labels))


# ==============================================================================
# SPARSE CONDITIONAL CONSTANT PROPAGATION (SCCP) & EARLEY CHART PARSER
# ==============================================================================


class SparseConditionalConstantPropagationSCCP:
    """Wegman-Zadeck Sparse Conditional Constant Propagation (SCCP) optimizer.

    Simultaneously propagates constants through SSA dataflow and evaluates
    control flow reachability, discovering constants that become known only
    because branches are proven unexecutable.
    """

    TOP = ("TOP",)
    BOT = ("BOT",)

    @classmethod
    def _meet(cls, v1: Any, v2: Any) -> Any:
        if v1 == cls.TOP:
            return v2
        if v2 == cls.TOP:
            return v1
        if v1 == cls.BOT or v2 == cls.BOT:
            return cls.BOT
        return v1 if v1 == v2 else cls.BOT

    @classmethod
    def _eval_op(cls, op: str, operands: List[Any]) -> Any:
        if any(v == cls.BOT for v in operands):
            return cls.BOT
        if any(v == cls.TOP for v in operands):
            return cls.TOP

        op_lower = op.lower()
        try:
            if op_lower in ("add", "+"):
                return operands[0] + operands[1]
            elif op_lower in ("sub", "-"):
                return operands[0] - operands[1]
            elif op_lower in ("mul", "*"):
                return operands[0] * operands[1]
            elif op_lower in ("div", "/"):
                return operands[0] // operands[1] if operands[1] != 0 else cls.BOT
            elif op_lower in ("eq", "=="):
                return operands[0] == operands[1]
            elif op_lower in ("ne", "!="):
                return operands[0] != operands[1]
            elif op_lower in ("lt", "<"):
                return operands[0] < operands[1]
            elif op_lower in ("le", "<="):
                return operands[0] <= operands[1]
            elif op_lower in ("gt", ">"):
                return operands[0] > operands[1]
            elif op_lower in ("ge", ">="):
                return operands[0] >= operands[1]
            elif op_lower in ("and", "&&"):
                return bool(operands[0] and operands[1])
            elif op_lower in ("or", "||"):
                return bool(operands[0] or operands[1])
            elif op_lower in ("not", "!"):
                return not operands[0]
            elif op_lower in ("neg",):
                return -operands[0]
        except Exception:
            return cls.BOT
        return cls.BOT

    @classmethod
    def optimize(cls, cfg_ir: Dict[str, Any]) -> Dict[str, Any]:
        """Runs SCCP on basic block SSA IR."""
        entry = cfg_ir.get("entry", "B0")
        raw_blocks = cfg_ir.get("blocks", {})
        if not raw_blocks:
            return {
                "constants": {},
                "executable_blocks": [],
                "executable_edges": [],
                "optimized_blocks": {},
            }

        lat_val: Dict[str, Any] = {}
        def_to_inst: Dict[str, Tuple[str, Dict[str, Any]]] = {}
        var_uses: Dict[str, List[Tuple[str, int, Dict[str, Any]]]] = {}

        for b_lbl, b_data in raw_blocks.items():
            for idx, inst in enumerate(b_data.get("instructions", [])):
                dest = inst.get("dest")
                if dest:
                    lat_val[dest] = cls.TOP
                    def_to_inst[dest] = (b_lbl, inst)
                for a in inst.get("args", []):
                    if isinstance(a, str) and not a.lstrip("-").replace(".", "", 1).isdigit():
                        var_uses.setdefault(a, []).append((b_lbl, idx, inst))
                if "cond" in inst:
                    cond_var = inst["cond"]
                    if isinstance(cond_var, str):
                        var_uses.setdefault(cond_var, []).append((b_lbl, idx, inst))
                if inst.get("op") == "phi":
                    for inc_b, inc_v in inst.get("incoming", {}).items():
                        if isinstance(inc_v, str) and not inc_v.lstrip("-").isdigit():
                            var_uses.setdefault(inc_v, []).append((b_lbl, idx, inst))

        cfg_worklist: List[Tuple[Optional[str], str]] = [(None, entry)]
        ssa_worklist: List[str] = []
        executed_edges: Set[Tuple[Optional[str], str]] = set()
        executed_blocks: Set[str] = set()

        def resolve_val(operand: Any) -> Any:
            if isinstance(operand, (int, float, bool)):
                return operand
            if isinstance(operand, str):
                if operand.lstrip("-").isdigit():
                    return int(operand)
                if operand in lat_val:
                    return lat_val[operand]
            return cls.BOT

        while cfg_worklist or ssa_worklist:
            while cfg_worklist:
                edge = cfg_worklist.pop(0)
                if edge in executed_edges:
                    continue
                executed_edges.add(edge)
                src, dest_b = edge
                is_first_visit = dest_b not in executed_blocks
                executed_blocks.add(dest_b)

                b_data = raw_blocks.get(dest_b, {})
                insts = b_data.get("instructions", [])

                for inst in insts:
                    if inst.get("op") == "phi":
                        dest_var = inst["dest"]
                        incoming = inst.get("incoming", {})
                        res = cls.TOP
                        for pred, in_var in incoming.items():
                            if (pred, dest_b) in executed_edges:
                                in_val = resolve_val(in_var)
                                res = cls._meet(res, in_val)
                        if res != lat_val[dest_var]:
                            lat_val[dest_var] = res
                            ssa_worklist.append(dest_var)

                if is_first_visit:
                    for inst in insts:
                        op = inst.get("op")
                        if op == "phi":
                            continue
                        dest_var = inst.get("dest")
                        if op == "const":
                            val = inst.get("value")
                            if dest_var and lat_val[dest_var] != val:
                                lat_val[dest_var] = val
                                ssa_worklist.append(dest_var)
                        elif dest_var:
                            args = [resolve_val(a) for a in inst.get("args", [])]
                            out_v = cls._eval_op(op, args)
                            if lat_val[dest_var] != out_v:
                                lat_val[dest_var] = out_v
                                ssa_worklist.append(dest_var)
                        elif op == "br_cond":
                            cond_v = resolve_val(inst.get("cond"))
                            t_target = inst.get("true_target")
                            f_target = inst.get("false_target")
                            if cond_v is True or cond_v == 1:
                                cfg_worklist.append((dest_b, t_target))
                            elif cond_v is False or cond_v == 0:
                                cfg_worklist.append((dest_b, f_target))
                            elif cond_v == cls.BOT:
                                cfg_worklist.append((dest_b, t_target))
                                cfg_worklist.append((dest_b, f_target))
                        elif op in ("jump", "goto"):
                            cfg_worklist.append((dest_b, inst.get("target")))

            while ssa_worklist:
                var = ssa_worklist.pop(0)
                for u_block, u_idx, u_inst in var_uses.get(var, []):
                    if u_block not in executed_blocks:
                        continue
                    op = u_inst.get("op")
                    dest_var = u_inst.get("dest")
                    if op == "phi":
                        incoming = u_inst.get("incoming", {})
                        res = cls.TOP
                        for pred, in_var in incoming.items():
                            if (pred, u_block) in executed_edges:
                                in_val = resolve_val(in_var)
                                res = cls._meet(res, in_val)
                        if res != lat_val[dest_var]:
                            lat_val[dest_var] = res
                            ssa_worklist.append(dest_var)
                    elif dest_var:
                        args = [resolve_val(a) for a in u_inst.get("args", [])]
                        out_v = cls._eval_op(op, args)
                        if lat_val[dest_var] != out_v:
                            lat_val[dest_var] = out_v
                            ssa_worklist.append(dest_var)
                    elif op == "br_cond":
                        cond_v = resolve_val(u_inst.get("cond"))
                        t_target = u_inst.get("true_target")
                        f_target = u_inst.get("false_target")
                        if cond_v is True or cond_v == 1:
                            cfg_worklist.append((u_block, t_target))
                        elif cond_v is False or cond_v == 0:
                            cfg_worklist.append((u_block, f_target))
                        elif cond_v == cls.BOT:
                            cfg_worklist.append((u_block, t_target))
                            cfg_worklist.append((u_block, f_target))

        known_constants: Dict[str, Any] = {}
        for var, val in lat_val.items():
            if val not in (cls.TOP, cls.BOT):
                known_constants[var] = val

        optimized_blocks: Dict[str, Any] = {}
        for b_lbl in sorted(list(executed_blocks)):
            b_data = raw_blocks[b_lbl]
            new_insts = []
            for inst in b_data.get("instructions", []):
                new_inst = dict(inst)
                if "args" in new_inst:
                    new_inst["args"] = [known_constants.get(a, a) for a in new_inst["args"]]
                if new_inst.get("op") == "br_cond":
                    cond_val = known_constants.get(new_inst.get("cond"), new_inst.get("cond"))
                    if cond_val is True or cond_val == 1:
                        new_inst = {"op": "jump", "target": new_inst["true_target"]}
                    elif cond_val is False or cond_val == 0:
                        new_inst = {"op": "jump", "target": new_inst["false_target"]}
                new_insts.append(new_inst)
            optimized_blocks[b_lbl] = {
                "instructions": new_insts,
                "successors": [tgt for (src, tgt) in executed_edges if src == b_lbl],
            }

        return {
            "constants": known_constants,
            "executable_blocks": sorted(list(executed_blocks)),
            "dead_blocks": sorted([b for b in raw_blocks if b not in executed_blocks]),
            "executable_edges": [f"{s}->{t}" for (s, t) in executed_edges if s is not None],
            "optimized_blocks": optimized_blocks,
        }


class EarleyChartParser:
    """Earley's general context-free grammar chart parsing algorithm.

    Parses any context-free grammar in O(n^3) time worst case, O(n^2) for
    unambiguous grammars, and O(n) for deterministic grammars. Correctly handles
    direct and indirect left recursion, epsilon (empty) rules, and ambiguous derivations.
    """

    @classmethod
    def parse(
        cls,
        grammar: Dict[str, Any],
        start_symbol: str,
        tokens: List[str],
    ) -> Dict[str, Any]:
        """Parses a token sequence using an Earley chart."""
        # Normalize grammar productions to List[Tuple[str, ...]]
        clean_grammar: Dict[str, List[Tuple[str, ...]]] = {}
        for nt, prods in grammar.items():
            clean_grammar[nt] = []
            for p in prods:
                if isinstance(p, (list, tuple)):
                    clean_grammar[nt].append(tuple(str(x) for x in p))
                elif isinstance(p, str):
                    clean_grammar[nt].append(tuple(p.split()))

        n = len(tokens)
        chart: List[List[Tuple[str, Tuple[str, ...], int, int]]] = [[] for _ in range(n + 1)]
        seen: List[Set[Tuple[str, Tuple[str, ...], int, int]]] = [set() for _ in range(n + 1)]

        def add_state(k: int, state: Tuple[str, Tuple[str, ...], int, int]) -> None:
            if state not in seen[k]:
                seen[k].add(state)
                chart[k].append(state)

        for prod in clean_grammar.get(start_symbol, []):
            add_state(0, (start_symbol, prod, 0, 0))

        for k in range(n + 1):
            i = 0
            while i < len(chart[k]):
                lhs, rhs, dot, origin = chart[k][i]
                i += 1
                if dot < len(rhs):
                    next_sym = rhs[dot]
                    if next_sym in clean_grammar:
                        # PREDICTOR
                        for prod in clean_grammar[next_sym]:
                            add_state(k, (next_sym, prod, 0, k))
                    elif k < n and next_sym == tokens[k]:
                        # SCANNER
                        add_state(k + 1, (lhs, rhs, dot + 1, origin))
                else:
                    # COMPLETER
                    for p_lhs, p_rhs, p_dot, p_origin in list(chart[origin]):
                        if p_dot < len(p_rhs) and p_rhs[p_dot] == lhs:
                            add_state(k, (p_lhs, p_rhs, p_dot + 1, p_origin))

        accepted_states = [
            (lhs, list(rhs), dot, origin)
            for (lhs, rhs, dot, origin) in chart[n]
            if lhs == start_symbol and dot == len(rhs) and origin == 0
        ]
        is_accepted = len(accepted_states) > 0

        chart_sizes = [len(c) for c in chart]
        total_states = sum(chart_sizes)

        return {
            "accepted": is_accepted,
            "tokens_length": n,
            "total_chart_states": total_states,
            "chart_sizes_by_column": chart_sizes,
            "accepted_derivation_count": len(accepted_states),
            "start_symbol": start_symbol,
        }


def compiler_sccp_optimize(cfg_ir: Dict[str, Any]) -> Any:
    """Executes Wegman-Zadeck SCCP optimization pass."""
    return Record(SparseConditionalConstantPropagationSCCP.optimize(cfg_ir))


def compiler_earley_parse(grammar: Dict[str, Any], start_symbol: str, tokens: List[str]) -> Any:
    """Executes Earley general CFG parsing."""
    return Record(EarleyChartParser.parse(grammar, start_symbol, tokens))




