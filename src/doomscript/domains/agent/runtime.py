"""Runtime execution engine for AI Agents and Multi-Agent Workflows domain."""

from typing import Any, Callable, Dict, List, Optional, Union
from doomscript.runtime import Record, ask_ai
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
