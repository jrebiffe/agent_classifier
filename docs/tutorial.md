# Tutorial

This walks through what happens when you classify an agent, end to end.

## How the pipeline works

A classification runs in three stages — input adaptation, agent construction, and the
run itself (there's a rendered diagram of this flow in the project
[README](https://github.com/jrebiffe/agent_classifier#how-it-works)):

1. **[`inputs.load_input`][agent_classifier.inputs.load_input]** normalises whatever you
    pass — a directory of agent files, a single text blob, or a structured dict — into
    the DeepAgents virtual filesystem.
2. **[`build_agent`][agent_classifier.build_agent]** builds one deep agent with the
    built-in filesystem tools (`ls`, `read_file`, `grep`, …), the enrichment tools, and
    `response_format=AgentClassification`.
3. The agent reads everything, optionally calls
    [`lookup_mcp_server`][agent_classifier.tools.lookup_mcp_server] /
    [`lookup_skill`][agent_classifier.tools.lookup_skill] to understand referenced
    components, then returns the schema.

## A worked example

The repository ships a sample agent under `tests/fixtures/sample_agent/` — a
customer-support refund assistant with a Stripe MCP server (refunds), a Postgres orders
database, and Slack. Classify it:

```python
from agent_classifier import build_agent, classify

agent = build_agent()
result = classify("tests/fixtures/sample_agent", agent=agent)
print(result.title, "—", result.summary)
print("domain:", result.domain, "| category:", result.category)
print("autonomy:", result.autonomy_level, "| data sensitivity:", result.data_sensitivity)
print("overall risk:", result.overall_risk, f"(confidence {result.confidence})")
```

## Reading the result

A few fields are worth understanding:

- **`goals`** — the agent's primary, secondary, and *implicit* goals, each with an
    `evidence` string pointing back at the input. Nothing is asserted without a quote or
    file reference to back it.
- **`risks`** — grounded risk findings using the [taxonomy](reference/taxonomy.md)'s
    categories and a severity. For the refund agent you should expect a
    `financial_transaction` risk (Stripe refunds) and likely `compliance_pii` (customer
    data in Postgres).
- **`overall_risk`** — an aggregate, not just the single worst item.
- **`missing_info`** — anything the input didn't reveal. The classifier records gaps
    here and lowers `confidence` instead of guessing.

!!! note "Enrichment"

    When the agent under analysis references an MCP server the classifier isn't sure about,
    it calls the lookup tools to learn the server's *real* capabilities (e.g. that a
    `github` server can push code and merge PRs) before scoring risk. Disable this with
    `build_agent(use_enrichment=False)` or the CLI's `--no-enrichment`.

Next: change the model, taxonomy, or enrichment in
**[Configuration](configuration.md)**.
