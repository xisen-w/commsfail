# Jev

Pure Jev typed-decision failure annotation, alongside `standard`. It uses the same
six failure classes and 37 patterns, but a different unit and output schema:
`commsfail/jev-annotation.v1`. It does not manufacture the free-form explanations
required by the standard schema. Read [PROTOCOL.md](PROTOCOL.md) for the method and limits.

Install the repository with Python 3.10+ and `pip install -e '.[dev]'`. Runtime
uses only the existing jsonschema dependency and Python's standard library.
Docker and Codex login are unnecessary for this direct OpenRouter backend.

```bash
python -m commsfail.annotators.jev smoke --out /private-output/jev-smoke \
  --key-file /private/path/to/openrouter-key
python -m commsfail.annotators.jev annotate-batch /path/to/records \
  --out /private-output/jev-research-v1 \
  --pattern 'research__*__n[234]__r1' --workers 2 --retries 3 \
  --key-file /private/path/to/openrouter-key
python -m commsfail.annotators.jev validate /private-output/jev-research-v1
```

Alternatively supply `OPENROUTER_API_KEY`. Never put the key value on the command
line. The model is pinned to `typesafe/jev-1.13`; `--effort` is inapplicable.

The unchanged command resumes cached requests and skips validated complete runs.
`summary.json` reports completed, failed and pending cases. Each case contains
`annotation.json`, `verdict.json`, A/B/judge decisions, agreement, a grade-blind
bundle, the input manifest, and a `requests/` audit trail. `COMPLETE.json` checksums
the output. Configuration, input or code changes require a fresh output root.

Agreement counts post/class slots. It is not standard incident-span F1 or a human
accuracy estimate. `explanation: null` is deliberate. Uncertain evidence, uncertain
severity and unresolved attribution remain explicit. Source records can be complete
while evidence supplied to individual decisions is partial; coverage is recorded.

Run the offline regression suite with `pytest`. Live checks are deliberately separate.
