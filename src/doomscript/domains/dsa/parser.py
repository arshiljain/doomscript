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

        # --- 13 Additional Algorithmic Powers ---

        # 1. Trie Engine
        trie_c_m = re.match(r"^create\s+trie\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if trie_c_m:
            return f"set {trie_c_m.group(1).strip()} to dsa_create_trie()"

        trie_ins_m = re.match(r"^insert\s+(?:word\s+)?(.+?)\s+into\s+(?:trie\s+)?([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if trie_ins_m:
            return f"dsa_trie_insert({trie_ins_m.group(2).strip()}, {trie_ins_m.group(1).strip()})"

        trie_has_m = re.match(r"^(?:check\s+if\s+)?(?:trie\s+)?([A-Za-z_]\w*)\s+contains\s+(?:word\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if trie_has_m:
            return f"set {trie_has_m.group(3).strip()} to dsa_trie_contains({trie_has_m.group(1).strip()}, {trie_has_m.group(2).strip()})"

        trie_sw_m = re.match(r"^(?:check\s+if\s+)?(?:trie\s+)?([A-Za-z_]\w*)\s+starts\s+with\s+(?:prefix\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if trie_sw_m:
            return f"set {trie_sw_m.group(3).strip()} to dsa_trie_starts_with({trie_sw_m.group(1).strip()}, {trie_sw_m.group(2).strip()})"

        trie_aw_m = re.match(r"^all\s+words\s+in\s+(?:trie\s+)?([A-Za-z_]\w*)\s+starting\s+with\s+(?:prefix\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if trie_aw_m:
            return f"set {trie_aw_m.group(3).strip()} to dsa_trie_words_with_prefix({trie_aw_m.group(1).strip()}, {trie_aw_m.group(2).strip()})"

        # 2. Disjoint Set Union (DSU / Union-Find)
        dsu_c_m = re.match(r"^create\s+disjoint\s+set\s+with\s+size\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if dsu_c_m:
            return f"set {dsu_c_m.group(2).strip()} to dsa_create_disjoint_set({dsu_c_m.group(1).strip()})"

        dsu_u_m = re.match(r"^union\s+(.+?)\s+and\s+(.+?)\s+in\s+(?:disjoint\s+set\s+)?([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if dsu_u_m:
            return f"dsa_dsu_union({dsu_u_m.group(3).strip()}, {dsu_u_m.group(1).strip()}, {dsu_u_m.group(2).strip()})"

        dsu_f_m = re.match(r"^find\s+root\s+of\s+(.+?)\s+in\s+(?:disjoint\s+set\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if dsu_f_m:
            return f"set {dsu_f_m.group(3).strip()} to dsa_dsu_find({dsu_f_m.group(2).strip()}, {dsu_f_m.group(1).strip()})"

        dsu_conn_m = re.match(r"^(?:check\s+if\s+)?(.+?)\s+and\s+(.+?)\s+are\s+connected\s+in\s+(?:disjoint\s+set\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if dsu_conn_m:
            return f"set {dsu_conn_m.group(4).strip()} to dsa_dsu_connected({dsu_conn_m.group(3).strip()}, {dsu_conn_m.group(1).strip()}, {dsu_conn_m.group(2).strip()})"

        dsu_cnt_m = re.match(r"^count\s+of\s+disjoint\s+sets\s+in\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if dsu_cnt_m:
            return f"set {dsu_cnt_m.group(2).strip()} to dsa_dsu_count({dsu_cnt_m.group(1).strip()})"

        # 3. Binary Tree Operations
        bt_b_m = re.match(r"^build\s+binary\s+tree\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if bt_b_m:
            return f"set {bt_b_m.group(2).strip()} to dsa_build_binary_tree({bt_b_m.group(1).strip()})"

        bt_lo_m = re.match(r"^level\s+order\s+traversal\s+of\s+(?:tree\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if bt_lo_m:
            return f"set {bt_lo_m.group(2).strip()} to dsa_level_order({bt_lo_m.group(1).strip()})"

        bt_trav_m = re.match(r"^(preorder|inorder|postorder)\s+traversal\s+of\s+(?:tree\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if bt_trav_m:
            order = bt_trav_m.group(1).lower()
            return f"set {bt_trav_m.group(3).strip()} to dsa_{order}({bt_trav_m.group(2).strip()})"

        bt_dep_m = re.match(r"^maximum\s+depth\s+of\s+(?:tree\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if bt_dep_m:
            return f"set {bt_dep_m.group(2).strip()} to dsa_tree_max_depth({bt_dep_m.group(1).strip()})"

        bt_inv_m = re.match(r"^invert\s+binary\s+tree\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if bt_inv_m:
            return f"set {bt_inv_m.group(1).strip()} to dsa_invert_binary_tree({bt_inv_m.group(1).strip()})"

        # 4. Binary Search / Bisect Suite
        bs_m = re.match(r"^binary\s+search\s+target\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if bs_m:
            return f"set {bs_m.group(3).strip()} to dsa_binary_search({bs_m.group(2).strip()}, {bs_m.group(1).strip()})"

        lb_m = re.match(r"^lower\s+bound\s+of\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if lb_m:
            return f"set {lb_m.group(3).strip()} to dsa_lower_bound({lb_m.group(2).strip()}, {lb_m.group(1).strip()})"

        ub_m = re.match(r"^upper\s+bound\s+of\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if ub_m:
            return f"set {ub_m.group(3).strip()} to dsa_upper_bound({ub_m.group(2).strip()}, {ub_m.group(1).strip()})"

        # 5. Monotonic Stack Engine
        nge_m = re.match(r"^next\s+greater\s+elements\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if nge_m:
            return f"set {nge_m.group(2).strip()} to dsa_next_greater_elements({nge_m.group(1).strip()})"

        nse_m = re.match(r"^next\s+smaller\s+elements\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if nse_m:
            return f"set {nse_m.group(2).strip()} to dsa_next_smaller_elements({nse_m.group(1).strip()})"

        pge_m = re.match(r"^previous\s+greater\s+elements\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if pge_m:
            return f"set {pge_m.group(2).strip()} to dsa_previous_greater_elements({pge_m.group(1).strip()})"

        # 6. Combinatorics & Power Set
        perm_m = re.match(r"^all\s+permutations\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if perm_m:
            return f"set {perm_m.group(2).strip()} to dsa_permutations({perm_m.group(1).strip()})"

        comb_m = re.match(r"^all\s+combinations\s+of\s+(.+?)\s+with\s+size\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if comb_m:
            return f"set {comb_m.group(3).strip()} to dsa_combinations({comb_m.group(1).strip()}, {comb_m.group(2).strip()})"

        pow_m = re.match(r"^power\s+set\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if pow_m:
            return f"set {pow_m.group(2).strip()} to dsa_power_set({pow_m.group(1).strip()})"

        # 7. Linked List Engine
        ll_b_m = re.match(r"^build\s+linked\s+list\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if ll_b_m:
            return f"set {ll_b_m.group(2).strip()} to dsa_build_linked_list({ll_b_m.group(1).strip()})"

        ll_r_m = re.match(r"^reverse\s+linked\s+list\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if ll_r_m:
            return f"set {ll_r_m.group(2).strip()} to dsa_reverse_linked_list({ll_r_m.group(1).strip()})"

        ll_c_m = re.match(r"^(?:check\s+if\s+)?linked\s+list\s+([A-Za-z_]\w*)\s+has\s+cycle\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if ll_c_m:
            return f"set {ll_c_m.group(2).strip()} to dsa_linked_list_has_cycle({ll_c_m.group(1).strip()})"

        ll_t_m = re.match(r"^convert\s+linked\s+list\s+([A-Za-z_]\w*)\s+to\s+list\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if ll_t_m:
            return f"set {ll_t_m.group(2).strip()} to dsa_linked_list_to_list({ll_t_m.group(1).strip()})"

        # 8. Kadane's Algorithm
        kad_s_m = re.match(r"^maximum\s+subarray\s+sum\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if kad_s_m:
            return f"set {kad_s_m.group(2).strip()} to dsa_max_subarray_sum({kad_s_m.group(1).strip()})"

        kad_a_m = re.match(r"^maximum\s+subarray\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if kad_a_m:
            return f"set {kad_a_m.group(2).strip()} to dsa_max_subarray({kad_a_m.group(1).strip()})"

        # 9. Prefix Sums & 2D Prefix Sums
        pref_m = re.match(r"^prefix\s+sums\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if pref_m:
            return f"set {pref_m.group(2).strip()} to dsa_prefix_sums({pref_m.group(1).strip()})"

        rs_m = re.match(r"^range\s+sum\s+in\s+([A-Za-z_]\w*)\s+from\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if rs_m:
            return f"set {rs_m.group(4).strip()} to dsa_range_sum({rs_m.group(1).strip()}, {rs_m.group(2).strip()}, {rs_m.group(3).strip()})"

        pref2d_m = re.match(r"^create\s+2d\s+prefix\s+sums\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if pref2d_m:
            return f"set {pref2d_m.group(2).strip()} to dsa_prefix_sums_2d({pref2d_m.group(1).strip()})"

        q2d_m = re.match(r"^query\s+2d\s+range\s+sum\s+in\s+([A-Za-z_]\w*)\s+from\s+(.+?),\s*(.+?)\s+to\s+(.+?),\s*(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if q2d_m:
            return f"set {q2d_m.group(6).strip()} to dsa_query_range_sum_2d({q2d_m.group(1).strip()}, {q2d_m.group(2).strip()}, {q2d_m.group(3).strip()}, {q2d_m.group(4).strip()}, {q2d_m.group(5).strip()})"

        # 10. Two-Pointer Pairs & Triplets
        pair_m = re.match(r"^find\s+pair\s+with\s+sum\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if pair_m:
            return f"set {pair_m.group(3).strip()} to dsa_find_pair_sum({pair_m.group(2).strip()}, {pair_m.group(1).strip()})"

        trip_m = re.match(r"^find\s+all\s+triplets\s+with\s+sum\s+(.+?)\s+in\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if trip_m:
            return f"set {trip_m.group(3).strip()} to dsa_find_triplets_sum({trip_m.group(2).strip()}, {trip_m.group(1).strip()})"

        # 11. Minimum Spanning Tree (MST)
        mst_w_m = re.match(r"^minimum\s+spanning\s+tree\s+weight\s+of\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if mst_w_m:
            return f"set {mst_w_m.group(2).strip()} to dsa_minimum_spanning_tree_weight({mst_w_m.group(1).strip()})"

        mst_m = re.match(r"^minimum\s+spanning\s+tree\s+of\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if mst_m:
            return f"set {mst_m.group(2).strip()} to dsa_minimum_spanning_tree({mst_m.group(1).strip()})"

        # 12. Knapsack & Coin Change
        knap_m = re.match(r"^solve\s+0-1\s+knapsack\s+with\s+weights\s+(.+?),\s*values\s+(.+?),\s*capacity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if knap_m:
            return f"set {knap_m.group(4).strip()} to dsa_solve_knapsack_01({knap_m.group(1).strip()}, {knap_m.group(2).strip()}, {knap_m.group(3).strip()})"

        coins_m = re.match(r"^minimum\s+coins\s+to\s+make\s+(.+?)\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if coins_m:
            return f"set {coins_m.group(3).strip()} to dsa_min_coins({coins_m.group(2).strip()}, {coins_m.group(1).strip()})"

        ways_m = re.match(r"^count\s+ways\s+to\s+make\s+(.+?)\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if ways_m:
            return f"set {ways_m.group(3).strip()} to dsa_coin_change_ways({ways_m.group(2).strip()}, {ways_m.group(1).strip()})"

        # 13. String Palindromes & KMP
        kmp_m = re.match(r"^find\s+pattern\s+(.+?)\s+in\s+(.+?)\s+using\s+kmp\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if kmp_m:
            return f"set {kmp_m.group(3).strip()} to dsa_kmp_search({kmp_m.group(2).strip()}, {kmp_m.group(1).strip()})"

        lps_m = re.match(r"^longest\s+palindromic\s+substring\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if lps_m:
            return f"set {lps_m.group(2).strip()} to dsa_longest_palindromic_substring({lps_m.group(1).strip()})"

        pal_m = re.match(r"^(?:check\s+if\s+)?(.+?)\s+is\s+palindrome\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if pal_m:
            return f"set {pal_m.group(2).strip()} to dsa_is_palindrome({pal_m.group(1).strip()})"

        # 14. Segment Tree Operations
        st_c_m = re.match(r"^create\s+segment\s+tree\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if st_c_m:
            return f"set {st_c_m.group(2).strip()} to dsa_create_segment_tree({st_c_m.group(1).strip()})"

        st_q_m = re.match(r"^query\s+range\s+sum\s+in\s+segment\s+tree\s+([A-Za-z_]\w*)\s+from\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if st_q_m:
            return f"set {st_q_m.group(4).strip()} to dsa_segment_tree_query({st_q_m.group(1).strip()}, {st_q_m.group(2).strip()}, {st_q_m.group(3).strip()})"

        st_u_m = re.match(r"^update\s+point\s+in\s+segment\s+tree\s+([A-Za-z_]\w*)\s+at\s+(.+?)\s+with\s+(.+)$", line.strip(), re.IGNORECASE)
        if st_u_m:
            return f"dsa_segment_tree_update({st_u_m.group(1).strip()}, {st_u_m.group(2).strip()}, {st_u_m.group(3).strip()})"

        # 15. Fenwick Tree (Binary Indexed Tree)
        fen_c_m = re.match(r"^create\s+fenwick\s+tree\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if fen_c_m:
            return f"set {fen_c_m.group(2).strip()} to dsa_create_fenwick_tree({fen_c_m.group(1).strip()})"

        fen_q_m = re.match(r"^prefix\s+sum\s+in\s+fenwick\s+tree\s+([A-Za-z_]\w*)\s+up\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if fen_q_m:
            return f"set {fen_q_m.group(3).strip()} to dsa_fenwick_prefix_sum({fen_q_m.group(1).strip()}, {fen_q_m.group(2).strip()})"

        fen_u_m = re.match(r"^update\s+fenwick\s+tree\s+([A-Za-z_]\w*)\s+at\s+(.+?)\s+by\s+(.+)$", line.strip(), re.IGNORECASE)
        if fen_u_m:
            return f"dsa_fenwick_update({fen_u_m.group(1).strip()}, {fen_u_m.group(2).strip()}, {fen_u_m.group(3).strip()})"

        # 16. Reservoir Sampling & LCS
        res_m = re.match(r"^sample\s+(.+?)\s+items\s+from\s+stream\s+(.+?)\s+using\s+reservoir\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if res_m:
            return f"set {res_m.group(3).strip()} to dsa_reservoir_sample({res_m.group(2).strip()}, {res_m.group(1).strip()})"

        lcs_m = re.match(r"^longest\s+common\s+subsequence\s+of\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if lcs_m:
            return f"set {lcs_m.group(3).strip()} to dsa_lcs({lcs_m.group(1).strip()}, {lcs_m.group(2).strip()})"

        # 17. Math & Statistics Operations
        corr_m = re.match(r"^correlation\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if corr_m:
            return f"set {corr_m.group(3).strip()} to dsa_correlation({corr_m.group(1).strip()}, {corr_m.group(2).strip()})"

        reg_m = re.match(r"^linear\s+regression\s+of\s+(.+?)\s+on\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if reg_m:
            return f"set {reg_m.group(3).strip()} to dsa_linear_regression({reg_m.group(1).strip()}, {reg_m.group(2).strip()})"

        mmed_m = re.match(r"^moving\s+median\s+of\s+(.+?)\s+with\s+window\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if mmed_m:
            return f"set {mmed_m.group(3).strip()} to dsa_moving_median({mmed_m.group(1).strip()}, {mmed_m.group(2).strip()})"

        pct_m = re.match(r"^percentile\s+(.+?)\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if pct_m:
            return f"set {pct_m.group(3).strip()} to dsa_percentile({pct_m.group(2).strip()}, {pct_m.group(1).strip()})"

        z_m = re.match(r"^z-score\s+normalize\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if z_m:
            return f"set {z_m.group(2).strip()} to dsa_z_score_normalize({z_m.group(1).strip()})"

        mms_m = re.match(r"^min-max\s+scale\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if mms_m:
            return f"set {mms_m.group(2).strip()} to dsa_min_max_scale({mms_m.group(1).strip()})"

        ecdf_m = re.match(r"^empirical\s+cdf\s+of\s+(.+?)\s+at\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if ecdf_m:
            return f"set {ecdf_m.group(3).strip()} to dsa_empirical_cdf({ecdf_m.group(1).strip()}, {ecdf_m.group(2).strip()})"

        # 18. Advanced DSA 350-Expansion Verbs
        # Prefix Tree (Trie)
        trie_cr_m = re.match(r"^create\s+(?:prefix\s+tree|trie)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if trie_cr_m:
            return f"set {trie_cr_m.group(1).strip()} to dsa_trie_create()"

        trie_ins_m = re.match(r"^insert\s+word\s+(.+?)\s+into\s+(?:prefix\s+tree|trie)\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if trie_ins_m:
            return f"dsa_trie_insert({trie_ins_m.group(2).strip()}, {trie_ins_m.group(1).strip()})"

        trie_srch_m = re.match(r"^search\s+word\s+(.+?)\s+in\s+(?:prefix\s+tree|trie)\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if trie_srch_m:
            return f"set {trie_srch_m.group(3).strip()} to dsa_trie_search({trie_srch_m.group(2).strip()}, {trie_srch_m.group(1).strip()})"

        trie_sw_m = re.match(r"^check\s+if\s+(?:prefix\s+tree|trie)\s+([A-Za-z_]\w*)\s+starts\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if trie_sw_m:
            return f"set {trie_sw_m.group(3).strip()} to dsa_trie_starts_with({trie_sw_m.group(1).strip()}, {trie_sw_m.group(2).strip()})"

        # Disjoint Set Union (DSU / Union-Find)
        dsu_cr_m = re.match(r"^create\s+(?:disjoint\s+set|union\s+find)\s+with\s+size\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if dsu_cr_m:
            return f"set {dsu_cr_m.group(2).strip()} to dsa_dsu_create({dsu_cr_m.group(1).strip()})"

        dsu_find_m = re.match(r"^find\s+root\s+of\s+(.+?)\s+in\s+(?:disjoint\s+set|union\s+find)\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if dsu_find_m:
            return f"set {dsu_find_m.group(3).strip()} to dsa_dsu_find({dsu_find_m.group(2).strip()}, {dsu_find_m.group(1).strip()})"

        dsu_u_m = re.match(r"^union\s+sets\s+(.+?)\s+and\s+(.+?)\s+in\s+(?:disjoint\s+set|union\s+find)\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if dsu_u_m:
            return f"set {dsu_u_m.group(4).strip()} to dsa_dsu_union({dsu_u_m.group(3).strip()}, {dsu_u_m.group(1).strip()}, {dsu_u_m.group(2).strip()})"

        # LRU Cache
        lru_cr_m = re.match(r"^create\s+lru\s+cache\s+with\s+capacity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if lru_cr_m:
            return f"set {lru_cr_m.group(2).strip()} to dsa_lru_create({lru_cr_m.group(1).strip()})"

        lru_get_m = re.match(r"^get\s+key\s+(.+?)\s+from\s+lru\s+cache\s+([A-Za-z_]\w*)(?:\s+with\s+default\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if lru_get_m:
            d_arg = f", default={lru_get_m.group(3).strip()}" if lru_get_m.group(3) else ""
            return f"set {lru_get_m.group(4).strip()} to dsa_lru_get({lru_get_m.group(2).strip()}, {lru_get_m.group(1).strip()}{d_arg})"

        lru_put_m = re.match(r"^put\s+key\s+(.+?)\s+with\s+value\s+(.+?)\s+into\s+lru\s+cache\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if lru_put_m:
            return f"dsa_lru_put({lru_put_m.group(3).strip()}, {lru_put_m.group(1).strip()}, {lru_put_m.group(2).strip()})"

        # Binary Search Variants
        bsl_m = re.match(r"^binary\s+search\s+leftmost\s+(.+?)\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if bsl_m:
            return f"set {bsl_m.group(3).strip()} to dsa_binary_search_left({bsl_m.group(2).strip()}, {bsl_m.group(1).strip()})"

        bsr_m = re.match(r"^binary\s+search\s+rightmost\s+(.+?)\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if bsr_m:
            return f"set {bsr_m.group(3).strip()} to dsa_binary_search_right({bsr_m.group(2).strip()}, {bsr_m.group(1).strip()})"

        # QuickSelect
        qs_m = re.match(r"^quickselect\s+(.+?)(?:th|st|nd|rd)?\s+smallest\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if qs_m:
            return f"set {qs_m.group(3).strip()} to dsa_quickselect({qs_m.group(2).strip()}, {qs_m.group(1).strip()})"

        # 2D Kadane
        kad2_m = re.match(r"^maximum\s+sum\s+2d\s+subgrid\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if kad2_m:
            return f"set {kad2_m.group(2).strip()} to dsa_kadane_2d({kad2_m.group(1).strip()})"

        # Inversion Count
        inv_m = re.match(r"^count\s+inversions\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if inv_m:
            return f"set {inv_m.group(2).strip()} to dsa_count_inversions({inv_m.group(1).strip()})"

        # Permutations
        np_m = re.match(r"^next\s+lexicographical\s+permutation\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if np_m:
            return f"set {np_m.group(2).strip()} to dsa_next_permutation({np_m.group(1).strip()})"

        pp_m = re.match(r"^previous\s+lexicographical\s+permutation\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if pp_m:
            return f"set {pp_m.group(2).strip()} to dsa_prev_permutation({pp_m.group(1).strip()})"

        # Rabin-Karp & Manacher
        rk_m = re.match(r"^rabin\s+karp\s+search\s+for\s+(.+?)\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if rk_m:
            return f"set {rk_m.group(3).strip()} to dsa_rabin_karp_search({rk_m.group(2).strip()}, {rk_m.group(1).strip()})"

        man_m = re.match(r"^longest\s+palindromic\s+substring\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if man_m:
            return f"set {man_m.group(2).strip()} to dsa_manacher({man_m.group(1).strip()})"

        # Bridges
        brg_m = re.match(r"^find\s+bridges\s+in\s+graph\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", line.strip(), re.IGNORECASE)
        if brg_m:
            return f"set {brg_m.group(2).strip()} to dsa_tarjan_bridges({brg_m.group(1).strip()})"

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
