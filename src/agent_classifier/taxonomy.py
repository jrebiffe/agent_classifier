"""The classification taxonomy.

This is the single place to reshape *what* the Classifier can output. The
schema (``schema.py``) and the system prompt (``prompts.py``) both derive their
allowed values from these enums, so editing a list here changes the whole
pipeline without touching anything else.

Every enum member's value is the exact string the model must produce. Values
are derived from member names via ``auto()`` (``NAME`` -> ``"name"``), so keep
names short, stable, and rename-averse: renaming a member changes the wire
value.
"""

from enum import StrEnum, auto


class Domain(StrEnum):
    """The primary problem space the analysed agent operates in."""

    SOFTWARE_ENGINEERING = auto()
    DATA_ANALYSIS = auto()
    CUSTOMER_SUPPORT = auto()
    SALES_MARKETING = auto()
    FINANCE = auto()
    LEGAL = auto()
    HEALTHCARE = auto()
    HR_RECRUITING = auto()
    RESEARCH = auto()
    SECURITY = auto()
    IT_OPERATIONS = auto()
    EDUCATION = auto()
    CONTENT_CREATION = auto()
    PERSONAL_PRODUCTIVITY = auto()
    OTHER = auto()


class Category(StrEnum):
    """The functional archetype of the agent."""

    CODING_ASSISTANT = auto()
    RESEARCH_AGENT = auto()
    WORKFLOW_AUTOMATION = auto()
    CONVERSATIONAL_ASSISTANT = auto()
    DATA_PIPELINE = auto()
    RETRIEVAL_QA = auto()
    ORCHESTRATOR = auto()
    MONITORING_ALERTING = auto()
    CREATIVE_GENERATION = auto()
    SECURITY_TESTING = auto()
    OTHER = auto()


class RiskCategory(StrEnum):
    """Families of risk an agent can carry, based on what it can do and read."""

    DESTRUCTIVE_ACTION = auto()  # deletes/overwrites irreversibly
    DATA_EXFILTRATION = auto()  # can move data outward
    SENSITIVE_DATA_ACCESS = auto()  # reads confidential data
    PROMPT_INJECTION = auto()  # ingests untrusted content
    EXCESSIVE_PRIVILEGE = auto()  # broader access than needed
    UNBOUNDED_AUTONOMY = auto()  # acts without human review
    FINANCIAL_TRANSACTION = auto()  # moves money / makes purchases
    COMPLIANCE_PII = auto()  # regulated / personal data
    SUPPLY_CHAIN = auto()  # unvetted 3rd-party servers/skills
    MISINFORMATION = auto()  # can assert unverified claims
    OTHER = auto()


class Severity(StrEnum):
    """Ordered severity used for individual risks and the aggregate."""

    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class AutonomyLevel(StrEnum):
    """How much the agent can do on its own, from advisory to fully autonomous."""

    READ_ONLY = auto()  # only observes / reports
    SUGGESTS = auto()  # proposes, a human executes
    ACTS_WITH_APPROVAL = auto()  # acts behind human-in-the-loop
    FULLY_AUTONOMOUS = auto()  # acts without approval


class DataSensitivity(StrEnum):
    """Sensitivity of the data the agent is exposed to."""

    NONE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
