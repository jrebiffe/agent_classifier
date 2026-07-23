"""Validation behaviour of the output schema."""

import pytest
from pydantic import ValidationError

from agent_classifier.schema import AgentClassification, Goal, Risk


def _minimal_classification(**overrides):
    data = {
        "title": "Test Agent",
        "summary": "An agent used for testing.",
        "domain": "software_engineering",
        "category": "coding_assistant",
        "autonomy_level": "suggests",
        "data_sensitivity": "low",
        "overall_risk": "low",
        "confidence": 0.8,
    }
    data.update(overrides)
    return AgentClassification(**data)


def test_minimal_valid_classification():
    result = _minimal_classification()
    assert result.title == "Test Agent"
    # list fields default to empty
    assert result.goals == []
    assert result.risks == []
    assert result.missing_info == []


def test_nested_goals_and_risks():
    result = _minimal_classification(
        goals=[Goal(description="Write code", kind="primary", evidence="line 1")],
        risks=[
            Risk(
                category="destructive_action",
                severity="high",
                description="can delete files",
                evidence="filesystem MCP server",
            )
        ],
    )
    assert result.goals[0].kind == "primary"
    assert result.risks[0].category == "destructive_action"
    assert result.risks[0].mitigation is None


def test_invalid_enum_rejected():
    with pytest.raises(ValidationError):
        _minimal_classification(domain="not_a_real_domain")


def test_confidence_bounds_enforced():
    with pytest.raises(ValidationError):
        _minimal_classification(confidence=1.5)
    with pytest.raises(ValidationError):
        _minimal_classification(confidence=-0.1)


def test_invalid_goal_kind_rejected():
    with pytest.raises(ValidationError):
        Goal(description="x", kind="tertiary", evidence="y")


def test_json_round_trip():
    result = _minimal_classification(
        risks=[
            Risk(
                category="financial_transaction",
                severity="critical",
                description="issues refunds",
                evidence="stripe server",
                mitigation="human approval over $100",
            )
        ],
    )
    payload = result.model_dump_json()
    restored = AgentClassification.model_validate_json(payload)
    assert restored == result
