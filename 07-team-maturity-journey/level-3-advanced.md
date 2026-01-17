# Level 3: Advanced

[Home](../README.md) > [Team Maturity](README.md) > Level 3: Advanced

---

## Timeline: Month 2+

---

## Goals

1. Optimize workspace organization
2. Implement MCP integrations
3. Establish team patterns
4. Contribute to shared resources

---

## Learning Path

### Workspace Optimization

- [ ] Read [Product-Centric Model](../06-workspace-organization/product-centric-model.md)
- [ ] Audit and reorganize workspace structure
- [ ] Implement directory-based rule scoping
- [ ] Create comprehensive .cursorignore

### MCP Integration

- [ ] Read [MCP Integration](../05-mcp-integration/README.md)
- [ ] Set up database MCP server
- [ ] Explore notebook MCP (if using Jupyter)
- [ ] Evaluate custom MCP needs

### Team Patterns

- [ ] Document team's rule standards
- [ ] Create onboarding rules for new members
- [ ] Establish rule review process
- [ ] Set up shared rule repository

---

## Key Skills to Develop

### Workspace Architecture

```
product-workspace/
├── .cursor/rules/
│   ├── core.mdc                    # Minimal always-apply
│   ├── domains/
│   │   ├── ml.mdc                  # src/ml/**
│   │   ├── data.mdc                # src/data/**
│   │   └── api.mdc                 # src/api/**
│   ├── languages/
│   │   ├── python.mdc              # **/*.py
│   │   └── sql.mdc                 # **/*.sql
│   └── reference/                  # On-demand
│       └── detailed-patterns.mdc
├── docs/
│   ├── data-dictionary.md          # @-referenceable
│   └── architecture.md
└── [project structure]
```

### MCP Configuration

```json
{
  "mcpServers": {
    "analytics-db": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${ANALYTICS_DB_URL}"
      }
    },
    "notebook": {
      "command": "npx",
      "args": ["-y", "cursor-notebook-mcp"]
    }
  }
}
```

### Team Rule Standards

Document and enforce:
- Naming conventions
- Frontmatter requirements
- Maximum rule length
- Review process

---

## Advanced Patterns

### Agent Workflow Modes

| Mode | Use Case | Rule Application |
|------|----------|------------------|
| Exploratory | EDA, debugging | Minimal rules |
| Parallel | Compare approaches | Same rules, different contexts |
| Decision | Validate rigor | Full rules, slow down |

### Parallel Agents with Git Worktrees

```bash
# Create worktrees for parallel experiments
git worktree add ../experiment-a feature-a
git worktree add ../experiment-b feature-b

# Run agents in each worktree independently
# Compare results, pick best approach
```

### Context Strategy for Complex Tasks

```
1. Start fresh dialog for critical tasks
2. Load specific rules with @rule-name
3. Reference relevant docs with @docs/
4. Build context incrementally
5. Validate understanding before proceeding
```

---

## Milestone: Level 3 Complete

You've completed Level 3 when:

- [ ] Workspace organized by product
- [ ] MCP integrations working
- [ ] Team has documented standards
- [ ] Contributing to shared rules
- [ ] Can design rule systems for new projects

---

## Toward Level 4: Expert

Expert level involves:
- Building custom MCP servers
- Contributing to org marketplace
- Mentoring others
- Shaping organizational standards

Start by:
1. Identifying a need for custom MCP server
2. Learning [Building Custom Servers](../05-mcp-integration/building-custom-servers.md)
3. Contributing your best rules to marketplace
4. Helping others level up

---

## See Also

- **Previous**: [Level 2: Intermediate](level-2-intermediate.md)
- **MCP**: [MCP Integration](../05-mcp-integration/README.md)
- **Marketplace**: [Contributing](../08-marketplace/governance/contribution-guide.md)
