# Versioning Policy

[Home](../../README.md) > [Marketplace](../README.md) > [Governance](README.md) > Versioning

---

## Semantic Versioning

The marketplace uses semantic versioning: `MAJOR.MINOR.PATCH`

---

## Version Numbers

### MAJOR (X.0.0)

Breaking changes that require action:
- Removing a rule
- Changing rule behavior significantly
- Renaming rules
- Changing required frontmatter

**Example:** Removing deprecated rules, restructuring categories

### MINOR (0.X.0)

New features, backward compatible:
- Adding new rules
- Adding new skills/prompts
- Expanding existing rules
- Adding optional frontmatter

**Example:** Adding new ML evaluation rule

### PATCH (0.0.X)

Fixes, no behavior change:
- Fixing typos
- Clarifying examples
- Bug fixes in examples
- Documentation improvements

**Example:** Fixing syntax error in code example

---

## Individual Resource Versions

Each rule/skill/prompt has its own version:

```yaml
---
description: Model training standards
version: "1.2.0"
---
```

Update when:
- **Major:** Significant behavior change
- **Minor:** New guidance added
- **Patch:** Fixes and clarifications

---

## Changelog

Maintained in `CHANGELOG.md`:

```markdown
# Changelog

## [2.1.0] - 2024-01-15

### Added
- New rule: `ml/hyperparameter-tuning.mdc`
- New skill: `error-analysis.md`

### Changed
- Updated `ml/evaluation.mdc` with confidence interval requirements

### Fixed
- Typo in `analytics/sql-safety.mdc`

## [2.0.0] - 2024-01-01

### Breaking
- Removed deprecated `general/old-rule.mdc`
- Renamed `ml/training.mdc` to `ml/model-training.mdc`
```

---

## Migration Guides

For major versions, provide migration guide:

```markdown
# Migration Guide: v1.x to v2.0

## Breaking Changes

### Rule Renamed
- Old: `rules/ml/training.mdc`
- New: `rules/ml/model-training.mdc`

**Action:** Update any @-references in your rules

### Rule Removed
- `rules/general/deprecated-pattern.mdc`

**Action:** Use `rules/general/new-pattern.mdc` instead
```

---

## See Also

- [Contribution Guide](contribution-guide.md)
- [Quality Standards](quality-standards.md)
