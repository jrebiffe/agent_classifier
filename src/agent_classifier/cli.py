"""Command-line interface: ``agent-classifier``.

Examples::

    agent-classifier ./path/to/agent            # classify a directory
    agent-classifier agent.md                    # classify a single file
    cat instructions.md | agent-classifier -     # classify text from stdin
    agent-classifier ./agent -o result.json      # write JSON to a file
"""

import argparse
import sys
from pathlib import Path
from typing import cast

STDIN_MARKER = Path("-")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="agent-classifier",
        description="Analyse an AI agent's artifacts and emit a structured classification.",
    )
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        default=STDIN_MARKER,
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
        type=Path,
        default=None,
        help="Write the JSON result to this file instead of stdout.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """Run the classifier from the command line and print/write JSON."""
    args = build_parser().parse_args(argv)

    if args.source == STDIN_MARKER:
        source: object = sys.stdin.read()
        if not str(source).strip():
            sys.exit("error: no input provided on stdin")
    else:
        source = cast(Path, args.source)
        if not source.exists():
            sys.exit(f"error: no such path: {source}")

    # Imported here so `--help` and the error paths above never pay for loading
    # the heavy agent / deepagents stack.
    from .agent import build_agent, classify

    agent = build_agent(model=args.model, use_enrichment=not args.no_enrichment)
    result = classify(source, agent=agent)
    payload = result.model_dump_json(indent=2)

    if args.output:
        args.output.write_text(payload, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
