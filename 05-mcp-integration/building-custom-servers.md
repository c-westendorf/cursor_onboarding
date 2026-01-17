# Building Custom MCP Servers

[Home](../README.md) > [MCP Integration](README.md) > Building Custom Servers

---

## Overview

When existing MCP servers don't meet your needs, you can build custom servers in Python or TypeScript.

---

## When to Build Custom

- Internal APIs that need agent access
- Custom data catalogs
- Proprietary tools or services
- Specialized workflows

---

## Python Server

### Basic Structure

```python
# my_mcp_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import json

# Create server instance
server = Server("my-custom-server")

# Define a tool
@server.tool("get_data")
async def get_data(query: str) -> str:
    """
    Fetch data based on query.

    Args:
        query: The search query
    """
    # Your implementation
    results = internal_api.search(query)
    return json.dumps(results)

@server.tool("process_data")
async def process_data(data_id: str, operation: str) -> str:
    """
    Process data with specified operation.

    Args:
        data_id: ID of the data to process
        operation: Operation to perform (clean, transform, validate)
    """
    # Your implementation
    result = internal_api.process(data_id, operation)
    return json.dumps(result)

# Run the server
if __name__ == "__main__":
    import asyncio
    asyncio.run(server.run_stdio())
```

### Installation

```bash
pip install mcp
```

### Configuration

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/path/to/my_mcp_server.py"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

---

## TypeScript Server

### Basic Structure

```typescript
// my-mcp-server.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server(
  {
    name: "my-custom-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define tools
server.setRequestHandler("tools/list", async () => {
  return {
    tools: [
      {
        name: "get_data",
        description: "Fetch data based on query",
        inputSchema: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "The search query",
            },
          },
          required: ["query"],
        },
      },
    ],
  };
});

server.setRequestHandler("tools/call", async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "get_data") {
    const result = await fetchData(args.query);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }],
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

// Run server
const transport = new StdioServerTransport();
server.connect(transport);
```

### Installation

```bash
npm install @modelcontextprotocol/sdk
```

### Configuration

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["/path/to/my-mcp-server.js"]
    }
  }
}
```

---

## Example: MLflow Integration

```python
# mlflow_mcp_server.py
from mcp.server import Server
import mlflow
import json

server = Server("mlflow-server")

@server.tool("list_experiments")
async def list_experiments() -> str:
    """List all MLflow experiments."""
    experiments = mlflow.search_experiments()
    return json.dumps([
        {"id": e.experiment_id, "name": e.name}
        for e in experiments
    ])

@server.tool("get_run_metrics")
async def get_run_metrics(run_id: str) -> str:
    """
    Get metrics for an MLflow run.

    Args:
        run_id: The run ID to fetch metrics for
    """
    run = mlflow.get_run(run_id)
    return json.dumps({
        "metrics": run.data.metrics,
        "params": run.data.params,
        "tags": run.data.tags,
    })

@server.tool("compare_runs")
async def compare_runs(run_ids: list[str], metric: str) -> str:
    """
    Compare a metric across multiple runs.

    Args:
        run_ids: List of run IDs to compare
        metric: Name of the metric to compare
    """
    results = []
    for run_id in run_ids:
        run = mlflow.get_run(run_id)
        results.append({
            "run_id": run_id,
            metric: run.data.metrics.get(metric)
        })
    return json.dumps(results)

if __name__ == "__main__":
    import asyncio
    asyncio.run(server.run_stdio())
```

---

## Example: Data Catalog

```python
# data_catalog_mcp_server.py
from mcp.server import Server
import json

server = Server("data-catalog")

# In-memory catalog (replace with actual database)
CATALOG = {
    "customers": {
        "description": "Customer master data",
        "location": "s3://data/customers/",
        "schema": ["id", "name", "email", "created_at"],
        "owner": "data-team",
    },
    "orders": {
        "description": "Order transactions",
        "location": "s3://data/orders/",
        "schema": ["id", "customer_id", "total", "status"],
        "owner": "data-team",
    },
}

@server.tool("search_datasets")
async def search_datasets(query: str) -> str:
    """
    Search for datasets in the catalog.

    Args:
        query: Search term
    """
    results = [
        {"name": name, **info}
        for name, info in CATALOG.items()
        if query.lower() in name.lower() or query.lower() in info["description"].lower()
    ]
    return json.dumps(results)

@server.tool("get_dataset_schema")
async def get_dataset_schema(name: str) -> str:
    """
    Get schema for a dataset.

    Args:
        name: Dataset name
    """
    if name not in CATALOG:
        return json.dumps({"error": f"Dataset {name} not found"})
    return json.dumps(CATALOG[name])

@server.tool("list_datasets")
async def list_datasets() -> str:
    """List all available datasets."""
    return json.dumps(list(CATALOG.keys()))

if __name__ == "__main__":
    import asyncio
    asyncio.run(server.run_stdio())
```

---

## Best Practices

### Error Handling

```python
@server.tool("risky_operation")
async def risky_operation(param: str) -> str:
    try:
        result = do_something_risky(param)
        return json.dumps({"success": True, "result": result})
    except ValueError as e:
        return json.dumps({"success": False, "error": str(e)})
    except Exception as e:
        return json.dumps({"success": False, "error": "Internal error"})
```

### Input Validation

```python
@server.tool("validated_operation")
async def validated_operation(count: int, mode: str) -> str:
    # Validate inputs
    if count < 1 or count > 100:
        return json.dumps({"error": "count must be between 1 and 100"})

    if mode not in ["fast", "accurate"]:
        return json.dumps({"error": "mode must be 'fast' or 'accurate'"})

    # Proceed with operation
    result = do_operation(count, mode)
    return json.dumps(result)
```

### Documentation

```python
@server.tool("well_documented")
async def well_documented(
    required_param: str,
    optional_param: int = 10
) -> str:
    """
    Clear description of what this tool does.

    This tool performs X operation on Y data and returns Z result.
    Use this when you need to accomplish [specific goal].

    Args:
        required_param: Description of what this parameter is for.
            Include valid values if constrained.
        optional_param: Description of optional parameter.
            Defaults to 10. Valid range: 1-100.

    Returns:
        JSON object with fields:
        - result: The main output
        - metadata: Additional information
    """
    pass
```

### Security

```python
import os

# Get credentials from environment
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable required")

@server.tool("authenticated_operation")
async def authenticated_operation(query: str) -> str:
    # Use API_KEY for authentication
    headers = {"Authorization": f"Bearer {API_KEY}"}
    # Make authenticated request
    pass
```

---

## Testing

### Manual Testing

```bash
# Run server directly
python my_mcp_server.py

# In another terminal, send test requests
echo '{"method": "tools/list"}' | python my_mcp_server.py
```

### Unit Testing

```python
# test_mcp_server.py
import pytest
from my_mcp_server import get_data, process_data

@pytest.mark.asyncio
async def test_get_data():
    result = await get_data("test query")
    data = json.loads(result)
    assert "results" in data

@pytest.mark.asyncio
async def test_process_data_invalid():
    result = await process_data("invalid-id", "clean")
    data = json.loads(result)
    assert data.get("error") is not None
```

---

## Deployment

### Local Development

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/path/to/my_mcp_server.py"]
    }
  }
}
```

### Published Package

```bash
# Publish to PyPI
pip install build twine
python -m build
twine upload dist/*
```

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "my-published-mcp-server"]
    }
  }
}
```

---

## See Also

- **Previous**: [Common Servers](common-servers.md)
- **MCP Documentation**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Python SDK**: [github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
