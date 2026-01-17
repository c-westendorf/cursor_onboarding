# Box 1: Stability Check

[Home](../../README.md) > [Core Concepts](../README.md) > [Decision Flow](README.md) > Stability Check

---

## The Question

**Is this knowledge expected to remain valid for 6-12 months or longer?**

---

## What This Tests

Whether the knowledge is **durable** or **ephemeral**.

- **Durable knowledge** is worth investing in codification
- **Ephemeral knowledge** should remain flexible

---

## Decision Criteria

### Answer YES if:

| Criterion | Example |
|-----------|---------|
| You'd teach this to every new hire | "Always validate input data" |
| Violations are clearly mistakes | "Don't train on test data" |
| It applies across multiple projects | "Set random seeds for reproducibility" |
| It reflects established best practices | "Use parameterized SQL queries" |
| The underlying reason won't change | "Protect PII" |

### Answer NO if:

| Criterion | Example |
|-----------|---------|
| It's context-specific to current work | "We're using XGBoost for this project" |
| It changes frequently | "Our preferred model architecture this quarter" |
| It reflects current exploration | "Let's try approach A first" |
| It's a personal preference | "I like using method X" |
| The decision is still being debated | "We might switch to Y" |

---

## Examples

### Stable Knowledge (YES → Continue)

| Knowledge | Why It's Stable |
|-----------|-----------------|
| "Prevent data leakage between train/test" | Fundamental ML principle |
| "Include reproducibility artifacts" | Required for scientific validity |
| "Don't fabricate metrics or results" | Ethical constant |
| "Validate data before processing" | Defensive programming |
| "Handle PII according to policy" | Regulatory requirement |

### Ephemeral Knowledge (NO → Human Judgment)

| Knowledge | Why It's Ephemeral |
|-----------|-------------------|
| "We usually try XGBoost first" | Preference, not rule |
| "Use this specific API version" | Will change |
| "Focus on feature X for this sprint" | Time-bounded |
| "This dataset has quirk Y" | Context-specific |
| "Skip validation for speed during prototyping" | Situational |

---

## Edge Cases

### "It's stable, but only for this project"

**Answer:** Still YES, but consider scope.
→ Create a project-specific rule, not an org-wide one.

### "It's best practice, but we're not sure our team agrees"

**Answer:** NO until consensus.
→ Discuss first, codify after agreement.

### "It's been true for years, but might change soon"

**Answer:** YES for now.
→ Codify it, but plan to review when the change happens.

### "It's true, but stating it seems obvious"

**Answer:** YES if violations actually happen.
→ "Obvious" rules prevent obvious mistakes.

---

## Common Mistakes

### Mistake 1: Codifying Preferences
```
# BAD: This is a preference, not a stable truth
"Always use pandas over polars"

# BETTER: State the actual invariant
"Ensure consistent DataFrame library usage within a module"
```

### Mistake 2: Codifying Current State
```
# BAD: This will change
"Use API v2.3"

# BETTER: State the principle
"Use the latest stable API version and document the version used"
```

### Mistake 3: Codifying Exploration
```
# BAD: This is an experiment
"Try ensemble methods before neural networks"

# BETTER: Don't codify. Discuss in conversation.
```

---

## Outcomes

| Answer | Next Step |
|--------|-----------|
| **YES** | Continue to [Enforcement Check](enforcement-check.md) |
| **NO** | Go to Human Judgment / Ad-hoc Prompts |

---

## See Also

- **Next Decision**: [Enforcement Check](enforcement-check.md)
- **Overview**: [Decision Flow](README.md)
- **Context**: [3-Layer Stack](../3-layer-stack.md)
