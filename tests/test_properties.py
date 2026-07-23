"""Property-based tests (hypothesis) for the adapters and schema."""

from hypothesis import given, settings
from hypothesis import strategies as st

from agent_classifier.inputs import from_json, from_text, load_input
from agent_classifier.schema import AgentClassification
from agent_classifier.taxonomy import (
    AutonomyLevel,
    Category,
    DataSensitivity,
    Domain,
    Severity,
)


@settings(deadline=None)
@given(st.text())
def test_from_text_preserves_content(s):
    files = from_text(s)
    assert len(files) == 1
    (data,) = files.values()
    assert data["content"] == s


@settings(deadline=None)
@given(st.dictionaries(st.text(min_size=1), st.text()))
def test_from_json_always_yields_readable_files(d):
    files = from_json(d)
    assert files  # never empty, even for {}
    assert all("content" in v for v in files.values())


@settings(deadline=None)
@given(st.text())
def test_load_input_never_crashes_on_arbitrary_text(s):
    # arbitrary text (incl. null bytes / path-like strings) must not raise
    files = load_input(s)
    assert files
    assert all("content" in v for v in files.values())


@settings(deadline=None)
@given(
    st.sampled_from(list(Domain)),
    st.sampled_from(list(Category)),
    st.sampled_from(list(AutonomyLevel)),
    st.sampled_from(list(DataSensitivity)),
    st.sampled_from(list(Severity)),
    st.floats(min_value=0, max_value=1),
)
def test_classification_json_round_trips(
    domain, category, autonomy, sensitivity, risk, confidence
):
    obj = AgentClassification(
        title="t",
        summary="s",
        domain=domain,
        category=category,
        autonomy_level=autonomy,
        data_sensitivity=sensitivity,
        overall_risk=risk,
        confidence=confidence,
    )
    restored = AgentClassification.model_validate_json(obj.model_dump_json())
    assert restored == obj
