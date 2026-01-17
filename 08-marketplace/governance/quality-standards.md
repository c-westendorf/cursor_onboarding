# Quality Standards

[Home](../../README.md) > [Marketplace](../README.md) > [Governance](README.md) > Quality Standards

---

## Overview

All marketplace resources must meet these quality standards before acceptance.

---

## Automated Validation

CI/CD checks run on every PR:

### YAML Validation
```yaml
# Required frontmatter fields
description: Required, under 100 characters
version: Required, semantic version format
author: Required
category: Required (ml, analytics, data-eng, general)
```

### Markdown Linting
- Valid markdown syntax
- Proper heading hierarchy
- Code blocks have language specified

### Spell Check
- No spelling errors in prose
- Technical terms in dictionary or ignore list

### Length Limits
| Resource | Max Lines |
|----------|-----------|
| Rules | 300 |
| Skills | 500 |
| Prompts | 200 |

### Duplicate Detection
- No exact duplicates
- Similarity check against existing resources

---

## Content Standards

### Rules

**Must have:**
- [ ] Clear, actionable constraints (not tutorials)
- [ ] Working code examples
- [ ] Both good AND bad patterns shown
- [ ] Appropriate glob patterns (if auto-attach)

**Must NOT have:**
- [ ] Step-by-step tutorials
- [ ] Ephemeral information
- [ ] Conflicting guidance
- [ ] Excessive length

### Skills

**Must have:**
- [ ] Clear purpose statement
- [ ] Ordered steps
- [ ] Decision points marked
- [ ] Checkpoints/validation
- [ ] Common issues section

### Prompts

**Must have:**
- [ ] Clear purpose
- [ ] Variables marked with `[brackets]`
- [ ] Concrete example usage
- [ ] Expected output description

---

## Style Guidelines

### Writing
- Active voice
- Concise sentences
- Action-oriented ("Do X" not "X should be done")

### Code Examples
- Working, tested code
- Language specified in code blocks
- Comments for non-obvious parts

### Formatting
- Consistent header levels
- Tables for comparisons
- Lists for multiple items

---

## Pre-Submission Checklist

Before submitting, verify:

```markdown
## Quality Checklist

### Automated
- [ ] YAML frontmatter is valid
- [ ] No markdown errors
- [ ] No spelling errors
- [ ] Under length limit

### Content
- [ ] Solves real problem
- [ ] Examples work
- [ ] No conflicts with existing
- [ ] Appropriate category

### Process
- [ ] Follows template
- [ ] Version set correctly
- [ ] Author specified
- [ ] Tags added
```

---

## See Also

- [Contribution Guide](contribution-guide.md)
- [Review Process](review-process.md)
