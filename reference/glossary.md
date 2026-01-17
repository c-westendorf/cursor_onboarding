# Glossary

[Home](../README.md) > [Reference](README.md) > Glossary

---

## A

### Agent Mode
Cursor's autonomous execution mode where the AI performs multi-step tasks independently, including file edits, terminal commands, and tool usage. Contrasts with conversational mode where each action requires confirmation.

### Always-Apply Rule
A rule with `alwaysApply: true` that is included in every conversation regardless of context. Used for universal standards like code style or security requirements.

### Auto-Attach Rule
A rule with `globs` patterns that automatically activates when matching files are in the conversation context.

---

## C

### Code Symbol
A reference to a code element (function, class, variable) that Cursor can recognize and navigate to. Used with `@` syntax (e.g., `@functionName`).

### Composer
Cursor's multi-file editing interface that allows coordinated changes across multiple files in a single session.

### Context
The information available to the AI during a conversation, including open files, selected code, referenced documents, and active rules. Limited by token budget.

### Context Budgeting
The practice of managing how much information is included in AI context to stay within token limits while maximizing relevance.

### Context Window
The maximum amount of text (measured in tokens) that can be processed in a single AI interaction. Typically 128K-200K tokens for modern models.

### Cursor Rules
Markdown files (`.mdc`) that provide persistent instructions to the AI. Stored in `.cursor/rules/` directory.

### .cursorignore
A file specifying patterns for files and directories that Cursor should exclude from indexing and context. Similar to `.gitignore` syntax.

---

## D

### Decision Flow
The framework for determining what type of artifact (rule, skill, prompt, or code) should be used to codify knowledge. Based on stability, enforcement needs, scope, and repeatability.

---

## E

### Enforcement
The mechanism by which standards are applied. Can be AI-enforced (through rules) or code-enforced (through linters, tests, CI/CD).

---

## F

### Frontmatter
The YAML metadata block at the top of an `.mdc` file, delimited by `---`. Contains `description`, `globs`, and `alwaysApply` fields.

---

## G

### Glob Pattern
A string pattern using wildcards to match file paths. Examples: `**/*.py` (all Python files), `src/**/*` (everything in src/).

---

## K

### Knowledge Codification
The process of capturing and encoding knowledge (standards, patterns, processes) into artifacts that can be shared and reused.

### Knowledge-Execution System
The mental model for understanding Cursor as a system that combines knowledge (rules) with execution capabilities (AI agent).

---

## L

### LLM (Large Language Model)
The AI model powering Cursor's capabilities. Processes natural language and code to provide assistance.

---

## M

### Marketplace
A shared repository of curated rules, skills, and prompts that teams can consume and contribute to.

### MCP (Model Context Protocol)
An open protocol that allows Cursor to connect to external data sources and tools through standardized servers.

### MCP Server
A service implementing the Model Context Protocol that provides Cursor access to external capabilities like databases, APIs, or specialized tools.

### MDC File
A Markdown file with `.mdc` extension used for Cursor rules. Combines YAML frontmatter with Markdown content.

---

## O

### On-Demand Rule
A rule without `alwaysApply` or `globs` that only activates when explicitly invoked using `@rulename`.

---

## P

### Playbook
A detailed, step-by-step guide for completing complex workflows. More comprehensive than a rule, focusing on process rather than constraints.

### Principles Layer
The top layer of the 3-Layer Stack representing stable, long-term standards encoded as rules.

### Product-Centric Model
A workspace organization strategy where each Cursor workspace corresponds to a single product or bounded context.

### Prompt
A structured request template with variables that can be filled in for specific situations. Reusable starting points for common tasks.

### Prompt Injection
A security concern where malicious content in files could influence AI behavior. Mitigated through careful rule design.

---

## R

### Rule
A persistent instruction to the AI that shapes behavior across conversations. Encoded as an `.mdc` file with YAML frontmatter.

### Rule Activation
The process by which a rule becomes part of the AI's context. Can be always-on, automatic (via globs), or manual (via @-mention).

---

## S

### Semantic Versioning
Version numbering scheme (MAJOR.MINOR.PATCH) used for marketplace resources. Major = breaking changes, Minor = new features, Patch = fixes.

### Skill
A structured workflow guide with sequential steps, decision points, and checkpoints. More dynamic than rules, focused on processes.

### Stability (Knowledge)
How long knowledge remains valid without significant changes. Stable knowledge (6+ months) is suitable for rules; volatile knowledge needs different approaches.

---

## T

### Token
The basic unit of text processing for LLMs. Roughly 4 characters or 0.75 words in English. Context windows are measured in tokens.

### 3-Layer Stack
The knowledge architecture model: Principles (Rules) → Playbooks (Skills) → Enforcement (Code/CI).

---

## W

### Workspace
A Cursor project context, typically corresponding to a directory or repository. Has its own `.cursor/` configuration.

---

## Y

### YAML
A data serialization format used for rule frontmatter. Human-readable with key-value pairs.

---

## See Also

- [MDC Schema](mdc-schema.md)
- [Core Concepts](../02-core-concepts/README.md)
- [Troubleshooting](troubleshooting.md)
