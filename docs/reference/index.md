# API reference

The public API is small. Everything below is importable from the top-level
`agent_classifier` package.

| Symbol                                                                                                                | Kind     | Page                              |
| --------------------------------------------------------------------------------------------------------------------- | -------- | --------------------------------- |
| [`classify`][agent_classifier.classify]                                                                             | function | [Classifier (agent)](classify.md) |
| [`build_agent`][agent_classifier.build_agent]                                                                       | function | [Classifier (agent)](classify.md) |
| [`AgentClassification`][agent_classifier.AgentClassification]                                                       | model    | [Output schema](schema.md)        |
| [`Goal`][agent_classifier.Goal] · [`Capability`][agent_classifier.Capability] · [`Risk`][agent_classifier.Risk] | models   | [Output schema](schema.md)        |

Supporting modules — [taxonomy](taxonomy.md) (the allowed classification values),
[inputs](inputs.md) (how sources are normalised), [enrichment tools](tools.md), and the
[CLI](cli.md) — are documented on their own pages.

::: agent_classifier
    options:
      show_root_heading: false
      show_source: false
      members: false
