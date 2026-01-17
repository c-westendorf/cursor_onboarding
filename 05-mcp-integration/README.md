# MCP Integration

[Home](../README.md) > MCP Integration

---

## Overview

MCP (Model Context Protocol) allows Cursor's AI agent to interact with external tools and data sources. Think of it as a plugin system that extends what the agent can do.

---

## What is MCP?

```
┌─────────────────────────────────────────────┐
│                Cursor IDE                    │
│  ┌─────────────────────────────────────┐    │
│  │           MCP Client                 │    │
│  │    (Built into Cursor)               │    │
│  └──────────────┬──────────────────────┘    │
└─────────────────┼───────────────────────────┘
                  │
         ┌────────┼────────┐
         │        │        │
         ▼        ▼        ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │Postgres│ │Notebook│ │ Custom │
    │ Server │ │ Server │ │ Server │
    └────────┘ └────────┘ └────────┘
```

**Key Components:**
- **MCP Client**: Built into Cursor, manages connections
- **MCP Servers**: Lightweight programs exposing specific capabilities
- **Transports**: stdio (local), SSE (remote), HTTP

---

## Documents in This Section

| Document | Description |
|----------|-------------|
| [Setup Guide](setup-guide.md) | Installation and configuration |
| [Common Servers](common-servers.md) | Database, notebook, browser tools |
| [Building Custom Servers](building-custom-servers.md) | Create your own MCP servers |

---

## Quick Start

### 1. Find MCP Settings

In Cursor: `Settings → MCP` or edit the MCP configuration JSON directly.

### 2. Add a Server

Example PostgreSQL configuration:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://localhost/mydb"
      ]
    }
  }
}
```

### 3. Use in Agent Mode

Once configured, the agent can use the server's tools:

```
User: Show me the schema of the users table

Agent: [Uses MCP postgres tools to query information_schema]
```

---

## Why Use MCP?

| Without MCP | With MCP |
|-------------|----------|
| Manual query, copy results to chat | Agent queries directly |
| Describe schema in prompts | Agent reads schema from database |
| Limited to local files | Access remote resources |
| Static context | Dynamic, real-time data |

---

## Common Use Cases

### Databases
- Query data directly
- Introspect schemas
- Run analyses

### Notebooks
- Edit cells programmatically
- Manage notebook structure
- Access remote notebooks

### Documentation
- Pull from Google Drive
- Access Notion pages
- Search Slack history

### Custom
- Internal APIs
- Data catalogs
- MLflow/W&B experiments

---

## Security Considerations

### Credential Management
```json
// BAD: Hardcoded credentials
"args": ["postgresql://admin:password123@prod.example.com/db"]

// GOOD: Environment variables
"env": {
  "DATABASE_URL": "${POSTGRES_URL}"
}
```

### Permission Control
- MCP servers prompt before executing tools
- Configure allowed/blocked domains
- Use read-only credentials when possible

---

## See Also

- **Previous Section**: [DS Workflows](../04-data-science-workflows/README.md)
- **Next Section**: [Workspace Organization](../06-workspace-organization/README.md)
- **DS Database Setup**: [Database Integration](../04-data-science-workflows/database-integration.md)
