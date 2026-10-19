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
            as_json = " as json" in s.lower()
            target_var = m_ask.group(4).strip()
            return f"set {target_var} to ask_agent({agent_var}, {task_expr}, context={ctx_expr}, as_json={as_json})"

        # create agent <name> with role <role> [and model <model>] into <target>
        m_agent = re.match(
            r"^create\s+agent\s+([A-Za-z_]\w*)\s+with\s+role\s+(.+?)(?:\s+and\s+model\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_agent:
            name_str = f'"{m_agent.group(1).strip()}"'
            role_expr = m_agent.group(2).strip()
            model_expr = m_agent.group(3).strip() if m_agent.group(3) else '"default"'
            target_var = m_agent.group(4).strip()
            return f"set {target_var} to create_agent({name_str}, role={role_expr}, model={model_expr})"

        # create team <name> with agents <agent_list> into <target>
        m_team = re.match(
            r"^create\s+team\s+([A-Za-z_]\w*)\s+with\s+agents\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_team:
            team_name = f'"{m_team.group(1).strip()}"'
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
            return f"set {target_var} to run_team({team_var}, {task_expr}, context={ctx_expr})"

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
