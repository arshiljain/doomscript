"""AI Agents & Multi-Agent Workflows Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.agent.spec import AgentSpec, TaskSpec, TeamSpec
from doomscript.domains.agent.parser import AgentDomainParser
from doomscript.domains.agent.runtime import (
    Agent,
    AgentTeam,
    AgentRuntime,
    create_agent,
    create_team,
    ask_agent,
    tell_agent,
    clear_agent_memory,
    agent_memory,
    run_team,
    execute_agent_ir,
)
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.agent.exporter import AgentASTExporter
from doomscript.domains.registry import get_domain_registry


class AgentDomain(DomainContract):
    """AI Agents & Multi-Agent Workflows domain pack."""

    name = "agent"
    aliases = ["agents", "multiagent", "ai_agent"]
    description = "AI Agents, LLM system prompts, memory contexts, tools, and multi-agent teams"
    parser = AgentDomainParser()
    runtime = AgentRuntime()
    exporter = AgentASTExporter()
    capabilities = ["agent", "memory", "tools", "teams", "reasoning"]
    optional_dependencies = ["google-genai", "openai"]

    verbs = [
        VerbSpec(
            name="create_agent",
            pattern="create agent {role:expr} [with tools {tools:expr}] into {target:ident}",
            arg_schema={"role": "expr", "target": "ident"},
            returns="Agent",
            description="Instantiate autonomous AI agent with role and tools",
        ),
        VerbSpec(
            name="ask_agent",
            pattern="ask agent {agent_var:ident} {prompt:expr} into {target:ident}",
            arg_schema={"agent_var": "ident", "prompt": "expr", "target": "ident"},
            returns="str",
            description="Send conversational prompt to agent and receive reply",
        ),
        VerbSpec(
            name="tell_agent",
            pattern="tell agent {agent_var:ident} {message:expr}",
            arg_schema={"agent_var": "ident", "message": "expr"},
            returns="None",
            description="Append information to agent conversational memory without expecting response",
        ),
        VerbSpec(
            name="create_team",
            pattern="create team {name:expr} with agents {agents:expr} into {target:ident}",
            arg_schema={"name": "expr", "agents": "expr", "target": "ident"},
            returns="AgentTeam",
            description="Form multi-agent collaborative team",
        ),
        VerbSpec(
            name="run_team",
            pattern="run team {team_var:ident} on {task:expr} into {target:ident}",
            arg_schema={"team_var": "ident", "task": "expr", "target": "ident"},
            returns="Record",
            description="Execute multi-agent collaborative task execution workflow",
        ),
        VerbSpec(
            name="agent_memory",
            pattern="memory of agent {agent_var:ident} into {target:ident}",
            arg_schema={"agent_var": "ident", "target": "ident"},
            returns="Collection",
            description="Retrieve conversation message history from agent",
        ),
        VerbSpec(
            name="clear_memory",
            pattern="clear memory of agent {agent_var:ident}",
            arg_schema={"agent_var": "ident"},
            returns="None",
            description="Reset agent context window and memory",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("create agent ")
            or s.startswith("ask agent ")
            or s.startswith("tell agent ")
            or s.startswith("create team ")
            or s.startswith("run team ")
            or s.startswith("clear memory of agent ")
            or s.startswith("memory of agent ")
        )

    def can_handle_block(self, header: str) -> bool:
        s = header.strip().lower()
        return s.startswith("define agent ") and (":" in s)


# Register with central registry
AGENT_DOMAIN = AgentDomain()
get_domain_registry().register(AGENT_DOMAIN)

__all__ = [
    "AgentDomain",
    "AGENT_DOMAIN",
    "AgentSpec",
    "TaskSpec",
    "TeamSpec",
    "AgentDomainParser",
    "AgentRuntime",
    "AgentASTExporter",
    "Agent",
    "AgentTeam",
    "create_agent",
    "create_team",
    "ask_agent",
    "tell_agent",
    "clear_agent_memory",
    "agent_memory",
    "run_team",
    "execute_agent_ir",
]
