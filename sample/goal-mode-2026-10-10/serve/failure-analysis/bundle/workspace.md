# The shared workspace at the end of the record

Files the team produced or changed (inputs under data/ and related_work/ are left out):

- TASK.md
- check.sh
- code/analyze.py
- outputs/audit_summary.json
- outputs/task_scores.csv
- report/images/data_overview.png
- report/images/rubric_scores.png
- report/images/task_validation.png
- report/report.md

## Snapshots: what changed after which post

- start 06:17:16: A TASK.md, A check.sh
- seq 4 06:17:56: A code/analyze.py
- seq 5 06:18:13: A outputs/audit_summary.json, A outputs/task_scores.csv, A report/images/data_overview.png, A report/images/rubric_scores.png, A report/images/task_validation.png, A report/report.md
- seq 10 06:18:40: M code/analyze.py, M outputs/audit_summary.json, M report/images/task_validation.png, M report/report.md
- seq 14 06:18:58: M report/report.md

## report/report.md

# A Single-Paper Audit of Hartree–Fock Task Annotations for MoTe₂/WSe₂

## Abstract

This report audits the Hartree–Fock (HF) calculation material supplied for arXiv:2111.01152. The available bundle contains a target paper, supplementary source, a staged prompt sequence, and a YAML file with 16 task records and rubric annotations. It does not contain the 15-paper corpus described in the broad research objective, nor a set of model-run transcripts, independently regenerated answers, or outcome-level scores from multiple language models. Consequently, the present work is a reproducible audit of one paper’s structured tasks and provided annotations; it cannot establish general LLM accuracy or the efficacy of prompt templates across research papers. We reconstruct the central HF decoupling, summarize the encoded scores, and identify where supplied metadata and source equations constrain interpretation.

## 1. Scope and data

The only structured case in `data/` is paper 2111.01152, on AB-stacked MoTe₂/WSe₂ moiré heterobilayers. The directory includes main text and supplementary TeX/PDF files, prompt and extraction markdown, and a YAML annotation file. That YAML parses into 17 top-level records: one metadata record and 16 staged tasks covering continuum single-particle terms, second quantization, particle-hole transformation, interaction construction, Wick decoupling, and momentum reduction. Five PDFs are present in `related_work/`, but no corresponding structured task annotations or explicit links establish that they are the other 14 target papers; they are therefore not treated as evaluated cases.

The reproducible script `code/analyze.py` reads the supplied YAML directly, calculates per-criterion means from encoded task-level scores (scale 0–2), exports task-level CSV and JSON, and regenerates three PNG figures. These are descriptive summaries of existing annotations, not new model experiments or independent human scoring. The score counts below use only numeric values present in the YAML; the six rubric fields have complete numeric task scores for all 16 records.

![Available structured evidence compared with the task’s stated corpus size](images/data_overview.png)

## 2. HF formulation and analytic validation

In the paper’s hole basis, the single-particle contribution (up to a constant) is `−b† hᵀ b`, where the paper defines the hole one-body matrix as `−hᵀ`. The interaction is a density-density Coulomb term with prefactor `1/(2A)`, momentum-conservation delta, and potential `V(kα−kδ)`. For a Slater-determinant density matrix, the standard Wick/HF decoupling of an ordered quartic product is

`b†₁ b†₂ b₃ b₄ → ⟨b†₁b₄⟩b†₂b₃ + ⟨b†₂b₃⟩b†₁b₄ − ⟨b†₁b₃⟩b†₂b₄ − ⟨b†₂b₄⟩b†₁b₃ − ⟨b†₁b₄⟩⟨b†₂b₃⟩ + ⟨b†₁b₃⟩⟨b†₂b₄⟩`.

The one-body terms are the direct (Hartree) contractions with positive sign and exchange (Fock) contractions with negative sign. Relabeling dummy indices in the two direct contributions and in the two exchange contributions combines equivalent terms, canceling the original factor of one half and producing the paper’s `1/A` coefficient for the bilinear HF interaction. The reference equation (supplementary TeX, Eq. (HF)) retains the momentum-conservation delta. This is the decisive algebraic cross-check for the output. The constant contractions are omitted from the reported one-body mean-field Hamiltonian; they remain relevant when computing total energy.

Translation symmetry needs careful treatment: the source states that a density-matrix element can be nonzero when its momentum difference is a reciprocal vector of the resulting unit cell. This condition allows density-wave order and does not imply equality of the two momenta. Reducing such deltas to equality would incorrectly discard commensurate symmetry-breaking states. The task annotations themselves flag a concern about delta simplification in the Hartree reduction. This report therefore treats the source equation and its explicit reciprocal-vector condition as validation authority rather than assuming every later staged answer is correct.

## 3. Annotation results

Across 16 tasks, the supplied rubric scores average: in-paper coverage 1.50/2, prompt quality 1.81/2, following instructions 1.88/2, physics logic 2.00/2, math derivation 1.88/2, and final-answer accuracy 1.75/2. These are recorded rubric values, not re-evaluated answers. In particular, YAML task 16 has all six scores set to 2 but its `answer` field is empty. It is therefore retained in the recorded-score aggregate, but excluded from the answer-bearing accuracy calculation: the other 15 tasks average 26/15 = 1.73/2 for final-answer accuracy. This inconsistency prevents interpreting the full 16-task score mean as accuracy of supplied answers. Physics logic is at the maximum in every staged record, while the main observed shortfalls occur in coverage, prompt/answer alignment, derivation, and final-answer ratings. The initial kinetic-Hamiltonian record has a low final-answer score and comments about basis ordering and whether a momentum or real-space form was requested. The particle-hole transformation and Wick’s-theorem records have zero in-paper coverage because these derivation steps are not presented as separate equations in the paper, despite their correctness scores being high. Thus the in-paper criterion is not a proxy for scientific correctness.

![Mean score by encoded rubric criterion](images/rubric_scores.png)

Among the 15 tasks with a nonempty answer, the recorded final-answer ratings are heterogeneous; most receive 2/2, with lower ratings clustered around the continuum setup and intermediate noninteracting-Hamiltonian transformations. Task 16 has no answer, so its 2/2 annotation is rubric-only and provides no evidence about answer accuracy. These ratings are encoded in the source file, not blind validation results. The notebook files suggest a workflow for extraction and scoring, but the supplied bundle does not document independent scorer calibration, inter-rater agreement, model identity/version, decoding settings, or repeated trials. The human-reference fields are incomplete and sometimes contain question marks, so the data are not sufficient to recompute a consistent inter-rater score.

![Task-level recorded final-answer ratings; task 16 is unanswered and shown as NA](images/task_validation.png)

## 4. Limitations and conclusion

The supplied evidence supports a narrow conclusion: a single paper has been decomposed into 16 useful sequential HF tasks, and its annotations show high scores for the supplied physics-logic criterion alongside lower scores for some setup and derivation tasks. The paper’s HF expression can be checked analytically against the standard Hartree-minus-Fock contraction and its stated momentum-selection rule. These findings do not test whether LLMs reliably perform research-level HF calculations, whether structured prompts mitigate research bottlenecks, or how results generalize across 15 papers. No raw model answers or independent recalculation dataset are provided, and the five related-work PDFs cannot be assumed to fill that gap.

Reproduction is limited by the input bundle: `code/analyze.py` requires Python 3, PyYAML, and Matplotlib, and summarizes static YAML annotations without access to original scoring judgments or model execution metadata. A broader evaluation would require the remaining paper-specific task sets, complete model outputs, scorer instructions and calibration, and a preregistered method for comparing correct derivations and step-level errors. Until then, aggregate numbers here should be interpreted as descriptive properties of the supplied annotation file, not estimates of LLM performance.


## code/analyze.py (first 3000 characters)

```
#!/usr/bin/env python3
"""Reproducibly audit the supplied single-paper HF task annotations."""
from pathlib import Path
import json
import yaml
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/2111.01152/2111.01152.yaml"
OUT = ROOT / "outputs"
FIG = ROOT / "report/images"
OUT.mkdir(exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

records = yaml.safe_load(DATA.read_text())
tasks = [r for r in records if isinstance(r, dict) and r.get("task")]
metrics = ["in_paper", "prompt_quality", "follow_instructions", "physics_logic", "math_derivation", "final_answer_accuracy"]
rows = []
for i, task in enumerate(tasks, 1):
    scores = task.get("score", {})
    rows.append({"index": i, "task": task["task"], **{m: scores.get(m) for m in metrics},
                 "answer_present": bool(task.get("answer")),
                 "has_human_reference": any(v.get("human") for v in task.get("placeholder", {}).values() if isinstance(v, dict))})

summary = {
    "source": "data/2111.01152/2111.01152.yaml",
    "paper_id": "2111.01152",
    "records_including_metadata": len(records),
    "task_count": len(tasks),
    "papers_with_structured_records": 1,
    "target_papers_in_task_description": 15,
    "score_scale": "0-2, as encoded in source YAML",
    "metrics": {},
    "answer_bearing_task_count": sum(bool(r.get("answer_present")) for r in rows),
    "tasks": rows,
}
for metric in metrics:
    vals = [r[metric] for r in rows if isinstance(r[metric], (int, float))]
    summary["metrics"][metric] = {"n": len(vals), "mean": sum(vals)/len(vals) if vals else None,
                                  "max": 2, "sum": sum(vals)}
answer_accuracy = [r["final_answer_accuracy"] for r in rows
                   if r["answer_present"] and isinstance(r["final_answer_accuracy"], (int, float))]
summary["answer_bearing_final_accuracy"] = {
    "n": len(answer_accuracy), "mean": sum(answer_accuracy)/len(answer_accuracy) if answer_accuracy else None,
    "max": 2, "sum": sum(answer_accuracy),
    "excluded_unanswered_tasks": [r["index"] for r in rows if not r["answer_present"]],
}
(OUT / "audit_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
(OUT / "task_scores.csv").write_text("index,task," + ",".join(metrics) + "\n" + "".join(
    f'{r["index"]},"{r["task"].replace(chr(34), chr(34)*2)}",' + ",".join(str(r[m]) for m in metrics) + "\n" for r in rows))

# Figure 1: what is actually present versus the stated target corpus.
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(["Structured paper\nrecords supplied", "Papers stated\nin task goal"], [1, 15], color=["#3478a8", "#c7d5df"])
ax.set_ylabel("Number of papers")
ax.set_title("Available structured evidence")
ax.set_ylim(0, 16)
for x, y in enumerate([1, 15]): ax.text(x, y + .35, str(y), ha="center", fontweight="bold")
fig.tight_layout(); fig.savefig(FIG / "data_overview.png", dpi=180); plt.close(fig)

# Figure 2: dimensions of the supplied task-level rubric.
me
```
