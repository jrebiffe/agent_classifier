"""Sanity checks on the taxonomy enums."""

from __future__ import annotations

import pytest

from agent_classifier.taxonomy import (
    AutonomyLevel,
    Category,
    DataSensitivity,
    Domain,
    RiskCategory,
    Severity,
)

ALL_ENUMS = [
    Domain,
    Category,
    RiskCategory,
    Severity,
    AutonomyLevel,
    DataSensitivity,
]


@pytest.mark.parametrize("enum_cls", ALL_ENUMS)
def test_values_are_lowercase_strings_and_unique(enum_cls):
    values = [member.value for member in enum_cls]
    assert values, f"{enum_cls.__name__} has no members"
    for value in values:
        assert isinstance(value, str)
        assert value == value.lower(), f"{value!r} is not lowercase"
        assert " " not in value, f"{value!r} contains whitespace"
    assert len(values) == len(set(values)), f"{enum_cls.__name__} has duplicates"


def test_str_enum_compares_as_string():
    # StrEnum members must equal their string value for schema round-tripping.
    assert RiskCategory.FINANCIAL_TRANSACTION == "financial_transaction"
    assert Severity.CRITICAL == "critical"


def test_expected_members_present():
    assert "other" in {m.value for m in Domain}
    assert "workflow_automation" in {m.value for m in Category}
    assert {"low", "medium", "high", "critical"} <= {m.value for m in Severity}
    assert "fully_autonomous" in {m.value for m in AutonomyLevel}
