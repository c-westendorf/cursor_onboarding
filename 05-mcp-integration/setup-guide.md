# MCP Setup Guide

[Home](../README.md) > [MCP Integration](README.md) > Setup Guide

---

## Overview

This guide covers how to install and configure MCP servers in Cursor.

---

## Installation Methods

### Method 1: One-Click (Recommended)

Cursor has curated popular MCP servers for easy installation:

1. Open Cursor Settings
2. Navigate to MCP section
3. Browse available servers
4. Click "Install" on desired server
5. Complete any OAuth/authentication

### Method 2: Manual Configuration

Edit your MCP settings JSON directly:

**Location:** Cursor Settings → MCP → Edit Configuration

```json
{
  "mcpServers": {
    "server-name": {
      "command": "command-to-run",
      "args": ["arg1", "arg2"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```

---

## Configuration Structure

### Basic Server

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "package-name"]
    }
  }
}
```

### With Arguments

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

### With Environment Variables

```json
{
  "mcpServers": {
    "api-server": {
      "command": "node",
      "args": ["./my-mcp-server.js"],
      "env": {
        "API_KEY": "${MY_API_KEY}",
        "BASE_URL": "https://api.example.com"
      }
    }
  }
}
```

### Multiple Servers

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/analytics"]
    },
    "notebook": {
      "command": "npx",
      "args": ["-y", "cursor-notebook-mcp"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/data"]
    }
  }
}
```

---

## Common Configurations

### PostgreSQL

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://user:password@localhost:5432/dbname"
      ]
    }
  }
}
```

### SQLite

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

### Filesystem Access

```json
{
  "mcpServers": {
    "files": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/allowed/directory"
      ]
    }
  }
}
```

### Jupyter Notebooks

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

---

## Environment Variables

### Setting Variables

**Option 1: In shell profile**
```bash
# ~/.bashrc or ~/.zshrc
export POSTGRES_URL="postgresql://user:pass@localhost/db"
export API_KEY="your-api-key"
```

**Option 2: In .env file (with dotenv)**
```bash
# .env
POSTGRES_URL=postgresql://user:pass@localhost/db
API_KEY=your-api-key
```

### Referencing in Config

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${POSTGRES_URL}"
      }
    }
  }
}
```

---

## Verifying Setup

### Check Server Status

1. Open Cursor Settings → MCP
2. Look for server status indicators
3. Green = connected, Red = error

### Test with Agent

```
User: List the available MCP tools

Agent: I have access to the following MCP tools:
- postgres: query, list_tables, describe_table
- notebook: edit_cell, add_cell, delete_cell
```

### Debug Issues

1. Check Cursor's MCP logs
2. Verify command exists and runs manually
3. Check environment variables are set
4. Verify network access for remote resources

---

## Troubleshooting

### Server Won't Start

**Check:**
- Command exists (`which npx`)
- Package can be installed (`npx -y package-name --help`)
- No typos in configuration

### Connection Errors

**Check:**
- Network access to resource
- Credentials are correct
- Firewall allows connection

### Permission Denied

**Check:**
- File paths are accessible
- User has necessary permissions
- Environment variables are set correctly

### Server Crashes

**Check:**
- Resource limits (memory, connections)
- Logs for error messages
- Try running server manually to see errors

---

## Best Practices

### Security

1. **Use environment variables** for credentials
2. **Use read-only access** when possible
3. **Limit file system access** to specific directories
4. **Review permissions** before approving tool use

### Performance

1. **Don't connect to slow resources** that will delay responses
2. **Use local servers** when possible
3. **Cache configurations** to avoid reconnection overhead

### Organization

1. **Name servers descriptively** (`prod-postgres`, `dev-sqlite`)
2. **Document custom servers** in team docs
3. **Version control** non-sensitive configuration

---

## See Also

- **Previous**: [MCP Overview](README.md)
- **Next**: [Common Servers](common-servers.md)
- **Custom**: [Building Custom Servers](building-custom-servers.md)
