# Real experiment samples

[Goal Run and serve-style communication pilot, 2026-10-10](goal-mode-2026-10-10/README.md)
contains two consented, sanitized experimental records, their per-agent turn
streams and session transcripts, and the matching independent failure analyses.

These are research samples, not synthetic ground truth. The offline annotator
contract tests also run on their `record-goal/` and `record-serve/` directories. Small synthetic fixtures
remain in [`tests/fixtures/`](../tests/fixtures/README.md).

## ProgramBench

[xsv multi-agent traces, 2026-10-15](xsv-2026-10-15/README.md) contains nine
Goal Run records with two, three, or four Codex agents. This is a local,
byte-preserving selection of core logs, with a SHA-256 manifest. See its
README for the included evidence and known message-linking limitations.

[yj multi-agent traces, 2026-10-15](yj-2026-10-15/README.md) contains three
Goal Run records with two, three, and four Codex agents, one run per configuration.
It includes core logs, task instructions, and a SHA-256 manifest. See its README
for validation results and known parser limitations.
