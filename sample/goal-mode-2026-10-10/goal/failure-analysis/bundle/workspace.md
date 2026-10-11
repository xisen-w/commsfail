# The shared workspace at the end of the record

Files the team produced or changed (inputs under data/ and related_work/ are left out):

- TASK.md
- check.sh
- code/analyze.py
- outputs/extraction_summary.json
- outputs/independent_review.md
- outputs/physics_reference_audit.json
- outputs/task_scores.csv
- outputs/task_scores.json
- report/images/data_overview.png
- report/images/rubric_means.png
- report/images/step_validation.png
- report/report.md

## Snapshots: what changed after which post

- start 06:11:49: A TASK.md, A check.sh
- seq 6 06:12:22: A outputs/independent_review.md
- seq 7 06:12:58: A code/analyze.py, A outputs/physics_reference_audit.json, A outputs/task_scores.csv, A outputs/task_scores.json, A report/images/data_overview.png, A report/images/rubric_means.png, A report/images/step_validation.png, A report/report.md
- seq 8 06:13:25: M code/analyze.py, A outputs/extraction_summary.json, M report/report.md
- seq 10 06:14:12: M outputs/independent_review.md, M report/report.md
- seq 12 06:15:10: M report/report.md
- seq 13 06:15:32: M report/report.md

## report/report.md

# Structured Hartree–Fock Calculation Tasks: Audit of the Supplied Moiré Paper

## Abstract

This report audits the machine-readable task record supplied for *AB-stacked MoTe₂/WSe₂* (arXiv:2111.01152). The stated research agenda concerns multi-step Hartree–Fock (HF) calculations over 15 quantum many-body papers. The available corpus, however, contains one paper directory and 16 annotated analytic task records. We therefore treat this work as a reproducible, single-paper audit of the supplied extraction and scoring data, not as evidence about LLM accuracy across 15 papers. We summarize the task inventory, calculate rubric statistics from the included annotations, and independently check key Hamiltonian and interaction expressions against the paper. The results indicate strong annotated physics-logic scores but identify concrete issues in early kinetic-Hamiltonian answers and reciprocal-lattice momentum reduction. No independent model run or numerical self-consistent HF calculation can be reproduced from the files provided.

## 1. Data and scope

The available target is `data/2111.01152`, containing the main article, supplementary material, a YAML task record, prompt templates, extractor/automatic-output Markdown, and notebooks. The main article describes the AB-stacked MoTe₂/WSe₂ continuum model and reports HF phase calculations. The YAML contains **16** task records spanning four continuum-model tasks, five basis-transformation tasks, and seven interaction/HF tasks (Figure 1). These are calculation steps associated with one source paper, not 15 independent papers. The distinction matters: repeated steps from one physical model do not provide independent-paper coverage or support generalization claims.

The machine-readable YAML was treated as the authoritative source for the task-level rubric scores, answers, and placeholder extraction fields. Across 105 placeholder slots, 81 contain an LLM value and 42 contain a human reference; reference fields are not expected for every prompt slot. Separate placeholder-level score annotations are available for Haining (84 numeric fields; mean 1.62), Will (76; mean 1.57), and Yasaman (84; mean 1.58). These named annotator scores are distinct from the six task-level rubric scores summarized below. All are annotations already present in the input. The analysis does not claim to have rerun the LLM that generated the answers, the original automated extractor, or human grading. Reproducibility is limited to parsing these files and recalculating descriptive statistics. The original notebooks are present but their full execution environment, model identifiers, prompts/runtime settings, and external dependencies are not established here.

![Task records by analytic stage](images/data_overview.png)

**Figure 1.** Distribution of the 16 annotated tasks by analytic stage. The categories are assigned deterministically from each task title in `code/analyze.py`.

## 2. Method

The analysis script (`code/analyze.py`) parses the YAML task list, exports one row per task with its six supplied rubric dimensions, computes per-dimension and overall means on the provided 0–2 scale, counts populated LLM/reference extraction fields, summarizes the separate annotator scores, and generates three PNG figures. It also exports a compact paper-grounded reference audit as JSON. Missing scores are excluded from the relevant mean. In the current records, the six task-level score fields are populated for all 16 tasks. The final-answer accuracy and mean-of-six score are compared per step in Figure 3.

For the physics check, we read Eq. (1) and the definitions immediately following it in `data/2111.01152/2111.01152.tex` (lines 55–79). The source Hamiltonian is a valley-resolved 2 × 2 block in bottom/top layer order:

\[
H_\tau(\mathbf r)=\begin{pmatrix}
-\dfrac{\hbar^2\mathbf k^2}{2m_{\mathfrak b}}+\Delta_{\mathfrak b}(\mathbf r)&\Delta_{\mathrm T,\tau}(\mathbf r)\\
\Delta^\dagger_{\mathrm T,\tau}(\mathbf r)&-\dfrac{\hbar^2(\mathbf k-\tau\boldsymbol\kappa)^2}{2m_{\mathfrak t}}+\Delta_{\mathfrak t}(\mathbf r)+V_{z\mathfrak t}
\end{pmatrix},\quad \tau=\pm1.
\]

The paper gives \((m_{\mathfrak b},m_{\mathfrak t})=(0.65,0.35)m_e\), \(\Delta_{\mathfrak t}=0\), and \(\Delta_{\mathfrak b}(\mathbf r)=2V_{\mathfrak b}\sum_{j=1,3,5}\cos(\mathbf g_j\cdot\mathbf r+\psi_{\mathfrak b})\). Its tunneling is \(\Delta_{\mathrm T,\tau}(\mathbf r)=\tau w[1+\omega^\tau e^{i\tau\mathbf g_2\cdot\mathbf r}+\omega^{2\tau}e^{i\tau\mathbf g_3\cdot\mathbf r}]\), with \(\omega=e^{i2\pi/3}\). The Coulomb kernel is dual-gate screened, \(V(q)=2\pi e^2\tanh(qd)/(\epsilon q)\), with \(d=5\) nm by default.

## 3. Results

Across all task-level rubric entries, the mean is **1.80/2**. Mean scores are 1.50 for in-paper support, 1.81 for prompt quality, 1.88 for following instructions, 2.00 for physics logic, 1.88 for mathematical derivation, and 1.75 for final-answer accuracy (Figure 2). These are summaries of the supplied scores and should not be read as an independent evaluation of model quality. The relatively lower in-paper and final-answer dimensions merit attention, especially because the task scores do not imply that every answer is physically correct.

![Mean rubric scores](images/rubric_means.png)

**Figure 2.** Mean of the supplied task scores for each rubric dimension (0–2 scale).

The source equation checks show that the early kinetic completions in `2111.01152_auto.md` are wrong: they put a \(\mathbf k-\tau\boldsymbol\kappa\) shift on the bottom-layer dispersion, assign shifts to both layers, and use positive kinetic signs. Eq. (1) instead has the unshifted bottom term \( -\hbar^2\mathbf k^2/(2m_{\mathfrak b}) \) and the shifted top term \( -\hbar^2(\mathbf k-\tau\boldsymbol\kappa)^2/(2m_{\mathfrak t}) \), with negative signs as printed. The separately stored YAML answer for kinetic task 2 does get the layer-specific shifts and signs right, although its supplied final-answer-accuracy score is only 1/2; that score appears inconsistent with the source check. The potential-only YAML answer for task 3 is consistent with that staged decomposition; the band offset is a separate term in the full Hamiltonian, and task 4 assigns it to the top-layer diagonal. The paper sets the top intralayer potential \(\Delta_{\mathfrak t}\) to zero; this does not remove the distinct band offset.

For the interaction analysis, the supplementary material provides the relevant source check (Eq. HF, `2111.01152_SM.tex`, around lines 110–117). In its hole convention it gives the one-body matrix as `−[h^(τ)]ᵀ` (after dropping the trace constant), followed by Hartree minus Fock contractions with prefactor `1/A`. The source-grounded mean-field operator is

\[
\hat{\mathcal H}^{\mathrm{HF}}=\hat{\mathcal H}_1+\frac{1}{A}\sum_{\substack{\mathbf k_\alpha,\mathbf k_\beta,\mathbf k_\gamma,\mathbf k_\delta\\ l_\alpha,l_\beta,\tau_\alpha,\tau_\beta}} V(\mathbf k_\alpha-\mathbf k_\delta)\left[\langle b^\dagger_{\mathbf k_\alpha l_\alpha\tau_\alpha}b_{\mathbf k_\delta l_\alpha\tau_\alpha}\rangle b^\dagger_{\mathbf k_\beta l_\beta\tau_\beta}b_{\mathbf k_\gamma l_\beta\tau_\beta}-\langle b^\dagger_{\mathbf k_\alpha l_\alpha\tau_\alpha}b_{\mathbf k_\gamma l_\beta\tau_\beta}\rangle b^\dagger_{\mathbf k_\beta l_\beta\tau_\beta}b_{\mathbf k_\delta l_\alpha\tau_\alpha}\right]\delta_{\mathbf k_\alpha+\mathbf k_\beta,\mathbf k_\delta+\mathbf k_\gamma}.
\]

The preceding Wick-expanded YAML task retains constants and paired bilinears with `1/(2V)`; the paired terms combine to the paper’s `1/A` expression after dummy-index relabeling, with constants omitted from the operator. The input task sequence represents these contractions symbolically, but its answers cannot be validated by score means alone. In particular, the YAML assigns the Hartree reciprocal-lattice delta reduction a math-derivation score of 1/2 and includes a comment that the delta simplification is incorrect. The supplemental paper allows enlarged commensurate unit cells, so momentum conservation involving reciprocal-lattice indices cannot be reduced without stating assumptions about that cell. The Hartree reduction record’s final-answer score is 2/2 despite its derivation score of 1/2; given the enlarged commensurate unit cells allowed in the supplement, the momentum reduction needs explicit assumptions and should be treated as unresolved rather than categorically wrong in every case. Other score fields also merit re-audit: task 8 gives `in_paper=0` for the raw particle-hole substitution explicitly defined in the supplement, and task 12 gives `in_paper=0` for the quadratic Hartree–Fock operator that the supplement presents. The YAML interaction operator (task 10) uses `V` in the prefactor where the paper uses area `A`; unless `V` is explicitly defined as area, the normalization is ambiguous. The particle-hole steps also require careful normal ordering: for a number-conserving one-body matrix, exchanging particle creation and annihilation operators generates a trace constant and a negative transpose in the hole basis.

![Per-step validation comparison](images/step_validation.png)

**Figure 3.** Supplied final-answer accuracy compared with the mean score across the six rubric dimensions for each task. Disagreement between a high aggregate score and a lower final-answer score illustrates why the rubric dimensions are retained separately.

## 4. Discussion and limitations

This dataset supports a useful workflow demonstration: a long analytic prompt sequence can be represented as structured task records with per-step answers and rubric annotations, then summarized consistently. It also demonstrates that high physics-logic or derivation annotations do not guarantee a correct final expression. Explicit checks against the source equation catch the kinetic shift/sign error, and the included reviewer comment catches a faulty momentum-conservation simplification. The audit therefore supports stepwise validation as a necessary part of a research calculation pipeline.

The scientific scope remains narrow. Only one target paper is present, so the stated 15-paper evaluation is not available; no across-paper accuracy, statistical uncertainty, or comparative LLM claim is justified. The source provides a physical HF study but the supplied records do not include the complete numerical setup needed to reproduce it: plane-wave cutoff and convergence details, full self-consistency initialization and stopping criteria, all sampled parameter grids, and raw iteration outputs are not established by this audit. We did not recalculate phase diagrams, gaps, or numerical HF solutions. The task-level score fields are separate from the three named placeholder annotators; their provenance and calibration are not fully recoverable from these files. Direct checks against the paper also expose inconsistencies in some scores (including the kinetic answer just noted), so the aggregate means describe the stored labels and should not be treated as calibrated ground truth. Some task records have blank answers or incomplete extraction fields, which further limits claims about end-to-end automated extraction.

## 5. Reproducibility and artifacts

From the workspace root, run `python3 code/analyze.py`. The script reads only the supplied YAML, writes `outputs/task_scores.json`, `outputs/task_scores.csv`, `outputs/extraction_summary.json`, and `outputs/physics_reference_audit.json`, and regenerates the figures referenced above. It requires Python 3, PyYAML, NumPy, and Matplotlib. The figures are PNG files under `report/images/`. The task scores, extraction-field counts and annotator summaries, and paper-grounded reference expressions are preserved in the outputs directory for inspection. The required workspace check verifies report/figure presence and report length; it does not validate scientific correctness.


## code/analyze.py (first 3000 characters)

```
#!/usr/bin/env python3
"""Reproducible summary of the single supplied paper's structured task data.

Reads the annotated YAML record and source equation, exports task-level rubric
scores and aggregate summaries, and renders report figures. It does not infer
missing papers or claim to rerun the original LLM.
"""
from pathlib import Path
import json
import yaml
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/2111.01152/2111.01152.yaml'
OUT = ROOT / 'outputs'
IMG = ROOT / 'report/images'
RUBRIC = ['in_paper', 'prompt_quality', 'follow_instructions', 'physics_logic',
          'math_derivation', 'final_answer_accuracy']

def main():
    records = yaml.safe_load(DATA.read_text(encoding='utf-8'))
    tasks = [r for r in records if isinstance(r, dict) and 'task' in r]
    rows = []
    for i, task in enumerate(tasks, 1):
        s = task.get('score') or {}
        row = {'step': i, 'task': task['task']}
        row.update({k: s.get(k) for k in RUBRIC})
        row['mean_score'] = float(np.mean([s[k] for k in RUBRIC if isinstance(s.get(k), (int, float))]))
        row['answer_present'] = bool(task.get('answer'))
        rows.append(row)
    vals = {k: [r[k] for r in rows if isinstance(r[k], (int, float))] for k in RUBRIC}
    # Summarize structured extraction fields separately from task rubric scores.
    placeholder_rows = []
    for task in tasks:
        for name, field in (task.get('placeholder') or {}).items():
            if not isinstance(field, dict):
                continue
            placeholder_rows.append({
                'task': task['task'], 'field': name,
                'llm_populated': field.get('LLM') not in (None, ''),
                'human_populated': field.get('human') not in (None, ''),
                'annotator_scores': field.get('score') or {}
            })
    annotators = sorted({a for row in placeholder_rows for a in row['annotator_scores']})
    extraction_summary = {
        'field_count': len(placeholder_rows),
        'llm_populated_count': sum(r['llm_populated'] for r in placeholder_rows),
        'human_reference_populated_count': sum(r['human_populated'] for r in placeholder_rows),
        'annotator_score_counts': {a: sum(isinstance(r['annotator_scores'].get(a), (int,float)) for r in placeholder_rows) for a in annotators},
        'annotator_score_means': {a: float(np.mean([r['annotator_scores'][a] for r in placeholder_rows if isinstance(r['annotator_scores'].get(a), (int,float))])) for a in annotators},
        'fields': placeholder_rows
    }
    (OUT / 'extraction_summary.json').write_text(json.dumps(extraction_summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    report = {
        'dataset': '2111.01152', 'source_file': 'data/2111.01152/2111.01152.yaml',
        'paper_count': 1, 'task_count': len(rows), 'rubric_scale': '0–2 (as supplied)',
        'task_rubric_means': {k: float(np.mean(v)
```
