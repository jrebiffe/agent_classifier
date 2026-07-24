# FAQ

## Which model providers are supported?

Any provider LangChain's `init_chat_model` supports — Anthropic (default), OpenAI,
local/open-weight via Ollama or vLLM, and others. Set `AGENT_CLASSIFIER_MODEL` (see
[Configuration](configuration.md)). Non-Anthropic providers need their integration
package installed (e.g. `langchain-openai`) and their own credentials.

## Does it need network access / an API key?

Running a classification calls a hosted model, so yes — unless you point
`AGENT_CLASSIFIER_MODEL` at a **local** model (e.g. `ollama:...`), in which case nothing
leaves your machine. The built-in enrichment tools are fully **offline** (a local
knowledge base), so they add no network calls of their own.

## Can I run it fully offline / air-gapped?

Yes: use a local provider (Ollama/vLLM) for the model and keep the default offline
enrichment. No part of the default pipeline requires the internet.

## What does "No readable agent artifacts found under …" mean?

You pointed it at a directory that contained no readable text artifacts (only binaries,
or everything was filtered out). Check the path, or pass the content as text instead.
Note that `load_input` won't cross filesystem boundaries and caps how many entries it
walks, so pointing it at something like `/` won't scan your whole disk — it just won't
find agent artifacts.

## Is Python 3.14 supported?

Yes. The project requires 3.13+ and CI runs on both 3.13 and 3.14.

## How reliable is the structured output?

The schema is enforced via the model's structured-output mode (`response_format`), so
you always get a valid [`AgentClassification`][agent_classifier.AgentClassification]
or an error — never malformed JSON. Every goal and risk carries an `evidence` field to
keep the content grounded, and `missing_info` captures what the input didn't reveal
instead of inventing it. Run at temperature `0` (the default) for stability.

## How do I add a new category or risk type?

Add a member to the relevant `StrEnum` in [`taxonomy.py`][agent_classifier.taxonomy].
Nothing else needs to change.

## How much does a classification cost / how long does it take?

It's a single agent run whose cost and latency depend on the model you choose and the
size of the input. Use a smaller/faster model (e.g. Sonnet) for cheap runs and a larger
one (e.g. Opus) when you want deeper analysis; disable enrichment
(`use_enrichment=False`) to cut a few tool-calling round-trips.

## Can I inspect or drive the agent myself?

Yes — [`build_agent`][agent_classifier.build_agent] returns the compiled
DeepAgents/LangGraph agent. `classify()` is just a convenience wrapper around building
it and reading `result["structured_response"]`.
