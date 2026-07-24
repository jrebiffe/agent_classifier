# Getting started

## Requirements

- Python **3.13+**
- An API key for your model provider (Anthropic by default).

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .            # add ".[dev]" for the test dependencies
cp .env.example .env        # then fill in your ANTHROPIC_API_KEY
```

Set your key in the environment (or in `.env`):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Your first classification

### From Python

```python
from agent_classifier import build_agent, classify

agent = build_agent()
result = classify("./path/to/agent", agent=agent)  # directory, file, text, or dict
print(result.domain, result.category, result.overall_risk, result.confidence)

for risk in result.risks:
    print(risk.severity, risk.category, "-", risk.description)

# the whole thing as JSON
print(result.model_dump_json(indent=2))
```

`classify()` returns a validated
[`AgentClassification`][agent_classifier.AgentClassification]. See the
[output schema](reference/schema.md) for every field.

### From the command line

```bash
agent-classifier ./path/to/agent            # classify a directory
agent-classifier agent.md -o result.json    # classify a file, write JSON
cat instructions.md | agent-classifier -    # classify text from stdin
agent-classifier ./agent --no-enrichment    # skip the lookup tools
```

## What counts as input?

Anything that describes the agent you want analysed — see
[`load_input`][agent_classifier.inputs.load_input]:

- a **directory** of artifacts (system prompt / `CLAUDE.md`, `.mcp.json`, `skills/`,
    settings) — the richest input;
- a single **file** or a raw **text blob**;
- a structured **dict** with keys like `instructions`, `mcpServers`, `skills`.

Next: walk through a full run in the **[tutorial](tutorial.md)**.
