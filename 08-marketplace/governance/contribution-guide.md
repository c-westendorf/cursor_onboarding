# Contribution Guide

[Home](../../README.md) > [Marketplace](../README.md) > [Governance](README.md) > Contribution Guide

---

## Overview

This guide explains how to submit rules, skills, or prompts to the marketplace.

---

## Before Contributing

### Check If It Belongs

Use the [Decision Flow](../../02-core-concepts/decision-flow/README.md):
- Is this knowledge stable for 6+ months?
- Does it apply broadly across teams?
- Will multiple teams benefit?

### Check If It Exists

1. Search the [catalog](../catalog/README.md)
2. Check for similar resources
3. Consider enhancing existing vs. creating new

---

## Submission Process

### Step 1: Fork and Clone

```bash
git clone https://github.com/org/cursor-marketplace.git
cd cursor-marketplace
git checkout -b add-my-new-rule
```

### Step 2: Create Your Resource

**For Rules:**
```bash
# Create in appropriate domain folder
touch rules/ml/my-new-rule.mdc
```

**For Skills:**
```bash
touch skills/my-new-skill.md
```

**For Prompts:**
```bash
touch prompts/eda/my-new-prompt.md
```

### Step 3: Follow Templates

Use the templates in `templates/`:
- `templates/rule-template.mdc`
- `templates/skill-template.md`
- `templates/prompt-template.md`

### Step 4: Write Content

Follow [Quality Standards](quality-standards.md):
- Clear description
- Working examples
- Under length limits
- No spelling errors

### Step 5: Test Locally

```bash
# Run validation
npm run validate

# Test in a real project
cp rules/ml/my-new-rule.mdc /path/to/project/.cursor/rules/
```

### Step 6: Submit PR

```bash
git add .
git commit -m "Add [category]: [name]"
git push origin add-my-new-rule
```

Create PR with:
- Clear title: `Add ML rule: model-training`
- Description of what it does
- Any testing done

---

## Submitting Rules

### Required Frontmatter

```yaml
---
description: Clear, brief description (under 100 chars)
globs: "pattern/**/*.py"  # Or omit for on-demand
alwaysApply: false
version: "1.0.0"
author: "your-name"
category: "ml"  # ml, analytics, data-eng, general
tags: ["training", "evaluation"]
---
```

### Content Requirements

- Under 300 lines
- Include working examples
- Show good AND bad patterns
- No tutorials (constraints only)

### Example

```markdown
---
description: Model evaluation requirements
globs: "**/*.py"
alwaysApply: false
version: "1.0.0"
author: "data-team"
category: "ml"
tags: ["evaluation", "metrics"]
---

# Model Evaluation

## Requirements

- Always compare to baseline
- Report multiple metrics
- Include confidence intervals

## Pattern

```python
# Good
results = {
    'baseline': baseline_f1,
    'model': model_f1,
    'improvement': model_f1 - baseline_f1,
    'ci_95': confidence_interval(model_f1)
}

# Bad: Missing baseline
results = {'model': model_f1}
```
```

---

## Submitting Skills

### Required Structure

```markdown
# Skill Name

## Purpose
What this skill accomplishes.

## When to Use
Scenarios where this applies.

## Steps

### 1. First Step
- Actions
- Checkpoint

### 2. Second Step
...

## Common Issues
Known problems and solutions.
```

### Content Requirements

- Clear step-by-step structure
- Decision points marked
- Examples included
- Under 500 lines

---

## Submitting Prompts

### Required Structure

```markdown
# Prompt: [Name]

## Purpose
What this prompt accomplishes.

## Variables
- `[variable1]`: Description
- `[variable2]`: Description

## Prompt

[The actual prompt text with [variables] marked]

## Example Usage

[Concrete example with variables filled in]
```

---

## After Submission

1. **Automated checks run** (CI/CD)
2. **Reviewers assigned** (within 24-48 hours)
3. **Feedback provided** (may request changes)
4. **Approval** (2 reviewers required)
5. **Merge** (maintainer merges)
6. **Release** (included in next version)

---

## See Also

- [Review Process](review-process.md)
- [Quality Standards](quality-standards.md)
- [Templates](../catalog/README.md)
