# Pattern: Verification Loop Skill | Principle: P5 | Tool: Claude Code CLI / VS Code
#
# Copy to: ~/.claude/skills/verification-loop/SKILL.md (rename README.md to SKILL.md)
# Activate with: /verification-loop or /verify after completing a feature
#
# Source: everything-claude-code (skills/verification-loop/SKILL.md) — simplified.

---
name: verification-loop
description: Verify that implementation is complete and correct before declaring
  done. Runs type check, tests, and a structured self-review checklist.
---

# /verification-loop — Don't Ship Until It's Verified

A structured checklist to run before declaring any task complete.
Catches the "I think it works" vs "I verified it works" gap.

## When to Use

- Before saying "done" on any feature
- After fixing a bug (verify the fix doesn't break something else)
- Before creating a PR or commit
- When the post-tool-verify hook caught errors and you've fixed them

## Verification Steps

### 1. Type check / linter
```bash
# TypeScript
npx tsc --noEmit

# Python
mypy . --ignore-missing-imports
python -m flake8 .

# Go
go vet ./...
```

### 2. Tests
```bash
npm test          # Node.js
pytest            # Python
go test ./...     # Go
```

### 3. Self-review checklist

Before marking complete:
- [ ] The task description is fully addressed (re-read it)
- [ ] No new type errors or linter warnings
- [ ] All existing tests still pass
- [ ] New code has tests (if applicable)
- [ ] No debug code, console.log, or temporary hacks left in
- [ ] No secrets or credentials in changed files
- [ ] Error cases are handled

### 4. Edge cases

Think through:
- What happens with empty input?
- What happens with the maximum expected input?
- What if a dependency is unavailable?

## Output Format

```
VERIFICATION — [task name]
Type check: PASS / FAIL (errors listed)
Tests: PASS / FAIL (X passed, Y failed)
Self-review: PASS / NEEDS WORK

Issues found:
  - [description + location]

Ready to ship: YES / NO
```
