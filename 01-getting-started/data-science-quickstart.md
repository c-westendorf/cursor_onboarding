# Data Science Quickstart

[Home](../README.md) > [Getting Started](README.md) > Data Science Quickstart

---

## Overview

This guide gets data scientists productive with Cursor quickly, focusing on Jupyter notebooks, pandas workflows, and common DS tooling.

**Time:** ~15 minutes
**Prerequisites:** [First 30 Minutes](first-30-minutes.md) completed

---

## Part 1: DS-Specific Rules (5 minutes)

Create rules that address common data science concerns.

### Create a DS Core Rule

Create `.cursor/rules/data-science-core.mdc`:

```markdown
---
description: Core data science standards for reproducibility and quality
alwaysApply: true
---

# Data Science Standards

## Reproducibility
- Set random seeds explicitly: `np.random.seed(42)` or `random_state=42`
- Document data sources and versions
- Log all hyperparameters and configurations

## Data Integrity
- Never train on test data (prevent data leakage)
- Validate data shapes after transformations
- Check for and handle missing values explicitly

## Code Quality
- Use vectorized pandas/numpy operations, not Python loops
- Prefer `df.loc[]` over chained indexing
- Include type hints for function parameters

## Documentation
- Document assumptions about input data
- Explain non-obvious transformations
- Note known limitations of models/analyses

## Example: Good vs Bad

Bad (data leakage risk):
```python
# DON'T: Fitting scaler on all data
scaler.fit(df[features])
```

Good (proper separation):
```python
# DO: Fit only on training data
scaler.fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)
```
```

### Create a Pandas-Specific Rule

Create `.cursor/rules/pandas-operations.mdc`:

```markdown
---
description: Pandas best practices and common patterns
globs: "**/*.py"
alwaysApply: false
---

# Pandas Best Practices

## Prefer Vectorized Operations

Bad:
```python
for i, row in df.iterrows():
    df.loc[i, 'new_col'] = row['a'] + row['b']
```

Good:
```python
df['new_col'] = df['a'] + df['b']
```

## Use Method Chaining

```python
result = (
    df
    .query('age > 18')
    .groupby('category')
    .agg({'sales': 'sum', 'quantity': 'mean'})
    .reset_index()
    .rename(columns={'sales': 'total_sales'})
)
```

## Explicit Column Selection

```python
# Be explicit about columns
selected_cols = ['id', 'name', 'value']
df_subset = df[selected_cols].copy()
```

## Memory-Efficient Data Types

```python
# Downcast numeric types
df['int_col'] = pd.to_numeric(df['int_col'], downcast='integer')
df['float_col'] = pd.to_numeric(df['float_col'], downcast='float')

# Use categories for low-cardinality strings
df['category_col'] = df['category_col'].astype('category')
```
```

---

## Part 2: Jupyter Notebook Setup (5 minutes)

### Native Notebook Support

Cursor supports `.ipynb` files natively:
1. Open any notebook file
2. AI completions work in code cells
3. Use `Cmd+L` / `Ctrl+L` to chat about the notebook

### Notebook Limitations & Workarounds

**Limitation:** Agent mode can struggle with cell-level edits.

**Workaround options:**

1. **Use cursor-notebook-mcp** (recommended for heavy notebook work):
   ```json
   {
     "mcpServers": {
       "notebook": {
         "command": "npx",
         "args": ["-y", "cursor-notebook-mcp"]
       }
     }
   }
   ```

2. **Convert to .py for major refactoring:**
   ```bash
   jupyter nbconvert --to script notebook.ipynb
   # Edit in Cursor
   # Convert back if needed
   ```

3. **Use cell magic for complex operations:**
   Ask the agent to write code, then copy into cells manually.

---

## Part 3: Database Integration (3 minutes)

### Option A: MCP Database Server (Recommended)

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
    }
  }
}
```

Now you can ask the agent:
- "Show me the schema of the users table"
- "Write a query to find top customers by revenue"
- "Analyze the distribution of values in the orders table"

### Option B: SQL Files with Context

Create a data dictionary and reference it:

```markdown
# docs/data-dictionary.md

## Tables

### users
- id (int): Primary key
- email (varchar): User email
- created_at (timestamp): Account creation date

### orders
- id (int): Primary key
- user_id (int): FK to users
- total (decimal): Order total
- status (enum): pending, completed, cancelled
```

Then in chat: `Using @docs/data-dictionary.md, write a query to find...`

---

## Part 4: Common DS Workflows (2 minutes)

### EDA Workflow

Ask the agent:
```
I'm starting EDA on this dataset. Please:
1. Check the shape and data types
2. Summarize missing values
3. Show distributions of numeric columns
4. Identify potential outliers
5. Check for duplicate rows
```

### Model Evaluation

Ask the agent:
```
Help me evaluate this classification model. I need:
1. Confusion matrix
2. Precision, recall, F1 for each class
3. ROC curve and AUC
4. Feature importance analysis
```

### Data Validation

Ask the agent:
```
Validate this dataframe before processing:
1. Check for expected columns
2. Validate data types
3. Check value ranges for numeric columns
4. Verify no unexpected null values
5. Check for data leakage indicators
```

---

## Recommended `.cursorignore`

Exclude large files from indexing:

```
# Data files
*.csv
*.parquet
*.feather
*.pkl
*.h5

# Large directories
data/
models/
checkpoints/
logs/

# Notebook outputs
*.ipynb_checkpoints/

# Virtual environments
venv/
.venv/
env/
```

---

## What You've Learned

1. **DS-specific rules** for reproducibility and pandas
2. **Notebook workflows** and limitations
3. **Database integration** options
4. **Common DS task patterns**

---

## Next Steps

- Explore [DS Workflows](../04-data-science-workflows/README.md) for detailed guidance
- Set up [MCP Integration](../05-mcp-integration/README.md) for database access
- Browse [Marketplace Rules](../08-marketplace/catalog/rules-by-domain.md) for more DS rules

---

## See Also

- **Previous**: [First 30 Minutes](first-30-minutes.md)
- **Next Section**: [Core Concepts](../02-core-concepts/README.md)
- **Deep Dive**: [Jupyter Notebooks](../04-data-science-workflows/jupyter-notebooks.md)
- **Reference**: [Shared DS Rules](../08-marketplace/catalog/rules-by-domain.md#ml)
