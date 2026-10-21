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
    agent_broadcast_message,
    agent_consensus_vote,
    agent_prioritize_tasks,
    agent_dispatch_task,
    agent_aggregate_responses,
    agent_filter_memory,
    agent_evaluate_response_quality,
    agent_format_chat_history,
    agent_summarize_memory,
    agent_route_task_by_keywords,
    agent_retry_with_backoff,
    agent_validate_json_output,
    agent_extract_action_calls,
    agent_chain_of_thought_step,
    agent_calculate_consensus_agreement,
    agent_debate_round,
    agent_plan_task_breakdown,
    agent_filter_memory_by_date,
    agent_merge_agent_memories,
    agent_register_dynamic_tool,
    agent_inspect_available_tools,
    agent_set_system_persona,
    agent_audit_conversation_safety,
    agent_count_conversation_turns,
    agent_export_chat_transcript,
    ToolHarness,
    AgentMemoryBuffer,
    ReActAgent,
    TreeOfThoughts,
    ToTNode,
    MultiAgentDebate,
    agent_react_run,
    agent_tree_of_thoughts_search,
    agent_run_debate,
    HierarchicalTaskNetworkHTNPlanner,
    MonteCarloTreeSearchMCTS,
    agent_htn_plan,
    agent_mcts_search,
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
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("create agent ")
            or s.startswith("ask agent ")
            or s.startswith("tell agent ")
            or s.startswith("create team ")
            or s.startswith("run team ")
            or s.startswith("clear memory of agent ")
            or s.startswith("memory of agent ")
            or s.startswith("broadcast message ")
            or s.startswith("tally consensus votes ")
            or s.startswith("prioritize agent tasks ")
            or s.startswith("dispatch task ")
            or s.startswith("aggregate agent responses ")
            or s.startswith("filter memory of agent ")
            or s.startswith("evaluate response quality ")
            or s.startswith("format chat history ")
            or s.startswith("summarize memory of ")
            or s.startswith("route task ")
            or s.startswith("retry task ")
            or s.startswith("validate json output ")
            or s.startswith("extract action calls ")
            or s.startswith("chain of thought prompt ")
            or s.startswith("calculate consensus agreement ")
            or s.startswith("debate topic ")
            or s.startswith("plan task breakdown ")
            or s.startswith("filter memory of ")
            or s.startswith("merge memories of ")
            or s.startswith("register tool ")
            or s.startswith("inspect available tools of ")
            or s.startswith("set persona of agent ")
            or s.startswith("audit conversation safety ")
            or s.startswith("count conversation turns ")
            or s.startswith("export chat transcript ")
        )

    def can_handle_block(self, header: str) -> bool:
        s = header.strip().lower()
        return (s.startswith("define agent ") or s.startswith("team ")) and (":" in s)


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
    "agent_broadcast_message",
    "agent_consensus_vote",
    "agent_prioritize_tasks",
    "agent_dispatch_task",
    "agent_aggregate_responses",
    "agent_filter_memory",
    "agent_evaluate_response_quality",
    "agent_format_chat_history",
    "agent_summarize_memory",
    "agent_route_task_by_keywords",
    "agent_retry_with_backoff",
    "agent_validate_json_output",
    "agent_extract_action_calls",
    "agent_chain_of_thought_step",
    "agent_calculate_consensus_agreement",
    "agent_debate_round",
    "agent_plan_task_breakdown",
    "agent_filter_memory_by_date",
    "agent_merge_agent_memories",
    "agent_register_dynamic_tool",
    "agent_inspect_available_tools",
    "agent_set_system_persona",
    "agent_audit_conversation_safety",
    "agent_count_conversation_turns",
    "agent_export_chat_transcript",
    "ToolHarness",
    "AgentMemoryBuffer",
    "ReActAgent",
    "TreeOfThoughts",
    "ToTNode",
    "MultiAgentDebate",
    "agent_react_run",
    "agent_tree_of_thoughts_search",
    "agent_run_debate",
    "HierarchicalTaskNetworkHTNPlanner",
    "MonteCarloTreeSearchMCTS",
    "agent_htn_plan",
    "agent_mcts_search",
]
