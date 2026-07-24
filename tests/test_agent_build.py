"""Offline tests for agent construction and classify()'s reuse contract.

``init_chat_model`` and ``create_deep_agent`` construct the graph lazily — no
API request is made until ``invoke`` — so the ``build_agent`` tests validate
the whole assembly (model, tools, system prompt, response_format) with a
dummy key. The ``classify`` test uses a fake agent to stay offline too.
"""

from typing import Any

from agent_classifier.agent import build_agent, classify, default_model


class _FakeAgent:
    """Duck-typed stand-in for a compiled deep agent, for reuse tests."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def invoke(self, payload: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(payload)
        return {"structured_response": "stub-result"}


def test_classify_reuses_a_prebuilt_agent():
    # `agent` is mandatory: build once, pass the same instance to multiple
    # classify() calls to reuse it without recompiling.
    agent = _FakeAgent()

    first = classify("hello world", agent=agent)
    second = classify("a different agent", agent=agent)

    assert first == second == "stub-result"
    assert len(agent.calls) == 2


def test_build_agent_with_enrichment(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-used")
    agent = build_agent()
    assert hasattr(agent, "invoke")


def test_build_agent_without_enrichment(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-used")
    agent = build_agent(use_enrichment=False)
    assert hasattr(agent, "invoke")


def test_build_agent_respects_model_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-used")
    monkeypatch.setenv("AGENT_CLASSIFIER_MODEL", "anthropic:claude-sonnet-4-6")
    agent = build_agent()
    assert hasattr(agent, "invoke")


def test_build_agent_accepts_model_id_string(monkeypatch):
    # exercises the str branch of _resolve_model
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-used")
    agent = build_agent(model="anthropic:claude-sonnet-4-6")
    assert hasattr(agent, "invoke")


def test_build_agent_accepts_model_instance_and_extra_tools(monkeypatch):
    # exercises the BaseChatModel passthrough branch and extra_tools
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-used")
    model = default_model()
    agent = build_agent(model=model, use_enrichment=False, extra_tools=[])
    assert hasattr(agent, "invoke")
