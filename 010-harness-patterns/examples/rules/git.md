# Pattern: Git Workflow Rule | Principle: P8 | Tool: Claude Code CLI / VS Code
#
# Copy to: ~/.claude/rules/git.md
# Claude reads all files in ~/.claude/rules/ at the start of every conversation.
# This file encodes your git conventions without repeating them in every prompt.
#
# Source: everything-claude-code (rules/common/git-workflow.md)

# Git Workflow

## Commit Message Format

```
<type>: <description>

<optional body explaining WHY, not what>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`

Examples:
- `feat: add user authentication via OAuth`
- `fix: prevent race condition in session expiry`
- `docs: update API endpoint documentation`

## Commit Rules

- One logical change per commit — don't batch unrelated changes
- Write the description in imperative mood: "add X", not "added X" or "adds X"
- If the why isn't obvious from the code, add a body paragraph
- Never commit secrets, credentials, or `.env` files
- Tests must pass before committing

## Pull Request Workflow

1. Analyze the full commit history for the branch (not just the latest commit)
2. Use `git diff [base-branch]...HEAD` to see all changes
3. Write a PR summary that explains WHY, not just what changed
4. Include a test plan as a checklist
5. Push with `-u` flag on first push for a new branch

## Branch Naming

- Features: `feat/short-description`
- Fixes: `fix/short-description`
- Experiments: `scratch/short-description` (use git worktrees for these)
