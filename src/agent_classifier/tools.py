"""Enrichment tools the Classifier can call during analysis.

These let the agent learn what a referenced MCP server or skill *actually* does
before it scores risk — the main quality lever over a naive one-shot classifier
(e.g. discovering that a ``github`` server can push code and merge PRs).

This is a starter, offline knowledge base. To go further, extend ``_MCP_KB`` or
replace [`lookup_mcp_server`][agent_classifier.tools.lookup_mcp_server] with a
live registry / web-search lookup; the
agent wiring in ``agent.py`` does not care how these tools are implemented.
"""

from langchain_core.tools import tool

# name fragment -> capability + risk summary. Keys are matched loosely.
_MCP_KB: dict[str, str] = {
    "github": (
        "GitHub API access. Can read AND write repositories, issues, PRs, and "
        "Actions: push code, merge PRs, trigger workflows. Relevant risks: "
        "destructive_action, supply_chain, excessive_privilege."
    ),
    "filesystem": (
        "Local filesystem access. Can read, create, edit, and delete files. "
        "Relevant risks: destructive_action, sensitive_data_access, "
        "data_exfiltration."
    ),
    "slack": (
        "Slack workspace access. Can read channels/DMs and post messages. "
        "Relevant risks: data_exfiltration, sensitive_data_access."
    ),
    "postgres": (
        "PostgreSQL database access, often read/write SQL. Relevant risks: "
        "destructive_action, sensitive_data_access, compliance_pii."
    ),
    "google-drive": (
        "Google Drive access; read/write documents. Relevant risks: "
        "data_exfiltration, sensitive_data_access, compliance_pii."
    ),
    "fetch": (
        "Fetches arbitrary URLs, pulling untrusted web content into context. "
        "Relevant risks: prompt_injection, data_exfiltration."
    ),
    "puppeteer": (
        "Headless browser automation; can browse and act on the web. Relevant "
        "risks: prompt_injection, unbounded_autonomy."
    ),
    "stripe": (
        "Stripe payments API. Can create charges and refunds. Relevant risks: "
        "financial_transaction, destructive_action."
    ),
    "memory": (
        "Persistent memory store; read/write agent memory. Relevant risks: "
        "sensitive_data_access."
    ),
    "sentry": (
        "Sentry error monitoring; mostly read access to stack traces and "
        "events. Relevant risks: sensitive_data_access."
    ),
}


@tool
def lookup_mcp_server(name: str) -> str:
    """Look up the typical capabilities and risk profile of a named MCP server.

    Call this whenever the analysed agent references an MCP server, so you can
    judge its true capabilities (especially write/delete access) before scoring
    risk. Returns guidance for unknown servers rather than failing.
    """
    key = name.strip().lower().replace("_", "-")
    for fragment, summary in _MCP_KB.items():
        if fragment in key or key in fragment:
            return f"{name}: {summary}"
    return (
        f"{name}: not in the knowledge base. Infer its capabilities from the "
        "name and any configuration in the input, treat unknown write or "
        "network access as a potential risk, and lower your confidence."
    )


@tool
def lookup_skill(name: str) -> str:
    """Explain what an agent 'skill' with the given name likely does.

    Skills are reusable instruction/tool bundles; the name usually signals
    intent. Use this alongside the skill's own files (if present in the input)
    to reason about the capabilities and risks it adds.
    """
    return (
        f"'{name}' is a skill: a reusable bundle of instructions and/or tools. "
        "Judge it by its name and, when available, its file contents in the "
        "input. A skill can add capabilities and risks beyond the base "
        "instructions, so account for it explicitly."
    )


ENRICHMENT_TOOLS = [lookup_mcp_server, lookup_skill]
