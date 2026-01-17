# First 30 Minutes with Cursor

[Home](../README.md) > [Getting Started](README.md) > First 30 Minutes

---

## Overview

This hands-on tutorial takes you from installation to your first AI-assisted coding session with a custom rule.

**Time:** ~30 minutes
**Prerequisites:** Cursor installed, a project to work on

---

## Part 1: Basic Setup (5 minutes)

### Step 1: Open Your Project

1. Launch Cursor
2. Open a project folder (`File → Open Folder`)
3. Let Cursor index your codebase (you'll see a progress indicator)

### Step 2: Verify AI Features

1. Open any code file
2. Start typing — you should see AI completions appear
3. Press `Tab` to accept a completion

### Step 3: Try the Chat

1. Press `Cmd+L` (Mac) or `Ctrl+L` (Windows/Linux) to open chat
2. Ask: "What does this file do?"
3. The AI will analyze the current file and respond

---

## Part 2: Create Your First Rule (10 minutes)

Rules are how you teach Cursor your standards. Let's create a simple one.

### Step 1: Create the Rules Directory

```bash
mkdir -p .cursor/rules
```

### Step 2: Create a Basic Rule

Create a file at `.cursor/rules/code-standards.mdc`:

```markdown
---
description: Basic code quality standards for this project
alwaysApply: true
---

# Code Standards

When writing or modifying code:

1. **Add docstrings** to all functions explaining what they do
2. **Use descriptive variable names** — no single letters except for loop indices
3. **Handle errors explicitly** — don't let exceptions pass silently

Example of good code:
```python
def calculate_average(values: list[float]) -> float:
    """Calculate the arithmetic mean of a list of numbers.

    Args:
        values: List of numeric values

    Returns:
        The arithmetic mean

    Raises:
        ValueError: If the list is empty
    """
    if not values:
        raise ValueError("Cannot calculate average of empty list")
    return sum(values) / len(values)
```
```

### Step 3: Test the Rule

1. Open a Python file (or create one)
2. Press `Cmd+L` / `Ctrl+L` to open chat
3. Ask: "Write a function to find the maximum value in a list"
4. Notice that the AI now includes docstrings and proper error handling

---

## Part 3: Understanding How Cursor Works (10 minutes)

Cursor runs **one agent per session**. You make it "specialized" through the knowledge you configure.

### The 3-Layer System

| Layer | What It Is | How to Use Efficiently |
|-------|------------|------------------------|
| **Rules (.mdc)** | Auto-loaded constraints | Put in `.cursor/rules/`, use globs for file-type targeting |
| **Skills (.md)** | Workflow procedures | Reference with `@skill-name.md` when needed |
| **Context (@)** | On-demand information | Pull in files, folders, or docs with `@` |

**Example:** When you open a Python file:
1. Rules with `globs: "**/*.py"` auto-activate
2. You invoke `@eda-workflow.md` for a specific task
3. You reference `@data-dictionary.md` for domain context

Result: The agent now behaves like a "Python data science specialist"—same agent, configured through knowledge.

### Ask vs Agent Mode

| Mode | What It Does | Use When |
|------|--------------|----------|
| **Ask** | Answers questions, suggests code | You'll apply changes manually |
| **Agent** | Takes actions (edits files, runs commands) | You want autonomous work |

### Capability Levels

| Level | Best For | Context Window |
|-------|----------|----------------|
| **Local** | Quick completions, simple tasks | Limited |
| **Cloud** | Complex reasoning, multi-file work | Full (128K+) |

### Step 1: Enable Agent Mode

1. Open chat (`Cmd+L` / `Ctrl+L`)
2. Click the dropdown next to the send button
3. Select "Agent" mode (not "Ask" mode)
4. Choose your capability level (Cloud for complex tasks)

### Step 2: Give a Multi-Step Task

Try a task that requires multiple steps:

```
Look at my project structure and suggest a good location
for a new utility module for data validation functions.
```

The agent will:
1. Explore your directory structure
2. Analyze existing patterns
3. Make a recommendation with reasoning

### Step 3: Let Agent Create Files

Ask the agent to create something:

```
Create a simple data validation utility module based on your
recommendation. Include functions for validating email format
and checking if a string is a valid date.
```

Watch as the agent:
1. Creates the file
2. Writes the code (following your rule!)
3. May suggest tests

### Quick Reference: Efficient 3-Layer Usage

```
RULES (.mdc):
  • Always-apply → Core standards for all files
  • Glob-targeted → Domain-specific (*.py, *.sql)
  • On-demand → Specialized contexts

SKILLS (.md):
  • Reference with @ when starting a workflow
  • Keep procedures reusable across projects

CONTEXT (@):
  • @file.py → Specific file
  • @folder/ → Directory contents
  • @docs → Indexed documentation
```

→ *Deep dive: [Agent Execution Model](../02-core-concepts/agent-execution-model.md)*

---

## Part 4: Context References (5 minutes)

The `@` symbol lets you pull specific context into your conversation.

### Common References

| Reference | What it does |
|-----------|--------------|
| `@file.py` | Include a specific file |
| `@folder/` | Include a folder's contents |
| `@docs` | Reference indexed documentation |
| `@codebase` | Search across the entire codebase |

### Try It

1. Open chat
2. Type: `@` and see the autocomplete options
3. Reference a file: `Explain @src/main.py`
4. Reference your rule: `Show me @.cursor/rules/code-standards.mdc`

---

## What You've Learned

1. **Basic interaction** — chat and completions
2. **Rules** — teaching Cursor your standards
3. **Agent mode** — letting Cursor take actions
4. **Context references** — pulling in specific information

---

## Next Steps

### Immediate
- Create 1-2 more rules for your most common issues
- Try agent mode on a real task in your project

### This Week
- Read [Core Concepts](../02-core-concepts/README.md) for deeper understanding
- Explore [Rules Deep Dive](../03-rules-deep-dive/README.md) for advanced rule writing

### For Data Scientists
- Continue to [Data Science Quickstart](data-science-quickstart.md) for Jupyter/pandas setup

---

## Troubleshooting

**AI not responding?**
- Check your internet connection
- Verify your Cursor subscription is active
- Try restarting Cursor

**Rules not being applied?**
- Ensure the file is in `.cursor/rules/`
- Check the file extension is `.mdc`
- Verify `alwaysApply: true` in frontmatter (or use appropriate globs)

**Agent mode not available?**
- Make sure you're using Cursor Pro
- Check that you've selected "Agent" not "Ask" mode

---

## See Also

- **Previous**: [What is Cursor?](what-is-cursor.md)
- **Next**: [Data Science Quickstart](data-science-quickstart.md)
- **Deeper**: [Rules Deep Dive](../03-rules-deep-dive/README.md)
