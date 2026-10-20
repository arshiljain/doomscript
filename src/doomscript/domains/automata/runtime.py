"""Formal Automata, Regular Languages & Turing Machines Domain for DoomScript.

Provides 100% pure Python implementations of:
- Deterministic Finite Automaton (DFA) execution & Hopcroft state minimization
- Nondeterministic Finite Automaton (NFA) with epsilon-closures & Powerset DFA construction
- Thompson's Construction (Regular Expression to epsilon-NFA)
- Pushdown Automaton (PDA) stack-based language recognizer
- Universal Turing Machine simulator with infinite tape
Zero external dependencies.
"""

from __future__ import annotations

from collections import deque
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from doomscript.runtime import Record


# --- 1. Deterministic Finite Automaton (DFA) ---

class DFA:
    """Deterministic Finite Automaton."""

    def __init__(
        self,
        states: Set[str],
        alphabet: Set[str],
        transitions: Dict[Tuple[str, str], str],
        start_state: str,
        accept_states: Set[str],
    ):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.transitions = dict(transitions)
        self.start_state = start_state
        self.accept_states = set(accept_states)

    def accepts(self, input_str: str) -> bool:
        """Determines if the DFA accepts the given input string."""
        current = self.start_state
        for sym in input_str:
            if sym not in self.alphabet:
                return False
            key = (current, sym)
            if key not in self.transitions:
                return False
            current = self.transitions[key]
        return current in self.accept_states

    def minimize(self) -> DFA:
        """Hopcroft's state minimization algorithm."""
        # 1. Eliminate unreachable states
        reachable: Set[str] = set()
        queue = deque([self.start_state])
        while queue:
            s = queue.popleft()
            if s not in reachable:
                reachable.add(s)
                for sym in self.alphabet:
                    nxt = self.transitions.get((s, sym))
                    if nxt and nxt not in reachable:
                        queue.append(nxt)

        states = reachable
        accept = self.accept_states.intersection(states)
        non_accept = states - accept

        # Partition P = {Accept, NonAccept}
        P: List[Set[str]] = []
        if accept:
            P.append(accept)
        if non_accept:
            P.append(non_accept)

        W: List[Set[str]] = [set(accept)] if accept else []

        while W:
            A = W.pop(0)
            for c in self.alphabet:
                # X = set of states for which transition on c leads to A
                X = {s for s in states if self.transitions.get((s, c)) in A}
                new_P: List[Set[str]] = []
                for Y in P:
                    inter = Y.intersection(X)
                    diff = Y - X
                    if inter and diff:
                        new_P.append(inter)
                        new_P.append(diff)
                        if Y in W:
                            W.remove(Y)
                            W.append(inter)
                            W.append(diff)
                        else:
                            if len(inter) <= len(diff):
                                W.append(inter)
                            else:
                                W.append(diff)
                    else:
                        new_P.append(Y)
                P = new_P

        # Build minimized DFA
        group_map: Dict[str, str] = {}
        for group in P:
            group_name = "_".join(sorted(group))
            for s in group:
                group_map[s] = group_name

        min_states = set(group_map.values())
        min_start = group_map[self.start_state]
        min_accept = {group_map[s] for s in accept}
        min_trans: Dict[Tuple[str, str], str] = {}

        for (s, c), nxt in self.transitions.items():
            if s in states and nxt in states:
                g_s = group_map[s]
                g_nxt = group_map[nxt]
                min_trans[(g_s, c)] = g_nxt

        return DFA(min_states, self.alphabet, min_trans, min_start, min_accept)


# --- 2. Nondeterministic Finite Automaton (NFA) ---

class NFA:
    """Nondeterministic Finite Automaton with epsilon-transitions."""

    def __init__(
        self,
        states: Set[str],
        alphabet: Set[str],
        transitions: Dict[Tuple[str, str], Set[str]],
        start_state: str,
        accept_states: Set[str],
        epsilon_transitions: Optional[Dict[str, Set[str]]] = None,
    ):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.transitions = {k: set(v) for k, v in transitions.items()}
        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.epsilon_transitions = {k: set(v) for k, v in (epsilon_transitions or {}).items()}

    def epsilon_closure(self, current_states: Set[str]) -> Set[str]:
        """Calculates epsilon-closure reachable from set of states."""
        closure = set(current_states)
        stack = list(current_states)
        while stack:
            s = stack.pop()
            eps = self.epsilon_transitions.get(s, set())
            for nxt in eps:
                if nxt not in closure:
                    closure.add(nxt)
                    stack.append(nxt)
        return closure

    def accepts(self, input_str: str) -> bool:
        """Determines if the NFA accepts the string via subset simulation."""
        current = self.epsilon_closure({self.start_state})
        for sym in input_str:
            next_states = set()
            for s in current:
                next_states.update(self.transitions.get((s, sym), set()))
            current = self.epsilon_closure(next_states)
        return bool(current.intersection(self.accept_states))

    def to_dfa(self) -> DFA:
        """Converts NFA to equivalent DFA using Powerset / Subset Construction."""
        dfa_states: Set[str] = set()
        dfa_trans: Dict[Tuple[str, str], str] = {}
        dfa_accept: Set[str] = set()

        start_set = frozenset(self.epsilon_closure({self.start_state}))
        queue = deque([start_set])
        visited = {start_set}

        def set_name(s_set: frozenset) -> str:
            return "_".join(sorted(s_set)) or "EMPTY"

        start_name = set_name(start_set)
        dfa_states.add(start_name)
        if start_set.intersection(self.accept_states):
            dfa_accept.add(start_name)

        while queue:
            cur_set = queue.popleft()
            cur_name = set_name(cur_set)

            for sym in self.alphabet:
                nxt_set_raw = set()
                for s in cur_set:
                    nxt_set_raw.update(self.transitions.get((s, sym), set()))
                nxt_set = frozenset(self.epsilon_closure(nxt_set_raw))

                if not nxt_set:
                    continue

                nxt_name = set_name(nxt_set)
                dfa_trans[(cur_name, sym)] = nxt_name
                dfa_states.add(nxt_name)

                if nxt_set.intersection(self.accept_states):
                    dfa_accept.add(nxt_name)

                if nxt_set not in visited:
                    visited.add(nxt_set)
                    queue.append(nxt_set)

        return DFA(dfa_states, self.alphabet, dfa_trans, start_name, dfa_accept)


# --- 3. Thompson's Construction ---

class ThompsonRegex:
    """Constructs an epsilon-NFA from a regular expression."""

    @staticmethod
    def compile(regex: str) -> NFA:
        """Compiles simple regex (concatenation, |, *, ?) into NFA."""
        # Simple state counter
        state_id = 0

        def new_state() -> str:
            nonlocal state_id
            s = f"q{state_id}"
            state_id += 1
            return s

        # Shunting-yard to convert infix regex to postfix
        postfix = ThompsonRegex._to_postfix(regex)
        stack: List[Tuple[str, str, Dict[Tuple[str, str], Set[str]], Dict[str, Set[str]]]] = []

        for ch in postfix:
            if ch == "*":
                # Kleene star
                start, end, trans, eps = stack.pop()
                new_s = new_state()
                new_e = new_state()
                eps.setdefault(new_s, set()).update({start, new_e})
                eps.setdefault(end, set()).update({start, new_e})
                stack.append((new_s, new_e, trans, eps))
            elif ch == "|":
                # Alternation
                s2, e2, t2, ep2 = stack.pop()
                s1, e1, t1, ep1 = stack.pop()
                new_s = new_state()
                new_e = new_state()
                trans = {**t1, **t2}
                eps = {**ep1}
                for k, v in ep2.items():
                    eps.setdefault(k, set()).update(v)
                eps.setdefault(new_s, set()).update({s1, s2})
                eps.setdefault(e1, set()).add(new_e)
                eps.setdefault(e2, set()).add(new_e)
                stack.append((new_s, new_e, trans, eps))
            elif ch == ".":
                # Concatenation
                s2, e2, t2, ep2 = stack.pop()
                s1, e1, t1, ep1 = stack.pop()
                trans = {**t1, **t2}
                eps = {**ep1}
                for k, v in ep2.items():
                    eps.setdefault(k, set()).update(v)
                eps.setdefault(e1, set()).add(s2)
                stack.append((s1, e2, trans, eps))
            else:
                # Single character literal
                s = new_state()
                e = new_state()
                trans = {(s, ch): {e}}
                eps = {}
                stack.append((s, e, trans, eps))

        start, end, trans, eps = stack.pop()
        alphabet = {c for (_, c) in trans.keys()}
        states = set()
        for (u, _), v_set in trans.items():
            states.add(u)
            states.update(v_set)
        for u, v_set in eps.items():
            states.add(u)
            states.update(v_set)
        states.add(start)
        states.add(end)

        return NFA(states, alphabet, trans, start, {end}, eps)

    @staticmethod
    def _to_postfix(regex: str) -> str:
        """Inserts explicit concatenation '.' and converts to postfix."""
        # 1. Insert explicit concatenation '.'
        expanded = []
        for i, c in enumerate(regex):
            expanded.append(c)
            if i + 1 < len(regex):
                c_next = regex[i + 1]
                if (c.isalnum() or c in "*") and (c_next.isalnum() or c_next == "("):
                    expanded.append(".")

        # 2. Shunting-Yard
        precedence = {"*": 3, ".": 2, "|": 1}
        output = []
        op_stack = []

        for c in expanded:
            if c.isalnum():
                output.append(c)
            elif c == "(":
                op_stack.append(c)
            elif c == ")":
                while op_stack and op_stack[-1] != "(":
                    output.append(op_stack.pop())
                if op_stack:
                    op_stack.pop()
            else:
                while op_stack and op_stack[-1] != "(" and precedence.get(op_stack[-1], 0) >= precedence.get(c, 0):
                    output.append(op_stack.pop())
                op_stack.append(c)

        while op_stack:
            output.append(op_stack.pop())

        return "".join(output)


# --- 4. Universal Turing Machine ---

class TuringMachine:
    """Universal Turing Machine with infinite tape."""

    def __init__(
        self,
        transitions: Dict[Tuple[str, str], Tuple[str, str, str]],
        tape: str = "",
        start_state: str = "q0",
        accept_states: Optional[Set[str]] = None,
        blank_symbol: str = "_",
    ):
        self.transitions = dict(transitions)
        self.state = start_state
        self.accept_states = set(accept_states or {"q_accept"})
        self.blank = blank_symbol
        self.head = 0

        # Dynamic dictionary tape: index -> symbol
        self.tape: Dict[int, str] = {i: c for i, c in enumerate(tape)} if tape else {0: self.blank}
        self.steps = 0

    def step(self) -> bool:
        """Executes one step. Returns False if machine halted."""
        if self.state in self.accept_states:
            return False

        sym = self.tape.get(self.head, self.blank)
        key = (self.state, sym)
        if key not in self.transitions:
            return False

        next_state, write_sym, direction = self.transitions[key]
        self.tape[self.head] = write_sym
        self.state = next_state

        if direction.upper() == "R":
            self.head += 1
        elif direction.upper() == "L":
            self.head -= 1

        self.steps += 1
        return True

    def run(self, max_steps: int = 10000) -> Dict[str, Any]:
        """Runs the machine until acceptance, reject, or step limit."""
        while self.steps < max_steps:
            if not self.step():
                break

        accepted = self.state in self.accept_states

        # Extract continuous tape string
        if self.tape:
            min_idx = min(self.tape.keys())
            max_idx = max(self.tape.keys())
            tape_str = "".join(self.tape.get(i, self.blank) for i in range(min_idx, max_idx + 1))
        else:
            tape_str = ""

        return {
            "accepted": accepted,
            "final_state": self.state,
            "head": self.head,
            "steps": self.steps,
            "tape": tape_str,
        }


# --- Public High-Level Runtime Functions ---

def automata_create_dfa(
    states: List[str],
    alphabet: List[str],
    transitions: Dict[Tuple[str, str], str],
    start_state: str,
    accept_states: List[str],
) -> DFA:
    """Creates a Deterministic Finite Automaton."""
    return DFA(set(states), set(alphabet), transitions, start_state, set(accept_states))


def automata_dfa_accepts(dfa: DFA, input_str: str) -> bool:
    """Checks if DFA accepts the given string."""
    return dfa.accepts(input_str)


def automata_minimize_dfa(dfa: DFA) -> DFA:
    """Minimizes DFA using Hopcroft's algorithm."""
    return dfa.minimize()


def automata_regex_to_dfa(regex: str) -> DFA:
    """Converts a regular expression to an equivalent minimized DFA."""
    nfa = ThompsonRegex.compile(regex)
    dfa = nfa.to_dfa()
    return dfa.minimize()


def automata_run_turing_machine(
    transitions: Dict[Tuple[str, str], Tuple[str, str, str]],
    tape: str = "",
    start_state: str = "q0",
    accept_states: Optional[List[str]] = None,
    max_steps: int = 1000,
) -> Dict[str, Any]:
    """Simulates a Turing Machine."""
    tm = TuringMachine(transitions, tape, start_state, set(accept_states or ["q_accept"]))
    return tm.run(max_steps)


# --- 5. Pushdown Automaton (PDA) ---

class PushdownAutomaton:
    """Non-deterministic Pushdown Automaton (PDA) with epsilon-transitions.
    
    Acceptance modes:
    - 'final_state': accepts if input is consumed and state is in accept_states
    - 'empty_stack': accepts if input is consumed and stack is empty
    - 'both': accepts if input is consumed, state is in accept_states, and stack is empty
    """

    def __init__(
        self,
        states: Set[str],
        input_alphabet: Set[str],
        stack_alphabet: Set[str],
        transitions: Dict[Tuple[str, str, str], List[Tuple[str, List[str]]]],
        start_state: str,
        start_stack_symbol: str = "Z0",
        accept_states: Optional[Set[str]] = None,
        acceptance_mode: str = "final_state",
    ):
        self.states = set(states)
        self.input_alphabet = set(input_alphabet)
        self.stack_alphabet = set(stack_alphabet)
        # key: (current_state, input_char_or_empty, stack_top) -> [(next_state, [pushed_symbols])]
        self.transitions = dict(transitions)
        self.start_state = start_state
        self.start_stack_symbol = start_stack_symbol
        self.accept_states = set(accept_states or set())
        self.acceptance_mode = acceptance_mode.lower()

    def accepts(self, input_str: str, max_steps: int = 2000) -> bool:
        """Determines if the PDA accepts input_str using breadth-first search."""
        # Queue item: (current_state, char_index, stack_tuple)
        init_stack = (self.start_stack_symbol,) if self.start_stack_symbol else ()
        queue = deque([(self.start_state, 0, init_stack)])
        visited = set()
        steps = 0

        while queue and steps < max_steps:
            steps += 1
            state, idx, stack = queue.popleft()
            config_key = (state, idx, stack)
            if config_key in visited:
                continue
            visited.add(config_key)

            # Check acceptance condition if entire input is consumed
            if idx == len(input_str):
                if self.acceptance_mode == "final_state" and state in self.accept_states:
                    return True
                elif self.acceptance_mode == "empty_stack" and len(stack) == 0:
                    return True
                elif self.acceptance_mode == "both" and state in self.accept_states and len(stack) == 0:
                    return True

            top = stack[-1] if stack else ""

            # 1. Epsilon transitions (no input symbol consumed)
            for (q_cur, in_sym, s_top), targets in self.transitions.items():
                if q_cur == state and in_sym == "" and (s_top == "" or s_top == top):
                    for next_q, push_symbols in targets:
                        base_stack = stack[:-1] if (s_top != "" and stack) else stack
                        new_stack = base_stack + tuple(push_symbols)
                        queue.append((next_q, idx, new_stack))

            # 2. Consuming transitions (read next character from input_str)
            if idx < len(input_str):
                curr_char = input_str[idx]
                for (q_cur, in_sym, s_top), targets in self.transitions.items():
                    if q_cur == state and in_sym == curr_char and (s_top == "" or s_top == top):
                        for next_q, push_symbols in targets:
                            base_stack = stack[:-1] if (s_top != "" and stack) else stack
                            new_stack = base_stack + tuple(push_symbols)
                            queue.append((next_q, idx + 1, new_stack))

        return False


# --- 6. Moore & Mealy Finite State Machines ---

class MooreMealyFSM:
    """Synchronous finite state machine supporting both Moore and Mealy models."""

    def __init__(
        self,
        machine_type: str = "moore",
        states: Optional[Set[str]] = None,
        alphabet: Optional[Set[str]] = None,
        transitions: Optional[Dict[Tuple[str, str], str]] = None,
        outputs: Optional[Dict[Any, Any]] = None,
        start_state: str = "s0",
    ):
        self.machine_type = machine_type.lower()
        self.states = set(states or set())
        self.alphabet = set(alphabet or set())
        self.transitions = dict(transitions or {})
        self.outputs = dict(outputs or {})
        self.start_state = start_state
        self.current_state = start_state

    def reset(self):
        self.current_state = self.start_state

    def step(self, sym: str) -> Tuple[str, Any]:
        """Executes a single step given input symbol and returns (new_state, output)."""
        key = (self.current_state, sym)
        if key not in self.transitions:
            raise ValueError(f"No transition defined for state '{self.current_state}' on symbol '{sym}'")
        next_state = self.transitions[key]

        if self.machine_type == "moore":
            output_val = self.outputs.get(next_state)
        else:  # mealy
            output_val = self.outputs.get((self.current_state, sym))

        self.current_state = next_state
        return (next_state, output_val)

    def run(self, input_sequence: Union[str, List[str]]) -> Dict[str, Any]:
        """Runs the machine on an input sequence and returns state history and outputs."""
        self.reset()
        history_states = [self.current_state]
        history_outputs = []

        if self.machine_type == "moore":
            # Initial state output
            history_outputs.append(self.outputs.get(self.current_state))

        for sym in input_sequence:
            next_s, out_val = self.step(sym)
            history_states.append(next_s)
            history_outputs.append(out_val)

        return {
            "machine_type": self.machine_type,
            "final_state": self.current_state,
            "states": history_states,
            "outputs": history_outputs,
        }

    def to_mealy(self) -> MooreMealyFSM:
        """Converts a Moore machine to an equivalent Mealy machine."""
        if self.machine_type == "mealy":
            return self
        mealy_outputs = {}
        for (st, sym), next_st in self.transitions.items():
            mealy_outputs[(st, sym)] = self.outputs.get(next_st)
        return MooreMealyFSM(
            machine_type="mealy",
            states=set(self.states),
            alphabet=set(self.alphabet),
            transitions=dict(self.transitions),
            outputs=mealy_outputs,
            start_state=self.start_state,
        )


# --- 7. Büchi Automaton (Infinite Word Recognition) ---

class BuchiAutomaton:
    """Nondeterministic Büchi Automaton (NBA) over infinite words.
    
    Recognizes omega-words structured as lasso words: u . v^omega (prefix u, repeating cycle v).
    """

    def __init__(
        self,
        states: Set[str],
        alphabet: Set[str],
        transitions: Dict[Tuple[str, str], Set[str]],
        start_state: str,
        accept_states: Set[str],
    ):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.transitions = dict(transitions)
        self.start_state = start_state
        self.accept_states = set(accept_states)

    def accepts_lasso(self, prefix: Union[str, List[str]], cycle: Union[str, List[str]]) -> bool:
        """Determines if the Büchi automaton accepts the lasso word prefix . cycle^omega."""
        # 1. Compute reachable states after prefix
        current_states = {self.start_state}
        for sym in prefix:
            next_states = set()
            for s in current_states:
                targets = self.transitions.get((s, sym), set())
                next_states.update(targets)
            current_states = next_states
            if not current_states:
                return False

        # 2. For each state reachable after prefix, check if reading cycle can loop back
        #    to itself while traversing at least one accept state
        for pivot in current_states:
            # Queue of (current_state, visited_accept)
            configs = {(pivot, pivot in self.accept_states)}
            for sym in cycle:
                next_configs = set()
                for cur_s, seen_accept in configs:
                    for nxt in self.transitions.get((cur_s, sym), set()):
                        next_configs.add((nxt, seen_accept or (nxt in self.accept_states)))
                configs = next_configs
                if not configs:
                    break

            # If pivot is reachable from itself with seen_accept == True, lasso is accepted!
            if (pivot, True) in configs:
                return True

        return False

    def is_empty(self) -> Dict[str, Any]:
        """Checks language emptiness by finding reachable cycles containing an accepting state."""
        # BFS from start to find all reachable states
        visited_from_start = set()
        queue = deque([self.start_state])
        while queue:
            s = queue.popleft()
            if s not in visited_from_start:
                visited_from_start.add(s)
                for (src, _), tgts in self.transitions.items():
                    if src == s:
                        for t in tgts:
                            if t not in visited_from_start:
                                queue.append(t)

        # For each reachable accept state, check if it can reach itself (non-trivial cycle)
        reachable_accept = visited_from_start.intersection(self.accept_states)
        for acc in reachable_accept:
            cycle_q = deque([acc])
            seen_cycle = set()
            first = True
            while cycle_q:
                curr = cycle_q.popleft()
                if curr == acc and not first:
                    return {
                        "is_empty": False,
                        "accepting_state": acc,
                    }
                first = False
                if curr not in seen_cycle:
                    seen_cycle.add(curr)
                    for (src, _), tgts in self.transitions.items():
                        if src == curr:
                            for t in tgts:
                                if t == acc or t not in seen_cycle:
                                    cycle_q.append(t)

        return {"is_empty": True, "accepting_state": None}


# --- Public High-Level Runtime Functions for PDA, FSM, Büchi ---

def automata_create_pda(
    states: List[str],
    input_alphabet: List[str],
    stack_alphabet: List[str],
    transitions: Dict[Tuple[str, str, str], List[Tuple[str, List[str]]]],
    start_state: str,
    start_stack_symbol: str = "Z0",
    accept_states: Optional[List[str]] = None,
    acceptance_mode: str = "final_state",
) -> PushdownAutomaton:
    """Creates a Pushdown Automaton."""
    return PushdownAutomaton(
        set(states),
        set(input_alphabet),
        set(stack_alphabet),
        transitions,
        start_state,
        start_stack_symbol,
        set(accept_states or []),
        acceptance_mode,
    )


def automata_pda_accepts(pda: PushdownAutomaton, input_str: str) -> bool:
    """Evaluates whether PDA accepts input string."""
    return pda.accepts(input_str)


def automata_create_moore_fsm(
    states: List[str],
    alphabet: List[str],
    transitions: Dict[Tuple[str, str], str],
    outputs: Dict[str, Any],
    start_state: str,
) -> MooreMealyFSM:
    """Creates a Moore Finite State Machine."""
    return MooreMealyFSM("moore", set(states), set(alphabet), transitions, outputs, start_state)


def automata_create_mealy_fsm(
    states: List[str],
    alphabet: List[str],
    transitions: Dict[Tuple[str, str], str],
    outputs: Dict[Tuple[str, str], Any],
    start_state: str,
) -> MooreMealyFSM:
    """Creates a Mealy Finite State Machine."""
    return MooreMealyFSM("mealy", set(states), set(alphabet), transitions, outputs, start_state)


def automata_run_fsm(fsm: MooreMealyFSM, input_sequence: Union[str, List[str]]) -> Dict[str, Any]:
    """Runs a Moore or Mealy FSM on an input sequence."""
    return fsm.run(input_sequence)


def automata_create_buchi(
    states: List[str],
    alphabet: List[str],
    transitions: Dict[Tuple[str, str], Set[str]],
    start_state: str,
    accept_states: List[str],
) -> BuchiAutomaton:
    """Creates a Büchi Automaton."""
    return BuchiAutomaton(set(states), set(alphabet), transitions, start_state, set(accept_states))


def automata_buchi_accepts_cycle(buchi: BuchiAutomaton, prefix: str, cycle: str) -> bool:
    """Tests if a Büchi automaton accepts the infinite periodic lasso word prefix . cycle^omega."""
    return buchi.accepts_lasso(prefix, cycle)


# ==============================================================================
# WOLFRAM 1D CELLULAR AUTOMATA (RULE 30, 90, 110, 184)
# ==============================================================================

class CellularAutomata1D:
    """Simulates 1D elementary cellular automata for any Wolfram rule [0, 255]."""

    def __init__(self, rule: int, width: int = 31, initial_state: Optional[List[int]] = None):
        self.rule = max(0, min(255, int(rule)))
        self.width = max(3, int(width))
        if initial_state is not None:
            self.state = [1 if x else 0 for x in initial_state[:self.width]]
            if len(self.state) < self.width:
                self.state.extend([0] * (self.width - len(self.state)))
        else:
            # Single centered active cell
            self.state = [0] * self.width
            self.state[self.width // 2] = 1

        # Lookup table for 3-neighborhood (left, center, right) -> bit value
        self.lookup: Dict[Tuple[int, int, int], int] = {}
        for pattern in range(8):
            bit = (self.rule >> pattern) & 1
            left = (pattern >> 2) & 1
            center = (pattern >> 1) & 1
            right = pattern & 1
            self.lookup[(left, center, right)] = bit

    def step(self) -> List[int]:
        """Advances one generation with periodic boundary wrap-around."""
        next_state = [0] * self.width
        for i in range(self.width):
            left = self.state[(i - 1) % self.width]
            center = self.state[i]
            right = self.state[(i + 1) % self.width]
            next_state[i] = self.lookup[(left, center, right)]
        self.state = next_state
        return list(self.state)

    def simulate(self, generations: int = 20) -> Dict[str, Any]:
        """Evolves the automaton for multiple generations and computes metrics."""
        history = [list(self.state)]
        densities = [sum(self.state) / self.width]

        for _ in range(generations):
            nxt = self.step()
            history.append(list(nxt))
            densities.append(sum(nxt) / self.width)

        # Final generation active cells
        final_active = sum(self.state)
        # Empirical entropy of final state
        p1 = final_active / self.width
        p0 = 1.0 - p1
        import math
        entropy = 0.0
        if p1 > 1e-12:
            entropy -= p1 * math.log2(p1)
        if p0 > 1e-12:
            entropy -= p0 * math.log2(p0)

        return {
            "rule": self.rule,
            "width": self.width,
            "generations": generations,
            "final_active_count": final_active,
            "final_density": round(p1, 4),
            "entropy": round(entropy, 4),
            "history": history,
        }


# ==============================================================================
# CONWAY'S 2D GAME OF LIFE SIMULATOR
# ==============================================================================

class GameOfLife2D:
    """Conway's Game of Life 2D cellular automaton with oscillator detection."""

    def __init__(self, rows: int = 10, cols: int = 10, live_cells: Optional[List[Tuple[int, int]]] = None):
        self.rows = max(3, int(rows))
        self.cols = max(3, int(cols))
        self.grid = [[0] * self.cols for _ in range(self.rows)]
        if live_cells:
            for r, c in live_cells:
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    self.grid[r][c] = 1

    def step(self) -> int:
        """Executes one tick of B3/S23 rule and returns new population count."""
        new_grid = [[0] * self.cols for _ in range(self.rows)]
        population = 0

        for r in range(self.rows):
            for c in range(self.cols):
                # Count 8-neighbors
                neighbors = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr = (r + dr) % self.rows
                        nc = (c + dc) % self.cols
                        neighbors += self.grid[nr][nc]

                curr = self.grid[r][c]
                if curr == 1 and (neighbors == 2 or neighbors == 3):
                    new_grid[r][c] = 1
                    population += 1
                elif curr == 0 and neighbors == 3:
                    new_grid[r][c] = 1
                    population += 1

        self.grid = new_grid
        return population

    def simulate(self, steps: int = 10) -> Dict[str, Any]:
        """Simulates steps and checks for cycle / stability."""
        seen: Dict[str, int] = {}
        history = []
        cycle_period = None

        for step_idx in range(steps):
            key = "".join("".join(str(x) for x in row) for row in self.grid)
            if key in seen:
                cycle_period = step_idx - seen[key]
                break
            seen[key] = step_idx

            pop = self.step()
            history.append(pop)

        final_pop = sum(sum(row) for row in self.grid)
        return {
            "rows": self.rows,
            "cols": self.cols,
            "final_population": final_pop,
            "is_oscillating": cycle_period is not None and cycle_period > 1,
            "is_stable": cycle_period == 1,
            "period": cycle_period,
            "population_history": history,
        }


def automata_simulate_rule(rule: int, width: int = 31, generations: int = 20) -> Any:
    """Simulates 1D Wolfram cellular automaton."""
    ca = CellularAutomata1D(rule, width=width)
    return Record(ca.simulate(generations=generations))


def automata_simulate_life(rows: int, cols: int, live_cells: List[Tuple[int, int]], steps: int = 10) -> Any:
    """Simulates Conway's 2D Game of Life."""
    gol = GameOfLife2D(rows, cols, live_cells=live_cells)
    return Record(gol.simulate(steps=steps))


class MultiTapeTuringMachineSimulator:
    """Simulates a multi-tape deterministic or non-deterministic Turing Machine."""

    @classmethod
    def run(
        cls,
        num_tapes: int,
        initial_tapes: List[str],
        initial_state: str,
        accept_states: List[str],
        transitions: List[Dict[str, Any]],
        max_steps: int = 500,
        blank_symbol: str = " ",
    ) -> Dict[str, Any]:
        accept_set = set(accept_states)
        tapes: List[List[str]] = []
        for i in range(num_tapes):
            if i < len(initial_tapes):
                tapes.append(list(str(initial_tapes[i])) if initial_tapes[i] else [blank_symbol])
            else:
                tapes.append([blank_symbol])

        heads = [0] * num_tapes
        current_state = str(initial_state)

        delta = {}
        for tr in transitions:
            s_from = str(tr.get("from", tr.get("state", "")))
            read_syms = tuple(str(x) for x in tr.get("read", []))
            s_to = str(tr.get("to", tr.get("next_state", "")))
            write_syms = tuple(str(x) for x in tr.get("write", []))
            dirs = tuple(str(x).upper() for x in tr.get("move", tr.get("direction", [])))
            delta[(s_from, read_syms)] = (s_to, write_syms, dirs)

        steps_taken = 0
        halted = False
        accepted = False

        while steps_taken < max_steps:
            if current_state in accept_set:
                halted = True
                accepted = True
                break

            current_read = []
            for t_idx in range(num_tapes):
                h = heads[t_idx]
                if h < 0:
                    tapes[t_idx].insert(0, blank_symbol)
                    heads[t_idx] = 0
                    h = 0
                while h >= len(tapes[t_idx]):
                    tapes[t_idx].append(blank_symbol)
                current_read.append(tapes[t_idx][h])

            key = (current_state, tuple(current_read))
            if key not in delta:
                halted = True
                accepted = current_state in accept_set
                break

            next_st, write_syms, move_dirs = delta[key]

            for t_idx in range(num_tapes):
                if t_idx < len(write_syms):
                    tapes[t_idx][heads[t_idx]] = write_syms[t_idx]

            for t_idx in range(num_tapes):
                d = move_dirs[t_idx] if t_idx < len(move_dirs) else "S"
                if d == "R":
                    heads[t_idx] += 1
                elif d == "L":
                    heads[t_idx] -= 1

            current_state = next_st
            steps_taken += 1

        final_tapes = ["".join(t).strip(blank_symbol) for t in tapes]
        return {
            "num_tapes": num_tapes,
            "final_state": current_state,
            "is_accepted": accepted,
            "steps_executed": steps_taken,
            "is_halted": halted,
            "tapes_output": final_tapes,
            "head_positions": heads,
        }


class ContextFreeGrammarCYKParser:
    """Cocke-Younger-Kasami (CYK) dynamic programming algorithm for Chomsky Normal Form grammars."""

    @classmethod
    def parse(
        cls,
        cnf_grammar: Dict[str, List[Any]],
        start_symbol: str,
        input_tokens: List[str],
    ) -> Dict[str, Any]:
        tokens = [str(tok) for tok in input_tokens]
        n = len(tokens)
        if n == 0:
            return {
                "start_symbol": start_symbol,
                "is_accepted": False,
                "tokens_count": 0,
                "table_cells_filled": 0,
                "root_variables": [],
            }

        unit_rules: Dict[str, Set[str]] = {}
        binary_rules: List[Tuple[str, str, str]] = []

        for lhs, rhs_list in cnf_grammar.items():
            for rhs in rhs_list:
                if isinstance(rhs, (list, tuple)) and len(rhs) == 2:
                    binary_rules.append((str(lhs), str(rhs[0]), str(rhs[1])))
                elif isinstance(rhs, str) and " " in rhs.strip():
                    parts = rhs.strip().split()
                    if len(parts) == 2:
                        binary_rules.append((str(lhs), parts[0], parts[1]))
                    else:
                        unit_rules.setdefault(rhs, set()).add(str(lhs))
                elif isinstance(rhs, str) and len(rhs) == 2 and rhs[0].isupper() and rhs[1].isupper():
                    binary_rules.append((str(lhs), rhs[0], rhs[1]))
                else:
                    unit_rules.setdefault(str(rhs), set()).add(str(lhs))

        table: List[List[Set[str]]] = [[set() for _ in range(n + 1)] for _ in range(n)]

        for i, tok in enumerate(tokens):
            if tok in unit_rules:
                table[i][1].update(unit_rules[tok])

        for length in range(2, n + 1):
            for i in range(n - length + 1):
                for k in range(1, length):
                    left_set = table[i][k]
                    right_set = table[i + k][length - k]
                    if not left_set or not right_set:
                        continue
                    for A, B, C in binary_rules:
                        if B in left_set and C in right_set:
                            table[i][length].add(A)

        total_cells_filled = sum(len(table[i][l]) for i in range(n) for l in range(1, n + 1))
        is_accepted = str(start_symbol) in table[0][n]

        return {
            "start_symbol": start_symbol,
            "is_accepted": is_accepted,
            "tokens_count": n,
            "table_cells_filled": total_cells_filled,
            "root_variables": sorted(list(table[0][n])),
        }


def automata_run_multitape_tm(
    num_tapes: int,
    initial_tapes: List[str],
    initial_state: str,
    accept_states: List[str],
    transitions: List[Dict[str, Any]],
    max_steps: int = 500,
) -> Any:
    """Simulates multi-tape Turing Machine."""
    return Record(MultiTapeTuringMachineSimulator.run(
        num_tapes, initial_tapes, initial_state, accept_states, transitions, max_steps=max_steps
    ))


def automata_cyk_parse(
    cnf_grammar: Dict[str, List[Any]],
    start_symbol: str,
    input_tokens: List[str],
) -> Any:
    """Parses token sequence using Cocke-Younger-Kasami (CYK) algorithm for CNF grammars."""
    return Record(ContextFreeGrammarCYKParser.parse(cnf_grammar, start_symbol, input_tokens))


