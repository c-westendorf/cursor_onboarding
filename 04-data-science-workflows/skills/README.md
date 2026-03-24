# Data Science Skills Library

Portable Claude Code skills for data science workflows. Each skill is a self-contained directory that can be copied into `~/.claude/skills/` and invoked immediately.

---

## Installation

Copy any skill into your Claude Code skills directory:

```bash
# Install a single skill
cp -r data-cleaning/ ~/.claude/skills/data-cleaning/

# Install all skills
cp -r data-cleaning/ data-quality-assurance/ missing-data-imputation/ eda-comprehensive/ feature-engineering/ ~/.claude/skills/
```

### Python Dependencies

```bash
pip install -r requirements.txt
```

For datasets over 1M rows, also install scaling dependencies:
```bash
pip install dask[dataframe] polars pyarrow
```

Skills activate when Claude detects a matching context in your conversation.

---

## Available Skills

| Skill | Job to Be Done | Trigger Contexts |
|-------|---------------|------------------|
| [data-cleaning](data-cleaning/) | Transform raw data into a structurally consistent DataFrame | Loading new datasets, starting projects, fixing dtype mismatches |
| [data-quality-assurance](data-quality-assurance/) | PASS/CONDITIONAL_PASS/FAIL quality gate | Before modeling, after ingestion, diagnosing model degradation |
| [missing-data-imputation](missing-data-imputation/) | Diagnose and fill missing values with audit trail | After cleaning identifies nulls, when QA flags completeness |
| [eda-comprehensive](eda-comprehensive/) | Discover distributions, relationships, and patterns | New dataset exploration, pre-modeling, debugging data issues |
| [feature-engineering](feature-engineering/) | Build model-ready feature matrix with featurewiz | Building features, after EDA, performance plateaus |

---

## Pipeline Order

These skills form a pipeline. Run them in this order:

```
Raw Data
  → data-cleaning → cleaned_df + cleaning_manifest.json
    → data-quality-assurance → qa_report.json (PASS / CONDITIONAL_PASS / FAIL)
      → IF FAIL: loop back or stop
    → missing-data-imputation → imputed_df + imputation_manifest.json
    → eda-comprehensive → eda_report.md + eda_findings.json
    → feature-engineering → X_train, X_test + feature_manifest.json + fitted pipeline
      → Model Training (use your preferred framework)
```

Each skill produces JSON artifacts that downstream skills consume. The handoff chain is:
- `cleaning_manifest.json` → consumed by QA, referenced by all downstream
- `qa_report.json` → gates the pipeline, consumed by imputation and EDA
- `imputation_manifest.json` → consumed by EDA and feature engineering
- `eda_findings.json` → consumed by feature engineering (recommended transforms, feature candidates)
- `feature_manifest.json` → consumed by model training (out of scope)

---

## Skill Structure

Each skill follows the Claude Code skill format:

```
skill-name/
├── SKILL.md              # Core workflow (<500 lines) with decision points
├── references/           # Supporting docs loaded as needed
│   ├── shared-pattern.md # Reusable patterns (audit, dtype classification)
│   └── specific-ref.md   # Skill-specific reference material
└── scripts/
    └── generate_*.py     # Deterministic artifact generation
```

---

## Shared References

The `_shared-references/` directory contains canonical versions of patterns used across multiple skills:

| Reference | Used By | Purpose |
|-----------|---------|---------|
| `dataset-audit-pattern.md` | cleaning, QA, EDA | 5-dimension data quality audit |
| `assumption-audit-pattern.md` | All 5 | Assumption challenge before decisions |
| `dtype-router.md` | cleaning, imputation, feature eng | Column type classification |
| `shape-aware-strategy.md` | cleaning, EDA | Data shape branching logic |
| `leakage-guard.md` | imputation, feature eng | Train-only fitting validation |

Each skill contains its own copy of the references it needs, so skills are fully portable. The `_shared-references/` directory is the source of truth during development.

---

## Modeling Task Coverage

Every skill handles these modeling contexts with specific branching logic:

| Task | Cleaning Behavior | QA Behavior | Imputation Behavior | EDA Behavior | Feature Eng Behavior |
|------|-------------------|-------------|---------------------|--------------|---------------------|
| Classification | Validate target as categorical | Check class balance | Never impute target; check class-missingness correlation | Per-class distributions, ANOVA | Target encoding (fold-based), featurewiz default |
| Regression | Validate target as numeric | Check target distribution | Never impute target | Scatter + Pearson/Spearman | log1p, polynomials, transform_target=True |
| Time-series | Sort by timestamp, detect gaps | Validate temporal completeness | Backward-only interpolation | ACF/PACF, ADF, decomposition | Lag features, rolling windows, cyclical encoding |
| NLP | Normalize encoding, clean whitespace | Validate text distributions | "[MISSING]" token | Token frequency, doc length | TF-IDF, text_length, word_count |
| Clustering | Focus on feature consistency | Check for zero-variance | Missingness as signal | Pairwise features, Hopkins | Manual only (no target for featurewiz) |
