# Writing Effective Rules

[Home](../README.md) > [Rules Deep Dive](README.md) > Writing Effective Rules

---

## Overview

This guide covers best practices for writing rules that are clear, useful, and don't bloat your context.

---

## The Golden Rules

### 1. Rules Are Constraints, Not Tutorials

```markdown
# BAD: Tutorial
How to clean data:
1. First, load your data with pd.read_csv()
2. Then check for missing values
3. Next, handle missing values by...

# GOOD: Constraint
Validate data before processing:
- Check for required columns
- Verify data types match expectations
- Handle missing values explicitly (don't ignore them)
```

### 2. Be Specific, Not Generic

```markdown
# BAD: Too generic
Write good code.

# GOOD: Specific
Use vectorized pandas operations instead of iterating with loops.
Prefer df.apply() over df.iterrows().
```

### 3. Include Examples

```markdown
# BAD: No example
Use parameterized queries.

# GOOD: With example
Use parameterized queries:
```sql
-- Bad
query = f"SELECT * FROM users WHERE id = {user_id}"

-- Good
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```
```

### 4. State Both Do and Don't

```markdown
# GOOD: Clear contrast
## Data Splitting

Don't:
```python
# Scaling before split — leaks information
scaler.fit(X)
X_train, X_test = train_test_split(X)
```

Do:
```python
# Split first, then scale
X_train, X_test = train_test_split(X)
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)
```
```

---

## Structure Template

Use this template as a starting point:

```markdown
---
description: [Clear, brief description]
globs: "[appropriate pattern]"
alwaysApply: false
---

# [Rule Name]

[1-2 sentence summary of what this rule covers]

## Principles

- [Key principle 1]
- [Key principle 2]
- [Key principle 3]

## Patterns

### [Pattern Name]

[Brief explanation]

```[language]
# Bad
[anti-pattern code]

# Good
[preferred code]
```

## Common Mistakes

- [Mistake 1]: [Why it's wrong]
- [Mistake 2]: [Why it's wrong]

## See Also

- @[related-rule] for [what it covers]
```

---

## Writing Clear Content

### Use Action-Oriented Language

```markdown
# BAD: Passive
Data should be validated.

# GOOD: Active
Validate data before processing.
```

### Be Concise

```markdown
# BAD: Verbose
When you are working with pandas DataFrames and you need to
create a new column based on the values of existing columns,
you should avoid using iterrows() because it is slow...

# GOOD: Concise
Use vectorized operations for new DataFrame columns. Avoid iterrows().
```

### Organize with Headers

```markdown
# Good structure
## Data Loading
...

## Data Validation
...

## Data Transformation
...
```

---

## Examples of Good Rules

### Example 1: Python Standards

```markdown
---
description: Python coding standards for data science
globs: "**/*.py"
alwaysApply: false
---

# Python Standards

## Type Hints

Add type hints to function signatures:

```python
def process_data(
    df: pd.DataFrame,
    columns: list[str],
    threshold: float = 0.5
) -> pd.DataFrame:
```

## Docstrings

Use Google-style docstrings for public functions:

```python
def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Calculate classification metrics.

    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels

    Returns:
        Dictionary with precision, recall, f1 scores
    """
```

## Error Handling

Be explicit about errors:

```python
# Bad: Silent failure
try:
    result = risky_operation()
except:
    pass

# Good: Explicit handling
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Validation failed: {e}")
    raise
```
```

### Example 2: SQL Safety

```markdown
---
description: SQL query safety and best practices
globs: "**/*.sql"
alwaysApply: false
---

# SQL Safety

## Parameterized Queries

Always use parameters, never string concatenation:

```python
# DANGEROUS: SQL injection risk
query = f"SELECT * FROM users WHERE id = {user_id}"

# SAFE: Parameterized
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

## Result Limits

Always limit results for exploratory queries:

```sql
-- Add LIMIT for exploration
SELECT * FROM large_table LIMIT 1000;
```

## Explicit Column Selection

Don't use SELECT *:

```sql
-- Bad
SELECT * FROM orders;

-- Good
SELECT order_id, user_id, total, created_at FROM orders;
```
```

### Example 3: ML Reproducibility

```markdown
---
description: Machine learning reproducibility requirements
globs:
  - "**/*.py"
  - "**/*.ipynb"
alwaysApply: false
---

# ML Reproducibility

## Random Seeds

Set seeds explicitly for all random operations:

```python
import numpy as np
import random
import torch

SEED = 42

np.random.seed(SEED)
random.seed(SEED)
torch.manual_seed(SEED)

# For sklearn
model = RandomForestClassifier(random_state=SEED)
```

## Version Tracking

Document versions of data and dependencies:

```python
# In notebooks or scripts
print(f"pandas: {pd.__version__}")
print(f"sklearn: {sklearn.__version__}")
print(f"Data version: {data_version}")
```

## Experiment Logging

Log all experiment parameters:

```python
experiment_config = {
    'model': 'xgboost',
    'learning_rate': 0.1,
    'max_depth': 6,
    'n_estimators': 100,
    'random_state': SEED,
    'data_version': 'v2.1',
    'timestamp': datetime.now().isoformat()
}
logger.info(f"Starting experiment: {experiment_config}")
```
```

---

## Common Mistakes

### Mistake 1: Too Long

```
# BAD: 500+ lines
[Everything about data science...]

# GOOD: Under 200 lines, focused
Split into multiple rules if needed
```

### Mistake 2: Too Abstract

```markdown
# BAD: No actionable guidance
"Be careful with data"

# GOOD: Specific actions
"Validate data shapes match expectations after each transformation"
```

### Mistake 3: Contradicting Other Rules

```markdown
# BAD: Contradicts another rule
Rule A: "Always use pandas"
Rule B: "Prefer polars for large datasets"

# GOOD: Consistent guidance
Rule A: "Use pandas for small-medium datasets"
Rule A: "Consider polars for datasets > 1GB"
```

### Mistake 4: Including Ephemeral Information

```markdown
# BAD: Will become outdated
"Use API version 2.3"
"Contact John for access"

# GOOD: Stable principles
"Use the latest stable API version"
"Document API versions in code"
```

---

## Testing Your Rules

### 1. Read It Fresh
Can someone new understand what to do?

### 2. Test with AI
Ask Cursor to write code that should follow the rule. Does it?

### 3. Check for Conflicts
Do any rules contradict each other?

### 4. Measure Impact
Is code quality improving? Are review comments decreasing?

---

## Rule Maintenance

### Quarterly Review
- Are rules still accurate?
- Are any rules unused?
- Should any be promoted to always-apply?
- Should any be demoted to on-demand?

### Update Process
1. Propose change in PR
2. Review with team
3. Update rule
4. Communicate change

---

## See Also

- **Previous**: [Rule Types](rule-types.md)
- **Next**: [Context Budgeting](context-budgeting.md)
- **Examples**: [Rule Examples](examples/README.md)
