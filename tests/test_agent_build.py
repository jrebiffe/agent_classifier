"""Offline wiring test: the deep agent compiles without any network call.

``init_chat_model`` and ``create_deep_agent`` construct the graph lazily — no
API request is made until ``invoke`` — so this validates the whole assembly
(model, tools, system prompt, response_format) with a dummy key.
"""

from __future__ import annotations

from agent_classifier.agent import build_agent, default_model


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
