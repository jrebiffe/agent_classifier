# Configuration

## Model & provider

The classifier is provider-agnostic via LangChain's `init_chat_model`. Control it with
environment variables:

<!--- pyml disable md013 --->

| Variable                       | Default                       | Purpose                                                                                                              |
| ------------------------------ | ----------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `AGENT_CLASSIFIER_MODEL`       | `anthropic:claude-sonnet-4-6` | Any `init_chat_model` id — e.g. `anthropic:claude-opus-4-8` for depth, `openai:gpt-5.5`, or a local `ollama:` model. |
| `AGENT_CLASSIFIER_TEMPERATURE` | `0`                           | Sampling temperature. `0` keeps classification stable.                                                               |

<!--- pyml enable md013 --->

Using OpenAI or a local provider also needs its own package (e.g. `langchain-openai`)
and credentials.

You can also pass a model per call — an id string or a pre-built `BaseChatModel` — which
overrides the environment:

```python
from agent_classifier import classify

classify(source, model="anthropic:claude-opus-4-8")
```

See [`default_model`][agent_classifier.agent.default_model] and
[`build_agent`][agent_classifier.build_agent].

## Taxonomy

The allowed `domain`, `category`, and risk categories live in
[`taxonomy.py`][agent_classifier.taxonomy] as `StrEnum`s. Edit those lists to reshape
the classification — the [schema](reference/schema.md) and the system prompt both derive
their allowed values from them, so a change here flows through the whole pipeline
without touching anything else.

Keep enum *values* short, lowercase, and stable: they are the exact strings the model
must emit.

## Enrichment tools

[`tools.py`][agent_classifier.tools] holds a small **offline** knowledge base of common
MCP servers (`_MCP_KB`). To go further you can:

- **Extend the knowledge base** — add entries to `_MCP_KB`.
- **Replace the lookup** — swap
    [`lookup_mcp_server`][agent_classifier.tools.lookup_mcp_server] for a live registry
    or web-search lookup. The agent wiring in [`agent.py`][agent_classifier.agent]
    doesn't care how the tools are implemented.
- **Add your own tools** — pass `extra_tools=[...]` to
    [`build_agent`][agent_classifier.build_agent].

Disable enrichment entirely with `classify(..., use_enrichment=False)`.
