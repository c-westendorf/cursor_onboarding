# P4: Subagent Orchestration

## The Pattern

An agent is a markdown file with YAML frontmatter that declares its name, model,
tool permissions, and a system prompt. Claude reads `~/.claude/agents/` and
delegates matching tasks automatically. The file format is what matters.

## Why It Matters

Without agents, every task gets the same general-purpose Claude. With agents,
you get specialists: a reviewer that can only read (not accidentally edit), a
docs agent that fetches current docs instead of guessing, a TDD agent that
refuses to write code before writing tests.

## Key Concepts

**Tool scoping:** The most important line in any agent file. A reviewer agent
that lists only `Read, Grep, Glob, Bash` cannot accidentally edit files.
A docs-lookup agent with only `Read, WebFetch` cannot touch the codebase.

**Model assignment:** Each agent declares its own model. Reviewers can use
Sonnet; a simple docs agent might use Haiku.

**Automatic delegation:** Claude routes tasks to agents based on the `description`
field. A clear, specific description is the difference between reliable delegation
and accidental invocation.

## Example Files

→ `examples/agents/docs-lookup.md` — minimal docs agent (68 lines)
→ `examples/agents/tdd-guide.md` — TDD enforcement agent (91 lines)
→ `examples/agents/security-reviewer.md` — security specialist (read-biased)
→ `examples/agents/harness-optimizer.md` — minimal example, 35 lines

## VS Code Equivalent

Same files — the Claude extension reads `~/.claude/agents/`. Create the markdown
file and the agent is immediately available. No difference.

## Implementation Notes

- Start with one agent: `docs-lookup`. It's the easiest to understand and
  immediately useful for any project.
- Write the `description:` field as if you're telling a human when to hand off
  the task: "When the user asks how to use a library..."
- Keep agents focused: one agent = one job. A "do everything" agent is just Claude.
- The `tools:` list is a security boundary — take it seriously.
