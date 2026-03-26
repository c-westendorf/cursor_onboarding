# Pattern: Testing Standards Rule | Principle: P8 | Tool: Claude Code CLI / VS Code
#
# Copy to: ~/.claude/rules/testing.md
# Claude reads all files in ~/.claude/rules/ at the start of every conversation.
# This file sets your testing standards without repeating them in every prompt.
#
# Source: everything-claude-code (rules/common/testing.md)

# Testing Standards

## Minimum Test Coverage: 80%

Test types (ALL required):
1. **Unit tests** — individual functions, utilities, components
2. **Integration tests** — API endpoints, database operations
3. **E2E tests** — critical user flows only

## Test-Driven Development

MANDATORY workflow:
1. Write test first (RED)
2. Run test — it should FAIL
3. Write minimal implementation (GREEN)
4. Run test — it should PASS
5. Refactor (IMPROVE)
6. Verify coverage (80%+)

## Rules

- Write tests before implementing features — no exceptions
- Every public function needs at least one test
- Mock only at system boundaries — never mock internal modules
- Tests must pass before committing — no "fix tests later"
- Prefer integration tests over unit tests for database interactions

## When Tests Fail

1. Fix the implementation, not the test (unless the test is wrong)
2. Check test isolation — tests must not share state
3. Verify mocks are correct and minimal
4. Use the **tdd-guide** agent for complex testing problems
