"""Command-line interface: ``agent-classifier``.

Examples::

    agent-classifier ./path/to/agent            # classify a directory
    agent-classifier agent.md                    # classify a single file
    cat instructions.md | agent-classifier -     # classify text from stdin
    agent-classifier ./agent -o result.json      # write JSON to a file
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="agent-classifier",
        description="Analyse an AI agent's artifacts and emit a structured classification.",
    )
    parser.add_argument(
        "source",
        nargs="?",
        default="-",
        help="Path to an agent directory or file, or '-' to read text from stdin.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override the model id (default: $AGENT_CLASSIFIER_MODEL or "
        "anthropic:claude-sonnet-4-6).",
    )
    parser.add_argument(
        "--no-enrichment",
        action="store_true",
        help="Disable the MCP/skill lookup tools.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Write the JSON result to this file instead of stdout.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the classifier from the command line and print/write JSON."""
    # Imported lazily so `--help` works without the heavy agent stack.
    from .agent import classify

    args = build_parser().parse_args(argv)

    if args.source == "-":
        source: object = sys.stdin.read()
        if not str(source).strip():
            print("error: no input provided on stdin", file=sys.stderr)
            return 2
    else:
        source = Path(args.source)
        if not source.exists():
            print(f"error: no such path: {source}", file=sys.stderr)
            return 2

    result = classify(
        source,
        model=args.model,
        use_enrichment=not args.no_enrichment,
    )
    payload = result.model_dump_json(indent=2)

    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
