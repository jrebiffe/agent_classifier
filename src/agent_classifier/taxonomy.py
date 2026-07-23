"""The classification taxonomy.

This is the single place to reshape *what* the Classifier can output. The
schema (``schema.py``) and the system prompt (``prompts.py``) both derive their
allowed values from these enums, so editing a list here changes the whole
pipeline without touching anything else.

Every enum member's value is the exact string the model must produce, so keep
values short, lowercase, and stable.
"""

from enum import StrEnum


class Domain(StrEnum):
    """The primary problem space the analysed agent operates in."""

    SOFTWARE_ENGINEERING = "software_engineering"
    DATA_ANALYSIS = "data_analysis"
    CUSTOMER_SUPPORT = "customer_support"
    SALES_MARKETING = "sales_marketing"
    FINANCE = "finance"
    LEGAL = "legal"
    HEALTHCARE = "healthcare"
    HR_RECRUITING = "hr_recruiting"
    RESEARCH = "research"
    SECURITY = "security"
    IT_OPERATIONS = "it_operations"
    EDUCATION = "education"
    CONTENT_CREATION = "content_creation"
    PERSONAL_PRODUCTIVITY = "personal_productivity"
    OTHER = "other"


class Category(StrEnum):
    """The functional archetype of the agent."""

    CODING_ASSISTANT = "coding_assistant"
    RESEARCH_AGENT = "research_agent"
    WORKFLOW_AUTOMATION = "workflow_automation"
    CONVERSATIONAL_ASSISTANT = "conversational_assistant"
    DATA_PIPELINE = "data_pipeline"
    RETRIEVAL_QA = "retrieval_qa"
    ORCHESTRATOR = "orchestrator"
    MONITORING_ALERTING = "monitoring_alerting"
    CREATIVE_GENERATION = "creative_generation"
    SECURITY_TESTING = "security_testing"
    OTHER = "other"


class RiskCategory(StrEnum):
    """Families of risk an agent can carry, based on what it can do and read."""

    DESTRUCTIVE_ACTION = "destructive_action"  # deletes/overwrites irreversibly
    DATA_EXFILTRATION = "data_exfiltration"  # can move data outward
    SENSITIVE_DATA_ACCESS = "sensitive_data_access"  # reads confidential data
    PROMPT_INJECTION = "prompt_injection"  # ingests untrusted content
    EXCESSIVE_PRIVILEGE = "excessive_privilege"  # broader access than needed
    UNBOUNDED_AUTONOMY = "unbounded_autonomy"  # acts without human review
    FINANCIAL_TRANSACTION = "financial_transaction"  # moves money / makes purchases
    COMPLIANCE_PII = "compliance_pii"  # regulated / personal data
    SUPPLY_CHAIN = "supply_chain"  # unvetted 3rd-party servers/skills
    MISINFORMATION = "misinformation"  # can assert unverified claims
    OTHER = "other"


class Severity(StrEnum):
    """Ordered severity used for individual risks and the aggregate."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AutonomyLevel(StrEnum):
    """How much the agent can do on its own, from advisory to fully autonomous."""

    READ_ONLY = "read_only"  # only observes / reports
    SUGGESTS = "suggests"  # proposes, a human executes
    ACTS_WITH_APPROVAL = "acts_with_approval"  # acts behind human-in-the-loop
    FULLY_AUTONOMOUS = "fully_autonomous"  # acts without approval


class DataSensitivity(StrEnum):
    """Sensitivity of the data the agent is exposed to."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
