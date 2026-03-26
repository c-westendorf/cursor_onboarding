# harness-patterns

A reference library of working examples for the **Agent Harness Optimization** presentation.

## What This Is

This is a **pattern reference**, not an install script.

Every file here demonstrates one concept from the presentation. Copy what you need, adapt to your project, and ignore the rest. Nothing here requires cloning this repo to work — each file is self-contained.

## What This Is Not

- Not a framework or platform
- Not a one-command installer
- Not a dependency you'll have to maintain

## How to Use

Browse the `examples/` directory. Each file has a comment header telling you which principle it illustrates and which tool it targets.

```
examples/
├── hooks/      ← Session lifecycle automation (Claude Code CLI)
├── agents/     ← Subagent definitions (Claude Code CLI + VS Code)
├── rules/      ← Always-on coding guidelines (Claude Code CLI + VS Code)
├── skills/     ← Slash-command workflows (Claude Code CLI + VS Code)
└── settings/   ← Token economics config (Claude Code CLI + VS Code)
```

The `patterns/` directory has a concept explanation for each of the 9 principles, with pointers to the relevant example files.

## Quick Start

1. Create your harness directories:
   ```bash
   mkdir -p ~/.claude/rules ~/.claude/agents ~/.claude/skills ~/.claude/commands ~/.claude/hooks ~/.claude/sessions
   ```

2. Copy what you want into the right place:
   ```bash
   # Rules (works in both Claude Code CLI and VS Code extension)
   cp examples/rules/testing.md ~/.claude/rules/
   cp examples/rules/security.md ~/.claude/rules/

   # Agents (works in both)
   cp examples/agents/docs-lookup.md ~/.claude/agents/

   # Hooks (Claude Code CLI only)
   cp examples/hooks/session-end.js ~/.claude/hooks/
   # Then register in ~/.claude/settings.json
   ```

3. Browse `patterns/` to understand the concept behind each file.

## Tool Compatibility

| Feature | Claude Code CLI | VS Code (Claude extension) |
|---------|-----------------|---------------------------|
| rules/ | ✓ | ✓ |
| agents/ | ✓ | ✓ |
| skills/ | ✓ | ✓ |
| settings.json | ✓ | ✓ |
| hooks/ | ✓ | — (lifecycle events not available) |

For VS Code hook equivalents, see the individual `patterns/0n-*.md` files.

## License

MIT. Use freely. Attribution appreciated but not required.
