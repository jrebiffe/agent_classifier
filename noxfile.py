"""Nox sessions mirroring CI.

Run everything with ``nox``, or a single session with e.g. ``nox -s tests``.
"""

import shutil
import subprocess

import nox

nox.options.sessions = [
    "lint",
    "typecheck",
    "security",
    "deps",
    "docs",
    "markdown",
    "tests",
]
nox.options.reuse_existing_virtualenvs = True

PYTHON = "3.13"
PATHS = ("src", "tests")


def _markdown_files() -> list[str]:
    # git-tracked only, so caches/build artifacts (e.g. .pytest_cache/README.md)
    # never leak in — the same universe pre-commit's `types: [markdown]` lints.
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git executable not found on PATH")
    out = subprocess.run(  # noqa: S603 — fixed argv, no external input
        [git, "ls-files", "*.md"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return sorted(out.splitlines())


@nox.session(python=PYTHON)
def lint(session: nox.Session) -> None:
    """Run ruff (lint + format check), flake8, black --check, and isort."""
    session.install("-e", ".[dev]")
    session.run("ruff", "check", *PATHS)
    session.run("ruff", "format", "--check", *PATHS)
    session.run("flake8", *PATHS)
    session.run("black", "--check", *PATHS)
    session.run("isort", "--check-only", *PATHS)


@nox.session(python=PYTHON)
def typecheck(session: nox.Session) -> None:
    """Run mypy static type checking."""
    session.install("-e", ".[dev]")
    session.run("mypy")


@nox.session(python=PYTHON)
def security(session: nox.Session) -> None:
    """Bandit code scan and pip-audit dependency scan."""
    session.install("-e", ".[dev]")
    session.run("bandit", "-q", "-c", "pyproject.toml", "-r", "src")
    session.run("pip-audit", "--progress-spinner=off")


@nox.session(python=PYTHON)
def deps(session: nox.Session) -> None:
    """Dependency hygiene with deptry."""
    session.install("-e", ".[dev]")
    session.run("deptry", ".")


@nox.session(python=PYTHON)
def docs(session: nox.Session) -> None:
    """Docstring coverage (interrogate) and conventions (pydocstyle)."""
    session.install("-e", ".[dev]")
    session.run("interrogate", "-c", "pyproject.toml", "src")
    session.run("pydocstyle", "src")


@nox.session(python=PYTHON)
def markdown(session: nox.Session) -> None:
    """Check Markdown formatting, structure, and prose quality."""
    session.install("-e", ".[dev]")
    md_files = _markdown_files()
    session.run("mdformat", "--number", "--wrap", "88", "--check", *md_files)
    session.run("pymarkdown", "-c", ".pymarkdown.json", "scan", *md_files)
    session.run("proselint", "check", *md_files)


@nox.session(python=PYTHON)
def tests(session: nox.Session) -> None:
    """Run the test suite with coverage."""
    session.install("-e", ".[dev]")
    session.run("pytest")
