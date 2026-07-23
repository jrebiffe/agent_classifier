"""The structured output the Classifier produces.

``AgentClassification`` is passed to the deep agent as ``response_format`` and
is what the model is required to return. Field descriptions are sent to the
model as part of the schema, so they double as instructions — keep them tight.

The enums come from ``taxonomy.py``; edit that module to reshape the output.
"""

from typing import Literal

from pydantic import BaseModel, Field

from .taxonomy import (
    AutonomyLevel,
    Category,
    DataSensitivity,
    Domain,
    RiskCategory,
    Severity,
)

type GoalKind = Literal["primary", "secondary", "implicit"]
type CapabilitySource = Literal[
    "instructions", "mcp_server", "skill", "tool", "inferred"
]


class Goal(BaseModel):
    """Something the analysed agent is trying to achieve."""

    description: str = Field(description="What the agent is trying to achieve.")
    kind: GoalKind = Field(
        description="primary = core purpose; secondary = supporting; "
        "implicit = not stated but evident from the artifacts.",
    )
    evidence: str = Field(
        description="Quote or reference from the input that supports this goal.",
    )


class Capability(BaseModel):
    """A concrete thing the agent can do, tied to where it comes from."""

    name: str = Field(description="Short name of the capability.")
    source: CapabilitySource = Field(
        description="Where the capability comes from in the input.",
    )
    description: str = Field(description="What the capability lets the agent do.")


class Risk(BaseModel):
    """A single identified risk, grounded in the input."""

    category: RiskCategory = Field(description="The family of risk.")
    severity: Severity = Field(description="Severity of this specific risk.")
    description: str = Field(description="The risk and how it could materialise.")
    evidence: str = Field(
        description="What in the input creates this risk (be specific).",
    )
    mitigation: str | None = Field(
        default=None,
        description="Existing or recommended mitigation, if any.",
    )


class AgentClassification(BaseModel):
    """Full structured classification of one analysed AI agent."""

    title: str = Field(description="Short human-readable name for the analysed agent.")
    summary: str = Field(
        description="One or two sentences describing what the agent is and does.",
    )
    domain: Domain = Field(description="Primary problem space.")
    subdomains: list[str] = Field(
        default_factory=list,
        description="Finer-grained, free-form domains (may be empty).",
    )
    category: Category = Field(description="Functional archetype of the agent.")
    goals: list[Goal] = Field(default_factory=list, description="Identified goals.")
    capabilities: list[Capability] = Field(
        default_factory=list,
        description="Capabilities the agent has, each tied to its source.",
    )
    autonomy_level: AutonomyLevel = Field(
        description="How much the agent can do without human approval.",
    )
    data_sensitivity: DataSensitivity = Field(
        description="Sensitivity of the data the agent is exposed to.",
    )
    risks: list[Risk] = Field(default_factory=list, description="Identified risks.")
    overall_risk: Severity = Field(
        description="Aggregate risk level across all identified risks.",
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="0-1 confidence in this classification given the input quality.",
    )
    missing_info: list[str] = Field(
        default_factory=list,
        description="Facts that could not be determined from the input. "
        "Record gaps here instead of guessing.",
    )
