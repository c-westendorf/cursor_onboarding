# P8: Structured Primitives

## The Pattern

Rules, agents, skills, and commands are the four primitive types of the Claude
harness. Each is a markdown file with a specific structure. Rules are always-on;
agents are specialist delegates; skills are slash-command workflows; commands
are task definitions.

## Why It Matters

Without structured primitives, you repeat context in every prompt: "remember to
write tests first", "always check for security issues", "use TypeScript". With
rules, these constraints are loaded automatically. With agents and skills, complex
workflows become single slash-commands.

## Key Concepts

**Rules (`~/.claude/rules/`):** Markdown files loaded at the start of every
conversation. Use for: coding standards, security policies, team conventions.
Keep them short and declarative — not procedural.

**Agents (`~/.claude/agents/`):** YAML frontmatter + system prompt. Scoped to
specific tasks with minimal tool permissions. Claude delegates automatically
based on the `description` field.

**Skills (`~/.claude/skills/`):** YAML frontmatter + workflow instructions.
Activated with `/skill-name`. Use for multi-step workflows you run repeatedly.

**Commands (`~/.claude/commands/`):** Task definitions for slash-commands. More
structured than skills; can invoke agents and run bash commands.

## Example Files

→ `examples/rules/testing.md` — testing standards rule
→ `examples/rules/security.md` — security standards rule
→ `examples/rules/git.md` — git workflow rule
→ `examples/agents/` — four agent examples showing scoping patterns
→ `examples/skills/` — three skill examples

## VS Code Equivalent

All four primitive types work identically in VS Code with the Claude extension.
The `~/.claude/` directory is shared between CLI and extension.

## Implementation Notes

**Rule file checklist:**
- Is it declarative? (what to do, not how to do it)
- Is it short enough to skim in 30 seconds?
- Does it conflict with another rule? (resolve conflicts explicitly)

**Agent design checklist:**
- Is the `description:` field specific enough to route correctly?
- Is the `tools:` list the minimum needed?
- Does the system prompt have a clear output format?

**File naming:** lowercase with hyphens. `testing.md` not `Testing.md`.
