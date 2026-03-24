---
name: skill-blueprint
description: Universal framework for designing, critiquing, and extending any AI-executable skill library. Read this before writing a new skill in any domain. Not a skill itself — it describes how skills are built, what makes them well-formed, and how to bootstrap a new domain library from scratch.
---

## What This Is

This document is the first-principles specification distilled from the data science skills library in `../skills/`. It answers four questions applicable to ANY domain — data science, deep learning, time series forecasting, NLP, MLOps, or beyond:

1. **Vocabulary:** What are the four building blocks and how do they relate?
2. **Principles:** What non-negotiable rules govern a well-formed skill?
3. **Template:** What is the canonical format for writing a skill? (The "sequence manifest")
4. **Governance:** How do you scope, critique, test, and bootstrap a new domain library?

The `../skills/` directory is the reference implementation. The DS pipeline is the worked example of this framework applied.

---

## Section 1 — Vocabulary

Four terms used throughout this document. Get these right and everything else follows.

| Term | Definition | Does Not Include |
|---|---|---|
| **Playbook** | A documented, repeatable procedure: ordered steps with explicit preconditions, decision forks, checkpoints, and a terminal artifact | Vague guidelines, ad-hoc analysis, one-off scripts |
| **Skill** | A Claude-executable package containing a playbook (`SKILL.md`), reusable references, and scripts. Installable to `~/.claude/skills/` | Infrastructure, models, databases — those are inputs/outputs |
| **Reference** | A reusable building block (algorithm, pattern, checklist) called *by* a skill. Produces no terminal artifact, executes no workflow independently | A full skill, a standalone script, domain configuration |
| **Pipeline** | An ordered sequence of skills where each skill's output artifact is the next skill's input contract | A single skill, a monolithic notebook, an unordered set of steps |

**Key distinction:** A playbook is the *procedure*; a skill is the *packaged, executable playbook*. The scoping decision — is this a standalone skill, a step inside an existing one, or a reference? — is Section 4's decision tree.

---

## Section 2 — Design Principles (8 Rules)

These apply to any domain. None are data-science-specific.

Each principle: **rule** / **violation looks like** / **why it matters**

---

**1. Single Job-to-be-Done**
Rule: One skill = one transformation of system state. Name it as `verb-noun`. The Scope Boundary section explicitly lists what it refuses.
Violation: A skill called `data-preparation` that cleans, imputes, and encodes — no clear handoff point between sub-jobs.
Why: When scope is ambiguous, downstream skills cannot trust what happened. The manifest becomes unreliable.

**2. Precondition / Postcondition Contracts**
Rule: Every skill declares verifiable preconditions (what must be true before it starts) and postconditions (what it guarantees after it ends). These are testable assertions, not goals.
Violation: Prerequisites listed as "clean data" — untestable. A precondition is: "upstream manifest exists; `schema_version == '1.0'`; artifact record count >= 1."
Why: Without explicit contracts, degraded upstream state silently contaminates all downstream work.

**3. Explicit Variance Surface**
Rule: Every skill declares the dimensions it must branch on (e.g., task type, data shape, framework, compute target) and shows how behavior differs per dimension value. A skill that handles only one variant is incomplete.
Violation: A training skill that only documents PyTorch behavior and ignores JAX/TF variants.
Why: Skills installed in a library must handle the full range of contexts the domain encounters.

**4. Artifact at Every State Change**
Rule: Any step that irreversibly changes the system's state (transforms data, trains weights, writes schema) produces a named, verifiable terminal artifact. The artifact is the only way downstream steps know what happened.
Violation: A skill that prints a summary to stdout but writes no artifact — the next skill has no provenance.
Why: Reproducibility requires that every state change be reconstructible from the artifact alone.

**5. Stateful Operations Are Scoped**
Rule: Any operation that learns from data (fitting, training, calibration) must be bounded to a declared subset (train split, calibration set, fold). The boundary is verified before the terminal artifact is written.
Violation: Fitting a scaler on the full dataset before splitting — test-set statistics contaminate training.
Why: Leakage is the most common silent failure in ML pipelines. An unverified scope boundary is a debt that compounds.

**6. Quality Bar Over Completeness**
Rule: A skill halts loudly on blocking conditions. Every checkpoint has an explicit HALT message. Partial output is worse than no output.
Violation: Catching exceptions silently, logging a warning, continuing — the manifest shows zero errors when the step actually failed.
Why: Silent degradation creates false confidence. A downstream skill making decisions on corrupted upstream output amplifies the error.

**7. Canonical Reference Library**
Rule: Any pattern used by two or more skills in a domain lives in `_shared-references/` as the single source of truth. Each skill carries its own copy for portability; copies are derived from the canonical source, never evolved independently.
Violation: Two skills with slightly different versions of the same validation function because one was edited in place.
Why: Reference drift creates subtle behavioral inconsistencies across a pipeline that are hard to debug.

**8. Self-Contained Portability**
Rule: A skill directory must function when copied in isolation to `~/.claude/skills/`. It must not depend on sibling skills, parent directory structure, or runtime imports from other skills.
Violation: A skill that runs `from ..data_cleaning.scripts import validate_names` — breaks immediately when installed standalone.
Why: Skills are distribution units. The install contract is `cp -r {skill}/ ~/.claude/skills/{skill}/`.

---

## Section 3 — The Playbook Template (Sequence Manifest)

This is the canonical fill-in-the-blank format for any skill in any domain. Every required section is listed with annotation. Write this before writing any code.

```markdown
---
name: {verb-noun-identifier}
description: {What this skill transforms. When to invoke it. What it accepts.
              What it produces. ≤3 sentences. No jargon — describe observable behavior.}
---

## Overview
{Why this step exists in the pipeline. What breaks if it is skipped. What guarantee
it provides to whatever runs next. 3–5 sentences of prose.}

---

## When to Activate
{5–8 observable trigger conditions. Each must be detectable from conversation context
or system state without asking the user. Use concrete signals, not vague categories.}
- {Observable signal 1}
- {Observable signal 2}

---

## Preconditions
What must be true before this skill begins:
- [ ] {Testable assertion — e.g., "upstream_artifact.json exists and schema_version == '1.0'"}
- [ ] {Testable assertion — e.g., "input record count >= 1"}
- [ ] {Testable assertion — e.g., "train/test split indices defined if any fitting occurs"}

Each precondition must have a HALT condition in Step 0 if violated.

---

## Prerequisites

### Library Dependencies
```
# Tier 1 — Domain core (required by all skills in this library)
{package}>={version}

# Tier 2 — Skill-specific (required only by this skill)
{package}>={version}

# Tier 3 — Optional branches (required only when {condition})
{package}>={version}    # used when {condition}
```
See `requirements.txt` at the library root for the full dependency manifest.
See `../skill-blueprint/requirements-template.txt` for the 4-tier format.

### Infrastructure Requirements
- **Compute:** {CPU-only / GPU recommended / GPU required / TPU}
- **Memory:** {minimum RAM for expected input size}
- **Disk:** {scratch space — e.g., "2× input size for intermediate artifacts"}
- **OS packages:** {non-Python dependencies, if any}
- **Environment:** {base Docker image or conda env — e.g., "python:3.10-slim"}

### Upstream Artifacts
- `{artifact_name.json}`: produced by `{skill-name}` — required fields: {field_1}, {field_2}
- `{split_indices}`: required if this skill fits or trains any component

---

## Variance Surface
Declare every dimension this skill branches on. Every declared dimension must have
≥2 values described. If behavior is identical across all values of a dimension, remove it.

| Dimension | Values | How behavior differs |
|---|---|---|
| {Dimension 1} | {A / B / C} | {what changes in the workflow per value} |
| {Dimension 2} | {A / B} | {what changes} |

---

## Workflow

### Step 0 — Context Classification and Upstream Validation (always first)

**Context Classification:** Before any processing, classify the variance dimensions
declared above. This determines which code paths the remaining steps follow.

```
classify {Dimension 1}: detect {A} or {B} or {C} from input context
classify {Dimension 2}: detect {A} or {B} from input context
log: "Running {skill-name} | {Dimension1}={value} | {Dimension2}={value}"
```

**Upstream Validation:** If this skill consumes an upstream artifact:
```
load {upstream_artifact.json}
assert schema_version == "1.0"
assert artifact record count matches current input count
assert required fields {field_1}, {field_2} are present
IF any assertion fails:
  HALT: "Upstream validation failed: {exact condition}. Investigate before proceeding."
```

---

### Step 1 — {Name: verb phrase}

**Goal:** {One sentence: what state the system is in after this step completes.}

**Pre-step assertion:** {What must be true before this step runs — testable.}

**Reference:** `references/{reference-file.md}` *(omit if not applicable)*

**Actions:**

*Branch on {Dimension}:*

**IF {value A}:**
```
{runnable instructions or code — not pseudocode}
```

**IF {value B}:**
```
{runnable instructions or code}
```

> **At {edge condition — e.g., very large input / no GPU}:** {What to do differently.}

**Checkpoint:**
> - [ ] Assert: {specific, testable assertion}
> - [ ] PASS: {exact description of "step is done"}
> - [ ] HALT: {condition} → "Exact error message text."
> - [ ] WARN: {condition where proceed-but-document is correct}

**Artifact produced:** Store `{variable or intermediate file}` for terminal artifact.

**Post-step assertion:** {What is guaranteed to be true after this step completes.}

---

### Step 2 — {Name}
{Repeat Step 1 structure. A well-scoped skill has 4–8 steps total.}

---

[... Steps 3–N ...]

---

## Terminal Artifact

The skill's permanent output — the verifiable record of what it did. The next skill
in the pipeline validates this before processing.

Run `scripts/generate_{name}_artifact.py`:

```python
from scripts.generate_{name}_artifact import generate_artifact
artifact = generate_artifact(
    {required_field_1}={value_1},
    {required_field_2}={value_2},
    output_path="{noun}_artifact.json",
)
```

CLI:
```bash
python scripts/generate_{name}_artifact.py \
  --{flag-1} {value} \
  --output {noun}_artifact.json
```

**Required fields in every terminal artifact:**
```json
{
  "schema_version": "1.0",
  "skill_name":     "{verb-noun-identifier}",
  "timestamp":      "{ISO-8601 UTC}",
  "{domain-universal field 1}": ...,
  "{domain-universal field 2}": ...,
  "{skill-specific field}": ...
}
```

Domain-universal fields are defined by the domain's manifest envelope (see Section 6).
Skill-specific fields are informational — downstream skills must not depend on them for
correctness, only the universal fields.

---

## Edge Cases

| Edge Case | Detection | Action |
|---|---|---|
| Empty input | record count == 0 | HALT: "Input is empty. Skill cannot proceed." |
| Single record | record count == 1 | WARN: "Single record — statistical steps will be skipped." |
| All-null dimension | {specific field} 100% missing | HALT / WARN / PROCEED per domain rules |
| Upstream schema mismatch | schema_version != "1.0" | WARN: log, proceed with reduced trust |
| {Domain-specific case 1} | {detection} | {action} |
| {Domain-specific case 2} | {detection} | {action} |

*(minimum 6 rows; first 4 are universal — include in every skill)*

---

## Postconditions
After successful completion, this skill guarantees:
- [ ] {Testable assertion about output state}
- [ ] {Testable assertion about terminal artifact}
- [ ] Terminal artifact exists, is valid JSON, and contains all required fields

## Quality Bar
This skill run is "done" when ALL of the following are true:
- [ ] All checkpoints passed or explicitly documented as WARN
- [ ] Terminal artifact exists and validates against schema
- [ ] {Domain-specific assertion 1}
- [ ] {Domain-specific assertion 2}
*(6–9 items total)*

## Scope Boundary
This skill does NOT:
- {Job 1} → handled by `{other-skill-name}`
- {Job 2} → handled by `{other-skill-name}`
- {Job 3} → handled by `{other-skill-name}`
*(4–6 items; each names the responsible skill)*

## Downstream
Run after this skill completes:
1. **`{next-skill}`** — {why it comes next; what fields of the terminal artifact it consumes}
```

---

## Section 4 — Scoping: Skill vs. Step vs. Reference

**Decision tree — stop at the first branch that matches:**

```
Q1: Does this procedure change the state of the system
    (transform data, update weights, write schema, produce an artifact)?
    NO  → It is a reference pattern or a QA check. Not a standalone skill.

Q2: Does the state change need a verifiable artifact so downstream steps
    can trust what happened?
    NO  → It belongs as a step inside an existing skill, not a standalone skill.

Q3: Is its "When to Activate" trigger meaningfully distinct from every
    existing skill's trigger in this domain?
    NO  → Add it as a new step to the closest existing skill.

Q4: Does it produce a stateful artifact (fitted model, trained weights,
    calibrated config, serialized transformer) that must be versioned and
    reproduced independently of other skills?
    YES → Almost certainly a standalone skill. Continue to Q5.

Q5: Adding it to an existing skill would push SKILL.md past 500 lines?
    YES → Standalone skill. Use Section 3 template.
    NO  → Evaluate as a subsection of the nearest existing skill first.
```

**What belongs in `_shared-references/`:** Any function or pattern called identically by ≥2 skills, producing no terminal artifact and having no task-specific branching of its own. Examples: upstream validation, input classification, leakage guard, shared glossary.

**Naming convention:**
- Skill directories: `verb-noun` kebab-case (e.g., `train-model`, `evaluate-forecast`)
- Terminal artifacts: `{noun}_manifest.json`, `{noun}_report.json`, `{noun}_checkpoint/`
- Scripts: `generate_{noun}_artifact.py` or `generate_{noun}_manifest.py`

---

## Section 5 — Critique Process (Explore → Select → Refine)

*For DESIGNING a skill, not for executing one.*

### Phase 1: Explore — Answer These Before Writing One Line

**Job definition:**
- Can you express the job as a single `verb + noun`?
- Which skill precedes this in the pipeline? Which follows it?
- What does the Scope Boundary say upfront — what does this skill refuse to do?

**Contracts:**
- What artifact does this skill consume? What does it produce?
- What happens if the upstream artifact is degraded (failed QA, partial write, wrong schema version)?
- What fields must the terminal artifact expose for the next skill to validate it?

**Variance surface:**
- What are all the dimension values this skill must branch on?
- For each value, does the workflow actually behave differently? If not, collapse that dimension.
- What is the worst-case combination of dimension values — can the skill still produce a valid terminal artifact?

**State scope:**
- Does this skill call any learning operation (fit, train, calibrate)?
- If yes: what variable or index gates that operation to the correct subset?
- How is that gate verified before the terminal artifact is written?

### Phase 2: Select — Structural Choices

For each candidate workflow step, ask four questions:
1. Does it change system state? (If no → it is a check, not a step)
2. Does it need a Checkpoint with explicit HALT/WARN/PASS? (If no → combine with adjacent step)
3. Does it produce a value stored in the terminal artifact? (If no → reconsider its presence)
4. Can it be expressed in ≤60 lines? (If no → extract to `references/`)

If all four are yes → it is a step.

**Five-axis comparison** for choosing between implementation options (ranked by importance):
1. **Safety** — stateful scope is verifiable before terminal artifact is written
2. **Scale** — degrades gracefully at worst-case input size without breaking the skill
3. **Artifact faithfulness** — terminal artifact captures enough to reproduce the run
4. **Variance coverage** — works for ≥3 values of each declared dimension without special-casing
5. **Reference reuse** — calls an existing `_shared-references/` function rather than reimplementing

### Phase 3: Refine — Pre-Merge Quality Check

Before submitting a skill for merge, a reviewer answers YES to all items in Section 7.

---

## Section 6 — Bootstrapping a New Domain Library

Use this procedure to build a skill library for a domain not yet covered.

**Step 1 — Define the pipeline order**
List the end-to-end sequence of state transformations for this domain:

| Domain | Example pipeline |
|---|---|
| Data Science | Cleaning → QA → Imputation → EDA → Feature Engineering |
| Deep Learning | Data Loading → Preprocessing → Architecture → Training → Evaluation → Export |
| Time Series | Ingestion → Stationarity → Decomposition → Features → Model Selection → Backtest |
| NLP Fine-tuning | Corpus Loading → Tokenization → Splitting → Fine-tuning → Evaluation → Export |
| MLOps | Schema Registration → Training Run → Versioning → Shadow Deploy → A/B Gate → Promote |

Each transformation in the sequence is a candidate skill.

**Step 2 — Define the variance dimensions**
Every skill in this domain must branch on these dimensions. Define them upfront:

| Domain | Variance dimensions |
|---|---|
| Data Science | task type (classification/regression/time-series/NLP/clustering), data shape (wide/tall/sparse/nested) |
| Deep Learning | framework (PyTorch/JAX/TF), model type (CNN/RNN/Transformer/MLP), compute (CPU/GPU/TPU) |
| Time Series | frequency (daily/weekly/monthly), seasonality (known/unknown), horizon (short/medium/long) |

**Step 3 — Define the domain's manifest envelope**
Five fields are universal across all domains:
```json
{ "schema_version": "1.0", "skill_name": "...", "timestamp": "...",
  "record_count": N, "artifact_id": "..." }
```
Add domain-specific required fields:

| Domain | Domain-specific required fields |
|---|---|
| Data Science | `row_count`, `column_count`, `column_list` |
| Deep Learning | `epoch_count`, `final_loss`, `hardware_config`, `model_checkpoint_path` |
| Time Series | `target_frequency`, `horizon`, `backtest_window`, `coverage_probability` |

**Step 4 — Define the shared reference library**
Identify what knowledge ≥2 skills will share:

| Domain | Shared references |
|---|---|
| Data Science | `handoff-validation.md`, `leakage-guard.md`, `dtype-router.md`, `shape-aware-strategy.md` |
| Deep Learning | `gradient-flow-guide.md`, `loss-function-selector.md`, `regularization-patterns.md` |
| Time Series | `stationarity-tests-guide.md`, `decomposition-methods.md`, `backtest-window-strategies.md` |

**Step 5 — Define the infrastructure contract**
Document the compute environment all skills in this domain share:

| Domain | Compute | Memory | Key OS deps | Base environment |
|---|---|---|---|---|
| Data Science | CPU | 4 GB | libgomp1 | `python:3.10-slim` |
| Deep Learning | GPU (8 GB VRAM) | 16 GB | CUDA 12.x, libcudnn | `pytorch/pytorch:2.x-cuda12.x` |
| Time Series | CPU | 8 GB | libgomp1 | `python:3.10-slim` |

**Step 6 — Create the library scaffold**
```
{domain-name}/
├── README.md                    ← pipeline diagram + install + manifest chain
├── requirements.txt             ← Tier 1+2 dependencies (see requirements-template.txt)
├── _shared-references/          ← canonical reference files for this domain
├── {skill-1}/
│   ├── SKILL.md
│   ├── references/              ← local copies of shared references + skill-specific refs
│   ├── scripts/
│   │   └── generate_{name}_artifact.py
│   └── requirements.txt         ← Tier 3 overrides (skill-specific only, if needed)
└── {skill-2}/...
```

**Cross-domain integration:** When a skill from one domain hands off to a skill from another (e.g., DS feature matrix feeds a DL training skill), only the 5 universal envelope fields are trusted across the boundary. Domain-specific fields are informational.

---

## Section 7 — New Skill Checklist (17 items)

All 17 must be checked before a skill is merged to the library.

**Definition and Structure (5)**
- [ ] SKILL.md frontmatter: `name` and `description` only; description states transformation, trigger, input, output in ≤3 sentences
- [ ] All required sections present in order: Overview, When to Activate, Preconditions, Prerequisites, Variance Surface, Workflow, Terminal Artifact, Edge Cases, Postconditions, Quality Bar, Scope Boundary, Downstream
- [ ] SKILL.md ≤500 lines; overflow extracted to named files in `references/` with `**Reference:**` links at point of use
- [ ] `scripts/generate_{name}_artifact.py` exists, standalone CLI with `--help`, no cross-skill imports
- [ ] `requirements.txt` declares all library dependencies in the 4-tier format; infrastructure requirements documented in `## Prerequisites`

**Contracts and Correctness (4)**
- [ ] Preconditions are testable assertions with explicit HALT in Step 0 if violated
- [ ] Terminal artifact contains all 5 universal envelope fields (`schema_version: "1.0"`, `skill_name`, `timestamp`, `record_count`, `artifact_id`) plus declared domain-specific required fields
- [ ] All stateful operations (fit/train/calibrate) are bounded to declared subset; boundary is verified before terminal artifact is written
- [ ] Degraded upstream (failed QA, partial artifact, wrong schema) produces explicit HALT — not silent continuation

**Variance and Testing (4)**
- [ ] Variance Surface table is complete; every declared dimension has ≥2 values with distinct described behavior
- [ ] Skill has been run with ≥3 values of each declared variance dimension; all produce valid terminal artifacts
- [ ] Terminal artifact passes downstream validation (`validate_upstream()` equivalent) from the perspective of the next skill
- [ ] Domain pipeline regression test passes with this skill inserted at its declared position

**Documentation and Integration (4)**
- [ ] Domain `README.md` pipeline diagram updated with new skill at correct position
- [ ] Domain `README.md` artifact chain updated with new skill's output and what consumes it
- [ ] Domain `README.md` variance coverage table updated with new skill's column
- [ ] Any new pattern used by ≥2 skills has been promoted to `_shared-references/` and copied into each consuming skill's `references/`
