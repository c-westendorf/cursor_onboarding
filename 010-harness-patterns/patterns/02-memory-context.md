# P2: Memory & Context

## The Pattern

Claude has no memory between sessions by default. Three hooks — Stop,
SessionStart, and PreCompact — create a persistence layer that survives
session boundaries.

## Why It Matters

Without memory hooks, every session starts cold. You repeat context, re-explain
decisions, and lose the thread of multi-day work. With hooks, Claude loads the
state of your last session automatically — no prompt engineering required.

## Key Concepts

**Stop hook:** Runs when Claude finishes a session. Saves session state to
`~/.claude/sessions/`. This is the write side of memory.

**SessionStart hook:** Runs when Claude starts a new session. Reads the last
session file and injects a summary into context. This is the read side.

**PreCompact hook:** Runs just before Claude compacts its context. Saves a
snapshot so you can review what was lost during compaction.

## Example Files

→ `examples/hooks/session-end.js` (Stop hook)
→ `examples/hooks/session-start.js` (SessionStart hook)
→ `examples/hooks/pre-compact.js` (PreCompact hook)
→ `examples/settings/settings.json.example` (hook registration)

## VS Code Gap

Hooks require Claude Code CLI lifecycle events (Stop, SessionStart, PreCompact).
These events don't fire in the VS Code Claude extension.

**VS Code workaround:** Maintain a `context.md` file in your project root and
update it manually at the end of each session. Add it to `.claudeignore` to
keep it out of Claude's automatic file reads, then paste it explicitly when
starting a new session.

## Implementation Notes

- Start with just the Stop hook — even a simple one that writes a timestamp
  and summary is better than nothing
- The `sessions/` directory grows over time — add a cleanup step to your Stop
  hook to keep only the last 30 sessions
- Session files are plain JSON — you can read them directly to review history
