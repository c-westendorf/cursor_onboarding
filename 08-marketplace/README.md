# Cursor Marketplace

[Home](../README.md) > Marketplace

---

## Overview

The marketplace is the organization's central repository of vetted, reusable Cursor artifacts: rules, skills, and prompts.

---

## Repository Location

The marketplace lives in a **separate repository**:

```
cursor-marketplace/
├── rules/
│   ├── ml/
│   ├── analytics/
│   └── data-eng/
├── skills/
├── prompts/
└── templates/
```

This documentation explains how to use and contribute to the marketplace.

---

## Browse Resources

| Category | Description | View |
|----------|-------------|------|
| Rules by Domain | ML, Analytics, Data-Eng rules | [Catalog](catalog/rules-by-domain.md) |
| Shared Skills | Cross-cutting procedures | [Catalog](catalog/shared-skills.md) |
| Prompt Templates | Reusable prompts | [Catalog](catalog/prompt-templates.md) |

---

## Quick Start

### Using Marketplace Resources

**Option 1: Git Submodule (Recommended)**
```bash
# Add marketplace to your project
git submodule add https://github.com/org/cursor-marketplace .cursor/shared

# Your rules can reference shared rules
# Or copy specific rules to .cursor/rules/
```

**Option 2: Manual Copy**
1. Browse the [catalog](catalog/README.md)
2. Copy relevant rules to your `.cursor/rules/`
3. Customize as needed

See [Distribution Guide](distribution/README.md) for details.

### Contributing to Marketplace

1. Read [Contribution Guide](governance/contribution-guide.md)
2. Follow [Quality Standards](governance/quality-standards.md)
3. Submit PR with new rule/skill/prompt
4. Pass review (2-person approval)

---

## Documents in This Section

### Governance
| Document | Description |
|----------|-------------|
| [Governance Overview](governance/README.md) | How the marketplace is managed |
| [Contribution Guide](governance/contribution-guide.md) | How to submit resources |
| [Review Process](governance/review-process.md) | 2-person approval workflow |
| [Versioning](governance/versioning.md) | Semantic versioning policy |
| [Quality Standards](governance/quality-standards.md) | CI/CD validation requirements |

### Catalog
| Document | Description |
|----------|-------------|
| [Catalog Overview](catalog/README.md) | Browse all resources |
| [Rules by Domain](catalog/rules-by-domain.md) | ML, Analytics, Data-Eng |
| [Shared Skills](catalog/shared-skills.md) | Cross-cutting procedures |
| [Prompt Templates](catalog/prompt-templates.md) | Reusable prompts |

### Distribution
| Document | Description |
|----------|-------------|
| [Distribution Overview](distribution/README.md) | How to consume resources |
| [Git Submodules](distribution/git-submodules.md) | Recommended approach |

---

## Why a Marketplace?

### Without Marketplace
- Teams duplicate effort creating similar rules
- Quality varies across teams
- Best practices stay siloed
- Onboarding inconsistent

### With Marketplace
- Vetted, high-quality resources
- Consistent standards across org
- Reduced duplication
- Faster onboarding

---

## See Also

- **Previous Section**: [Team Maturity](../07-team-maturity-journey/README.md)
- **Next Section**: [Anti-Patterns](../09-anti-patterns/README.md)
- **Contributing**: [Contribution Guide](governance/contribution-guide.md)
