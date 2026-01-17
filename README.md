# Cursor for Data Science Teams

> A comprehensive guide to using Cursor as a **knowledge execution system** for building data products

---

## What is This Guide?

This documentation helps data science teams use Cursor effectively—not just as an AI-powered IDE, but as a system that **encodes best practices once, applies them consistently, and scales knowledge without scaling meetings**.

**Core insight:** Cursor sits between *what you want* and *what gets written*. Its effectiveness depends on how knowledge is codified, scoped, and enforced.

---

## Quick Navigation

| I want to... | Go to |
|--------------|-------|
| Get started immediately | [First 30 Minutes](01-getting-started/first-30-minutes.md) |
| Understand the core concepts | [Core Concepts](02-core-concepts/README.md) |
| Write my first rule | [Rules Deep Dive](03-rules-deep-dive/README.md) |
| Set up for data science work | [DS Workflows](04-data-science-workflows/README.md) |
| Connect external tools (MCP) | [MCP Integration](05-mcp-integration/README.md) |
| Organize my workspace | [Workspace Organization](06-workspace-organization/README.md) |
| Find shared rules & skills | [Marketplace](08-marketplace/README.md) |
| See the full document index | [Navigation](NAVIGATION.md) |

---

## The 3-Layer Knowledge Stack

Cursor works best when you **separate concerns deliberately**:

```
┌────────────────────────────────────┐
│  Layer 1: Principles               │  ← Rules (.mdc files)
│  "What NOT to do / invariants"     │     Shape default behavior
└────────────────┬───────────────────┘
                 ▼
┌────────────────────────────────────┐
│  Layer 2: Playbooks                │  ← Skills + Prompts
│  "How to do it well"               │     Repeatable procedures
└────────────────┬───────────────────┘
                 ▼
┌────────────────────────────────────┐
│  Layer 3: Enforcement              │  ← Code + CI
│  "Fail if wrong"                   │     Prevent drift
└────────────────────────────────────┘
```

- **If everything is a rule** → context bloat
- **If everything is a prompt** → inconsistency
- **If everything is code** → slow iteration

[Learn more about the 3-Layer Stack →](02-core-concepts/3-layer-stack.md)

---

## Start Here Based on Your Role

### New to Cursor
Start with the basics and build understanding progressively.

1. [What is Cursor?](01-getting-started/what-is-cursor.md) (30 seconds)
2. [First 30 Minutes](01-getting-started/first-30-minutes.md) (hands-on setup)
3. [Core Concepts](02-core-concepts/README.md) (mental models)

### Data Scientist
Focus on workflows relevant to your daily work.

1. [DS Quickstart](01-getting-started/data-science-quickstart.md) (15 minutes)
2. [Jupyter & Pandas](04-data-science-workflows/jupyter-notebooks.md)
3. [Common Challenges](04-data-science-workflows/common-challenges.md)

### Team Lead / Platform Engineer
Focus on organization and governance.

1. [Workspace Organization](06-workspace-organization/README.md)
2. [Team Maturity Journey](07-team-maturity-journey/README.md)
3. [Marketplace Governance](08-marketplace/governance/README.md)

### Looking for Shared Resources
Browse the organization's curated rules, skills, and prompts.

1. [Marketplace Overview](08-marketplace/README.md)
2. [Rules Catalog](08-marketplace/catalog/rules-by-domain.md)
3. [Shared Skills](08-marketplace/catalog/shared-skills.md)

---

## Documentation Structure

This documentation uses **progressive disclosure**—start broad, zoom in as needed:

```
Layer 0: This README (entry point)
    │
    ├── Layer 1: Section READMEs (orientation)
    │       │
    │       ├── Layer 2: Topic documents (concepts & how-to)
    │       │       │
    │       │       └── Layer 3: Reference (specifications)
    │       │
    │       └── Layer 2: Examples (annotated code)
    │
    └── Navigation.md (flat index)
```

Each section's README provides:
- Table of contents
- Suggested reading order
- Prerequisites

---

## Key Decision Framework

When deciding **where knowledge belongs**, use this flow:

```
Is it stable for 6-12 months?
    │
    ├── NO → Human judgment or ad-hoc prompt
    │
    └── YES → Should violations block CI/prod?
                  │
                  ├── YES → Code / CI enforcement
                  │
                  └── NO → Does it apply broadly?
                              │
                              ├── YES → Cursor Rule (.mdc)
                              │
                              └── NO → Is it repeatable?
                                          │
                                          ├── YES → Skill / Prompt template
                                          │
                                          └── NO → Human judgment
```

[Full decision flow with examples →](02-core-concepts/decision-flow/README.md)

---

## Quick Links

### By Topic
- [Rules: anatomy, types, best practices](03-rules-deep-dive/README.md)
- [MCP: connecting external tools](05-mcp-integration/README.md)
- [Anti-patterns: what to avoid](09-anti-patterns/README.md)

### Reference
- [MDC file schema](reference/mdc-schema.md)
- [Glossary](reference/glossary.md)
- [Troubleshooting](reference/troubleshooting.md)

### Templates
- [Basic rule template](templates/basic-rule.mdc)
- [Project structure templates](templates/README.md)

---

## Source Materials

This documentation synthesizes and organizes content from:
- [Cursor Data Science Research](cursor_data_science_research.md) — feature deep-dives
- [Decision Flow](cursor_decion_flow.md) — knowledge classification framework
- [Playbook v4](cursor_playbook_v4.md) — system architecture and mental models

---

*Last updated: January 2026*
