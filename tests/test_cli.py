"""CLI behaviour, with the model call stubbed out."""

from __future__ import annotations

import io
import json
from pathlib import Path

from agent_classifier import cli
from agent_classifier.schema import AgentClassification

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "sample_agent"


def _fake_result() -> AgentClassification:
    return AgentClassification(
        title="X",
        summary="a stub result",
        domain="other",
        category="other",
        autonomy_level="read_only",
        data_sensitivity="none",
        overall_risk="low",
        confidence=0.5,
    )


def _stub_classify(monkeypatch):
    monkeypatch.setattr(
        "agent_classifier.agent.classify", lambda *a, **k: _fake_result()
    )


def test_build_parser_defaults():
    args = cli.build_parser().parse_args([])
    assert args.source == "-"
    assert args.model is None
    assert args.no_enrichment is False
    assert args.output is None


def test_main_prints_json_for_a_path(monkeypatch, capsys):
    _stub_classify(monkeypatch)
    rc = cli.main([str(FIXTURE_DIR)])
    assert rc == 0
    assert json.loads(capsys.readouterr().out)["title"] == "X"


def test_main_writes_output_file(monkeypatch, tmp_path):
    _stub_classify(monkeypatch)
    out = tmp_path / "result.json"
    rc = cli.main([str(FIXTURE_DIR), "-o", str(out)])
    assert rc == 0
    assert json.loads(out.read_text(encoding="utf-8"))["domain"] == "other"


def test_main_reads_text_from_stdin(monkeypatch, capsys):
    _stub_classify(monkeypatch)
    monkeypatch.setattr("sys.stdin", io.StringIO("some agent instructions"))
    rc = cli.main(["-"])
    assert rc == 0
    assert json.loads(capsys.readouterr().out)["title"] == "X"


def test_main_empty_stdin_errors(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    assert cli.main(["-"]) == 2


def test_main_missing_path_errors():
    assert cli.main(["/no/such/path/really-not-here"]) == 2
