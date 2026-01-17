# Git Submodules Distribution

[Home](../../README.md) > [Marketplace](../README.md) > [Distribution](README.md) > Git Submodules

---

## Overview

Using git submodules is the recommended way to consume marketplace resources. It provides version control and easy updates.

---

## Setup

### Add Marketplace as Submodule

```bash
# Navigate to your project
cd your-project

# Add the marketplace
git submodule add https://github.com/org/cursor-marketplace .cursor/shared

# Commit the addition
git add .gitmodules .cursor/shared
git commit -m "Add cursor-marketplace as submodule"
```

### Structure After Setup

```
your-project/
├── .cursor/
│   ├── rules/           # Your project-specific rules
│   │   └── local.mdc
│   └── shared/          # Marketplace (submodule)
│       ├── rules/
│       │   ├── ml/
│       │   ├── analytics/
│       │   └── data-eng/
│       ├── skills/
│       └── prompts/
├── src/
└── ...
```

---

## Using Shared Rules

### Option 1: Reference Directly

Reference marketplace rules with `@`:
```
Using the patterns in @.cursor/shared/rules/ml/model-training.mdc,
write a training pipeline for this classifier.
```

### Option 2: Symlink to Rules Directory

```bash
# Symlink specific rules you want active
ln -s ../shared/rules/ml/model-training.mdc .cursor/rules/
ln -s ../shared/rules/analytics/sql-safety.mdc .cursor/rules/
```

### Option 3: Copy and Customize

```bash
# Copy for customization
cp .cursor/shared/rules/ml/model-training.mdc .cursor/rules/

# Edit to add project-specific guidance
vi .cursor/rules/model-training.mdc
```

---

## Updating

### Update to Latest Version

```bash
# Update submodule to latest
git submodule update --remote

# Check what changed
cd .cursor/shared
git log --oneline -5

# Commit the update
cd ../..
git add .cursor/shared
git commit -m "Update cursor-marketplace to latest"
```

### Pin to Specific Version

```bash
# Check out specific tag/version
cd .cursor/shared
git checkout v2.0.0
cd ../..

# Commit the pinned version
git add .cursor/shared
git commit -m "Pin cursor-marketplace to v2.0.0"
```

---

## Team Setup

### Cloning Projects with Submodule

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/org/your-project.git

# Or if already cloned
git submodule init
git submodule update
```

### CI/CD Setup

```yaml
# GitHub Actions example
jobs:
  build:
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: recursive
```

---

## Troubleshooting

### Submodule Not Initialized

```bash
git submodule init
git submodule update
```

### Submodule Shows Dirty

```bash
# Check for untracked changes in submodule
cd .cursor/shared
git status

# Reset if needed
git checkout .
```

### Version Mismatch

```bash
# Sync submodule to committed version
git submodule update --init
```

---

## See Also

- [Distribution Overview](README.md)
- [Catalog](../catalog/README.md)
