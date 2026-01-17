# Agent Execution Model

[Home](../README.md) > [Core Concepts](README.md) > Agent Execution Model

---

## Overview

Understanding Cursor's agent architecture is essential for data scientists. The key insight: **Cursor runs ONE agent per session, and "specialization" happens through knowledge configuration—not by spawning different agents.**

---

## The Single-Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURSOR EXECUTION MODEL                        │
│                                                                  │
│  WRONG MENTAL MODEL:                                             │
│  "I spawn specialized sub-agents for different tasks"           │
│                                                                  │
│  CORRECT MENTAL MODEL:                                           │
│  "I configure ONE agent with domain-specific knowledge"         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### What This Means

- **One agent per chat session** — Each conversation is a single AI assistant instance
- **No hierarchical sub-agents** — There is no "parent agent" delegating to "child agents"
- **Multi-step work = same agent iterating** — When Cursor performs complex tasks, it's one agent executing a plan, not multiple agents coordinating
- **"Specialization" = different knowledge loaded** — The agent behaves differently based on which rules, skills, and context are active

---

## How Specialization Works: The 3-Layer System

The agent becomes "specialized" through the knowledge layers you configure:

```
┌─────────────────────────────────────────────────────────────────┐
│                   SPECIALIZATION MECHANISM                       │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  LAYER 1: RULES (.mdc) — Auto-load based on context      │    │
│  │                                                          │    │
│  │  How it works:                                           │    │
│  │  • globs: "**/*.py" → Python rules activate             │    │
│  │  • globs: "**/*.sql" → SQL rules activate               │    │
│  │  • alwaysApply: true → Always active                    │    │
│  │                                                          │    │
│  │  Result: Agent "knows" domain constraints automatically  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  LAYER 2: SKILLS (.md) — User invokes for workflows      │    │
│  │                                                          │    │
│  │  How it works:                                           │    │
│  │  • @eda-workflow.md → EDA specialist behavior           │    │
│  │  • @model-eval.md → Evaluation specialist behavior      │    │
│  │  • @feature-engineering.md → Feature work guidance      │    │
│  │                                                          │    │
│  │  Result: Agent follows structured procedures             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  LAYER 3: CONTEXT (@) — User provides task-specific info │    │
│  │                                                          │    │
│  │  How it works:                                           │    │
│  │  • @data-dictionary.md → Domain knowledge               │    │
│  │  • @src/models/ → Relevant code context                 │    │
│  │  • @requirements.txt → Project dependencies             │    │
│  │                                                          │    │
│  │  Result: Agent has domain-specific information           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↓                                   │
│                                                                  │
│              ONE AGENT operates with all layers                  │
│              (Same agent, different configuration)               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Example: "Specialized" ML Agent

When you open a Python ML file, Cursor doesn't spawn an "ML agent." Instead:

1. **Rules auto-load:** `ml/model-training.mdc`, `ml/data-leakage-prevention.mdc` activate via glob patterns
2. **You invoke a skill:** `@model-evaluation-protocol.md` for structured workflow
3. **You provide context:** `@data-dictionary.md` for domain knowledge

**Result:** The same agent now behaves like an "ML specialist" — but it's configuration, not a different agent.

---

## Agent Mode: Tool-Driven Execution

"Agent Mode" is an **execution capability**, not a different agent:

### Ask Mode vs Agent Mode

| Aspect | Ask Mode | Agent Mode |
|--------|----------|------------|
| **What it is** | Conversation only | Conversation + actions |
| **File operations** | Suggests changes | Makes changes directly |
| **Terminal** | Suggests commands | Executes commands |
| **Iteration** | You apply suggestions manually | Agent iterates autonomously |
| **Same agent?** | Yes | Yes — same agent, more capabilities |

### How Agent Mode Works

```
┌─────────────────────────────────────────────────────────────────┐
│                       AGENT MODE EXECUTION                       │
│                                                                  │
│   User: "Add input validation to the API endpoint"              │
│                              │                                   │
│                              ▼                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  SAME AGENT executes a plan:                             │   │
│   │                                                          │   │
│   │  1. Read existing endpoint code                          │   │
│   │  2. Analyze validation requirements                      │   │
│   │  3. Write validation functions                           │   │
│   │  4. Modify endpoint to use validators                    │   │
│   │  5. Add tests (if configured in rules)                   │   │
│   │  6. Run tests to verify                                  │   │
│   │                                                          │   │
│   │  All steps: ONE agent, iterating through the plan        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   NOT: Multiple agents dividing work                            │
│   BUT: One agent executing sequential steps                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Capability Levels: Local vs Cloud

The "local vs cloud" distinction is about **capability levels**, not different agents:

| Aspect | Local Mode | Cloud Mode |
|--------|------------|------------|
| **Same agent architecture?** | Yes | Yes |
| **Model quality** | Smaller, faster models | Largest, most capable (Claude, GPT-4) |
| **Context window** | Limited | Full (128K+ tokens) |
| **Agent Mode capabilities** | Basic file ops | Full autonomous execution |
| **Complex reasoning** | Limited | Full capability |
| **Best for** | Quick completions, simple tasks | Multi-step implementations |

### Choosing Based on Task Complexity

```
Task Complexity          →  Recommended Mode
─────────────────────────────────────────────
Simple completion        →  Local (fast, sufficient)
Quick Q&A about code     →  Local (basic capability enough)
Multi-file refactor      →  Cloud (needs large context)
Complex debugging        →  Cloud (needs reasoning)
Full feature build       →  Cloud + Agent Mode
```

**Note:** Privacy/cost are secondary considerations. Primary consideration is: **Does the task need the full model capabilities?**

---

## Parallel Exploration: Manual "Multi-Agent" Patterns

If you need to explore multiple approaches simultaneously, you manage this yourself:

### Git Worktree Pattern

```bash
# Create independent working directories
git worktree add ../exp-xgboost feature-xgboost
git worktree add ../exp-neural feature-neural
git worktree add ../exp-ensemble feature-ensemble

# Open each in a separate Cursor window
# Each runs an INDEPENDENT agent session with SAME rules
# You compare results and pick the best approach
```

### Why This Isn't "Sub-Agents"

- Each worktree is a **separate, independent agent session**
- They don't communicate or share state
- **You** coordinate and compare results
- This is user-managed parallelism, not agent orchestration

---

## Data Science Examples

### Example 1: EDA Workflow

**What happens:**
```
1. You open customer_data.py
   → Rules auto-load: data-science-core.mdc, pandas-operations.mdc

2. You reference: @eda-workflow.md
   → Skill loads: Structured EDA procedure

3. You provide: @data-dictionary.md
   → Context loads: Column definitions, business rules

4. ONE agent executes EDA following all three layers
   → Agent is "specialized" for EDA through configuration
```

**Not what happens:**
- ❌ "EDA Agent" spawned
- ❌ "Data Quality Sub-Agent" created
- ❌ Multiple agents coordinating

### Example 2: Model Training

**What happens:**
```
1. You open train_model.py
   → Rules auto-load: model-training.mdc, reproducibility.mdc, data-leakage-prevention.mdc

2. You invoke Agent Mode and say:
   "Train a classifier using the prepared features"

3. ONE agent executes:
   - Reads data
   - Sets seeds (from reproducibility rule)
   - Splits data properly (from leakage prevention rule)
   - Trains model
   - Logs hyperparameters
   - Evaluates results

   All guided by active rules — ONE agent, multiple steps
```

### Example 3: Comparing Approaches

**If you want to compare XGBoost vs Neural Network:**

```
Option A: Sequential (same agent, new chat)
──────────────────────────────────────────
1. Chat 1: "Build XGBoost classifier"
   → Agent completes, you save results
2. Chat 2: "Build neural network classifier"
   → New agent session, same rules
3. You compare results manually

Option B: Parallel (multiple windows)
──────────────────────────────────────────
1. Window 1: XGBoost approach
2. Window 2: Neural network approach
3. Each is an independent agent session
4. You compare and merge best results
```

**Neither option involves sub-agents** — just independent sessions you coordinate.

---

## Key Takeaways for Data Scientists

### Mental Model Shift

| Old Thinking | New Thinking |
|-------------|--------------|
| "I need an ML agent and a data quality agent" | "I need ML rules and data quality rules configured" |
| "The agent should spawn helpers for subtasks" | "The agent follows rules and skills for all subtasks" |
| "Different agents for different specialties" | "Same agent, different knowledge layers activated" |
| "Local agent is a different agent than cloud" | "Local/cloud are capability levels of same architecture" |

### Practical Implications

1. **Invest in rules** — They shape ALL agent interactions in your workspace
2. **Create domain skills** — Structured workflows the single agent can follow
3. **Use context references** — `@` syntax loads domain knowledge into the agent
4. **Parallel work = multiple windows** — You manage coordination, not the agent

### Configuration Checklist

To make Cursor's single agent behave like a "domain specialist":

- [ ] Domain-specific rules in `.cursor/rules/` with appropriate globs
- [ ] Workflow skills in `docs/skills/` for common procedures
- [ ] Domain context (data dictionaries, specs) referenceable via `@`
- [ ] Agent Mode enabled for autonomous execution needs

---

## See Also

- **Previous**: [Artifact Types](artifact-types.md)
- **Next**: [Decision Flow](decision-flow/README.md)
- **Knowledge Layers**: [3-Layer Stack](3-layer-stack.md)
- **Practical**: [First 30 Minutes](../01-getting-started/first-30-minutes.md)
