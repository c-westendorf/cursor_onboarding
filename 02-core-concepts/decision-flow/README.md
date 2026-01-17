# Knowledge Codification Decision Flow

[Home](../../README.md) > [Core Concepts](../README.md) > Decision Flow

---

## Overview

This decision flow helps you determine **where knowledge belongs** when working with Cursor. It answers:
- **WHAT** kind of knowledge is this?
- **HOW** should it be encoded?
- **WHERE** should it live?

---

## The Decision Flowchart

```
┌─────────────────────────────────────────┐
│  Is this knowledge stable               │
│  for 6-12 months?                       │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
      NO              YES
       │               │
       ▼               ▼
┌─────────────┐  ┌─────────────────────────┐
│  Ephemeral  │  │  Should violations      │
│  Knowledge  │  │  block prod or CI?      │
└──────┬──────┘  └───────────┬─────────────┘
       │                     │
       │             ┌───────┴───────┐
       │             │               │
       │            YES             NO
       │             │               │
       │             ▼               ▼
       │    ┌────────────────┐ ┌─────────────────┐
       │    │ Executable     │ │ Does this apply │
       │    │ Enforcement    │ │ broadly?        │
       │    │ (Code / CI)    │ └────────┬────────┘
       │    └────────────────┘          │
       │                        ┌───────┴───────┐
       │                        │               │
       │                       YES             NO
       │                        │               │
       │                        ▼               ▼
       │               ┌────────────────┐ ┌─────────────────┐
       │               │ Cursor Rule    │ │ Is this a       │
       │               │ (.mdc file)    │ │ repeatable      │
       │               └────────────────┘ │ workflow?       │
       │                                  └────────┬────────┘
       │                                           │
       │                                   ┌───────┴───────┐
       │                                   │               │
       │                                  YES             NO
       │                                   │               │
       │                                   ▼               │
       │                          ┌────────────────┐       │
       │                          │ Prompt Template│       │
       │                          │ or Skill       │       │
       │                          └────────────────┘       │
       │                                                   │
       └───────────────────────────────────────────────────┘
                                   │
                                   ▼
                          ┌────────────────┐
                          │ Human Judgment │
                          │ or Conversation│
                          └────────────────┘
```

---

## Decision Summary Table

| Knowledge Type | Where It Lives | Purpose |
|----------------|----------------|---------|
| Stable + Should block CI | Code / CI | Prevent violations |
| Stable + Applies broadly | Cursor Rule (.mdc) | Shape behavior |
| Stable + Narrow scope | On-demand Rule | Context-specific guidance |
| Ephemeral + Repeatable | Prompts / Skills | Guide reasoning |
| Ephemeral + Situational | Human judgment | Preserve flexibility |

---

## The Four Decision Boxes

Each decision point has detailed criteria and examples:

### [Box 1: Stability Check](stability-check.md)
**Question:** Is this knowledge stable for 6-12 months?
- Tests whether knowledge is **durable** or **ephemeral**
- Determines if codification is worth the investment

### [Box 2: Enforcement Check](enforcement-check.md)
**Question:** Should violations block production or CI?
- Tests whether the system should **fail loudly**
- Determines if code/CI enforcement is needed

### [Box 3: Scope Check](scope-check.md)
**Question:** Does this apply broadly across files/workflows?
- Tests whether Cursor should **auto-apply** guidance
- Determines rule activation strategy

### [Box 4: Repeatability Check](repeatability-check.md)
**Question:** Is this a repeatable reasoning pattern?
- Tests whether guidance helps humans **think**
- Determines if a skill or prompt template is useful

---

## How to Use This Flow

### Step 1: Start at Stability
Ask: "Would I teach this to every new hire? Will it be true in a year?"

### Step 2: Follow the Path
Answer each question honestly. Don't over-engineer.

### Step 3: Place the Knowledge
Put it in the artifact type indicated by the flow.

### Step 4: Review Periodically
Knowledge changes. Re-evaluate quarterly.

---

## Walkthrough Example: "Data Leakage Prevention"

Let's trace this knowledge through the flow:

**Box 1: Is it stable for 6-12 months?**
→ YES. Preventing data leakage is a fundamental principle that won't change.

**Box 2: Should violations block CI?**
→ YES (for critical checks). Data leakage can invalidate entire analyses.

**Result for critical checks:** → **Code/CI** (write tests for leakage)

BUT there's also softer guidance...

**Box 2 (again): Should ALL guidance block CI?**
→ NO. Some leakage prevention is about awareness, not hard failures.

**Box 3: Does it apply broadly?**
→ YES. Any ML code could have leakage risks.

**Result for guidance:** → **Cursor Rule (.mdc)**

**Final placement:**
- Hard checks (test/train contamination) → CI tests
- Soft guidance (awareness, patterns) → Rule

---

## Common Patterns

### Pattern: "We keep making this mistake"
→ If stable and broad: **Rule**
→ If critical: Also add **CI check**

### Pattern: "This is how we do X"
→ If procedural: **Skill**
→ If task-starting: **Prompt template**

### Pattern: "It depends on context"
→ **Human judgment** (don't over-codify)

### Pattern: "Everyone needs to know this"
→ If invariant: **Always-apply Rule**
→ If procedure: **Onboarding Skill**

---

## See Also

- **Deep Dives:**
  - [Stability Check](stability-check.md)
  - [Enforcement Check](enforcement-check.md)
  - [Scope Check](scope-check.md)
  - [Repeatability Check](repeatability-check.md)

- **Related:**
  - [Artifact Types](../artifact-types.md)
  - [3-Layer Stack](../3-layer-stack.md)
  - [Writing Effective Rules](../../03-rules-deep-dive/writing-effective-rules.md)
