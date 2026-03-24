# Dtype Router

Classify DataFrame columns into standard type buckets. This classification drives branching decisions in cleaning, imputation, and feature engineering.

## Column Type Classification

```python
import numpy as np
import pandas as pd

def classify_columns(df, text_length_threshold=50, discrete_nunique_threshold=20):
    """
    Classify DataFrame columns into standard type buckets.

    Returns a dict mapping bucket names to lists of column names.
    Each column appears in exactly one bucket.
    """
    col_types = {
        'numeric_continuous': [],
        'numeric_discrete': [],
        'categorical_low_card': [],
        'categorical_high_card': [],
        'datetime': [],
        'text_free': [],
        'boolean': [],
        'unknown': [],
    }

    for col in df.columns:
        dtype = df[col].dtype

        # Boolean
        if dtype == 'bool' or (dtype == 'object' and
            set(df[col].dropna().unique()) <= {'True', 'False', 'true', 'false', 'yes', 'no', 'Yes', 'No', '0', '1'}):
            col_types['boolean'].append(col)

        # Datetime
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            col_types['datetime'].append(col)

        # Numeric
        elif pd.api.types.is_numeric_dtype(dtype):
            nunique = df[col].nunique()
            if nunique <= discrete_nunique_threshold:
                col_types['numeric_discrete'].append(col)
            else:
                col_types['numeric_continuous'].append(col)

        # Object / String / Category
        elif dtype in ('object', 'string') or pd.api.types.is_categorical_dtype(dtype):
            nunique = df[col].nunique()

            # Check if it's free-form text (long strings)
            avg_length = df[col].dropna().astype(str).str.len().mean()
            if avg_length > text_length_threshold:
                col_types['text_free'].append(col)
            elif nunique <= discrete_nunique_threshold:
                col_types['categorical_low_card'].append(col)
            else:
                col_types['categorical_high_card'].append(col)

        else:
            col_types['unknown'].append(col)

    return col_types
```

## How Each Bucket Is Handled

| Bucket | Cleaning | Imputation | Feature Engineering |
|--------|----------|------------|---------------------|
| `numeric_continuous` | Coerce to float, check range | Median (MCAR), IterativeImputer (MAR) | log1p, StandardScaler, polynomials, interactions |
| `numeric_discrete` | Coerce to Int64 (nullable), verify levels | Mode (MCAR), ordinal-aware KNN (MAR) | Leave as-is for trees, one-hot for linear |
| `categorical_low_card` | Standardize labels, strip whitespace | Mode (MCAR), "Unknown" (MNAR) | Ordinal (trees), one-hot (linear), target encoding |
| `categorical_high_card` | Standardize labels, assess if truly needed | "Unknown" always | Frequency encoding, target encoding, hash encoding. NEVER one-hot |
| `datetime` | Parse with `pd.to_datetime`, validate range | Interpolate (regular) or None+flag | Extract: year/month/dow/hour/is_weekend + cyclical sin/cos + time-since |
| `text_free` | Normalize encoding (UTF-8), strip whitespace | "[MISSING]" token | TF-IDF, text_length, word_count, embeddings |
| `boolean` | Standardize to True/False | Mode + `_was_missing` indicator | Pass through as 0/1 |

## Usage

```python
# At the start of any playbook:
col_types = classify_columns(df)

# Then branch:
for col in col_types['numeric_continuous']:
    # Apply numeric-specific logic
    ...

for col in col_types['categorical_high_card']:
    # Apply high-cardinality categorical logic
    ...
```

## Edge Cases

- **IDs that look numeric** (zip codes, phone numbers): Override classification — force to `categorical_high_card` or `string`
- **Ordinal categories** (low/medium/high): Start as `categorical_low_card`, convert to ordinal integer during feature engineering
- **Mixed-type columns**: Flag during cleaning; split into separate columns if needed
- **Sparse columns** (>80% null): Flag separately regardless of type; downstream playbooks decide keep/drop
