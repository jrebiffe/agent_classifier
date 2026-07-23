"""Nox sessions mirroring CI. Run everything with ``nox``; a single session
with e.g. ``nox -s tests``.
"""

from __future__ import annotations

import nox

nox.options.sessions = ["lint", "typecheck", "security", "deps", "docs", "tests"]
nox.options.reuse_existing_virtualenvs = True

PYTHON = "3.11"
PATHS = ("src", "tests")


@nox.session(python=PYTHON)
def lint(session: nox.Session) -> None:
    """Ruff + flake8 lint and black/isort formatting checks."""
    session.install("-e", ".[dev]")
    session.run("ruff", "check", *PATHS)
    session.run("flake8", *PATHS)
    session.run("black", "--check", *PATHS)
    session.run("isort", "--check-only", *PATHS)


@nox.session(python=PYTHON)
def typecheck(session: nox.Session) -> None:
    """Static type checking with mypy."""
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
    """Docstring coverage with interrogate."""
    session.install("-e", ".[dev]")
    session.run("interrogate", "-c", "pyproject.toml", "src")


@nox.session(python=PYTHON)
def tests(session: nox.Session) -> None:
    """Run the test suite with coverage."""
    session.install("-e", ".[dev]")
    session.run("pytest")
