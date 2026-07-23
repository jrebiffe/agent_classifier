"""Input adapters: directory, blob, and structured dict."""

from pathlib import Path

import pytest

from agent_classifier.inputs import (
    from_directory,
    from_json,
    from_text,
    load_input,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "sample_agent"


def _content(file_data) -> str:
    # Every FileData entry must carry readable text under "content".
    assert "content" in file_data
    return file_data["content"]


def test_from_text_single_file():
    files = from_text("hello agent")
    assert len(files) == 1
    (data,) = files.values()
    assert _content(data) == "hello agent"


def test_from_directory_reads_expected_artifacts():
    files = from_directory(FIXTURE_DIR)
    assert "/agent/CLAUDE.md" in files
    assert "/agent/.mcp.json" in files
    assert "/agent/skills/issue-refund.md" in files
    # content is actually loaded, not just the path
    assert "refund" in _content(files["/agent/CLAUDE.md"]).lower()
    assert "stripe" in _content(files["/agent/.mcp.json"]).lower()


def test_from_directory_skips_tooling_dirs(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("real content", encoding="utf-8")
    junk = tmp_path / ".git"
    junk.mkdir()
    (junk / "config").write_text("should be ignored", encoding="utf-8")
    files = from_directory(tmp_path)
    assert "/agent/CLAUDE.md" in files
    assert not any(".git" in path for path in files)


def test_from_directory_rejects_non_directory():
    with pytest.raises(NotADirectoryError):
        from_directory(FIXTURE_DIR / "CLAUDE.md")


def test_from_json_renders_known_sections():
    files = from_json(
        {
            "instructions": "You are a helper.",
            "mcpServers": {"github": {"command": "x"}},
            "skills": ["refund", "lookup"],
            "owner": "team-support",
        }
    )
    assert "You are a helper." in _content(files["/agent/instructions.md"])
    assert "github" in _content(files["/agent/mcp_servers.json"])
    assert "refund" in _content(files["/agent/skills.json"])
    # unknown keys are preserved, not dropped
    assert "team-support" in _content(files["/agent/metadata.json"])


def test_load_input_dispatch(tmp_path):
    # dict -> from_json
    assert "/agent/instructions.md" in load_input({"instructions": "hi"})
    # existing directory -> from_directory
    assert "/agent/CLAUDE.md" in load_input(FIXTURE_DIR)
    # existing file path -> single file
    single = load_input(FIXTURE_DIR / "CLAUDE.md")
    assert any(path.endswith("CLAUDE.md") for path in single)
    # non-existent string -> treated as a raw blob
    blob = load_input("just some instructions, not a path")
    (data,) = blob.values()
    assert "instructions" in _content(data)


def test_load_input_falls_back_to_text_when_matching_dir_has_no_artifacts(
    tmp_path, monkeypatch
):
    # A string can coincidentally name a real directory (e.g. a stray
    # __pycache__ in the caller's cwd) that holds nothing readable as an
    # agent artifact. That must fall back to raw text, not raise.
    monkeypatch.chdir(tmp_path)
    (tmp_path / "empty_dir").mkdir()
    (tmp_path / "empty_dir" / "binary.pyc").write_bytes(b"\x00\x01")

    files = load_input("empty_dir")
    (data,) = files.values()
    assert _content(data) == "empty_dir"
