"""Prompts for the Classifier deep agent.

The prompt text lives in the adjacent Markdown files (``system.md`` and
``user.md``) so it reads and edits as prose. This module just loads them and
exposes them as strings:

- ``SYSTEM_PROMPT`` carries the methodology; it is placed in front of the
  DeepAgents default harness prompt.
- ``USER_INSTRUCTION`` is the per-run task message that points the agent at the
  artifacts on its virtual filesystem.
"""

from importlib import resources

_FILES = resources.files(__name__)

SYSTEM_PROMPT: str = (_FILES / "system.md").read_text(encoding="utf-8")
USER_INSTRUCTION: str = (_FILES / "user.md").read_text(encoding="utf-8")

__all__ = ["SYSTEM_PROMPT", "USER_INSTRUCTION"]
