# Box 2: Enforcement Check

[Home](../../README.md) > [Core Concepts](../README.md) > [Decision Flow](README.md) > Enforcement Check

---

## The Question

**Should violating this knowledge block production, fail CI, or require explicit review?**

---

## What This Tests

Whether the system should **fail loudly** when this knowledge is violated.

- If yes → the knowledge needs **hard enforcement** (code/CI)
- If no → the knowledge can be **soft guidance** (rules/skills)

---

## Decision Criteria

### Answer YES if:

| Criterion | Example |
|-----------|---------|
| Silent failure is unacceptable | Data leakage corrupts model evaluation |
| Violations could cause real harm | Security vulnerabilities, data exposure |
| This protects correctness | Schema validation before processing |
| Trust depends on this being true | Evaluation metrics must be accurate |
| Regulatory/compliance requirement | PII handling, audit requirements |
| You need an audit trail | Who deployed what, when |

### Answer NO if:

| Criterion | Example |
|-----------|---------|
| Violations are suboptimal but not wrong | "Prefer method X" |
| Context matters for the decision | "Usually do Y, but Z is fine too" |
| Human judgment should be involved | Code style preferences |
| Enforcement would slow iteration too much | Strict typing during exploration |
| The cost of violation is low | Minor inefficiency |

---

## Examples

### Needs Hard Enforcement (YES → Code/CI)

| Knowledge | Why Hard Enforcement |
|-----------|---------------------|
| "Dataset schema must validate" | Invalid data causes downstream failures |
| "No credentials in code" | Security breach risk |
| "Evaluation must include baselines" | Meaningless results without baseline |
| "Test/train split must be temporal for time-series" | Data leakage invalidates model |
| "Required fields must be non-null" | Application crashes otherwise |

### Soft Guidance is Sufficient (NO → Continue Flow)

| Knowledge | Why Soft Guidance |
|-----------|------------------|
| "Prefer vectorized operations" | Loop is suboptimal but works |
| "Add docstrings to functions" | Good practice, not critical |
| "Use descriptive variable names" | Style, not correctness |
| "Consider edge cases" | Guidance for thinking |
| "Log important operations" | Helpful but not blocking |

---

## Types of Hard Enforcement

### In Code (Runtime)
```python
# Schema validation
def process_data(df: pd.DataFrame) -> pd.DataFrame:
    required_cols = {'user_id', 'timestamp', 'value'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_cols - set(df.columns)}")
    return df

# Type validation
def calculate_metric(values: list[float]) -> float:
    if not all(isinstance(v, (int, float)) for v in values):
        raise TypeError("All values must be numeric")
    return sum(values) / len(values)
```

### In CI (Pipeline)
```yaml
# .github/workflows/validate.yml
- name: Run data leakage tests
  run: pytest tests/test_no_leakage.py

- name: Validate schemas
  run: python scripts/validate_schemas.py

- name: Check for secrets
  run: detect-secrets scan
```

### In Pre-commit (Developer)
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: no-hardcoded-secrets
      name: Check for hardcoded secrets
      entry: detect-secrets-hook
      language: python
```

---

## Edge Cases

### "It's important, but we're early stage"

**Answer:** Consider a phased approach.
- Add as a **rule** now (soft enforcement)
- Add **CI checks** when the pattern stabilizes
- Don't skip enforcement just because it's early

### "Enforcement would slow us down"

**Answer:** Consider the cost of violations.
- If violations cause rework, enforcement saves time
- If violations are easily fixed, soft guidance may suffice
- Balance speed vs. risk

### "Some violations are okay, some aren't"

**Answer:** Split the knowledge.
- Hard cases → Code/CI
- Soft cases → Rules

Example:
- "Schema must have required fields" → CI (hard)
- "Schema should have documentation" → Rule (soft)

### "We want to enforce it, but can't automate it"

**Answer:** This needs human review, not automation.
- Add a **rule** to raise awareness
- Create a **checklist** for manual review
- Consider if the knowledge can be restructured to be automatable

---

## Common Mistakes

### Mistake 1: Over-Enforcement
```
# BAD: This blocks legitimate patterns
CI fails if any function lacks a docstring

# BETTER: Warn, don't fail
Rule suggests docstrings, CI checks public API only
```

### Mistake 2: Under-Enforcement
```
# BAD: Critical check is only in a rule
Rule says "don't use test data for training"

# BETTER: Enforce in CI
pytest test_no_data_leakage.py
```

### Mistake 3: Unenforceable "Enforcement"
```
# BAD: Can't be automated
CI check: "Code should be readable"

# BETTER: Make it concrete
CI check: Function complexity score < 10
```

---

## Outcomes

| Answer | Artifact Type | Next Step |
|--------|---------------|-----------|
| **YES** | Code / CI | Done — implement enforcement |
| **NO** | Continue | [Scope Check](scope-check.md) |

---

## See Also

- **Previous Decision**: [Stability Check](stability-check.md)
- **Next Decision**: [Scope Check](scope-check.md)
- **Overview**: [Decision Flow](README.md)
