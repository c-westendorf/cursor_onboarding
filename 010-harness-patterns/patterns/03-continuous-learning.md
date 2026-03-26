# P3: Continuous Learning

## The Pattern

A Stop hook evaluates each session and extracts reusable patterns. Over time,
these patterns compound into a project-specific knowledge base that makes
Claude progressively better at your codebase.

## Why It Matters

Without learning hooks, every session starts with the same generic Claude. With
them, Claude accumulates knowledge about your patterns, decisions, and preferences
— and can load that knowledge into subsequent sessions via rules or context files.

## Key Concepts

**Pattern extraction:** After each session, the Stop hook appends a summary to
`~/.claude/patterns.md`. This file grows into a searchable pattern library.

**The `/learn` and `/learn-eval` commands:** Invoke these at the end of a session
to explicitly extract and evaluate what was learned.

**The `/evolve` command:** Clusters accumulated patterns into skills — converting
ad-hoc learnings into formal, reusable workflows.

## Example Files

→ `examples/hooks/session-end.js` (includes pattern capture)

## VS Code Gap

Stop hooks are Claude Code CLI only.

**VS Code workaround:** Create a keyboard shortcut that opens `~/.claude/patterns.md`
and prompts you to add a one-line note after each session. Manual, but effective.

## Implementation Notes

- The simplest possible learning hook: append a line to patterns.md with the
  date and a one-line summary. That's it. Build from there.
- Review patterns.md weekly — delete stale entries, promote good ones to rules/
- A pattern that recurs 3+ times should become a rule file
- Patterns that recur 10+ times with variations should become a skill
