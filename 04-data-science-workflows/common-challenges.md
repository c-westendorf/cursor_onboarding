# Common DS Challenges with Cursor

[Home](../README.md) > [DS Workflows](README.md) > Common Challenges

---

## Overview

AI assistants excel at many tasks but have consistent challenges with certain data science patterns. This guide identifies common issues and provides strategies.

---

## Challenge 1: Complex Pandas Operations

### The Problem

AI often struggles with:
- Multi-level groupby with custom aggregations
- Complex window functions
- Chained operations with conditional logic

### Example Failure

```python
# User request: "Group by category and date, calculate rolling 7-day average,
#               then pivot to wide format"

# AI might produce overly complex or incorrect code
```

### Solution: Break It Down

Instead of one complex request, use steps:

```
Step 1: "Group df by category and date, sum the values"
Step 2: "Add a rolling 7-day average for each category"
Step 3: "Pivot this to wide format with categories as columns"
```

### Solution: Provide Examples

Include input/output examples:

```
Given this data:
| category | date       | value |
|----------|------------|-------|
| A        | 2024-01-01 | 10    |
| A        | 2024-01-02 | 20    |
| B        | 2024-01-01 | 15    |

Produce this result:
| date       | A  | B  |
|------------|----|----|
| 2024-01-01 | 10 | 15 |
| 2024-01-02 | 20 | NA |
```

### Solution: Create a Rule

```markdown
---
description: Complex pandas patterns
globs: "**/*.py"
---

# Complex Pandas Operations

For multi-step transformations:
1. Break into intermediate DataFrames
2. Validate shape at each step
3. Use explicit column names

Example pattern:
```python
# Step 1: Aggregate
df_agg = (
    df
    .groupby(['category', 'date'])
    .agg({'value': 'sum'})
    .reset_index()
)

# Step 2: Window function
df_agg['rolling_avg'] = (
    df_agg
    .groupby('category')['value']
    .transform(lambda x: x.rolling(7, min_periods=1).mean())
)

# Step 3: Pivot
df_wide = df_agg.pivot(
    index='date',
    columns='category',
    values='rolling_avg'
)
```
```

---

## Challenge 2: PEP8 Compliance

### The Problem

Even with rules, AI may not fully comply with:
- Line length limits
- Import ordering
- Spacing conventions

### Solution: Use Linter Integration

Configure linting to auto-fix:

```json
// settings.json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "python.formatting.provider": "black"
}
```

### Solution: Be Explicit in Rules

```markdown
---
description: Python style enforcement
globs: "**/*.py"
---

# Style Requirements

- Maximum line length: 88 characters (Black default)
- Use Black for formatting
- Import order: stdlib, third-party, local (with blank lines)

Run `black .` before committing.
```

### Solution: Post-Generation Fix

Ask for a fix pass:

```
"Format this code according to PEP8 and Black standards"
```

---

## Challenge 3: Reproducibility Gaps

### The Problem

AI may generate code that:
- Uses random operations without seeds
- Doesn't document versions
- Has hidden state dependencies

### Solution: Strong Rule

```markdown
---
description: Reproducibility requirements
alwaysApply: true
---

# Reproducibility

Every script/notebook MUST:
1. Set random seeds at the start
2. Document library versions
3. Log experiment parameters

Template:
```python
import random
import numpy as np

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Document versions
print(f"numpy: {np.__version__}")
print(f"pandas: {pd.__version__}")
```
```

### Solution: Template Files

Provide starter templates:

```python
# templates/experiment_template.py
"""
Experiment: [NAME]
Date: [DATE]
Author: [AUTHOR]
"""

import random
import numpy as np
import pandas as pd

# Reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Versions
VERSIONS = {
    'numpy': np.__version__,
    'pandas': pd.__version__,
}
print(f"Running with: {VERSIONS}")

# Configuration
CONFIG = {
    'seed': SEED,
    'data_version': 'v1.0',
}

# Your code below
```

---

## Challenge 4: Data Leakage

### The Problem

AI might write code that:
- Fits scalers on full data before splitting
- Uses target information in features
- Ignores temporal ordering

### Solution: Explicit Rule

```markdown
---
description: Data leakage prevention
globs:
  - "**/*.py"
  - "**/*.ipynb"
---

# Preventing Data Leakage

## Order of Operations
1. Split data FIRST
2. Fit transformers on training data ONLY
3. Transform both train and test

## Pattern
```python
# CORRECT ORDER
X_train, X_test, y_train, y_test = train_test_split(X, y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # fit + transform
X_test_scaled = scaler.transform(X_test)        # transform only
```

## Red Flags
- `fit()` called on anything except training data
- `fit_transform()` on full dataset before split
- Features derived from target
```

### Solution: Validation Tests

```python
def test_no_leakage():
    """Verify no data leakage in preprocessing."""
    # Check that test data was never used for fitting
    assert scaler._fit_X.shape[0] == len(X_train), "Scaler fit on wrong data"
```

---

## Challenge 5: Hallucinated APIs

### The Problem

AI might reference:
- Non-existent pandas methods
- Wrong scikit-learn parameter names
- Outdated API signatures

### Solution: Provide Documentation Context

```
Using the pandas 2.0 documentation, write code to...
```

Or reference local docs:

```
@docs/pandas-api-reference.md
```

### Solution: Verification Prompt

```
"Now verify this code runs without errors. If any methods don't exist,
find the correct alternatives."
```

### Solution: Rule with Known Patterns

```markdown
---
description: Verified pandas patterns
globs: "**/*.py"
---

# Verified Pandas 2.x Patterns

## Correct Methods
- `df.groupby().agg()` — aggregation
- `df.transform()` — element-wise
- `df.apply()` — row/column operations
- `pd.concat()` — combining DataFrames

## Deprecated (Don't Use)
- `df.append()` — use `pd.concat()` instead
- `df.iteritems()` — use `df.items()` instead
```

---

## Challenge 6: Performance Issues

### The Problem

AI-generated code may be:
- Using loops instead of vectorization
- Loading full datasets into memory
- Missing obvious optimizations

### Solution: Performance Rule

```markdown
---
description: Performance patterns
globs: "**/*.py"
---

# Performance Guidelines

## Vectorization
```python
# Slow
for i in range(len(df)):
    df.loc[i, 'new'] = df.loc[i, 'a'] + df.loc[i, 'b']

# Fast
df['new'] = df['a'] + df['b']
```

## Memory
- Use `dtype` specification on load
- Read large files in chunks
- Delete intermediate DataFrames

## Large Files
```python
# Chunked processing
chunks = pd.read_csv('large.csv', chunksize=100000)
results = [process(chunk) for chunk in chunks]
df = pd.concat(results)
```
```

### Solution: Post-Review Prompt

```
"Review this code for performance. Are there any loops that
could be vectorized or memory issues to address?"
```

---

## General Strategies

### 1. Use Test-Driven Prompts

```
"Write a function that does X.
Here are the test cases it must pass:
- Input: [example1] → Output: [expected1]
- Input: [example2] → Output: [expected2]
- Edge case: [edge] → Output: [expected]"
```

### 2. Request Validation

```
"Write the code, then add assertions to validate:
- Output shape is correct
- No null values in key columns
- Values are within expected ranges"
```

### 3. Incremental Complexity

Start simple, add complexity:

```
Step 1: "Load the data and show shape"
Step 2: "Filter to relevant rows"
Step 3: "Add the aggregation"
Step 4: "Add the window function"
```

### 4. Context References

Provide context files:

```
Using @data-dictionary.md and @existing-patterns.py,
write code to process the new dataset
```

---

## See Also

- **Previous**: [Database Integration](database-integration.md)
- **Next**: [Workflows](workflows/README.md)
- **Rules**: [Writing Effective Rules](../03-rules-deep-dive/writing-effective-rules.md)
