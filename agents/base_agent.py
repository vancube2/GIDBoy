"""Base agent class for GIDBoy Intelligence OS."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json


@dataclass
class AgentState:
    """State container for agent execution."""
    query: str
    mode: str
    context: Dict[str, Any]
    memory: List[Dict[str, Any]]
    output: Dict[str, Any]
    status: str = "pending"  # pending, running, completed, error
    reasoning: List[str] = None

    def __post_init__(self):
        if self.reasoning is None:
            self.reasoning = []


class BaseAgent(ABC):
    """Base class for all GIDBoy agents."""

    def __init__(self, name: str, llm_client=None):
        self.name = name
        self.llm_client = llm_client
        self.reasoning_log = []

    @abstractmethod
    def process(self, state: AgentState) -> AgentState:
        """Process the agent's task and return updated state."""
        pass

    def log_reasoning(self, step: str, thought: str):
        """Log reasoning step."""
        self.reasoning_log.append({
            "step": step,
            "thought": thought,
            "agent": self.name
        })

    def format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with variables."""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return template

    def parse_json_output(self, text: str) -> Dict[str, Any]:
        """Parse JSON from LLM output."""
        import re

        # Try to find JSON block
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass

        # Try to find JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass

        # Return raw text as fallback
        return {"raw_output": text}

    def __str__(self) -> str:
        return f"{self.name}Agent"
