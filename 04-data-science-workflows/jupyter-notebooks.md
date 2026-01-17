# Jupyter Notebooks in Cursor

[Home](../README.md) > [DS Workflows](README.md) > Jupyter Notebooks

---

## Overview

Cursor supports `.ipynb` files natively, but with some important limitations. This guide covers what works, what doesn't, and workarounds.

---

## Native Support

### What Works Well

| Feature | Support |
|---------|---------|
| Opening/viewing notebooks | Full support |
| AI code completion in cells | Full support |
| Chat about notebook content | Full support |
| Running cells | Full support |
| Creating new notebooks | Full support |

### How to Use

1. **Open notebook**: `File → Open` any `.ipynb` file
2. **Code completion**: Start typing in a code cell
3. **Chat context**: Press `Cmd+L` / `Ctrl+L` and reference `@notebook.ipynb`
4. **Run cells**: Use standard Jupyter shortcuts (`Shift+Enter`)

---

## Limitations

### Agent Mode Cell Editing

**Problem:** Agent mode can struggle with precise cell-level operations:
- Adding code to specific cells
- Splitting cells
- Reordering cells
- Editing outputs

**Why:** Notebook format is JSON-based, and cell boundaries aren't always clear to the agent.

### Workarounds

#### Option 1: Manual Cell Operations

Ask agent to write code, then manually place it:

```
User: Write code to visualize the distribution of the 'age' column

Agent: Here's the code:
```python
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.hist(df['age'], bins=30, edgecolor='black')
plt.xlabel('Age')
plt.ylabel('Count')
plt.title('Age Distribution')
plt.show()
```

You: [Copy code to desired cell manually]
```

#### Option 2: cursor-notebook-mcp

Install the notebook MCP server for programmatic cell editing:

```json
{
  "mcpServers": {
    "notebook": {
      "command": "npx",
      "args": ["-y", "cursor-notebook-mcp"]
    }
  }
}
```

**Capabilities:**
- Cell editing, splitting, duplicating
- Output manipulation
- SFTP support for remote notebooks

**Usage after setup:**
```
User: Add a markdown cell above cell 3 explaining the preprocessing steps
[Agent uses MCP tools to modify notebook structure]
```

#### Option 3: Convert for Major Refactoring

For significant refactoring, convert to `.py`:

```bash
# Convert notebook to script
jupyter nbconvert --to script notebook.ipynb

# Edit in Cursor (agent mode works better with .py)
# [Make changes]

# Convert back if needed (or keep as .py)
```

#### Option 4: Cell Magic with Comments

Guide the agent with clear cell markers:

```python
# CELL: Data Loading
import pandas as pd
df = pd.read_csv('data.csv')

# CELL: Preprocessing
df = df.dropna()

# CELL: Visualization
import matplotlib.pyplot as plt
plt.hist(df['value'])
```

---

## Best Practices

### For Notebooks

1. **Use clear cell purposes**: One concept per cell
2. **Add markdown headers**: Help AI understand structure
3. **Keep cells focused**: Don't mix data loading, processing, and viz

### For Chat

1. **Reference specific sections**: "In the preprocessing cell..."
2. **Describe cell contents**: "The cell that loads the data..."
3. **Use @-references**: `@notebook.ipynb` for context

### For Agent Mode

1. **Be explicit about placement**: "Add this code after the imports"
2. **Describe relative position**: "Before the visualization section"
3. **Consider manual placement**: For precise control

---

## Notebook-Specific Rules

Create a rule for notebook work:

```markdown
---
description: Jupyter notebook best practices
globs: "**/*.ipynb"
alwaysApply: false
---

# Notebook Standards

## Cell Organization
- One clear purpose per cell
- Markdown cells to explain sections
- Keep related code together

## Documentation
- Start with overview markdown cell
- Document non-obvious transformations
- Include cell output interpretation

## Reproducibility
- Set random seeds at notebook start
- Clear outputs before committing
- Document data versions
```

---

## Remote Notebooks

### SSH Connection

Connect to remote Jupyter servers:

1. Configure Remote-SSH in Cursor
2. Connect to your server
3. Open notebooks normally

### SFTP via MCP

With cursor-notebook-mcp:

```json
{
  "mcpServers": {
    "notebook": {
      "command": "npx",
      "args": ["-y", "cursor-notebook-mcp"],
      "env": {
        "SFTP_HOST": "your-server.com",
        "SFTP_USER": "username"
      }
    }
  }
}
```

---

## Troubleshooting

### Notebook won't open
- Check if file is valid JSON
- Try `jupyter nbconvert --to notebook notebook.ipynb`

### Code completion not working
- Ensure notebook kernel is running
- Check Python environment is selected

### Agent making wrong changes
- Be more specific in instructions
- Consider manual cell placement
- Use cursor-notebook-mcp for precise control

---

## See Also

- **Previous**: [DS Workflows](README.md)
- **Next**: [Database Integration](database-integration.md)
- **MCP Setup**: [MCP Integration](../05-mcp-integration/README.md)
