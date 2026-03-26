# P6: Parallelization

## The Pattern

Git worktrees let you check out multiple branches simultaneously in separate
directories. Open Claude in each — run different tasks in parallel without
context bleed between them.

## Why It Matters

Without worktrees, parallel work means juggling contexts in one session or
stashing/switching branches constantly. With worktrees, each branch is a
separate directory with its own Claude session — completely isolated.

## Key Concepts

**Git worktrees:** `git worktree add ../project-scratch scratch-branch` creates
a new working directory on a new branch. Both directories share the same git
repository but track different branches.

**Session isolation:** Each worktree directory gets its own Claude session.
Context from session A cannot contaminate session B. This is the key benefit.

**Use cases:**
- Exploration in worktree A while implementing in worktree B
- Running two different features simultaneously
- Testing a hypothesis without switching branches

## VS Code Equivalent

Open the worktree folder in a second VS Code window (File → Open Folder). The
Claude extension runs independently in each window — same parallel isolation
without the CLI.

## Implementation Notes

```bash
# Create a scratch worktree for codebase exploration
git worktree add ../my-project-scratch scratch-branch
cd ../my-project-scratch && claude

# List active worktrees
git worktree list

# Remove a worktree when done
git worktree remove ../my-project-scratch
```

**Naming convention:** Use descriptive branch names: `scratch/explore-auth`,
`feat/add-oauth`, `fix/session-bug`. Your worktrees become self-documenting.

**Anti-pattern:** Don't use worktrees as a substitute for good branch management.
Remove stale worktrees regularly: `git worktree prune`.
