# Information_002

## Research Task

### Task Description
Input multi-step analytic calculation tasks of the Hartree-Fock method from 15 quantum many-body physics research papers; output correctly derived Hartree-Fock Hamiltonians, calculation step scores, and automated results of paper information extraction and step scoring; the scientific goal is to verify whether large language models (LLMs) can accurately perform research-level theoretical physics calculations via structured prompt templates and mitigate key bottlenecks in the research process.

### Available Data Files
- **2111.01152** [feature_data] (`data/2111.01152`): The target scientific paper defining the AB-stacked MoTe2/WSe2 moiré system and its Hamiltonian parameters.

---

## Workspace

Your workspace is: `/workspace`

- All file reads and writes must stay inside this directory.
- `data/` and `related_work/` are read-only — do not modify them.

### Layout
- `data/` — Input datasets (read-only)
- `related_work/` — Reference papers (read-only)
- `code/` — Write your analysis code here
- `outputs/` — Save intermediate results
- `report/` — Write your final report here
- `report/images/` — Save all figures here as **PNG files** (`.png` only)

### Deliverables
1. Analysis code in `code/`
2. Intermediate results in `outputs/`
3. A comprehensive research report as `report/report.md`:
   - Methodology, results, and discussion
   - Academic writing style
   - **Figures are mandatory** — generate plots and save to `report/images/`, reference them with relative paths: `images/figure_name.png`
   - Include at minimum: data overview, main results, and validation/comparison plots

### Technical Notes
- Install Python packages as needed before using them.
- Use matplotlib, seaborn, or any suitable visualization library. Save all figures as **PNG files** (`.png`). Do not use uncommon formats such as PPM, BMP, TIFF, or EPS — these cannot be rendered in the report viewer.
- Ensure code is reproducible.

---

## How to check your work

Run `bash check.sh` in this directory. It must pass before you say DONE.
When check.sh passes and the report is complete, say DONE in the Room.

Coordination experiment instructions (identical task appendix in both arms):
You are one of two collaborating agents. codex-1 initially owns analysis code,
outputs and the report. codex-2 owns independent validation and review notes.
Agree concrete scope through the Room; inspect existing claims before editing.
Do not duplicate your teammate's changes. Use @codex-1 or @codex-2 explicitly for
handoffs, findings and requests; include both names for shared decisions.
State paths and checks performed. Reviewers should independently verify claims
and tell the owner what needs correction. Change file ownership only by an
explicit handoff. Keep room messages concise and avoid acknowledgment loops.
When waiting, end your turn; never start another wait/serve responder or poll
idly. The harness supplies the next message. Follow the harness instruction on
whether it auto-posts your final reply; never publish that reply twice.
Only codex-1 announces completion, after codex-2 has reviewed the final artifact
and check.sh passes. Completion must be an entire standalone message DONE.
Discuss unfinished work without using DONE as a completion signal. Do not claim
scientific requirements are met when the supplied data cannot support them.
Record missing scope and reproducibility limits explicitly in the report.

