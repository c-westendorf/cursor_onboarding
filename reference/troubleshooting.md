# Troubleshooting

[Home](../README.md) > [Reference](README.md) > Troubleshooting

---

## Overview

Common issues and solutions when working with Cursor rules and configuration.

---

## Rules Not Working

### Rule Not Appearing in List

**Symptoms:**
- Rule doesn't show when typing `@`
- Rule not in "Cursor Settings > Rules"

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Wrong file location | Move to `.cursor/rules/` directory |
| Wrong extension | Rename to `.mdc` (not `.md`) |
| Invalid YAML | Fix frontmatter syntax |
| Missing frontmatter | Add `---` delimiters |
| Cursor not reloaded | Restart Cursor or reload window |

**Validation:**
```bash
# Check file exists
ls -la .cursor/rules/

# Validate YAML
cat .cursor/rules/my-rule.mdc | head -20
```

### Rule Not Auto-Attaching

**Symptoms:**
- Rule has `globs` but doesn't activate
- Files match pattern but rule ignored

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Wrong glob pattern | Test pattern matches your files |
| File not in context | Open or reference the file |
| Pattern too specific | Use broader pattern like `**/*.py` |
| Conflicting rules | Check for duplicate rules |

**Debug:**
```bash
# Test if glob matches files
# In project root
ls **/*.py  # Should list files you expect

# Compare to your glob
globs: "**/*.py"  # Should match
```

### Rule Content Ignored

**Symptoms:**
- Rule activates but instructions not followed
- AI seems to ignore rule guidance

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Rule too long | Keep under 300 lines |
| Instructions unclear | Use direct, imperative language |
| Conflicting rules | Remove contradictions |
| Context overflow | Reduce active rules |
| Instructions too vague | Be specific about what to do |

**Best Practice:**
```markdown
# Bad: Vague
Write good code.

# Good: Specific
- Use type hints for all function parameters
- Add docstrings to public functions
- Limit functions to 50 lines maximum
```

---

## YAML Errors

### Parse Errors

**Symptoms:**
- Rule fails to load
- Syntax error messages

**Common Causes:**

```yaml
# Error: Unquoted special characters
description: Code style: Python  # Colon causes issues
# Fix:
description: "Code style: Python"

# Error: Incorrect indentation
globs:
- "**/*.py"  # Missing space after dash
# Fix:
globs:
  - "**/*.py"

# Error: Missing quotes on glob
globs: **/*.py  # Asterisks need quotes
# Fix:
globs: "**/*.py"
```

### Frontmatter Not Recognized

**Symptoms:**
- YAML appears as content
- Rule metadata not parsed

**Solution:**
Ensure proper delimiters:
```yaml
---
description: My rule
---

# Content starts here
```

**Not:**
```yaml
description: My rule
---
# Missing opening ---
```

---

## Context Issues

### Context Window Exceeded

**Symptoms:**
- "Context too long" errors
- Responses cut off
- AI forgets earlier conversation

**Solutions:**

1. **Reduce active rules:**
   - Disable always-apply rules not needed
   - Use more specific globs

2. **Reduce file context:**
   - Close unnecessary files
   - Use `.cursorignore` for large files

3. **Start fresh conversation:**
   - Context accumulates; new chat resets

4. **Be selective:**
   - Only `@`-reference files you need

### AI Not Using Context

**Symptoms:**
- AI ignores open files
- Doesn't know about referenced code

**Solutions:**

1. **Explicitly reference:**
   ```
   Look at @src/utils.py and refactor the parse function
   ```

2. **Check file is indexed:**
   - Not in `.cursorignore`
   - Not a binary file
   - File exists and is readable

3. **Reload indexing:**
   - Command Palette > "Cursor: Resync Index"

---

## MCP Issues

### MCP Server Not Connecting

**Symptoms:**
- Server listed but not available
- Connection timeout errors

**Solutions:**

1. **Check server is running:**
   ```bash
   # For stdio servers, check process
   ps aux | grep mcp-server
   ```

2. **Verify configuration:**
   ```json
   // .cursor/mcp.json
   {
     "mcpServers": {
       "myserver": {
         "command": "npx",
         "args": ["-y", "@org/mcp-server"]
       }
     }
   }
   ```

3. **Check logs:**
   - View > Output > MCP

4. **Restart Cursor:**
   - MCP connections established on startup

### MCP Tools Not Appearing

**Symptoms:**
- Server connects but tools unavailable
- "No tools found" messages

**Solutions:**

1. **Server implementation issue:**
   - Check server exposes tools correctly
   - Verify tool definitions in server code

2. **Permissions:**
   - Some tools require explicit enabling
   - Check Cursor settings

---

## Performance Issues

### Slow Responses

**Symptoms:**
- Long wait times for AI responses
- Typing lag in editor

**Solutions:**

1. **Reduce context:**
   - Fewer open files
   - Fewer active rules

2. **Check indexing:**
   - Large repos take time to index
   - Use `.cursorignore` for vendor/dependencies

3. **Network:**
   - Check internet connection
   - API might be under load

### High Memory Usage

**Symptoms:**
- Cursor consuming excessive RAM
- System slowdown

**Solutions:**

1. **Reduce workspace size:**
   - Split into smaller workspaces
   - Use `.cursorignore`

2. **Close unused tabs:**
   - Each open file uses memory

3. **Restart Cursor:**
   - Clears accumulated state

---

## File Issues

### Files Not Appearing in Search

**Symptoms:**
- Can't find files with Cmd/Ctrl+P
- Files not in codebase search

**Solutions:**

1. **Check `.cursorignore`:**
   ```bash
   cat .cursorignore
   # Ensure not excluding wanted files
   ```

2. **Check file size:**
   - Very large files may be excluded
   - Binary files not indexed

3. **Resync index:**
   - Command Palette > "Cursor: Resync Index"

### Binary Files in Context

**Symptoms:**
- AI confused by file content
- Garbled text in responses

**Solutions:**

Add to `.cursorignore`:
```
# Binary files
*.png
*.jpg
*.pdf
*.zip
*.exe

# Generated
node_modules/
__pycache__/
*.pyc
```

---

## Getting Help

### Cursor Support

1. **Documentation:** [cursor.com/docs](https://cursor.com/docs)
2. **Community:** Cursor Discord server
3. **Issues:** GitHub issues

### Debug Information

When reporting issues, include:

1. **Cursor version:** Help > About
2. **OS and version:** macOS/Windows/Linux
3. **Rule content:** (if rule-related)
4. **Error messages:** From Output panel
5. **Steps to reproduce:** What you did before the issue

---

## See Also

- [MDC Schema](mdc-schema.md)
- [Context Budgeting](../03-rules-deep-dive/context-budgeting.md)
- [.cursorignore Guide](../06-workspace-organization/cursorignore-guide.md)
