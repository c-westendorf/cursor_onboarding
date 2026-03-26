# Pattern: Security Standards Rule | Principle: P7, P8 | Tool: Claude Code CLI / VS Code
#
# Copy to: ~/.claude/rules/security.md
# Claude reads all files in ~/.claude/rules/ at the start of every conversation.
# This file enforces security standards without repeating them in every prompt.
#
# Source: everything-claude-code (rules/common/security.md)

# Security Standards

## Before ANY commit, verify:

- [ ] No hardcoded secrets (API keys, passwords, tokens) in source code
- [ ] All user inputs validated and sanitized
- [ ] SQL queries use parameterized statements (no string concatenation)
- [ ] HTML output is escaped or using framework auto-escaping
- [ ] CSRF protection enabled on state-changing endpoints
- [ ] Authentication checked on every protected route
- [ ] Rate limiting on all public endpoints
- [ ] Error messages don't leak implementation details or sensitive data

## Secret Management

- NEVER hardcode secrets in source code — use environment variables or a secret manager
- ALWAYS validate that required secrets are present at startup
- Rotate any secrets that may have been exposed immediately
- Use `.env.example` for documentation; `.env` for actual values (gitignored)

## When a Security Issue Is Found

1. STOP current task immediately
2. Invoke the **security-reviewer** agent
3. Fix all CRITICAL issues before continuing any other work
4. Rotate any exposed credentials
5. Check the rest of the codebase for the same pattern

## Common Violations (high priority)

| Pattern | Never do this | Do this instead |
|---------|--------------|-----------------|
| Secrets in code | `const key = "sk-abc123"` | `process.env.API_KEY` |
| String SQL | `"SELECT * WHERE id=" + id` | Parameterized query |
| HTML injection | `el.innerHTML = userInput` | `el.textContent = userInput` |
| Unvalidated redirect | `res.redirect(req.query.next)` | Allowlist of valid URLs |
