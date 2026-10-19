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
from doomscript.domains.agent.exporter import AgentASTExporter
from doomscript.domains.registry import get_domain_registry


class AgentDomain(DomainContract):
    """AI Agents & Multi-Agent Workflows domain pack."""

    name = "agent"
    aliases = ["agents", "multiagent", "ai_agent"]
    parser = AgentDomainParser()
    runtime = AgentRuntime()
    exporter = AgentASTExporter()

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
