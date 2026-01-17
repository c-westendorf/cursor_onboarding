# What is Cursor?

[Home](../README.md) > [Getting Started](README.md) > What is Cursor?

---

## The 30-Second Version

**Cursor is an AI-powered code editor that becomes more effective when you tell it how to behave.**

Think of it as VS Code + AI assistant + your team's best practices, all working together.

---

## The Key Insight

Cursor is not just a chat tool. It's a **knowledge execution system**.

```
        Your Intent
            ↓
    ┌─────────────┐
    │   Rules     │  ← What NOT to do
    │   Skills    │  ← How to do it well
    │   Prompts   │  ← Questions to ask
    └─────────────┘
            ↓
        Your Code
```

**Without configuration:** Cursor uses its general training to help you code.

**With configuration:** Cursor applies your team's specific standards, catches your specific mistakes, and follows your specific patterns.

---

## What Makes Cursor Different

| Traditional IDE | Traditional AI Chat | Cursor |
|-----------------|---------------------|--------|
| Rules via linters | No persistent rules | Rules applied contextually |
| Manual lookup | Forgets context | Learns your codebase |
| Extensions for features | General knowledge | Domain-specific knowledge |

---

## One Agent, Configured Through Knowledge

**Key insight:** Cursor runs **one agent per session**. You don't spawn specialized sub-agents—you configure the single agent with domain-specific knowledge.

### How Specialization Works

| Layer | Artifact Type | How It Works |
|-------|---------------|--------------|
| **Rules** | `.mdc` files | Auto-load based on file patterns (globs) |
| **Skills** | `.md` files | You invoke via `@skill-name.md` |
| **Context** | `@` references | You provide domain knowledge on-demand |

The agent becomes "specialized" based on which rules, skills, and context are active—not by being a different type of agent.

### Execution Modes

| Mode | What It Does | Use When |
|------|--------------|----------|
| **Ask Mode** | Answers questions, suggests code | You want suggestions to apply manually |
| **Agent Mode** | Takes actions: edits files, runs commands | You want autonomous multi-step work |

### Capability Levels

| Level | Context Size | Best For |
|-------|--------------|----------|
| **Local** | Limited | Quick completions, simple tasks |
| **Cloud** | Full (128K+) | Complex reasoning, multi-file work |

→ *Deep dive: [Agent Execution Model](../02-core-concepts/agent-execution-model.md)*

---

## Four Types of Knowledge Artifacts

Cursor uses different file types for different purposes:

### 1. Rules (`.mdc` files) — Auto-loaded by Cursor
Persistent instructions that shape AI behavior automatically:
```yaml
# .cursor/rules/standards.mdc
---
description: Code standards
alwaysApply: true
---
Always use type hints...
```
- **Extension:** `.mdc` (NOT `.md`)
- **Location:** `.cursor/rules/`
- **Activation:** Automatic

### 2. Skills (`.md` files) — Referenced manually
Step-by-step procedures you pull into conversations:
```markdown
# docs/skills/eda-workflow.md
## Step 1: Load Data
## Step 2: Check Missing Values
...
```
- **Extension:** `.md`
- **Location:** Anywhere (docs/, wiki, marketplace)
- **Activation:** `@docs/skills/eda-workflow.md`

### 3. Prompts (`.md` files) — Copy/paste templates
Reusable starting points for common tasks:
```markdown
# docs/prompts/debug-model.md
Debug why my [MODEL_TYPE] has [METRIC]...
```
- **Extension:** `.md`
- **Location:** Anywhere
- **Activation:** Copy, fill variables, paste in chat

### 4. Context References (`@`)
On-demand information pulled into any conversation:
- `@file.py` — specific file
- `@folder/` — directory contents
- `@rulename` — specific rule

→ *Deep dive: [Artifact Types](../02-core-concepts/artifact-types.md)*

---

## Why This Matters for Data Science

Data science work has unique challenges:
- **Reproducibility** is critical
- **Data leakage** is easy to introduce
- **Best practices** vary by domain and team

Cursor lets you encode these concerns once and have them applied consistently.

---

## Next Steps

- **Ready to try it?** → [First 30 Minutes](first-30-minutes.md)
- **Want deeper understanding?** → [Core Concepts](../02-core-concepts/README.md)
- **Data science focus?** → [DS Quickstart](data-science-quickstart.md)

---

## See Also

- **Previous**: [Getting Started](README.md)
- **Next**: [First 30 Minutes](first-30-minutes.md)
- **Deeper**: [Knowledge Execution System](../02-core-concepts/knowledge-execution-system.md)
