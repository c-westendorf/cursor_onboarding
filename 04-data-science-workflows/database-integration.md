# Database Integration

[Home](../README.md) > [DS Workflows](README.md) > Database Integration

---

## Overview

Cursor can connect to databases via MCP servers (agent-accessible) or IDE extensions (manual queries). This guide covers both approaches.

---

## Approach Comparison

| Feature | MCP Server | IDE Extension |
|---------|------------|---------------|
| Agent can query | Yes | No |
| Interactive exploration | Limited | Full |
| Schema introspection | Yes | Yes |
| Query building assistance | Yes | Limited |
| Connection management | Config-based | GUI |
| Best for | Automated workflows | Manual exploration |

**Recommendation:** Use MCP for agent workflows, extensions for manual exploration. They can coexist.

---

## Option 1: MCP Database Servers

### PostgreSQL Setup

Add to your MCP configuration:

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

**With authentication:**

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://user:password@host:5432/dbname"
      ]
    }
  }
}
```

**Using environment variables (recommended):**

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres"
      ],
      "env": {
        "DATABASE_URL": "${POSTGRES_URL}"
      }
    }
  }
}
```

### SQLite Setup

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

### MySQL Setup

```json
{
  "mcpServers": {
    "mysql": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-mysql",
        "mysql://user:password@localhost:3306/dbname"
      ]
    }
  }
}
```

---

## Using MCP Database Connections

Once configured, use agent mode:

### Schema Exploration

```
User: Show me the schema of the users table

Agent: [Queries information_schema via MCP]
The users table has the following columns:
- id (int, primary key)
- email (varchar(255), unique)
- name (varchar(100))
- created_at (timestamp)
- status (enum: active, inactive, pending)
```

### Query Building

```
User: Write a query to find the top 10 customers by total order value

Agent: [Uses MCP to understand schema, then writes query]
```sql
SELECT
    u.id,
    u.name,
    u.email,
    SUM(o.total) as total_spent
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.status = 'completed'
GROUP BY u.id, u.name, u.email
ORDER BY total_spent DESC
LIMIT 10;
```

### Data Analysis

```
User: Analyze the distribution of order values in the orders table

Agent: [Runs exploratory queries via MCP]
Based on my analysis:
- Mean order value: $127.50
- Median: $85.00
- 90th percentile: $250.00
- Distribution is right-skewed with some high-value outliers
```

---

## Option 2: IDE Extensions

### Recommended Extensions

| Database | Extension |
|----------|-----------|
| PostgreSQL | PostgreSQL (by Chris Kolkman) |
| MySQL | MySQL (by Jun Han) |
| SQLite | SQLite (by alexcvzz) |
| Multi-database | Database Client (by Weijan Chen) |

### Setup

1. Install extension from Cursor marketplace
2. Configure connection in extension settings
3. Use extension's query interface

### Integration with Cursor AI

While AI can't query directly, you can:

1. **Copy schema to chat:**
   - Right-click table → "Copy CREATE statement"
   - Paste in chat for context

2. **Reference query results:**
   - Run query in extension
   - Copy results to chat for analysis

3. **Use @-references:**
   - Save query results to file
   - Reference with `@query_results.csv`

---

## Data Dictionary Approach

For projects without MCP access, maintain a data dictionary:

### Create Data Dictionary

```markdown
# docs/data-dictionary.md

## Database: analytics_db

### users
Primary table for user information.

| Column | Type | Description |
|--------|------|-------------|
| id | int | Primary key |
| email | varchar(255) | Unique email address |
| name | varchar(100) | Display name |
| created_at | timestamp | Account creation time |
| status | enum | active, inactive, pending |

### orders
Order transactions.

| Column | Type | Description |
|--------|------|-------------|
| id | int | Primary key |
| user_id | int | FK to users.id |
| total | decimal(10,2) | Order total in USD |
| status | enum | pending, completed, cancelled |
| created_at | timestamp | Order time |

### Relationships
- orders.user_id → users.id (many-to-one)
```

### Use in Chat

```
User: Using @docs/data-dictionary.md, write a query to find inactive users
      who have placed orders in the last 30 days

Agent: [Uses data dictionary context to write accurate query]
```

---

## Security Best Practices

### Credential Management

**Don't:**
```json
// BAD: Hardcoded credentials
"args": ["postgresql://admin:password123@prod-db.example.com/production"]
```

**Do:**
```json
// GOOD: Environment variables
"env": {
  "DATABASE_URL": "${POSTGRES_URL}"
}
```

### Access Control

1. **Use read-only credentials** for exploration
2. **Limit to specific schemas** when possible
3. **Avoid production databases** during development
4. **Log queries** for audit purposes

### Connection Security

```json
{
  "mcpServers": {
    "postgres": {
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://user@host/db?sslmode=require"
      ]
    }
  }
}
```

---

## Troubleshooting

### MCP Server Not Connecting

1. Check connection string format
2. Verify network access to database
3. Check credentials
4. Look at MCP server logs

### Slow Queries

1. Add appropriate indexes
2. Limit result sets
3. Use EXPLAIN to analyze
4. Consider caching frequent queries

### Permission Errors

1. Verify user has necessary grants
2. Check schema access
3. Confirm table-level permissions

---

## See Also

- **Previous**: [Jupyter Notebooks](jupyter-notebooks.md)
- **Next**: [Common Challenges](common-challenges.md)
- **MCP Details**: [MCP Integration](../05-mcp-integration/README.md)
