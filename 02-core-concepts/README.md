# Core Concepts

[Home](../README.md) > Core Concepts

---

## Overview

This section explains the mental models that make Cursor effective. Understanding these concepts helps you make better decisions about how to structure your rules, skills, and workflows.

---

## Key Concepts

### 1. [Knowledge Execution System](knowledge-execution-system.md)
Cursor is not a chat tool — it's a system that executes codified knowledge. Understanding this changes how you think about configuration.

### 2. [The 3-Layer Stack](3-layer-stack.md)
Knowledge belongs in different places depending on its nature. Learn to separate **principles** (rules), **playbooks** (skills), and **enforcement** (code).

### 3. [Artifact Types](artifact-types.md)
Compare Rules (`.mdc`) vs Skills (`.md`) vs Prompts (`.md`) vs Code — file formats, activation methods, and when to use each.

### 4. [Agent Execution Model](agent-execution-model.md)
Cursor runs ONE agent per session. Learn how specialization happens through knowledge configuration (rules, skills, context) and how to use Ask vs Agent mode efficiently.

### 5. [Decision Flow](decision-flow/README.md)
A systematic framework for deciding where knowledge belongs. Includes detailed criteria and examples for each decision point.

---

## Suggested Reading Order

**For conceptual understanding:**
1. [Knowledge Execution System](knowledge-execution-system.md) (5 min)
2. [3-Layer Stack](3-layer-stack.md) (5 min)
3. [Artifact Types](artifact-types.md) (5 min)
4. [Interaction Modes](interaction-modes.md) (5 min)

**For practical decision-making:**
1. [Decision Flow Overview](decision-flow/README.md) (3 min)
2. Individual decision boxes as needed

---

## Quick Reference

### Where Does This Knowledge Belong?

| If the knowledge is... | Then use... |
|------------------------|-------------|
| Stable AND should block CI | Code / CI |
| Stable AND applies broadly | Cursor Rule (`.mdc`) |
| Stable AND narrow scope | On-demand Rule |
| Ephemeral AND repeatable | Prompt Template / Skill |
| Ephemeral AND situational | Human judgment |

### The Separation of Concerns

```
Layer 1: Principles (Rules)      → "What NOT to do"
Layer 2: Playbooks (Skills)      → "How to do it well"
Layer 3: Enforcement (Code/CI)   → "Fail if wrong"
```

---

## Documents in This Section

| Document | Time | Description |
|----------|------|-------------|
| [knowledge-execution-system.md](knowledge-execution-system.md) | 5 min | Mental model for Cursor |
| [3-layer-stack.md](3-layer-stack.md) | 5 min | Principles, playbooks, enforcement |
| [artifact-types.md](artifact-types.md) | 5 min | Rules (.mdc) vs skills (.md) vs prompts vs code |
| [agent-execution-model.md](agent-execution-model.md) | 5 min | Single-agent model, knowledge-driven specialization |
| [decision-flow/](decision-flow/README.md) | 10+ min | Full decision framework |

---

## See Also

- **Previous Section**: [Getting Started](../01-getting-started/README.md)
- **Next Section**: [Rules Deep Dive](../03-rules-deep-dive/README.md)
- **Full Index**: [Navigation](../NAVIGATION.md)
