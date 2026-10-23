from __future__ import annotations
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainContract, DomainIR


class DomainRegistrationError(ValueError):
    """Raised when registering a domain with conflicting names or aliases."""
    pass


_NON_DOMAIN_STARTS = frozenset({
    "def", "class", "from", "return", "pass", "break",
    "continue", "raise", "yield", "try", "except", "finally",
    "while", "for", "assert", "with", "async", "await", "if", "elif", "else"
})

CORE_VERBS = frozenset({
    "add", "create", "save", "render", "find", "get", "set", "load", "run",
    "display", "build", "check", "clean", "count", "convert", "extract",
    "filter", "list", "read", "remove", "reverse", "sort", "split", "update",
    "calculate", "compute", "make", "put", "let"
})

_ASSIGNMENT_RE = re.compile(r"^[A-Za-z_]\w*\s*=[^=]")


import contextlib
import contextvars
from dataclasses import dataclass, field


@dataclass
class CompilationState:
    """Isolated, per-compilation session state supporting safe concurrent compilation."""
    active_domains: List[str] = field(default_factory=list)
    specs: Dict[str, DomainIR] = field(default_factory=dict)
    spec_counter: int = 0
    last_parsed: Optional[Tuple[str, int, DomainContract, str]] = None


_COMPILATION_STATE: contextvars.ContextVar[Optional[CompilationState]] = contextvars.ContextVar(
    "compilation_state", default=None
)


class DomainRegistry:
    """Registry coordinating available domain packs, namespaces, and dispatch."""

    def __init__(self):
        self._domains: Dict[str, DomainContract] = {}
        self._alias_map: Dict[str, str] = {}
        self._verb_index: Dict[str, List[DomainContract]] = {}
        self._default_state = CompilationState()

    def _get_state(self) -> CompilationState:
        state = _COMPILATION_STATE.get()
        if state is None:
            return self._default_state
        return state

    @property
    def _active_domains(self) -> List[str]:
        return self._get_state().active_domains

    @_active_domains.setter
    def _active_domains(self, val: List[str]) -> None:
        self._get_state().active_domains = val

    @property
    def _specs(self) -> Dict[str, DomainIR]:
        return self._get_state().specs

    @_specs.setter
    def _specs(self, val: Dict[str, DomainIR]) -> None:
        self._get_state().specs = val

    @property
    def _spec_counter(self) -> int:
        return self._get_state().spec_counter

    @_spec_counter.setter
    def _spec_counter(self, val: int) -> None:
        self._get_state().spec_counter = val

    @property
    def _last_parsed(self) -> Optional[Tuple[str, int, DomainContract, str]]:
        return self._get_state().last_parsed

    @_last_parsed.setter
    def _last_parsed(self, val: Optional[Tuple[str, int, DomainContract, str]]) -> None:
        self._get_state().last_parsed = val

    @contextlib.contextmanager
    def compilation_context(self):
        """Context manager providing isolated, reentrant compilation state for concurrent compilation units."""
        existing = _COMPILATION_STATE.get()
        if existing is not None:
            yield existing
            return
        new_state = CompilationState(
            active_domains=list(self._default_state.active_domains),
            specs=dict(self._default_state.specs)
        )
        token = _COMPILATION_STATE.set(new_state)
        try:
            yield new_state
        finally:
            _COMPILATION_STATE.reset(token)

    def register(self, domain: DomainContract) -> None:
        """Registers a domain pack and its aliases. Disallows conflicting aliases."""
        primary_name = domain.name.lower()
        if primary_name in self._domains and self._domains[primary_name] is not domain:
            raise DomainRegistrationError(
                f"Domain '{primary_name}' is already registered by {self._domains[primary_name]}"
            )

        # Check alias conflicts
        for alias in domain.aliases:
            norm_alias = alias.lower()
            if norm_alias in self._alias_map:
                existing = self._alias_map[norm_alias]
                if existing != primary_name:
                    raise DomainRegistrationError(
                        f"Alias collision: '{alias}' is already registered to domain '{existing}', "
                        f"cannot register to domain '{primary_name}'"
                    )

        self._domains[primary_name] = domain
        self._alias_map[primary_name] = primary_name

        for alias in domain.aliases:
            self._alias_map[alias.lower()] = primary_name

        self._index_domain(domain)

    def _index_domain(self, domain: DomainContract) -> None:
        """Indexes domain verbs, prefixes, and operations for fast O(1) candidate lookup."""
        import inspect
        primary_name = domain.name.lower()
        # Index primary name and aliases as keywords
        all_names = [primary_name] + [a.lower() for a in domain.aliases]
        for name in all_names:
            self._verb_index.setdefault(name, [])
            if domain not in self._verb_index[name]:
                self._verb_index[name].append(domain)

        def _add_prefix(w1: str, w2: Optional[str] = None):
            w1_low = w1.lower()
            if w1_low not in CORE_VERBS and w1_low not in _NON_DOMAIN_STARTS:
                self._verb_index.setdefault(w1_low, [])
                if domain not in self._verb_index[w1_low]:
                    self._verb_index[w1_low].append(domain)
            if w2:
                w2_low = f"{w1_low} {w2.lower()}"
                self._verb_index.setdefault(w2_low, [])
                if domain not in self._verb_index[w2_low]:
                    self._verb_index[w2_low].append(domain)

        # Index domain verbs
        verbs = getattr(domain, "verbs", []) or []
        for v in verbs:
            pattern = getattr(v, "pattern", "")
            if pattern:
                tokens = re.findall(
                    r"[A-Za-z_]\w*",
                    pattern.replace("{", " ").replace("}", " ").replace("[", " ").replace("]", " ")
                )
                if tokens:
                    _add_prefix(tokens[0], tokens[1] if len(tokens) > 1 else None)

            name = getattr(v, "name", "")
            if name:
                norm_name = name.lower()
                if norm_name not in CORE_VERBS and norm_name not in _NON_DOMAIN_STARTS:
                    self._verb_index.setdefault(norm_name, [])
                    if domain not in self._verb_index[norm_name]:
                        self._verb_index[norm_name].append(domain)

        # Index regex patterns and comments from domain parser
        p = getattr(domain, "parser", None)
        if p:
            try:
                src = inspect.getsource(p.__class__)

                # 1. Comments with syntax examples (# <verb> <noun> ...)
                for c_line in src.splitlines():
                    c_line = c_line.strip()
                    if c_line.startswith("#") and not c_line.startswith("##") and not c_line.startswith("# -*-"):
                        comment_text = c_line[1:].strip()
                        if any(comment_text.startswith(x) for x in ("TODO", "NOTE", "FIXME", "XXX", "==", "--")):
                            continue
                        words = re.findall(r"[a-zA-Z_]\w*", comment_text)
                        if words:
                            _add_prefix(words[0], words[1] if len(words) > 1 else None)
                            if words[0].lower() in CORE_VERBS and len(words) > 1:
                                _add_prefix(words[1])

                # 2. Regex patterns
                patterns = re.findall(r'r["\']\^([^"\']+)["\']', src)
                for pat in patterns:
                    # Pattern branch alternation e.g. ^find\s+(?:branch1|branch2)
                    m = re.match(r'^(?:([a-zA-Z_]\w*)\\s\+)?\(\?:([^)]+)\)', pat)
                    if m:
                        lead = m.group(1)
                        alts = m.group(2).split('|')
                        for alt in alts:
                            cleaned = re.sub(r'\\[a-zA-Z]', ' ', alt)
                            alt_words = re.findall(r'[a-zA-Z_]\w*', cleaned)
                            if alt_words:
                                if lead:
                                    _add_prefix(lead, alt_words[0])
                                else:
                                    _add_prefix(alt_words[0], alt_words[1] if len(alt_words) > 1 else None)
                    for branch in pat.split('|'):
                        cleaned = re.sub(r'\\[a-zA-Z]', ' ', branch)
                        cleaned = cleaned.replace('(?:', ' ').replace('(?P<', ' ')
                        words = re.findall(r'[a-zA-Z_]\w*', cleaned)
                        if words:
                            _add_prefix(words[0], words[1] if len(words) > 1 else None)
                            if words[0].lower() in CORE_VERBS and len(words) > 1:
                                _add_prefix(words[1])
            except Exception:
                pass

        # Common inspect / explore / profile verbs for domains supporting inspect
        if hasattr(domain, "parser") and hasattr(domain.parser, "parse_inspect"):
            for inspect_kw in ("inspect", "explore", "profile", "examine", "describe", "preview"):
                self._verb_index.setdefault(inspect_kw, [])
                if domain not in self._verb_index[inspect_kw]:
                    self._verb_index[inspect_kw].append(domain)

    def has_domain(self, name: str) -> bool:
        """Checks if a domain or alias is registered."""
        return name.lower() in self._alias_map

    def get_domain(self, name: str) -> Optional[DomainContract]:
        """Resolves a domain contract by name or alias."""
        norm_name = name.lower()
        primary = self._alias_map.get(norm_name)
        if primary and primary in self._domains:
            return self._domains[primary]
        return None

    def activate(self, name: str) -> bool:
        """Activates a domain namespace for the current compilation unit (LIFO order)."""
        norm_name = name.lower()
        primary = self._alias_map.get(norm_name)
        if primary:
            if primary in self._active_domains:
                self._active_domains.remove(primary)
            self._active_domains.append(primary)
            return True
        return False

    def deactivate(self, name: str) -> bool:
        """Deactivates a domain namespace."""
        norm_name = name.lower()
        primary = self._alias_map.get(norm_name)
        if primary and primary in self._active_domains:
            self._active_domains.remove(primary)
            return True
        return False

    def is_active(self, name: str) -> bool:
        """Checks if a domain is currently active."""
        norm_name = name.lower()
        primary = self._alias_map.get(norm_name)
        return primary in self._active_domains if primary else False

    def reset_active(self) -> None:
        """Resets active domains between compilation runs."""
        self._active_domains.clear()
        self._last_parsed = None

    def store_spec(self, ir: DomainIR) -> str:
        """Stores a validated DomainIR spec and returns a unique spec identifier."""
        self._spec_counter += 1
        spec_id = f"ds_spec_{self._spec_counter}"
        self._specs[spec_id] = ir
        self._default_state.specs[spec_id] = ir
        return spec_id

    def get_spec(self, spec_id: str) -> Optional[DomainIR]:
        """Retrieves a DomainIR spec by its unique identifier."""
        return self._specs.get(spec_id) or self._default_state.specs.get(spec_id)

    @property
    def specs(self) -> Dict[str, DomainIR]:
        """Returns dictionary of stored specs."""
        combined = dict(self._default_state.specs)
        combined.update(self._specs)
        return combined

    def get_spec_by_name(self, name: str) -> Optional[DomainIR]:
        """Retrieves a spec by its human-assigned name attribute."""
        for s in list(self._specs.values()) + list(self._default_state.specs.values()):
            if hasattr(s, "name") and s.name == name:
                return s
        return None

    def clear_specs(self) -> None:
        """Clears stored DomainIR specs."""
        self._specs.clear()
        self._default_state.specs.clear()

    def get_all_domains(self) -> List[DomainContract]:
        """Returns all registered domain contracts."""
        return list(self._domains.values())

    def get_active_domains(self) -> List[DomainContract]:
        """Returns all currently active domain instances in LIFO precedence order."""
        return [self._domains[name] for name in reversed(self._active_domains) if name in self._domains]

    def _get_candidate_domains_for_line(self, line: str) -> List[DomainContract]:
        """Determines candidate domains using leading tokens, verbs, and keywords."""
        s = line.strip()
        tokens = s.split()
        if not tokens:
            return []

        w1 = tokens[0].lower()
        candidates: List[DomainContract] = []

        # Check two-word prefix if available (strictly active domains)
        if len(tokens) > 1:
            w2 = f"{w1} {tokens[1].lower()}"
            for d in self._verb_index.get(w2, []):
                if d.name.lower() in self._active_domains and d not in candidates:
                    candidates.append(d)

        # Check single-word prefix (strictly active domains)
        for d in self._verb_index.get(w1, []):
            if d.name.lower() in self._active_domains and d not in candidates:
                candidates.append(d)

        # Special case: tabular queries: <source> where <cond> into <target>
        if "where" in s and "into" in s and "data" in self._domains and "data" in self._active_domains:
            d_data = self._domains["data"]
            if d_data not in candidates:
                candidates.append(d_data)

        # Special case: plot/chart exploration
        if ("explore" in s or "plot" in s or "chart" in s) and "viz" in self._domains and "viz" in self._active_domains:
            d_viz = self._domains["viz"]
            if d_viz not in candidates:
                candidates.append(d_viz)

        return candidates

    def try_parse_domain_line(self, line: str, line_no: int = 0) -> Optional[str]:
        """Fast single-pass matcher: parses a candidate line once and returns the transformed code string."""
        s = line.strip()
        if not s or s.startswith("#"):
            return None

        tokens = s.split()
        first_token = tokens[0].lower().rstrip(":")

        # Fast rejection of Python keywords
        if first_token in _NON_DOMAIN_STARTS:
            return None

        # Fast rejection of regular Python assignments (unless it has 'into' or 'where' keywords)
        if _ASSIGNMENT_RE.match(s) and "into" not in s and "where" not in s:
            return None

        # 1. Check active domains in LIFO order
        for name in reversed(self._active_domains):
            domain = self._domains.get(name)
            if domain:
                try:
                    from doomscript.domains.thought_paradigms import parse_thought_paradigm
                    tp_res = parse_thought_paradigm(name, line, line_no)
                    if tp_res is not None:
                        self._last_parsed = (line, line_no, domain, tp_res)
                        return tp_res
                    res = domain.parser.parse_inspect(line, line_no)
                    if res is not None:
                        self._last_parsed = (line, line_no, domain, res)
                        return res
                    res = domain.parser.parse_operation(line, line_no)
                    if res is not None:
                        self._last_parsed = (line, line_no, domain, res)
                        return res
                except Exception:
                    pass

        # 2. Check explicitly namespaced domains (e.g. "db.find ...")
        if "." in first_token:
            prefix = first_token.split(".")[0]
            dom = self.get_domain(prefix)
            if dom:
                stripped_line = line.replace(f"{prefix}.", "", 1)
                try:
                    res = dom.parser.parse_inspect(stripped_line, line_no)
                    if res is not None:
                        self._last_parsed = (line, line_no, dom, res)
                        return res
                    res = dom.parser.parse_operation(stripped_line, line_no)
                    if res is not None:
                        self._last_parsed = (line, line_no, dom, res)
                        return res
                except Exception:
                    pass

        # 3. Check unambiguous inactive domains (Zero-Import auto-routing for non-scoped domains)
        EXPLICIT_SCOPED_DOMAINS = {"sim", "ml"}
        if len(tokens) > 1:
            w2 = f"{tokens[0].lower()} {tokens[1].lower()}"
            candidates = self._verb_index.get(w2, [])
            if len(candidates) == 1:
                dom = candidates[0]
                if dom.name.lower() not in EXPLICIT_SCOPED_DOMAINS:
                    try:
                        res = dom.parser.parse_inspect(line, line_no)
                        if res is None:
                            res = dom.parser.parse_operation(line, line_no)
                        if res is not None:
                            self.activate(dom.name)
                            self._last_parsed = (line, line_no, dom, res)
                            return res
                    except Exception:
                        pass
        w1 = tokens[0].lower()
        if w1 not in CORE_VERBS and w1 not in _NON_DOMAIN_STARTS:
            candidates = self._verb_index.get(w1, [])
            if len(candidates) == 1:
                dom = candidates[0]
                if dom.name.lower() not in EXPLICIT_SCOPED_DOMAINS:
                    try:
                        res = dom.parser.parse_inspect(line, line_no)
                        if res is None:
                            res = dom.parser.parse_operation(line, line_no)
                        if res is not None:
                            self.activate(dom.name)
                            self._last_parsed = (line, line_no, dom, res)
                            return res
                    except Exception:
                        pass

        # 4. Check thought paradigms across all registered domains (Zero-Import auto-routing)
        try:
            from doomscript.domains.thought_paradigms import parse_thought_paradigm
            for dom_name, dom_inst in self._domains.items():
                tp_res = parse_thought_paradigm(dom_name, line, line_no)
                if tp_res is not None:
                    self.activate(dom_name)
                    self._last_parsed = (line, line_no, dom_inst, tp_res)
                    return tp_res
        except Exception:
            pass

        return None

    def find_domain_for_line(self, line: str, active_only: bool = True) -> Optional[DomainContract]:
        """Finds a domain capable of handling the line. When active_only=True (default), inactive domains are strictly ignored."""
        if self._last_parsed and self._last_parsed[0] == line:
            dom = self._last_parsed[2]
            if not active_only or dom.name.lower() in self._active_domains:
                return dom

        for name in reversed(self._active_domains):
            domain = self._domains.get(name)
            if domain:
                try:
                    res = domain.parser.parse_inspect(line, 0)
                    if res is None:
                        res = domain.parser.parse_operation(line, 0)
                    if res is not None:
                        return domain
                except Exception:
                    pass

        if not active_only:
            for domain in self._domains.values():
                if domain.name.lower() not in self._active_domains:
                    try:
                        res = domain.parser.parse_inspect(line, 0)
                        if res is None:
                            res = domain.parser.parse_operation(line, 0)
                        if res is not None:
                            return domain
                    except Exception:
                        pass

        return None

    def find_domain_for_block(self, header: str, active_only: bool = True) -> Optional[DomainContract]:
        """Finds a domain capable of handling the block header. When active_only=True (default), inactive domains are strictly ignored."""
        for name in reversed(self._active_domains):
            domain = self._domains.get(name)
            if domain and domain.can_handle_block(header):
                return domain

        if not active_only:
            for domain in self._domains.values():
                if domain.name.lower() not in self._active_domains and domain.can_handle_block(header):
                    return domain

        return None

    def get_domain_exports(self, domain_name: Optional[str] = None) -> Dict[str, Any]:
        """Returns runtime functions and classes exported by domain runtime packages."""
        import inspect
        import types
        exports: Dict[str, Any] = {}
        target_domains = [self._domains[domain_name.lower()]] if domain_name and domain_name.lower() in self._domains else list(self._domains.values())

        for domain in target_domains:
            rt = getattr(domain, "runtime", None)
            if rt:
                rt_module = inspect.getmodule(rt.__class__)
                if rt_module:
                    for k, v in vars(rt_module).items():
                        if k.startswith("_") or isinstance(v, types.ModuleType):
                            continue
                        if getattr(v, "__module__", "") in ("typing", "typing_extensions"):
                            continue
                        exports[k] = v
        # Export Thought-to-Code paradigm runtime functions
        try:
            import doomscript.domains.thought_paradigms as tp
            for k, v in vars(tp).items():
                if k.startswith("ds_"):
                    exports[k] = v
        except Exception:
            pass
        return exports


# Global registry singleton
_GLOBAL_DOMAIN_REGISTRY = DomainRegistry()


def get_domain_registry() -> DomainRegistry:
    """Returns the process-wide global DomainRegistry instance."""
    return _GLOBAL_DOMAIN_REGISTRY
