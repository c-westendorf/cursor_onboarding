# Box 4: Repeatability Check

[Home](../../README.md) > [Core Concepts](../README.md) > [Decision Flow](README.md) > Repeatability Check

---

## The Question

**Is this a repeatable reasoning or workflow pattern?**

---

## What This Tests

Whether the guidance helps humans **think through** a problem in a structured way.

- If yes → Create a **skill** or **prompt template**
- If no → Leave as **human judgment**

---

## Decision Criteria

### Answer YES (Repeatable Pattern) if:

| Criterion | Example |
|-----------|---------|
| You follow similar steps each time | EDA always starts with shape, nulls, distributions |
| Multiple people would benefit from the structure | Model evaluation checklist |
| The pattern has proven valuable | Error analysis workflow |
| It guides thinking without forcing outcomes | Feature engineering considerations |
| You find yourself explaining the same process | "Here's how we do X" |

### Answer NO (Situational Judgment) if:

| Criterion | Example |
|-----------|---------|
| Every situation is truly unique | Architecture decisions for novel problems |
| The "pattern" is really just experience | "Knowing when to stop iterating" |
| Codifying would constrain valuable flexibility | Creative problem-solving |
| It's a one-time procedure | Specific migration task |
| The steps depend entirely on context | "How to debug" (too broad) |

---

## Examples

### Repeatable Patterns (YES → Skill/Prompt)

| Pattern | Type | Structure |
|---------|------|-----------|
| EDA checklist | Skill | 1. Shape, 2. Types, 3. Nulls, 4. Distributions, 5. Correlations |
| Model evaluation protocol | Skill | 1. Baseline, 2. Metrics, 3. Error analysis, 4. Documentation |
| Code review workflow | Skill | 1. Correctness, 2. Style, 3. Performance, 4. Security |
| Feature engineering | Prompt | "Given [data], suggest features for [target] prediction" |
| SQL optimization | Prompt | "Review this query for performance issues" |

### Situational Judgment (NO → Human Decides)

| Knowledge | Why Not Codifiable |
|-----------|-------------------|
| "When to use deep learning vs. traditional ML" | Highly context-dependent |
| "How to balance speed vs. quality" | Trade-off requires judgment |
| "When to stop adding features" | Experience-based intuition |
| "How to prioritize technical debt" | Business context matters |
| "When to refactor vs. rewrite" | Many factors to weigh |

---

## Skills vs. Prompts

Both are "Layer 2" artifacts, but serve different purposes:

### Skills (Procedures)
- **Structure:** Step-by-step checklist
- **Usage:** Referenced when doing a specific type of work
- **Example content:**
  ```markdown
  # Model Evaluation Protocol

  ## 1. Establish Baseline
  - Run simple baseline (mean, majority class, etc.)
  - Document baseline performance

  ## 2. Evaluate Model
  - Calculate primary metrics (precision, recall, F1)
  - Generate confusion matrix
  - Plot ROC/PR curves

  ## 3. Error Analysis
  - Sample misclassified examples
  - Identify patterns in errors
  - Document failure modes

  ## 4. Document Results
  - Compare to baseline
  - Note limitations
  - Record hyperparameters and random seeds
  ```

### Prompt Templates (Task Starters)
- **Structure:** A reusable prompt with variable slots
- **Usage:** Invoke at the start of a task
- **Example content:**
  ```markdown
  # EDA Starter Prompt

  Run initial EDA on this dataset:
  1. Show shape and column types
  2. Summarize missing values
  3. Display distributions of numeric columns
  4. Show correlations with [target variable]
  5. Identify potential outliers
  6. Note any data quality concerns

  Dataset: [file or description]
  Target: [target variable]
  ```

---

## Edge Cases

### "It's somewhat repeatable, but varies a lot"

**Answer:** Create a flexible skill with decision points.

```markdown
# Debugging Workflow

## 1. Reproduce the Issue
- Get specific inputs that cause the problem
- Confirm the issue is reproducible

## 2. Isolate the Cause
Choose based on symptom:
- Performance issue → Start with profiling
- Wrong output → Start with input validation
- Crash → Start with stack trace

## 3. Fix and Verify
- Make minimal change to fix
- Verify fix doesn't break other things
- Add test to prevent regression
```

### "The pattern is useful, but I don't want to constrain thinking"

**Answer:** Frame as questions, not commands.

```markdown
# Instead of:
1. Do X
2. Do Y
3. Do Z

# Use:
1. Have you considered X?
2. Did you check Y?
3. What about Z?
```

### "Different people do it differently, but all approaches are valid"

**Answer:** Document the options, not a single path.

```markdown
# Feature Engineering Approaches

When engineering features, consider these strategies:

**Statistical Features:**
- Rolling averages, sums, counts
- Lag features for time series
- Aggregations by category

**Domain Features:**
- Business-specific calculations
- Derived ratios and rates
- Encoded domain knowledge

**Interaction Features:**
- Products of related features
- Polynomial features
- Cross-category combinations

Choose based on your domain and data characteristics.
```

### "It's repeatable for me, but might not be for everyone"

**Answer:** Share it! Others might find it valuable.
- Put in team skills library
- Get feedback on usefulness
- Iterate based on usage

---

## Common Mistakes

### Mistake 1: Skill is Really a Rule
```
# BAD: This should be a rule, not a skill
Skill: "Always validate inputs"

# BETTER: Make it a rule
---
description: Input validation
alwaysApply: true
---
Validate all inputs before processing.
```

### Mistake 2: Skill is Too Rigid
```
# BAD: Assumes one right way
Step 1: Use XGBoost
Step 2: Use default parameters
Step 3: ...

# BETTER: Flexible guidance
Step 1: Select appropriate algorithm for the problem
Step 2: Start with reasonable defaults, then tune
Step 3: ...
```

### Mistake 3: Prompt is Too Vague
```
# BAD: No structure
"Help me with my data"

# BETTER: Clear structure
"Analyze this dataset by:
1. Checking data quality
2. Identifying key patterns
3. Suggesting relevant features
Focus on [specific goal]"
```

---

## Outcomes

| Answer | Artifact Type | Location |
|--------|---------------|----------|
| **YES (procedural)** | Skill | Docs / marketplace |
| **YES (task-starting)** | Prompt Template | Docs / saved prompts |
| **NO** | Human Judgment | Conversation |

---

## Creating Good Skills

### Structure
1. **Clear purpose** — what is this skill for?
2. **When to use** — triggers for invoking
3. **Steps** — ordered actions or considerations
4. **Decision points** — where judgment is needed
5. **Examples** — concrete illustrations
6. **Anti-patterns** — what to avoid

### Maintenance
- Review quarterly for relevance
- Update based on team feedback
- Retire skills that aren't used
- Promote valuable skills to marketplace

---

## See Also

- **Previous Decision**: [Scope Check](scope-check.md)
- **Overview**: [Decision Flow](README.md)
- **Skills Examples**: [Shared Skills](../../08-marketplace/catalog/shared-skills.md)
- **Prompts Examples**: [Prompt Templates](../../08-marketplace/catalog/prompt-templates.md)
