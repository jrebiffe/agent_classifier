"""The enrichment lookup tools."""

from agent_classifier.tools import ENRICHMENT_TOOLS, lookup_mcp_server, lookup_skill


def test_lookup_known_mcp_server_reports_capabilities():
    out = lookup_mcp_server.invoke({"name": "github"})
    assert "github" in out.lower()
    assert "risk" in out.lower()


def test_lookup_mcp_server_matches_loosely():
    # underscores normalise to hyphens and partial names still match
    out = lookup_mcp_server.invoke({"name": "google_drive"})
    assert "drive" in out.lower()


def test_lookup_unknown_mcp_server_returns_guidance():
    out = lookup_mcp_server.invoke({"name": "totally-unknown-server-xyz"})
    assert "knowledge base" in out.lower()
    assert "confidence" in out.lower()


def test_lookup_skill_mentions_the_name():
    out = lookup_skill.invoke({"name": "issue-refund"})
    assert "issue-refund" in out


def test_enrichment_tools_exported():
    assert lookup_mcp_server in ENRICHMENT_TOOLS
    assert lookup_skill in ENRICHMENT_TOOLS
