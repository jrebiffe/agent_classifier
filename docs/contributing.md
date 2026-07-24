# Contributing

## Dev setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install          # run the checks on every commit
```

## Quality gates

Everything is wired through **pre-commit** and mirrored in CI and **nox**:

```bash
pre-commit run --all-files  # lint, format, type, security, docstrings, prose
nox                         # the full suite in isolated envs
pytest                      # tests with coverage (gate: 90%)
```

The stack: `ruff` + `flake8` (lint), `ruff format` + `isort` + `black --check` (format),
`mypy` (strict types), `bandit` + `pip-audit` + `detect-secrets` (security), `deptry`
(deps), `interrogate` + `pydocstyle` (docstrings), `codespell` + `pymarkdown` +
`proselint` (prose/markdown), and `pytest` + `hypothesis` (tests). All tool config lives
in `pyproject.toml`.

## Working on the docs

```bash
pip install -e ".[docs]"
mkdocs serve                # live preview at http://127.0.0.1:8000
nox -s docs                 # build with --strict (the docs gate)
```

Docs pages live under `docs/` and are Markdown. The API reference is generated from
docstrings by [mkdocstrings](https://mkdocstrings.github.io/) — so keep docstrings
accurate; that's what readers see. Write docstrings in Google style (`Args:` /
`Returns:`) and use mkdocstrings cross-references (`` [`name`][fully.qualified.path] ``)
rather than reStructuredText roles.

!!! note

    `docs/` is excluded from `mdformat` and `pymarkdown` — they corrupt or misparse
    mkdocstrings `:::` blocks, Material admonitions, and autorefs cross-references (for
    example, `mdformat` escapes `[text][ref]` cross-references into broken literal text).
    `proselint` still lints the docs' prose, and `mkdocs build --strict` is the real docs
    gate: it fails on broken links and unresolved API references.

## Docstring coverage & style

`interrogate` enforces 100% docstring coverage and `pydocstyle` enforces PEP 257
conventions (both scoped to `src/`). Run them via `nox -s docstrings`.
