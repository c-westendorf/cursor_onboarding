# P1: Token Economics

## The Pattern

Every token costs money and burns context. The harness controls costs by routing
tasks to the cheapest model that can handle them, capping thinking tokens, and
triggering context compaction before the window fills.

## Why It Matters

Without token controls, an unconfigured Claude instance defaults to the most
expensive model for every task, uses unlimited thinking tokens, and waits until
context is 80% full to compact. These defaults can triple your costs compared
to a tuned configuration.

## Key Concepts

**Model routing:** Haiku for simple/repetitive tasks, Sonnet for default, Opus
only when the first attempt fails or the task requires deep architectural reasoning.
Cost ratio: Haiku ~5× cheaper than Opus; Sonnet ~1.7× cheaper.

**Thinking token cap:** `MAX_THINKING_TOKENS=10000` prevents runaway reasoning
costs on tasks that don't benefit from extended thinking.

**Early compaction:** `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50` triggers compaction
at 50% context instead of 80%. Earlier compaction produces smaller summaries,
which reduces the token cost of every subsequent turn.

## Example File

→ `examples/settings/settings.json.example`

## VS Code Equivalent

Same file — the Claude extension reads `~/.claude/settings.json`. No difference.

## Implementation Notes

- Start with Sonnet as default — it handles 95% of development tasks well
- Add `"use haiku"` to prompts for formatting, simple transforms, repetitive subtasks
- Reserve Opus for genuine architectural decisions, not just "hard" tasks
- Monitor costs with `/cost` command before and after tuning
