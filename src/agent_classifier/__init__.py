"""agent_classifier: a DeepAgents-based Classifier for AI agents.

Given the artifacts of an AI agent (instructions, MCP servers, skills, tools,
settings), it identifies goals, domain, category, capabilities, autonomy, and
risks, and returns them as a validated :class:`AgentClassification`.
"""

from .agent import build_agent, classify
from .schema import AgentClassification, Capability, Goal, Risk

__all__ = [
    "AgentClassification",
    "Capability",
    "Goal",
    "Risk",
    "build_agent",
    "classify",
]
