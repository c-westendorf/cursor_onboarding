# Rule Examples

[Home](../../README.md) > [Rules Deep Dive](../README.md) > Examples

---

## Overview

This section contains annotated examples of real-world rules. Each example includes the full rule content and commentary on design decisions.

---

## Example Rules

### 1. Core Principles (Always-Apply)

This rule is always active and contains only essential, universal principles.

```markdown
---
description: Core data science principles
alwaysApply: true
---

# Core Principles

## Non-Negotiables

1. **Reproducibility**: Set random seeds. Document versions.
2. **Data Integrity**: Never modify source data. Work on copies.
3. **No Fabrication**: Never fabricate metrics, data, or results.
4. **Explicit > Implicit**: State assumptions. Validate inputs.

## Quality Standards

- Handle errors explicitly, not silently
- Log operations that matter
- Test critical paths
```

**Design notes:**
- Very short (~30 lines) to minimize context usage
- Only universal principles that apply everywhere
- No code examples (those belong in domain-specific rules)
- Action-oriented statements

---

### 2. Python Standards (Auto-Attach)

This rule activates for Python files and contains specific patterns.

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
    ...
```

## Docstrings

Use Google-style for public functions:

```python
def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Calculate classification metrics.

    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels

    Returns:
        Dictionary with precision, recall, f1 scores

    Raises:
        ValueError: If arrays have different lengths
    """
```

## Error Handling

```python
# Bad: Silent failure
try:
    result = operation()
except:
    pass

# Good: Explicit handling
try:
    result = operation()
except ValueError as e:
    logger.error(f"Validation failed: {e}")
    raise
```

## Imports

```python
# Standard library
import os
from pathlib import Path

# Third-party
import numpy as np
import pandas as pd

# Local
from src.utils import helper
```
```

**Design notes:**
- Moderate length (~80 lines)
- Focused on Python-specific patterns
- Includes code examples with good/bad contrast
- Uses `globs: "**/*.py"` to only activate for Python files

---

### 3. Pandas Operations (Auto-Attach)

Specific patterns for pandas DataFrame work.

```markdown
---
description: Pandas DataFrame best practices
globs: "**/*.py"
alwaysApply: false
---

# Pandas Best Practices

## Vectorized Operations

```python
# Bad: Loop
for i, row in df.iterrows():
    df.loc[i, 'total'] = row['price'] * row['quantity']

# Good: Vectorized
df['total'] = df['price'] * df['quantity']
```

## Method Chaining

```python
result = (
    df
    .query('status == "active"')
    .groupby('category')
    .agg({
        'sales': 'sum',
        'quantity': 'mean'
    })
    .reset_index()
    .rename(columns={'sales': 'total_sales'})
)
```

## Explicit Selection

```python
# Bad: Implicit all columns
new_df = df.copy()

# Good: Explicit columns
cols = ['id', 'name', 'value']
new_df = df[cols].copy()
```

## Memory Efficiency

```python
# Downcast numeric types
df['int_col'] = pd.to_numeric(df['int_col'], downcast='integer')

# Use categories for low-cardinality strings
df['status'] = df['status'].astype('category')
```

## Null Handling

```python
# Be explicit about nulls
df['value'].fillna(0, inplace=False)  # Don't modify in place
df = df.dropna(subset=['required_col'])  # Explicit about what to drop
```
```

**Design notes:**
- Could be combined with Python standards or kept separate
- Very pattern-focused with clear examples
- All examples show transformation, not just description

---

### 4. SQL Safety (Auto-Attach)

SQL-specific security and quality patterns.

```markdown
---
description: SQL query safety and quality
globs:
  - "**/*.sql"
  - "**/*.py"
alwaysApply: false
---

# SQL Safety

## Parameterized Queries

```python
# DANGEROUS: SQL injection
query = f"SELECT * FROM users WHERE id = {user_id}"

# SAFE: Parameterized
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

## Explicit Columns

```sql
-- Bad: SELECT *
SELECT * FROM orders;

-- Good: Explicit columns
SELECT order_id, user_id, total, status, created_at
FROM orders;
```

## Result Limits

```sql
-- Always limit exploratory queries
SELECT order_id, total
FROM orders
WHERE status = 'pending'
LIMIT 1000;
```

## Comments

```sql
-- Explain non-obvious joins
SELECT
    o.order_id,
    u.name,
    p.product_name
FROM orders o
-- Join to get customer info
JOIN users u ON o.user_id = u.id
-- Join through order_items to get products
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE o.status = 'completed';
```
```

**Design notes:**
- Applies to both `.sql` files AND `.py` files (for embedded SQL)
- Security-focused (parameterization)
- Quality-focused (explicit columns, limits)

---

### 5. ML Reproducibility (Auto-Attach)

Machine learning specific reproducibility requirements.

```markdown
---
description: ML reproducibility requirements
globs:
  - "src/ml/**/*.py"
  - "**/*.ipynb"
alwaysApply: false
---

# ML Reproducibility

## Random Seeds

```python
import numpy as np
import random
import torch

SEED = 42

def set_seeds(seed: int = SEED):
    """Set all random seeds for reproducibility."""
    np.random.seed(seed)
    random.seed(seed)
    if torch.cuda.is_available():
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

# Set at script start
set_seeds()

# Pass to sklearn models
model = RandomForestClassifier(random_state=SEED)
```

## Version Tracking

```python
# Log versions at experiment start
import sys
print(f"Python: {sys.version}")
print(f"pandas: {pd.__version__}")
print(f"sklearn: {sklearn.__version__}")
print(f"Data version: {DATA_VERSION}")
```

## Experiment Config

```python
config = {
    'model_type': 'xgboost',
    'hyperparameters': {
        'learning_rate': 0.1,
        'max_depth': 6,
        'n_estimators': 100,
    },
    'random_state': SEED,
    'data_version': 'v2.1',
    'train_date': '2024-01-15',
}

# Save config with model
with open('model_config.json', 'w') as f:
    json.dump(config, f, indent=2)
```

## Data Splitting

```python
# Always split BEFORE any preprocessing
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=SEED,
    stratify=y  # For classification
)

# Then preprocess
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)  # Note: transform only!
```
```

**Design notes:**
- Scoped to ML directory AND notebooks
- Comprehensive but focused on reproducibility
- Includes complete, copy-pasteable code examples

---

### 6. Data Validation (On-Demand)

Detailed validation patterns, invoked when needed.

```markdown
---
description: Data validation patterns (invoke with @data-validation)
alwaysApply: false
---

# Data Validation Patterns

## Schema Validation

```python
REQUIRED_COLUMNS = {
    'user_id': 'int64',
    'timestamp': 'datetime64[ns]',
    'value': 'float64',
}

def validate_schema(df: pd.DataFrame) -> None:
    """Validate DataFrame schema."""
    # Check columns exist
    missing = set(REQUIRED_COLUMNS.keys()) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Check types
    for col, expected_type in REQUIRED_COLUMNS.items():
        actual = str(df[col].dtype)
        if actual != expected_type:
            raise TypeError(
                f"Column {col}: expected {expected_type}, got {actual}"
            )
```

## Value Range Validation

```python
def validate_ranges(df: pd.DataFrame) -> None:
    """Validate value ranges."""
    # Numeric ranges
    if (df['age'] < 0).any() or (df['age'] > 150).any():
        raise ValueError("Age out of valid range [0, 150]")

    # Categorical values
    valid_statuses = {'active', 'inactive', 'pending'}
    invalid = set(df['status'].unique()) - valid_statuses
    if invalid:
        raise ValueError(f"Invalid status values: {invalid}")
```

## Null Handling

```python
def check_nulls(df: pd.DataFrame) -> dict:
    """Report null statistics."""
    null_counts = df.isnull().sum()
    null_pcts = (null_counts / len(df)) * 100

    report = {
        col: {
            'count': int(null_counts[col]),
            'percent': float(null_pcts[col])
        }
        for col in df.columns
        if null_counts[col] > 0
    }

    return report
```

## Duplicate Detection

```python
def check_duplicates(
    df: pd.DataFrame,
    key_columns: list[str]
) -> pd.DataFrame:
    """Find duplicate rows by key columns."""
    duplicates = df[df.duplicated(subset=key_columns, keep=False)]
    return duplicates.sort_values(key_columns)
```

## Complete Validation Pipeline

```python
def validate_dataset(df: pd.DataFrame) -> dict:
    """Run full validation suite."""
    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
    }

    # Schema
    try:
        validate_schema(df)
    except (ValueError, TypeError) as e:
        results['valid'] = False
        results['errors'].append(str(e))

    # Ranges
    try:
        validate_ranges(df)
    except ValueError as e:
        results['valid'] = False
        results['errors'].append(str(e))

    # Nulls (warning, not error)
    null_report = check_nulls(df)
    if null_report:
        results['warnings'].append(f"Nulls found: {null_report}")

    # Duplicates (warning)
    dups = check_duplicates(df, ['user_id', 'timestamp'])
    if len(dups) > 0:
        results['warnings'].append(f"Found {len(dups)} duplicate rows")

    return results
```
```

**Design notes:**
- Long and detailed — appropriate for on-demand
- Complete, working code examples
- Can be invoked with `@data-validation` when needed
- Too long to include in every context, but valuable when called

---

## See Also

- **Parent**: [Rules Deep Dive](../README.md)
- **Writing Guide**: [Writing Effective Rules](../writing-effective-rules.md)
- **Shared Rules**: [Marketplace Catalog](../../08-marketplace/catalog/README.md)
