# Templates

[Home](../README.md) > Templates

---

## Overview

Starter templates for creating your own rules, skills, and prompts.

---

## Available Templates

| Template | Description | Use Case |
|----------|-------------|----------|
| [Basic Rule](basic-rule.mdc) | Minimal rule structure | Quick rule creation |

---

## Using Templates

### 1. Copy Template

```bash
# Copy to your rules directory
cp templates/basic-rule.mdc .cursor/rules/my-new-rule.mdc
```

### 2. Customize

Edit the copied file:
1. Update the `description` field
2. Set `globs` if auto-attach needed
3. Set `alwaysApply` if always-on needed
4. Replace placeholder content

### 3. Test

1. Reload Cursor window
2. Verify rule appears in `@` menu
3. Test activation behavior

---

## Template Guidelines

When creating from templates:

**Do:**
- Keep descriptions under 100 characters
- Include working code examples
- Show both good and bad patterns
- Stay under 300 lines total

**Don't:**
- Include tutorial content
- Add excessive commentary
- Duplicate existing rules
- Use vague instructions

---

## Creating New Templates

If you create a useful template pattern:

1. Generalize specific content
2. Add clear placeholder markers
3. Include inline comments
4. Submit to marketplace

---

## See Also

- [Writing Effective Rules](../03-rules-deep-dive/writing-effective-rules.md)
- [MDC Schema](../reference/mdc-schema.md)
- [Marketplace Templates](../08-marketplace/catalog/README.md)
