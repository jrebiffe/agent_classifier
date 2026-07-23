"""The Classifier deep agent.

A single DeepAgents agent with the built-in virtual filesystem, the enrichment
tools, and ``response_format=AgentClassification``. The agent reads the
artifacts seeded onto its filesystem, optionally enriches its understanding via
the lookup tools, and returns the structured classification.

If you later want deeper, auditable per-dimension analysis, this is the place to
add specialist ``subagents`` (goal-analyst / risk-assessor / domain-classifier)
to ``create_deep_agent`` — the input/output contract below stays the same.
"""

import os
from typing import Any, cast

from deepagents import create_deep_agent
from langchain_core.language_models import BaseChatModel

from .inputs import load_input
from .prompts import SYSTEM_PROMPT, USER_INSTRUCTION
from .schema import AgentClassification
from .tools import ENRICHMENT_TOOLS

DEFAULT_MODEL = "anthropic:claude-sonnet-4-6"


def default_model(model_id: str | None = None) -> BaseChatModel:
    """Build the classifier model via ``init_chat_model`` (provider-agnostic).

    The id defaults to ``AGENT_CLASSIFIER_MODEL`` or :data:`DEFAULT_MODEL`;
    temperature defaults to ``AGENT_CLASSIFIER_TEMPERATURE`` (0 for stability).
    """
    from langchain.chat_models import init_chat_model

    model_id = model_id or os.getenv("AGENT_CLASSIFIER_MODEL", DEFAULT_MODEL)
    temperature = float(os.getenv("AGENT_CLASSIFIER_TEMPERATURE", "0"))
    return cast(BaseChatModel, init_chat_model(model_id, temperature=temperature))


def _resolve_model(model: str | BaseChatModel | None) -> BaseChatModel:
    if model is None:
        return default_model()
    if isinstance(model, str):
        return default_model(model)
    return model


def build_agent(
    model: str | BaseChatModel | None = None,
    *,
    use_enrichment: bool = True,
    extra_tools: list[Any] | None = None,
) -> Any:
    """Construct (compile) the Classifier deep agent.

    Args:
        model: model id string, a ``BaseChatModel`` instance, or ``None`` for
            the environment/default model.
        use_enrichment: include the MCP/skill lookup tools.
        extra_tools: additional tools to expose to the agent.
    """
    tools: list[Any] = list(ENRICHMENT_TOOLS) if use_enrichment else []
    if extra_tools:
        tools.extend(extra_tools)

    return create_deep_agent(
        model=_resolve_model(model),
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        response_format=AgentClassification,
    )


def classify(
    source: Any,
    *,
    model: str | BaseChatModel | None = None,
    use_enrichment: bool = True,
    recursion_limit: int = 50,
) -> AgentClassification:
    """Classify an agent from its artifacts.

    Args:
        source: a directory path, a file path, a raw text blob, or a structured
            dict describing the agent (see :func:`agent_classifier.inputs.load_input`).
        model: optional model override.
        use_enrichment: enable the MCP/skill lookup tools.
        recursion_limit: LangGraph recursion budget for the agent loop.

    Returns:
        A validated :class:`AgentClassification`.
    """
    files = load_input(source)
    agent = build_agent(model=model, use_enrichment=use_enrichment)
    result = agent.invoke(
        {"messages": [{"role": "user", "content": USER_INSTRUCTION}], "files": files},
        config={"recursion_limit": recursion_limit},
    )
    return cast(AgentClassification, result["structured_response"])
