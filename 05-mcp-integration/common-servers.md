# Common MCP Servers

[Home](../README.md) > [MCP Integration](README.md) > Common Servers

---

## Overview

This guide covers popular MCP servers useful for data science workflows.

---

## Database Servers

### PostgreSQL

**Package:** `@modelcontextprotocol/server-postgres`

**Configuration:**
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://user:pass@host:5432/dbname"
      ]
    }
  }
}
```

**Capabilities:**
- Execute queries
- List tables and schemas
- Describe table structure
- Get sample data

**Usage:**
```
User: Show me the structure of the customers table

User: Write a query to find customers who ordered in the last 30 days

User: What's the average order value by customer segment?
```

### SQLite

**Package:** `@modelcontextprotocol/server-sqlite`

**Configuration:**
```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sqlite",
        "/path/to/database.db"
      ]
    }
  }
}
```

**Capabilities:**
- Full SQL query support
- Schema introspection
- Read-only or read-write modes

### MySQL

**Package:** `@modelcontextprotocol/server-mysql`

**Configuration:**
```json
{
  "mcpServers": {
    "mysql": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-mysql",
        "mysql://user:pass@host:3306/dbname"
      ]
    }
  }
}
```

---

## Notebook Servers

### cursor-notebook-mcp

**Package:** `cursor-notebook-mcp`

**Configuration:**
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
- Edit notebook cells
- Add/delete/split cells
- Manipulate cell outputs
- SFTP support for remote notebooks

**Usage:**
```
User: Add a markdown cell at the beginning explaining the analysis purpose

User: Split cell 5 after the data loading section

User: Clear all outputs from this notebook
```

**With SFTP (remote notebooks):**
```json
{
  "mcpServers": {
    "notebook": {
      "command": "npx",
      "args": ["-y", "cursor-notebook-mcp"],
      "env": {
        "SFTP_HOST": "jupyter.example.com",
        "SFTP_USER": "username",
        "SFTP_KEY_PATH": "~/.ssh/id_rsa"
      }
    }
  }
}
```

---

## File System Servers

### Filesystem

**Package:** `@modelcontextprotocol/server-filesystem`

**Configuration:**
```json
{
  "mcpServers": {
    "files": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/data",
        "/path/to/outputs"
      ]
    }
  }
}
```

**Capabilities:**
- Read files
- Write files (if allowed)
- List directories
- Search files

**Usage:**
```
User: List all CSV files in the data directory

User: Read the first 100 lines of data/raw/customers.csv

User: Save this analysis to outputs/report.md
```

---

## Browser Tools

### BrowserTools MCP

**Package:** Various (e.g., AgentDesk)

**Capabilities:**
- Take screenshots
- Read console logs
- Click elements
- Fill forms

**Use Cases:**
- Test web applications
- Debug frontend issues
- Automate browser tasks

---

## Documentation Servers

### Google Drive

**Configuration:** Via OAuth in Cursor settings

**Capabilities:**
- Read documents
- Search files
- Access shared drives

**Usage:**
```
User: Find the requirements document for the ML project

User: Read the data dictionary from Google Drive
```

### Notion

**Configuration:** Via API key

**Capabilities:**
- Read pages
- Search workspace
- Access databases

### Slack

**Configuration:** Via OAuth

**Capabilities:**
- Search messages
- Read channel history
- Find discussions

---

## Experiment Tracking

### Custom MLflow Server

Build a custom MCP server to access MLflow:

```python
# mlflow_mcp_server.py
from mcp import Server

server = Server()

@server.tool("list_experiments")
def list_experiments():
    """List all MLflow experiments."""
    import mlflow
    return mlflow.search_experiments()

@server.tool("get_run")
def get_run(run_id: str):
    """Get details of an MLflow run."""
    import mlflow
    return mlflow.get_run(run_id).to_dictionary()
```

**Use Cases:**
- Query past experiments
- Compare model versions
- Retrieve hyperparameters

---

## Choosing Servers

### For Data Scientists

| Need | Server |
|------|--------|
| Query databases | postgres, sqlite, mysql |
| Edit notebooks | cursor-notebook-mcp |
| Access data files | filesystem |
| Track experiments | Custom MLflow server |

### For Data Engineers

| Need | Server |
|------|--------|
| Multiple databases | postgres + mysql |
| Data pipelines | filesystem + custom |
| Documentation | Google Drive / Notion |

### For Teams

| Need | Server |
|------|--------|
| Shared databases | postgres (read-only) |
| Documentation | Notion / Google Drive |
| Communication | Slack |

---

## Server Discovery

### Finding Servers

1. **Cursor Directory:** [cursor.directory/mcp](https://cursor.directory/mcp)
2. **MCP.so:** 3000+ indexed servers
3. **Smithery:** Community catalog
4. **GitHub:** Search for "mcp server"

### Evaluating Servers

- Check maintenance status
- Review security considerations
- Test in development first
- Read documentation

---

## See Also

- **Previous**: [Setup Guide](setup-guide.md)
- **Next**: [Building Custom Servers](building-custom-servers.md)
- **DS Databases**: [Database Integration](../04-data-science-workflows/database-integration.md)
