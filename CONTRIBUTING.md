# Contributing

Thanks for helping improve the Agentic Universe research graph and tooling.

## Research and graph changes

1. Prefer primary sources. Link the paper, dataset, code, or experiment directly.
2. State what was read (abstract, full text, code, or replication) and what was not checked.
3. Separate a source's reported result from this project's interpretation. Add limitations and counterevidence.
4. Add candidate graph changes to `evolution/proposals/` first. Keep new claims `to_test` unless independently replicated in the relevant setting.
5. Check node and edge identifiers, endpoints, evidence links, and relationship direction.
6. Update the research note and graph together; do not leave source or rationale only in a conversation.

## Before opening a pull request

```bash
python tools/knowledge_graph.py validate
# For a new patch, run this before applying it to the canonical graph:
python tools/knowledge_graph.py check-proposal evolution/proposals/<your-patch>.json
python -m unittest discover -s tests -v
```

The CI workflow runs structural graph validation and unit tests for pull requests to `main`. Add a regression test when changing validation behavior. Avoid committing credentials, local runtime data, or generated logs.

## Review standard

A valid JSON graph is necessary but not sufficient. Reviewers should be able to trace each external claim to its source and distinguish author-reported results from independent evidence. Do not promote claims based only on citation count, model-generated summaries, or one unreplicated benchmark.
