"""Input adapters.

Whatever represents the agent-under-analysis — a directory of files, a single
blob of text, or a structured dict — is normalised here into the mapping the
DeepAgents virtual filesystem expects: ``{path: FileData}``, passed as the
``files`` key when the agent is invoked.
"""

from __future__ import annotations

import json
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


def from_directory(path: str | Path) -> dict[str, Any]:
    """Read a directory of agent artifacts into the virtual filesystem.

    Binary, oversized, and tooling files are skipped. Paths are preserved
    relative to ``path`` under ``/agent/`` so the agent can navigate them.
    """
    root = Path(path)
    if not root.is_dir():
        raise NotADirectoryError(f"{root} is not a directory")

    files: dict[str, Any] = {}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in _SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if p.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        try:
            if p.stat().st_size > _MAX_BYTES:
                continue
            content = p.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeError):
            continue
        rel = p.relative_to(root).as_posix()
        files[f"/agent/{rel}"] = _make_file_data(content)

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

    - ``dict``  -> :func:`from_json`
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
        p = Path(source)
        if p.exists():
            return load_input(p)
        return from_text(source)

    raise TypeError(f"Unsupported input source type: {type(source)!r}")
