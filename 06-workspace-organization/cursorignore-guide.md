# .cursorignore Guide

[Home](../README.md) > [Workspace Organization](README.md) > .cursorignore Guide

---

## Overview

`.cursorignore` tells Cursor which files to exclude from indexing. This improves performance and keeps irrelevant content out of context.

---

## Basic Syntax

Same as `.gitignore`:

```bash
# Comment
file.txt          # Specific file
*.csv             # All CSV files
data/             # Directory
!important.csv    # Exception (include this)
**/*.log          # Recursive pattern
```

---

## Recommended for Data Science

```bash
# ===================
# Data Files
# ===================
data/
*.csv
*.tsv
*.parquet
*.feather
*.arrow
*.h5
*.hdf5
*.json           # Large JSON data files (be specific if needed)
*.jsonl

# ===================
# Model Artifacts
# ===================
models/
checkpoints/
*.pkl
*.pickle
*.joblib
*.h5
*.pt
*.pth
*.onnx
*.pb
*.savedmodel/

# ===================
# Outputs
# ===================
outputs/
results/
figures/
*.png
*.jpg
*.jpeg
*.svg
*.pdf

# ===================
# Logs
# ===================
logs/
*.log
mlruns/
wandb/
tensorboard/

# ===================
# Caches
# ===================
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.pyc
.ipynb_checkpoints/

# ===================
# Virtual Environments
# ===================
venv/
.venv/
env/
.env/
conda-env/

# ===================
# Build Artifacts
# ===================
dist/
build/
*.egg-info/
node_modules/

# ===================
# IDE/Editor
# ===================
.idea/
.vscode/         # Keep if you want to exclude VS Code settings
*.swp
*.swo

# ===================
# Archives
# ===================
docs/archive/
old/
deprecated/
```

---

## Common Patterns

### Exclude All Data, Include Schema

```bash
data/
!data/schemas/     # Keep schema files
!data/README.md    # Keep documentation
```

### Exclude Large Files by Size (not supported)

`.cursorignore` doesn't support size-based rules. Use naming conventions:

```bash
*_large.csv
*_full.parquet
raw_*.csv
```

### Exclude Test Fixtures

```bash
tests/fixtures/large_*.json
tests/fixtures/data/
```

### Exclude Generated Code

```bash
generated/
*_generated.py
*.auto.py
```

---

## Project-Specific Examples

### ML Project

```bash
# Data
data/raw/
data/processed/
*.csv
*.parquet

# Models
models/
experiments/
mlruns/

# Large notebooks outputs
*.ipynb_checkpoints/
```

### Analytics Project

```bash
# Query results
results/
exports/
*.csv
*.xlsx

# Cached queries
.query_cache/
```

### Full-Stack Data Product

```bash
# Backend data
backend/data/
backend/logs/

# Frontend build
frontend/dist/
frontend/node_modules/

# Shared data
shared/data/
```

---

## What NOT to Ignore

### Keep These Indexed

| File Type | Why |
|-----------|-----|
| Source code (`*.py`) | Core functionality |
| Tests (`tests/`) | AI should understand test patterns |
| Config (`*.yaml`, `*.toml`) | Project configuration |
| Documentation (`docs/*.md`) | Context for AI |
| SQL queries (`*.sql`) | Data logic |
| Small data samples | Examples for AI |

### Exception Pattern

```bash
# Ignore all CSVs
*.csv

# But keep small sample files
!data/samples/*.csv
!tests/fixtures/small_*.csv
```

---

## Verification

### Check What's Indexed

```bash
# See what files would be indexed (not ignored)
find . -type f | grep -v -f .cursorignore | head -50
```

### Check Specific File

Cursor's indexing status is visible in the IDE. Look for indexing progress indicators.

---

## Performance Impact

### Before .cursorignore

```
Indexing: 50,000 files
Time: 5+ minutes
Context: Bloated with data files
```

### After .cursorignore

```
Indexing: 500 files
Time: 10 seconds
Context: Clean, relevant code only
```

---

## Troubleshooting

### Files Still Appearing in Context

1. Check pattern syntax
2. Verify file path matches pattern
3. Re-index after changes (may need Cursor restart)

### Important Files Being Ignored

1. Check for overly broad patterns
2. Use `!` exceptions
3. Be more specific with patterns

### .cursorignore Not Working

1. File must be in project root
2. Check for syntax errors
3. Patterns are case-sensitive on some systems

---

## See Also

- **Previous**: [Directory Structures](directory-structures.md)
- **Related**: [Context Budgeting](../03-rules-deep-dive/context-budgeting.md)
