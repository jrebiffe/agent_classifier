# Inputs

Adapters that normalise whatever represents the agent-under-analysis — a directory, a
text blob, or a structured dict — into the virtual filesystem the deep agent reads.
[`load_input`][agent_classifier.inputs.load_input] is the dispatcher the CLI and
`classify()` use.

::: agent_classifier.inputs
