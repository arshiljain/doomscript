"""Independent Domain Parser for Testing & Algorithm Analysis (DSA)."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.dsa.spec import BenchmarkSpec


class DsaDomainParser(DomainParser):
    """Independent parser for Algorithm Analysis, Complexity, and Benchmarking."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        # complexity of <fn> [into <target>]
        m = re.match(
            r"^(?:empirical\s+)?complexity\s+of\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m:
            fn_name = m.group(1)
            target = m.group(2) or f"{fn_name}_complexity"
            return f'set {target} to analyze_complexity("{fn_name}")'

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        # trace <fn> on/with <input> into <target>
        trace_m = re.match(
            r"^trace\s+([A-Za-z_]\w*)\s+(?:on|with)\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if trace_m:
            fn = trace_m.group(1)
            inp = trace_m.group(2).strip()
            target = trace_m.group(3) or f"{fn}_trace"
            return f'set {target} to trace_recursion("{fn}", {inp})'

        # profile memory of <fn> with <input> into <target>
        prof_m = re.match(
            r"^profile\s+memory\s+of\s+([A-Za-z_]\w*)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if prof_m:
            fn = prof_m.group(1)
            inp = prof_m.group(2).strip()
            target = prof_m.group(3)
            return f'set {target} to profile_memory_of_function("{fn}", {inp})'

        # benchmark <fn> with/on sizes <sizes> into <target>
        bm_m = re.match(
            r"^benchmark\s+([A-Za-z_]\w*)\s+(?:with|on)\s+sizes\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if bm_m:
            fn = bm_m.group(1)
            sizes = bm_m.group(2).strip()
            target = bm_m.group(3) or f"{fn}_bench"
            return f'set {target} to run_benchmark_with_sizes("{fn}", {sizes})'

        # create [2d] grid of <fill> with <r> rows and <c> cols into <target>
        grid_m2 = re.match(
            r"^create\s+(?:2d\s+)?grid\s+of\s+(.+?)\s+with\s+(.+?)\s+rows?\s+and\s+(.+?)\s+col(?:umn)?s?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if grid_m2:
            fill = grid_m2.group(1).strip()
            r = grid_m2.group(2).strip()
            c = grid_m2.group(3).strip()
            target = grid_m2.group(4).strip()
            return f"set {target} to dsa_create_grid({r}, {c}, {fill})"

        # create [2d] grid with <r> rows and <c> cols [filled with / of <fill>] into <target>
        grid_m1 = re.match(
            r"^create\s+(?:2d\s+)?grid\s+(?:with\s+)?(.+?)\s+rows?\s+and\s+(.+?)\s+col(?:umn)?s?(?:\s+(?:filled\s+with|of)\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if grid_m1:
            r = grid_m1.group(1).strip()
            c = grid_m1.group(2).strip()
            fill = grid_m1.group(3).strip() if grid_m1.group(3) else "0"
            target = grid_m1.group(4).strip()
            return f"set {target} to dsa_create_grid({r}, {c}, {fill})"

        # create dp table with <r> rows and <c> cols [filled with <fill>] into <target>
        dp_m = re.match(
            r"^create\s+dp\s+table\s+(?:with\s+)?(.+?)\s+rows?\s+and\s+(.+?)\s+col(?:umn)?s?(?:\s+(?:filled\s+with|of)\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if dp_m:
            r = dp_m.group(1).strip()
            c = dp_m.group(2).strip()
            fill = dp_m.group(3).strip() if dp_m.group(3) else "0"
            target = dp_m.group(4).strip()
            return f"set {target} to dsa_create_grid({r}, {c}, {fill})"

        # find [4-way|8-way] connected components in <grid> where cell is <val> into <target>
        find_cc_m = re.match(
            r"^find\s+(?:(4-way|8-way)\s+)?connected\s+components\s+in\s+([A-Za-z_]\w*)\s+where\s+cell\s+is\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if find_cc_m:
            conn = 8 if find_cc_m.group(1) and "8" in find_cc_m.group(1) else 4
            grid_var = find_cc_m.group(2).strip()
            cell_val = find_cc_m.group(3).strip()
            target = find_cc_m.group(4).strip()
            return f"set {target} to dsa_connected_components_grid({grid_var}, {cell_val}, {conn})"

        # count [4-way|8-way] connected components in <grid> where cell is <val> into <target>
        count_cc_m = re.match(
            r"^count\s+(?:(4-way|8-way)\s+)?connected\s+components\s+in\s+([A-Za-z_]\w*)\s+where\s+cell\s+is\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if count_cc_m:
            conn = 8 if count_cc_m.group(1) and "8" in count_cc_m.group(1) else 4
            grid_var = count_cc_m.group(2).strip()
            cell_val = count_cc_m.group(3).strip()
            target = count_cc_m.group(4).strip()
            return f"set {target} to dsa_count_connected_components_grid({grid_var}, {cell_val}, {conn})"

        # create min/max heap into <target>
        heap_create_m = re.match(
            r"^create\s+(min|max)\s+heap\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if heap_create_m:
            kind = heap_create_m.group(1).lower()
            target = heap_create_m.group(2).strip()
            return f'set {target} to dsa_create_heap("{kind}")'

        # create deque/queue into <target>
        deque_create_m = re.match(
            r"^create\s+(?:deque|queue)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if deque_create_m:
            target = deque_create_m.group(1).strip()
            return f"set {target} to dsa_create_deque()"

        # peek min from <coll> into <target>
        peek_min_m = re.match(
            r"^peek\s+min(?:imum)?\s+from\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if peek_min_m:
            coll = peek_min_m.group(1).strip()
            target = peek_min_m.group(2).strip()
            return f"set {target} to dsa_peek_min({coll})"

        # peek max from <coll> into <target>
        peek_max_m = re.match(
            r"^peek\s+max(?:imum)?\s+from\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if peek_max_m:
            coll = peek_max_m.group(1).strip()
            target = peek_max_m.group(2).strip()
            return f"set {target} to dsa_peek_max({coll})"

        # peek left/first from <coll> into <target>
        peek_left_m = re.match(
            r"^peek\s+(?:left|first)\s+from\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if peek_left_m:
            coll = peek_left_m.group(1).strip()
            target = peek_left_m.group(2).strip()
            return f"set {target} to dsa_peek_left({coll})"

        # pop right/last from <coll> into <target>
        pop_right_m = re.match(
            r"^pop\s+(?:right|last)\s+from\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if pop_right_m:
            coll = pop_right_m.group(1).strip()
            target = pop_right_m.group(2).strip()
            return f"set {target} to dsa_pop_right({coll})"

        # push left <item> into <coll>
        push_left_m = re.match(
            r"^push\s+left\s+(.+?)\s+(?:into|to)\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if push_left_m:
            item = push_left_m.group(1).strip()
            coll = push_left_m.group(2).strip()
            return f"dsa_push_left({coll}, {item})"

        # build [directed|undirected] graph from <edges> into <target>
        build_g_m = re.match(
            r"^build\s+(?:(directed|undirected)\s+)?graph\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if build_g_m:
            kind_str = build_g_m.group(1).lower() if build_g_m.group(1) else "directed"
            directed_bool = "false" if kind_str == "undirected" else "true"
            edges = build_g_m.group(2).strip()
            target = build_g_m.group(3).strip()
            return f"set {target} to dsa_build_graph({edges}, {directed_bool})"

        # [check if] <g> has cycle into <target>
        cycle_m = re.match(
            r"^(?:check\s+if\s+)?([A-Za-z_]\w*)\s+has\s+cycle\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if cycle_m:
            g = cycle_m.group(1).strip()
            target = cycle_m.group(2).strip()
            return f"set {target} to dsa_graph_has_cycle({g})"

        # topological sort/order of <g> into <target>
        topo_m = re.match(
            r"^topological\s+(?:sort|order)\s+of\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if topo_m:
            g = topo_m.group(1).strip()
            target = topo_m.group(2).strip()
            return f"set {target} to dsa_graph_topological_sort({g})"

        # shortest path in <g> from <start> to <end> into <target>
        sp_m = re.match(
            r"^shortest\s+path\s+in\s+([A-Za-z_]\w*)\s+from\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if sp_m:
            g = sp_m.group(1).strip()
            start = sp_m.group(2).strip()
            end = sp_m.group(3).strip()
            target = sp_m.group(4).strip()
            return f"set {target} to dsa_graph_shortest_path({g}, {start}, {end})"

        # connected components of <g> into <target>
        g_cc_m = re.match(
            r"^connected\s+components\s+of\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if g_cc_m:
            g = g_cc_m.group(1).strip()
            target = g_cc_m.group(2).strip()
            return f"set {target} to dsa_graph_connected_components({g})"

        # memoize [function] <fn>
        mem_m = re.match(
            r"^memoize\s+(?:function\s+)?([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if mem_m:
            fn = mem_m.group(1).strip()
            return f'set {fn} to dsa_memoize("{fn}")'

        # merge overlapping intervals in <intervals> into <target>
        merge_int_m = re.match(
            r"^merge\s+overlapping\s+intervals\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if merge_int_m:
            intervals = merge_int_m.group(1).strip()
            target = merge_int_m.group(2).strip()
            return f"set {target} to dsa_merge_intervals({intervals})"

        # intersect intervals <a> and <b> into <target>
        intersect_int_m = re.match(
            r"^intersect\s+intervals\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if intersect_int_m:
            a = intersect_int_m.group(1).strip()
            b = intersect_int_m.group(2).strip()
            target = intersect_int_m.group(3).strip()
            return f"set {target} to dsa_intersect_intervals({a}, {b})"

        # frequency map / frequencies of <coll> into <target>
        freq_m = re.match(
            r"^(?:frequency\s+map|frequencies)\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if freq_m:
            coll = freq_m.group(1).strip()
            target = freq_m.group(2).strip()
            return f"set {target} to dsa_frequency_map({coll})"

        # sliding window maximum of <arr> with size <k> into <target>
        sw_m = re.match(
            r"^sliding\s+window\s+maximum\s+of\s+(.+?)\s+with\s+size\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if sw_m:
            arr = sw_m.group(1).strip()
            k = sw_m.group(2).strip()
            target = sw_m.group(3).strip()
            return f"set {target} to dsa_sliding_window_max({arr}, {k})"

        # push <item> into heap <heap>
        heap_push_m = re.match(
            r"^push\s+(.+?)\s+(?:into|to)\s+heap\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if heap_push_m:
            item = heap_push_m.group(1).strip()
            heap_var = heap_push_m.group(2).strip()
            return f"dsa_heap_push({heap_var}, {item})"

        # push <item> into <container>
        push_m = re.match(
            r"^push\s+(.+?)\s+(?:into|to)\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if push_m:
            item = push_m.group(1).strip()
            container = push_m.group(2).strip()
            return f"dsa_push({container}, {item})"

        # pop min from <heap> into <target>
        pop_min_m = re.match(
            r"^pop\s+min(?:imum)?\s+from\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if pop_min_m:
            heap_var = pop_min_m.group(1).strip()
            target = pop_min_m.group(2).strip()
            return f"set {target} to dsa_heap_pop_min({heap_var})"

        # pop max from <heap> into <target>
        pop_max_m = re.match(
            r"^pop\s+max(?:imum)?\s+from\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if pop_max_m:
            heap_var = pop_max_m.group(1).strip()
            target = pop_max_m.group(2).strip()
            return f"set {target} to dsa_heap_pop_max({heap_var})"

        # pop left/first from <deque> into <target>
        pop_left_m = re.match(
            r"^pop\s+(?:left|first)\s+from\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if pop_left_m:
            q_var = pop_left_m.group(1).strip()
            target = pop_left_m.group(2).strip()
            return f"set {target} to dsa_deque_pop_left({q_var})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[BenchmarkSpec, str]:
        # benchmark <fn_name> [into <target>]:
        m = re.match(
            r"^benchmark\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?:?$",
            header.strip(),
            re.IGNORECASE,
        )
        if not m:
            raise SyntaxError(f"Invalid benchmark header: {header}")

        fn_name = m.group(1)
        target = m.group(2) or f"{fn_name}_benchmark"

        spec = BenchmarkSpec(fn_name=fn_name, target_var=target)

        for l_no, raw_line in body_lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # input_sizes: [100, 1000, 10000]
            sizes_m = re.match(r"^input_sizes\s*:\s*\[(.*?)\]", line, re.IGNORECASE)
            if sizes_m:
                raw_nums = sizes_m.group(1).split(",")
                spec.input_sizes = [int(s.strip()) for s in raw_nums if s.strip()]
                continue

            # repeat: <n>
            rep_m = re.match(r"^repeat\s*:\s*(\d+)", line, re.IGNORECASE)
            if rep_m:
                spec.repeat = int(rep_m.group(1))
                continue

            # measure: execution_time, memory
            meas_m = re.match(r"^measure\s*:\s*(.+)$", line, re.IGNORECASE)
            if meas_m:
                spec.measure_memory = "memory" in meas_m.group(1).lower()
                continue

            # generator: <gen>
            gen_m = re.match(r"^generator\s*:\s*([A-Za-z_]\w*)$", line, re.IGNORECASE)
            if gen_m:
                spec.generator = gen_m.group(1).lower()
                continue

        errors = spec.validate()
        if errors:
            raise SyntaxError(f"Benchmark validation error for '{fn_name}': {'; '.join(errors)}")

        return spec, target
