# Data Contracts for Data Science

[Home](../README.md) > [Data Science Workflows](README.md) > Data Contracts

---

## Overview

Data contracts are formal agreements that define the structure, quality, and semantics of data exchanged between systems or teams. For data scientists, they're the bridge between **"I hope upstream data doesn't change"** and **"I'll know immediately if it does."**

---

## What Is a Data Contract?

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA CONTRACT                               │
│                                                                  │
│  A formal specification that defines:                            │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │     SCHEMA      │  │    QUALITY      │  │   SEMANTICS     │  │
│  │                 │  │                 │  │                 │  │
│  │ • Column names  │  │ • Freshness     │  │ • Definitions   │  │
│  │ • Data types    │  │ • Completeness  │  │ • Business rules│  │
│  │ • Constraints   │  │ • Value ranges  │  │ • Ownership     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  WHO: Producer commits to consumer                               │
│  WHEN: Validated at runtime, CI, or both                         │
│  WHY: Breaks are detected, not discovered                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Why Data Contracts Matter for Data Scientists

### The Problem Without Contracts

```
┌─────────────────────────────────────────────────────────────────┐
│  WITHOUT DATA CONTRACTS                                          │
│                                                                  │
│  Data Engineering Team              Data Science Team            │
│  ──────────────────────             ─────────────────            │
│                                                                  │
│  "We renamed                        "Why did my model           │
│   customer_id to                     suddenly break?"           │
│   cust_id for                                                   │
│   consistency"                      "The feature pipeline       │
│                                      failed silently for        │
│  "We removed the                     3 days before anyone       │
│   deprecated column                  noticed"                   │
│   last quarter"                                                 │
│                                     "Upstream nulls caused      │
│  "The schema is in                   training data corruption"  │
│   the wiki somewhere"                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### The Solution With Contracts

```
┌─────────────────────────────────────────────────────────────────┐
│  WITH DATA CONTRACTS                                             │
│                                                                  │
│  ┌──────────────┐                   ┌──────────────┐            │
│  │   Producer   │                   │   Consumer   │            │
│  │   (DE Team)  │                   │   (DS Team)  │            │
│  └──────┬───────┘                   └──────┬───────┘            │
│         │                                   │                    │
│         │   ┌───────────────────────┐      │                    │
│         └──►│   DATA CONTRACT       │◄─────┘                    │
│             │                       │                            │
│             │  Schema: defined      │                            │
│             │  Quality: enforced    │                            │
│             │  Changes: versioned   │                            │
│             │  Breaks: alerted      │                            │
│             └───────────────────────┘                            │
│                         │                                        │
│                         ▼                                        │
│              CI VALIDATION / RUNTIME CHECKS                      │
│                         │                                        │
│                         ▼                                        │
│              ✓ Pass → Data flows                                │
│              ✗ Fail → Alert + block                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Contract Components

### 1. Schema Definition

Defines the structure of the data:

```yaml
schema:
  - name: customer_id
    type: string
    description: "Unique customer identifier (UUID format)"
    not_null: true
    unique: true
    pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

  - name: signup_date
    type: date
    description: "Date customer created account"
    not_null: true

  - name: lifetime_value
    type: float
    description: "Total revenue from customer (USD)"
    range: [0, null]  # No upper bound

  - name: churn_probability
    type: float
    description: "Model-predicted churn risk"
    range: [0, 1]
```

### 2. Quality Expectations

Defines data quality SLAs:

```yaml
quality:
  freshness:
    max_age: "24 hours"
    measured_by: "max(updated_at)"

  completeness:
    customer_id: 1.0        # 100% required
    email: 0.95             # 95% minimum
    phone: 0.80             # 80% minimum

  volume:
    min_rows: 10000
    max_rows: 10000000
    row_count_change: "< 20%"  # Alert on >20% change

  uniqueness:
    customer_id: 1.0        # Must be unique
```

### 3. Semantic Definitions

Defines business meaning:

```yaml
semantics:
  owner: "ml-platform-team@company.com"
  domain: "customer"

  business_rules:
    - "lifetime_value only includes completed transactions"
    - "churn_probability updated daily at 2am UTC"
    - "Customers with <30 days history have churn_probability = null"

  lineage:
    source: "raw.transactions + raw.customers"
    transforms: "dbt/models/customer_features.sql"
```

---

## Implementing Data Contracts

### Option 1: YAML/JSON Contract Files

Simple, version-controlled contract definitions:

```
contracts/
├── customer_features.yaml
├── transaction_summary.yaml
└── model_training_data.yaml
```

**Pros:** Easy to start, works with any validation tool
**Cons:** Requires separate validation logic

### Option 2: Great Expectations

Python-based data validation framework:

```python
import great_expectations as gx

# Define expectations (the "contract")
suite = gx.ExpectationSuite("customer_features_contract")

suite.add_expectation(
    gx.ExpectColumnToExist(column="customer_id")
)
suite.add_expectation(
    gx.ExpectColumnValuesToNotBeNull(column="customer_id")
)
suite.add_expectation(
    gx.ExpectColumnValuesToBeBetween(
        column="churn_probability",
        min_value=0,
        max_value=1
    )
)

# Validate data against contract
results = gx.validate(df, suite)
assert results.success, f"Contract violation: {results.failures}"
```

### Option 3: Pydantic Models

Type-safe contract enforcement in Python:

```python
from pydantic import BaseModel, Field, validator
from datetime import date
from typing import Optional

class CustomerFeatures(BaseModel):
    """Data contract for customer_features table."""

    customer_id: str = Field(..., regex=r'^[0-9a-f-]{36}$')
    signup_date: date
    lifetime_value: float = Field(..., ge=0)
    churn_probability: Optional[float] = Field(None, ge=0, le=1)

    @validator('churn_probability')
    def validate_churn_for_new_customers(cls, v, values):
        """New customers (< 30 days) should have null churn."""
        # Business logic validation
        return v

# Validate each row
for row in data:
    CustomerFeatures(**row)  # Raises ValidationError on contract breach
```

### Option 4: dbt Contracts

For dbt-based data pipelines:

```yaml
# models/customer_features.yml
models:
  - name: customer_features
    description: "Customer-level features for ML models"

    config:
      contract:
        enforced: true  # dbt 1.5+ contract enforcement

    columns:
      - name: customer_id
        data_type: string
        constraints:
          - type: not_null
          - type: unique

      - name: lifetime_value
        data_type: float
        constraints:
          - type: not_null
        tests:
          - dbt_utils.accepted_range:
              min_value: 0

      - name: churn_probability
        data_type: float
        tests:
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1
```

---

## Data Contracts in the 3-Layer System

Data contracts fit into **Layer 3: Enforcement**:

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: RULES (.mdc)                                          │
│  "Always validate input data before training"                   │
│  "Never assume upstream schema is stable"                       │
└────────────────────────┬────────────────────────────────────────┘
                         │ Guides behavior
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: SKILLS (.md)                                          │
│  "Data Contract Review Checklist"                               │
│  "How to add a new column to an existing contract"              │
└────────────────────────┬────────────────────────────────────────┘
                         │ Provides procedures
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: ENFORCEMENT (Contracts + Code + CI)                   │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Contract YAML   │  │ Validation Code │  │ CI Checks       │  │
│  │                 │  │                 │  │                 │  │
│  │ Schema specs    │  │ Great Expects   │  │ Pre-merge tests │  │
│  │ Quality SLAs    │  │ Pydantic models │  │ Scheduled scans │  │
│  │ Ownership       │  │ dbt tests       │  │ Alerting        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  RESULT: Contract violations BLOCK, not just warn                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cursor Rules for Data Contracts

Create a rule to ensure data contract awareness:

```markdown
---
description: Enforce data contract practices
globs: ["**/*.py", "**/*.sql"]
---

# Data Contract Enforcement

When working with data pipelines or ML features:

1. **Check for existing contracts** before using a dataset
   - Look in `contracts/` directory
   - Check dbt schema files for constraints

2. **Validate data at boundaries**
   - Validate inputs when reading from external sources
   - Validate outputs before writing to shared tables

3. **Document schema expectations** in code
   - Use type hints and Pydantic models
   - Add Great Expectations suites for critical paths

4. **Never assume upstream stability**
   - Add defensive checks even with contracts
   - Log schema drift warnings
```

---

## Workflow: Adding a New Data Contract

### Step 1: Define the Contract

```yaml
# contracts/new_feature_table.yaml
contract:
  name: new_feature_table
  version: "1.0.0"
  owner: your-team@company.com

schema:
  # Define all columns with types and constraints

quality:
  # Define freshness, completeness, volume expectations

semantics:
  # Document business rules and ownership
```

### Step 2: Implement Validation

```python
# validation/new_feature_table.py
from contracts import load_contract, validate_dataframe

contract = load_contract("new_feature_table")

def validate_new_feature_table(df):
    """Validate data against contract before use."""
    results = validate_dataframe(df, contract)
    if not results.passed:
        raise ContractViolationError(results.failures)
    return df
```

### Step 3: Add CI Checks

```yaml
# .github/workflows/data-contracts.yml
name: Data Contract Validation

on:
  push:
    paths:
      - 'contracts/**'
      - 'src/features/**'

jobs:
  validate-contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate contract schemas
        run: python -m contracts.validate_all
      - name: Run contract tests
        run: pytest tests/contracts/
```

### Step 4: Set Up Alerting

```python
# alerts/contract_monitor.py
def monitor_contract_health():
    """Scheduled job to check contract compliance."""
    for contract in load_all_contracts():
        df = fetch_latest_data(contract.table_name)
        results = validate_dataframe(df, contract)

        if not results.passed:
            send_alert(
                channel="#data-quality",
                message=f"Contract violation: {contract.name}",
                details=results.failures
            )
```

---

## Common Contract Patterns for DS

### Feature Table Contract

```yaml
contract:
  name: ml_feature_store

schema:
  - name: entity_id
    type: string
    not_null: true
    description: "Primary key for feature lookup"
  - name: feature_timestamp
    type: timestamp
    not_null: true
    description: "Point-in-time for feature values"
  # ... feature columns

quality:
  freshness: "< 1 hour"
  completeness:
    entity_id: 1.0
    feature_timestamp: 1.0
```

### Training Data Contract

```yaml
contract:
  name: model_training_data

schema:
  - name: target
    type: float
    range: [0, 1]
    description: "Binary classification target"
  # ... feature columns

quality:
  volume:
    min_rows: 100000
  class_balance:
    target_0: [0.4, 0.6]  # 40-60% negative class
    target_1: [0.4, 0.6]  # 40-60% positive class
```

### Inference Input Contract

```yaml
contract:
  name: model_inference_input

schema:
  # Must match training schema exactly

quality:
  latency: "< 100ms"  # For real-time inference
  null_handling: "reject"  # Don't allow nulls in inference
```

---

## Key Takeaways

| Without Contracts | With Contracts |
|-------------------|----------------|
| Schema changes break pipelines silently | Schema changes trigger immediate alerts |
| Data quality issues discovered in production | Quality issues caught in CI/staging |
| "It worked on my machine" | Consistent validation across environments |
| Tribal knowledge about data meaning | Documented semantics and ownership |
| Reactive firefighting | Proactive quality gates |

---

## See Also

- **Previous**: [Common Challenges](common-challenges.md)
- **Related**: [3-Layer Stack](../02-core-concepts/3-layer-stack.md) — Where contracts fit
- **Tools**: [Great Expectations](https://greatexpectations.io/), [dbt Contracts](https://docs.getdbt.com/docs/collaborate/govern/model-contracts)
