# Pattern: Research-First Skill | Principle: P9 | Tool: Claude Code CLI / VS Code
#
# Copy to: ~/.claude/skills/search-first/SKILL.md (rename README.md to SKILL.md)
# Activate with: /search-first before starting any implementation task
#
# Source: everything-claude-code (skills/search-first/SKILL.md) — simplified.

---
name: search-first
description: Research before writing code. Check for existing libraries, patterns,
  and documentation before implementing anything from scratch.
---

# /search-first — Research Before You Code

Prevents reinventing the wheel. Forces a "what already exists?" pass before
touching any implementation files.

## When to Use

- Starting a new feature that likely has existing solutions
- Adding any new dependency or integration
- Before creating a new utility, helper, or abstraction
- Anytime you'd normally start coding immediately

## Workflow

```
1. DEFINE — What functionality is needed? What constraints exist?
2. SEARCH — Check package registry, project codebase, and documentation
   ├── npm/PyPI/pkg.go.dev — is there a maintained library?
   ├── Project codebase — does this pattern already exist here?
   └── Library docs — check /llms.txt if available
3. EVALUATE — Score candidates: functionality, maintenance, license, dependencies
4. DECIDE — Adopt / Extend / Build (in order of preference)
5. IMPLEMENT — Only after steps 1-4 are complete
```

## Decision Rules

| Signal | Action |
|--------|--------|
| Exact match, well-maintained, permissive license | **Adopt** — install and use directly |
| Partial match, good foundation | **Extend** — install + write thin wrapper |
| Multiple weak matches | **Compose** — combine 2-3 small packages |
| Nothing suitable | **Build** — write custom, informed by research |

## llms.txt

Many libraries publish a machine-readable docs summary at `/llms.txt`:
- `docs.library.com/llms.txt`
- Try it for any library before asking Claude to guess at the API

## Output Before Implementing

Before writing any code, output:
1. What you searched for and where
2. What you found (name, version, stars/downloads if relevant)
3. Your recommendation (Adopt/Extend/Build) and one-sentence rationale
4. Then proceed with implementation
