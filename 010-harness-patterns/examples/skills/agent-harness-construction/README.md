# Pattern: Agent Harness Construction Skill | Principle: P4 | Tool: Claude Code CLI / VS Code
#
# Copy to: ~/.claude/skills/agent-harness-construction/SKILL.md (rename README.md to SKILL.md)
# Activate with: /agent-harness-construction when designing your harness
#
# Source: everything-claude-code (skills/agent-harness-construction/SKILL.md) — simplified.

---
name: agent-harness-construction
description: Design and build an AI agent harness. Use when setting up a new
  project's agent configuration or auditing an existing one.
---

# /agent-harness-construction — Build Your Agent Harness

A structured approach to building the configuration layer that wraps Claude
in your development workflow.

## Harness Components (in setup order)

```
~/.claude/
├── settings.json     ← Model routing, token limits, hook registration
├── rules/            ← Always-on guidelines Claude reads every session
├── agents/           ← Subagent definitions (specialist delegation)
├── skills/           ← Slash-command workflows (/tdd, /review, etc.)
├── hooks/            ← Lifecycle automation (session, tool use events)
└── sessions/         ← Persisted session state (written by hooks)
```

## Design Principles

### 1. Rules before agents
Set up your rules/ first — they constrain all conversations including
agent sessions. Security rules and coding standards go here.

### 2. Scope agents tightly
Each agent should have the minimum tools needed for its job.
A reviewer doesn't need Write. A docs-lookup agent doesn't need Edit.

### 3. One hook per concern
Don't write one hook that does five things. Write five focused hooks.
They're easier to debug and can be disabled independently.

### 4. Measure before optimizing
Before adding hooks or agents, run /harness-audit to see what's
actually costing tokens or causing failures.

## Quick Setup Checklist

- [ ] Create directory structure: `mkdir -p ~/.claude/rules ~/.claude/agents ~/.claude/skills ~/.claude/hooks ~/.claude/sessions`
- [ ] Copy settings.json.example to ~/.claude/settings.json and set your model
- [ ] Add testing.md and security.md to rules/
- [ ] Add at least one agent (docs-lookup is a good start)
- [ ] Add the secret-scan UserPromptSubmit hook
- [ ] Add session-end Stop hook for memory persistence
- [ ] Test: start a Claude session and verify hooks fire

## Audit Command

After setup, run `/harness-audit` to get a scorecard of your configuration.
It checks hook coverage, rule completeness, agent scoping, and cost settings.
