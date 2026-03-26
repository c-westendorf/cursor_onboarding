# P5: Verification & Evals

## The Pattern

A PostToolUse hook runs your type checker or test suite after every file write.
If it fails, Claude sees the output and self-corrects without you asking. This
closes the feedback loop between code generation and validation.

## Why It Matters

Without verification hooks, Claude writes code and declares it done. You have
to manually run tests and paste failures back. With a PostToolUse hook, Claude
gets immediate feedback after every edit — and self-corrects in the same turn.

## Key Concepts

**PostToolUse hook:** Fires after Claude uses the Write or Edit tool. Gets the
file path in stdin as JSON. Run your checker; exit 0 to proceed, exit 2 to block.

**Exit code 2:** Blocks Claude from continuing. Claude sees your hook's stdout
and stderr output and uses it to fix the error — exactly like you would.

**The /verify and /checkpoint commands:** Manual verification workflows that
run the full checklist: type check, tests, and a structured self-review.

## Example Files

→ `examples/hooks/post-tool-verify.sh` (PostToolUse hook)
→ `examples/skills/verification-loop/README.md` (manual /verify workflow)
→ `examples/settings/settings.json.example` (hook registration)

## VS Code Gap

PostToolUse hooks are Claude Code CLI only.

**VS Code equivalent:** Enable "Run on Save" in your test extension (Python Test
Explorer, Jest Runner, etc.) to get automatic test feedback after every file save.
Not as tightly integrated, but achieves similar feedback loops.

## Implementation Notes

- Start simple: just run `tsc --noEmit` for TypeScript projects. Add more checks later.
- Make hooks fast (<2 seconds) — slow hooks break the flow of development
- Use exit code 2 sparingly — only for errors that genuinely need fixing before proceeding
- Exit code 1 shows a warning but lets Claude continue; useful for style warnings
