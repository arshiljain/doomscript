"""Independent Domain Parser for AI Agents & Multi-Agent Workflows."""

import re
from typing import Any, Dict, List, Optional, Tuple
import ast
from doomscript.domains.base import DomainParser
from doomscript.domains.agent.spec import AgentSpec, TaskSpec, TeamSpec
from doomscript.domains.registry import get_domain_registry


class AgentDomainParser(DomainParser):
    """Independent parser for Agent domain syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # memory of agent <agent> into <target>
        m_mem = re.match(
            r"^memory\s+of\s+agent\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mem:
            agent_var = m_mem.group(1).strip()
            target_var = m_mem.group(2).strip()
            return f"set {target_var} to agent_memory({agent_var})"

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        # run debate on topic <topic> [rounds <r>] into <target>
        m_deb = re.match(
            r"^run\s+debate\s+on\s+topic\s+(.+?)(?:\s+rounds\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m_deb:
            top = m_deb.group(1).strip()
            r_val = m_deb.group(2).strip() if m_deb.group(2) else "2"
            target = m_deb.group(3).strip()
            if not (top.startswith('"') or top.startswith("'") or top.isidentifier()):
                top = f'"{top}"'
            return f"set {target} to Record(agent_run_debate({top}, rounds={r_val}))"


        s = line.strip()

        # clear memory of agent <agent>
        m_clr = re.match(
            r"^clear\s+memory\s+of\s+agent\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_clr:
            agent_var = m_clr.group(1).strip()
            return f"clear_agent_memory({agent_var})"

        # tell agent <agent> <message>
        m_tell = re.match(
            r"^tell\s+agent\s+([A-Za-z_]\w*)\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_tell:
            agent_var = m_tell.group(1).strip()
            msg_expr = m_tell.group(2).strip()
            return f"tell_agent({agent_var}, {msg_expr})"

        # ask agent <agent> to <task> [with context <ctx>] [as json] into <target>
        m_ask = re.match(
            r"^ask\s+agent\s+([A-Za-z_]\w*)\s+to\s+(.+?)(?:\s+with\s+context\s+(.+?))?(?:\s+as\s+json)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ask:
            agent_var = m_ask.group(1).strip()
            task_expr = m_ask.group(2).strip()
            ctx_expr = m_ask.group(3).strip() if m_ask.group(3) else "None"
            as_json = "true" if " as json" in s.lower() else "false"
            target_var = m_ask.group(4).strip()
            return f"set {target_var} to ask_agent({agent_var}, {task_expr}, {ctx_expr}, {as_json})"

        # create agent <name> with role <role> [and model <model>] into <target>
        m_agent = re.match(
            r"^create\s+agent\s+(.+?)\s+with\s+role\s+(.+?)(?:\s+and\s+model\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_agent:
            raw_name = m_agent.group(1).strip().strip('"\'')
            name_str = f'"{raw_name}"'
            role_expr = m_agent.group(2).strip()
            model_expr = m_agent.group(3).strip() if m_agent.group(3) else '"default"'
            target_var = m_agent.group(4).strip()
            return f"set {target_var} to create_agent({name_str}, {role_expr}, '', {model_expr})"

        # create agent <role> [with tools <tools>] into <target>
        m_agent_tools = re.match(
            r"^create\s+agent\s+(.+?)(?:\s+with\s+tools\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_agent_tools and " with role " not in s.lower():
            role_expr = m_agent_tools.group(1).strip()
            tools_expr = m_agent_tools.group(2).strip() if m_agent_tools.group(2) else "None"
            target_var = m_agent_tools.group(3).strip()
            return f"set {target_var} to create_agent({role_expr}, {role_expr}, '', 'default', tools={tools_expr})"

        # create team <name> with agents <agent_list> into <target>
        m_team = re.match(
            r"^create\s+team\s+([A-Za-z_]\w*)\s+with\s+agents\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_team:
            team_name = f'"{m_team.group(1).strip().strip(chr(34)).strip(chr(39))}"'
            agents_expr = m_team.group(2).strip()
            target_var = m_team.group(3).strip()
            return f"set {target_var} to create_team({team_name}, {agents_expr})"

        # run team <team> on task <task> [with context <ctx>] into <target>
        m_run_team = re.match(
            r"^run\s+team\s+([A-Za-z_]\w*)\s+on\s+task\s+(.+?)(?:\s+with\s+context\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_run_team:
            team_var = m_run_team.group(1).strip()
            task_expr = m_run_team.group(2).strip()
            ctx_expr = m_run_team.group(3).strip() if m_run_team.group(3) else "None"
            target_var = m_run_team.group(4).strip()
            return f"set {target_var} to run_team({team_var}, {task_expr}, {ctx_expr})"

        # broadcast message <msg> to team/agents <team> into <target>
        m_bcast = re.match(
            r"^broadcast\s+message\s+(.+?)\s+to\s+(?:team|agents)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bcast:
            msg = m_bcast.group(1).strip()
            team = m_bcast.group(2).strip()
            target = m_bcast.group(3).strip()
            return f"set {target} to agent_broadcast_message({team}, {msg})"

        # tally consensus votes from/in <votes> [with threshold <thresh>] into <target>
        m_vote = re.match(
            r"^tally\s+consensus\s+votes\s+(?:from|in)\s+(.+?)(?:\s+with\s+threshold\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vote:
            votes = m_vote.group(1).strip()
            thresh = m_vote.group(2)
            target = m_vote.group(3).strip()
            thresh_arg = f", {thresh.strip()}" if thresh else ", 0.5"
            return f"set {target} to agent_consensus_vote({votes}{thresh_arg})"

        # prioritize agent tasks <tasks> [by <key>] into <target>
        m_prio = re.match(
            r"^prioritize\s+agent\s+tasks\s+(.+?)(?:\s+by\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_prio:
            tasks = m_prio.group(1).strip()
            key = m_prio.group(2)
            target = m_prio.group(3).strip()
            key_arg = f', "{key.strip().strip(chr(34)).strip(chr(39))}"' if key else ""
            return f"set {target} to agent_prioritize_tasks({tasks}{key_arg})"

        # dispatch task <task> to team/agents <team> into <target>
        m_disp = re.match(
            r"^dispatch\s+task\s+(.+?)\s+to\s+(?:team|agents)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_disp:
            task = m_disp.group(1).strip()
            team = m_disp.group(2).strip()
            target = m_disp.group(3).strip()
            return f"set {target} to agent_dispatch_task({team}, {task})"

        # aggregate agent responses <responses> into <target>
        m_agg = re.match(
            r"^aggregate\s+agent\s+responses\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_agg:
            responses = m_agg.group(1).strip()
            target = m_agg.group(2).strip()
            return f"set {target} to agent_aggregate_responses({responses})"

        # filter memory of agent <agent> by <filter> into <target>
        m_filt = re.match(
            r"^filter\s+memory\s+of\s+agent\s+(.+?)\s+by\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_filt:
            agent = m_filt.group(1).strip()
            filt_val = m_filt.group(2).strip()
            target = m_filt.group(3).strip()
            return f"set {target} to agent_filter_memory({agent}, {filt_val})"

        # evaluate response quality of <resp> [with rubric <rubric>] into <target>
        m_erq = re.match(
            r"^evaluate\s+response\s+quality\s+of\s+(.+?)(?:\s+with\s+rubric\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_erq:
            resp, rubric, target = m_erq.group(1).strip(), m_erq.group(2), m_erq.group(3).strip()
            rub_val = rubric.strip() if rubric else "None"
            return f"set {target} to agent_evaluate_response_quality({resp}, {rub_val})"

        # format chat history of <agent> as <style> into <target>
        m_fch = re.match(
            r"^format\s+chat\s+history\s+of\s+(.+?)\s+as\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fch:
            agent, style, target = m_fch.group(1).strip(), m_fch.group(2).strip(), m_fch.group(3).strip()
            return f"set {target} to agent_format_chat_history({agent}, {style})"

        # summarize memory of <agent> [max tokens <max_tok>] into <target>
        m_sm = re.match(
            r"^summarize\s+memory\s+of\s+(.+?)(?:\s+max\s+tokens\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sm:
            agent, tok, target = m_sm.group(1).strip(), m_sm.group(2), m_sm.group(3).strip()
            tok_val = tok.strip() if tok else "500"
            return f"set {target} to agent_summarize_memory({agent}, {tok_val})"

        # route task <task> using skills <skill_map> into <target>
        m_rt = re.match(
            r"^route\s+task\s+(.+?)\s+using\s+skills\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rt:
            task, skill_map, target = m_rt.group(1).strip(), m_rt.group(2).strip(), m_rt.group(3).strip()
            return f"set {target} to agent_route_task_by_keywords({task}, {skill_map})"

        # retry task <task> with agent <agent> [max retries <retries>] into <target>
        m_rwb = re.match(
            r"^retry\s+task\s+(.+?)\s+with\s+agent\s+(.+?)(?:\s+max\s+retries\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rwb:
            task, agent, retries, target = m_rwb.group(1).strip(), m_rwb.group(2).strip(), m_rwb.group(3), m_rwb.group(4).strip()
            ret_val = retries.strip() if retries else "3"
            return f"set {target} to agent_retry_with_backoff({agent}, {task}, {ret_val})"

        # validate json output of <resp> against schema <schema> into <target>
        m_vjo = re.match(
            r"^validate\s+json\s+output\s+of\s+(.+?)\s+against\s+schema\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vjo:
            resp, schema, target = m_vjo.group(1).strip(), m_vjo.group(2).strip(), m_vjo.group(3).strip()
            return f"set {target} to agent_validate_json_output({resp}, {schema})"

        # extract action calls from <resp> into <target>
        m_eac = re.match(
            r"^extract\s+action\s+calls\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_eac:
            resp, target = m_eac.group(1).strip(), m_eac.group(2).strip()
            return f"set {target} to agent_extract_action_calls({resp})"

        # chain of thought prompt for task <task> [with context <ctx>] into <target>
        m_cot = re.match(
            r"^chain\s+of\s+thought\s+prompt\s+for\s+task\s+(.+?)(?:\s+with\s+context\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cot:
            task, ctx, target = m_cot.group(1).strip(), m_cot.group(2), m_cot.group(3).strip()
            ctx_val = ctx.strip() if ctx else "None"
            return f"set {target} to agent_chain_of_thought_step({task}, {ctx_val})"

        # calculate consensus agreement among <responses> into <target>
        m_cca = re.match(
            r"^calculate\s+consensus\s+agreement\s+among\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cca:
            resps, target = m_cca.group(1).strip(), m_cca.group(2).strip()
            return f"set {target} to agent_calculate_consensus_agreement({resps})"

        # debate topic <topic> between <agent1> and <agent2> [for <rounds> rounds] into <target>
        m_deb = re.match(
            r"^debate\s+topic\s+(.+?)\s+between\s+(.+?)\s+and\s+(.+?)(?:\s+for\s+(\d+)\s+rounds)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_deb:
            topic, a1, a2, r_cnt, target = m_deb.group(1).strip(), m_deb.group(2).strip(), m_deb.group(3).strip(), m_deb.group(4), m_deb.group(5).strip()
            rounds_val = r_cnt.strip() if r_cnt else "2"
            return f"set {target} to agent_debate_round({a1}, {a2}, {topic}, {rounds_val})"

        # plan task breakdown for <goal> with agent <agent> into <target>
        m_ptb = re.match(
            r"^plan\s+task\s+breakdown\s+for\s+(.+?)\s+with\s+agent\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ptb:
            goal, agent, target = m_ptb.group(1).strip(), m_ptb.group(2).strip(), m_ptb.group(3).strip()
            return f"set {target} to agent_plan_task_breakdown({agent}, {goal})"

        # filter memory of <agent> from <start_date> to <end_date> into <target>
        m_fmd = re.match(
            r"^filter\s+memory\s+of\s+(.+?)\s+from\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fmd:
            agent, s_date, e_date, target = m_fmd.group(1).strip(), m_fmd.group(2).strip(), m_fmd.group(3).strip(), m_fmd.group(4).strip()
            return f"set {target} to agent_filter_memory_by_date({agent}, {s_date}, {e_date})"

        # merge memories of <agent1> and <agent2> into <target_agent>
        m_mma = re.match(
            r"^merge\s+memories\s+of\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mma:
            a1, a2, target = m_mma.group(1).strip(), m_mma.group(2).strip(), m_mma.group(3).strip()
            return f"agent_merge_agent_memories({a1}, {a2}, {target})"

        # register tool <name> with function <fn> and description <desc> for agent <agent>
        m_rtool = re.match(
            r"^register\s+tool\s+(.+?)\s+with\s+function\s+(.+?)\s+and\s+description\s+(.+?)\s+for\s+agent\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rtool:
            name, fn, desc, agent = m_rtool.group(1).strip(), m_rtool.group(2).strip(), m_rtool.group(3).strip(), m_rtool.group(4).strip()
            return f"agent_register_dynamic_tool({agent}, {name}, {fn}, {desc})"

        # inspect available tools of agent <agent> into <target>
        m_itool = re.match(
            r"^inspect\s+available\s+tools\s+of\s+agent\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_itool:
            agent, target = m_itool.group(1).strip(), m_itool.group(2).strip()
            return f"set {target} to agent_inspect_available_tools({agent})"

        # set persona of agent <agent> to role <role> and instructions <inst>
        m_sp = re.match(
            r"^set\s+persona\s+of\s+agent\s+([A-Za-z_]\w*)\s+to\s+role\s+(.+?)\s+and\s+instructions\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_sp:
            agent, role, inst = m_sp.group(1).strip(), m_sp.group(2).strip(), m_sp.group(3).strip()
            return f"agent_set_system_persona({agent}, {role}, {inst})"

        # audit conversation safety of <history> against <banned_terms> into <target>
        m_acs = re.match(
            r"^audit\s+conversation\s+safety\s+of\s+(.+?)\s+against\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_acs:
            hist, banned, target = m_acs.group(1).strip(), m_acs.group(2).strip(), m_acs.group(3).strip()
            return f"set {target} to agent_audit_conversation_safety({hist}, {banned})"

        # count conversation turns of agent <agent> into <target>
        m_cct = re.match(
            r"^count\s+conversation\s+turns\s+of\s+agent\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cct:
            agent, target = m_cct.group(1).strip(), m_cct.group(2).strip()
            return f"set {target} to agent_count_conversation_turns({agent})"

        # export chat transcript of agent <agent> to <output_file> into <target>
        m_ect = re.match(
            r"^export\s+chat\s+transcript\s+of\s+agent\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ect:
            agent, out_file, target = m_ect.group(1).strip(), m_ect.group(2).strip(), m_ect.group(3).strip()
            return f"set {target} to agent_export_chat_transcript({agent}, {out_file})"

        # plan htn tasks <tasks> state <state> methods <methods> operators <ops> into <target>
        m_htn = re.match(
            r"^plan\s+htn\s+tasks\s+(.+?)\s+state\s+(.+?)\s+methods\s+(.+?)\s+operators\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_htn:
            tasks, state, methods, ops, target = m_htn.group(1).strip(), m_htn.group(2).strip(), m_htn.group(3).strip(), m_htn.group(4).strip(), m_htn.group(5).strip()
            return f"set {target} to agent_htn_plan({tasks}, {state}, {methods}, {ops})"

        # run mcts planning state <state> actions <actions> [iterations <iter>] [exploration <c>] into <target>
        m_mcts = re.match(
            r"^run\s+mcts\s+planning\s+state\s+(.+?)\s+actions\s+(.+?)(?:\s+iterations\s+(\d+))?(?:\s+exploration\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mcts:
            st, acts, iters, expl, target = m_mcts.group(1).strip(), m_mcts.group(2).strip(), m_mcts.group(3), m_mcts.group(4), m_mcts.group(5).strip()
            it_val = iters if iters else "100"
            ex_val = expl.strip() if expl else "1.414"
            return f"set {target} to agent_mcts_search({st}, {acts}, iterations={it_val}, exploration_c={ex_val})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[AgentSpec, str]:
        # define agent <Name> [with role <role>]:
        m = re.match(
            r"^define\s+agent\s+([A-Za-z_]\w*)(?:\s+with\s+role\s+(.+?))?:?$",
            header.strip(),
            re.IGNORECASE,
        )
        if not m:
            raise SyntaxError(f"Invalid agent block header: {header}")

        agent_name = m.group(1).strip()
        role = m.group(2).strip().strip('"\'') if m.group(2) else ""
        instructions = ""
        model = "default"
        tools = []
        memory = True

        for _, raw_line in body_lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            r_m = re.match(r"^role\s*:\s*(.+)$", line, re.IGNORECASE)
            if r_m:
                role = r_m.group(1).strip().strip('"\'')
                continue

            inst_m = re.match(r"^instructions?\s*:\s*(.+)$", line, re.IGNORECASE)
            if inst_m:
                instructions = inst_m.group(1).strip().strip('"\'')
                continue

            mod_m = re.match(r"^model\s*:\s*(.+)$", line, re.IGNORECASE)
            if mod_m:
                model = mod_m.group(1).strip().strip('"\'')
                continue

            tools_m = re.match(r"^tools?\s*:\s*\[(.*)\]$", line, re.IGNORECASE)
            if tools_m:
                items = [t.strip().strip('"\'') for t in tools_m.group(1).split(",") if t.strip()]
                tools.extend(items)
                continue

            mem_m = re.match(r"^memory\s*:\s*(true|false)$", line, re.IGNORECASE)
            if mem_m:
                memory = mem_m.group(1).lower() == "true"
                continue

        spec = AgentSpec(
            name=agent_name,
            role=role,
            instructions=instructions,
            model=model,
            tools=tools,
            memory=memory,
        )
        errors = spec.validate()
        if errors:
            raise SyntaxError(f"Agent validation error: {'; '.join(errors)}")

        return spec, agent_name
