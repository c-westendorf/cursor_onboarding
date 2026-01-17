# Distribution Guide

[Home](../../README.md) > [Marketplace](../README.md) > Distribution

---

## Overview

How to use marketplace resources in your projects.

---

## Methods

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| [Git Submodule](git-submodules.md) | Teams, governance | Version control, updates | More setup |
| Manual Copy | Quick use, customization | Simple, flexible | No updates |

---

## Quick Start

### Git Submodule (Recommended)

```bash
# Add marketplace as submodule
git submodule add https://github.com/org/cursor-marketplace .cursor/shared

# Update to latest
git submodule update --remote
```

### Manual Copy

```bash
# Copy specific rules
cp cursor-marketplace/rules/ml/model-training.mdc .cursor/rules/
```

---

## See Also

- [Git Submodules](git-submodules.md)
- [Catalog](../catalog/README.md)
