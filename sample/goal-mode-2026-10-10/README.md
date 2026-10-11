# Goal Run versus serve-style communication

Two real, paired ResearchClawBench `Information_002` pilot runs from
2026-10-10. Xisen requested publication of these owned experiment traces and
their corresponding analysis. This export contains **sanitized copies**, not
byte-identical original logs. `manifest.json` records original and published
SHA-256 values for every exported file and the redaction counts.

| Sample | Harness | Agents | Room posts | Final model-judged incidents |
|---|---|---:|---:|---:|
| [`goal/`](goal/) | original `goal run`, source `e0481bd` | 2 | 15 | 3 |
| [`serve/`](serve/) | experimental `--communication-mode serve`, source `c553ebacc67e045cb754b6825f6118feb2648d11` | 2 | 14 | 1 |

Both use `codex:gpt-6-luna`, low reasoning via the image wrapper, image
`sha256:d724b9126ded4a0d8238c9abf28b215913efa0cc0445e03ca59b14d30ae4d397`,
an eight-minute limit, a 500k fresh-token target, the same two-role coordination
prompt, and a strict `/^DONE$/` completion trigger. Budgets are evaluated at
turn boundaries and are not real-time hard ceilings. The experimental source
commit is provenance, not a claim that the branch was published or shipped.

## What is included

Each arm has:

- `record-goal/` or `record-serve/`: directly loadable Goal Run record, including `episode.json`,
  `room.ndjson`, `wakes.ndjson`, `checks.ndjson`, `exit.json`, and every
  `agents/<seat>/turn-NNN.jsonl` harness output stream.
- `agent-sessions/<seat>/session.jsonl`: the agent's own serialized session,
  including rendered inputs/tool responses. This complements the turn stream;
  the default loader does not read this directory. Encrypted reasoning payloads
  are omitted. A logged input is evidence of availability, not understanding.
- `failure-analysis/A.json` and `B.json`: the two saved independent model
  annotations; `final.json` is the judge's adjudication, and `annotation.json`
  is the corresponding pipeline record. These were produced during the pilot,
  not regenerated for publication, and are not human gold labels.
- `failure-analysis/bundle/`: the sanitized task, timeline, per-agent action
  evidence, workspace inventory, codebook, and index used by the annotators.

`fresh-comparison.json` is the original paired trace audit (sanitized), including
observed delivery timing and exact visible sequence sets. The accompanying
`annotation-timestamp.patch` records the local timestamp compatibility fix used
to build the historical annotation bundles; it is evidence, not an applied
library change. Both original analyses have **no scientific grading verdict**.

## Read and validate

From the repository root after installing `.[dev]`:

```sh
commsfail trace sample/goal-mode-2026-10-10/goal/record-goal
commsfail trace sample/goal-mode-2026-10-10/serve/record-serve
commsfail analyse sample/goal-mode-2026-10-10/goal/record-goal --annotator facts_v1 -o /tmp/goal-facts.json
commsfail validate /tmp/goal-facts.json
pytest
```

The ordinary offline annotators run through the existing contract matrix.
The archived A/B/judge records are additionally checked against their own
bundle indexes and the actual published message sequences. Offline analysis
may differ from the historical model annotations: they are different methods.

## Limits and interpretation

This is **one task, one run per arm**, with several mechanisms changed together,
sequential execution, no fixed model seed, and possible host-load interference.
The 3-versus-1 count is descriptive, not a causal or statistical improvement
claim. Both basic checks passed, but checked report length and figure files,
not scientific correctness. The supplied task snapshot covers one paper and
16 scored tasks despite the benchmark description requesting 15 papers.

The baseline contains crossed reports, a review-finding inversion, and closing
before the requested final review reply arrives. The serve variant has a
partially omitted reviewer request. Both contain shell-quoting changes to
intended messages. See the judged incidents and exact post/action references
before drawing conclusions. None of these counts is a network packet-loss rate.

The variant reuses selected serve communication behavior. It does not recreate
the assistants' entire historical conversation, permissions, tools, or Cloud
environment. This sample also does not replace the later multi-task paper results.

## Publication boundary

Room, message, principal, instance, artifact and session identifiers are
consistently pseudonymized; host paths are normalized. Credential fields,
tokens, bearer/JWT strings, URLs, email addresses and encrypted payloads are
removed or replaced when encountered. The identifier mapping is not published.
No agent home, auth/config file, environment file, or workspace Git database is
copied. A secret scan is a supplementary check, not proof that arbitrary raw
agent homes would be safe to publish. Commands and outputs remain historical
evidence, not instructions to execute.
