# agent-classifier

A **Classifier agent** that analyses *other* AI agents and returns a structured
classification of them: goals, domain, category, capabilities, autonomy level, data
sensitivity, and risks — all validated against a fixed schema.

It is built on [DeepAgents](https://github.com/langchain-ai/deepagents) (the LangChain
agent harness). The agent under analysis is loaded onto the deep agent's virtual
filesystem; the classifier reads the artifacts, looks up what referenced MCP servers and
skills actually do, and emits the schema via DeepAgents' `response_format`.

```python
from agent_classifier import classify

result = classify("./path/to/agent")   # a directory, file, text blob, or dict
print(result.domain, result.overall_risk)
print(result.model_dump_json(indent=2))
```

## Where to go next

- **[Getting started](getting-started.md)** — install, set your API key, and run your
    first classification.
- **[Tutorial](tutorial.md)** — how the pipeline works, end to end, on a real sample
    agent.
- **[Configuration](configuration.md)** — swap the model/provider, reshape the taxonomy,
    extend the enrichment tools.
- **[FAQ](faq.md)** — providers, keys, offline use, common errors, cost.
- **[API reference](reference/index.md)** — generated from the docstrings.

!!! tip "For LLMs"

    A machine-readable index of this site is published at
    [`/llms.txt`](https://jrebiffe.github.io/agent_classifier/llms.txt), with the full
    content at
    [`/llms-full.txt`](https://jrebiffe.github.io/agent_classifier/llms-full.txt).
