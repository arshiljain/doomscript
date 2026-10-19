"""Unit and integration tests for AI Agents & Multi-Agent Workflows domain (use agent)."""

import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.agent.runtime import (
    Agent,
    AgentTeam,
    create_agent,
    create_team,
    ask_agent,
    tell_agent,
    clear_agent_memory,
    agent_memory,
    run_team,
)


def test_agent_runtime_direct():
    analyst = create_agent(
        name="DataAnalyst",
        role="Senior Financial Analyst",
        instructions="Analyze financial metrics concisely",
        model="default",
    )
    assert analyst.name == "DataAnalyst"
    assert analyst.role == "Senior Financial Analyst"
    assert len(analyst.get_memory()) == 0

    # Tell instruction
    tell_agent(analyst, "Q3 budget is $200,000")
    mem = agent_memory(analyst)
    assert len(mem) == 1
    assert mem[0]["content"] == "Q3 budget is $200,000"

    # Ask task
    resp = ask_agent(analyst, "What is our Q3 strategy?", context="Inflation is declining")
    assert resp is not None
    assert len(agent_memory(analyst)) >= 3  # Initial tell + prompt + answer

    # Clear memory
    clear_agent_memory(analyst)
    assert len(agent_memory(analyst)) == 0


def test_agent_team_runtime():
    scout = create_agent("Scout", role="Fact Finder")
    editor = create_agent("Editor", role="Copy Editor")
    team = create_team("EditorialBoard", [scout, editor])

    result = run_team(team, "Summarize global chip industry")
    assert result.team == "EditorialBoard"
    assert len(result.steps) == 2
    assert result.steps[0].agent == "Scout"
    assert result.steps[1].agent == "Editor"
    assert result.final_output is not None


def test_agent_domain_one_liner_execution():
    source = """use agent

create agent Coder with role "Software Architect" into dev
ask agent dev to "Design a key-value store" into design
tell agent dev "Use in-memory LRU cache"
memory of agent dev into dev_mem
"""
    env = execute(source)
    assert "dev" in env
    assert isinstance(env["dev"], Agent)
    assert "design" in env
    assert len(env["dev_mem"]) >= 3


def test_agent_domain_declarative_block_execution():
    source = """use agent

define agent Researcher with role "Market Analyst":
    instructions: "Highlight key market drivers and risks"
    model: "default"
    tools: [search, summarize]

create agent Reviewer with role "Executive Editor" into reviewer

ask agent Researcher to "Analyze battery demand" into analysis
ask agent reviewer to "Polish the findings" with context analysis into polished

create team StrategyUnit with agents [Researcher, reviewer] into unit
run team unit on task "Evaluate solid-state batteries" into report
"""
    env = execute(source)
    assert "Researcher" in env
    assert env["Researcher"].role == "Market Analyst"
    assert "reviewer" in env
    assert "analysis" in env
    assert "polished" in env
    assert "unit" in env
    assert "report" in env
    assert len(env["report"].steps) == 2


def test_agent_domain_python_export():
    source = """use agent

create agent Scout with role "Finder" into s
ask agent s to "Find articles" into articles
"""
    py_code = export_to_python(source)
    assert "create_agent" in py_code
    assert "ask_agent" in py_code
    assert "from doomscript.runtime import *" in py_code
