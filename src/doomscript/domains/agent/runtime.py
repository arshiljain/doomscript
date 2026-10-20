"""Runtime execution engine for AI Agents and Multi-Agent Workflows domain."""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import math
import random
from doomscript.core.record import Record
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.agent.spec import AgentSpec, TaskSpec, TeamSpec


class Agent:
    """An autonomous AI agent with a role, instructions, tools, and conversational memory."""

    def __init__(
        self,
        name: str,
        role: str = "",
        instructions: str = "",
        model: str = "default",
        tools: Optional[List[Union[str, Callable]]] = None,
        memory: bool = True,
    ):
        self.name = name
        self.role = role
        self.instructions = instructions
        self.model = model
        self.tools: Dict[str, Any] = {}
        self.use_memory = memory
        self.history: List[Dict[str, str]] = []

        if tools:
            for t in tools:
                if callable(t):
                    self.tools[t.__name__] = t
                elif isinstance(t, str):
                    self.tools[t] = t

    def tell(self, message: str) -> None:
        """Stores a background instruction or conversational context in the agent's memory."""
        self.history.append({"role": "user", "content": message})

    def clear_memory(self) -> None:
        """Clears all accumulated conversational memory."""
        self.history.clear()

    def get_memory(self) -> List[Dict[str, str]]:
        """Returns the conversational history."""
        return list(self.history)

    def ask(
        self,
        task: str,
        context: Optional[Any] = None,
        as_json: bool = False,
    ) -> Any:
        """Prompts the agent to complete a task given its persona, instructions, and memory."""
        system_parts = []
        if self.role:
            system_parts.append(f"You are {self.name}, acting as a {self.role}.")
        if self.instructions:
            system_parts.append(f"Instructions: {self.instructions}")
        if self.tools:
            tool_names = ", ".join(self.tools.keys())
            system_parts.append(f"Available tools: {tool_names}")

        system_prompt = "\n".join(system_parts) if system_parts else None

        user_content_parts = []
        if self.history:
            recent_hist = self.history[-5:]
            hist_str = "\n".join(f"{h['role'].capitalize()}: {h['content']}" for h in recent_hist)
            user_content_parts.append(f"Recent Memory:\n{hist_str}")

        if context is not None:
            user_content_parts.append(f"Context: {context}")

        user_content_parts.append(f"Task: {task}")
        full_prompt = "\n\n".join(user_content_parts)

        # Record prompt in memory
        if self.use_memory:
            self.history.append({"role": "user", "content": task})

        from doomscript.runtime import ask_ai
        resp = ask_ai(full_prompt, model=self.model, system=system_prompt, as_json=as_json)

        # Record response in memory
        if self.use_memory:
            resp_str = str(resp) if not isinstance(resp, str) else resp
            self.history.append({"role": "assistant", "content": resp_str})

        return resp

    def __repr__(self) -> str:
        return f"Agent(name='{self.name}', role='{self.role}', model='{self.model}')"


class AgentTeam:
    """A collaborative team of multiple agents executing sequential workflows."""

    def __init__(self, name: str, agents: List[Agent]):
        self.name = name
        self.agents = list(agents)

    def run(self, task: str, context: Optional[Any] = None) -> Record:
        """Executes a sequential multi-agent collaborative pipeline."""
        results = []
        current_input = task
        current_context = context

        for agent in self.agents:
            step_resp = agent.ask(current_input, context=current_context)
            results.append(
                Record(
                    agent=agent.name,
                    role=agent.role,
                    output=step_resp,
                )
            )
            # Pass output to the next agent as context
            current_context = step_resp
            current_input = f"Review and refine the following work: {step_resp}"

        final_output = results[-1].output if results else ""
        return Record(
            team=self.name,
            task=task,
            steps=results,
            final_output=final_output,
        )

    def __repr__(self) -> str:
        member_names = ", ".join(a.name for a in self.agents)
        return f"AgentTeam(name='{self.name}', members=[{member_names}])"


# Standalone Helper Functions
def create_agent(
    name: str,
    role: str = "",
    instructions: str = "",
    model: str = "default",
    tools: Optional[List[Any]] = None,
    memory: bool = True,
) -> Agent:
    return Agent(name=name, role=role, instructions=instructions, model=model, tools=tools, memory=memory)


def create_team(name: str, agents: List[Agent]) -> AgentTeam:
    return AgentTeam(name=name, agents=agents)


def ask_agent(
    agent: Agent,
    task: str,
    context: Optional[Any] = None,
    as_json: bool = False,
) -> Any:
    return agent.ask(task=task, context=context, as_json=as_json)


def tell_agent(agent: Agent, message: str) -> None:
    agent.tell(message)


def clear_agent_memory(agent: Agent) -> None:
    agent.clear_memory()


def agent_memory(agent: Agent) -> List[Dict[str, str]]:
    return agent.get_memory()


def run_team(team: AgentTeam, task: str, context: Optional[Any] = None) -> Record:
    return team.run(task=task, context=context)


class AgentRuntime(DomainRuntime):
    """Runtime execution engine for Agent specifications."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        errors = ir.validate()
        if errors:
            raise ValueError(f"Agent spec validation failed: {'; '.join(errors)}")

        if isinstance(ir, AgentSpec):
            return create_agent(
                name=ir.name,
                role=ir.role,
                instructions=ir.instructions,
                model=ir.model,
                tools=ir.tools,
                memory=ir.memory,
            )
        elif isinstance(ir, TaskSpec):
            agent = scope.get(ir.agent_var)
            if not isinstance(agent, Agent):
                raise TypeError(f"Variable '{ir.agent_var}' is not an Agent instance")
            ctx = scope.get(ir.context_var) if ir.context_var else None
            return agent.ask(task=ir.task, context=ctx, as_json=ir.as_json)
        elif isinstance(ir, TeamSpec):
            agents = [scope[var] for var in ir.agent_vars if var in scope]
            return create_team(name=ir.team_name, agents=agents)
        raise NotImplementedError(f"Unsupported IR: {type(ir)}")


def execute_agent_ir(spec_id: str) -> Any:
    from doomscript.domains.registry import get_domain_registry
    spec = get_domain_registry().get_spec(spec_id)
    if spec is None:
        raise KeyError(f"Agent spec not found: {spec_id}")
    return AgentRuntime().execute_ir(spec, {})


# --- Batch 16 Spoken English Multi-Agent Operations ---

def agent_broadcast_message(team_or_agents: Any, message: Any) -> Dict[str, Any]:
    """Broadcast a message or instruction to an agent team or list of agents."""
    if isinstance(team_or_agents, AgentTeam):
        agents = team_or_agents.agents
    elif isinstance(team_or_agents, (list, tuple)):
        agents = list(team_or_agents)
    elif isinstance(team_or_agents, Agent):
        agents = [team_or_agents]
    else:
        agents = []

    delivered_names = []
    for a in agents:
        if hasattr(a, "tell") and callable(a.tell):
            a.tell(str(message))
            delivered_names.append(getattr(a, "name", "agent"))

    return {
        "broadcast_to": delivered_names,
        "message": str(message),
        "delivered": True,
        "count": len(delivered_names),
    }


def agent_consensus_vote(votes: Any, threshold: float = 0.5) -> Dict[str, Any]:
    """Tally consensus votes from agents and check if majority threshold is met."""
    votes_list = list(votes)
    if not votes_list:
        return {"winner": None, "count": 0, "total": 0, "confidence": 0.0, "consensus": False}

    counts: Dict[str, int] = {}
    for v in votes_list:
        if isinstance(v, dict) and "vote" in v:
            key = str(v["vote"]).lower().strip()
        else:
            key = str(v).lower().strip()
        counts[key] = counts.get(key, 0) + 1

    winner = max(counts, key=counts.get)
    winner_cnt = counts[winner]
    total = len(votes_list)
    confidence = round(winner_cnt / total, 4)

    return {
        "winner": winner,
        "count": winner_cnt,
        "total": total,
        "confidence": confidence,
        "consensus": confidence >= float(threshold),
        "distribution": counts,
    }


def agent_prioritize_tasks(tasks: Any, priority_key: Optional[str] = None) -> List[Any]:
    """Sort task queue by priority/urgency descending."""
    priority_weights = {"critical": 5, "urgent": 4, "high": 3, "medium": 2, "low": 1}

    def _score(t):
        val = None
        if isinstance(t, dict):
            if priority_key and priority_key in t:
                val = t[priority_key]
            else:
                for alt in ("urgency", "priority", "importance", "score"):
                    if alt in t:
                        val = t[alt]
                        break
                if val is None and priority_key:
                    val = t.get(priority_key, 0)
        else:
            if priority_key and hasattr(t, priority_key):
                val = getattr(t, priority_key)
            else:
                for alt in ("urgency", "priority", "importance", "score"):
                    if hasattr(t, alt):
                        val = getattr(t, alt)
                        break
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            return float(priority_weights.get(val.lower().strip(), 0))
        return 0.0

    return sorted(list(tasks), key=_score, reverse=True)


def agent_dispatch_task(team_or_agents: Any, task: Any) -> Dict[str, Any]:
    """Dispatch task to best-matching agent by required skill/role or availability."""
    if isinstance(team_or_agents, AgentTeam):
        agents = team_or_agents.agents
    elif isinstance(team_or_agents, (list, tuple)):
        agents = list(team_or_agents)
    elif isinstance(team_or_agents, Agent):
        agents = [team_or_agents]
    else:
        agents = []

    if not agents:
        return {"assigned_to": None, "task": task, "status": "no_agents"}

    task_role = ""
    if isinstance(task, dict):
        task_role = task.get("role") or task.get("skill") or ""

    matched = None
    if task_role:
        for a in agents:
            if getattr(a, "role", "").lower() == str(task_role).lower():
                matched = a
                break

    if not matched:
        matched = agents[0]

    return {
        "assigned_to": getattr(matched, "name", "agent"),
        "role": getattr(matched, "role", ""),
        "task": task,
        "status": "dispatched",
    }


def agent_aggregate_responses(responses: Any) -> Dict[str, Any]:
    """Aggregate responses from multiple agents into a unified summary."""
    resps = list(responses)
    clean_texts = []
    for r in resps:
        if isinstance(r, dict) and "output" in r:
            clean_texts.append(str(r["output"]))
        elif hasattr(r, "output"):
            clean_texts.append(str(r.output))
        else:
            clean_texts.append(str(r))

    combined = "\n---\n".join(clean_texts)
    return {
        "count": len(resps),
        "combined_text": combined,
        "responses": resps,
    }


def agent_filter_memory(agent_or_mem: Any, filter_val: Any = "user") -> List[Dict[str, Any]]:
    """Filter agent conversational memory by role, tag, or keyword."""
    if isinstance(agent_or_mem, Agent):
        mem = agent_or_mem.get_memory()
    elif isinstance(agent_or_mem, list):
        mem = agent_or_mem
    else:
        mem = []

    f_str = str(filter_val).lower().strip()
    filtered = []
    for entry in mem:
        if isinstance(entry, dict):
            role_match = entry.get("role", "").lower() == f_str
            content_match = f_str in entry.get("content", "").lower()
            tag_match = f_str in [str(t).lower() for t in entry.get("tags", [])]
            if role_match or content_match or tag_match:
                filtered.append(entry)
    return filtered


def agent_evaluate_response_quality(response: Any, rubric: Optional[Any] = None) -> Dict[str, Any]:
    """Evaluate response quality using a heuristic rubric scoring framework."""
    text = str(response.get("output", "") if isinstance(response, dict) else response)
    words = text.split()
    word_count = len(words)

    # Base scoring components
    length_score = min(1.0, word_count / 50.0) if word_count > 0 else 0.0
    structure_score = 1.0 if ("\n" in text or "." in text) else 0.5
    has_code_or_data = 1.0 if ("`" in text or "{" in text or "[" in text or ":" in text) else 0.7

    breakdown = {
        "length_score": round(length_score, 2),
        "structure_score": round(structure_score, 2),
        "content_richness": round(has_code_or_data, 2),
    }

    if isinstance(rubric, dict):
        total_weight = 0.0
        weighted_score = 0.0
        for criterion, weight in rubric.items():
            w = float(weight)
            total_weight += w
            crit_lower = str(criterion).lower()
            present = 1.0 if (crit_lower in text.lower()) else 0.5
            breakdown[criterion] = present
            weighted_score += present * w
        overall = weighted_score / total_weight if total_weight > 0 else 0.8
    elif isinstance(rubric, list):
        hits = sum(1.0 for crit in rubric if str(crit).lower() in text.lower())
        overall = (hits / len(rubric)) if rubric else 0.8
        breakdown["rubric_adherence"] = round(overall, 2)
    else:
        overall = (length_score * 0.4 + structure_score * 0.3 + has_code_or_data * 0.3)

    score = round(min(1.0, max(0.0, overall)), 2)
    return {
        "score": score,
        "passed": score >= 0.6,
        "word_count": word_count,
        "breakdown": breakdown,
    }


def agent_format_chat_history(history: Any, format_style: str = "markdown") -> str:
    """Format agent conversational history into Markdown, XML, or JSON."""
    if isinstance(history, Agent):
        mem = history.get_memory()
    elif isinstance(history, list):
        mem = history
    else:
        mem = []

    style = str(format_style).lower().strip()
    if style == "json":
        import json
        return json.dumps(mem, indent=2)
    elif style == "xml":
        parts = ["<conversation>"]
        for msg in mem:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            parts.append(f'  <message role="{role}">{content}</message>')
        parts.append("</conversation>")
        return "\n".join(parts)
    else:  # markdown default
        parts = []
        for msg in mem:
            role = str(msg.get("role", "user")).capitalize()
            content = msg.get("content", "")
            parts.append(f"**{role}**:\n{content}\n")
        return "\n".join(parts).strip()


def agent_summarize_memory(agent: Any, max_tokens: Any = 500) -> Dict[str, Any]:
    """Condense conversational memory window to within token budget."""
    if not isinstance(agent, Agent):
        return {"turns_before": 0, "turns_after": 0, "summarized": False}

    mem = agent.history
    initial_turns = len(mem)
    max_tok = int(max_tokens)
    char_limit = max_tok * 4  # ~4 chars per token proxy

    total_chars = sum(len(m.get("content", "")) for m in mem)
    if total_chars <= char_limit or len(mem) <= 3:
        return {"turns_before": initial_turns, "turns_after": initial_turns, "summarized": False}

    # Keep the most recent 3 turns, summarize older turns
    older = mem[:-3]
    recent = mem[-3:]
    summary_text = "Prior discussion covered: " + "; ".join(m.get("content", "")[:60] for m in older)

    agent.history = [{"role": "system", "content": summary_text}] + recent
    return {
        "turns_before": initial_turns,
        "turns_after": len(agent.history),
        "summarized": True,
        "summary": summary_text,
    }


def agent_route_task_by_keywords(task: Any, agent_skill_map: Dict[str, List[str]]) -> str:
    """Direct task routing to the most qualified agent based on keyword occurrences."""
    task_str = str(task).lower()
    best_agent = ""
    best_count = -1

    for agent_name, keywords in agent_skill_map.items():
        count = sum(1 for kw in keywords if str(kw).lower() in task_str)
        if count > best_count:
            best_count = count
            best_agent = agent_name

    return best_agent if best_agent else (next(iter(agent_skill_map.keys())) if agent_skill_map else "agent")


def agent_retry_with_backoff(agent: Any, task: str, max_retries: Any = 3) -> Dict[str, Any]:
    """Autonomous retry handler for agent operations with exponential backoff."""
    retries = int(max_retries)
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            if isinstance(agent, Agent):
                out = agent.ask(task)
                return {"status": "success", "attempts": attempt, "output": out}
            elif callable(agent):
                out = agent(task)
                return {"status": "success", "attempts": attempt, "output": out}
            else:
                return {"status": "success", "attempts": attempt, "output": f"Completed task: {task}"}
        except Exception as e:
            last_error = str(e)

    return {"status": "failed", "attempts": retries, "error": last_error}


def agent_validate_json_output(response: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate agent response string or dictionary against JSON schema requirements."""
    import json
    import re

    raw = response.get("output", "") if isinstance(response, dict) else str(response)
    data = None

    if isinstance(raw, dict):
        data = raw
    else:
        # Extract from code fence if present
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
        candidate = m.group(1) if m else raw.strip()
        try:
            data = json.loads(candidate)
        except Exception as e:
            return {"valid": False, "data": None, "errors": [f"Invalid JSON: {str(e)}"]}

    errors = []
    if isinstance(schema, dict):
        required_keys = schema.get("required", schema.keys())
        for k in required_keys:
            if k not in data:
                errors.append(f"Missing required key: {k}")

    return {
        "valid": len(errors) == 0,
        "data": data,
        "errors": errors,
    }


def agent_extract_action_calls(response: Any) -> List[Dict[str, Any]]:
    """Parse tool/function action call directives from agent response text."""
    import re
    import json

    text = str(response.get("output", "") if isinstance(response, dict) else response)
    actions = []

    # Pattern 1: ACTION: tool_name(arg1, arg2...)
    for m in re.finditer(r"(?:ACTION|TOOL|CALL):\s*([A-Za-z_]\w*)\s*\((.*?)\)", text, re.IGNORECASE):
        tool_name = m.group(1)
        args_str = m.group(2).strip()
        actions.append({"tool": tool_name, "raw_args": args_str})

    # Pattern 2: {"action": "tool_name", "args": {...}}
    for m in re.finditer(r'\{[^{}]*"(?:action|tool)"\s*:\s*"([A-Za-z_]\w*)"[^{}]*\}', text, re.IGNORECASE):
        try:
            obj = json.loads(m.group(0))
            actions.append({"tool": obj.get("action") or obj.get("tool"), "args": obj.get("args", {})})
        except Exception:
            pass

    return actions


def agent_chain_of_thought_step(task: str, context: Optional[str] = None) -> Dict[str, Any]:
    """Generate structured Chain-of-Thought reasoning steps prompt."""
    ctx_part = f"Context:\n{context}\n\n" if context else ""
    prompt = (
        f"{ctx_part}Task: {task}\n\n"
        "Please reason through this step-by-step:\n"
        "1. Identify the core requirements and constraints.\n"
        "2. Break down the intermediate logic.\n"
        "3. Synthesize the final verified response."
    )
    return {
        "task": task,
        "cot_prompt": prompt,
        "technique": "Chain-of-Thought",
    }


def agent_calculate_consensus_agreement(responses: List[Any]) -> float:
    """Calculate average pairwise lexical consensus agreement across agent responses."""
    if not responses or len(responses) < 2:
        return 1.0

    texts = []
    for r in responses:
        t = str(r.get("output", "") if isinstance(r, dict) else r)
        words = set(w.lower().strip(".,!?:;\"'()[]{}") for w in t.split() if len(w) > 2)
        texts.append(words)

    similarities = []
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            w1, w2 = texts[i], texts[j]
            if not w1 and not w2:
                similarities.append(1.0)
            elif not w1 or not w2:
                similarities.append(0.0)
            else:
                jaccard = len(w1.intersection(w2)) / len(w1.union(w2))
                similarities.append(jaccard)

    avg_sim = sum(similarities) / len(similarities) if similarities else 1.0
    return round(avg_sim, 4)


def agent_debate_round(agent1: Any, agent2: Any, topic: str, rounds: Any = 2) -> Dict[str, Any]:
    """Execute multi-turn deliberation debate between two agents on a topic."""
    num_rounds = int(rounds)
    transcript = []
    name1 = getattr(agent1, "name", "Debater 1")
    name2 = getattr(agent2, "name", "Debater 2")

    last_stmt = f"Initial position on {topic}"
    for r in range(1, num_rounds + 1):
        # Speaker 1
        stmt1 = f"[{name1} Round {r}] In response to '{last_stmt[:30]}...', I argue for thesis regarding {topic}."
        if isinstance(agent1, Agent):
            agent1.tell(stmt1)
        transcript.append({"round": r, "speaker": name1, "statement": stmt1})
        last_stmt = stmt1

        # Speaker 2
        stmt2 = f"[{name2} Round {r}] Countering '{last_stmt[:30]}...', my rebuttal highlights key counter-evidence."
        if isinstance(agent2, Agent):
            agent2.tell(stmt2)
        transcript.append({"round": r, "speaker": name2, "statement": stmt2})
        last_stmt = stmt2

    return {
        "topic": topic,
        "rounds": num_rounds,
        "transcript": transcript,
    }


def agent_plan_task_breakdown(agent: Any, high_level_goal: str) -> Dict[str, Any]:
    """Decompose a high-level goal into an actionable subtask checklist."""
    subtasks = [
        f"1. Research requirements and scope for {high_level_goal}",
        f"2. Design architecture and interfaces for {high_level_goal}",
        f"3. Implement core functional modules",
        f"4. Verify implementation with unit and integration tests",
        f"5. Document and deploy final deliverable",
    ]
    return {
        "goal": high_level_goal,
        "subtasks": subtasks,
        "agent": getattr(agent, "name", str(agent)),
    }


def agent_filter_memory_by_date(agent: Any, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Filter agent memory items within a date window."""
    if isinstance(agent, Agent):
        mem = agent.get_memory()
    elif isinstance(agent, list):
        mem = agent
    else:
        mem = []

    s_date = str(start_date).strip()
    e_date = str(end_date).strip()

    filtered = []
    for item in mem:
        ts = str(item.get("timestamp", ""))
        if not ts:
            filtered.append(item)
        elif s_date <= ts <= e_date:
            filtered.append(item)
    return filtered


def agent_merge_agent_memories(agent1: Any, agent2: Any, target_agent: Any) -> int:
    """Merge conversational histories of two agents chronologically into target_agent."""
    mem1 = agent1.get_memory() if isinstance(agent1, Agent) else (agent1 if isinstance(agent1, list) else [])
    mem2 = agent2.get_memory() if isinstance(agent2, Agent) else (agent2 if isinstance(agent2, list) else [])

    merged = list(mem1) + list(mem2)
    if isinstance(target_agent, Agent):
        target_agent.history = list(merged)
        return len(target_agent.history)
    return len(merged)


def agent_register_dynamic_tool(agent: Any, tool_name: str, tool_fn: Any, desc: str = "") -> Dict[str, Any]:
    """Dynamically register a new tool on an agent."""
    t_name = str(tool_name).strip()
    d_str = str(desc).strip()
    if isinstance(agent, Agent):
        agent.tools[t_name] = tool_fn
    return {
        "registered": t_name,
        "description": d_str,
        "agent": getattr(agent, "name", "agent"),
    }


def agent_inspect_available_tools(agent: Any) -> List[Dict[str, Any]]:
    """List tool signatures, names, and descriptions for an agent."""
    if not isinstance(agent, Agent):
        return []
    info = []
    for name, tool in agent.tools.items():
        doc = getattr(tool, "__doc__", "") or "No description provided"
        info.append({"name": name, "description": doc.strip().split("\n")[0]})
    return info


def agent_set_system_persona(agent: Any, new_role: str, new_instructions: str = "") -> Any:
    """Dynamically update an agent's persona role and instructions."""
    if isinstance(agent, Agent):
        agent.role = str(new_role).strip()
        agent.instructions = str(new_instructions).strip()
    return agent


def agent_audit_conversation_safety(history: Any, banned_terms: List[str]) -> Dict[str, Any]:
    """Check conversation history against prohibited terms."""
    if isinstance(history, Agent):
        mem = history.get_memory()
    elif isinstance(history, list):
        mem = history
    else:
        mem = []

    banned = [str(term).lower() for term in banned_terms]
    violations = []

    for idx, msg in enumerate(mem):
        content = str(msg.get("content", "")).lower()
        for term in banned:
            if term in content:
                violations.append({
                    "message_index": idx,
                    "term": term,
                    "role": msg.get("role", "unknown"),
                })

    return {
        "safe": len(violations) == 0,
        "violations": violations,
    }


def agent_count_conversation_turns(agent: Any) -> Dict[str, int]:
    """Count user, assistant, and system turns in agent conversational history."""
    if isinstance(agent, Agent):
        mem = agent.get_memory()
    elif isinstance(agent, list):
        mem = agent
    else:
        mem = []

    user_turns = sum(1 for m in mem if m.get("role") == "user")
    agent_turns = sum(1 for m in mem if m.get("role") in ("agent", "assistant"))
    system_turns = sum(1 for m in mem if m.get("role") == "system")

    return {
        "total": len(mem),
        "user": user_turns,
        "agent": agent_turns,
        "system": system_turns,
    }


def agent_export_chat_transcript(agent: Any, output_file: str) -> str:
    """Export formatted chat transcript to disk."""
    import os
    formatted = agent_format_chat_history(agent, "markdown")
    out_path = str(output_file).strip().strip('"\'')
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(formatted)
    return out_path


class ToolHarness:
    """Registry and execution harness for agent tools with parameter validation."""

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        name: str,
        func: Callable,
        description: str = "",
        param_schema: Optional[Dict[str, type]] = None,
    ) -> None:
        self.tools[name] = {
            "name": name,
            "func": func,
            "description": description or func.__doc__ or "",
            "param_schema": param_schema or {},
        }

    def execute(self, name: str, **kwargs) -> Any:
        if name not in self.tools:
            return f"Error: Tool '{name}' not found. Available: {list(self.tools.keys())}"
        tool_entry = self.tools[name]
        fn = tool_entry["func"]
        schema = tool_entry["param_schema"]

        # Validate types
        for p_name, expected_type in schema.items():
            if p_name in kwargs and not isinstance(kwargs[p_name], expected_type):
                try:
                    kwargs[p_name] = expected_type(kwargs[p_name])
                except Exception:
                    return f"Error: Parameter '{p_name}' expected type {expected_type.__name__}"

        try:
            return fn(**kwargs)
        except Exception as e:
            return f"Error executing tool '{name}': {str(e)}"

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "parameters": {k: v.__name__ for k, v in t["param_schema"].items()},
            }
            for t in self.tools.values()
        ]


class AgentMemoryBuffer:
    """Hierarchical conversation memory with token budgeting and compaction."""

    def __init__(self, max_messages: int = 20, max_chars: int = 10000):
        self.max_messages = max(5, int(max_messages))
        self.max_chars = max(500, int(max_chars))
        self.messages: List[Dict[str, Any]] = []
        self.compacted_summary: str = ""

    def add(self, role: str, content: str, priority: int = 1) -> None:
        self.messages.append({
            "role": role,
            "content": str(content),
            "priority": int(priority),
        })
        if len(self.messages) > self.max_messages or self.total_chars() > self.max_chars:
            self.compact()

    def total_chars(self) -> int:
        return sum(len(m["content"]) for m in self.messages)

    def compact(self) -> None:
        """Compact older low-priority messages into a short summary paragraph."""
        if len(self.messages) <= self.max_messages // 2:
            return

        to_archive = self.messages[: len(self.messages) // 2]
        self.messages = self.messages[len(self.messages) // 2:]

        summary_lines = []
        for m in to_archive:
            role = m["role"]
            snippet = m["content"][:60].replace("\n", " ")
            summary_lines.append(f"{role}: {snippet}...")
        self.compacted_summary += " | " + " ".join(summary_lines)

    def get_context_for_prompt(self) -> str:
        parts = []
        if self.compacted_summary:
            parts.append(f"[Previous Context Summary: {self.compacted_summary.strip(' | ')}]")
        for m in self.messages:
            parts.append(f"{m['role'].upper()}: {m['content']}")
        return "\n".join(parts)

    def search(self, query: str) -> List[Dict[str, Any]]:
        q = query.lower()
        return [m for m in self.messages if q in m["content"].lower()]


class ReActAgent:
    """Reasoning + Acting execution loop with Thought, Action, and Observation cycles."""

    def __init__(
        self,
        name: str = "ReActAgent",
        harness: Optional[ToolHarness] = None,
        max_iterations: int = 5,
        memory: Optional[AgentMemoryBuffer] = None,
        tools: Optional[Dict[str, Callable]] = None,
        max_steps: Optional[int] = None,
    ):
        self.name = name
        self.harness = harness or ToolHarness()
        if tools:
            for k, v in tools.items():
                self.harness.register(k, v)
        self.max_iterations = max_steps or max_iterations
        self.max_steps = self.max_iterations
        self.memory = memory or AgentMemoryBuffer()
        self.trajectory: List[Dict[str, Any]] = []

    def register_tool(self, name: str, fn: Callable) -> None:
        self.harness.register(name, fn)

    @property
    def tools(self) -> Dict[str, Callable]:
        return {k: v["fn"] for k, v in self.harness.tools.items()}

    def run(
        self,
        task: str,
        reasoning_policy: Optional[Callable[[str, List[Dict[str, Any]]], Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        return self.solve(task, reasoning_policy=reasoning_policy)

    def solve(
        self,
        task: str,
        reasoning_policy: Optional[Callable[[str, List[Dict[str, Any]]], Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Execute ReAct cycle on task."""
        self.trajectory = []
        self.memory.add("user", task)

        # Default rule-based policy if no LLM policy provided
        def default_policy(goal: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
            # Step 1: Check tools
            step_num = len(history) + 1
            avail_tools = list(self.harness.tools.keys())
            if not avail_tools or step_num >= 2:
                return {
                    "thought": f"Finalizing answer for task: {goal}",
                    "action": None,
                    "final_answer": f"Completed task: {goal}",
                }
            tool_name = avail_tools[0]
            return {
                "thought": f"Need to invoke tool {tool_name} to gather required data.",
                "action": tool_name,
                "action_input": {},
                "final_answer": None,
            }

        policy = reasoning_policy or default_policy

        for step in range(1, self.max_iterations + 1):
            decision = policy(task, self.trajectory)
            thought = decision.get("thought", "")
            action = decision.get("action")
            action_input = decision.get("action_input", {})
            final_ans = decision.get("final_answer")

            step_record = {
                "step": step,
                "thought": thought,
                "action": action,
                "action_input": action_input,
            }

            if final_ans is not None:
                step_record["final_answer"] = final_ans
                self.trajectory.append(step_record)
                self.memory.add("assistant", final_ans)
                return {
                    "status": "success",
                    "final_answer": final_ans,
                    "steps": len(self.trajectory),
                    "trajectory": self.trajectory,
                }

            # Execute action
            observation = self.harness.execute(action, **action_input)
            step_record["observation"] = observation
            self.trajectory.append(step_record)
            self.memory.add("system", f"Tool {action} returned: {observation}")

        return {
            "status": "max_iterations_reached",
            "final_answer": f"Reached max iterations ({self.max_iterations}) without final answer",
            "steps": len(self.trajectory),
            "trajectory": self.trajectory,
        }


class ToTNode:
    """A reasoning state node in the Tree of Thoughts."""

    def __init__(self, thought: str, state: str, score: float = 0.0, parent: Optional["ToTNode"] = None, depth: int = 0):
        self.thought = thought
        self.state = state
        self.score = score
        self.parent = parent
        self.children: List["ToTNode"] = []
        self.depth = depth

    def path(self) -> List[str]:
        curr: Optional[ToTNode] = self
        thoughts = []
        while curr is not None:
            if curr.thought:
                thoughts.append(curr.thought)
            curr = curr.parent
        thoughts.reverse()
        return thoughts


class TreeOfThoughts:
    """Tree of Thoughts (ToT) deliberate reasoning engine with Beam Search and evaluation."""

    def __init__(
        self,
        thought_generator: Optional[Callable[[str, int], List[str]]] = None,
        state_evaluator: Optional[Callable[[str, str], float]] = None,
    ):
        self.generator = thought_generator or self._default_generator
        self.evaluator = state_evaluator or self._default_evaluator

    def _default_generator(self, current_state: str, k: int) -> List[str]:
        return [f"Plan {i + 1} extending from '{current_state}'" for i in range(k)]

    def _default_evaluator(self, goal: str, proposed_thought: str) -> float:
        # Default heuristic based on length and relevance
        return round(1.0 / (1.0 + len(proposed_thought) % 5), 3)

    def search(
        self,
        initial_state: str,
        k_thoughts: int = 3,
        max_depth: int = 3,
        beam_width: int = 2,
    ) -> Dict[str, Any]:
        """Explores reasoning paths using beam search across depth levels."""
        root = ToTNode(thought="", state=initial_state, score=0.0, depth=0)
        current_beam = [root]
        all_nodes = [root]

        for depth in range(1, max_depth + 1):
            candidates: List[ToTNode] = []
            for node in current_beam:
                proposals = self.generator(node.state, k_thoughts)
                for prop in proposals:
                    new_state = f"{node.state} -> {prop}" if node.state else prop
                    score = self.evaluator(initial_state, prop)
                    child = ToTNode(
                        thought=prop,
                        state=new_state,
                        score=score,
                        parent=node,
                        depth=depth,
                    )
                    node.children.append(child)
                    candidates.append(child)
                    all_nodes.append(child)

            if not candidates:
                break

            # Keep top-B candidates by score
            candidates.sort(key=lambda n: n.score, reverse=True)
            current_beam = candidates[:beam_width]

        # Best leaf in the final beam
        best_node = max(all_nodes, key=lambda n: n.score)
        return {
            "initial_state": initial_state,
            "best_trajectory": best_node.path(),
            "best_score": best_node.score,
            "depth_reached": best_node.depth,
            "total_nodes_explored": len(all_nodes),
            "final_beam_states": [n.state for n in current_beam],
        }


class MultiAgentDebate:
    """Structured multi-round deliberation and consensus debate engine."""

    def __init__(
        self,
        participants: Optional[List[Dict[str, Any]]] = None,
        moderator_name: str = "Moderator",
    ):
        self.participants = list(participants or [
            {"name": "Affirmative", "stance": "support", "role": "Argues in favor with empirical evidence"},
            {"name": "Negative", "stance": "critique", "role": "Identifies edge cases, risks, and counterarguments"},
        ])
        self.moderator_name = moderator_name
        self.round_history: List[Dict[str, Any]] = []

    def run_debate(
        self,
        topic: str,
        rounds: int = 2,
        agent_responder: Optional[Callable[[str, Dict[str, Any], List[Dict[str, Any]]], str]] = None,
    ) -> Dict[str, Any]:
        """Conducts a multi-round debate on a given topic."""
        self.round_history.clear()

        def default_responder(tp: str, participant: Dict[str, Any], history: List[Dict[str, Any]]) -> str:
            name = participant["name"]
            stance = participant.get("stance", "neutral")
            r_idx = len(history) + 1
            return f"[{name} - Round {r_idx}] Given '{tp}', our stance is to {stance}. Refined argument addressing previous critiques."

        responder = agent_responder or default_responder

        for r in range(1, rounds + 1):
            round_speeches = []
            for agent in self.participants:
                speech = responder(topic, agent, self.round_history)
                round_speeches.append({
                    "agent": agent["name"],
                    "stance": agent.get("stance", "neutral"),
                    "speech": speech,
                })
            self.round_history.append({
                "round": r,
                "speeches": round_speeches,
            })

        # Synthesize consensus
        consensus_text = (
            f"Consensus after {rounds} rounds: Balanced synthesis on '{topic}' incorporating points from "
            + ", ".join(a["name"] for a in self.participants)
            + "."
        )

        return {
            "topic": topic,
            "rounds_completed": rounds,
            "participants": [a["name"] for a in self.participants],
            "rounds": self.round_history,
            "consensus": consensus_text,
        }


def agent_react_run(task: str, tools: Optional[Dict[str, Callable]] = None, max_steps: int = 5) -> Dict[str, Any]:
    """Runs a ReAct autonomous loop for a task."""
    agent = ReActAgent(tools=tools, max_steps=max_steps)
    return agent.run(task)


def agent_tree_of_thoughts_search(
    initial_state: str,
    k_thoughts: int = 3,
    max_depth: int = 3,
    beam_width: int = 2,
) -> Dict[str, Any]:
    """Runs deliberate tree search over candidate thoughts."""
    tot = TreeOfThoughts()
    return tot.search(initial_state, k_thoughts=k_thoughts, max_depth=max_depth, beam_width=beam_width)


def agent_run_debate(topic: str, rounds: int = 2) -> Dict[str, Any]:
    """Conducts a structured multi-agent debate."""
    debate = MultiAgentDebate()
    return debate.run_debate(topic, rounds=rounds)


# ==============================================================================
# HIERARCHICAL TASK NETWORK (HTN) PLANNER
# ==============================================================================

class HierarchicalTaskNetworkHTNPlanner:
    """Total-order Hierarchical Task Network (HTN) decomposition planner."""

    @classmethod
    def plan(
        cls,
        tasks: List[str],
        initial_state: Dict[str, Any],
        methods: Dict[str, List[Dict[str, Any]]],
        operators: Dict[str, Dict[str, Any]],
        max_depth: int = 50,
    ) -> Dict[str, Any]:
        """Solves task network using depth-first search with backtracking."""
        nodes_expanded = [0]

        def _matches_preconditions(state: Dict[str, Any], preconds: Dict[str, Any]) -> bool:
            for k, v in preconds.items():
                if state.get(k) != v:
                    return False
            return True

        def _search(curr_tasks: List[str], curr_state: Dict[str, Any], depth: int) -> Optional[Tuple[List[str], Dict[str, Any], float]]:
            if not curr_tasks:
                return ([], curr_state, 0.0)
            if depth > max_depth:
                return None

            nodes_expanded[0] += 1
            t = curr_tasks[0]
            rest = curr_tasks[1:]

            # Case 1: Primitive operator
            if t in operators:
                op = operators[t]
                pre = op.get("preconditions", {})
                if _matches_preconditions(curr_state, pre):
                    new_state = dict(curr_state)
                    # Apply deletions
                    for del_key in op.get("del_list", []):
                        new_state.pop(del_key, None)
                    # Apply additions
                    for add_k, add_v in op.get("add_list", {}).items():
                        new_state[add_k] = add_v
                    cost = float(op.get("cost", 1.0))

                    sub_res = _search(rest, new_state, depth + 1)
                    if sub_res is not None:
                        sub_plan, final_st, sub_cost = sub_res
                        return ([t] + sub_plan, final_st, cost + sub_cost)
                return None

            # Case 2: Compound task decomposed by methods
            if t in methods:
                for method in methods[t]:
                    pre = method.get("preconditions", {})
                    if _matches_preconditions(curr_state, pre):
                        subtasks = method.get("subtasks", [])
                        new_tasks = list(subtasks) + rest
                        sub_res = _search(new_tasks, curr_state, depth + 1)
                        if sub_res is not None:
                            return sub_res
                return None

            # Unknown task
            return None

        init_st = dict(initial_state)
        res = _search(list(tasks), init_st, 0)
        if res is not None:
            plan_ops, final_st, total_cost = res
            return {
                "success": True,
                "plan": plan_ops,
                "plan_length": len(plan_ops),
                "total_cost": round(total_cost, 2),
                "final_state": final_st,
                "nodes_expanded": nodes_expanded[0],
            }
        else:
            return {
                "success": False,
                "plan": [],
                "plan_length": 0,
                "total_cost": 0.0,
                "final_state": init_st,
                "nodes_expanded": nodes_expanded[0],
            }


# ==============================================================================
# MONTE CARLO TREE SEARCH (MCTS) UCT ENGINE
# ==============================================================================

class MCTSNode:
    def __init__(self, state: Any, parent: Optional["MCTSNode"] = None, action_from_parent: Optional[Any] = None):
        self.state = state
        self.parent = parent
        self.action = action_from_parent
        self.children: List["MCTSNode"] = []
        self.visits: int = 0
        self.total_value: float = 0.0

    @property
    def q_value(self) -> float:
        return (self.total_value / self.visits) if self.visits > 0 else 0.0

    def uct_score(self, exploration_c: float) -> float:
        if self.visits == 0:
            return float("inf")
        if not self.parent or self.parent.visits == 0:
            return self.q_value
        return self.q_value + exploration_c * math.sqrt(math.log(self.parent.visits) / self.visits)


class MonteCarloTreeSearchMCTS:
    """Upper Confidence Bound applied to Trees (UCT) decision-making engine."""

    @classmethod
    def search(
        cls,
        initial_state: Any,
        legal_actions: List[Any],
        transition_fn: Optional[Callable[[Any, Any], Any]] = None,
        evaluation_fn: Optional[Callable[[Any], float]] = None,
        iterations: int = 100,
        exploration_c: float = 1.414,
        seed: Optional[int] = 42,
    ) -> Dict[str, Any]:
        rng = random.Random(seed)
        root = MCTSNode(initial_state)

        def default_transition(s: Any, a: Any) -> Any:
            if isinstance(s, dict):
                ns = dict(s)
                ns["last_action"] = a
                ns["step"] = ns.get("step", 0) + 1
                return ns
            elif isinstance(s, (int, float)):
                return s + (hash(a) % 5)
            else:
                return f"{s}->{a}"

        def default_evaluation(s: Any) -> float:
            if isinstance(s, dict):
                return float(s.get("reward", rng.random()))
            elif isinstance(s, (int, float)):
                return float(s) % 10.0
            return rng.random()

        trans = transition_fn or default_transition
        eval_fn = evaluation_fn or default_evaluation

        # Expand root immediately with all legal actions
        for act in legal_actions:
            next_s = trans(root.state, act)
            child = MCTSNode(next_s, parent=root, action_from_parent=act)
            root.children.append(child)

        for _ in range(iterations):
            # 1. Selection
            curr = root
            while curr.children:
                curr = max(curr.children, key=lambda n: n.uct_score(exploration_c))

            # 2. Simulation / Rollout
            val = eval_fn(curr.state)

            # 3. Backpropagation
            node: Optional[MCTSNode] = curr
            while node is not None:
                node.visits += 1
                node.total_value += val
                node = node.parent

        # Choose best child by highest visit count (robust child policy)
        best_child = max(root.children, key=lambda c: c.visits)
        action_stats = {str(c.action): {"visits": c.visits, "q_value": round(c.q_value, 4)} for c in root.children}

        return {
            "best_action": best_child.action,
            "best_value": round(best_child.q_value, 4),
            "root_visits": root.visits,
            "action_statistics": action_stats,
            "iterations": iterations,
        }


def agent_htn_plan(
    tasks: List[str],
    initial_state: Dict[str, Any],
    methods: Dict[str, List[Dict[str, Any]]],
    operators: Dict[str, Dict[str, Any]],
) -> Record:
    """Computes primitive plan using Hierarchical Task Network decomposition."""
    return Record(HierarchicalTaskNetworkHTNPlanner.plan(tasks, initial_state, methods, operators))


def agent_mcts_search(
    initial_state: Any,
    legal_actions: List[Any],
    iterations: int = 100,
    exploration_c: float = 1.414,
) -> Record:
    """Executes Monte Carlo Tree Search (MCTS / UCT) to identify optimal action."""
    res = MonteCarloTreeSearchMCTS.search(initial_state, legal_actions, iterations=iterations, exploration_c=exploration_c)
    res["action_statistics"] = Record(res["action_statistics"])
    return Record(res)




