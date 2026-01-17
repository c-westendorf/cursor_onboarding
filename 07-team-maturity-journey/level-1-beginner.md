# Level 1: Beginner

[Home](../README.md) > [Team Maturity](README.md) > Level 1: Beginner

---

## Timeline: Weeks 1-2

---

## Goals

1. Use Cursor for daily development work
2. Understand basic AI interaction patterns
3. Create your first rule
4. Build habit of using context references

---

## Learning Path

### Week 1: Basics

**Day 1-2: Setup & Orientation**
- [ ] Install and configure Cursor
- [ ] Read [What is Cursor?](../01-getting-started/what-is-cursor.md)
- [ ] Complete [First 30 Minutes](../01-getting-started/first-30-minutes.md)
- [ ] Explore code completion features

**Day 3-4: Core Interaction**
- [ ] Practice chat interactions (`Cmd+L`)
- [ ] Learn `@` references (`@file`, `@folder`)
- [ ] Try agent mode on a simple task
- [ ] Understand ask vs agent mode

**Day 5: First Rule**
- [ ] Read [MDC File Anatomy](../03-rules-deep-dive/mdc-file-anatomy.md)
- [ ] Create a simple always-apply rule
- [ ] Test that the rule affects AI output

### Week 2: Building Habits

**Day 6-8: Daily Usage**
- [ ] Use Cursor for all coding tasks
- [ ] Practice explaining context to AI
- [ ] Note where AI struggles (for future rules)
- [ ] Experiment with different prompt styles

**Day 9-10: Refinement**
- [ ] Add 1-2 more rules based on patterns
- [ ] Read [DS Quickstart](../01-getting-started/data-science-quickstart.md)
- [ ] Set up `.cursorignore` for your project
- [ ] Review and iterate on your rules

---

## Key Skills to Develop

### Effective Prompting

**Instead of:**
```
Fix this bug
```

**Try:**
```
The function calculate_total on line 45 returns incorrect results when
the input list is empty. It should return 0 instead of raising an error.
```

### Context References

Learn to use:
```
@file.py          # Include specific file
@folder/          # Include folder
@docs/            # Reference documentation
```

### Agent vs Ask Mode

| Use Agent When | Use Ask When |
|----------------|--------------|
| Need file changes | Just need explanation |
| Multi-step tasks | Quick questions |
| Tool access needed | Discussing approach |

---

## First Rules to Create

### Rule 1: Basic Standards

```markdown
---
description: Basic code standards for this project
alwaysApply: true
---

# Code Standards

- Add docstrings to all functions
- Use descriptive variable names
- Handle errors explicitly
```

### Rule 2: Domain Hints

```markdown
---
description: Project-specific context
alwaysApply: true
---

# Project Context

This is a [type] project using:
- Python 3.10+
- pandas for data processing
- scikit-learn for modeling

Key conventions:
- [List 2-3 key conventions]
```

---

## Milestone: Level 1 Complete

You've completed Level 1 when:

- [ ] Using Cursor daily without friction
- [ ] Have 1-3 working rules
- [ ] Comfortable with basic prompting
- [ ] Understand `@` references
- [ ] Know when to use agent vs ask mode

---

## Common Challenges

### "AI doesn't understand my project"

**Solution:** Add project context to an always-apply rule. Be specific about tech stack and patterns.

### "Rules don't seem to work"

**Check:**
- File is in `.cursor/rules/`
- Extension is `.mdc`
- Frontmatter is valid YAML
- `alwaysApply: true` for testing

### "AI output is verbose/wrong style"

**Solution:** Add style guidance to rules:
```markdown
- Keep responses concise
- Use [specific style] conventions
- Avoid [specific anti-pattern]
```

---

## Next Steps

When you've completed the milestone checklist:
→ [Level 2: Intermediate](level-2-intermediate.md)

---

## See Also

- **Getting Started**: [First 30 Minutes](../01-getting-started/first-30-minutes.md)
- **Rules**: [MDC File Anatomy](../03-rules-deep-dive/mdc-file-anatomy.md)
- **Assessment**: [Self-Assessment Checklist](assessment-checklist.md)
