# MDC File Anatomy

[Home](../README.md) > [Rules Deep Dive](README.md) > MDC File Anatomy

---

## Overview

`.mdc` files are the standard format for Cursor rules. They combine YAML frontmatter with Markdown content.

---

## Basic Structure

```markdown
---
description: Short description of the rule's purpose
globs: optional/path/pattern/**/*
alwaysApply: false
---

# Rule Title

Main content explaining the rule with markdown formatting.
```

---

## The Two Parts

### Part 1: YAML Frontmatter

The frontmatter is enclosed by `---` delimiters and contains metadata.

```yaml
---
description: Prevent data leakage in ML pipelines
globs: "**/*.py"
alwaysApply: false
---
```

### Part 2: Markdown Content

Everything after the frontmatter is the rule content, written in standard Markdown.

```markdown
# Data Leakage Prevention

When working with ML pipelines:

1. **Split data first** — always split before any preprocessing
2. **Fit only on training** — transformers must be fit on training data only
3. **Transform both** — apply same transformation to train and test

## Example

```python
# CORRECT: Fit on train, transform both
scaler.fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)
```
```

---

## Frontmatter Properties

### `description` (Required)

A brief explanation of the rule's purpose. Helps the AI understand when the rule is relevant.

```yaml
description: SQL query safety and optimization patterns
```

**Best practices:**
- Keep under 100 characters
- Be specific about scope
- Use action-oriented language

### `globs` (Optional)

File patterns that trigger auto-attachment. Uses glob syntax.

```yaml
# Single pattern
globs: "**/*.py"

# Multiple patterns
globs:
  - "**/*.py"
  - "**/*.ipynb"

# Directory-specific
globs: "src/ml/**/*.py"
```

**Common patterns:**
| Pattern | Matches |
|---------|---------|
| `**/*.py` | All Python files |
| `**/*.sql` | All SQL files |
| `src/**/*` | Everything under src/ |
| `*.md` | Markdown files in root only |
| `**/*.{py,ipynb}` | Python files and notebooks |

### `alwaysApply` (Optional)

Whether the rule should always be included in context.

```yaml
# Always included
alwaysApply: true

# Only when triggered by globs or @-reference
alwaysApply: false  # This is the default
```

**Guidance:**
- Use `true` sparingly (1-2 rules per project)
- Default to `false` with appropriate globs

---

## Content Best Practices

### Use Clear Headers

```markdown
# Main Topic

## Subtopic 1

### Specific Guideline
```

### Include Examples

```markdown
## Pattern

Bad:
```python
# Don't do this
for i, row in df.iterrows():
    ...
```

Good:
```python
# Do this instead
df.apply(lambda row: ..., axis=1)
```
```

### Be Concise

Rules are constraints, not tutorials. State what should/shouldn't be done, not step-by-step instructions.

```markdown
# Good: Concise constraint
Validate all DataFrame inputs have expected columns before processing.

# Bad: Tutorial-style
Step 1: First, check if the DataFrame has columns
Step 2: Then, verify each column type
Step 3: Next, look for missing values
...
```

### Use Lists for Multiple Points

```markdown
When writing SQL queries:
- Use parameterized queries to prevent injection
- Add appropriate indexes for filtered columns
- Limit result sets for exploratory queries
- Include comments for complex joins
```

---

## Complete Example

```markdown
---
description: Data science code standards for reproducibility and quality
globs: "**/*.py"
alwaysApply: false
---

# Data Science Standards

## Reproducibility

- Set random seeds explicitly: `np.random.seed(42)` or `random_state=42`
- Document data versions and sources
- Log all hyperparameters

## Data Integrity

- Validate input shapes before processing
- Check for nulls explicitly — never assume clean data
- Preserve original data; create copies for transformations

## Code Quality

- Use vectorized operations over loops
- Prefer explicit column selection over `df[df.columns]`
- Add type hints to function signatures

## Example: Good Practice

```python
def process_features(
    df: pd.DataFrame,
    target_col: str,
    random_state: int = 42
) -> tuple[pd.DataFrame, pd.Series]:
    """Process features for modeling.

    Args:
        df: Input DataFrame
        target_col: Name of target column
        random_state: Random seed for reproducibility
    """
    # Validate inputs
    required_cols = {'user_id', 'timestamp', target_col}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing columns: {required_cols - set(df.columns)}")

    # Work on copy
    df_processed = df.copy()

    # Explicit column selection
    feature_cols = [c for c in df.columns if c != target_col]

    return df_processed[feature_cols], df_processed[target_col]
```
```

---

## File Organization

### Naming Convention

Use kebab-case for file names:
```
.cursor/rules/
├── data-science-core.mdc
├── pandas-operations.mdc
├── sql-safety.mdc
└── model-evaluation.mdc
```

### Directory Structure

For larger projects, use subdirectories:
```
.cursor/rules/
├── core.mdc                    # Always-apply
├── ml/
│   ├── model-training.mdc
│   ├── evaluation.mdc
│   └── hyperparameters.mdc
├── data/
│   ├── validation.mdc
│   └── quality.mdc
└── sql/
    ├── safety.mdc
    └── optimization.mdc
```

---

## Common Mistakes

### Mistake 1: Missing Frontmatter

```markdown
# BAD: No frontmatter
# This Rule

Content here...
```

```markdown
# GOOD: Proper frontmatter
---
description: This rule's purpose
---

# This Rule

Content here...
```

### Mistake 2: Tutorial Instead of Rule

```markdown
# BAD: Step-by-step tutorial
1. First import pandas
2. Then load your data
3. Check the head

# GOOD: Constraint
Validate DataFrame shapes after loading and before processing.
```

### Mistake 3: Too Long

```markdown
# BAD: 1000+ lines of content
[Everything about data science...]

# GOOD: Focused rule under 200 lines
[Specific topic with clear constraints]
```

---

## See Also

- **Next**: [Rule Types](rule-types.md)
- **Reference**: [MDC Schema](../reference/mdc-schema.md)
- **Examples**: [Rule Examples](examples/README.md)
