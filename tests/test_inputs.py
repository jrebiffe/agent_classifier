"""Input adapters: directory, blob, and structured dict."""

import os
from pathlib import Path

import pytest

import agent_classifier.inputs as inputs_module
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


def test_from_directory_tolerates_permission_denied_subdirectory(tmp_path, monkeypatch):
    # A subdirectory os.walk can't list (e.g. chmod 000, or a permission wall
    # under /proc when a mistaken path like "/" is passed) must be skipped,
    # not crash the whole walk.
    (tmp_path / "readable.md").write_text("hello", encoding="utf-8")
    locked = tmp_path / "locked"
    locked.mkdir()
    (locked / "secret.md").write_text("secret", encoding="utf-8")

    real_scandir = os.scandir

    def flaky_scandir(path="."):
        if Path(path) == locked:
            raise PermissionError(13, "Permission denied", str(path))
        return real_scandir(path)

    monkeypatch.setattr(os, "scandir", flaky_scandir)

    files = from_directory(tmp_path)
    assert any(p.endswith("readable.md") for p in files)
    assert not any("secret" in p for p in files)


def test_from_directory_does_not_cross_filesystem_boundaries(tmp_path, monkeypatch):
    # Mirrors `find -xdev`: a subdirectory on a different device (a mount
    # point — in real usage /proc, /sys, or any other mounted filesystem)
    # must not be descended into, regardless of _SKIP_DIRS.
    (tmp_path / "readable.md").write_text("hello", encoding="utf-8")
    other_mount = tmp_path / "other_mount"
    other_mount.mkdir()
    (other_mount / "elsewhere.md").write_text("should not be read", encoding="utf-8")

    real_stat = Path.stat

    class _FakeStat:
        def __init__(self, real):
            self._real = real
            self.st_dev = real.st_dev + 1

        def __getattr__(self, name):
            return getattr(self._real, name)

    def fake_stat(self, *args, **kwargs):
        result = real_stat(self, *args, **kwargs)
        return _FakeStat(result) if self == other_mount else result

    monkeypatch.setattr(Path, "stat", fake_stat)

    files = from_directory(tmp_path)
    assert any(p.endswith("readable.md") for p in files)
    assert not any("elsewhere" in p for p in files)


def test_from_directory_stops_after_max_entries(tmp_path, monkeypatch):
    # Bounds a mistaken or coincidental path like "/" to a fast, partial scan
    # instead of an unbounded walk of the whole filesystem. The cap is
    # checked between directories, so each subdirectory visited before the
    # cap trips is still read in full — only further descent is stopped.
    monkeypatch.setattr(inputs_module, "_MAX_ENTRIES", 3)
    for i in range(10):
        sub = tmp_path / f"dir{i}"
        sub.mkdir()
        (sub / "file.md").write_text(f"content {i}", encoding="utf-8")

    files = from_directory(tmp_path)
    assert 0 < len(files) < 10


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
