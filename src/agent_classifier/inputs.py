"""Input adapters.

Whatever represents the agent-under-analysis — a directory of files, a single
blob of text, or a structured dict — is normalised here into the mapping the
DeepAgents virtual filesystem expects: ``{path: FileData}``, passed as the
``files`` key when the agent is invoked.
"""

import json
import os
from pathlib import Path
from typing import Any

# Suffixes we treat as readable agent artifacts. "" covers extension-less files
# such as ``Dockerfile`` or ``LICENSE``.
_TEXT_SUFFIXES = {
    ".md",
    ".markdown",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".py",
    ".js",
    ".ts",
    ".sh",
    ".env",
    ".cfg",
    ".ini",
    ".xml",
    ".csv",
    "",
}
_SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
}
_MAX_BYTES = 200_000
# Safety cap on total directory entries walked, so a mistaken or coincidental
# path like "/" can't trigger a slow, unbounded scan of the whole filesystem
# (or read sensitive files far outside the intended agent directory).
_MAX_ENTRIES = 5_000

# Keys we know how to render from a structured (JSON/dict) description.
_INSTRUCTION_KEYS = ("instructions", "system_prompt", "systemPrompt", "prompt")
_MCP_KEYS = ("mcp_servers", "mcpServers", "servers")


def _make_file_data(content: str) -> dict[str, Any]:
    """Build a DeepAgents ``FileData`` entry, using the SDK helper if present."""
    try:
        from deepagents.backends.utils import create_file_data

        return dict(create_file_data(content))
    except Exception:  # pragma: no cover - fallback if the helper moves
        return {"content": content, "encoding": "utf-8"}


def from_text(blob: str, name: str = "/agent/agent.md") -> dict[str, Any]:
    """Wrap a single blob of text as one virtual file."""
    return {name: _make_file_data(blob)}


def _should_descend(child: Path, name: str, root_dev: int | None) -> bool:
    """Whether a subdirectory should be walked into.

    Excludes named tooling directories, and (like ``find -xdev``) anything on
    a different device than the root — real usage is /proc, /sys, and other
    mounted filesystems, whose pseudo-files can be unreadable, unbounded in
    size, or block forever on read.
    """
    if name in _SKIP_DIRS:
        return False
    if root_dev is None:
        return True
    try:
        return (child / name).stat().st_dev == root_dev
    except OSError:
        return False


def _read_as_file_data(p: Path) -> dict[str, Any] | None:
    """Read one artifact, or ``None`` if it's too big, unreadable, or binary."""
    if p.suffix.lower() not in _TEXT_SUFFIXES:
        return None
    try:
        if p.stat().st_size > _MAX_BYTES:
            return None
        content = p.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeError):
        return None
    return _make_file_data(content)


def from_directory(path: str | Path) -> dict[str, Any]:
    """Read a directory of agent artifacts into the virtual filesystem.

    Binary, oversized, and tooling files are skipped. Paths are preserved
    relative to ``path`` under ``/agent/`` so the agent can navigate them.
    """
    root = Path(path)
    if not root.is_dir():
        raise NotADirectoryError(f"{root} is not a directory")

    try:
        root_dev = root.stat().st_dev
    except OSError:
        root_dev = None

    files: dict[str, Any] = {}
    entries_seen = 0
    # os.walk (unlike Path.rglob + .is_file()) tolerates permission-denied
    # directories and unreadable entries — e.g. broken symlinks under /proc —
    # by skipping them instead of raising.
    for dirpath, dirnames, filenames in os.walk(root, onerror=lambda _err: None):
        current_dir = Path(dirpath)
        dirnames[:] = sorted(
            d for d in dirnames if _should_descend(current_dir, d, root_dev)
        )

        for name in sorted(filenames):
            p = current_dir / name
            file_data = _read_as_file_data(p)
            if file_data is not None:
                rel = p.relative_to(root).as_posix()
                files[f"/agent/{rel}"] = file_data

        # Counts directories actually visited (1 for this one) plus files
        # actually examined — not the not-yet-visited child directory names
        # in `dirnames`, which would over-count a directory merely for
        # having many siblings before any of them is ever walked. Checked
        # after fully handling this directory, so one that alone exceeds the
        # cap still gets read in full — the cap only stops further descent.
        entries_seen += 1 + len(filenames)
        if entries_seen > _MAX_ENTRIES:
            break

    if not files:
        raise ValueError(f"No readable agent artifacts found under {root}")
    return files


def from_json(obj: dict[str, Any]) -> dict[str, Any]:
    """Render a structured agent description into readable virtual files.

    Known keys (instructions, MCP servers, skills, tools) become their own
    file; anything else is preserved in ``metadata.json`` so no input is lost.
    """
    files: dict[str, Any] = {}
    rendered_keys: set[str] = set()

    for key in _INSTRUCTION_KEYS:
        if obj.get(key):
            files["/agent/instructions.md"] = _make_file_data(str(obj[key]))
            rendered_keys.add(key)
            break

    for key in _MCP_KEYS:
        if key in obj:
            files["/agent/mcp_servers.json"] = _make_file_data(
                json.dumps(obj[key], indent=2, ensure_ascii=False),
            )
            rendered_keys.add(key)
            break

    for key, fname in (("skills", "skills.json"), ("tools", "tools.json")):
        if key in obj:
            files[f"/agent/{fname}"] = _make_file_data(
                json.dumps(obj[key], indent=2, ensure_ascii=False),
            )
            rendered_keys.add(key)

    rest = {k: v for k, v in obj.items() if k not in rendered_keys}
    if rest:
        files["/agent/metadata.json"] = _make_file_data(
            json.dumps(rest, indent=2, ensure_ascii=False),
        )

    if not files:
        files["/agent/raw.json"] = _make_file_data(
            json.dumps(obj, indent=2, ensure_ascii=False),
        )
    return files


def load_input(source: str | Path | dict[str, Any]) -> dict[str, Any]:
    """Normalise any supported source into ``{path: FileData}``.

    - ``dict``  -> [`from_json`][agent_classifier.inputs.from_json]
    - ``Path`` / path string that exists -> directory or single file
    - other ``str`` -> treated as a raw text blob
    """
    if isinstance(source, dict):
        return from_json(source)

    if isinstance(source, Path):
        if source.is_dir():
            return from_directory(source)
        text = source.read_text(encoding="utf-8", errors="replace")
        return from_text(text, name=f"/agent/{source.name}")

    if isinstance(source, str):
        try:
            path = Path(source)
            is_path = path.exists()
        except (OSError, ValueError):
            # e.g. an embedded null byte or an over-long path: it's not a path,
            # so treat the string as raw agent text.
            is_path = False
        if is_path:
            try:
                return load_input(path)
            except ValueError:
                # The string coincidentally names a real directory (e.g. a
                # stray __pycache__) that holds nothing readable as an agent
                # artifact. Fall back to treating the string as raw text
                # rather than crashing on the coincidence.
                pass
        return from_text(source)

    raise TypeError(f"Unsupported input source type: {type(source)!r}")
