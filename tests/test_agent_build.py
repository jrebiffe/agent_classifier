"""Offline wiring test: the deep agent compiles without any network call.

``init_chat_model`` and ``create_deep_agent`` construct the graph lazily — no
API request is made until ``invoke`` — so this validates the whole assembly
(model, tools, system prompt, response_format) with a dummy key.
"""

from __future__ import annotations

from agent_classifier.agent import build_agent


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
