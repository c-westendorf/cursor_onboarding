# Reference

[Home](../README.md) > Reference

---

## Overview

Technical reference documentation for quick lookup.

---

## Documents in This Section

| Document | Description |
|----------|-------------|
| [MDC Schema](mdc-schema.md) | Complete YAML frontmatter specification |
| [Glossary](glossary.md) | Terminology definitions |
| [Troubleshooting](troubleshooting.md) | Common issues and solutions |

---

## Quick Links

### MDC Frontmatter

```yaml
---
description: Required, under 100 chars
globs: "**/*.py"        # Optional, for auto-attach
alwaysApply: false      # Optional, default false
---
```

### Rule Activation Types

| Type | Config | When Active |
|------|--------|-------------|
| Always | `alwaysApply: true` | Every interaction |
| Auto | `globs: "pattern"` | Matching files in context |
| On-demand | Neither | When invoked with @name |

### Glob Patterns

| Pattern | Matches |
|---------|---------|
| `**/*.py` | All Python files |
| `src/**/*` | Everything under src/ |
| `*.{py,ipynb}` | Python and notebooks |
| `tests/**/*.py` | Python files in tests/ |

---

## See Also

- [MDC Schema](mdc-schema.md)
- [Glossary](glossary.md)
- [Troubleshooting](troubleshooting.md)
