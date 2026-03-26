# P7: Security

## The Pattern

A UserPromptSubmit hook inspects every message before Claude sees it. It blocks
prompts that contain credentials, rejects injection attempts, or flags suspicious
patterns. This runs at the first line of defense — before any tool use.

## Why It Matters

Without a prompt scan hook, pasting a log file that happens to contain an API
key will send that key to the API. A UserPromptSubmit hook catches this before
transmission. It also protects against accidental prompt injection when pasting
external content.

## Key Concepts

**UserPromptSubmit hook:** Fires before every user message. Gets the prompt text
in stdin as JSON. Exit 0 to allow, exit 2 to block.

**Secret patterns:** Regular expressions that match common credential formats
(API keys, AWS tokens, private keys). One match = block the prompt.

**Prompt injection:** When external content (docs, logs, web pages) contains
instructions to Claude. The hook can detect and flag this pattern.

## Example Files

→ `examples/hooks/secret-scan.js` (UserPromptSubmit hook)
→ `examples/rules/security.md` (security coding standards)
→ `examples/agents/security-reviewer.md` (code security audit agent)

## VS Code Gap

UserPromptSubmit hooks are Claude Code CLI only.

**VS Code workaround:** Use file references instead of pasting content directly.
`@filename.log` loads the file into context without you seeing its contents —
reducing the chance of accidentally including credentials in the chat.

## Implementation Notes

- Start with the 5 most common patterns: OpenAI keys, AWS access keys, GitHub
  tokens, GitHub OAuth tokens, and inline `password=` assignments. These cover
  ~80% of accidental leaks.
- Keep the hook fast — it fires on EVERY message. Pure regex, no I/O.
- Log blocked attempts (to a local file, not a remote service) — useful for
  understanding what's being caught.
- The hook blocks the prompt, not the session — the user can fix the message
  and resend.
