"""GIDBoy LangGraph Research Workflow.

This module implements the core research workflow using LangGraph:
question → clarify → map context → investigate → generate hypotheses → compare → identify opportunities → generate content → suggest next directions
"""
from typing import Dict, Any, List, TypedDict, Annotated
import operator

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("Warning: LangGraph not available, using fallback implementation")

from agents import (
    AgentState,
    ResearchAgent,
    OpportunityAgent,
    ContentAgent,
    MemoryAgent,
    ExecutionAgent
)


class WorkflowState(TypedDict):
    """State for the research workflow."""
    query: str
    mode: str
    context: Dict[str, Any]
    memory: List[Dict[str, Any]]
    output: Dict[str, Any]
    status: str
    reasoning: List[str]
    current_step: str


class ResearchWorkflow:
    """
    GIDBoy Research Workflow using LangGraph.

    Implements the full intelligence pipeline:
    1. Memory retrieval
    2. Research investigation
    3. Opportunity discovery
    4. Content generation
    5. Execution planning
    6. Memory storage
    """

    def __init__(self, llm_client=None, vector_store=None):
        self.llm_client = llm_client
        self.vector_store = vector_store
        self.agents = self._initialize_agents()
        self.graph = self._build_graph()

    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all agents."""
        return {
            "research": ResearchAgent(self.llm_client),
            "opportunity": OpportunityAgent(self.llm_client),
            "content": ContentAgent(self.llm_client),
            "memory": MemoryAgent(self.llm_client, self.vector_store),
            "execution": ExecutionAgent(self.llm_client),
        }

    def _build_graph(self):
        """Build the LangGraph workflow."""
        if not LANGGRAPH_AVAILABLE:
            return None

        # Define the state graph
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("memory_retrieve", self._memory_retrieve_node)
        workflow.add_node("research", self._research_node)
        workflow.add_node("opportunity", self._opportunity_node)
        workflow.add_node("content", self._content_node)
        workflow.add_node("execution", self._execution_node)
        workflow.add_node("memory_store", self._memory_store_node)

        # Define edges
        workflow.set_entry_point("memory_retrieve")
        workflow.add_edge("memory_retrieve", "research")
        workflow.add_edge("research", "opportunity")
        workflow.add_edge("opportunity", "content")
        workflow.add_edge("content", "execution")
        workflow.add_edge("execution", "memory_store")
        workflow.add_edge("memory_store", END)

        # Compile the graph
        return workflow.compile()

    def _memory_retrieve_node(self, state: WorkflowState) -> WorkflowState:
        """Retrieve relevant memories."""
        agent_state = self._to_agent_state(state)
        result = self.agents["memory"].process(agent_state)
        return self._from_agent_state(result, state, "memory_retrieved")

    def _research_node(self, state: WorkflowState) -> WorkflowState:
        """Execute research."""
        agent_state = self._to_agent_state(state)
        result = self.agents["research"].process(agent_state)
        return self._from_agent_state(result, state, "research_completed")

    def _opportunity_node(self, state: WorkflowState) -> WorkflowState:
        """Discover opportunities."""
        agent_state = self._to_agent_state(state)
        result = self.agents["opportunity"].process(agent_state)
        return self._from_agent_state(result, state, "opportunities_found")

    def _content_node(self, state: WorkflowState) -> WorkflowState:
        """Generate content."""
        agent_state = self._to_agent_state(state)
        result = self.agents["content"].process(agent_state)
        return self._from_agent_state(result, state, "content_generated")

    def _execution_node(self, state: WorkflowState) -> WorkflowState:
        """Plan execution."""
        agent_state = self._to_agent_state(state)
        result = self.agents["execution"].process(agent_state)
        return self._from_agent_state(result, state, "execution_planned")

    def _memory_store_node(self, state: WorkflowState) -> WorkflowState:
        """Store results to memory."""
        agent_state = self._to_agent_state(state)
        agent_state.status = "completed"
        result = self.agents["memory"].process(agent_state)
        return self._from_agent_state(result, state, "workflow_complete")

    def _to_agent_state(self, state: WorkflowState) -> AgentState:
        """Convert workflow state to agent state."""
        return AgentState(
            query=state.get("query", ""),
            mode=state.get("mode", "research"),
            context=state.get("context", {}),
            memory=state.get("memory", []),
            output=state.get("output", {}),
            status=state.get("status", "pending"),
            reasoning=state.get("reasoning", [])
        )

    def _from_agent_state(
        self,
        agent_state: AgentState,
        original: WorkflowState,
        step: str
    ) -> WorkflowState:
        """Convert agent state back to workflow state."""
        return {
            "query": agent_state.query,
            "mode": agent_state.mode,
            "context": agent_state.context,
            "memory": agent_state.memory,
            "output": agent_state.output,
            "status": agent_state.status,
            "reasoning": agent_state.reasoning,
            "current_step": step
        }

    def run(self, query: str, mode: str = "research") -> Dict[str, Any]:
        """
        Run the full research workflow.

        Args:
            query: The research query
            mode: The execution mode

        Returns:
            Complete workflow output with research, opportunities, content, and execution plan
        """
        if not self.graph:
            # Fallback to sequential execution
            return self._run_sequential(query, mode)

        # Initialize state
        initial_state = {
            "query": query,
            "mode": mode,
            "context": {},
            "memory": [],
            "output": {},
            "status": "pending",
            "reasoning": [],
            "current_step": "start"
        }

        # Run the workflow
        try:
            result = self.graph.invoke(initial_state)
            return {
                "query": result.get("query"),
                "mode": result.get("mode"),
                "output": result.get("output", {}),
                "status": result.get("status"),
                "reasoning": result.get("reasoning", []),
                "steps_completed": result.get("current_step")
            }
        except Exception as e:
            print(f"Workflow error: {e}, falling back to sequential")
            return self._run_sequential(query, mode)

    def _run_sequential(self, query: str, mode: str) -> Dict[str, Any]:
        """Fallback sequential execution without LangGraph."""
        print("Running sequential workflow...")

        # Initialize state
        state = AgentState(
            query=query,
            mode=mode,
            context={},
            memory=[],
            output={},
            status="pending"
        )

        # Step 1: Memory retrieve
        print("Step 1: Retrieving memories...")
        state = self.agents["memory"].process(state)

        # Step 2: Research
        print("Step 2: Conducting research...")
        state = self.agents["research"].process(state)

        # Step 3: Opportunities
        print("Step 3: Discovering opportunities...")
        state = self.agents["opportunity"].process(state)

        # Step 4: Content
        print("Step 4: Generating content...")
        state = self.agents["content"].process(state)

        # Step 5: Execution
        print("Step 5: Planning execution...")
        state = self.agents["execution"].process(state)

        # Step 6: Memory store
        print("Step 6: Storing to memory...")
        state.status = "completed"
        state = self.agents["memory"].process(state)

        return {
            "query": state.query,
            "mode": state.mode,
            "output": state.output,
            "status": state.status,
            "reasoning": state.reasoning
        }

    def run_research_only(self, query: str) -> Dict[str, Any]:
        """Run only the research phase."""
        state = AgentState(
            query=query,
            mode="research",
            context={},
            memory=[],
            output={},
            status="pending"
        )

        # Retrieve memories first
        state = self.agents["memory"].process(state)

        # Research only
        state = self.agents["research"].process(state)

        return state.output.get("research", {})

    def run_opportunities_only(self, query: str, research: Dict[str, Any]) -> Dict[str, Any]:
        """Run only opportunity discovery."""
        state = AgentState(
            query=query,
            mode="opportunity",
            context={},
            memory=[],
            output={"research": research},
            status="pending"
        )

        state = self.agents["opportunity"].process(state)

        return state.output.get("opportunities", [])


# Simple interface for API usage
def create_workflow(llm_client=None, vector_store=None):
    """Factory function to create a research workflow."""
    return ResearchWorkflow(llm_client, vector_store)
